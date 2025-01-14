       """  
     Goal is to generate synthetic questions from random prebuilt JSON/Tags
     And use it to use to fine tune on error made.
        
    alias pyclean="python3 -u rag/rag_clean.py "
    
    export dir1="ztmp/finetune/query_tags"

    pyclean TagsIndustry process_industry --new_tag "pharma" 
            ---> new_tag (str/csv/parquet)

    pyclean llm_generate_tag_v2 --batch_size 5 --num 1000 --dirout "$dir1/tags_ref.json"
         --> "ztmp/tag_ref_question.json"
        
        
    pyclean llm_generate_question_fromtag --batch_size 5 --num 1000  --tag_json "$dir1/tags_ref.json"  --dirout "$dir1/tag_questions.parquet"
         --> "ztmp/tag_questions.parquet"
             

    pyclean llm_query_extract_NER  --dirout "$dir1/tag_questions_predict.parquet"
         -->  "ztmp/generated_tag.parquet"
           cols: tags_ref, question, tags_predict,  n_error


    pyclean llm_create_finetune_json --dirin "$dir1/tag_questions_predict.parquet"  --label_col "tags_ref"    --dirout "$dir1/gpt_train/"
         --> "ztmp/gpt_train/data_finetune.jsonl", "ztmp/gpt_train/df_finetune_debug_20241013_221013.parquet"

         """


if "import":
    import json, os, warnings, random
    import re
    import traceback

    warnings.filterwarnings("ignore")
    import pandas as pd, numpy as np

    from rag.engine_tv import fusion_search
    from rag.engine_qd import QdrantClient

    from utilmy import log, log2, pd_read_file, pd_to_file, json_save, date_now
    from utilmy.asearch.rag.engine_kg import dbsql_fetch_text_by_doc_ids
    from utilmy.asearch.rag.engine_qd import EmbeddingModelSparse
    from utilmy.asearch.rag.llm import LLM, llm_cleanup_gpt_jsonformat, promptRequest
    from pydantic import BaseModel, Field
    import pandas as pd

    import pandas as pd
    from collections import Counter

    import pyarrow.parquet as pq
    import pandas as pd
    from fuzzywuzzy import fuzz
    import json
    import traceback  #


######################### pydantic output validation ###################################
class questionNER(BaseModel):
    """
          Provide some comparisons and summarize the acquisitions of Palo Alto and Meta world
          in Cloud medical computing and military health field this year,
          for companies in America, but not in Canada ?

         {
              "task": [ "compare", "summarize" ]
              "date": ['this year']
              "date_period" : ['in' ]
              "industry_tags": ['Cloud medical computing", "military health" ]
              "company_names": ["Palto Alto", "Meta world"],
                "activity_tags": ["acquisition"],
              "context": ["companies in America",  "not in canada" ]
        }
    """
    ### Trick to improve accuracy.
    reasoning: str      = Field(description="Summarize in 2 sentences your reasoning on this entity extraction.")

    task: list          = Field(description="Example of tasks like \"report\", \"summarize\", \"what are\", \"unknown\" ")

    data_source: str   = Field(description="Example of data source \"news\", \"industry\",  ")


    date_period: str    = Field(description="before/between/after/in")
    date: list          = Field(description="Dates information in the text in this format:  YYYY  or YYYY-MM")

    company_names: list = Field(description="Names of the corporate entities")
    industry_tags: list = Field(description="tags related to company or business industries such as generative ai")


    # industry_tags_exclude: list = Field(description="tags which are excluded, tags is related to company or business industries such as healthcare, ai ")


    activity_tags: list = Field(description="company activity or actions mentioned in the text. Example: partnership, acquisition, collaboration")

    context:       list = Field(description="words of the text that did not get categorized in other fields")

    display_tags:  list = Field(description="list of tags to describe how the results should be ranked: 'most_recent', 'most_relevant' ")


#####################################################################################################
########### Create of normalize industry tags #######################################################
class TagsIndustry:
    def __init__(self, reference_file="datasmall/ref/question_industry_ref.csv"):
        """        
        Example usage:
            industry = TagsIndustry('industry_reference.json')
            industry.load_ref()
            industry.add_new_industry('Renewable Energy', 'Industry focused on renewable energy sources.')
            industry.save_ref()        
        Args:
            reference_file (str): The file path to the industry reference data.
        """
        self.dirin = reference_file
        self.dfr0 = None 
        self.dfnew = None
        log("############## Add Tags ###################")

    def load_ref(self):
        """
        Load the industry reference data from the specified file.
        """
        try:
            self.dfr0 = pd_read_file(self.dirin, sep="\t")
            log("Loaded reference data:", self.dfr0.head())
        except FileNotFoundError:
            log(f"Error: File {self.dirin} not found.")
        except Exception as e:
            log(f"Error loading reference data: {e}")

    def add_new_industry(self, ss: str):
        """
        Add a new industry to the reference data.

        Args:
            ss (str): The new industry data.
        """
        self.dfnew = pd_industry_load_normalize(ss, priority=2, origin='L_cat2', add_days=0)
        self.dfnew = self.dfnew.drop_duplicates(subset=['industry'], keep='first')
        log(f"new tag counts : {len(self.dfnew)}")
        
    def merge_new_industry(self):
        """ Merge new industry data with the reference data. """
        if self.dfr0 is None:
            log("Error: Reference data (dfr0) is not loaded.")
            return
        if self.dfnew is None:
            log("Error: New industry data (dfnew) is not loaded.")
            return
        
        log(f"############## Reference Data: {self.dfr0.head()}")
        log(f"############## New Industry Data: {self.dfnew.head()}")
        
        self.dfr0 = pd.concat((self.dfr0, self.dfnew)) 
        self.dfr0 = self.dfr0.drop_duplicates(subset=['industry'], keep='first')  
        self.dfr0 = self.dfr0.sort_values(by='industry')
        
        log(f"final tag counts : {len(self.dfr0)}")

    def save_ref(self):
        """
        Save the updated industry reference data to the specified file.
        """
        pd_to_file(self.dfr0, self.dirin, sep="\t", index=False)

    def process_industry(self, new_tag):
        """
        Process the industry data by loading, adding, merging, and saving.

        Args:
            new_industry (str): The new industry data to add.
        """
        log("Starting industry processing...")
        self.load_ref()
        self.add_new_industry(new_tag)
        self.merge_new_industry()
        self.save_ref()
        log("Industry processing completed successfully.")




def pd_industry_load_normalize(ss:str, priority=2, origin='L_cat2', add_days=2):
    
    
    log("###################### Normalized Tag ####################")
    
    if isinstance(ss, pd.DataFrame):
        dfr = ss 

    elif ".csv" in ss or ".parquet" in ss :
        from utilmy import pd_read_file
        dfr = pd_read_file(ss)
    elif isinstance(ss, str):        
        dfr = [ x.strip() for x in ss.split("\n")  if len( x.strip()) > 0  ]
    dfr = pd.DataFrame(dfr, columns=['industry'])
    dfr['priority'] = priority
    dfr['dt']       = int(date_now(fmt="%Y%m%d", add_days=add_days))
    dfr['n_words']  = dfr['industry'].apply(lambda x: len(x.split(" ")) )
    dfr['family']   = ' '  

    dfr['origin']   = origin

    log(dfr.head())
    return dfr



def pd_industry_add_new(ss=None):    
    #pd_to_file(dfr, "ztmp/data/cats/arag/questions/ref/question_industry_ref.csv", sep="\t", index=False)

    ####backup
    dfr0 = pd_read_file("datasmall/ref/question_industry_ref.csv", sep="\t")

    #### New one  
    if ".csv" in ss or ".parquet" in ss :  
        dfi = pd_read_file(ss)
        ss = "\n".join( dfi['industry'].tolist() )
        
    else:          
        ss = """
        5g
        air mobility
        manufacturing tech
        aerospace
        data
        agri
        agricultural equipment
        agri tech
        airline
        airport
        """
    
    dfr = pd_industry_load_normalize(ss, priority=2, origin='L_cat2', add_days=2)
    dfr = pd.concat((dfr0, dfr))
    dfr = dfr.drop_duplicates("industry", keep='first')

    ts = date_now(fmt="%y%m%d_%H%M%S")
    pd_to_file(f"datasmall/ref/question_industry_ref_{ts}.csv", sep="\t", index=False)


def pd_industry_count_freq(indus_file="datasmall/ref/question_industry_ref.csv", data_file: str, 
                           dirout="datasmall/ref/industry_count.csv"):
    """
            
    
    """
    def ismatch(word, x):
        return all(wi in x for wi in word.split(" "))

    df1 = pd_read_file(indus_file) 
    df2 = pd_read_file(data_file) 
    keyword_list_ref = df1['industry'].unique()  
    res = []

    for word in keyword_list_ref:
        count = df2[df2['L_cat'].apply(lambda x: ismatch(word, x))].shape[0]
        res.append([word, count])
    res_df = pd.DataFrame(res, columns=["word", "n_samples"])
    pd_to_file(res_df, dirout)





#############################################################################################
############# Fine Tuning Function calling ##################################################
"""  
     Goal is to generate synthetic questions from random prebuilt JSON/Tags
     And use it to use to fine tune on error made.
        
    alias pyclean="python3 -u rag/rag_clean.py "
    
    export dir1="ztmp/finetune/query_tags"


    pyclean llm_generate_tag --dirout "$dir1/tags_ref.json"
         --> "ztmp/tag_ref_question.json"
        
        
    pyclean llm_generate_question_fromtag --batch_size 5 --num 1000  --tag_json "$dir1/tags_ref.json"  --dirout "$dir1/tag_questions.parquet"
         --> "ztmp/tag_questions.parquet"
             

    pyclean llm_query_extract_NER  --dirout "$dir1/tag_questions_predict.parquet"
         -->  "ztmp/generated_tag.parquet"
           cols: tags_ref, question, tags_predict,  n_error


    pyclean llm_create_finetune_json --dirin "$dir1/tag_questions_predict.parquet"  --label_col "tags_ref"    --dirout "$dir1/gpt_train/"
         --> "ztmp/gpt_train/data_finetune.jsonl", "ztmp/gpt_train/df_finetune_debug_20241013_221013.parquet"

    pyclean generate_tags --dirout "$dir1/tag_query.parquet"
         --> "ztmp/tag_ref.json"
"""
def llm_generate_tag( ind_csv_path="datasmall/indus_ref.csv",com_csv_path="datasmall/labeled_companies.csv" ,
        question_prompt="",
        llm_service="groq",
        llm_model="llama3-70b-8192",
        dirout="ztmp/tags_ref.json",
        batch_size=50,
        num=1000
):
    """ Generate random tags from company names, industry tags, and activity tags.
            python3 -u rag/rag_summ.py llm_generate_sample_questions --batch_size 5 --num 1000

        Generate tags ---> Create question from tag

    """
    act_tag = [
            "partnership",
            "funding",
            "m and a",
            "industry news",
            "new product",
            "product",
            "service launch",
            "earnings",
            "listing",
            "expansion",
            "management",
            "approval",
            "regulation"
        ]
    act_sample = random.sample(act_tag, k=random.randint(1, 2))
    
    
    # Default prompt if not provided
    if not question_prompt:
        question_prompt = f"""
            You are a Researcher. Generate a single dictionary output that appears to be directly extracted from the user queries, with the following criteria:
            - Generate tags like company names, industry tags, and activity tags.
            - Cover a range of business scenarios by sampling contextually tailored 1-2 activity_tags, industries, and companies ONLY from the given context.
            - Include the following tags: company_names, industry_tags, activity_tags, date, and task.

            **Examples of output:
            Example 1. {{
                "reasoning": ["The text appears to be a question asking about the key partnerships formed by Habu and Syniti in the business performance enhancement industry from 2018 to 2022 and how these partnerships have impacted their market positions."],
                "task": ["summarize"],
                "date": ["2018", "2022"],
                "date_period": ["between"],
                "industry_tags": ["business performance enhancement"],
                "company_names": ["habu", "syniti"],
                "activity_tags": ["partnership"],
                "context": ["business performance enhancement industry", "market positions"],
                "display_tags": ["most_recent"],
                "data_source": ["industry"]
            }}

            Example 2. {{
                "reasoning": ["The text is about comparing the market strategies of Pfizer and Moderna in the pharmaceutical industry during the COVID-19 pandemic, highlighting their key partnerships and product developments in the genomic therapeutics sector."],
                "task": ["compare"],
                "date_period": ["during"],
                "industry_tags": ["pharmaceutical industry", "genomic therapeutics", "covid-19 pandemic"],
                "company_names": ["pfizer", "moderna"],
                "activity_tags": ["partnership", "product"],
                "context": ["market strategies", "key partnerships", "product developments"],
                "display_tags": ["most_relevant"],
                "data_source": ["industry"]
            
            Important Note: Use only the Given activity_tags, Industries and Companies refrain from using tags outside of the given scope!

            Respond only with the dictionary format: No additional text.
            }}
        """
    ind_df = pd_read_file(ind_csv_path, sep='\t')
    com_df = pd_read_file(com_csv_path)
    ind_list = ind_df['industry'].tolist()
    com_list = com_df['Company'].tolist()
    
    llm = LLM(service=llm_service, model=llm_model)
    all_tags = []
    tag_counts = {com: 0 for com in com_list}
    for _ in range(num):
        act_sample = random.sample(act_tag, k=random.randint(1, 2))
        avail_com  = [c for c in com_list if tag_counts[c] < 50]
        
        if not avail_com:
            print("No more companies can be sampled. Exiting loop.")
            break
        samp_com = random.sample(avail_com, min(batch_size, len(avail_com)))

        for com in samp_com:
            tag_counts[com] += 1
              
        batch_prompt = question_prompt + f"\nIndustries: {', '.join(ind_list)}\nCompanies: {', '.join(samp_com)}\nactivity_tags: {', '.join(act_sample)}"
        
        try:
            ### question generated from tags
            result = llm.get_save_sync(batch_prompt, output_schema=questionNER)
            if 'choices' in result and len(result['choices']) > 0:
                llm_resp = result['choices'][0]['message']['content']
                print(f'res: {llm_resp}')
                tags_dict = llm_cleanup_gpt_jsonformat(llm_resp)
                
                if tags_dict is not None and isinstance(tags_dict, dict):
                    all_tags.append(tags_dict)
                    for company in samp_com:
                        tag_counts[company] += 1

            else:
                print("Unexpected result format:", result)

        except Exception as e:
            print(f"Error while processing LLM response: {e}")
   

    ###### Saving Dictionnary
    print(f"Final tags count: {len(all_tags)}")
    json_save(all_tags, dirout, show=1, indent=4)





def llm_generate_tag_v2(
        dirdef="ztmp/tags_ref/create_tags.json",  
        dirout="ztmp/tags_ref11.json",                        
        dirin_ref_tags="datasmall/tags_ref/",
        llm_service="groq",
        llm_model="llama3-70b-8192",
        num=10
):
    """ Generate random tags from company names, industry tags, and activity tags.
        python3 -u rag/rag_summ.py llm_generate_tag_v2 --batch_size 5 --num 1000

        Generate tags ---> Create question from tag
    """
    from utilmy import glob_glob,json_load
    tag_definition = json_load(dirdef) 
    
    question_prompt = tag_definition.get("question_prompt", "")
    

    log("######### Extracted Samples of Reference TAGS #################################") 
    

    flist = glob_glob(dirin_ref_tags + "/*.parquet")
    from copy import deepcopy
    tag_copy = deepcopy(tag_definition)
    
    tag_all = {}

    for tag_key, ddict in tag_copy['tags'].items():  
        if 'fpath' in ddict: 
            fpath = ddict['fpath']
            dfi = pd_read_file(fpath, concat_sort=False) 
            ci = ddict['colname'] 
            tag_all[tag_key] = {
                'tag_name': ddict['tag_name'],
                'tag_count': len(dfi), 
                'tag_list': dfi[ci].tolist()  
            }
            log(f"##\npath : {fpath}\n")

    
       
    llm = LLM(service=llm_service, model=llm_model)
    

    all_tags = []
    tkeys = list(tag_all.keys())
       
    for _ in range(num):
        samp_li = []
        nmax = tag_copy['nmax']
        for t in tkeys:
            samp = random.sample(tag_all[t]["tag_list"], k=min(nmax, len(tag_all[t]["tag_list"])))
            samp_li.append(samp)

        msg=""
        for t, samp in zip(tkeys, samp_li):
            msg+=f"{tag_all[t]['tag_name']}: {','.join(samp)}\n"  

           
        batch_prompt = question_prompt + msg
        log(msg)
        log(f"\n################## Final Prompt with reference TAGS#################\n")
        log(batch_prompt)
        try:
            ### question generated from tags
            result = llm.get_save_sync(batch_prompt, output_schema=questionNER)
            log(f'############### GENERATED TAG DICTIONARY ############')
            if 'choices' in result and len(result['choices']) > 0:
                llm_resp = result['choices'][0]['message']['content']
                
                tags_dict = llm_cleanup_gpt_jsonformat(llm_resp)

                log(f"\n\n ################  GENERATED TAG  ##################\n{tags_dict}\n")

                   
                if tags_dict is None:
                    log(f"##unable to parse dictionary from the following response: \n{llm_resp}") 
                    continue
                       
                if tags_dict is not None and isinstance(tags_dict, dict):
                    log(tags_dict)
                    all_tags.append(tags_dict)
            else:
                log("Unexpected result format:", result)

        except Exception as e:
            log(f"Error while processing LLM response: {e}")

       
    ###### Saving Dictionary
    log(f"\n\n##### size : {len(all_tags)}\n")
    json_save(all_tags, dirout, show=1, indent=4)

def test_generate1():
       
    log("Running test for llm_generate_tag_v2...")
    try:
        llm_generate_tag_v2()
        log("Test completed successfully.")
    except ValueError as ve:
        log(f"Test failed with ValueError: {ve}")
    except TypeError as te:
        log(f"Test failed with TypeError: {te}")
    except Exception as e:
        log(f"Test failed with unexpected error: {e}")


############## Tag Query Gen #########################

def generate_tags(dirdef="ztmp/tags_ref/create_tags.json",  
        dirout="ztmp/tag_query/",                        
        dirin_ref_tags="datasmall/tags_ref/", llm_service="groq",
        llm_model="llama3-70b-8192",
        num=10):

    from utilmy import glob_glob, json_load, pd_read_file, json_save
    from copy import deepcopy

    log("######### Extracted Samples of Reference TAGS #################################")
    tag_definition = json_load(dirdef)
    flist = glob_glob(dirin_ref_tags + "/*.parquet")
    tag_copy = deepcopy(tag_definition)
    tag_all = {}
    
    if tag_copy['question_prompt'] is None:
        question_prompt = f"""
                Using the provided keywords or tags, generate 10 well-thought-out, diverse queries that explore a broad spectrum of contexts and ideas. 
                Each query should focus on a different angle or perspective related to the tags, touching on various relevant aspects such as challenges, opportunities, 
                implications, use cases, trends, or emerging issues.
                The goal is to ensure that the generated queries span a wide array of topics within the provided tags, encouraging deep exploration of different contexts. 
                
                The final output should be strictly 10 accurate questions only, covering the full range of concepts tied to the provided tags, with each query offering 
                a unique and expansive point of inquiry.

        \ntags : 
            """
    else: 
        question_prompt = tag_copy['question_prompt']

    # Extract tag details from files
    for tag_key, ddict in tag_copy['tags'].items():  
        if 'fpath' in ddict: 
            fpath = ddict['fpath']
            dfi = pd_read_file(fpath, concat_sort=False) 
            ci = ddict['colname'] 
            tag_all[tag_key] = {
                'tag_name': ddict['colname'],
                'tag_count': len(dfi), 
                'tag_list': dfi[ci].tolist()
            }
            log(f"##\npath : {fpath}\n")
            log(f"###### key names : {tag_all.keys()}")
    
    log(f"\nTag_ALL : \n{tag_all} \n\n")
    nmax = tag_copy.get('nmax', 2) 
    all_tags = []
    all_questions = []
    tag_batchs = []
    llm = LLM(service=llm_service, model=llm_model)

    for _ in range(num):
        tag = {} 
        msg = ""
        for k, v in tag_all.items():
            if isinstance(v['tag_list'], list):
                tag[k] = random.sample(v['tag_list'], random.randint(1, nmax))
            else:
                log(f"Warning: Expected list, got {type(v['tag_list'])} for key: {k}")

        all_tags.append(tag)        
        msg = '\n'.join([f"\n {k}: {', '.join(v)}" for k, v in tag.items()])
        batch_prompt = question_prompt + msg
        log(f"################ Batch Prompt ##################")
        log(f'{batch_prompt}')
        try:
            log(f"################ Generating 10 Questions ###############")
            result = llm.get_save_sync(batch_prompt)
            llm_resp = result['choices'][0]['message']['content']
            qlist = llm_resp.split("\n")
            log(qlist)

            qlist = [q for q in qlist if re.match('^[0-9]+', q)]
            qlist = [re.sub(r"^[0-9]*\.", "", q) for q in qlist]
            qlist = [q.strip() for q in qlist if len(q.strip()) > 0]
            
            all_questions.extend(qlist)
            tag_batchs.extend([tag] * len(qlist))  # Store corresponding tags for each question
        except Exception as e:
            log(traceback.format_exc())

    if all_questions:
        df = pd.DataFrame({
            'question': all_questions,
            'tag': tag_batchs  
        })
    else:
        df = pd.DataFrame(columns=['question', 'tag']) 

    log(f"\n\n##### size : {len(all_questions)}\n")
    pd_to_file(df, dirout + "tag_query.parquet")
    json_save(all_tags, dirout + "tags_json.json", show=1, indent=4)

####Generate quesions from tag#####
def llm_generate_question_fromtag(
        tag_json="ztmp/tags_ref11.json",
        llm_service="groq",
        llm_model="llama3-8b-8192",
        dirout="ztmp/tag_questions.parquet",
        num=1000,
        llm_max_tokens=1000
):       
    """
        python3 -m fire rag.rag_clean llm_generate_question_fromtag

        param: 
            tag_json: tags/generated 
            num: max_num of generation
    """
    from utilmy import json_load
    log("############## loading tags #############################")
    tag_json = json_load(tag_json)
    sample_tags = [
    {
        key: [
            re.sub(r"^[^a-zA-Z0-9]+", "", value).strip()
            for value in values if len(value.strip()) > 0
        ]
        for key, values in tag_dict.items()
    }


    for tag_dict in tag_json]
    api_key = os.environ.get("GKEYS")
    llm = LLM(service=llm_service, model=llm_model, api_key=api_key, llm_max_tokens=llm_max_tokens)
    all_questions = []

    for dict1 in sample_tags:

        question_prompt = f"""
            You are a researcher in NLP. Your task is to create a coherent query or question
            based on the provided tag represents parsed tag from query for Name Entities Recognition purpose
            the goal is to come up with a query that closely represent the given tag, and you should generate ONLY a query that accurately 
            reflects those tags.

            rule: only provide question without any additional text!

            Example: 
                dictionary : {{
                "reasoning": ["The text appears to be a question asking about the key partnerships formed by Habu and Syniti in the business performance enhancement industry from 2018 to 2022 and how these partnerships have impacted their market positions."],
                "task": ["summarize"],
                "date_period": ["between"],
                "date": ["2018","2022"],
                "industry_tags": ["business performance enhancement"],
                "company_names": ["Habu", "Syniti"],
                "activity_tags": ["partnership"],
                "context": ["business performance enhancement industry", "market positions"],
                "display_tags": ["most_recent"],
                "data_source": ["industry"]
            }}   
                question: "What are the key partnerships formed by Habu and Syniti in the business performance enhancement industry from 2018 to 2022 and how have these impacted their market positions?"
                dictionary: {dict1}
        """
        log(dict1)


        if len(all_questions) >= num:
            break
        batch_prompt = question_prompt
        log(f"\nBatch_prompt: \n{batch_prompt}")
        try:
            result = llm.get_save_sync(batch_prompt)
            llm_resp = result['choices'][0]['message']['content']
            log("######################### Generated Question ##############################")
            qlist = llm_resp.split("\n")
            qlist = [re.sub(r"^[^a-zA-Z0-9]+", "", q) for q in qlist]
            qlist = [q.strip() for q in qlist if len(q.strip()) > 0]
            log(qlist) 
            if qlist:
                for q in qlist:
                    if len(all_questions) < num:
                        all_questions.append({"tags_ref": dict1, "question": q})
                    else:
                        break
                if len(all_questions) >= num:
                    break
                   
        except Exception as e:
            log(traceback.format_exc())

    log(f"###### total size :{len(all_questions)}")
    df = pd.DataFrame(all_questions)
    pd_to_file(df, dirout, index=True)
    return all_questions





### Extract NER ####################################################
def llm_query_extract_NER( dirin="ztmp/tag_query/tag_query.parquet", 
                              dirout="ztmp/generated_tag.parquet", 
    
    indus_ref="datasmall/tags_ref/question_industry_ref.parquet", 
    llm_service="groq", 
    llm_model="llama3-70b-8192", 
    llm_max_tokens=1000
) -> dict:
    """
    query_tags_dict: {
        'task': ['summarize'], 
        'date_period': 'in', 
        'date': ['2024'], 
        'company_names': ['microsoft'], 
        'industry_tags': ['generative AI'],  ---> normalize 
        'activity_tags': ['partner'],        ---> partnership 
        'display_tags': ['most_recent']
    }
    """

    log("####################### Loading Query ###########################")
    df = pd_read_file(dirin)

    log(df.head())
    result = []

    def count_err(x):

        log("######################## catch error tags #######################")
        err_cnt = 0
        keys = ['activity_tags', 'company_names', 'industry_tags']
        ref = x['tag']
        pred = x['output_tag']
        
        if not isinstance(ref, dict):
            raise ValueError("tag_ref must be a dictionary")
        if not isinstance(pred, dict):
            return len(keys)
        
        for key in keys:
            ref_val = ref.get(key, '')
            pred_val = pred.get(key, '')
            
            if isinstance(ref_val, np.ndarray):
                ref_val = sorted([str(item).strip().lower() for item in ref_val.tolist()])
            elif isinstance(ref_val, list):
                ref_val = sorted([str(item).strip().lower() for item in ref_val])
            else:
                ref_val = sorted([item.strip().lower() for item in str(ref_val).split(',')])
            
            if isinstance(pred_val, np.ndarray):
                pred_val = sorted([str(item).strip().lower() for item in pred_val.tolist()])
            elif isinstance(pred_val, list):
                pred_val = sorted([str(item).strip().lower() for item in pred_val])
            else:
                pred_val = sorted([item.strip().lower() for item in str(pred_val).split(',')])
            
            if ref_val != pred_val:

                log(f"referece tag : {ref_val} \n predicted tag : {pred_val} \n")
                err_cnt += 1
                
        return err_cnt

    from rag.rag_summ import llm_question_extract_NER
    for ix, row in df.iterrows():
        question_text = row['question']
        llm_output = llm_question_extract_NER(
            question=question_text, 
            llm_service=llm_service, 
            llm_model=llm_model, 
            llm_max_tokens=llm_max_tokens
        )

        if llm_output is None:
            result.append({})
            continue  
        
        if not isinstance(llm_output, dict):
            result.append({})
            continue  
        
        
        log("################# Extract Tags #################")
        llm_output['industry_tags'] = []
        ind_df = pd_read_file(indus_ref)
        xlist = ind_df['industry'].tolist()
        for ti in llm_output.get('industry_tags', []):
            ti = ti.replace("tech", "").strip().replace("industry", "").strip()
            if ti.split(" ")[0] not in question_text:
                continue
            ti2 = str_fuzzy_match(ti, xlist)
            llm_output['industry_tags'].append(ti2)
            log(llm_output)
        result.append(llm_output) 
    
    df['output_tag'] = result
    df['err_count']   = df.apply(lambda x: count_err(x), axis=1)

    log(f"#### Total Tags : {len(df)}")
    pd_to_file(df, dirout)



def llm_create_finetune_json(dirin, q_col="question", label_col="tag", dirout="ztmp/gpt_train", 
                             create_prompt_func=None):
    """ 
    
    
    """
    log('###### Load Error Tags #################################')
    from rag.rag_summ import llm_finetune_create_json

    df = pd_read_file(dirin)

    df = df[df['err_count'] >= 1]
    log(df[[label_col]].head())

    
    def to_json_compatible(val):
        if isinstance(val, np.ndarray):
            return val.tolist()
        if isinstance(val, dict):
            return {k: to_json_compatible(v) for k, v in val.items()}
        return val

    df[label_col] = df[label_col].apply(to_json_compatible)

    log(f"###### size : {len(df)}")

    return llm_finetune_create_json(df, q_col, label_col, dirout, create_prompt_func)





####### calculate confusion matrix #######
def list_flatten(lst):
    return [item for sublist in lst for item in (sublist if isinstance(sublist, list) else [sublist])]

def compare_json(tlist='ztmp/actual_tags.json', plist='ztmp/predicted_tag.json', key='company_names'):
    """
       Scikit learn you can chatGPT to use scikit learn precision recall 
    

    """
    true_json = json_load(tlist)
    predicted_json = json_load(plist)
    if len(true_json) != len(predicted_json):
        print(f'len: {len(true_json)} && {len(predicted_json)}')
        return "The number of dictionaries in true and predicted values do not match."

    metrics = []
    total_TP = total_FP = total_FN = 0 

    for i in range(len(true_json)):
        tval = list_flatten(true_json[i].get(key, [])) 
        pval = list_flatten(predicted_json[i].get(key, [])) 
        tset = set(tval)
        pset = set(pval)

        TP = len(tset.intersection(pset))  
        FP = len(pset - tset)             
        FN = len(tset - pset)             
        TN = 0  

        total_TP += TP
        total_FP += FP
        total_FN += FN

        total = TP + FP + FN + TN
        acc = (TP + TN) / total if total > 0 else 0
        prec = TP / (TP + FP) if (TP + FP) > 0 else 0
        rec = TP / (TP + FN) if (TP + FN) > 0 else 0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0

        metrics.append({
            "Idx": i,
            "TP": TP,
            "FP": FP,
            "FN": FN,
            "Acc": acc,
            "Prec": prec,
            "Rec": rec,
            "F1": f1
        })

    overall_prec = total_TP / (total_TP + total_FP) if (total_TP + total_FP) > 0 else 0
    overall_rec = total_TP / (total_TP + total_FN) if (total_TP + total_FN) > 0 else 0
    overall_f1 = (2 * overall_prec * overall_rec) / (overall_prec + overall_rec) if (overall_prec + overall_rec) > 0 else 0

    metrics.append({
        "Idx": "Overall",
        "TP": total_TP,
        "FP": total_FP,
        "FN": total_FN,
        "Acc": "N/A", 
        "Prec": overall_prec,
        "Rec": overall_rec,
        "F1": overall_f1
    })

    mdf = pd.DataFrame(metrics)
    pd_to_file(mdf, 'ztmp/act_matrix.csv')





#################################################################################################
def pd_clean_industry_tags(dirin: str, json_file="ztmp/tags/refs/industry_map.json", dirout="ztmp/tags/norm/", cutoff=95) -> None:
    """

        df['industry_tags'].apply(lambda x: x.split(",") ),count_values()
       output: List of indivual tags



    """
    df = pd_read_file(dirin)


    tag_all =[]
    for ii, x in df.iterrows():

        question = x['Questions']
        xtags    = str(x['industry_tags']).strip().split(",")
        tag_all  = tag_all + [   [question, xi] for xi in xtags        ]

    df2 = pd.DataFrame(tag_all, columns=['question, tag'] )


    #### Deduplciate.
    df2 = df2.drop_duplicates(['tag'] )
    df2 = df2.sort_values("tag", ascending=True)


    #### Add normalized tags
    from utilmy import json_load, json_save
    tag_ref =  json_load(json_file)


    def norm_tag(tag):
        ## do fuzzy match and return the values using tag_ref
        ## industry_tags_ref_list = [xi.strip() for xi industry_tags_ref.split("\n") ]

        tagnorm= ""
        return tagnorm

    df2['tag2'] =  df['tag'].apply(lambda  x: norm_tag(x))

    ###  question, tag, tag2
    pd_to_file(df2, dirout +"/df_industry_tag_normed.parquet", show=1)



def pd_add_activity_tag2(parquet_file: str, json_file: str, output_file: str) -> None:
    # Read the Parquet file
    df = pq.read_table(parquet_file).to_pandas()

    if 'activity_tags' not in df.columns:
        raise ValueError("The Parquet file must contain an 'activity_tags' column.")

    # Convert all elements in the 'activity_tags' column to strings, assuming empty string if None
    df['activity_tags'] = df['activity_tags'].apply(convert_to_strings)

    # Load the JSON file with keywords
    with open(json_file, 'r') as f:
        keywrd = json.load(f)

    # Invert the dictionary for fuzzy matching
    invert = {var: keyword for keyword, variations in keywrd.items() for var in [keyword] + variations}

    # Function to map a word to the closest keyword using fuzzy logic
    def map_to_closest_keyword(word):
        match = None
        highest_score = 0
        for var in invert.keys():
            score = fuzz.token_sort_ratio(word, var)
            if score > highest_score:
                highest_score = score
                match = invert[var]
        return match if highest_score > 95 else None

    # Process activity_tags and create a new column 'activity_tag2'
    activity_tags = []
    for tags in df['activity_tags']:
        mapped_tags = [map_to_closest_keyword(tag) for tag in tags if map_to_closest_keyword(tag)]
        activity_tags.append(mapped_tags)

    # Add the new column to the DataFrame
    df['activity_tag2'] = activity_tags

    # Write the DataFrame back to Parquet
    df.to_parquet(output_file)


def pd_add_industry_tag2(parquet_file: str, json_file: str, output_file: str, cutoff=95) -> None:
    """
        cutoff @ 95

        df['industry_tags'].apply(lambda x: x.split(",") ),count_values()


    """
    df = pq.read_table(parquet_file).to_pandas()

    tags = set()
    clean = lambda t: t.strip() if isinstance(t, str) else t  ### handle trailing

    """handling data types and empty fields




    """
    for idx, val in enumerate(df['industry_tags']):
        if isinstance(val, str) and val.strip():
            tag_list = val.split('","')
            tags.update(clean(t) for t in tag_list)
            print(f"Row {idx}: Found tags - {tag_list}")
        elif isinstance(val, list):
            tags.update(clean(t) for t in val if isinstance(t, str) and t.strip())
            print(f"Row {idx}: Found list - {val}")

        elif isinstance(val, np.ndarray):
            tags.update(clean(t) for t in val if isinstance(t, str) and t.strip())
            print(f"Row {idx}: Found ndarray - {val}")
        elif pd.isna(val):
            print(f"Row {idx}: Empty or invalid value")
        else:
            print(f"Row {idx}: Unexpected type - {type(val)}")

    print(f"All unique tags collected: {tags}")

    with open(json_file, 'r') as f:
        kws = json.load(f)

    # inverting dictionary
    inv_map = {v: k for k, vs in kws.items() for v in [k] + vs}

    ## extracting keys for the mapping
    kw_keys = list(inv_map.keys())

    uniq_map = {}

    for t in tags:
        t = clean(t)  # Ensure no trailing spaces
        norm_t = t.lower()

        """
        pre-conditional mapping: ----> ion, ed ,pre, es/s, multi, .....



        """
        var = {norm_t}

        if norm_t.endswith('s'):
            var.add(norm_t[:-1])
        if norm_t.endswith('es'):
            var.add(norm_t[:-2])
        if norm_t.endswith('ies'):
            var.add(norm_t[:-3] + 'y')
        if norm_t.endswith('ions'):
            var.add(norm_t[:-4])
        if norm_t.endswith('ion'):
            var.add(norm_t[:-3])
        if norm_t.startswith('multi'):
            var.add(norm_t[5:])
        if norm_t.startswith('multi '):
            var.add(norm_t[6:])
        if norm_t.startswith('pre'):
            var.add(norm_t[3:])
        if norm_t.startswith('pre '):
            var.add(norm_t[4:])
        if norm_t.startswith('pre-'):
            var.add(norm_t[4:])
        if norm_t.startswith('multi-'):
            var.add(norm_t[6:])

        for v in var:
            if v in inv_map:
                uniq_map[t] = inv_map[v]
                break
        else:
            def map_closest(word):
                res = process.extract(word.strip(), kw_keys, scorer=fuzz.partial_ratio, score_cutoff=cutoff)
                if res:
                    res = sorted(res, key=lambda x: (x[1], len(x[0])), reverse=True)
                    best = res[0][0]
                    return inv_map[best]
                return ""

            mapped = map_closest(t)
            if t not in uniq_map:
                uniq_map[t] = mapped

    print(f"Unique mapping results: {uniq_map}")

    # Write json
    with open(output_file, 'w') as outfile:
        json.dump(uniq_map, outfile, indent=4)


def pd_industry_count_freq(dirin, dirout):
    """
       python rag_clean.py pd_industry_count_freq   --dirin  "ztmp/df.parquet"   --dirout datasmall/ref/
    
        L_cat 
    
         def ismatch(word, x):
       for wi in word.split(" "):
         if wi in x:
           flag=True
         else
           flag=False  
      return flag           
              
     res = []         
     for word in keyword_list_ref:
        df1 = df[ df['L_cat'].apply( lambda x : ismatch(word, x)  )   ]
        res.append([word, len(df1)])      
        
     res = pd.DataFrame(res, columns=["word", "n_samples"])
     pd_to_file(res, "datasmall/ref/question_industry_tag_count_samples.csv")              
           

    """





###############################################################################################
############ LLM generation ###################################################################
def llm_keyword_variations(
        keywords,
        llm_service="groq",
        llm_model="llama3-8b-8192",
        examples=None,
        num_var=50,
        max_tokens=2000,
        output="normalized_variations.json"
):
    # Examples of context
    if examples is None:
        examples = {
            'automation': ['automated', 'automation', 'automating'],
            'auto': ['automobile', 'auto mobile', 'vehicles', 'locomotive'],
            'health': ['healthcare', 'health care', 'well-being', 'wellness', 'medical', 'medicine']
        }

    api_key = os.environ.get("GKEY")
    llm = LLM(service=llm_service, model=llm_model, api_key=api_key, max_tokens=max_tokens)

    # Dictionary to hold all keyword variations
    norm_var = {}

    for keyword in keywords:
        prompt = f"""
                    You are an advanced NLP specialist. For the primary keyword '{keyword}', generate exactly {num_var} variations or synonyms. These variations are intended to:

                    1. Normalize Queries: Expand search queries to cover different linguistic forms and variations of the keyword.
                    2. Reduce Redundancy: Ensure that each variation is unique and avoid duplication.
                    3. Handle Linguistic Diversity: Reflect the same or similar meaning to maintain context and relevance, considering linguistic nuances throughout all variations.
                    4. Common Misspellings and Variations: Include common misspellings or alternate spellings to capture a wider range of search queries.

                    Guidelines:
                    - Ensure that the variations are unique and avoid redundancy.
                    - Maintain close relevance & meaning to the original keyword.
                    - Generate exactly {num_var} variations for each keyword.

                    Examples: {examples}

                    Keyword: {keyword}

                    Output Format: '{keyword}': ['variation1', 'variation2', 'variation3']
"""
        try:
            # Fetch result from LLM
            result = llm.get_save_sync(prompt)
            llm_response = result['choices'][0]['message']['content']

            # Parse the response for the keyword without splitting by characters
            if ':' in llm_response:
                _, var = llm_response.split(':', 1)
                variations_list = re.findall(r"'(.*?)'", var)

                # Ensure the number of variations matches num_var
                if len(variations_list) < num_var:
                    # Pad with existing variations to meet num_var requirement
                    variations_list += variations_list[:num_var - len(variations_list)]
                elif len(variations_list) > num_var:
                    # Truncate to exactly num_var
                    variations_list = variations_list[:num_var]

                norm_var[keyword] = variations_list

        except Exception as e:
            print(f"An error occurred for keyword '{keyword}': {e}")

    # Ensure uniqueness across all keywords
    all_var = set()
    for key, variations in norm_var.items():
        unique_var = []
        for variation in variations:
            if variation not in all_var:
                unique_var.append(variation)
                all_var.add(variation)
        norm_var[key] = unique_var

    # Save the entire dictionary
    with open(output, 'w') as f:
        json.dump(norm_var, f, indent=4)

    return output







#############################################################################################
def llm_generate_sample_questions(
        ind_csv_path="",
        com_csv_path="",
        question_prompt="",
        llm_service="groq",
        llm_model="llama3-8b-8192",
        dirout="ztmp/gpt_train/synthetic_questions.csv",
        batch_size=50,
        num=1000
):

    """
        python3 -u rag/rag_summ.py llm_generate_sample_questions --batch_size 5 --num 1000


    """
    if not question_prompt:
        question_prompt = f"""
            You are a business analyst. Generate {batch_size} questions with the following criteria:
            - Questions should include 1-2 company/industry names, along with relevant business/industry terms.
            - Cover a range of business scenarios, including but not limited to acquisitions, partnerships, technological innovations, market performance, and strategic initiatives.
            - Reference various sectors such as technology, finance, healthcare, and manufacturing.
            - Include companies of different sizes, from established giants to emerging startups.
            - Incorporate different timeframes, ensuring a mix of historical and recent contexts.

            Example questions:
            1. What are the key acquisitions made by Microsoft and Amazon in the field of AI from 2010 to 2020, and how have these impacted their market positions?
            2. Describe the performance of Google and Facebook in the digital advertising industry in 2020, focusing on their revenue growth and market strategies.
            3. How have recent technological innovations by companies like Tesla and IBM influenced advancements in the electric vehicle and cloud computing sectors?
            4. Compare the market strategies of Pfizer and Moderna in the pharmaceutical industry during the COVID-19 pandemic, highlighting their key partnerships and product developments.

            NB: Ensure that you generate EXACTLY {batch_size} questions.
        """

    # Read data from CSV files
    from utilmy import pd_read_file, pd_to_file
    ind_df = pd_read_file(ind_csv_path)
    com_df = pd_read_file(com_csv_path)

    print(ind_df.columns)  # Debugging: Print column names
    print(com_df.columns)  # Debugging: Print column names

    ind_list = ind_df['L2_cat'].tolist()  # Adjust column name if needed
    com_list = com_df['com_name'].tolist()  # Adjust column name if needed

    api_key = os.environ.get("GKEY")
    llm = LLM(service=llm_service, model=llm_model, api_key=api_key)
    all_questions = []
    used_com = set()

    while len(all_questions) < num:

        avail_com = [c for c in com_list if c not in used_com]  # Re-sampling

        if not avail_com:
            break

        # Randomly sample companies
        samp_com = random.sample(avail_com, min(batch_size, len(avail_com)))
        used_com.update(samp_com)

        # Create the prompt template within Industries context
        batch_prompt = question_prompt + f"\nIndustries: {', '.join(ind_list)}\nCompanies: {', '.join(samp_com)}"

        try:
            result = llm.get_save_sync(batch_prompt)
            llm_resp = result['choices'][0]['message']['content']
            qlist = llm_resp.split("\n")
            qlist = [q for q in qlist if re.match('^[0-9]+', q)]
            qlist = [re.sub(r"^[0-9]*\.", "", q) for q in qlist]
            qlist = [q.strip() for q in qlist if len(q.strip()) > 0]

            # Add questions to the list, making sure we don't exceed 'num'
            all_questions.extend(qlist)
            if len(all_questions) >= num:
                break

        except Exception as e:
            print(traceback.format_exc())

    all_questions = list(set(all_questions))[:num]

    df = pd.DataFrame(all_questions, columns=['Questions'])
    pd_to_file(df, dirout, index=False)
    return all_questions







############################################################################################
######## Actual query extraction ###########################################################
def llm_question_extract_batch(dirin: str, output_file: str, llm_service="openai", llm_model="gpt-4o-mini",
                             llm_max_tokens=1000) -> pd.DataFrame:
    """
    Process questions from a Parquet file and extract tags, saving the result to a new Parquet file.
    Args:
        parquet_file (str): Path to the input Parquet file.
        output_file (str): Path to save the output Parquet file.
        llm_service (str): LLM service to use (default: "openai").
        llm_model (str): LLM model to use (default: "gpt-4o-mini").
        llm_max_tokens (int): Maximum tokens for LLM (default: 1000).

    Returns:
        pd.DataFrame: DataFrame containing the extracted tags.
    """
    if isinstance(dirin, str):
        df = pd_read_file(dirin)
    else: 
        df = dirin        
        
    df['tags_extract'] = df['Questions'].apply( lambda x: llm_question_extract_NER(question=x, llm_service=llm_service,
                                                                                  llm_model=llm_model, llm_max_tokens=llm_max_tokens))
    return df




def llm_question_extract_NER(question="Summarize the news", llm_service="openai", llm_model="gpt-4o-mini", llm_max_tokens=1000) -> dict:
    """
      query_tags_dict: {
       
           'task': ['summarize'], 
           'date_period': 'in', 
           'date': ['2024'], 
           'company_names': ['microsoft'], 
           'industry_tags': ['generative AI'],  ---> normalize 
           'activity_tags': ['partner'],        ---> partnership 
                       
           'display_tags': ['most_recent']}
    
    """
    prompt = f"""
    Extract specific tags from the question below:
    -----------question-----------
    {question}


    Reread the question again:
    -----------question-----------
    {question}
    
    
    Make sure that the extracted tags are extracted from the sentence.
    Do not invent tags which is not in the question.
    
    Example of activity_tags:
 'partnership"
 'funding'
 'm and a'
 'industry news'
 'new product'
 'product'
 'service launch'
 'earnings'
 'listing'
 'expansion'
 'management'
 'approval'
 'regulation '


    Example of potential industry_tags :
    additive manufacturing
    generative ai
    generative ai infrastructure
    genai
    ai
    ai drug
    aircraft
    alternative energy
    automobile
    automation
    automated store
    beauty
    bio materials
    biometric
    biotech
    blockchain
    business expense
    carbon
    cell cultured
    cell gene
    climate
    clinical trial
    cloud
    cloud optimization
    fitness
    conservation
    crm
    cyber insurance
    cybersecurity
    dairy egg
    data infrastructure
    commerce
    decentralized finance
    devops
    digital privacy
    digital retail    
    digital twin
    digital wellness
    edge computing
    edtech
    esport
    EV
    Electrice Vehicule
    extended reality
    facial recognition
    farming
    fertility
    financial wellness
    fintech
    insurance
    food delivery
    food waste
    foundation models
    gene therapy
    generative ai
    health
    human gene
    hydrogen
    identity access
    insurtech
    last mile
    livestock biotech
    logistics
    longevity
    code
    machine learning
    marketing automation
    metaverse
    natural fertilizers
    banks
    online freelancing
    pay later
    pet
    meat
    precision medicine                                                                                            
    prefab
    quantum computing
    remote work
    residential
    restaurant robotics
    retail robots
    retail trading
    sales engagement
    satellite
    serverless computing
    smart factory
    smart farming
    smart mobility
    smart packaging
    space travel
    supply chain
    travel
    truck
    web
    workflow automation     

    """

    llm_1   = LLM(llm_service, llm_model, max_tokens=llm_max_tokens)
    llm_res = llm_1.get_save_sync(prompt=prompt, output_schema=questionNER, dirout=None)
    msg = llm_res["choices"][0]["message"]["content"]
    dd  = llm_cleanup_gpt_jsonformat(msg)
    log('\n###### msg_dict_raw: ', dd)


    #### Post process task ###################################
    lsource = {'news': 'LZnews', 'industry':  'Eindustry'}
    ti = dd.get('data_source', 'industry')
    if 'activi' in ti:      ti = 'news'

    dd['data_source'] = lsource.get(ti, 'Eindustry')


    #### Post process task ###################################
    ll2 = []
    for ti in dd.get('task', ['summarize']):
       if  'what are' in ti.lower():
          ll2.append( 'summarize')

       else:
          ll2.append(ti)
    dd['task'] = ll2


    #### Post process date ###################################
    ll2 = []
    for ti in dd.get('date', ['2024']):
          ll2.append( ti.lower() )
    dd['date'] = ll2 


    #### Post process activity ###############################
    ll2 = []
    log(dd['activity_tags'] )
    for ti in dd.get('activity_tags', ['partnership']):
       #if ti.split(" ")[0] not in question:
       #     continue

       ti2 = NER_activity_norm(ti)

       if  'partner' in ti2 or 'collabo'  in ti2:
          ll2.append( 'partnership')

       elif  'acqui' in ti2 or 'merge'  in ti2:
          ll2.append( 'm and a')

       elif  'activi'   in ti2:
          pass
       else:
          ll2.append(ti2)
       log(ti, ti2) 

    dd['activity_tags'] = ll2


    #### Industry ###########################################
    ll2 = []
    for ti in dd.get('industry_tags', []):
       ti = ti.replace("tech", " ").strip()
       if ti.split(" ")[0] not in question:
           continue

       if 'ev' in ti.lower():
          ll2.append('automobile') 
       ti2 = NER_industry_norm(ti)
       ll2.append(ti2)
    dd['industry_tags'] = ll2


    #### Post process Company ###############################
    ll2 =[]
    for ti in dd.get('company_names', []):
          ll2.append( ti.lower() )
    dd['company_names'] = ll2 


    #### Post process display ###############################
    ll2 =[]
    for ti in dd.get('display_tags', ['most_recent']):
          ll2.append( ti.lower() )
    dd['display_tags'] = ll2 
 
    # assert len(dd[ questionNER.keys()])>0, 'Missing keys' 


    log("\n##### query_tags_dict:", dd) 
    return dd



def NER_activity_norm(ti):
    ti2 = ti.lower()
    ti2 = ti2.replace('investment',  'funding')  
    ti2 = ti2.replace('investments', 'funding')      
    return ti2



def NER_industry_norm(ti):
    ti2 = ti.lower()
    ti2 = ti2.replace('artificial intelligence', 'ai')
    ti2 = ti2.replace('technology', 'tech')
    ti2 = ti2.replace('genai', 'generative ai')   
    ti2 = ti2.replace('healthcare', 'health')   
    # ti2 = ti2.replace('automobile', 'auto')    
    return ti2




############################################################################################
######## utils #############################################################################
def convert_to_strings(tags):
    """ Convert all elements in the list to strings, handling None or missing values. """
    if tags is None:  # Check if tags is None
        return []  # Return an empty list if None
    return [str(tag) if tag is not None else '' for tag in tags]


def str_fuzzy_match(xstr:str, xlist:list, cutoff=70.0):
    from rapidfuzz import process, fuzz
    results = process.extract(xstr, xlist, scorer=fuzz.ratio, score_cutoff=cutoff)
    return [result[0] for result in results]


def generate_bigram_frequency(sentence_list):
    """
    sentence_list: list of sentences (need to be split)
    return pandas dataframe with columns ['bigram', 'freq']
    dfb = generate_bigram_frequency( dfg['L3_cat'].values )

    """
    bigrams = [b for s in sentence_list for b in zip(s.split()[:-1], s.split()[1:])]
    bigram_counts = Counter(bigrams)
    df = pd.DataFrame(bigram_counts.items(), columns=['bigram', 'freq'])
    return df[['bigram', 'freq']].sort_values('freq', ascending=False)




#### Synomous list
{
    
 "about":  """  Concerning, Regarding, Touching, Respecting, Apropos, Around, Approximately, Nearby, Adjacent, Atop, Upon, Over, Above, Covering, Alongside, Beside, Near, Towards, Approaching, Surrounding, Encompassing, Pertaining to, In relation to, With reference to, As regards, In the matter of, Dealing with, Relating to, Considering, Discussing """
    
 ,"write a report": """ Compose a document, Draft a summary, Prepare an account, Produce a record, Create a narrative, Formulate a brief, Develop a chronicle, Generate a statement, Construct a review, Author an analysis, Pen a description, Craft a synopsis, Compile findings, Assemble a dossier, Outline observations, Detail an assessment, Jot down conclusions, Scribe an evaluation, Document results, Transcribe information, Log data, Record outcomes, Recount events, Relate occurrences, Narrate proceedings, Delineate facts, Enumerate details, Itemize particulars, Render an account, Set forth findings
 """   
    
    
}



#############################################################################################
if __name__ == '__main__':
    import fire
    fire.Fire()

"""


     ##logs:                                                                                       
                pyclean llm_generate_tag_v2


        ######### Extract Reference TAGS #################################
        [['regulation', 'partnership', 'm and a', 'service launch', 'approval'], ['smart packaging', 'material', 'airline', 'health', 'ingredient'], ['Levi Strauss & Co.', 'ServiceNow', 'GlaxoSmithKline', 'Bayer', 'Deutsche Telekom']]


        ################## Final Prompt with reference TAGS#################
        You are a Researcher. Generate a single dictionary output that appears to be parsed from a human question or query
        - Select 1 or 2 for tags from the provided lists , following these guidelines:
        - Use only the provided tags and generate the rest of the tags that fits contextually with selected tags
        Respond only with a dictionary format. No additional characters are allowed except a dictionary

        Activity: regulation,partnership,m and a,service launch,approval
        Industry: smart packaging,material,airline,health,ingredient
        Company: Levi Strauss & Co.,ServiceNow,GlaxoSmithKline,Bayer,Deutsche Telekom


        ############### GENERATED TAG DICTIONARY ############
        {'reasoning': "The query appears to be related to a company's activity in the health industry, specifically regarding 
        a service launch. The extracted entities suggest a focus on a specific company and its actions.", 'task': ['report'], 'data_source': 
        'industry', 'date_period': 'in', 'date': ['2022'], 'company_names': ['GlaxoSmithKline'], 'industry_tags': ['health'], 'activity_tags': 
        ['service launch', 'approval'], 'context': ['new'], 'display_tags': ['most_relevant']}

        ##################  Count : 1

        ######################################################################################################################################################################
        ##################################################################################################################################################################3###
        ######################################################################################################################################################################



    `               pyclean rag_clean generate_query_tags --num 1

        ######### Extracted Samples of Reference TAGS #################################
        ##
        path : datasmall/tags_ref/activity_tags.parquet

        ##
        path : datasmall/tags_ref/question_industry_ref.parquet

        ##
        path : datasmall/tags_ref/labeled_companies.parquet

        ################ Batch Prompt ##################
        Using the provided keywords or tags, generate 10 well-thought-out, diverse queries that explore a broad spectrum of contexts and ideas.
        Each query should focus on a different angle or perspective related to the tags, touching on various relevant aspects such as challenges, opportunities,
        implications, use cases, trends, or emerging issues.
        The goal is to ensure that the generated queries span a wide array of topics within the provided tags, encouraging deep exploration of different contexts.
        The final output should be strictly 10 accurate questions only, covering the full range of concepts tied to the provided tags, with each query offering
        a unique and expansive point of inquiry.
        tags :
        activity_tags: m and a, approval

        industry: environmental services, streaming media

        company: AutoStore

        ################ Generating 10 Questions ###############

        ['Here are 10 diverse queries that explore a broad spectrum of contexts and ideas related to the provided tags:', '', '1. How can environmental services 
        companies like AutoStore leverage M&A strategies to expand their offerings and stay competitive in the market, while ensuring sustainable practices are 
        maintained?', '2. What are the key regulatory approval hurdles that environmental services companies face when acquiring or merging with other companies, 
        and how can they navigate these challenges effectively?', '3. In the context of streaming media, how can companies like AutoStore utilize M&A to enhance 
        their content offerings and improve user engagement, while minimizing environmental impact?', '4. What are the emerging trends in environmental services 
        that are driving M&A activity, and how can companies like AutoStore position themselves to take advantage of these opportunities?', '5. How can environmental
        services companies balance the need for growth through M&A with the need to maintain approval from regulatory bodies and stakeholders?', '6. What role does 
        approval from regulatory bodies play in shaping the M&A strategies of environmental services companies, and how can companies like AutoStore ensure compliance?', 
        '7. In what ways can M&A activity in the environmental services sector drive innovation and the development of new sustainable technologies, and how can companies 
        like AutoStore capitalize on these opportunities?', '8. How can companies like AutoStore use M&A to expand their geographic reach and enter new markets, 
        while ensuring that their environmental services offerings are adapted to local regulations and approval requirements?', '9. What are the key risks and challenges 
        associated with M&A activity in the environmental services sector, and how can companies like AutoStore mitigate these risks to ensure successful integrations?', 
        '10. How can environmental services companies like AutoStore use M&A to enhance their reputation and build trust with stakeholders, including regulatory bodies,
        customers, and investors, and what are the implications for their approval and licensing requirements?']

        ##### size : 10

        ztmp/tag_query/tag_query.parquet
        (10, 2)

        ######################################################################################################################################################################
        ##################################################################################################################################################################3###
        ######################################################################################################################################################################


        pyclean TagsIndustry process_industry --new_tag "pharma"


        ############## Add Tags ###################
        Starting industry processing...
        Loaded reference data:          dt family                industry  n_words  origin  priority
        0  20241003                             5g        1  L_cat2         2
        1  20241003                        5g tech        2  L_cat2         2
        2  20241003                       additive        2  L_cat2         2
        3  20241003          advanced air mobility        3  L_cat2         2
        4  20241003         advanced manufacturing        3  L_cat2         2
        ###################### Normalized Tag ####################
        industry  priority        dt  n_words family  origin
        0   pharma         2  20241026        1         L_cat2
        new tag counts : 1
        ############## Reference Data:          dt family                industry  n_words  origin  priority
        0  20241003                             5g        1  L_cat2         2
        1  20241003                        5g tech        2  L_cat2         2
        2  20241003                       additive        2  L_cat2         2
        3  20241003          advanced air mobility        3  L_cat2         2
        4  20241003         advanced manufacturing        3  L_cat2         2
        ############## New Industry Data:   industry  priority        dt  n_words family  origin
        0   pharma         2  20241026        1         L_cat2
        final tag counts : 14
        datasmall/ref/question_industry_ref.csv
        (14, 6)
        Industry processing completed successfully.



        ######################################################################################################################################################################
        ##################################################################################################################################################################3###
        ######################################################################################################################################################################
        

        py310            pyclean llm_query_extract_NER 

        ################# Extract Tags #################

        ###### msg_dict_raw:  {'reasoning': 'The question asks about how companies can leverage industry news and trends to identify potential M&A targets, and the role of
        #  coworking spaces in facilitating these connections. The entity extraction focuses on identifying relevant industry tags and activity tags related to M&A and coworking spaces.', '
        # task': ['unknown'], 'data_source': 'industry', 'date_period': '', 'date': [], 'company_names': [], 'industry_tags': [], 'activity_tags': ['m and a'], 
        # 'context': ['companies', 'leverage', 'industry', 'news', 'trends', 'identify', 'potential', 'targets', 'coworking', 'spaces', 'facilitating', 'connections'], 'display_tags': []}
     

        ##### query_tags_dict: {'reasoning': 'The question asks about how companies can leverage industry news and trends to identify potential M&A targets, 
        # and the role of coworking spaces in facilitating these connections. The entity extraction focuses on identifying relevant industry tags and activity 
        # tags related to M&A and coworking spaces.', 'task': ['unknown'], 'data_source': 'Eindustry', 'date_period': '', 'date': [], 'company_names': [], 
        # 'industry_tags': [], 'activity_tags': ['m and a'], 'context': ['companies', 'leverage', 'industry', 'news', 'trends', 'identify', 'potential', 'targets', 
        # 'coworking', 'spaces', 'facilitating', 'connections'], 'display_tags': []}

        ######################## catch error tags #######################
        referece tag : ['eli lilly', 'thales group'] 
        predicted tag : [] 

        referece tag : ['coworking'] 
        predicted tag : [] 

        #### Total Tags : 10


        ######################################################################################################################################################################
        ##################################################################################################################################################################3###
        ######################################################################################################################################################################

    

        py310            pyclean llm_create_finetune_json --dirin ztmp/generated_tag.parquet
        ###### Load Error Tags #################################
                                                        tag
        0  {'activity_tags': ['industry news', 'm and a']...
        1  {'activity_tags': ['industry news', 'm and a']...
        2  {'activity_tags': ['industry news', 'm and a']...
        3  {'activity_tags': ['industry news', 'm and a']...
        4  {'activity_tags': ['industry news', 'm and a']...
        ###### size : 10
        ###### Load data      #################################
                                                    question                                                tag
        0  How are coworking spaces adapting to the chang...  {'activity_tags': ['industry news', 'm and a']...
        1  What are the key challenges faced by companies...  {'activity_tags': ['industry news', 'm and a']...
        2  In what ways are industry trends in coworking ...  {'activity_tags': ['industry news', 'm and a']...
        3  How do coworking spaces foster innovation and ...  {'activity_tags': ['industry news', 'm and a']...
        4  What are the implications of increasing M&A ac...  {'activity_tags': ['industry news', 'm and a']...
        5  How can companies leverage industry news and t...  {'activity_tags': ['industry news', 'm and a']...
        6  What are the benefits and drawbacks of coworki...  {'activity_tags': ['industry news', 'm and a']...
        7  In what ways are companies like Thales Group a...  {'activity_tags': ['industry news', 'm and a']...
        8  How can the coworking industry respond to the ...  {'activity_tags': ['industry news', 'm and a']...
        9  What are the emerging trends in M&A that will ...  {'activity_tags': ['industry news', 'm and a']...
        ###### Create JSON Samples ###########################
        ###### Save JSON Samples ###########################
        ztmp/gpt_train/df_finetune_debug_20241026_211026.parquet
        (10, 6)
        ztmp/gpt_train/data_finetune.jsonl

"""



