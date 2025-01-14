"""
    Summary:
          Summary of each news article. + reference URL


    Eval of the summary ??
    Idea : Reverse  Queston:

      News Articles  : Merged manually 5 of them (Thruth).
           ---> Ask LLM to generate precise questions. ---> list of questions (store on disk).



          Use those questions --> Sumarizer ---> LLM summary (to evaluate)


          Ask LLM to compare the summary with reference text (that we know as reference).
             to find differences, innacurate facts.


          Pypi /  github: new cross check.
          Integer: 1 to 10,


       Step 1: think about pipelines as empty functions.

       1 row : 1 eval:
           df['text1', 'text2', 'text3', 'merge_text', 'question_list_from_llmn', ],



    Eval pipeline for Summarizer

       Check if summary is "correct"





os.environ['PYTHONPATH'] = "/Users/kevin.noel/gitdev/agen/gen_dev/aigen/src/engine/usea"




df2 = pd_text_chunks(df, sentence_chunk=30)


df2['n'] = df2['text_chunk'].str.len()
df['L4_cat']

def data_clean(df):
  return df


"""

if "import":
    from utilmy import log, pd_read_file, pd_to_file
    from box import Box
    from pydantic import BaseModel, Field
    import json
    import ast

    from rag.llm import LLM


    #from utils.utilmy_aws import pd_read_file_s3 





#######################################################################
def test1():
    # test



    df = run_eval_summary(dirin="ztmp/data/summary_20240906_093345_247.parquet",
                          nmax=10, text_col = "art2_text",summary_col = "text_summary")



def str_remove_html_tags(html_string):
    import re
    try:
       # Compile the regex pattern once for efficiency
       CLEANR = re.compile('<.*?>')    
       cleantext = re.sub(CLEANR, '', html_string)
       return cleantext
    except Exception as e:
       log(e)
       return html_string 
       


def str_clean(x):
  x = str(x).replace("https://", "").replace("datawrapper", "").replace(".dwcdn.net", "")
  return x


def date_get(ymd=None, add_days=0):
    y,m,d,h = date_now(ymd, fmt="%Y-%m-%d-%H", add_days= add_days).split("-")
    ts      = date_now(ymd, fmt="%Y%m%d_%H%M%S")
    return y,m,d,h,ts




def hash_text(x, nchars=200):
     from utilmy import hash_int64
     x1 = str( hash_int64(str(x)[:nchars] + f"-{len(str(x))}" ))
     return x1 


def textid_create(x, nchars=200, prefix="", nbucket=10**9):
     from utilmy import hash_int64
     x1 = hash_int64(str(x)[:nchars]) % nbucket

     if len(str(prefix)) > 0:
         x2 = f"{prefix}-{x1}-{len(str(x))}"
     else:
         x2 = f"{x1}-{len(str(x))}"

     return x2


def pd_add_textid(x, nchars=200, prefix="", nbucket=10**9):
    df2['text_id2'] = df2.apply( lambda x: textid_create(x[coltext], nchars=200, prefix="", nbucket=10**9) , axis=1 )



def pd_add_chunkid(df, coltextid="text_id2", nchars=200, prefix="", nbucket=10**9):
    df['chunk_id'] = df.groupby('text_id2').cumcount()
    df['chunk_id'] = df.apply( lambda x: f"{x['text_id2']}-{x['chunk_id']}", axis=1 )
    return df


def pd_text_chunks(df, coltext='text2', sentence_chunk=10):
    """ Split into block of 10 sentences. with title added

       'url', 'text_id', 'text', 'title'. --->.  'text_id', 'text',  'chunk_id',  'text_chunk'

    """
    def split_text_into_sentence_chunks(text, sentences_per_chunk=sentence_chunk):
        sentences = text.split('. ')
        return ['. '.join(sentences[i:i + sentences_per_chunk]) for i in range(0, len(sentences), sentences_per_chunk)]

    df['text_chunks'] = df[coltext].apply(split_text_into_sentence_chunks)

    df2 = df.explode('text_chunks').reset_index()
    df2 = df2.rename(columns={'text_chunks': 'text_chunk'})

    df2['text_id2'] = df2.apply( lambda x: textid_create(x[coltext], nchars=200, prefix="", nbucket=10**10) , axis=1 )
    df2['chunk_id'] = df2.groupby('text_id2').cumcount()
    df2['chunk_id'] = df2.apply( lambda x: f"{x['text_id2']}-{x['chunk_id']}", axis=1 )


    log(df2[['text_id2', 'chunk_id', 'text_chunk']])
    log("added cols:",['text_id2', 'chunk_id', 'text_chunk']  )
    return df2



##########################################################################
def run_question_create(cfg=None, cfg_name ="test01", dirin="./ztmp/test_df.parquet", 
                     dirout= "ztmp/data/arag/question_generated/", 
                     tag='marketsize' ,
                     nmax=4, npool=1, keeponly_msg=0,
                     llm_service='groq', llm_model='gemma2-9b-it', #'llama-3.1-70b-versatile',
                     n_questions = 5 , istest=1,
                     use_question=0,
                     text_col="text",summary_col="summary"):
    """ LLM Extractor

        nmax=4; npool=1; keeponly_msg=0;
        llm_service='groq'; llm_model='llama-3.1-70b-versatile',
        n_questions = 5; text_count = 3; istest=1;
        use_question=0;
        text_col="text"; summary_col="summary"
        os.environ["LLM_ROTATE_KEY"] ="1"
        dirout ="ztmp/data/arag/question_generated/"

       d1 = "src/engine/usea/"
       df = pd_read_file(d1 + "/df_edge_industry_marketsize.parquet")
       dirin = "ztmp/db/db_sqlite/df*marketsize.parquet"

       tag   = "insight" 
       dirin = f"ztmp/db/db_sqlite/df*{tag}.parquet"


       tag   = "overview" 



        dirout ="ztmp/data/arag/question_generated/"

        python rag/llm_eval.py summarize_metric_evaluation   --dirin  "./ztmp/data/test_df.parquet"

 
        cc.llm_service ="groq"
        cc.llm_model =  'gemma2-9b-it'

        cc.llm_service ="openai" 
        cc.llm_model = "gpt-4o-mini"

        cc.llm_service ="openai"
        cc.llm_model = "gpt-4o"


    """
    log("##### Load config #######################################################")
    from utilmy import config_load
    cfg0 = config_load(cfg)
    cfgd = cfg0.get(cfg_name, {})
    dirdata ="ztmp/data"

    dirin1 = dirdata + f"/db/aws/db_sqlite/df*{tag}.parquet"
    

    log("##### Params ##########################################################")
    cc = Box({})
    cc.n_questions = n_questions
    cc.llm_service = llm_service
    cc.llm_model   = llm_model
    llm_key        = None
    cc.istest      = istest
    keeponly_msg=0   if istest==0 else 1  ### for debugging
    log(cc)


    log("##### Load data #######################################################")
    ### ['L3_catid', 'L_cat', 'title', 'text_html', 'text_id', 'text', 'date','url', 'text_raw']
    ### overview: (['L_cat', 'L_catid', 'date', 'text', 'text_full', 'text_id', 'text_short', 'title', 'url'],
    df0 = pd_read_file(dirin1)
    log("df", df0, df0.columns)

    col_input = 'text_full'

    col_title = 'title'
    col_text  = 'text_chunk'
    col_indus = 'L_cat'


    df0['text2'] = df0[col_input].apply(lambda x: str_remove_html_tags(x) )
    df           = pd_text_chunks(df0, sentence_chunk=10, coltext='text2', colout='text_chunk')

    df[col_text] = df[col_text].apply(lambda x: str_clean(x) )
    df['n']      = df[col_text].str.len()
    log(df[[ col_text, col_indus, 'n', 'chunk_id' ]])


    log("##### LLM init  ######################################################")
    llm = LLM(service = cc.llm_service ,
                model = cc.llm_model,
                max_tokens=20000, 
             ) 

    log("##### LLM Generate  ####################################")
    output_schema = None

    ### pseudo function coded as english language
    prompt = """
       You are a market researcher, writing a market research report for executives.
       Based on the text reference below, generate 20 questions related 
       to this industry "<industry_name>" .

       ** Important:  **
          Question must include this industry name : <industry_name>
          Answer of the question should be extracted only from the text reference.
          Do not use your own knowledge for the answer.

       ## Output follows this JSON records format:
         [  {"question" :  "question related to text reference"
             "answer": "extracted answer"
            }
        ]

        ## Text reference:
        <title>.
        <text_reference>
    """
    #### Static
    #  prompt = prompt_align_question.format( n_q= cc.n_questions )


    #### Mapping the prompt with actual variables
    prompt_map_dict = { "<title>" : col_title,
                        "<text_reference>": col_text,
                        "<industry_name>":  col_indus
                      }

    kbatch = 10
    df2 = df.iloc[:nmax]
    mbatch = len(df2) // kbatch
    for kk in range(0, mbatch+1):
        dfk = df2.iloc[kk*kbatch: (kk+1)*kbatch, : ]
        if len(dfk)< 1: break
        log(kk, dfk.shape)

        df1 = llm.get_batch_df(dfk, prompt, prompt_map_dict, 
                              dirout=None, npool=npool ,
                              keeponly_msg = keeponly_msg,
                              output_schema= output_schema ) ### custom parser in LLM class

        log(df1.head(1).T)
        log(df1['llm_msg'].values[0])

        df1['question_list'] = df1['llm_msg'].apply(lambda x: str(x).replace("```",""))
        df1['question_list'] = df1['question_list'].apply(lambda x: str(x).replace("json\n",""))
        del df1['llm_msg']

        y,m,d,h,ts = date_get()
        pd_to_file(df1, dirout + f"/{tag}/df_question_list_{tag}_{ts}_{len(df1)}.parquet")



def json_load2(x):
   try: 
      return json.loads(str(x))
   except Exception as e:
      log(e)
      return {}   


def run_question_clean(cfg=None, cfg_name ="test01", dirin="./ztmp/test_df.parquet", 
                     dirout= "ztmp/data/arag/question_generated/", 
                     tag='marketsize' ,
                     nmax=4, npool=1, keeponly_msg=0,istest=1,
                     text_col="text",summary_col="summary"):
    """ LLM Extractor

        nmax=4; npool=1; keeponly_msg=0;
        llm_service='groq'; llm_model='llama-3.1-70b-versatile',
        n_questions = 5; text_count = 3; istest=1;
        use_question=0;
        text_col="text"; summary_col="summary"

    """
    log("##### Load config #######################################################")
    from utilmy import config_load
    cfg0 = config_load(cfg)
    cfgd = cfg0.get(cfg_name, {})
    dirdata="ztmp/data"
    
    
    log("##### Params ############################################################")
    cc = Box({})
    cc.istest      = istest
    log(cc)

    # tag = "marketsize" 
    dirin1 = dirdata + f"/arag/question_generated/{tag}/*.parquet"
    df = pd_read_file(dirin1)
    ## ['L3_catid', 'L_cat', 'date', 'question_list', 'text', 'text_html', 'text_id', 'text_raw', 'title', 'url'],
    

    df['question_list'] = df['question_list'].apply(lambda x: str(x).replace("```","").replace("json\n",""))
    df['question_list2'] = df['question_list'].apply(lambda x: json_load2(x) )

    df2 = df[df['question_list2'].apply(lambda x: len(x)>0 )  ] 

    df2 = df2.explode('question_list2').reset_index()
    df2 = df2.rename(columns={'question_list2': 'qa'})

    df2['question'] = df2['qa'].apply(lambda x: x['question']  )
    df2['answer']   = df2['qa'].apply(lambda x: x['answer']  )

   
    dirin2 = dirdata + f"/arag/question_generated/aclean"
    y,m,d,h,ts = date_get()
    pd_to_file(df2, dirin2 + f"/{tag}/df_qa_clean_{tag}_{ts}_{len(df2)}.parquet")

    ## Index(['index', 'L3_catid', 'L_cat', 'date', 'question_list', 'text', 'text_html', 'text_id', 'text_raw', 'title', 'url', 'qa', 'question',
    ##   'answer'],

    cols2 = [ 'url', 'L_cat', 'question', 'answer', ] 
    df3 = df2[ -df2['answer'].str.contains("http") ]
    df3 = df3[ -df3['answer'].str.contains("text does not") ]

    pd_to_file(df3[cols2], dirin2 + f"/{tag}/df_qa_analyst_{tag}_{ts}_{len(df2)}.csv", sep="\t" )




def run_question_validate(cfg=None, cfg_name ="test01", dirin="./ztmp/test_df.parquet", 
                     dirout= "ztmp/data/arag/question_generated/", 
                     tag='marketsize' ,
                     nmax=4, npool=1, keeponly_msg=0,
                     llm_service='groq', llm_model='gemma2-9b-it', #'llama-3.1-70b-versatile',
                     n_questions = 5 , istest=1,
                     use_question=0,
                     text_col="text",summary_col="summary"):
    """ LLM Extractor


        nmax=4; npool=1; keeponly_msg=0;
        llm_service='groq'; llm_model='llama-3.1-70b-versatile',
        n_questions = 5; text_count = 3; istest=1;
        use_question=0;
        text_col="text"; summary_col="summary"


       d1 = "src/engine/usea/"
       df = pd_read_file(d1 + "/df_edge_industry_marketsize.parquet")
       dirin = "ztmp/db/db_sqlite/df*marketsize.parquet"

       tag   = "insight" 
       dirin = f"ztmp/db/db_sqlite/df*{tag}.parquet"


       tag = "marketsize" 
       dirin = f"ztmp/db/db_sqlite/df*{tag}.parquet"

        dirout ="ztmp/data/arag/question_generated/"
        os.environ["LLM_ROTATE_KEY"] ="1"


        python rag/llm_eval.py summarize_metric_evaluation   --dirin  "./ztmp/data/test_df.parquet"


        cc.llm_service ="groq"
        cc.llm_model =  'gemma2-9b-it'


        cc.llm_service ="groq"
        cc.llm_model =  "llama3-8b-8192"


          llama3_70b_8192 = "llama3-70b-8192"
          llama3_8b_8192  = "llama3-8b-8192"
          llama31_8b_instant = 'llama-3.1-8b-instant'
          gemma_7b_it     = 'gemma-7b-it'
          llama31_70b     = "llama-3.1-70b-versatile"

        cc.llm_model = "gpt-4o-mini"
        cc.llm_service ="openai"

        cc.llm_model = "gpt-4o"
        cc.llm_service ="openai"


    """
    log("##### Load config #######################################################")
    from utilmy import config_load
    cfg0 = config_load(cfg)
    cfgd = cfg0.get(cfg_name, {})
    dirdata="ztmp/data"

    dirout1 = dirdata + "/arag/question_generated/zcheck"
    
    
    log("##### Params ############################################################")
    cc = Box({})
    cc.llm_service = llm_service
    cc.llm_model   = llm_model
    llm_key        = None
    cc.istest      = istest
    keeponly_msg=0   if istest==0 else 1  ### for debugging
    log(cc)


    log("##### Load data #######################################################")
    dirin1 = dirdata + f"/arag/question_generated/aclean/{tag}/*.parquet"
    df = pd_read_file(dirin1)
    ### ['L3_catid', 'L_cat', 'title', 'text_html', 'text_id', 'text', 'date','url', 'text_raw']

    col_title = "title"
    col_text  = 'text_chunk'
    col_indus = 'L_cat'
    col_query = "question"

    if 'text_chunk' not in df.columns:
        df['text_chunk'] = df['text']


    log("##### LLM init  #####################################################")
    llm = LLM(service = cc.llm_service ,
                model = cc.llm_model,
                max_tokens=20000, 
             ) 

    log("##### LLM Generate  ####################################")
    output_schema = None

    def clean1(x):
        x = str(x).replace("```","").replace("json\n","")
        x = x.replace("Here is the extracted answer to the question:", "")
        return x
        

    ### pseudo function coded as english language
    prompt = """
       You are a market researcher, writing a market report for executives
       in this industry: "<industry_name>".
       Based on the text reference below, provide answers to the question.

       ** Important rules **:  
          Answer should be extracted only from the text reference.

       ### Output as JSON list without any extra comment:
         [ "extracted answer 1", "extracted answer 2", "extracted answer 3",
         ]
        
       ### Question:
         <question> 

       ### Text reference:
           <title>.
           <text_reference>

    """

    #### Mapping the prompt with actual variables
    prompt_map_dict = { "<title>" :     col_title,
                        "<question>" :  col_query,

                        "<text_reference>": col_text,
                        "<industry_name>":  col_indus
                      }

    kbatch = 10
    df2    = df.iloc[:nmax]
    mbatch = len(df2) // kbatch
    for kk in range(0, mbatch+1):
        dfk = df2.iloc[kk*kbatch: (kk+1)*kbatch, : ]
        if len(dfk)< 1: break
        log(kk, dfk.shape)

        df1 = llm.get_batch_df(dfk, prompt, prompt_map_dict, 
                              dirout=None, npool=npool ,
                              keeponly_msg = 1,
                              output_schema= output_schema ) ### custom parser in LLM class

        log(df1.head(1).T)
        log(df1['llm_msg'].values[0])
        df1['answer_list'] = df1['llm_msg'].apply(lambda x: clean1(x) )
        del df1['llm_msg']

        y,m,d,h,ts = date_get()
        pd_to_file(df1, dirout1 + f"/{tag}/df_answer_check_{tag}_{ts}_{len(df1)}.parquet")









##########################################################################
def run_eval_summary(cfg=None, cfg_name ="test01", dirin="./ztmp/test_df.parquet", dirout= "ztmp/data/out", nmax=4, npool=1, keeponly_msg=0,
                     llm_service='groq', llm_model='llama-3.1-70b-versatile',
                     n_questions = 5 , text_count = 3, istest=1,
                     use_question=0,
                     text_col="text",summary_col="summary"):
    """ LLM Extractor

        python rag/llm_eval.py summarize_metric_evaluation   --dirin  "./ztmp/data/test_df.parquet"
        print( os.environ['GROQ_KEY'] )  # by LLM class

              ----------------------- Based on deepeveal summarization metric: (https://www.confident-ai.com/blog/a-step-by-step-guide-to-evaluating-an-llm-text-summarization-task)

              Problem :
              - Given a text or [text] and a sumamry -> generate an evaluation score
              Solution :
              - compute two scores : Coverage (texts -> summary) and align (summary -> texts)
              - final score is min(coverage_score,align_score)

              Details:
              - coverage score?
              step 1 : given text or [texts] generate (n) questions that always answer -yes-
              step2 : given sumary as context generate answer for questions (yes/no/idk) - penalize only idk questions

              - align score? (measure hallu)
              step 1 : geerate claims from summary
              step 2 : give sumary and sumary as inputs and outiput a dict of verified summary claims (yes,no,idk) with reason

              check https://github.com/confident-ai/deepeval/blob/c12640acb7d6b03d7ebc763e8b08d93259ddab82/deepeval/metrics/summarization/template.py for prompts.


              NB: the metric is created to work on one article we can either loop over articles and average the score or feed them as one big article ?

    """
    log("##### Load config #######################################################")
    from utilmy import config_load
    cfg0 = config_load(cfg)
    cfgd = cfg0.get(cfg_name, {})



    log("##### Params ##########################################################")
    cc = Box({})
    cc.n_questions            = n_questions
    cc.llm_service = llm_service
    cc.llm_model   = llm_model
    llm_key        = None
    cc.istest      = istest
    keeponly_msg=0   if istest==0 else 1  ### for debugging


    log("##### Load data #######################################################")
    df = pd_read_file(dirin)
    df = df.iloc[:nmax, :]
    df = df[[text_col,summary_col]]


    log("##### LLM init  #######################################################")
    llm = LLM(service = cc.llm_service ,
              api_key = llm_key , ### print( os.environ['GROQ_KEY'] )
              model   = cc.llm_model ) # "llama-3.1-70b-versatile" )


    log("##### LLM Extract align questions ####################################")
    if "llm_msg_align_questions_parsed" in df.columns and use_question >0 :
        ### you can try LLM class own JSON parser... it should work
        class questionJSON(BaseModel):
            """ {  "questions": [ "myquestion", "summarize" ] }
            """
            ### Trick to improve accuracy.
            #reasoning: str = Field(description=" Summarize in 2 sentences your reasoning on this entity extraction.")
            question: list = Field(description="list of closed-ended questions")
        questionJSON = None


        ### pseudo function coded as english language
        #    Only return a JSON with a 'questions' key, which is a list of strings.
        prompt_align_question = """Based on the given text, generate 10 closed-ended questions that can be answered with either a 'yes' or 'no'. 
       The questions generated should ALWAYS result in a 'yes' or 'no' based on the given text. 

       ** IMPORTANT

       The questions have to be STRICTLY closed ended.
       The given text should be able to answer 'yes' for each question.
       in your answer only output a json with this schema: {"questions":[question_1,question_2,...]}
       **
       Text:
       <prompt_text>

       QUESTIONS:
       """

        ### Static
        #  prompt_align_question = prompt_align_question.format( n_q= cc.n_questions )

        ### map <. Placeholder  >. with dataframe column "text'"
        prompt_map_dict = {"<prompt_text>": text_col}

        df = llm.get_batch_df(df, prompt_align_question, prompt_map_dict, dirout=None, npool=npool ,
                              keeponly_msg = keeponly_msg,
                              output_schema= questionJSON ) ### custom parser in LLM class

        ### Rename columns
        cols_llm = [ 'llm_prompt', 'llm_json', 'llm_msg' ]
        df       = pd_col_rename(df, cols_llm, suffix="_align_questions", prefix=None)
        df["llm_msg_align_questions_parsed"] = df["llm_msg_align_questions"].apply(parse_questions)
        pd_to_file(df, dirout +"/df_question_only.parquet")



    log("##### LLM Extract Answers summary,quesions -> answers  ##############################")
    prompt_align_answers="""
            Based on the list of close-ended 'yes' or 'no' questions, generate a JSON with key 'answers', which is a list of strings that determines whether the provided text contains sufficient information to answer EACH question.
        Answers should STRICTLY be either 'yes' or 'no'.
        Answer 'no' if the provided text does not contain enough information to answer the question.
        **
        IMPORTANT: Please make sure to only return in JSON format, with the 'answers' key as a list of strings.

        Example:
        Example Text: Mario and Luigi were best buds but since Luigi had a crush on Peach Mario ended up killing him.
        Example Questions: ["Are there enough information about Luigi and Mario?"]
        Example Answers:
        {{
            "answers": ["yes"]
        }}

        The length of 'answers' SHOULD BE STRICTLY EQUAL to that of questions.
        ===== END OF EXAMPLE ======

        Text:
        <summary>

        Questions:
        <questions>

        JSON:
   """


    #### Dynamic:  map <. Placeholder  >. with dataframe column "text'"
    prompt_map_dict = {"<summary>": summary_col,
                       "<questions>": "llm_msg_align_questions_parsed"}

    df = llm.get_batch_df(df, prompt_align_answers,
                          prompt_map_dict, dirout=None, npool=npool ,keeponly_msg = keeponly_msg )

    ###### Normalized columns
    cols_llm = [ 'llm_prompt', 'llm_json', 'llm_msg' ]
    df       = pd_col_rename(df, cols_llm, suffix="_align_answers", prefix=None)


    log("########## parse and compute allignment scorre  ###################################")
    # parse answers
    df["llm_msg_align_answers_parsed"] = df["llm_msg_align_answers"].apply(parse_answers)
    df["llm_msg_align_score"]          = df["llm_msg_align_answers_parsed"].apply(compute_allignment_score)


    log("########## hallu score  ##########################################################")
    prompt_hallu = """Based on the given summary, generate a list of JSON objects to indicate whether EACH piece of info contradicts any facts in the original text. The JSON will have 2 fields: 'verdict' and 'reason'.
         The 'verdict' key should STRICTLY be either 'yes', 'no', or 'idk', which states whether the given summary claim agrees with the original text. 
         The provided summary claims is drawn from the summary. Try to provide a correction in the reason using the facts in the original text.

         **
         IMPORTANT: Please make sure to only return in JSON format, with the 'verdicts' key as a list of JSON objects.
         Example Original Text: "Einstein won the Nobel Prize for his discovery of the photoelectric effect. Einstein won the Nobel Prize in 1968. Einstein is a German Scientist."
         Example Summary: "Barack Obama is a caucasian male. Zurich is a city in London Einstein won the Nobel Prize for the discovery of the photoelectric effect which may have contributed to his fame. Einstein won the Nobel Prize in 1969 for his discovery of the photoelectric effect. Einstein was a Germen chef."

         Example:
         {{
            "verdicts": [
               {{
                     "verdict": "idk",
                     "reason": "The original text does not mention Barack Obama at all, let alone his racial features.
               }},
               {{
                     "verdict": "idk",
                     "reason": "The original text does not mention Zurich, not does it mention Zurich being in London".
               }},
               {{
                     "verdict": "yes"
                     "reason": "the text mentions : Einstein won the Nobel Prize for his discovery of the photoelectric effect."
               }},
               {{
                     "verdict": "no",
                     "reason": "The summary claims Einstein won the Nobel Prize in 1969, which is untrue as the original text states it is 1968 instead."
               }},
               {{
                     "verdict": "no",
                     "reason": "The summary claims Einstein is a Germen chef, which is not correct as the original text states he was a German scientist instead."
               }},
            ]  
         }}
         ===== END OF EXAMPLE ======

         ONLY provide a 'no' answer if the summary DIRECTLY CONTRADICTS the claims. YOU SHOULD NEVER USE YOUR PRIOR KNOWLEDGE IN YOUR JUDGEMENT.
         Claims made using vague, suggestive, speculative language such as 'may have', 'possibility due to', does NOT count as a contradiction.
         Claims that is not backed up due to a lack of information/is not mentioned in the summary MUST be answered 'idk', otherwise I WILL DIE.
         **

         Original Text:
         <orignal_text>

         Summary:
         <summary>

         JSON:
         """
    prompt_map_dict = {"<summary>":      summary_col,
                       "<orignal_text>": text_col}

    df = llm.get_batch_df(df, prompt_hallu,
                          prompt_map_dict, dirout=None, npool=npool ,keeponly_msg = keeponly_msg )

    ###### Normalized columns
    cols_llm = [ 'llm_prompt', 'llm_json', 'llm_msg' ]
    df       = pd_col_rename(df, cols_llm, suffix="_hallu_answers", prefix=None)


    log("########## parse and compute hallu scorre  #########################################")
    # parse answers
    df["llm_msg_hallu_answers_parsed"] = df["llm_msg_hallu_answers"].apply(parse_hallu_answers)
    df["llm_msg_hallu_answers_score"] =  df["llm_msg_hallu_answers_parsed"].apply(compute_hallu_score)


    log("########## create flagged df (filtered view) #######################################")
    df_errs = pd_eval_get_bad_(df,text_col=text_col, summary_col=summary_col)

    log("########## Write data   #######################################")
    if isinstance(dirout, str):
        from utilmy import date_now
        ts = date_now(fmt="%y%m%d_%H%M%S")
        pd_to_file(df, dirout + f"/df_eval_{ts}_{len(df)}.parquet")
        pd_to_file(df_errs, dirout + f"/df_eval_errors_{ts}_{len(df_errs)}.parquet")

        if istest==1:
            pd_to_file(df.iloc[:10,:], dirout + f"/df_eval_{ts}_{len(df)}.csv", sep="\t")
            pd_to_file(df_errs.iloc[:10,:], dirout + f"/df_eval_errors_{ts}_{len(df_errs)}.csv", sep="\t")

    return df








############################################################################
#####  Helper functions ####################################################
def pd_col_rename(df, cols, suffix=None, prefix=None):

    suffix = "" if suffix is None else suffix
    prefix = "" if prefix is None else prefix
    # cols_llm = [ 'llm_prompt', 'llm_json', 'llm_msg' ]
    for ci in cols :
        if ci not in df.columns : continue
        cinew = f"{prefix}{ci}{suffix}"
        df[cinew ] = df[ci]
        log(ci, cinew)
        del df[ci]
    return df


def parse_json(text: str):
    try:
        parsed_json = json.loads(text)
        return parsed_json
    except json.JSONDecodeError as e:
        print(f"JSON Parsing failed with error: { e.msg}")
        print(f"FAULTY JSON: {text}")
        return None


def parse_questions(question_ans,istest=True):

    response = question_ans.replace("```", '')
    json_data = parse_json(response)
    if json_data:
        # test
        return str(json_data["questions"])
    return ""


def parse_answers(answers_ans,istest=True):

    response = answers_ans.replace("```", '')
    json_data = parse_json(response)
    if json_data:
        return json_data["answers"]
    return []


def compute_allignment_score(answer_list):
    if len(answer_list) == 0: # parsing problem !
        return -1
    return sum([1 if ans=="yes" else 0 for ans in answer_list ]) / len(answer_list)


def parse_hallu_answers(answers_ans,istest=True):

    response = answers_ans.replace("```", '')
    json_data = parse_json(response)
    if json_data:
        # test
        return json_data["verdicts"]
    return []


def compute_hallu_score(answer_list):
    if len(answer_list) == 0: # parsing problem !
        return -1
    return sum([1 if ans["verdict"]=="yes" else 0 for ans in answer_list ]) / len(answer_list)






def pd_eval_get_bad_(df, text_col='text',summary_col='summary', dirout=None):
  def extract_qa_bad(x):
        questions, answers = x.llm_msg_align_questions_parsed, x.llm_msg_align_answers_parsed
        questions = ast.literal_eval(questions)
        return [(question, answer) for question, answer in zip(questions, answers) if answer == "no"]

  def extract_verdicts_bad(verdicts):
        # print(verdicts)
        return [verdict["reason"] for verdict in verdicts if verdict["verdict"] == "no"]


  df = df[[text_col,summary_col,"llm_msg_align_questions_parsed","llm_msg_align_answers_parsed","llm_msg_hallu_answers_parsed"]]
  df["llm_msg_align_bad"]    = df.apply(lambda x: extract_qa_bad(x), axis=1)
  df["llm_msg_verdicts_bad"] = df.apply(lambda x: extract_verdicts_bad(x.llm_msg_hallu_answers_parsed ), axis=1)

  df = df[[text_col,summary_col,"llm_msg_align_bad", "llm_msg_verdicts_bad"]]
  return df



# to be run on each row in out test_df - we will use adhere to batch_Df ..


###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()






