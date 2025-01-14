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
import warnings
warnings.simplefilter(action='ignore')

if "import":
    from box import Box
    from pydantic import BaseModel, Field
    import json, pandas as pd, numpy as np, ast

    from rag.llm import LLM


    from utilmy import log, pd_read_file, pd_to_file, date_now, json_load, json_save, glob_glob

    from utils.util_text import (pd_add_chunkid_int, pd_add_textid, pd_text_chunks, str_remove_punctuation,
                 pd_add_chunkid

        )

    from copy import deepcopy

    #from utils.utilmy_aws import pd_read_file_s3 



###########################################################################
def test1():
    # test



    df = run_eval_summary(dirin="ztmp/data/summary_20240906_093345_247.parquet",
                          nmax=10, text_col = "art2_text",summary_col = "text_summary")




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

        cfg=None ;  cfg_name ="test01"
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
       tag   = "overview" 
       tag  ='insight'



        dirout ="ztmp/data/arag/question_generated/"

        python rag/llm_eval.py summarize_metric_evaluation   --dirin  "./ztmp/data/test_df.parquet"

          llama31_8b_instant = 'llama-3.1-8b-instant'
          gemma_7b_it     = 'gemma-7b-it'
          llama31_70b     = "llama-3.1-70b-versatile"

 
        cc.llm_service ="groq" ; cc.llm_model =  'gemma2-9b-it'

        cc.llm_service ="groq" ; cc.llm_model =  "llama3-70b-8192"

        cc.llm_service ="groq" ; cc.llm_model =  "llama3-8b-8192"

        cc.llm_service ="groq" ; cc.llm_model =  'gemma-7b-it'


        cc.llm_service ="openai"  ; cc.llm_model = "gpt-4o-mini"

        cc.llm_service ="openai" ; cc.llm_model = "gpt-4o"


    """
    log("##### Load config #######################################################")
    from utilmy import config_load
    cfg0 = config_load(cfg)
    cfgd = cfg0.get(cfg_name, {})
    dirdata ="ztmp/data"


    

    log("##### Params ##########################################################")
    cc = Box({})
    cc.n_questions = n_questions
    cc.llm_service = llm_service
    cc.llm_model   = llm_model
    llm_key        = None
    cc.istest      = istest
    keeponly_msg   = 0   if istest==0 else 1  ### for debugging
    log(cc)


    log("##### Load data #######################################################")
    ### ['L3_catid', 'L_cat', 'title', 'text_html', 'text_id', 'text', 'date','url', 'text_raw']
    ### overview: (['L_cat', 'L_catid', 'date', 'text', 'text_full', 'text_id', 'text_short', 'title', 'url'],
    dirin1 = dirdata + f"/db/db_sqlite/df*{tag}.parquet"
    df0 = pd_read_file(dirin1)
    log("df", df0, df0.columns)

    if 'text_full' not in df0.columns:
       df0 = df0.rename(columns={  'text_html' : 'text_full'  })

    col_input = 'text_full'

    col_title = 'title'
    col_text  = 'text_chunk'
    col_indus = 'L_cat'


    df0['text2'] = df0[col_input].apply(lambda x: str_remove_html_tags(x) )
    df           = pd_text_chunks(df0, sentence_chunk=10, coltext='text2', colout='text_chunk')

    df[col_text] = df[col_text].apply(lambda x: str_clean(x) )
    df['n']      = df[col_text].str.len()
    log(df[[ col_text, col_indus, 'n', 'chunk_id' ]])


    log("##### LLM init  #############################################")
    llm = LLM(service = cc.llm_service , model = cc.llm_model,
              max_tokens=16384 , 
             ) 

    log("##### LLM Prompt  ###########################################")
    output_schema = None

    ### pseudo function coded as english language
    prompt = PROMPTS["question_create_v3"]

    #### Mapping the prompt with actual variables
    prompt_map_dict = { "<title>"         : col_title,
                        "<text_reference>": col_text,
                        "<industry_name>":  col_indus
                      }
    assert prompt_validate(prompt, prompt_map_dict),"Missing variable"
    log(df[prompt_map_dict.values() ].shape)


    log("##### LLM Generate  ########################################")
    def clean1(x):
        x = str(x).replace("```","").replace("json\n","")
        x = x.replace("Here is the extracted answer to the question:", "")
        return x


    kbatch = 20
    df2    = df.iloc[:nmax]
    mbatch = len(df2) // kbatch
    ymd    = date_now(fmt="%y%m%d")    
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
        df1['model'] = f"{cc.llm_service}_{cc.llm_model}"
        df1['tag']   = tag 

        df1['question_list'] = df1['llm_msg'].apply(lambda x: clean1(x) )
        del df1['llm_msg']

        y,m,d,h,ts = date_get()
        pd_to_file(df1, dirout + f"/{tag}/{ymd}/df_qa_list_{tag}_{ts}_{kk}_{len(df1)}.parquet")






def run_question_create_ext(cfg=None, cfg_name ="test01", dirin="./ztmp/test_df.parquet", 
                     dirout= "ztmp/data/arag/question_generated/", 
                     tag='marketsize' ,
                     nmax=4, npool=1, keeponly_msg=0,
                     llm_service='groq', llm_model='gemma2-9b-it', #'llama-3.1-70b-versatile',
                     n_questions = 5 , istest=1,
                     use_question=0,
                     text_col="text",summary_col="summary"):
    """ LLM Extractor

        cfg=None ;  cfg_name ="test01"
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

        dirout ="ztmp/data/arag/question_generated/"

        python rag/llm_eval.py summarize_metric_evaluation   --dirin  "./ztmp/data/test_df.parquet"

          llama31_8b_instant = 'llama-3.1-8b-instant'
          gemma_7b_it     = 'gemma-7b-it'
          llama31_70b     = "llama-3.1-70b-versatile"

 
        cc.llm_service ="groq" ; cc.llm_model =  'gemma2-9b-it'
        cc.llm_service ="groq" ; cc.llm_model =  "llama3-70b-8192"
        cc.llm_service ="groq" ; cc.llm_model =  "llama3-8b-8192"
        cc.llm_service ="groq" ; cc.llm_model =  'gemma-7b-it'


        cc.llm_service ="openai"  ; cc.llm_model = "gpt-4o-mini"

        cc.llm_service ="openai" ; cc.llm_model = "gpt-4o"


    """
    log("##### Load config #######################################################")
    from utilmy import config_load
    cfg0    = config_load(cfg)
    cfgd    = cfg0.get(cfg_name, {})
    dirdata ="ztmp/data"


    log("##### Params ##########################################################")
    cc = Box({})
    cc.n_questions = n_questions
    cc.llm_service = llm_service
    cc.llm_model   = llm_model
    llm_key        = None
    cc.istest      = istest
    keeponly_msg   = 0   if istest==0 else 1  ### for debugging
    log(cc)


    log("##### Load data #######################################################")
    ### ['L3_catid', 'L_cat', 'title', 'text_html', 'text_id', 'text', 'date','url', 'text_raw']
    ### overview: (['L_cat', 'L_catid', 'date', 'text', 'text_full', 'text_id', 'text_short', 'title', 'url'],
    dirin1 = dirdata + f"/db/db_sqlite/df*{tag}.parquet"
    df0 = pd_read_file(dirin1)
    log("df", df0, df0.columns)

    df = df0.drop_duplicates(['L_cat'])

    col_title   = 'title'
    col_indus   = 'L_cat'
    col_text    = 'text_ext'
    col_topic   = 'topic'

    df['topic']    = df.apply( lambda x:  f""" {x['L_cat']}  industry and market trend related to companies. """ , axis=1)
    df['text_ext'] = df.apply(lambda x: get_data_v3(x['topic'])[0] , axis=1)
    log(df[[ col_text, col_indus, ]])


    y,m,d,h,ts = date_get()
    pd_to_file(df, dirout + f"/custom/df_industry_addon_webcontext_{tag}_{ts}_{len(df)}.parquet")



    log("##### LLM init  #############################################")
    llm = LLM(service = cc.llm_service , model = cc.llm_model,
              max_tokens=16384 , 
             ) 

    log("##### LLM Prompt  ###########################################")
    output_schema = None

    ### pseudo function coded as english language
    prompt = PROMPTS["question_create_v4"]

    #### Mapping the prompt with actual variables
    prompt_map_dict = { "<topic>"         : col_topic,
                        "<text_reference>": col_text,
                        "<industry_name>":  col_indus
                      }
    assert prompt_validate(prompt, prompt_map_dict),"Missing variable"
    log(df[prompt_map_dict.values() ].shape)


    log("##### LLM Generate  ########################################")
    def clean1(x):
        x = str(x).replace("```","").replace("json\n","")
        x = x.replace("Here is the extracted answer to the question:", "")
        return x


    kbatch = 5
    df2    = df.iloc[:nmax]
    mbatch = len(df2) // kbatch
    ymd    = date_now(fmt="%y%m%d")    
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
        df1['model'] = f"{cc.llm_service}_{cc.llm_model}"
        df1['tag']   = tag 

        df1['question_list'] = df1['llm_msg'].apply(lambda x: clean1(x) )
        del df1['llm_msg']

        y,m,d,h,ts = date_get()
        pd_to_file(df1, dirout + f"/custom/{ymd}/df_qa_list_{tag}_{ts}_{kk}_{len(df1)}.parquet")





def run_question_clean(cfg=None, cfg_name ="test01", dirin="./ztmp/test_df.parquet", 
                     dirout= "ztmp/data/arag/question_generated/", 
                     tag='marketsize' ,
                     nmax=4, istest=1,):
    """ LLM Extractor

        nmax=4; npool=1; keeponly_msg=0;
        llm_service='groq'; llm_model='llama-3.1-70b-versatile',
        n_questions = 5; text_count = 3; istest=1;
        use_question=0;
        text_col="text"; summary_col="summary"

        tag="custom/241125"

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

    tag2 = tag.split("/")[0]
    dirin1 = dirdata + f"/arag/question_generated/{tag}/*.parquet" 
    df = pd_read_file(dirin1)
    log(df)
    ## ['L3_catid', 'L_cat', 'date', 'question_list', 'text', 'text_html', 'text_id', 'text_raw', 'title', 'url'],

    def clean1(x):
       xl = str(x).split("\n[")
       
       if len(xl)>1:
           x1 = "[" + " ".join(xl[1:])
       else:
           x1 = x 

       xl = x1.split("]\n]\n")
       if len(xl)>1:
           x1 = xl[0] + "]\n]\n"

       x1 = x1.replace("```","").replace("json\n","")
       x1 = x1.strip()
       return x1       

    df['question_list2'] = df['question_list'].apply(lambda x:  clean1(x) )    
    df['question_list2'] = df['question_list2'].apply(lambda x: json_load2(x) )

    df2 = df[df['question_list2'].apply(lambda x: len(x)>0 )  ] 

    df2 = df2.explode('question_list2').reset_index()
    df2 = df2.rename(columns={'question_list2': 'qa'})

    df2['question'] = df2['qa'].apply(lambda x: x[0] if len(x)>1 else x[0].split(",")[0] )
    df2['answer']   = df2['qa'].apply(lambda x: x[1] if len(x)>1 else x[0].split(",")[-1] )

    def clean3(x):
       if ";work;" in x: 
           return  x.replace(";", " ")
       else: 
           x1 = x.split(";")
           xx = f" {x1[0]}  {x[-1]}"
           return xx

    df2['question']   = df2['question'].apply(lambda x: clean3(x)  )
    df2 = df2.drop_duplicates([ 'question', 'answer' ])

   
    y,m,d,h,ts = date_get()
    dirin2     = dirdata + f"/arag/question_generated/zaclean"
    pd_to_file(df2, dirin2 + f"/{tag}/df_qa_all_{tag2}_{ts}_{len(df2)}.parquet")

    ## Index(['index', 'L3_catid', 'L_cat', 'date', 'question_list', 'text', 'text_html', 'text_id', 'text_raw', 'title', 'url', 'qa', 'question',
    ##   'answer'],

    df3 = df2[ -df2['answer'].str.contains("http") ]
    df3 = df3[ -df3['answer'].str.contains("text does not") ]
    df3 = df3[ -df3['answer'].str.contains(" does not contain") ]
    pd_to_file(df3, dirin2 + f"/{tag}/df_qa_clean_{tag2}_{ts}_{len(df3)}.parquet" )


    cols2 = [ 'url', 'L_cat', 'question', 'answer', ] 
    if ";" in df3['L_cat'].values[0]:
        df3['L_catfull'] = df3['L_cat']
        df3['L_cat'] = df3['L3_cat']

    noutput = 6000
    df4 = df3[cols2].sample(n= noutput).sort_values(['L_cat'])
    pd_to_file(df4, dirin2 + f"/{tag}/df_qa_analyst_{tag2}_{ts}_{noutput}.csv", sep="\t" )





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

       For each (question, answer) pair, 
           ( "FromContext", "correct"   ) if the answer is extracted from context and is valid.
           ( "FromContext", "incorrect" )
           ( "Not Context", "correct"   )
           ( "Not Context", "incorrect" )
            


       ## Question,answer pairs
           <question_answer>



       ## Context
           <text_reference>

       ### Output as JSON list without any extra comment:
         [ 
         ]
        

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



PROMPTS = {
  
    "question_create_v1" : """
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



    ,"question_create_v2" : """
           You are a market researcher, writing a market research report for executives, 
           with those topics: <industry_name> and <title>.
           Generate 10 questions whose answer is given by the text below:


           ** Important **:
             Question formulation should strictly match the answer.

           ## Answer
              <text_reference>


           ## Output follows this JSON list format:
             [  "question1",  "question2", "question3", ]


      """


  ,"question_create_v3": """
      You are a market researcher, writing a market research report 
      for executives on this topic: "<industry_name>".

       Generate 20  questions and long answers pairs based on the context below.
      *Important*: 
           Question must include this industry name "<industry_name>".
           Answer should be 3 lines long and refer strictly from the context below.
           Do not use your own knowledge for the answer response.


       ## Context:
          <text_reference>

       ## Output follows this JSON list format:
               [  ["question1",  "answer1"]
                  [ "question2", "answer2"],    
                  ... 
              ]

   """



   #### External source.
  ,"question_create_v4": """
      You are a market researcher, writing a market research report 
      for executives on this topic: "<topic>".

       Generate 50  questions and answers pairs related to "<topic>" 
       and based on the context below.

      *Important*: 
           Question must include this industry name "<industry_name>".
           Answer should be 3 lines long and must be specific.

       ## Context:
        Topic:  "<topic>".

         <text_reference>


       ## Output follows this JSON list format:
               [  ["question1",  "answer1"]
                  [ "question2", "answer2"],    
                  ... 
              ]

   """
}



def llm_run_custom():
    """ Ad hoc code to run LLM


    """
    prompt = """
         You are market researcher working for a report for Business executives.
     
     Related to  this industry field: "<industry_name>"  and the CONTEXT below,
     generate 30 keyword tags or synonymous and 30 business questions.


     ## Important:
         Question should be related to market size, future growth, impact of technology, competitors,...

     ## CONTEXT:
        <text_reference> 

     ## Output follows this JSON list format:
       [ ["tag1",  "tag2", "tag3"]
         ['question1','question2', 'question3']


    """
    from rag.llm import LLM
    from utils.util_text import (str_remove_html_tags,)

    dirin1=""
    df = pd_read_file(dirin1)

    #df1['text'] = df1['text_html'].apply( str_remove_html_tags)
    #df['text']  =df['text'].apply(lambda x: x[:600].strip() )


    log("##### LLM init  #############################################")
    llm = LLM(service = "openai" , model =  "gpt-4o",    ###   "gpt-4o-mini",
              max_tokens=16384 , ) 

    prompt = """
         You are market researcher working for a report for Business executives.
     
        Related to  this industry field: "<industry_name>"  and the CONTEXT below,
        generate 30 keyword tags or synonymous.

        ## CONTEXT:
            <text_reference> 

        ## Output follows this JSON list format:
            ["tag1",  "tag2", "tag3", ]

        Do not add extra words other the JSON list.   
    """

    prompt_map_dict = { "<text_reference>": 'text',
                        "<industry_name>":  'L_cat'
                      }

    log('Prompt correct:', llm.prompt_validate(prompt, prompt_map_dict))
    log(df[prompt_map_dict.values() ].shape)

    log("##### LLM Generate  ########################################")
    nmax  = 10000
    npool = 4

    colnew = 'tag_synonym'
    tag    = "industry"
    dirout = f"ztmp/data/arag/synonymous/{tag}"

    kbatch = 20
    df2    = df.iloc[:nmax]
    mbatch = len(df2) // kbatch
    ymd    = date_now(fmt="%y%m%d")   
    log(df2.head(1).T)
    for kk in range(0, mbatch+1):
        dfk = df2.iloc[kk*kbatch: (kk+1)*kbatch, : ]
        if len(dfk)< 1: break
        log(kk, dfk.shape)

        df1 = llm.get_batch_df(dfk, prompt, prompt_map_dict, 
                              dirout=None, npool=npool ,
                              keeponly_msg = 1,
                              output_schema= None ) ### custom parser in LLM class
        log(df1['llm_msg'].values[0])

        df1 = df1.rename(columns={'llm_msg': colnew})
        df1['tag'] = colnew 
        y,m,d,h,ts = date_get()
        pd_to_file(df1, dirout + f"/{ymd}/df_tags_list_{tag}_{ts}_{kk}_{len(df1)}.parquet")



"""

dfa.com_all_info.columns

"""


############## ETL for RAG #####################################################################
if "######## Col init ################################":
    global ccols
    ccols = Box({})
    ccols.com_all_info = ['com_id', 'description', 'name', 'number_of_employees_min', 'total_funding_amount']


    ##### Company Details ####################
    ccols.com_disrup_info_full              = ['L1_cat', 'L2_cat', 'L3_cat', 'L4_cat', 'business_model', 'category_id',
                                                'category_name',
                                                'com_id', 'com_name', 'crunchbase_url', 'disruptor_type', 'focus_market',
                                                'industry_id',
                                                'number_of_employees_max', 'number_of_employees_min', 'operational_presence',
                                                'product_or_service', 'product_stage', 'revenue', 'target_audience',
                                                'total_funding_amount', 'unique_value', 'website_url']

    ccols.com_incum_info_full = ['L1_cat', 'L2_cat', 'L3_cat', 'L3_catid2', 'L4_cat', 'L4_catid2',
                                 'L4_catid_segment_summery', 'com_id', 'com_name', 'incumbent_description',
                                 'incumbent_id',
                                 'incumbent_inhouse_dev_id', 'incumbent_logo', 'incumbent_master_description',
                                 'incumbent_master_id', 'incumbent_master_logo', 'incumbent_name', 'incumbent_name2',
                                 'isPublish', 'logo']

    ccols.com_incum_info_industry_specific = ['L3_catid', 'com_id', 'com_name', 'incumbent_description', 'incumbent_id',
                                              'incumbent_logo', 'incumbent_master_description', 'incumbent_master_id',
                                              'incumbent_master_logo', 'incumbent_name', 'incumbent_name2', 'isPublish',
                                              'logo']


    ##### Company Product ####################
    ccols.com_incum_product_ca = ['L3_catid', 'business_model', 'com_id', 'com_name', 'com_name2', 'description',
                                  'differentiator', 'external_entry_id', 'feat_id', 'focus_market',
                                  'incumbent_master_id',
                                  'incumbent_product_id', 'industry_specific_field1', 'industry_specific_field10',
                                  'industry_specific_field2', 'industry_specific_field3', 'industry_specific_field4',
                                  'industry_specific_field5', 'industry_specific_field6', 'industry_specific_field7',
                                  'industry_specific_field8', 'industry_specific_field9', 'launched_acquired_date',
                                  'launched_acquired_text', 'operational_presence', 'product_com_id',
                                  'product_image_id',
                                  'product_link', 'product_name', 'product_or_service', 'product_stage',
                                  'reporting_segment_id', 'revenue', 'segment_name', 'sort_order', 'target_audience']


    ccols.com_disrup_info_ca_segment        = ['L3_catid', 'business_model', 'category_id', 'category_name', 'com_id',
                                        'disruptor_type', 'focus_market', 'name', 'operational_presence',
                                        'product_or_service', 'product_stage', 'revenue', 'target_audience',
                                        'unique_value']

    ccols.com_disrup_info_ca_segment_matrix = ['L3_catid', 'L4_catid', 'com_id', 'field_key', 'matrix_name',
                                               'matrix_value']



    ccols.incum_in_house_development = ['L1_cat', 'L2_cat', 'L3_cat', 'L4_cat', 'com_id', 'com_name', 'summary']







    #############  Strategy Data #########################################
    ccols.incum_strategy = ['com_name', 'corporate_goal', 'enabled', 'feat_id', 'id', 'last_updated_date', 'mission',
                            'published_financial_targets', 'strategy_items', 'vision']

    ccols.incum_strategy_item = ['analysts_quick_take', 'enabled', 'id', 'key_initiatives_for_segment1',
                                 'key_initiatives_for_segment2', 'key_initiatives_for_segment3',
                                 'key_initiatives_for_segment4', 'key_initiatives_for_segment5',
                                 'key_initiatives_for_segment6', 'key_initiatives_for_segment7', 'last_updated_date',
                                 'reporting_segment1', 'reporting_segment2', 'reporting_segment3', 'reporting_segment4',
                                 'reporting_segment5', 'reporting_segment6', 'reporting_segment7', 'title']

    ccols.incum_strategy_item_initiative = ['enabled', 'id', 'industries_in_focus', 'key_initiative',
                                            'last_updated_date',
                                            'products_in_focus', 'title']


    ############ Investment Activity #####################################
    ccols.com_investment_activity = ['L1_cat', 'L2_cat', 'L3_cat', 'L4_cat', 'amount', 'announced_on', 'cb_link',
                                     'com_id',
                                     'com_name', 'company_id', 'company_name', 'country', 'description', 'edge_link',
                                     'funding_stage_name', 'industry_id', 'industry_name', 'is_lead_investor',
                                     'segment_name', 'state', 'total_funding', 'website']


    ############ Industry data ###########################################
    ccols.indus_market_size_html    = ['graph_data', 'industry_id', 'industry_name', 'market_sizing_headline', 'text',
                                            'url']
    ccols.indus_overview            = ['edge_link', 'external_entry_id', 'full_overview_text', 'isEnabled',
                                            'short_description_text']
    ccols.indus_overview_contentful = ['datawrapper_urls', 'enabled', 'full_description', 'id', 'industry_id',
                                            'industry_name', 'short_description']

    ccols.indus_update_all          = ['L1_cat', 'L2_cat', 'L3_cat', 'L3_cat2', 'L3_catid', 'L4_cat', 'com_name', 'content_id',
                                            'dt',
                                            'id', 'news_type', 'text', 'title', 'url']

    ccols.map_catid                 = ['L1_cat', 'L1_catid', 'L2_cat', 'L2_catid', 'L3_cat', 'L3_catid', 'L4_cat', 'L4_catid']
    ccols.map_com_incum_disru       = ['com_id', 'com_name', 'disruptor_id', 'incumbent_id']
    ccols.map_indus_incum_fields    = ['L3_catid', 'field_key', 'field_name']

    #ccols.news_activity_all         = ['acquisition_price', 'activity_date', 'activity_id', 'activity_type', 'activity_url',
    #                                       'associated_company_ids', 'created_date', 'currency', 'initiator_company_company_id',
    #                                       'is_deleted', 'ma_type', 'partnership_type', 'publication_state', 'source', 'summary',
    #                                       'updated_date']

    # ccols.news_merger_activity      = ['L1_cat', 'L2_cat', 'L3_cat', 'L4_cat', 'acquisition_price', 'activity_id',
    #                                    'art2_date',
    #                                    'art_title', 'com_buyer', 'com_extract_norm', 'created_date', 'currency', 'ma_type',
    #                                    'publication_state', 'url']

    ccols.news_merger_activity_old  = ['L1_cat', 'L2_cat', 'L3_cat', 'L3_catid', 'L4_cat', 'L4_cat2', 'L4_catid',
                                      'com_id_acquired', 'com_id_buyer', 'com_name_acquired', 'com_name_buyer',
                                      'funding_amount_acquired', 'ma_amount', 'ma_currency', 'ma_date', 'ma_type',
                                      'title','url']


    #ccols.news_partnership_activity     = ['L1_cat', 'L2_cat', 'L3_cat', 'L4_cat', 'activity_id', 'com_extract_norm',
    #                                   'created_date', 'dt', 'partnership_type', 'text', 'url']

    ccols.news_partnership_activity_old = ['L1_cat', 'L1_cat1', 'L2_cat', 'L2_catid', 'L2_catidn', 'L3_cat',
                                           'L3_cat_des',
                                           'L3_catid', 'L4_cat', 'L4_catid', 'cat_id', 'cat_name', 'com_id', 'com_id2',
                                           'com_name', 'com_name2', 'dt', 'ind_id', 'ind_name',
                                           'partnership_acquisition',
                                           'partnership_type', 'text', 'url']

    ccols.news_product_all_old =['L1_cat', 'L2_cat', 'L3_cat', 'L3_catid', 'com_id', 'com_name', 'date',
                                         'industry_update_item_id', 'news_type', 'title', 'url_text']


    ######## Output Schema #############################
    ccols.com_all                  = ['L_cat', 'com_id', 'com_type', 'description', 'name', 'url']
    ccols.com_all_info             = ['com_id', 'description', 'name', 'number_of_employees_min', 'total_funding_amount']
    ccols.edge_industry_activity   = ['L0_catnews', 'L1_cat', 'L2_cat', 'L3_cat', 'L3_cat2', 'L3_catid', 'L_cat',
                                       'com_extract', 'content_id', 'date', 'dt', 'info', 'n', 'news_type', 'score', 'text',
                                       'text_id', 'text_qdrant', 'text_summary', 'title', 'url']

    ccols.edge_industry_comlist    = ['L2_cat', 'L3_cat', 'L3_catid', 'L_cat', 'L_cat_full', 'coms']

    ccols.edge_industry_insight    = ['L3_cat', 'L4_cat', 'L_cat', 'date', 'keywords', 'text', 'text_full', 'text_id',
                                      'text_short', 'title', 'url']

    ccols.edge_industry_marketsize = ['L3_catid', 'L_cat', 'date', 'text', 'text_html', 'text_id', 'title', 'url']

    ccols.edge_industry_overview   = ['L_cat', 'L_catid', 'date', 'text', 'text_full', 'text_id', 'text_short', 'title',
                                       'url']

    ##### RAG type
    ccols.rag_all                  = [  'date', 'url', 'title',  'text_html',
                                        'chunk_id', 'chunk_id_int',  'text_chunk',
                                        'L_cat', 'content_type',
                                        'L0_catnews',      ### news type
                                        'com_extract',     ##3 company name
                                        'info', 'emb', 'question_list',
                                     ]


def dbs3_create_schema(dirin1="ztmp/aiui/data/rag/db_tmp/final/*.parquet", tag='initial'):
    """
    #### Output
    dbs3_create_schema(dirin1="ztmp/aiui/data/zlocal/db/db_sqlite/*.parquet",
                   tag='dblocal')


    """
    res = []
    flist = glob_glob(dirin1)
    for fi in flist:
        df = pd_read_file(fi)
        dd = {
            'table': fi.split("/")[-1].replace(".parquet", "")
            , 'cols': list(df.columns)
            , 'nrows': len(df)
            , 'uri': fi
            , 'info': ""
        }
        res.append(dd)

    res = pd.DataFrame(res)
    if len(res) > 0:
        pd_to_file(res, f"ztmp/aiui/rag/schema/table_schema_{tag}.parquet")

    ss = ""
    for ii, x in res.iterrows():
        ss += f"ccols.{x['table']} = {x['cols']} " + "\n"
    print(ss)



def dbs3_load_all(dirin1="ztmp/aiui/data/rag/db_tmp/final/*.parquet", ):
    """

       global dfa
       dfa = dbs3_load_all(dirin1="ztmp/aiui/data/rag/db_tmp/final/*.parquet")


        log(dfa.com_all_info.country.unique())
        dfa.com_all_info.columns

    """
    # from utils.utilmy_aws import pd_read_file_s3, glob_glob_s3
    from copy import deepcopy
    dfa = Box({})
    flist = glob_glob(dirin1)
    for fi in flist:
        log(fi)
        df = pd_read_file(fi)
        log(df.shape)
        fname = fi.split("/")[-1].replace(".parquet", "")
        dfa[fname] = deepcopy(df)

    print(dfa.keys())
    return dfa




def test1():
    dfa = dbs3_load_all(dirin1="ztmp/aiui/data/rag/db_tmp/final/*.parquet", )

    ['L0_catnews', 'L_cat', 'com_extract', 'date', 'info', 'n', 'score', 'text_id', 'text_qdrant', 'text_summary']

    def export_rag_investment_activity(dfa, tag="-v1", ):
        """

             Funding and investment from Crunchbase.


        """
        diroot = "ztmp/aiui"
        dirlocal = diroot + "/data/zlocal/"

        ccols.com_investment_activity = ['L1_cat', 'L2_cat', 'L3_cat', 'L4_cat', 'amount', 'announced_on', 'cb_link',
                                         'com_id',
                                         'com_name', 'company_id', 'company_name', 'country', 'description',
                                         'edge_link',
                                         'funding_stage_name', 'industry_id', 'industry_name', 'is_lead_investor',
                                         'segment_name', 'state', 'total_funding', 'website']

        df1 = dfa.com_investment_activity
        cols1 = ccols.com_investment_activity

        del df1['L4_cat']
        df1 = pd_add_Lcat_industry(df1, colout='L_cat')

        df1 = df1.rename(columns={'com_name': 'investor_name', "company_name": "receiver_name",
                                  "announced_on": 'date',
                                  })

        log("####### Sort by date ###################################")
        df1 = df1.sort_values(['receiver_name', 'date'], ascending=[1, 0])
        log(df1[['date', 'receiver_name']])

        cols2 = ['amount', 'date', 'cb_link',
                 'com_id', "L_cat",
                 'investor_name', 'company_id', 'receiver_name', 'country', 'description',
                 'edge_link',
                 'funding_stage_name', 'is_lead_investor',
                 'state', 'total_funding', 'website']

        df1 = df1.groupby(cols2).apply(
            lambda dfi: ";".join([ci for ci in dfi['L3_cat'].values if ci is not None])).reset_index()
        df1.columns = cols2 + ['L3_cat']
        log(df1['L3_cat'])

        log("####### Export for News activity #######################")
        dirout1 = diroot + "/data/zlocal/db/db_sqlite_tmp/"
        pd_to_file(df1, dirout1 + "/edge_investment_activity.parquet")








############ Export RAG Data ################################################################
def export_rag_news_activity(dfa, tag="-v1", ):
        """

        ccols.news_merger_activity_old  = ['L1_cat', 'L2_cat', 'L3_cat', 'L3_catid', 'L4_cat', 'L4_cat2', 'L4_catid',
                                          'com_id_acquired', 'com_id_buyer', 'com_name_acquired', 'com_name_buyer',
                                          'funding_amount_acquired', 'ma_amount', 'ma_currency', 'ma_date', 'ma_type',
                                          'title','url']


        ccols.news_partnership_activity_old = ['L1_cat', 'L1_cat1', 'L2_cat', 'L2_catid', 'L2_catidn', 'L3_cat',
                                               'L3_cat_des',
                                               'L3_catid', 'L4_cat', 'L4_catid', 'cat_id', 'cat_name', 'com_id', 'com_id2',
                                               'com_name', 'com_name2', 'dt', 'ind_id', 'ind_name',
                                               'partnership_acquisition',
                                               'partnership_type', 'text', 'url']

        ccols.edge_industry_activity   = ['L0_catnews', 'L1_cat', 'L2_cat', 'L3_cat', 'L3_cat2', 'L3_catid', 'L_cat',
                                           'com_extract', 'content_id', 'date', 'dt', 'info', 'n', 'news_type', 'score', 'text',


        """
        diroot  = "ztmp/aiui"
        dirlocal= diroot + "/data/zlocal/"

        ccols.news_activity_all = ['L3_cat', 'L3_catid', 'L4_cat', 'L4_catid',
                'acquisition_price', 'associated_companies_company_id',  'currency','ma_type',
                                   'initiator_company_company_id',

               'activity_date', 'activity_type',
               'com_name', 'created_by', 'created_date', 'id',

                'is_deleted', 'partnership_type', 'publication_state', 'source', 'summary',
                'updated_date' ]

        df1 = dfa.news_activity_all
        df1 = df1[df1['publication_state'] == 'PUBLISHED' ]


        def add_L0(x):
            x2= ""
            if   x['activity_type'] == "Partnership": x2 = 'partner-' + x['partnership_type']
            elif x['activity_type'] == "M&A":         x2 = 'merger-'  + x['ma_type']
            else:                                     x2 = x['activity_type']
            x2 = str(x2).lower().replace("_", " ")
            return x2
        df1['L0_catnews'] = df1.apply(lambda  x : add_L0(x) , axis=1)


        def addinfo(x):
            dd ={ "ma_price":         x['acquisition_price'],
                  "ma_currency":      x['currency'],
                  "initiator_comid":  x['initiator_company_company_id'],
                 # "associated_comid": x['associated_companies_company_id'],
                  "ma_type"         : x['ma_type']
            }
            return dd

        df1['info'] = df1.apply(lambda x: json.dumps(addinfo(x)) , axis=1)

        df1['url']  = df1['source']
        df1['date'] = df1['activity_date']
        df1['activity_id'] = df1['id']
        df1['text'] = df1['summary']

        cols1 = [ 'activity_id', 'url', 'date'   ]
        log( df1[cols1])
        df2 = pd_groupby_concat_string(df1, colgroup=cols1, colconcat='com_name')
        df2['com_extract'] = df2['com_name'].apply(lambda x: " ; ".join(np_unique([  ti.strip() for ti in    x.split(";") ]) ) )


        cols2 = [ 'activity_id', 'L0_catnews', 'text', 'info', 'L3_cat', 'L4_cat', 'L4_catid', 'L3_catid'    ]
        df2 = df2.merge(df1[cols2].drop_duplicates(), on = ['activity_id'], how='left')

        df2 = df2.merge(dfa.map_catid[[ 'L4_catid', 'L1_cat', 'L2_cat'   ]], on = ['L4_catid'], how='left')
        df2 = df2.fillna("")
        df2['date']  = df2['date'].apply(lambda x: str(x).split(" ")[0] )
        df2 = df2.sort_values([ 'date'], ascending=[ False])


        df2['title']    = df2['text']
        df2['L3_cat2']      =  df2['L3_cat']
        cols3 = ['activity_id', 'url', 'date', 'L0_catnews', 'title', 'text', 'info', 'L1_cat', 'L2_cat', 'L3_cat', 'L4_cat',
                 'com_extract', 'L3_catid', 'L3_cat2']
        log(df2[cols3][[ 'date', 'url' ]])
        df7 = deepcopy(df2)



        log("#### Product page #########################################################")
        df2 = dfa.news_product_all
        ## ['L1_cat', 'L2_cat', 'L3_cat', 'L3_catid', 'com_id', 'com_name', 'date',   'industry_update_item_id', 'news_type', 'title', 'url_text', 'url'],
        ## missing:  "['activity_id', 'L0_catnews', 'info', 'L4_cat', 'com_extract_norm']
        df2['url']  = df2['url_text'].apply(lambda x: str_extract_url(x))
        df2['text'] = df2['url_text'].apply(lambda x: str_remove_html_tags(x))
        df2['date'] = df2['date'].apply(lambda x: str(x).split(" ")[0] )
        df2['L0_catnews'] = df2['news_type'].apply(lambda x:'product - ' +  str(x).lower().replace("_", " ").replace("none","")  )
        df2['activity_id'] = df2['industry_update_item_id']

        cols2 = [ 'activity_id', 'url', 'text', 'date', 'L0_catnews', 'title', 'L1_cat', 'L2_cat', 'L3_cat', 'L3_catid'    ]
        df2a  = pd_groupby_concat_string(df2, colgroup= cols2, colconcat='com_name', sep=" ; ")
        df2a['com_extract']  = df2['com_name']

        dfcat4 = pd_groupby_concat_string(dfa.map_catid, colgroup= ['L3_catid'], colconcat='L4_cat', sep=" , ")
        df2a   = df2a.merge(dfcat4, on=['L3_catid'], how='left')
        df2a['info']    = ""
        df2a['L3_cat2'] = df2a['L3_cat']
        log(df2a[cols3].columns)

        df2a = df2a[ df2a['date'].apply(lambda x: '2024' in x or '2023' in x ) ]
        log(df2a[[ 'L0_catnews' ]])
        log(df2a[cols3].head(1).T)

        df3 = pd.concat((df7[cols3], df2a[cols3]))
        df3 = df3.drop_duplicates(['url', 'date'])



        log("##### Text missing   #####################################################")
        df3 = pd_add_Lcat_industry(df3)
        df3 = pd_add_textid(df3, coltext="text", colid='text_id')
        df3['text_summary'] = df3['text']
        df3['text_qdrant']  = ""
        df3['content_id']   = df3['text_id']
        df3['score']        = 0.0
        df3['n'] = df3['text'].str.len()
        df3['news_type']    = df3['L0_catnews'].apply(lambda x: 'news-' + str(x).lower().replace("_", " ")  )
        df3['dt']           = df3['date']

        #df3                 = newsengine_add_news_title(df3, colout='title')
        #df3                 = newsengine_add_news_text(df3, colout='text')


        log("####### Export for df_edge_industry_activity #######################")
        log( df3[ccols.edge_industry_activity])
        colse  = ['L0_catnews', 'L1_cat', 'L2_cat', 'L3_cat', 'L3_cat2', 'L3_catid', 'L_cat',
                  'com_extract', 'content_id', 'date', 'dt', 'info', 'n', 'news_type', 'score', 'text',
                  'text_id', 'text_qdrant', 'text_summary', 'title', 'url']

        log(df3[ccols.edge_industry_activity].head(1).T )
        log(df3[[ 'date', 'url' ]])


        ###
        dirout1 = diroot + "/data/zlocal/db/db_sqlite_tmp/df_edge_industry_activity.parquet"
        df0     = pd_read_file(dirout1 )
        df4 = pd.concat((df0[ccols.edge_industry_activity], df3[ccols.edge_industry_activity]))
        df4['date']       = df4['date'].apply(lambda x: str(x).split(" ")[0] )
        df4 = df4.sort_values(['date'], ascending=[False])
        df4 = df4.drop_duplicates(['url', 'text'], keep='first')

        df4['L0_catnews'] = df4['L0_catnews'].apply(lambda x: x.replace(",", " ").replace("-"," "))
        df4['content_id'] = df4['content_id'].astype("str")
        df4['info']       = df4['info'].astype("str")
        df4['dt'] = df4['date']

        log(df4[[ 'date', 'url' ]])
        log(df4[[ 'L0_catnews', 'title', 'url' ]])
        log(df4[[ 'L_cat', 'com_extract' ]])

        pd_to_file(df4[ccols.edge_industry_activity], dirout1, show=1)


def export_rag_com_industry_segment_ca(dfa, tag="-v1", ):
    """

        ccols.df_edge_industry_activity   = ['L0_catnews', 'L1_cat', 'L2_cat', 'L3_cat', 'L3_cat2', 'L3_catid', 'L_cat', 'com_extract', 'content_id', 'date', 'dt', 'info', 'n', 'news_type', 'score', 'text', 'text_id', 'text_qdrant', 'text_summary', 'title', 'url']

        L0_catnews                          product service partnership
        L1_cat                                      aerospace & defense
        L2_cat                                                aerospace
        L3_cat                                      next-gen satellites
        L3_cat2                                     Next-gen Satellites
        L3_catid                                                    152
        L_cat         aerospace & defense : aerospace : next-gen sat...
        com_extract                                     aac clyde space
        content_id                                                29649
        date                                                 2024-05-27
        dt                                          2024-05-27 04:00:00
        info
        n                                                           747
        news_type                           PRODUCT_SERVICE_PARTNERSHIP
        score                                                       0.0
        text          \n  \n  \n  \n    \n      \n        AAC Clyde ...
        text_id                                           536889009-747
        text_qdrant   \n  \n  \n  \n    \n      \n        AAC Clyde ...
        text_summary  \n  \n  \n  \n    \n      \n        AAC Clyde ...
        title         AAC Clyde Space partners to create laser commu...
        url                           https://eeddge.com/updates/30759

     file:///Users/kevin.noel/gitdev/agen/gen_dev/aigen/src/engine/usea/ui/static/answers/ageneric/chart_html/example/multtree.html

         industry,
         Funding --->  split by companies.



        df1 = df0[ df0['L2_cat'] == "distribution & logistics" ]

        df1a = df1.groupby(['L2_cat', 'L3_cat']).agg({'com_id': 'nunique'}).reset_index()

        df1b =  df1.groupby(['L3_cat', 'L4_cat']).agg({'com_id': 'nunique'}).reset_index()
            colors = [
                '#e6194B',  # Red
                '#3cb44b',  # Green
                '#ffe119',  # Yellow
                '#4363d8',  # Blue
                '#f58231',  # Orange
                '#911eb4',  # Purple
                '#42d4f4',  # Cyan
                '#f032e6',  # Magenta
                '#bfef45',  # Lime
                '#fabed4',  # Pink
                '#469990',  # Teal
                '#dcbeff',  # Lavender
                '#9A6324',  # Brown
                '#fffac8',  # Beige
                '#800000',  # Maroon
                '#aaffc3',  # Mint
                '#808000',  # Olive
                '#ffd8b1',  # Apricot
                '#000075',  # Navy
                '#a9a9a9'   # Grey
            ]


    """
    diroot   = "ztmp/aiui"
    dirlocal = diroot +"/data/zlocal/"



    df1 = dfa.com_disrup_info_ca_segment

    cols1 = ['L3_catid', 'business_model', 'category_id', 'category_name', 'com_id',
       'disruptor_type', 'focus_market', 'name', 'operational_presence',
       'product_or_service', 'product_stage', 'revenue', 'target_audience',
       'unique_value']

    df1 = df1.rename(columns={
             'category_id' : 'L4_catid',
             'category_name' : 'L4_cat',
             'name': 'com_name',
    })


    df1 = df1.merge( dfa.map_catid[[ 'L4_catid', 'L3_cat', 'L2_cat', 'L1_cat' ]] , on="L4_catid", how="left" )

    cols0 = ['com_id', 'com_name', 'L3_catid', 'L3_cat', 'L4_cat', 'L4_catid', 'product_stage',
             'revenue', 'target_audience',  ]
    log( df1[cols0].columns)
    log( df1[cols0].head(1).T)

    df1 = df1.drop_duplicates(['com_id', 'L3_cat', 'L4_cat'])



    df2 = dfa.com_incum_product_ca
    cols2=  ['L3_catid', 'business_model', 'com_id', 'com_name', 'com_name2',
       'description', 'differentiator', 'external_entry_id', 'feat_id',
       'focus_market', 'incumbent_master_id', 'incumbent_product_id',
       'industry_specific_field1', 'industry_specific_field10',
       'industry_specific_field2', 'industry_specific_field3',
       'industry_specific_field4', 'industry_specific_field5',
       'industry_specific_field6', 'industry_specific_field7',
       'industry_specific_field8', 'industry_specific_field9',
       'launched_acquired_date', 'launched_acquired_text',
       'operational_presence', 'product_com_id', 'product_image_id',
       'product_link', 'product_name', 'product_or_service', 'product_stage',
       'reporting_segment_id', 'revenue', 'segment_name', 'sort_order',
       'target_audience']

    df2 = df2.rename(columns={
             'segment_name'        : 'L4_cat',
             'reporting_segment_id': 'L4_catid'
    })
    df2 = df2.merge( dfa.map_catid[[ 'L3_catid', 'L3_cat', 'L2_cat', 'L1_cat' ]] , on="L3_catid", how="left" )
    df2[cols0]
    log( df2[cols0].head(1).T)

    df2 = df2.drop_duplicates(['com_id', 'L3_cat', 'L4_cat'])


    df0 = pd.concat((df1, df2))
    df0 = pd_fillna_dtype(df0)
    log( df0[cols0].head(1).T)


    log("####### Export for RAG ################################")
    log(df1.shape)

    #### Load
    df0 = pd_read_file(dirlocal + "/db/db_sqlite/com_indus_segment.parquet")
    log(df0.shape)

    df0 = pd.concat((df1[ ccols.rag_all ], df0[ ccols.rag_all ] ))
    df0 = df0.drop_duplicates(['url', 'date', 'chunk_id'], keep='first') ### Keep updates one
    log(df0.shape)

    log(df0[cols0].head(1).T)
    dirout1 = dirlocal + "/db/db_sqlite_tmp/"
    pd_to_file(df0[cols0], dirout1 + "/com_indus_segment.parquet")


def pd_fillna_dtype(df):
    for col in df.columns:
        dtype = df[col].dtype
        if 'float' in str(dtype) or 'int' in str(dtype):
            df[col] = df[col].fillna(-1)

        elif 'object' in str(dtype) or 'string' in str(dtype):
            df[col] = df[col].fillna('')
    return df


def export_rag_industry_ca_matrix(dfa, tag="-v1", ):
    """

        ccols.df_edge_industry_activity   = ['L0_catnews', 'L1_cat', 'L2_cat', 'L3_cat', 'L3_cat2', 'L3_catid', 'L_cat', 'com_extract', 'content_id', 'date', 'dt', 'info', 'n', 'news_type', 'score', 'text', 'text_id', 'text_qdrant', 'text_summary', 'title', 'url']

        L0_catnews                          product service partnership
        L1_cat                                      aerospace & defense
        L2_cat                                                aerospace
        L3_cat                                      next-gen satellites
        L3_cat2                                     Next-gen Satellites
        L3_catid                                                    152
        L_cat         aerospace & defense : aerospace : next-gen sat...
        com_extract                                     aac clyde space
        content_id                                                29649
        date                                                 2024-05-27
        dt                                          2024-05-27 04:00:00
        info
        n                                                           747
        news_type                           PRODUCT_SERVICE_PARTNERSHIP
        score                                                       0.0
        text          \n  \n  \n  \n    \n      \n        AAC Clyde ...
        text_id                                           536889009-747
        text_qdrant   \n  \n  \n  \n    \n      \n        AAC Clyde ...
        text_summary  \n  \n  \n  \n    \n      \n        AAC Clyde ...
        title         AAC Clyde Space partners to create laser commu...
        url                           https://eeddge.com/updates/30759



    """
    diroot   = "ztmp/aiui"
    dirlocal = diroot +"/data/zlocal/"



    df1 = dfa.com_disrup_info_ca_segment_matrix

    cols1 = ['L3_catid', 'L4_catid', 'com_id', 'field_key', 'matrix_name',
             'matrix_value']

    log("##### Merge L4 cat #############################################")
    df1 = df1[[ 'com_id', 'field_key', 'matrix_name', 'matrix_value', 'L4_catid'  ]].merge(dfa.map_catid, on=['L4_catid'], how='left' )


    df1['text']       = df1.apply(lambda x:  f"{x['matrix_name']} : {x['matrix_value']} ", axis=1 )
    df1['L0_catnews'] = df1.apply(lambda x:  f"{x['matrix_name']}", axis=1 )
    df1['title']      = df1['text']

    df1 = pd_add_Lcat_industry(df1, colout='L_cat' )


    from utils.util_text import pd_add_textid, pd_add_chunkid
    df1 = pd_add_textid(df1, colid='text_id', coltext='text')

    df1 = df1.merge(dfa.com_all_info[[ 'com_id', 'name' ]] , on=['com_id'], how='left' )
    df1['com_extract'] = df1['name'].fillna("")

    df1['url']  = df1.apply(lambda x : f"http://wwww.eeddge.com/companies/{x['com_id']}" , axis=1)
    df1['info'] = ""
    df1['date'] = ""
    df1['n']    = df1['text'].str.len()

    df1['text_chunk']   = df1['text'].apply(lambda  x: x.strip() )
    df1['chunk_id']     = df1['text_id'].apply(lambda x: x + "-0")
    df1['chunk_id_int'] = pd_add_chunkid_int(df1, colid="chunk_id", colidnew='chunk_id_int' )

    df1['text_html']     = df1['text']
    df1['content_type']  = " industry competitor analysis"
    df1['emb']           = ""
    df1['question_list'] = ""
    df1['version']       = date_now(fmt="%Y%m%d") + tag


    log("####### Export for RAG ################################")
    ccols.rag_all = [  'date', 'url', 'title',  'text_html',
                          'chunk_id', 'chunk_id_int',  'text_chunk',
                          'L_cat', 'content_type',
                          'L0_catnews',      ### news type
                          'com_extract',     ##3 company name
                          'info', 'emb', 'question_list',
                    ]
    log(df1[ccols.rag_all].shape)

    #### Load
    dfrag = pd_read_file(dirlocal + "/db/db_sqlite/df_rag_all.parquet")
    log(dfrag.shape)

    dfrag = pd.concat((df1[ ccols.rag_all ], dfrag[ ccols.rag_all ] ))
    dfrag = dfrag.drop_duplicates(['url', 'date', 'chunk_id'], keep='first') ### Keep updates one
    log(dfrag.shape)

    log(dfrag[ccols.rag_all].head(1).T)
    dirout1 = dirlocal + "/db/db_sqlite_tmp/"
    pd_to_file(dfrag[ccols.rag_all], dirout1 + "/df_rag_all.parquet")



def export_rag_industry_activity(dfa, tag="-v1", ):
    """

        ccols.df_edge_industry_activity   = ['L0_catnews', 'L1_cat', 'L2_cat', 'L3_cat', 'L3_cat2', 'L3_catid', 'L_cat', 'com_extract', 'content_id', 'date', 'dt', 'info', 'n', 'news_type', 'score', 'text', 'text_id', 'text_qdrant', 'text_summary', 'title', 'url']

        L0_catnews                          product service partnership
        L1_cat                                      aerospace & defense
        L2_cat                                                aerospace
        L3_cat                                      next-gen satellites
        L3_cat2                                     Next-gen Satellites
        L3_catid                                                    152
        L_cat         aerospace & defense : aerospace : next-gen sat...
        com_extract                                     aac clyde space
        content_id                                                29649
        date                                                 2024-05-27
        dt                                          2024-05-27 04:00:00
        info
        n                                                           747
        news_type                           PRODUCT_SERVICE_PARTNERSHIP
        score                                                       0.0
        text          \n  \n  \n  \n    \n      \n        AAC Clyde ...
        text_id                                           536889009-747
        text_qdrant   \n  \n  \n  \n    \n      \n        AAC Clyde ...
        text_summary  \n  \n  \n  \n    \n      \n        AAC Clyde ...
        title         AAC Clyde Space partners to create laser commu...
        url                           https://eeddge.com/updates/30759



    """
    diroot   = "ztmp/aiui"
    dirlocal = diroot +"/data/zlocal/"



    df1 = dfa.indus_update_all

    cols1 = ['L1_cat', 'L2_cat', 'L3_cat', 'L3_cat2', 'L3_catid',
             'com_name', 'content_id', 'dt', 'id', 'news_type', 'text', 'title', 'url']

    log("##### Merge L4 cat")
    df1 = df1.groupby(cols1).apply(lambda dfi: " ; ".join(dfi['L4_cat'].values)).reset_index()
    df1.columns = cols1 + ['L4_cat']
    log(df1['L4_cat'])

    from utils.util_text import pd_add_textid, pd_add_chunkid
    df1 = pd_add_textid(df1, colid='text_id', coltext='text')

    df1['com_extract'] = df1['com_name'].str.lower()
    df1['info']        = ""
    df1['score']       = 0.0
    df1['text_summary'] = df1['text']
    df1['text_qdrant']  = df1['text']
    df1['date']         = df1['dt'].apply(lambda x: str(x).split(" ")[0])
    df1['n']            = df1['text'].str.len()

    df1 = pd_add_Lcat_industry(df1, colout='L_cat' )
    df1 = pd_add_L0_catnews_activity(df1, colin="news_type",  colout='L0_catnews' )

    log(df1[ccols.df_edge_industry_activity].head(1).T)
    log(df1[df1['com_extract'].str.contains('microsoft')])


    log("####### Remove Press release ############################")
    log(df1.shape)
    df1 = df1.sort_values('n', ascending=[0])
    df1 = df1.drop_duplicates(['url'], keep='first')
    log(df1.shape)


    log("####### Sort by date ###################################")
    df1 = df1.sort_values(['com_extract', 'date'], ascending=[1, 0])
    log(df1[['date', 'com_extract']])

    """ ['L1_cat', 'L2_cat', 'L3_cat', 'L3_cat2', 'L3_catid', 'com_name',
       'content_id', 'dt', 'id', 'news_type', 'text', 'title', 'url', 'L4_cat',
       'text_id', 'L0_catnews', 'com_extract', 'info', 'score', 'text_summary',
       'text_qdrant', 'date', 'n', 'L_cat']
    """

    log("####### Export for News activity #######################")
    df2 = df1[df1['date'].apply(lambda x: '2024' in x or '2023' in x)]
    dirout1 = diroot + "/data/zlocal/db/db_sqlite_tmp/"
    pd_to_file(df2[ccols.edge_industry_activity], dirout1 + "/df_edge_industry_activity.parquet")



    log("####### Export for RAG ################################")
    ccols.rag_all = [  'date', 'url', 'title',  'text_html',
                          'chunk_id', 'chunk_id_int',  'text_chunk',
                          'L_cat', 'content_type',
                          'L0_catnews',      ### news type
                          'com_extract',     ##3 company name
                          'info', 'emb', 'question_list',
                    ]

    ### "['chunk_id', 'chunk_id_int', 'content_type', 'emb', 'question_list', 'text_chunk', 'text_html'] not
    df2 = df1[df1['date'].apply(lambda x: '2024' in x or '2023' in x)]

    df2['text_chunk']   = df2['text'].apply(lambda  x: x.strip() )
    df2['chunk_id']     = df2['text_id'].apply(lambda x: x + "-0")
    df2['chunk_id_int'] = pd_add_chunkid_int(df2, colid="chunk_id", colidnew='chunk_id_int' )

    df2['text_html']     = df2['text']
    df2['content_type']  = "industry news ; industry_update "
    df2['emb']           = ""
    df2['question_list'] = ""

    df2['L0_catnews']  = df2['L0_catnews']
    df2['com_extract'] = df2['com_extract']
    df2['version']     = date_now(fmt="%Y%m%d") + tag

    #### Load
    dfrag = pd_read_file(dirlocal + "/db/db_sqlite/df_rag_all.parquet")
    log(dfrag.shape)


    cmiss = [ ci for ci in ccols.rag_all if ci not in dfrag    ]
    for ci in cmiss:
        dfrag[ci] = ""

    log(dfrag.shape)
    dfrag = pd.concat((df2[ ccols.rag_all ], dfrag[ ccols.rag_all ] ))
    dfrag = dfrag.drop_duplicates(['url', 'date', 'chunk_id'], keep='first') ### Keep updates one
    log(dfrag.shape)

    log(dfrag[ccols.rag_all].head(1).T)
    dirout1 = dirlocal + "/db/db_sqlite_tmp/"
    pd_to_file(dfrag[ccols.rag_all], dirout1 + "/df_rag_all.parquet")




def export_rag_com_strategy(dfa, tag="-v1", ):
    """
        incumbent_strategy.parquet      id --> contenful_strategy_id       OK ?
                                                          feat_id  → contentful_strategy_itemid

        Incumbent_strategy_item.parquet      id → contentful_strategy_itemid,
                                          key_initiatives_segment1 ( contentful_strategy_item_initiatives_id )                           ….
                                          key_initiatives_segment7 ( contentful_strategy_item_initiatives_id )

        Incumbent_strategy_item_initiatives.parquet/
                                                           id                                    →  contentful_strategy_item_initiatives_id
                                                           product_in_focus(key)   →  contentful_incumbent_product_list
                                                           industry_in_focus(key)  →  contentful_industry_overview_list          FROM  industry_overview.parquet

        {'enabled': False,
          'industries_in_focus': '[]',
          'key_initiative': '<p>•\xa0Transforming the operating model from a complex matrix structure to a more agile and accountable one in 2022 (Compass Strategy) to improve transparency and category-focus as well as be more responsive to market dynamics.</p>',
          'last_updated_date': '',
          'products_in_focus': '["673HClZ3OgMbYWYsEiM5ii"]',
          'title': 'Transforming the operating model '},
         ...}
            dirout1:

        ti=  "3fjA1KspGBee7dCGNQS7Rl"

    """
    diroot   = "ztmp/aiui"
    dirlocal = diroot +"/data/zlocal/"

    df1 = dfa.incum_strategy
    df1['itemid'] = df1['itemid'].apply(lambda x: json.loads(x) )
    df1 = df1.explode('itemid')

    df2 = df1.merge(dfa.incum_strategy_item, left_on=[ 'itemid'], right_on= ['id'], how='left')

    ### Initiatives into dictionnary
    df5   = dfa.incum_strategy_item_initiative.set_index("id")
    dinit = df5.to_dict('index')

    def jj(x):
        x1  = str(x).replace("[","").replace("]","").replace("'", "").replace('"', "")
        x2 = x1.split(",")
        return x2

    def add2(x):
        global dinit
        ss = f""" ## Analysis summary :   
                      {x['analysts_quick_take']}
        
        """
        for ti in jj(x['key_initiatives_for_segment1']):
            di = dinit.get(ti, {})
            log(ti)
            if len(di)<1: continue
            ss = ss + f""" 
                ## Title:       {di['title']} 
                ## Reporting:   {x['reporting_segment1']}  
                ## Initiatives: {di['key_initiative']}     

            """

        for ti in jj(x['key_initiatives_for_segment2']):
            di = dinit.get(ti, {})
            if len(di)<1: continue
            ss = ss + f""" 
                ## Title:       {di['title']}     
                ## Reporting:   {x['reporting_segment2']}    
                ## Initiatives: {di['key_initiative']}     

            """

        for ti in jj(x['key_initiatives_for_segment3']):
            di = dinit.get(ti, {})
            if len(di)<1: continue
            ss = ss + f""" 
                ## Title:       {di['title']}     
                ## Reporting:   {x['reporting_segment3']}                    
                ## Initiatives: {di['key_initiative']}     
                
            """

        return ss
    df2['text_initiative']  = df2.apply(lambda x: add2(x), axis=1)


    cols3 = ['com_name', 'vision', 'mission', 'published_financial_targets', 'corporate_goal', 'last_updated_date_x']
    df3   = df2.groupby(cols3).apply(lambda dfi:  "--------------------\n".join( dfi['text_initiative'].values) ).reset_index()
    df3.columns = cols3 + ['text_initiative']

    def add3(x):
        ss= f"""
           ## Company:   {x['com_name']}

           ## Visiion:  
                {x['vision']}
                
           ## Mission:  
               {x['mission']}
        
           ## Financial Targets:
               {x['published_financial_targets']}    
               
           ## Corporal goals:
               {x['corporate_goal']}    
            
           ## Initiatives 
               {x['text_initiative']}  
        """
        return ss

    df3['text']  = df3.apply(lambda x: add3(x), axis=1)
    print(df3['text'].values[2])


    from utils.utils_base import pd_to_dict

    df7 = dfa.map_com_incum_disrup[ -dfa.map_com_incum_disrup.apply(lambda x :  pd.isna(x['incumbent_id']) and pd.isna(x['disruptor_id']), axis=1  ) ]
    df7 = df7.drop_duplicates(['com_name'])

    COMID = pd_to_dict(df7, colkey=['com_name'], colval=['com_id'])

    log("####### Export for RAG ################################")
    ccols.rag_all                  = [  'date', 'url', 'title',  'text_html',
                                        'chunk_id', 'chunk_id_int',  'text_chunk',
                                        'L_cat', 'content_type',
                                        'L0_catnews',      ### news type
                                        'com_extract',     ##3 company name
                                        'info', 'emb', 'question_list',
                                     ]
    ######################                   ###############################
    tag = "strategy"

    df3['date'] = df3['last_updated_date_x']
    # df3['com_extract'] = df3['com_name']
    df3['L_cat'] = ""

    df3['title'] = df3.apply(lambda  x: f"{x['com_extract']} strategy mission :  {x['mission']}" , axis=1)
    df3['text_chunk'] = df3['text'].apply(lambda  x: x.strip() )
    df3['text_html']  = df3['text'].apply(lambda  x: x.strip() )

    df3['content_type']  = "company strategy "
    df3['L0_catnews']    = "compnany corporate strategy "
    df3['emb']           = ""
    df3['question_list'] = ""
    df3['info']          = ""

    df3['url'] = df3.apply(lambda  x:  "https://www.eeddge.com/companies/" + str(COMID.get(x['com_extract'], {}).get('com_id')) + "#strategy" , axis=1)


    df3 = pd_add_textid(df3)
    df3['chunk_id']     = df3['text_id'].apply(lambda x: x + "-0")
    df3 = pd_add_chunkid_int(df3, colid="chunk_id", colidnew='chunk_id_int' )
    df3['version']      = date_now(fmt="%Y%m%d") + tag

    df3 = df3.sort_values(['com_extract', 'date'], ascending=[1, 0])
    log(df3[['date', 'com_extract']])
    log(df3[ccols.rag_all].shape)


    log("####### Load Previous/Export ################################")
    dfrag = pd_read_file(dirlocal + "/db/db_sqlite/df_rag_all.parquet")
    log(dfrag.shape)

    cmiss = [ ci for ci in ccols.rag_all if ci not in dfrag    ]
    for ci in cmiss:
        dfrag[ci] = ""

    log(dfrag.shape)
    dfrag = pd.concat((df3[ ccols.rag_all ], dfrag[ ccols.rag_all ] ))
    dfrag = dfrag.drop_duplicates(['url', 'date', 'chunk_id'], keep='first') ### Keep updates one
    log(dfrag.shape)

    log(dfrag[ccols.rag_all].head(1).T)
    dirout1 = dirlocal + "/db/db_sqlite_tmp/"
    pd_to_file(dfrag[ccols.rag_all], dirout1 + "/df_rag_all.parquet")




def export_rag_com_disrup_incum(dfa, tag="-v1", ):
    """

    """
    diroot = "ztmp/aiui"
    dirlocal = diroot + "/data/zlocal/"

    df1   = dfa.com_disrup_info_full
    cols1 = ['L1_cat', 'L2_cat', 'L3_cat', 'L4_cat', 'business_model', 'category_id',
                                    'category_name',
                                    'com_id', 'com_name', 'crunchbase_url', 'disruptor_type', 'focus_market',
                                    'industry_id',
                                    'number_of_employees_max', 'number_of_employees_min', 'operational_presence',
                                    'product_or_service', 'product_stage', 'revenue', 'target_audience',
                                    'total_funding_amount', 'unique_value', 'website_url']

    del df1['L4_cat']
    df1 = pd_add_Lcat_industry(df1, colout='L_cat')
    df1 = df1.drop_duplicates(['com_id'], keep='first')
    df1['com_name2'] = df1.apply(lambda x: f"""<a href='http://www.eeddge.com/companies/{x["com_id"]}'>{x['com_name']}</a>""", axis=1)
    df1['L3_cat2'] = df1.apply(lambda x: f"""<a href='http://www.eeddge.com/industry/{x["industry_id"]}'>{x['L3_cat'].capitalize()}</a>""", axis=1)


    name  = "com_disrup"
    cols1 = [ ci for ci in cols1 + ['com_name2', 'L3_cat2', 'L_cat'] if ci not in ['L4_cat'] ]

    log("####### Dump to sqlite ################################")
    pd_to_db_sqlite_tmp(df1, cols1, dirlocal, name= name)


    ########## com incumbent #############################################################
    df1   = dfa.com_incum_info_full
    cols1 = ['L1_cat', 'L2_cat', 'L3_cat', 'L3_catid2',
       'L4_catid_segment_summery', 'com_id', 'com_name',
       'incumbent_description', 'incumbent_id', 'incumbent_inhouse_dev_id',
         'incumbent_master_description', 'incumbent_master_id',
       'incumbent_master_logo', 'incumbent_name', 'incumbent_name2',
       'isPublish', 'logo']

    for ci in [   'incumbent_master_logo', 'logo',  'isPublish'   ]:
        df1[ci] = df1[ci].replace({"": 0.0}).astype('float32')


    df1 = df1[ df1['isPublish'] == 1.0 ]

    for ci in ['L1_cat', 'L2_cat', 'L3_cat', 'L3_catid2',
       'L4_catid_segment_summery',  'com_name','incumbent_description',   'incumbent_master_description',
       'incumbent_name', 'incumbent_name2',
       'isPublish', ] :
           df1[ci] = df1[ci].fillna("")

    df1 = df1.drop_duplicates(['com_id'], keep='first')
    df1 = pd_add_Lcat_industry(df1, colout='L_cat')
    df1['com_name2'] = df1.apply(lambda x: f"""<a href='http://www.eeddge.com/companies/{x["com_id"]}'>{x['com_name']}</a>""", axis=1)
    df1['L3_cat2']   = df1.apply(lambda x: f"""<a href='http://www.eeddge.com/industry/{x["L3_catid2"]}'>{x['L3_cat'].capitalize()}</a>""", axis=1)


    log("####### Dump to sqlite ################################")
    pd_to_db_sqlite_tmp(df1, cols1 +['L_cat', 'com_name2', 'L3_cat2'  ], dirlocal, name=  "com_incum")




def pd_to_db_sqlite_tmp(df1,cols1, dirlocal, name=""):
    log("####### Load Previous/Export #########################")
    try:
        df0 = pd_read_file(dirlocal + f"/db/db_sqlite/{name}.parquet")
        log(df0.shape)
        df1 = pd.concat((df1[cols1], df0[cols1]))
    except Exception as e:
        log(e)

    df1 = df1.drop_duplicates(['com_id', ], keep='first')  ### Keep updates one
    log(df1.shape)

    log(df1[cols1].head(1).T)
    dirout1 = dirlocal + "/db/db_sqlite_tmp/"
    pd_to_file(df1[cols1], dirout1 + f"/{name}.parquet")





############ Utils function ################################################################
def newsengine_add_news_title(df3, colout):
    df3['title'] = df3['text']
    return df3


def newsengine_add_news_text(df3, colout):
    return df3


def pd_add_L4_cat_industry_merge(df, colsmerge=None , sep= " ; "):
    import string

    colsmerge = ['L4_cat'] if colsmerge is None else colsmerge
    cols      = [ ci for ci in df.columns if ci not in colsmerge  ]
    log('merging list in', colsmerge)

    dfall = pd.DataFrame()
    for ci in colsmerge:
        dfi = df.groupby(cols).apply(lambda dfj: sep.join([ str(xi) for xi in dfj[ci].values]) )
        # dfi.columns = cols + [ci]
        dfall[ci]   = dfi

    dfall = dfall.reset_index()
    log(dfall[colsmerge])
    return dfall



def pd_add_Lcat_industry(df, colout='L_cat'):
    import string
    def clean1(x):
        s = ""
        for ci in ['L1_cat', 'L2_cat', 'L3_cat', 'L4_cat', ]:
            if ci in x:
                s = s + " : " + x[ci] if x[ci] is not None else s

        s = s.replace(" & ", " ").replace(" and ", " ")
        s = s.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation))) ### Remove punction with space

        s = s.replace("CCUS", "CCUS Carbon Capture Utilization and Storage")
        s = s.replace("NFTs", "nfts nft Non Fungible Tokens Digital Assets")
        s = s.replace(" CRM", " Customer Relationship Management")
        s = s.replace(" Tech ", " ").replace(" tech ", " ")

        s = ' '.join([ xi  for xi in  s.split(" ") if len(xi)>=1 ])  ### mutiple space with single
        s = s.lower()
        return s

    for ci in ['L1_cat', 'L2_cat', 'L3_cat', 'L4_cat', ]:
        if ci in df.columns:
            df[ci] = df[ci].fillna("").astype("str")

    df[colout] = df.apply(lambda x: clean1(x), axis=1)
    log(df[colout])
    return df




def pd_add_L0_catnews_activity(df, colin='news_type', colout='L0_catnews'):
    import string
    def clean1(x1):
        x1 = x1.lower().replace("m_and_a", "merger and acquisition").replace("_", " ").replace(",", " , ")
        return x1

    df[colout] = df[colin].apply( lambda  x: clean1(x))
    log(df[colout])
    return df





############ New keyword generation #######################################################
def create_new_keyword_for_question():
    #### Query Expansion:

    prompt = """
         You are market researcher working for a report for Business executives.

     Related to  this industry field: "<industry_name>"  and the CONTEXT below,
     generate 30 keyword tags or synonymous and 30 business questions.


     ## Important:
         Question should be related to market size, future growth, impact of technology, competitors,...

     ## CONTEXT:
        <text_reference> 

     ## Output follows this JSON list format:
       [ ["tag1",  "tag2", "tag3"]
         ['question1','question2', 'question3']


    """

    from utils.util_text import str_remove_html_tags

    df1['text'] = df1['text_html'].apply(str_remove_html_tags)
    df['text'] = df['text'].apply(lambda x: x[:600].strip())

    df0 = deepcopy(df)
    df = df1
    log("##### LLM init  #############################################")
    llm = LLM(service="openai", model="gpt-4o",  ###   "gpt-4o-mini",
              max_tokens=16384, )

    prompt = """
         You are market researcher working for a report for Business executives.

     Related to  this industry field: "<industry_name>"  and the CONTEXT below,
     generate 30 keyword tags or synonymous.

     ## CONTEXT:
        <text_reference> 

     ## Output follows this JSON list format:
        ["tag1",  "tag2", "tag3", ]

     Do not add extra words other the JSON list.   
    """

    prompt_map_dict = {"<text_reference>": 'text',
                       "<industry_name>": 'L_cat'
                       }
    assert prompt_validate(prompt, prompt_map_dict), "Missing variable"
    log(df[prompt_map_dict.values()].shape)

    log("##### LLM Generate  ########################################")
    nmax = 10000
    npool = 4

    colnew = 'tag_synonym'
    tag = "industry"
    dirout = f"ztmp/data/arag/synonymous/{tag}"

    kbatch = 20
    df2 = df.iloc[:nmax]
    mbatch = len(df2) // kbatch
    ymd = date_now(fmt="%y%m%d")
    for kk in range(0, mbatch + 1):
        dfk = df2.iloc[kk * kbatch: (kk + 1) * kbatch, :]
        if len(dfk) < 1: break
        log(kk, dfk.shape)

        df1 = llm.get_batch_df(dfk, prompt, prompt_map_dict,
                               dirout=None, npool=npool,
                               keeponly_msg=keeponly_msg,
                               output_schema=output_schema)  ### custom parser in LLM class
        log(df1.head(1).T)
        log(df1['llm_msg'].values[0])

        df1 = df1.rename(columns={'llm_msg': colnew})
        df1['tag'] = colnew
        y, m, d, h, ts = date_get()
        pd_to_file(df1, dirout + f"/{ymd}/df_tags_list_{tag}_{ts}_{kk}_{len(df1)}.parquet")

    dirin1 = "ztmp/data/arag/synonymous/industry/241128/*.parquet"
    dfa = pd_read_file(dirin1)
    dfa[['url', 'L_cat', 'date', 'tag_synonym']]

    def clean(x):
        i1 = x.find("[")
        x1 = x[i1:]
        x1 = x1.replace("[", "").replace("]", "")
        ll = x1.split(",")
        return ll

    dfa['tags'] = dfa['tag_synonym'].apply(lambda x: clean(x))
    dfa = dfa.iloc[1:, :]

    dfa['tags'] = dfa['tags'].apply(lambda x: ",".join(x))
    dfa['tags'] = dfa['tags'].apply(lambda x: x.replace('"', ''))
    dfa = dfa.drop_duplicates('url', keep='last')

    dfa = dfa[['url', 'L_cat', 'tags', 'date', 'text', 'title']]
    dfa.columns = ['url', 'L_cat', 'tags', 'date', 'text', 'industry_name']

    pd_to_file(dfa, "ztmp/data/arag/synonymous/industry/indus_tag_synonym.parquet")







############ Metrics generation   ########################################################
def calc_retrieval_metrics():
      """
           Test rankig of category position.


      """

      from utils.util_text import (date_get, str_replace_punctuation, str_fuzzy_match_list_score
      )

      ##### Load question ####################################
      dirin1 = "ztmp/data/arag/question_generated/zaclean/**/df*qa_clean*.parquet"
      flist  =  glob_glob(dirin1)
      dfq    = pd_read_file(flist, )
      cols1  = [ 'url', 'question', 'answer', 'L_cat', 'L3_catid', 'text', 'text_chunk', 'chunk_id'   ]
      dfq    = dfq[cols1] 

      indulist ="""
          Generative AI Applications
          Generative AI Infrastructure
          Current-gen renewables
          Smart Factory
          Alternative Energy
          Additive Manufacturing
          Digital Twin
          Next-gen Cybersecurity
          Supply Chain Tech
          Foundation Models
          Carbon Capture, Utilization
          AI Drug Discovery
          Hydrogen Economy
          B2B SaaS Management Platforms
          Age Tech
          Remote Work Tools
          Bio-based Materials
          Humanoid Robots
          Financial Wellness Tools
      """
      indulist2 = [ xi.strip() for xi in indulist.split("\n")    if len(xi.strip())>3        ]
       
      dfq2 = pd.DataFrame()
      for xi in indulist2:
          dfq1 = dfq[ dfq['L_cat'].str.contains( xi ) ]
          dfq2 = pd.concat((dfq2, dfq1)) 

      dfq3 = dfq2.sample(n=500)
      dfq3.index = np.arange(0, len(dfq3)) 
      log(dfq3)

      nmax= 10
      topk =5

      #######

      dfragall['L_cat'] = dfragall['L_cat'].apply(lambda x: str_replace_punctuation(x.lower(), " ") )


      from rag.rag_summ2 import query_expand_clean, fun_search_edge_score

        
      log("######## Start Search Retrieval test #############################")
      llg = Box({ 'query_tags': { 'industry_tags' : []   } })
      res = [] 
      ii  = 0
      for ii,x in dfq3.iterrows():
          if ii > nmax: break
          qq = x['question']
          log(ii, qq)
          
          llg.query2 = qq
          llg.llist  = query_expand_clean( qq ) ; log(llist)
          llg.query_tags['industry_tags']  = llg.llist

          dftxt = fun_search_edge_score(dfragall, llg)
          if len(dftxt) < 1: continue

          lcati = dftxt['L_cat'].values

          dd = {
             "words"     : list(llg.llist)
             ,"topk_score":  dftxt['score'].values[:topk]
             ,"topk_Lcat" :  lcati

             ,"topp1" : sum( str_fuzzy_match_list_score( x['L_cat'].lower(), lcati[:1] ) ) * 0.01
             ,"topp5" : sum( str_fuzzy_match_list_score( x['L_cat'].lower(), lcati[:5] ) ) / 5.0 * 0.01

          }
          dd  = dd | dict(x)
          res.append( dd ) 


      res2 = pd.DataFrame(res)
      y,m,d,h,ts = date_get()
      dirout1    = f"ztmp/data/arag/qa_test/{y}{m}{d}"
      pd_to_file(res2, dirout1 + f"/df_qa_test_{ts}_{len(res2)}.parquet" )






############################################################################
#####  Helper functions ####################################################
if "######## Utils #########################":
    def prompt_validate(prompti:str, pr_dict:dict):
          """
             prompti = PROMPTS["question_create_v3"]
          """
          import re
          matches = re.findall(r'<(.*?)>', prompti)

          for xi in matches:
              if  "<"+xi+">" not in pr_dict:
                 log("missing var in Map_dict:", xi )
                 return False

          log("prompt vars exist in map")       
          return True


    def str_extract_url(html_string):
        import re
        try:
            urls = re.findall(r'href=[\'"]?([^\'" >]+)', html_string)
            return urls[0]
        except Exception as e:
            log(e);
            return ""

    def json_load2(x):
       try: 
          return json.loads(str(x))
       except Exception as e:
          log(e)
          return {}   


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
        y,m,d,h = date_now(ymd, fmt="%y-%m-%d-%H", add_days= add_days).split("-")
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


    def pd_add_textid(df, coltext='text', colid='text_id', nchars=200, prefix="", nbucket=10**9):
        df[colid] = df.apply( lambda x: textid_create(x[coltext], nchars=200, prefix="", nbucket=10**9) , axis=1 )
        return df


    def pd_add_chunkid(df, coltextid="text_id2", colout='text_chunk', nchars=200, prefix="", nbucket=10**9):
        df['chunk_id'] = df.groupby(coltextid).cumcount()
        df['chunk_id'] = df.apply( lambda x: f"{x[coltextid]}-{x['chunk_id']}", axis=1 )
        log("Added chunk_id")
        return df


    def pd_text_chunks(df, coltext='text2', colout='text_chunk', sentence_chunk=10):
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



def testzz():

    dfrag = pd_read_file("ztmp/aiui/data/zlocal/db/db_sqlite/df_rag_all.parquet")

    ## dfrag[ dfrag['content_type'].str.contains('marketsize') ]

    dfrag['L0_catnews'] = dfrag.apply(lambda  x:  'market size' if  'marketsize' in x['content_type'] else x['L0_catnews'], axis=1  )


    ## dfrag[ dfrag['L0_catnews'].str.contains('market size') ]


    dfrag = pd_to_file(dfrag, "ztmp/aiui/data/zlocal/db/db_sqlite/df_rag_all.parquet")


    dfrag = pd_to_file(dfrag, "ztmp/aiui/data/zlocal/db/db_sqlite_tmp/df_rag_all.parquet")

    def export_rag_news_activity_old(dfa, tag="-v1", ):
        """
              All external News.

        """
        diroot = "ztmp/aiui"
        dirlocal = diroot + "/data/zlocal/"

        ccols.news_activity_all = ['acquisition_price', 'activity_date', 'activity_id', 'activity_type', 'activity_url',
                                   'associated_company_ids', 'created_date', 'currency', 'initiator_company_company_id',
                                   'is_deleted', 'ma_type', 'partnership_type', 'publication_state', 'source',
                                   'summary',
                                   'updated_date']

        df1 = dfa.news_activity_all
        df1 = df1[df1['publication_state'] == 'PUBLISHED']

        def add_L0(x):
            x2 = ""
            if x['activity_type'] == "Partnership":
                x2 = 'partner-' + x['partnership_type']
            elif x['activity_type'] == "M&A":
                x2 = 'merger-' + x['ma_type']
            else:
                x2 = x['activity_type']
            x2 = str(x2).lower().replace("_", " ")
            return x2

        df1['L0_catnews'] = df1.apply(lambda x: add_L0(x), axis=1)

        def addinfo(x):
            dd = {"ma_price": x['acquisition_price'],
                  "ma_currency": x['currency'],
                  "initiator_comid": x['initiator_company_company_id'],
                  "associated_comid": x['associated_company_ids']
                  }
            return dd

        df1['info'] = df1.apply(lambda x: addinfo(x), axis=1)

        df1['url'] = df1['source']
        df1['date'] = df1['activity_date']
        df1['text'] = df1['summary']

        cols1 = ['activity_id', 'url', 'date', 'L0_catnews', 'text', 'info']
        df1 = df1[cols1]
        log(df1[['date', 'url']])

        #### Parnterships ###################################################
        cols2 = ['activity_id', 'L1_cat', 'L2_cat', 'L3_cat', 'L4_cat', 'com_extract_norm', ]
        df2 = dfa.news_partnership_activity[cols2]
        df2 = pd_add_L4_cat_industry_merge(df2, colsmerge=['L4_cat'], sep=" ; ")
        ### ['L1_cat', 'L2_cat', 'L3_cat', 'activity_id', 'com_extract_norm','created_date', 'dt', 'partnership_type', 'text', 'url', 'L4_cat'],

        df3 = df1.merge(df2[cols2], on=['activity_id'], how='left')
        df3 = df3[-df3['com_extract_norm'].isna()]  ### Partner
        log('partner', df3[['date', 'url']])

        #### Merger #########################################################
        ### ['L1_cat', 'L2_cat', 'L3_cat', 'L4_cat', 'acquisition_price', 'activity_id', 'art2_date', 'art_title', 'com_buyer',
        cols2 = ['activity_id', 'L1_cat', 'L2_cat', 'L3_cat', 'L4_cat', 'com_extract_norm']
        df2 = dfa.news_merger_activity

        df2 = pd_add_L4_cat_industry_merge(df2, colsmerge=['L4_cat'], sep=" ; ")
        df2['com_extract_norm'] = df2.apply(lambda x: x['com_extract_norm'] + " @@buyer: " + x['com_buyer'], axis=1)

        df2 = df1.merge(df2[cols2], on=['activity_id'], how='left')
        df2 = df2[-df2['com_extract_norm'].isna()]  ### Partner
        log('merger', df2[['date', 'url']])

        #### All concat #########################################################
        df3 = df3  ### Partner - extra field added
        df3 = pd.concat((df3, df2))  ### Merger  - extra field added
        df3 = pd.concat((df3, df1))  ### All news
        df3 = df3.drop_duplicates(['url', 'text'], keep='first')
        df3 = df3.fillna("")
        df3 = df3.sort_values(['date'], ascending=[False])

        df3['title'] = df3['text']
        df3['L3_catid'] = 0
        df3['L3_cat2'] = ""
        cols3 = ['activity_id', 'url', 'date', 'L0_catnews', 'title', 'text', 'info', 'L1_cat', 'L2_cat', 'L3_cat',
                 'L4_cat',
                 'com_extract_norm', 'L3_catid', 'L3_cat2']
        log(df3[cols3][['date', 'url']])

        #### Product page #########################################################
        df2 = dfa.news_product_all
        ## ['L1_cat', 'L2_cat', 'L3_cat', 'L3_catid', 'com_id', 'com_name', 'date',   'industry_update_item_id', 'news_type', 'title', 'url_text', 'url'],
        ## missing:  "['activity_id', 'L0_catnews', 'info', 'L4_cat', 'com_extract_norm']
        df2['url'] = df2['url_text'].apply(lambda x: str_extract_url(x))
        df2['text'] = df2['url_text'].apply(lambda x: str_remove_html_tags(x))
        df2['date'] = df2['date'].apply(lambda x: str(x).split(" ")[0])
        df2['L0_catnews'] = df2['news_type'].apply(
            lambda x: 'product - ' + str(x).lower().replace("_", " ").replace("none", ""))
        df2['activity_id'] = df2['industry_update_item_id']

        cols2 = ['activity_id', 'url', 'text', 'date', 'L0_catnews', 'title', 'L1_cat', 'L2_cat', 'L3_cat', 'L3_catid']
        df2a = pd_groupby_concat_string(df2, colgroup=cols2, colconcat='com_name', sep=" ; ")
        df2a['com_extract_norm'] = df2['com_name']

        dfcat4 = pd_groupby_concat_string(dfa.map_catid, colgroup=['L3_catid'], colconcat='L4_cat', sep=" , ")
        df2a = df2a.merge(dfcat4, on=['L3_catid'], how='left')
        df2a['info'] = ""
        df2a['L3_cat2'] = df2a['L3_cat']
        log(df2a[cols3].columns)

        log("##### Text missing   #####################################################")
        df3 = pd_add_Lcat_industry(df3)
        df3 = pd_add_textid(df3, coltext="text", colid='text_id')
        df3['text_summary'] = df3['text']
        df3['text_qdrant'] = ""
        df3['content_id'] = df3['text_id']
        df3['score'] = 0.0
        df3['com_extract'] = df3['com_extract_norm']
        df3['n'] = df3['text'].str.len()
        df3['news_type'] = df3['L0_catnews'].apply(lambda x: 'news-' + str(x).lower().replace("_", " "))
        df3['dt'] = df3['date']

        # df3                 = newsengine_add_news_title(df3, colout='title')
        # df3                 = newsengine_add_news_text(df3, colout='text')
        log(df3.head(1).T)
        log(df3[['date', 'url']])

        log("####### Export for df_edge_industry_activity #######################")
        log(df3[ccols.edge_industry_activity])
        colse = ['L0_catnews', 'L1_cat', 'L2_cat', 'L3_cat', 'L3_cat2', 'L3_catid', 'L_cat',
                 'com_extract', 'content_id', 'date', 'dt', 'info', 'n', 'news_type', 'score', 'text',
                 'text_id', 'text_qdrant', 'text_summary', 'title', 'url']

        ###
        dirout1 = diroot + "/data/zlocal/db/db_sqlite_tmp/df_edge_industry_activity.parquet"
        df0 = pd_read_file(dirout1)
        df4 = pd.concat((df0[ccols.edge_industry_activity], df3[ccols.edge_industry_activity]))
        df4 = df4.drop_duplicates(['url', 'text'], keep='first')
        df4['date'] = df4['date'].apply(lambda x: str(x).split(" ")[0])
        df4['content_id'] = df4['content_id'].astype("str")
        df4['info'] = df4['info'].astype("str")

        df4 = df4.sort_values(['date', 'com_extract'], ascending=[0, 0])
        log(df4[['date', 'url']])

        pd_to_file(df4[ccols.edge_industry_activity], dirout1, show=1)














