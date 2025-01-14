"""

    ##### 
        mkdir -p ./ztmp/db//qdrant_storage
        mkdir -p ./ztmp/db//qdrant_snapshots


       docker run -d -p 6333:6333     -v  ./ztmp/db//qdrant_storage:/qdrant/storage     qdrant/qdrant   


       http://localhost:6333/dashboard


       #################################################
          Lighting Warehouse
          Image Plus Consultants Ltd
          New Era Communications
          CASADEPAW
          Career Hound
          Fireflux
          CYBER CONSTABLE INTELLIGENECE; THE BEST RECOVERY EXPERT FOR CRYPTOCURRENCY
          TOH-The Orange Hotels
          Peace Culture Culb
          EarthaPro
          Mida Technologies Inc
          Tilt
          GX Ventures
          Bluug
          Apple Marketing LLC
          Youth Advocacy Council
          TransHelp


"""
import json, os, warnings, random, string
warnings.filterwarnings("ignore")
import pandas as pd, numpy as np
from pydantic import BaseModel, Field
from typing import List, Dict, Union, Tuple
from copy import deepcopy

from utilmy import log, log2, pd_read_file, pd_to_file, json_save, date_now
from utilmy import diskcache_load, diskcache_decorator



from rag.engine_tv import fusion_search
from rag.engine_qd import QdrantClient
from rag.engine_sql import dbsql_fetch_text_by_doc_ids
from rag.engine_qd import EmbeddingModelSparse
from rag.llm import LLM, llm_cleanup_gpt_jsonformat, promptRequest




##########################################################################################
def test1(q="""  Recent Partnership of Microsoft     """):

    res = search_run(q, server_url="http://127.0.0.1:6333",
                                         engine="sparse",
                                         topk=10, llm_model="gpt-4o-mini", llm_max_tokens=1000)
    log(res)


def clean():
    from utilmy import pd_read_file, pd_to_file, hash_int64
    # preprocessing
    df = pd_read_file("./ztmp/df_LZ_merge_90k.parquet")
    log(df)
    df["text_id"] = df["url"].apply(lambda x: hash_int64(x))
    df.rename(
        columns={"pred-L1_cat": "L1_cat", "pred-L2_cat": "L2_cat", "pred-L3_cat": "L3_cat", "pred-L4_cat": "L4_cat"},
        inplace=True)
    df.fillna("", inplace=True)
    pd_to_file(df, "../ztmp/df_LZ_merge_90k_tmp.parquet")






#########################################################################################
from box import Box
ccols = Box({})
# {
#     "task": ["compare", "summarize"]

#     "date": ['this year']
#     "date_period": ['in']
#  L-cat:    "industry_tags": ['Cloud medical computing", "military health" ]
#  com_extract   "company_names": ["Palto Alto", "Meta world"],
# L0_catnews  "activity_tags": ["acquisition"],
#.   "context": ["companies in America", "not in canada"]
# }

ccols.cols_qdrant = ['url', 'date', 'L0_catnews', 'L_cat', 'com_extract', 'text_qdrant', 'info']
ccols.cols_sqlite = ["url", "date", "L0_catnews", "L_cat", "com_extract", "title", "text", "text_summary", "info", 'score' ]


def create_qdrant_table():
    """
          alias pyqd="python3 -u rag/engine_qd.py  "
          export dirtmp="./ztmp"
          export server="http://localhost:6333"


          export dirparquet="$dirtmp/rag/df_internal_news_2024_RAG_8879.parquet"

      ### create collection
          pyqd  qdrant_sparse_create_collection --server_url $server --collection_name "LZnews"


      ### set payload settings
          pyqd  qdrant_update_payload_indexes --server_url $server --collection_name "LZnews" --payload_settings "{ 'L0_catnews': 'text', 'L_cat': 'text','com_extract': 'text', 'date': 'text',  'info': 'text'}"


      ### index documents
          pyqd  qdrant_sparse_create_index --dirin $dirparquet --server_url $server --collection_name "LZnews" --colscat "text_id, com_extract, L_cat, date, L0_catnews, info"  --collection_name 'LZnews' --coltext "text_qdrant" --batch_size 64 --max_words 512 --imax 10000


     http://localhost:6333/dashboard#/collections/LZnews

    """


def create_sql_table():
    """
                python -m spacy download en_core_web_sm

                alias pykg="python3 -u rag/engine_kg.py"
                export dirtmp="./ztmp"

                export  db="$dirtmp/db/db_sqlite/datasets.db"
                export  data="$dirtmp/rag/df_LZ_merge_90k_tmp.parquet"
                chmod 777  $db


            export dirparquet="$dirtmp/rag/df_internal_news_2024_RAG_8879.parquet"

            ### Create SQL table with column settings
                pykg dbsql_create_table --db_path $db --table_name "LZnews" --columns '{"text_id": "VARCHAR(255) PRIMARY KEY","url": "VARCHAR(255)", "title": "VARCHAR(255)", "date": "VARCHAR(255)", "text": "TEXT", "text_summary": "TEXT", "L0_catnews": "VARCHAR(255)", "L_cat": "VARCHAR(255)",  "com_extract": "VARCHAR(255)",  "info": "TEXT"  }'

            ### Insert in sqlite
                export nrows="10000"
                pykg dbsql_save_records_to_db   --dirin $dirparquet   --db_path $db  --table_name "LZnews" --coltext "text"  --colscat 'url,date,title,text,text_summary,L0_catnews,L_cat,com_extract,info' --colid "text_id" --nrows $nrows


    """




#########################################################################################
global sparse_model
sparse_model = None

global dfacti, dfcom, dfcom2 
dfacti, dfcom, dfcom2 = None, None, None



#########################################################################################
from utilmy import json_load

# @diskcache_decorator
def jload_cache(dirin):
    return json_load(dirin)




#########################################################################################
msg_error0 = jload_cache("ui/static/answers/zfallback_error/data.json")


msg_no_enough = deepcopy(msg_error0)
msg_no_enough['html_tags']['summary'] = "No answers, please enlarge the scope of your question"


msg_error = deepcopy(msg_error0)
msg_error['html_tags']['summary'] = "No answers, Internal System issues"


msg_too_many = deepcopy(msg_error0)
msg_too_many['html_tags']['summary'] =     "Our apologies. There are too many results related to this question. Please refine the question scope."
log('msg loaded')







os.environ['istest'] = "0"



def do_exists(var_name):
    return var_name in locals() or var_name in globals()





#########################################################################################
from functools import lru_cache

@lru_cache(maxsize=None)
def load_all_dataset(dname="com,indus,overview,insight"):
    global dfacti, dfcom, dfcom2, dfover, dfinsight

    if "com" in dname:
        dfcom   = pd_read_file("ztmp/db/db_sqlite/df_com_all.parquet")
        log("dfcom:", dfcom.shape, dfcom.columns)

        dfcom2 = pd_read_file("ztmp/db/db_sqlite/df_com_all_info.parquet")
        log("dfcom2:",  dfcom2.shape,  dfcom2.columns)


    if "indus" in dname:
        colstxt = ['text_id', 'url', 'date', 'title', 'text', 'score', 'L0_catnews', 'L_cat', 'com_extract' ]
        dfacti  = pd_read_file("ztmp/db/db_sqlite/df_edge_industry_activity.parquet")
        dfacti = dfacti[colstxt]
        log("dfindus:",  dfacti.shape,  dfacti.columns)


    if "overview" in dname:
        cols2  = ['text_id', 'url', 'date', 'title', 'text',  'L_cat' ]
        dfover = pd_read_file("ztmp/db/db_sqlite/df_edge_industry_overview.parquet", cols=cols2)
        log("dfover:",  dfover.shape,  dfover.columns)


    if "insight" in dname:
        cols2  = ['text_id', 'url', 'date', 'title', 'text',  'L_cat' ]
        dfinsight = pd_read_file("ztmp/db/db_sqlite/df_edge_industry_insight.parquet", cols=cols2)
        log("dfinsight:",  dfinsight.shape,  dfinsight.columns)




class tasks:
  describe_company = "decribe company"





def str_docontain(words, x):
    x2 = str(x).lower()
    for wi in words.split(" "):
        if wi.lower() not in x2 : return False 
    return True


def str_fuzzy_match_list(xstr:str, xlist:list, cutoff=70.0):
    from rapidfuzz import process, fuzz
    results = process.extract(xstr, xlist, scorer=fuzz.ratio, score_cutoff=cutoff)
    return [result[0] for result in results]



def str_fuzzy_match(str1, str2, threshold=95):
    from rapidfuzz import fuzz
    score = fuzz.ratio( str(str1).lower(), str(str2).lower() )
    if score >= threshold : return True 
    return False



def pd_find_com(dfcom, llg, threshold=90):
    dfkall = pd.DataFrame()
    for w in llg.query_tags['company_names']:
       dfk = dfcom[ dfcom['name'].apply(lambda x : str_fuzzy_match( w,  x, threshold= threshold ) ) ] 
       log(w, dfk.shape)
       if len(dfk)>0:
           dfkall = pd.concat((dfkall, dfk))
    return dfkall



def query_normalize(q):

  q = q.replace("Give me",  "Describe")
  q = q.replace("What are", "Describe")
  q = q.replace("What is",  "Describe")
  q = q.replace("Provide details on", "Describe")
  log("new query", q)

  return q 


def search_run(cfg=None, cfg_name="test", query: str = "",
                                   llm_service: str = "openai", 
                                   llm_model: str = "gpt-4o-mini",
                                   llm_max_tokens: int = 16000, istest=1,
                                   dirout="./ztmp/chat_log/"

                                   ):
    """Search and summarize text based on the given query using a sparse model and LLM.

       export OPENAI_KEY=""
       alias pysum="python3 -u rag/rag_summ.py "

       modelid="gpt-4o-2024-08-06"
       pysum search_summarize_with_citation --query "What are the microsoft partnerships in 2024 ?"  --llm_model $modelid --topk 20


       pysum search_summarize_with_citation --query "What are the activities in generative ai  in 2024 ?"  --llm_model $modelid --topk 10

       pysum search_summarize_with_citation --query "What are the partnerships between Amazon and  Microsoft in generative ai in 2024 ? show the most relevant at first"  --llm_model $modelid --topk 5

       source ../../../scripts/bins/env.sh


    """
    log("\n######### New query #########################################################")
    log(query)
    global sparse_model, dfcom
    llg = Box({'query_id': date_now(fmt="%Y%m%d_%H%M%S") + "-" + str(int(random.uniform(1000,9999)))  })
    llg.query_input_user = query
    llg.dirout           = dirout

    prefix = query.split("@@@")[0]
    query2 = query.split("@@@")[-1]
    llg.query2 = query2


    if "gpt mode" in prefix  in query or 'definition' in llg.query2  :
        msg_dict =   task_gpt_answer(llg)
        return msg_dict


    debug = False
    if "debug" in prefix:
        query2 = query2.replace("debug", "").replace("debug.", "")
        debug  = True

    llg.query = query_normalize(query2)


    log("######## Extract tags from question    ################## ")
    llg.query_tags = llm_question_extract_NER(question=llg.query2, llm_service=llm_service,
                                              llm_model="gpt-4o-mini", llm_max_tokens=1000)
    if llg.query_tags is None :
       return msg_no_enough

    msg1 = summary_question_error_handle(llg.query2, llg.query_tags)
    if msg1 is not None:
       log(msg1); return msg_no_enough


    llg.query2 = summary_question_rewrite(llg.query2, llg.query_tags)
    llg.task   = llg.query_tags['task']
    log('task:', llg.task)
    load_all_dataset()


    ####### Task ##################################################################
    if 'describe_company' in llg.task :
        msg_dict = task_com_describe(llg)
        return msg_dict


    if 'describe_industry' in llg.task :
        msg_dict = task_indus_overview(llg)
        return msg_dict 


    # llg.sparse_collection_name = llg.query_tags['data_source']
    log("####### Default case: Search and summarize text based on activity only.")
    msg_dict= task_search_activity(llg)
    return msg_dict



#####################################################################################
######### Task Definition ###########################################################

def task_gpt_answer(llg):


    dout = jload_cache("ui/static/answers/gpt_answer/data.json")

    query = llg.query2
    llm_service: str = "openai",
    llm_model: str = "gpt-4o-mini",
    llm_max_tokens = 16000; istest = 1,

    llm_1 = LLM(llm_service, llm_model, max_tokens=llm_max_tokens)
    llg.prompt = query
    query2 = query.replace("open mode.", "").replace("open mode", "")
    query2 = query.replace("gpt mode.", "").replace("gpt mode", "")
    llm_json = llm_1.get_save_sync(prompt=query2, output_schema=None, dirout=None)
    msg = llm_json["choices"][0]["message"]["content"]

    #msg  = "**Summary** \n\n " + msg
    #msg2 = answer_format(msg)
    llg.msg_answer = msg

    dout['html_tags']['summary'] = msg

    json_save2(llg, llg.dirout)
    return dout



def task_com_describe(llg)->Dict:
    """
        ui/ui/static/answers/com_describe/data.json

        "html_tags": {
         "com_list": [
            {
              "url": "https://eeddge.com/companies/362567",
              "com_id": "362567",
              "name": "OpenAI",
              "text": "OpenAI is an AI research lab and applied AI company building artificial general intelligence (AGI) and derived generative AI products and services. OpenAI was founded in 2015 as a non-profit organization with a commitment of USD 1 billion from Sam Altman (OpenAI CEO), Tesla’s Elon Musk, Microsoft, and AWS."
            },

    """
    global dfcom, dfcom2
    dfkall = pd_find_com(dfcom, llg, )         
    if len(dfkall) < 1: 
       dfkall = pd_find_com(dfcom2, llg, )    
       if len(dfkall) < 1: 
          return msg_no_enough     

    dout = jload_cache('ui/static/answers/com_describe/data.json' )
    dd   = []

    for k, x in dfkall.iterrows():
       xout = {}
       xout['url']    = "https://eeddge.com/companies/" + str(x['com_id'])
       xout['com_id'] = x['com_id']
       xout['name']   = x['name']
       xout['text']   = x['description']
       dd.append(xout)

    dout['html_tags']['com_list'] = dd
    llg.msg_answer  = dout


    ##### Clean up ######################
    json_save2(llg, llg.dirout)
    return dout




def task_indus_overview(llg):
    """

  "html_tags": {
    "overview_list": [
      {
        "name": "Carbon Capture, Utilization & Storage (CCUS)",
        "text": "Climate efforts so far have had limited tangible results, and global emissions have continued to increase every year, as current efforts to reduce emissions from hard-to-decarbonize industries such as oil and gas, power, steel, cement, fertilizers, etc., have been inadequate. Carbon capture is one method that can remove carbon dioxide (CO2) emissions from these heavy industries. Moreover, newer technologies like direct air capture (DAC) can also reduce the carbon footprints of industries that do not have active flue stacks, such as construction and data centers, as well as non-stationary emissions from transportation. Carbon capture technologies, along with utilization and sequestration, would play a vital role in quickly decarbonizing economies over the next few decades to reach aggressive zero-emission targets.",
        "url": "https://eeddge.com/industry/63",
        "date": ""
      },


    """
    log("########## Start task_describe_industry  #####################")
    global dfacti, dfover, dfinsight

    dout = jload_cache('ui/static/answers/indus_overview/data.json' )
    dd   = []

    log("##### Overview ###############################################")
    dfi = deepcopy(dfover)
    for w in llg.query_tags['industry_tags']:
       w1 = str(w).lower().strip() 
       for wi in w1.split(" "):      
          log(wi)
          dfi = dfi[ dfi['title'].apply(lambda x:  wi in str_norm(x).split(" ")   ) ] 
          log(dfi)
          log(dfi.shape)

    # if len(dfi)<1: 
    #     dfi = deepcopy(dfover)
    #     for w in llg.query_tags['industry_tags']:
    #        w1  = str(w).lower() 
    #        dfi = dfi[ dfi['text'].apply(lambda x:  w1 in x  ) ] 

    # if len(dfi)<1: 
    #     return msg_no_enough
    log(dfi)
    dd = []
    for k, x in dfi.iterrows():
       xout = {
          #'name':  x['title'],
          'title': x['title'],
          'url':   x['url'],
          'date':  x['date'],
          'text':  x['text'],
       }
       dd.append(xout)

    dout['html_tags']["overview_list"] = dd


    log("##### Insight ###########################################")
    dfi = deepcopy(dfinsight)
    for w in llg.query_tags['industry_tags']:
       w1 = str(w).strip().lower() 
       for wi in w1.split(" "):      
          log(wi)
          dfi = dfi[ dfi['title'].apply(lambda x:  wi in str_norm(x).split(" ")   ) ] 
          log(dfi.shape)

    if len(dfi)<1: 
        dfi = deepcopy(dfinsight)
        for w in llg.query_tags['industry_tags']:
           w1  = str(w).lower() 
           for wi in w1.split(" "):      
              log(wi)          
              dfi = dfi[ dfi['text'].apply(lambda x:  w1 in  str_norm(x).split(" ")   ) ] 
              log(dfi.shape)

    # if len(dfi)<1: 
    #     return msg_no_enough

    log(dfi)
    dfi  = dfi.iloc[:3,:]
    dd = []
    for k, x in dfi.iterrows():
        xout = {
            #'name': x['title'],
            'title': x['title'],
            'url': x['url'],
            'date': x['date'],
            'text': x['text'],
        }
        dd.append(xout)

    dout['html_tags']["insight_list"] = dd


    log("##### Activity #########################################")
    dfi = deepcopy(dfacti)
    for w in llg.query_tags['industry_tags']:
       w1 = str(w).strip().lower() 
       for wi in w1.split(" "):
           dfi = dfi[ dfi['L_cat'].apply(lambda x:  wi in str_norm(x).split(" ")  ) ] 
           log(dfi.shape)

    if len(dfi)<1: 
        dfi = deepcopy(dfacti)
        for w in llg.query_tags['industry_tags']:
           w1  = str(w).lower() 
           dfi = dfi[ dfi['title'].apply(lambda x:  wi in str_norm(x).split(" ")   ) ] 

    # if len(dfi)<1: 
    #     return msg_no_enough

    dfi = dfi.sort_values('date', ascending=False)
    dfi = dfi.iloc[:5,:]

    log(dfi[[  'date', "L_cat", 'text'  ]])
    dd = []
    for k, x in dfi.iterrows():
        xout = {
            #'name': x['title'],
            'title': x['title'],
            'url': x['url'],
            'date': x['date'],
            'text': x['text'],
        }
        dd.append(xout)

    dout['html_tags']["activity_list"] = dd


    ######### return msg_no_enough
    log("##### Final html ####################################")
    llg.msg_answer  = dout
    # llg.msg_display = msg
    # log(msg)

    ##### Clean up ######################
    log(str(dout)[:200])
    json_save2(llg, llg.dirout)
    return dout




def task_search_activity(llg):
    """
       "html_tags": {
    "summary": "Tesla (NASDAQ: TSLA) is an American multinational automotive and clean energy company. It designs and manufactures electric vehicles (EVs; including cars and trucks), battery energy storage systems, solar panels, solar roof tiles, and other related products and services. Tesla was incorporated in 2003 as Tesla Motors, named after the inventor and electrical engineer Nikola Tesla. Entrepreneur and investor Elon Musk became the largest shareholder of the company following an investment in 2004 and has been serving as the CEO of Tesla since 2008. Even though Tesla accounts for only around 1% of the global vehicle market share (as of March 2022), it is one of the largest listed companies globally. The company reported revenue of USD 96.8 billion in 2023 and hit a market cap of USD 1 trillion in October 2021 for the first time, after 11 years since listing—joining only a handful of companies to have done so. Tesla steered its way to the top 100 of the Fortune 500 list for the first time in 2021 and remained within the cluster in 2023 as well.",
    "activity_list": [

         "**Memo: Partnerships of Microsoft in Generative AI - 2024**
     \n\nIn 2024, Microsoft has actively engaged in strategic partnerships to enhance its generative AI capabilities,
     focusing on ethical AI solutions and compliance. These collaborations aim to integrate advanced AI technologies into Microsoft's ecosystem,
     making them more accessible to businesses.
     The partnerships also emphasize navigating regulatory challenges while maximizing the potential of AI offerings.
     Key players in these initiatives include technology providers and consulting firms, reflecting a commitment to responsible AI development.
     \n\n---\n\n** Synergist Technology partners with Microsoft to advance ethical AI solutions  **\n
     2024-08-29  \n [Synergist Technology partners with Microsoft](https://eeddge.com/updates/33088)  \n
     Synergist Technology has partnered with Microsoft to develop compliant AI solutions, integrating its AFFIRM platform
     into Microsoft's Marketplace.

     This collaboration aims to enhance accessibility for businesses and involves partners like Pliant Consulting and Maureen Data Systems.

     The initiative focuses on helping businesses navigate complex AI regulations while leveraging Microsoft's AI capabilities.",



    """
    topk = 3
    llm_service = "openai"
    llm_model   = "gpt-4o-mini"
    llm_max_tokens = 4000
    query = llg.query2
    log("########## Start task_search_activity  ##########################")

    dout = jload_cache('ui/static/answers/search_activity/data.json' )
    dd   = []


    log("\n####### Fetch actual text from SQL DB ################################# ")
    #### match date pattern here
    # text_ids = [res["text_id"] for res in llg.results ]
    global dfacti
    if dfacti is None:
        cols = ['text_id', 'url', 'date', 'title', 'text', 'score', 'L0_catnews', 'L_cat', 'com_extract']
        dfacti = dbsql_fetch_text_by_doc_ids(db_path=llg.db_path_sql,
                                             table_name=llg.table_name_sql, cols=cols, text_ids=[])
        dfacti = pd.DataFrame(dfacti)

    dftxt = deepcopy(dfacti)
    log('Doc retrieved:', dftxt, dftxt.shape)


    log("#### Doc Keyword filtering ##############################")
    # def str_docontain(w, x):
    #     x2 = str(x).lower()
    #     for wi in w.split(" "):
    #         if wi.lower() not in x2 : return False
    #     return True

    for w in llg.query_tags['company_names']:
        dftxt = dftxt[dftxt['com_extract'].apply(lambda x: str_docontain(w, x))]
        log(w, dftxt.shape)
        # if len(dftxt) < 1: return msg_no_enough

    for w in llg.query_tags['activity_tags']:
        dftxt = dftxt[dftxt['L0_catnews'].apply(lambda x: str_docontain(w, x))]
        log(w, dftxt.shape)
        # if len(dftxt) < 1: return msg_no_enough

    for w in llg.query_tags['industry_tags']:
        dftxt = dftxt[dftxt['L_cat'].apply(lambda x: str_docontain(w, x))]
        log(w, dftxt.shape)
        # if len(dftxt) < 1: return msg_no_enough

    for w in llg.query_tags['date']:
        dftxt = dftxt[dftxt['date'].apply(lambda x: str_docontain(w, x))]
        log(w, dftxt.shape)
        # if len(dftxt) < 1: return msg_no_enough

    if len(dftxt) < 1:
        log("empty, searching into text ")
        dftxt = deepcopy(dfacti)
        for w in llg.query_tags['industry_tags']:
            dftxt = dftxt[dftxt['text'].apply(lambda x: w in x)]
            log(w, dftxt.shape)

    if len(dftxt) < 1:
        return msg_no_enough

    if len(dftxt) > 500:
        return msg_too_many

    log("#### Doc Re-Ranking ######################################")
    ### Re rank based on doc individual relevance
    # dfqd = pd.DataFrame(llg.results)
    # dfqd.columns =['text_id', 'score_qd']
    # dftxt    = dftxt.merge(dfqd, on=['text_id'], how='left')

    t0 = date_now(returnval='unix')
    # def rerank_score(x):
    #  return float(x['score']) * x['score_qd']

    # dftxt['score2'] = dftxt.apply(lambda x: rerank_score(x), axis=1  )
    # dftxt = dftxt.sort_values(['score2'], ascending=[0])

    # if len(llg.results)> 80:
    #     lscores = np.array([ x['score'] for x in llg.results  ])
    #     q25 = np.quantile(lscores, 0.25)
    #     llg.results =  [ x for x in llg.results if x['score'] > q25 ]

    log("\n####### Dsiplay ranking ############################################## ")
    dftxt = summary_display_ranking(dftxt, llg.query_tags)

    log("\n####### Format Docs prompt ########################################### ")
    topk = min(5, topk)
    multi_dftxt = []
    for ii, doc in dftxt.iloc[:topk, :].iterrows():
        url = doc['url']
        title = doc['title']
        text = doc['text']
        date = doc['date']

        txt = f""" title: {title}\ndate:{date}url:{url}\ntext:{text}"""
        multi_dftxt.append(txt)

    multi_doc_str = "\n---\n".join(multi_dftxt)
    log('Doc appended:', ii + 1)
    log('Full doc size: ', len(multi_doc_str), 'chars, ', len(multi_doc_str.split(" ")), ' words')

    if os.environ.get('istest', "0") == "1":
        return multi_doc_str

    log("\n#######  LLM :Summarize #############################################")
    llm_1 = LLM(llm_service, llm_model, max_tokens=llm_max_tokens)

    llg.llm_prompt_id = "summarize_02_noref"   #"summarize_01"
    tsk0 = ",".join(llg.query_tags['task'])
    log("tasks: ", tsk0)
    if 'report' in tsk0:
        llm_prompt_id = "report_00"
    log("Prompt used:", llg.llm_prompt_id)

    ptext = promptlist[ llg.llm_prompt_id]
    ptext = ptext.replace("<question>", query)
    ptext = ptext.replace("<multi_doc_string>", multi_doc_str)
    llg.prompt = ptext


    log("LLM call")
    llm_json = llm_1.get_save_sync(prompt=ptext, output_schema=None, dirout=None)
    # log(llm_json)
    msg = llm_json["choices"][0]["message"]["content"]
    llg.msg_answer = msg
    # log(msg)

    msg2 = msg.replace("**Overview Summary:**", "")
    msg2 = msg2.replace("**Market Trend Analysis:**", "")
    # msg2 = answer_format(msg)
    llg.msg_display = msg2
    # log(msg2)

    # i0= find_str(msg2, "\n\n", 2)
    # i1= find_str(msg2,     "\n\n", i0+1)
    #
    # summary = msg2['msg'][i0:i1]
    dout['html_tags']["summary"] = msg2

    # msgi = msg2[i1:]

    dd = []
    for ii, doc in dftxt.iloc[:topk, :].iterrows():
        xout =       {
          "title": doc['title'],
          "url":   doc['url'],
          "date":  doc['date'],
          "text":  doc['text']
        }
        dd.append(xout)

    dout['html_tags']["activity_list"] = dd


    log("##### Final html ####################################")
    llg.msg_answer  = dout
    json_save2(llg, llg.dirout)

    return dout



def find_str(x:str,x2:str, istart=0):
    try:
        i1 = x.find(x2, istart)
        return i1
    except Exception as e:
        return -1









##################################################################################################
def rag_search_fusion(llg):
    log("######## Fusion search   ################################################ ")
    if "fusion_search":
        "test"
        # query_filter = qdrant_query_createfilter_custom(llg.query_tags)
        # client       = QdrantClient(server_url)
        # if sparse_model is None:
        #     sparse_model = EmbeddingModelSparse()

        # results = fusion_search(query= llg.query2, engine=engine, client=client,
        #                               sparse_collection_name= llg.sparse_collection_name,
        #                               neo4j_db="neo4j", sparse_model=sparse_model,
        #                               query_tags=None, query_filter= query_filter,
        #                               topk= qdrant_topk
        #                         )

        # llg.results  = [{"text_id": text_id, "score": score} for text_id, score in results.items()]
        # log2('Retrieved all:', len(llg.results))
        # if len(llg.results)< 1:
        #    msg = 'Empty results'
        #    json_save2(llg, dirout)
        #    log2(msg); return msg

        # log('Retrie Filter: ', len(llg.results))
        # if len(llg.results)< 1:
        #    msg = 'Empty results'
        #    json_save2(llg, dirout)
        #    log2(msg); return msg



def rag_search_embedding():
    """
    engine="sparse",
    server_url: str = "http://localhost:6333",
    # sparse_collection_name: str = "LZnews",

    table_name_sql = "LZnews",
    db_path_sql = "./ztmp/db/db_sqlite",

    llm_prompt_id = "summarize_01",
    topk: int = 10,

    qdrant_topk = 1000,
    qdrant_score_min = 20.0,

    # llg.table_name_sql         = llg.query_tags['data_source']
    # llg.db_path_sql            = f"{db_path_sql}/{llg.table_name_sql}.db"
    # llg.db_path_sql            = f"./ztmp/db/db_sqlite/datasets.db"

    ### log('db:', llg.db_path_sql, llg.sparse_collection_name )
    ### llg.query_tags = summary_tags_expansion(query, llg.query_tags)
    """
    pass





##################################################################################################
def answer_format(msg)->dict:
    msg_list = msg.split("\n")
    msgs2 = []
    for xi in msg_list:
        if "**Overall Summary:**" in xi:
            xi = xi.replace(":**", ":**\n")

        elif "**Title:**" in xi:
            xi = xi.replace("**Title:**", "")
            xi = "**" + xi + "**"

        elif "**Date:**" in xi:
            xi = xi.replace("**Date:**", "")

        elif "**URL:**" in xi:
            xi = xi.replace("**URL:**", "")

        elif "**Summary:**" in xi:
            xi = xi.replace("**Summary:**", "")
            # xi = "*" + xi +"*"
        msgs2.append(xi)

    msg2 = "\n".join(msgs2)

    msg2 ={
      'msg' : msg2,
      'msg_format': 'markdown'
    }
    return msg2 



promptlist = {

    'summarize_00': f"""Summarize information from below articles using bullets points.
        Make sure the the summary contain factual information extracted from the articles.
        Provide inline citation by numbering the article information is fetched from.
        Add numbered article details(date, url, title) in footnotes.\nArticles: \n```\n<multi_doc_string>\n```
        """


    ,'summarize_02_noref': f"""You are a market researcher. 
      Provide an overview summary from below articles in 5 lines maximun.
      Provide a market trend analysis  in 2 lines.
      Summary should only contain only facts extracted only from the articles.
      Re-read the above task question again.
      
     \n\nArticles\n\n:
     ```\n<multi_doc_string>\n```
    """



    ,'report_00': f"""You are a market researcher. Write a report of one page.
        Summarize information from below articles into 4 or 5 paragraphs.        
        Make sure the the summary contain factual information extracted from the articles.
        Write the report following this structure:
          Title
          Summary
          Conclusion
          References

        References should the list of articles with the original url


        <Input text>:
        ```\n<multi_doc_string>\n```  

        """


    , 'summarize_01': f"""
        You are a businesss intelligence researcher writing a memo about <question>  for business executives.
        The memo contains the following:

        At the beginning, provide overall summary of all the articles in 5 lines.      
        Keep only factual information.   

        Then, for each news article below, provide those information as follow:
                title 
                date
                URL
                Summary of the article in 4 lines. Keep only factual information and concise text.

        News articles are below:

       ```\n<multi_doc_string>\n``` 
        """



    , 'P03': f"""Write down a small introduction, replying to the question, Summarize each news article individually using bullets point and attach URL and article date.
     Make sure the summaries contain factual information extracted from the article.
     Write down a conclusion for the overall news articles and topics. \nArticles: \n```\n<multi_doc_string>\n```
     """


}






def json_save2(llg, dirout):
    y,m,d,h = date_now(fmt="%Y-%m-%d-%H").split("-")
    ts      = date_now(fmt="%y%m%d_%H%M%s")
    json_save(llg.to_dict(), dirout + f"/year={y}/month={m}/day={d}/hour={h}/chat_{ts}.json" )


def str_norm(text):
    return str(text).lower().translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation)))




############################################################################################
def summary_question_error_handle(query, query_tags):
    try:
        q= query_tags
        #if len(query_tags['company_names']) < 1:
        #     return "Question should contain at least one company name."

        if len(query_tags['data_source']) < 1:
             return "Question should contain one data source."

        if len(q['industry_tags']) < 1 and len(q['activity_tags']) < 1 and len(q['company_names']) < 1  :
             return "Our apologies. Please refine your question: some company name, some industry or some kind of corporate activity such as: partnerships, activities"


    except Exception as e:
        log(e)
        return "Question cannot be analyzed"
    return None    


def summary_question_rewrite(query, query_tags):
  q2 = query.lower()
  q2 = q2.replace("what are", " ").replace("?", " ")

  q3 = []
  for x in q2.split("."):
     x2 = x.lower()
     if 'most relevant' in x2 or 'most recent' in x2: continue
     q3.append(x)

  q3 = ". ".join(q3)
  log2('\nquestion rewrite: ', q3)
  return q3 


def summary_display_ranking(dftxt, query_tags=None):

    if  query_tags is None or  'display_tags' not in query_tags:
        display_tag = 'most_recent'
    
    elif len(query_tags['display_tags']) < 1:
        display_tag = 'most_recent'
    else:
        display_tag = query_tags['display_tags'][0]


    log("Display results:", display_tag)
    if 'most_recent' in display_tag: 
        dftxt  = dftxt.sort_values('date', ascending=0)

    elif 'most_relevant' in display_tag: 
        dftxt  = dftxt.sort_values('date', ascending=0)

    dftxt.index = np.arange(0, len(dftxt)) 
    return dftxt




###########################################################################################
######## Question Entity Extraction #######################################################
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

    task: list          = Field(description="List of tasks ")

    # data_source: str   = Field(description="List of data source \"news\", \"industry\",  ")


    date_period: str    = Field(description="before/between/after/in")
    date: list          = Field(description="Dates information in the text in this format:  YYYY  or YYYY-MM")

    company_names: list = Field(description="Names of the corporate entities")
    industry_tags: list = Field(description="tags related to company or business industries such as generative ai,  healthcare, data ")


    # industry_tags_exclude: list = Field(description="tags which are excluded, tags is related to company or business industries such as healthcare, ai ")


    activity_tags: list = Field(description="company activity or actions mentioned in the text. Example: partnership, acquisition, collaboration")

    context:       list = Field(description="words of the text that did not get categorized in other fields")

    display_tags:  list = Field(description="list of tags to describe how the results should be ranked: 'most_recent', 'most_relevant' ")




def llm_question_extract_NER(question="Summarize the news", llm_service="openai", 
                             llm_model="gpt-4o-mini", llm_max_tokens=1000) -> dict:
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
    prompt = """
    Extract specific tags from the question below:
    ## question:
    {question1}


    Reread the question again:
    ## question:
    {question1}
    
    
    Make sure that the extracted tags are extracted from the sentence.
    Do not invent tags which is not in the question.

    ### Example of task:
      describe     
      summarize
      make a report
      what are
      find company
      unknown


    ### Example of activity_tags:
      activities
      partnership
      funding
      acquisition
      merger
      m and a
      news
      product
      service
      earnings
      listing
      expansion
      management
      approval
      regulation


    ### Example of industry_tags :
      carbon capture
      5g
      accelerator
      access
      additive
      advertising
      aerospace
      agri
      agricultural
      ai
      ai drug
      air
      aircraft
      airline
      airport
      alternative
      alternative energy
      analytic
      apparel
      application
      athletic
      augmented
      automated
      automation
      automobile
      aviation
      bank
      banks
      batteries
      battery
      beauty
      beverage
      big data
      bio
      bio materials
      biofuels
      biometric
      biotech
      blockchain
      brewing
      business
      capital
      car
      carbon
      care
      cell
      center
      chain
      chemical
      chinese
      chocolate
      climate
      clinical
      cloud
      code
      coffee
      commerce
      commercial
      communication
      community
      complex
      component
      computer
      computing
      connected
      conservation
      construction
      consulting
      consumer
      content
      contract
      contractors
      cosmetic
      coworking
      crm
      cryptocurrency
      cultured
      customer
      cyber
      cyber insurance
      cybersecurity
      dairy
      data
      data center
      data infrastructure
      decentralized
      defense
      delivery
      design
      development
      device
      devops
      digital
      digital privacy
      digital retail
      digital twin
      digital wellness
      display
      distribution
      document
      drone
      drug
      e-commerce
      edge
      edge computing
      edtech
      education
      egg
      electronic
      employee
      energy
      engagement
      engine
      engineering
      entertainment
      environmental
      equipment
      esport
      estate
      ev
      expense
      experience
      extended
      extended reality
      facial
      facial recognition
      factory
      fan
      farm
      farming
      fashion
      fast
      fertility
      fertilizers
      finance
      financial
      financial wellness
      fintech
      fitness
      fleet
      food
      foods
      foundation
      foundation models
      freelancing
      gaming
      gas
      gen
      genai
      gene
      generative ai
      genomic
      genomics
      geothermal
      good
      gps
      graphics
      grid
      grocery
      health
      home
      hospitality
      hotel
      household
      human
      hydrogen
      identity
      identity access
      imaging
      industrial
      information
      infrastructure
      ingredient
      innovation
      insurance
      insurtech
      intelligence
      language
      last
      last mile
      learning
      lithium
      livestock
      logistics
      longevity
      luxury
      machine
      machine learning
      management
      manufacturing
      marine
      market
      marketing
      marketing automation
      material
      meat
      media
      medical
      medicine
      mental
      metaverse
      metro
      mile
      mining
      mobile
      mobility
      models
      natural
      navigation
      network
      networking
      next
      novel
      nutrition
      oil
      online
      open source
      optimization
      organic
      packaging
      pay
      pay later
      payment
      performance
      personal
      pet
      pharma
      plant-based
      precision
      precision medicine
      prefab
      primary
      printing
      privacy
      process
      productivity
      project
      property
      psychedelic
      quantum
      quantum computing
      quick-service
      r&d
      rail
      railway
      real
      real estate
      reality
      recognition
      relationship
      remote
      remote work
      research
      residential
      resorts
      resource
      restaurant
      retail
      revenue
      ride
      risk
      robotics
      robots
      sales
      satellite
      science
      search
      sector
      security
      semiconductor
      serverless
      service
      shipping
      signature
      simulation
      skincare
      smart
      smartphone
      social
      software
      solutions
      space
      space travel
      specialty
      sport
      storage
      store
      streaming
      supply chain
      sustainable
      system
      tele
      telecom
      testing
      textile
      therapeutic
      therapy
      tourism
      toy
      trading
      transformation
      transportation
      travel
      trial
      truck
      twin
      vaccine
      vehicle
      venture
      venture capital
      virtual
      virtual reality
      vision
      warehousing
      waste
      wealth
      wealth management
      wearable
      web
      wellness
      wind
      wind farm
      wireless
      work
      workflow
      workplace 


    ### Example of tag extraction:

      question 1: provide  toyota activities in 2024

      answer 1:
          {{'reasoning': 'The question specifically asks for activities related to Toyota in the year 2024', 'task': ['provide', ], 'date_period': 'in', 'date': ['2024'], 'company_names': ['Toyota'], 'industry_tags': [], 'activity_tags': ['activities'], 'context': [], 'display_tags': ['most_recent', 'most_relevant']}}



    """
    prompt = prompt.format(question1= question)
    # log(prompt)
    llm_1   = LLM(llm_service, llm_model, max_tokens=llm_max_tokens)
    try:
        llm_res = llm_1.get_save_sync(prompt=prompt, output_schema=questionNER, dirout=None)
    except Exception as e:
        log(e)
        return None     
    msg = llm_res["choices"][0]["message"]["content"]
    dd  = llm_cleanup_gpt_jsonformat(msg)
    log('\n###### msg_dict_raw: ', dd)


    #### Data Source  ########################################
    lsource = {'news': 'LZnews', 'industry':  'Eindustry'}
    ti = dd.get('data_source', 'industry')
    if 'activi' in ti:      ti = 'news'

    dd['data_source'] = lsource.get(ti, 'Eindustry')



    #### Post process date ###################################
    ll2 = []
    for ti in dd.get('date', ['2024']):
          ll2.append( ti.lower() )
    dd['date'] = ll2 


    #### Post process activity ###############################
    ll2 = []
    log(dd['activity_tags'] )
    for ti in dd.get('activity_tags', []):

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

    ll2 = list(set(ll2))  
    dd['activity_tags'] = ll2


    log("#### Industry ")
    # log(dd)
    ll2 = []
    for ti in dd.get('industry_tags', []):
       log(ti)
       ti = ti.replace("tech", " ").strip()
       #if ti.split(" ")[0] not in question:
       #    continue

       #if 'ev' in ti.lower():
       #   ll2.append('automobile') 

       ti2 = NER_industry_norm(ti)
       log(ti2)
       ll2.append(ti2)

    ll2 = list(set(ll2))   
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

    #### Post process task ###################################
    ll2 = []
    for ti in dd.get('task', ['summarize']):
       log(ti)
       ti2 = NER_task_norm(ti, dd)
       ll2.append(ti2)
       log(ti2)

    dd['task'] = ll2


    log("\n##### query_tags_dict:", dd) 
    return dd




###############################################################################################
def NER_task_norm(ti,dd:dict):
    ti2 = ti.lower()


    if len(dd.get('activity_tags', [])) < 1 and len(dd.get('company_names', [])) >= 1 and len(dd.get('industry_tags', [])) < 1 :
        ti2 = 'describe_company'


    elif len(dd.get('activity_tags', [])) < 1 and len(dd.get('company_names', [])) < 1 and  len(dd.get('industry_tags', [])) >= 1  :
        ti2 = 'describe_industry'

    elif len(dd.get('industry_tags', [])) >= 1 and len(dd.get('company_names', [])) >= 1:
        pass 

    else:
        ti2 = ti2.replace('write report',  'report')  
        ti2 = ti2.replace('what are', 'summarize')
        ti2 = ti2.replace('find company', 'describe company')
        ti2 = ti2.replace("provide", "describe")

    return ti2



def NER_activity_norm(ti):
    ll = """partnership
    funding
    m and a
    industry news
    new product
    product
    service launch
    earnings
    listing
    expansion
    management
    approval
    regulation
    """
    ll =  [  xi.strip() for xi in    ll.split("\n") ]
    ti2 = ti.lower()
    ti2 = ti2.replace('investment',  'funding')  
    ti2 = ti2.replace('investments', 'funding') 

    tlist = str_fuzzy_match_list(ti2, ll, cutoff=70.0)   
    if len(tlist) < 1:
       return ""
    return ti2



def NER_industry_norm(ti):
    ti2 = ti.lower()
    ti2 = ti2.replace('artificial intelligence', 'ai')
    ti2 = ti2.replace('technology', 'tech')
    ti2 = ti2.replace('genai', 'generative ai')   
    ti2 = ti2.replace('healthcare', 'health')   
    # ti2 = ti2.replace('automobile', 'auto')    
    return ti2



def qdrant_query_createfilter_custom(query_tags: dict):
    """
      query_tags ---> Map to Qdrant categories field

         Qdrant columns:
              L_cat = L1_cat + L2_cat + L3_cat + L4_cat
              "['L0_catnews', 'com_extract',   'Lcat, 'text_id', 'title']"

        query_filter=Filter(
            should=[FieldCondition(key="category", match=MatchValue(value="electronics")), FieldCondition(key="brand", match=MatchValue(value="apple")) ]

        query_filter=models.Filter(
            must=[
                models.FieldCondition(key="category", match=models.MatchText(text="elec") ) ]
 
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


        Qdrant only word token match in qdrant  Not string match

      activty=  "partnership  collaboration"         --->  'partner'  : partial  won't match !!!!!!

    """
    from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchText

    must = []
    for key, valist in query_tags.items():
      if key == "company_names":
           for val in valist:
               must.append(FieldCondition(key="com_extract", match=MatchText(text=val)))

    should = []
    for key, valist in query_tags.items():

        if key == "date":
            for val in valist:
                should.append(FieldCondition(key="date", match=MatchText(text=val)))

        if key == "industry_tags":
            for val in valist:  #### concatenated
                should.append(FieldCondition(key="L_cat", match=MatchText(text=val)))

        if key == "activity_tags":  ### acquisition
            for val in valist:
                should.append(FieldCondition(key="L0_catnews", match=MatchText(text=val)))

        # if key == "context":
        #     for val in valist:
        #         should.append(FieldCondition(key="info", match=MatchText(text=val)))

    query_filter = Filter(must=must, should=should)
    log2(query_filter)    
    return query_filter




#############################################################################################
#############################################################################################
def test_question_ner_extraction(llm_service="openai", llm_model="gpt-4o-mini"):
    """  80% of use cases,     remaining 20% --> fine tune the LLM OpenAI.

    --> query_tags ={

        tasks : ['Summarize']
            companies_name : ['Microsoft'],
            industry_tags:   ['Generative AI', "Cloud" ],
            date_period:     ['2024'],
            context :  ['acquisition'], #### All others

       Goal :  Fine tune the Question NER extraction.

       CSV file  (manually) OR


       A) generate manually: tricky question
             Questions, json_ouput

              Provide some comparisons and summarize the acquisitions of Palo Alto and Meta world
              in Cloud medical computing and military health field this year,
              for companies in America, but not in Canada ?

             {
                  "task": [ "compare", "summarize" ]
                  "date": ['this year']
                  "date_period" : ['in' ]
                  "industry_tags": ['Cloud medical computing", "military health" ]
                  "company_names": ["Palto Alto", "Meta world"],
                    "relation_tags": ["acquisition"],
                  "context": ["companies in America",  "not in canada" ]
            }




       B)
           Generate the dataset:
              Input promppt:  Use this json as input and create question of this json
              output:  question.
             ---> Dataset:

    """

    test_queries = [

        ["Summarize acquisitions done by Microsoft in Generative AI/Cloud in 2024",
         {"date_period": "after",
          "company_names": ["Microsoft"],
          "date": "2024"}],

        ["Describe in detail the stock exchange performance of Google since 2000?",
         {"company_names": ["Google"], "date_period": "after",
          "date": "2000"
          }
         ],

        ["When did Microsoft acquire Github?",
         {"company_names": ["Microsoft", "Github"],
          "relation_tags": ["acquire"], "date": ""}
         ],


        ["Describe the stock exchange performance of Intel and NVIDIA between 2000 and 2020?",
         {"company_names": ["Intel", "NVIDIA"],
          "date_period": "between",
          "date": "2000-2020"}
         ],

        [ "Summarize recent developments in social media platforms like facebook, twitter and reddit between 2000 and 2020?",

            {"task": ["summarize"],
             "date_period": "between",
             "company_names": ["facebook", "twitter", "reddit"],
             "date": "2000-2020"}
        ]
    ]

    for test_query in test_queries:
        q = test_query[0]
        expected = test_query[1]
        query_tags_dict = llm_question_extract_NER(question=q, llm_service=llm_service,
                                                   llm_model=llm_model, llm_max_tokens=1000)
        # print(query_tags_dict)
        for k, v in expected.items():
            assert query_tags_dict[k] == v


def eval_question_ner_extraction():
    """
    # run following commands to generate questions from text
    # then run the function
    # generate triplets from text
    python3 -u rag/engine_kg.py kg_triplets_extract_v2 --dirin "./ztmp/df_LZ_merge_90k_tmp.parquet" --dirout "./ztmp/df_LZ_merge_90k_tmp_relations.parquet" --istart 0 --nrows 25
    # generate questions from triplets
    python3 -u rag/engine_kg.py kg_generate_questions_from_triplets --dirin "./ztmp/df_LZ_merge_90k_tmp_relations_0_0_25.parquet" --dirout "./ztmp/df_LZ_merge_90k_tmp_questions_0_0_25.parquet"
    """
    import os
    from utilmy import pd_read_file
    from rag.llm import LLM
    # from rag_summ import llm_question_extract_NER
    from pydantic import BaseModel

    df = pd_read_file("../ztmp/df_LZ_merge_90k_tmp_questions_0_0_25.parquet")
    llm1 = LLM('openai', 'gpt-4o', api_key=os.environ['OPENAI_API_KEY'])

    for i, row in df.iterrows():
        print(row.question)
        json_output = llm_question_extract_NER(question=row.question)
        print(json_output)
        print("=" * 20)



def eval_summary_rag():
    """
        # generate triplets from text
        python3 -u rag/engine_kg.py kg_triplets_extract_v2 --dirin "./ztmp/df_LZ_merge_90k_tmp.parquet" --dirout "./ztmp/df_LZ_merge_90k_tmp_relations.parquet" --istart 0 --nrows 25


        # generate questions from triplets
        python3 -u rag/engine_kg.py kg_generate_questions_from_triplets --dirin "./ztmp/df_LZ_merge_90k_tmp_relations_0_0_25.parquet" --dirout "./ztmp/df_LZ_merge_90k_tmp_questions_0_0_25.parquet"


    """






#############################################################################################################
############ Fine Tune ######################################################################################
def json_records_save(records, dirout="ztmp/gpt_train/mydata.jsonl"):
    import json
    with open(dirout, "w") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")
    log(dirout)


def llm_finetune_create_json(dirin, question_col="question", label_col="label", dirout="ztmp/gpt_train",
                             create_prompt_func=None,
                             ):
    """
    Takes prompt, answer pairs and prepare openai compatible format for finetuning.


    python3 -u rag/rag_summ.py llm_finetune_create_json --dirin "ztmp/test_queries.json" --question_col "question" --label_col "answer"


    """
    log('###### Load data      #################################')
    df = pd_read_file(dirin)
    log(df[[ question_col, label_col  ]])


    log('###### Create JSON Samples ###########################')
    from rag.llm import prompt_fun_addprefix_jsonformat


    create_prompt = create_prompt_func
    if create_prompt is None:
            def create_prompt(question1):
                class questionNER(BaseModel):
                    ### Trick to improve accuracy.
                    reasoning: str   = Field(description=" Summarize in 2 sentences your reasoning on this entity extraction.")
                    task: list       = Field(description="predefined tasks like \"compare\", \"summarize\", \"unknown\"    )")
                    date_period: str = Field(description="before/between/after/in")
                    date: list       = Field(description="Dates year information in the text")
                    company_names: list = Field(description="Names of the corporate entities")
                    industry_tags: list = Field(description="tags related to company or business industries")
                    activity_tags: list = Field(description="company activity or actions mentioned in the text")
                    context: list = Field(description="keywords that didnt get categorized anywhere else")

                schema_json  = prompt_fun_addprefix_jsonformat(questionNER)
                final_prompt = f"{question1}\nRespond with the following JSON schema: \n{schema_json}"
                return final_prompt

    df['prompt']  = df[question_col].apply(lambda x: create_prompt(x))


    def create_data_example(x):
        # ensure that all columns are strings
        #if not isinstance(x[question_col], str):
        #    x[question_col] = str(x[question_col])

        if isinstance(x[label_col], dict):
            x[label_col] = json.dumps(x[label_col])

        return {"messages": [{"role": "user", "content":      str(x['prompt']) },
                             {"role": "assistant", "content": x[label_col]}]}

    df["example"] = df.apply(lambda x: create_data_example(x), axis=1)



    log('###### Save JSON Samples ###########################')
    # df.rename(columns={label_col:"label"}, inplace=True)
    ts = date_now(fmt= "%Y%m%d_%H%m%d")
    pd_to_file(df, dirout + f"/df_finetune_debug_{ts}.parquet")


    djson   = df["example"].to_list()
    dirout2 = dirout + "/data_finetune.jsonl"
    json_records_save(djson, dirout2)
    return dirout2




def llm_finetune_train(dirin="ztmp/gpt_train/mydata.jsonl",
                 dirout="ztmp/gpt_train", modelid="gpt-4o-mini-2024-07-18"):
    """
            5 rows csv with \t  tab separated
            Usage: python3 -u rag/rag_summ.py llm_finetune_train --dirin "ztmp/gpt_train/data_finetune.jsonl" --dirout "ztmp/gpt_train"
    """
    import openai
    from utilmy import date_now

    openai.api_key = os.environ["OPENAI_KEY"]

    log("######## Upload training file")
    client = openai.OpenAI()
    file_response = client.files.create(
        file=open(dirin, "rb"), purpose="fine-tune")
    training_file_id = file_response.id


    log("####### create the training job ###################")
    response = client.fine_tuning.jobs.create(training_file=training_file_id, model=modelid )

    res = response.to_dict()
    log(res)
    ts = date_now(fmt="%Y%m%d_%H%M%S", returnval="str")
    json_save(res, dirout + f"/finetune_{ts}.json")
    return res

    # # Use the fine-tuned model
    # completion = openai.Completion.create(
    #     model=response.fine_tuned_model,
    #     prompt="Your prompt here"
    # )
    # print(completion.choices[0].text)


def llm_finetune_check(ft_model_id="ft:gpt-4o-mini-2024-07-18:personal::A31CIqSJ", max_tokens=1000, service="openai",
                       question_answer_list=None, output_schema=None,
                       ):
    """
    Takes finetuned model id and returns answer

    Usage: python3 -u rag/rag_summ.py llm_finetune_check --ft_model_id "ft:gpt-4o-mini-2024-07-18:personal::A31CIqSJ"
    Output:
        openai ft:gpt-4o-mini-2024-07-18:personal::A31CIqSJ <openai.OpenAI object at 0x7236f7160450>
        HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
        llm_response:{
            'reasoning': 'The request asks for a comparison and summary of the acquisitions by Meta group and Microsoft in the Cloud medical computing and military health fields, specifically focusing on the date of the event which is this year. Additionally, it specifies that the companies should be in America and not in Canada.',
            'task': ['compare', 'summarize'], 'date_period': 'in', 'date': ['this year'],
            'company_names': ['Microsoft', 'Meta group'], 'industry_tags': ['Cloud medical computing', 'military health'],
            'activity_tags': ['acquisition'], 'context': ['companies in America', 'not in canada']}
    """

    for question, answer in question_answer_list:
        llm    = LLM(service, ft_model_id, max_tokens=max_tokens)
        result = llm.get_save_sync(question, output_schema= output_schema, dirout=None, )
        try:
            llm_response = json.loads(result['choices'][0]['message']['content'])
            print(f"llm_response:{llm_response}")
        except Exception as e:
            llm_response = {}

        log(question)
        log(llm_response)
        log(answer)









def llm_finetune_check_custom(ft_model_id="ft:gpt-4o-mini-2024-07-18:personal::A31CIqSJ", max_tokens=1000, service="openai"):
    """
    Takes finetuned model id and returns answer

    Usage: python3 -u rag/rag_summ.py llm_finetune_check --ft_model_id "ft:gpt-4o-mini-2024-07-18:personal::A31CIqSJ"
    Output:
        openai ft:gpt-4o-mini-2024-07-18:personal::A31CIqSJ <openai.OpenAI object at 0x7236f7160450>
        HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
        llm_response:{
            'reasoning': 'The request asks for a comparison and summary of the acquisitions by Meta group and Microsoft in the Cloud medical computing and military health fields, specifically focusing on the date of the event which is this year. Additionally, it specifies that the companies should be in America and not in Canada.',
            'task': ['compare', 'summarize'], 'date_period': 'in', 'date': ['this year'],
            'company_names': ['Microsoft', 'Meta group'], 'industry_tags': ['Cloud medical computing', 'military health'],
            'activity_tags': ['acquisition'], 'context': ['companies in America', 'not in canada']}
    """
    question_list = [(
        "Provide some comparisons and summarize the acquisitions by Meta group and Microsoft in Cloud medical computing and military health field this year, for companies in America, but not in Canada.",
        {
            'company_names': ['Microsoft', 'Meta group'],
            'industry_tags': ['Cloud medical computing', 'military health'],
            'activity_tags': ['acquisition'],
            'context':       ['companies in America', 'not in canada']}
    )]

    class questionNER(BaseModel):
        ### Trick to improve accuracy.
        reasoning: str = Field(description=" Summarize in 2 sentences your reasoning on this entity extraction.")
        task: list = Field(description="predefined tasks like \"compare\", \"summarize\", \"unknown\"    )")
        date_period: str = Field(description="before/between/after/in")
        date: list = Field(description="Dates year information in the text")
        company_names: list = Field(description="Names of the corporate entities")
        industry_tags: list = Field(description="tags related to company or business industries")
        activity_tags: list = Field(description="company activity or actions mentioned in the text")
        context: list = Field(description="keywords that didnt get categorized anywhere else")


    llm_finetune_check(ft_model_id="ft:gpt-4o-mini-2024-07-18:personal::A31CIqSJ", max_tokens=1000, service="openai",
                       question_answer_list=question_list, output_schema= questionNER,
                       )




def llm_finetune_create_dummy_train_samples():
    """
    Creates dummy training examples for finetuning
    """
    import pandas as pd
    test_queries = [

        ["Summarize acquisitions done by Microsoft in Generative AI/Cloud in 2024",
         {"date_period": "after",
          "company_names": ["Microsoft"],
          "date": "2024"}],

        ["Describe in detail the stock exchange performance of Google since 2000?",
         {"company_names": ["Google"], "date_period": "after",
          "date": "2000"
          }
         ],

        ["When did Microsoft acquire Github?",
         {"company_names": ["Microsoft", "Github"],
          "relation_tags": ["acquire"], "date": ""}
         ],

        ["Describe the stock exchange performance of Intel and NVIDIA between 2000 and 2020?",
         {"company_names": ["Intel", "NVIDIA"],
          "date_period": "between",
          "date": "2000-2020"}
         ],

        [
            "Summarize recent developments in social media platforms like facebook, twitter and reddit between 2000 and 2020?",

            {"task": ["summarize"],
             "date_period": "between",
             "company_names": ["facebook", "twitter", "reddit"],
             "date": "2000-2020"}
        ],
        [
            "Provide some comparisons and summarize the acquisitions by Meta group and Microsoft in Cloud medical computing and military health field this year, for companies in America, but not in Canada.",
            {
                "task": ["compare", "summarize"],
                "date": ['this year'],
                "date_period": ['in'],
                "industry_tags": ["Cloud medical computing", "military health"],
                "company_names": ["Microsoft", "Meta group"],
                "relation_tags": ["acquisition"],
                "context": ["companies in America", "not in canada"]
            }
        ]
    ]

    df = pd.DataFrame(test_queries * 2, columns=["question", "answer"])
    pd_to_file(df, "../ztmp/test_queries.json")





#############################################################################################################
if __name__ == '__main__':
    import fire
    fire.Fire()










def search_summarize_with_citation2(cfg=None, cfg_name="test", query: str = "", engine="sparse",
                                   server_url: str = "http://localhost:6333",
                                   # sparse_collection_name: str = "LZnews",

                                   table_name_sql="LZnews",
                                   db_path_sql="./ztmp/db/db_sqlite",

                                   llm_prompt_id="summarize_01",
                                   topk: int = 10,  


                                   qdrant_topk = 1000,
                                   qdrant_score_min = 20.0,

                                   llm_service: str = "openai", 
                                   llm_model: str = "gpt-4o-mini",
                                   llm_max_tokens: int = 16000, istest=1,
                                   dirout="./ztmp/chat_log/"

                                   ):
    """Search and summarize text based on the given query using a sparse model and LLM.

       export OPENAI_KEY=""
       alias pysum="python3 -u rag/rag_summ.py "

       modelid="gpt-4o-2024-08-06"
       pysum search_summarize_with_citation --query "What are the microsoft partnerships in 2024 ?"  --llm_model $modelid --topk 20


       pysum search_summarize_with_citation --query "What are the activities in generative ai  in 2024 ?"  --llm_model $modelid --topk 10


       pysum search_summarize_with_citation --query "What are Mistral partnerships in 2023 ?"  --llm_model $modelid --topk 10


       pysum search_summarize_with_citation --query "What are  the acquisitions of microsoft in generative ai  ?"  --llm_model $modelid --topk 10



       pysum search_summarize_with_citation --query "What are the microsoft partnerships in generative ai in 2024 ?"  --llm_model $modelid --topk 5


       pysum search_summarize_with_citation --query "What are the microsoft partnerships in generative ai in 2024 ? show the most relevant at first"  --llm_model $modelid --topk 5


       pysum search_summarize_with_citation --query "What are the partnerships between Amazon and  Microsoft in generative ai in 2024 ? show the most relevant at first"  --llm_model $modelid --topk 5

       source ../../../scripts/bins/env.sh


    """
    log("\n######### New query #########################################################")
    log(query)
    global sparse_model
    llg = Box({'query_id': date_now(fmt="%Y%m%d_%H%M%S") + "-" + str(int(random.uniform(1000,9999)))  })
    llg.input_query_user = query


    if "gpt mode" in query or "open mode" in query:
        llm_1      = LLM(llm_service, llm_model, max_tokens=llm_max_tokens)
        llg.prompt = query
        query2 = query.replace("open mode.", "").replace("open mode", "")
        query2 = query.replace("gpt mode.", "").replace("gpt mode", "")        
        llm_json = llm_1.get_save_sync(prompt=query2, output_schema=None, dirout=None)        
        msg      = llm_json["choices"][0]["message"]["content"]
        llg.msg_answer = msg
        json_save2(llg, dirout)
        return msg    


    log("######## Extract tags from question    ################## ")
    llg.query_tags = llm_question_extract_NER(question=query, llm_service=llm_service,
                                              llm_model="gpt-4o-mini", llm_max_tokens=1000)

    msg = summary_question_error_handle(query, llg.query_tags)
    if msg is not None:
       log(msg); return msg 

    llg.query2 = summary_question_rewrite(query, llg.query_tags)

    llg.sparse_collection_name = llg.query_tags['data_source']
    llg.table_name_sql         = llg.query_tags['data_source']
    #llg.db_path_sql            = f"{db_path_sql}/{llg.table_name_sql}.db" 
    llg.db_path_sql            = f"./ztmp/db/db_sqlite/datasets.db" 

    log('db:', llg.db_path_sql, llg.sparse_collection_name )
    ### llg.query_tags = summary_tags_expansion(query, llg.query_tags)


    log("######## Fusion search   ############################# ")
    query_filter = qdrant_query_createfilter_custom(llg.query_tags)
    client       = QdrantClient(server_url)
    if sparse_model is None:
        sparse_model = EmbeddingModelSparse()


    results = fusion_search(query= llg.query2, engine=engine, client=client,
                                  sparse_collection_name= llg.sparse_collection_name,
                                  neo4j_db="neo4j", sparse_model=sparse_model,
                                  query_tags=None, query_filter= query_filter,
                                  topk= qdrant_topk
                            )

    llg.results  = [{"text_id": text_id, "score": score} for text_id, score in results.items()]
    log2('Retrieved all:', len(llg.results))
    if len(llg.results)< 1:
       msg = 'Empty results'
       json_save2(llg, dirout)
       log2(msg); return msg 
    

    log('Retrie Filter: ', len(llg.results))
    if len(llg.results)< 1:
       msg = 'Empty results'
       json_save2(llg, dirout)
       log2(msg); return msg 


    log("\n####### Fetch actual text from SQL DB ################################# ")
    #### match date pattern here
    text_ids = [res["text_id"] for res in llg.results ]
    cols     = ['text_id', 'url', 'date', 'title', 'text', 'score', 'L0_catnews', 'L_cat' ]
    dftxt = dbsql_fetch_text_by_doc_ids(db_path= llg.db_path_sql,
                                            table_name= llg.table_name_sql,
                                            cols=cols,
                                            text_ids=text_ids)
    dftxt = pd.DataFrame(dftxt)
    log('Doc retrieved:', dftxt, dftxt.shape)


    log("#### Doc Keyword filtering ##############################")
    def str_docontain(w, x):
        x2 = str(x).lower()
        for wi in w.split(" "):
            if wi not in x2 : return False 
        return True

    for w in llg.query_tags['activity_tags']:
       dftxt = dftxt[ dftxt['L0_catnews'].apply(lambda x :  str_docontain(w, x)) ] 
       log(w, dftxt.shape)

    for w in llg.query_tags['industry_tags']:
       dftxt = dftxt[ dftxt['L_cat'].apply(lambda x :       str_docontain(w, x)) ] 
       log(w, dftxt.shape)

    for w in llg.query_tags['date']:
       dftxt = dftxt[ dftxt['date'].apply(lambda x :        str_docontain(w, x)) ] 
       log(w, dftxt.shape)

    if len(dftxt) < 1:
        log("empty")
        return " No answers, please enlarge the scope of your question"


    log("#### Doc Re-Ranking ######################################")
    ### Re rank based on doc individual relevance
    """
    
    
    """
    dfqd = pd.DataFrame(llg.results)
    dfqd.columns =['text_id', 'score_qd']
    dftxt    = dftxt.merge(dfqd, on=['text_id'], how='left')
    

    t0 = date_now(returnval='unix')
    def rerank_score(x):
      return float(x['score']) * x['score_qd']

    dftxt['score2'] = dftxt.apply(lambda x: rerank_score(x), axis=1  )
    dftxt = dftxt.sort_values(['score2'], ascending=[0])

    # if len(llg.results)> 80:
    #     lscores = np.array([ x['score'] for x in llg.results  ])
    #     q25 = np.quantile(lscores, 0.25)
    #     llg.results =  [ x for x in llg.results if x['score'] > q25 ]  



    log("\n####### Dsiplay ranking ############################################## ")
    dftxt = summary_display_ranking(dftxt, llg.query_tags)


    log("\n####### Format Docs prompt ########################################### ")
    topk = min(10, topk)
    multi_dftxt = []
    for ii, doc in dftxt.iloc[:topk,:].iterrows() :
        url   = doc['url']
        title = doc['title']
        text  = doc['text']
        date  = doc['date']

        txt = f""" title: {title}\ndate:{date}url:{url}\ntext:{text}"""
        multi_dftxt.append(txt)

    multi_doc_str = "\n---\n".join(multi_dftxt)
    log('Doc appended:', ii+1)
    log('Full doc size: ', len(multi_doc_str), 'chars, ', len(multi_doc_str.split(" ")), ' words') 


    log("\n#######  LLM :Summarize #############################################")
    llm_1 = LLM(llm_service, llm_model, max_tokens=llm_max_tokens)
    ptext = promptlist[llm_prompt_id]
    ptext = ptext.replace("<question>", query)
    ptext = ptext.replace("<multi_doc_string>", multi_doc_str)
    llg.prompt = ptext

    llm_json = llm_1.get_save_sync(prompt=ptext, output_schema=None, dirout=None)
    msg      = llm_json["choices"][0]["message"]["content"]
    llg.msg_answer = msg

    msg2 = answer_format(msg)
    llg.msg_display = msg2

    ##### Clean ip
    json_save2(llg, dirout)
    return msg2



"""
### logs

    (py39r) \W$                                                                                        
    (py39r) \W$        pysum search_summarize_with_citation --query "What are the microsoft partnerships in generative ai in 2024 ?"  --llm_model $modelid --topk 5                                       

    ######## Extract tags from question    ################################### 
    openai gpt-4o-2024-08-06 <openai.OpenAI object at 0x1062bc310>
    HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    query_tags_dict: {'reasoning': "The text is asking about Microsoft's partnerships in the field of generative AI for the year 2024. It seeks information on specific collaborations or alliances that Microsoft may have formed in this area during that time.", 'task': ['summarize'], 'date_period': 'in', 'date': ['2024'], 'company_names': ['microsoft'], 'industry_tags': ['generative AI'], 'activity_tags': ['partner'], 'context': ['What', 'the', 'in'], 'display_tags': ['most_recent']}

    question rewrite:    the microsoft partnerships in generative ai in 2024  


    ######## Get results from fusion search   ############################### 
    should=[FieldCondition(key='date', match=MatchText(text='2024'), range=None, geo_bounding_box=None, geo_radius=None, geo_polygon=None, values_count=None), FieldCondition(key='L_cat', match=MatchText(text='generative AI'), range=None, geo_bounding_box=None, geo_radius=None, geo_polygon=None, values_count=None), FieldCondition(key='L0_catnews', match=MatchText(text='partner'), range=None, geo_bounding_box=None, geo_radius=None, geo_polygon=None, values_count=None)] min_should=None must=[FieldCondition(key='com_extract', match=MatchText(text='microsoft'), range=None, geo_bounding_box=None, geo_radius=None, geo_polygon=None, values_count=None)] must_not=None
    engines ['sparse']
    Using: sparse
    HTTP Request: POST http://localhost:6333/collections/LZnews/points/search "HTTP/1.1 200 OK"
    HTTP Request: POST http://localhost:6333/collections/LZnews/points/search "HTTP/1.1 200 OK"
    Retrieved all: 203

    Retrie Filter:  40    score > 25.0


    ####### Fetch actual text from SQL DB ################################# 
    SELECT text_id,url,date,title,text,score FROM LZnews WHERE text_id IN ('5777941435270968929', '9640924470771532287', '17577508699724508634', '1143658958290503235', '15079138884218292406', '13965052015877913548', '15657751878160493932', '10587001136211832533', '16109192610270594760', '575991153852634094', '12710501389387547957', '11057191840449583931', '1633154844307977104', '16651598197672198632', '7148422744404787840', '17721541317404051942', '7097324763635429462', '5836433310886898158', '16354695118152391196', '12247300828686850578', '10824889868967783099', '18018609611627989259', '2355647363399832315', '3789968352458346440', '1164003485633814506', '4789972660336247866', '15271843213204319879', '7682472335429925575', '3691496458224753266', '7529330476215893540', '13697261117193152068', '6870481525068342337', '6776302579204205550', '15723358398459734476', '5299980654201715206', '8061925757068798302', '11992315908033369171', '17421437417548529490', '11430840246448740615', '3031388281568985934')
    Doc retrieved:                  text_id  ... score
    0    5777941435270968929  ...   1.0
    1    9640924470771532287  ...   1.0
    2   17577508699724508634  ...   1.0
    3    1143658958290503235  ...   1.0
    4   15079138884218292406  ...   1.0
    5   13965052015877913548  ...   1.0
    6   15657751878160493932  ...   1.0
    7   10587001136211832533  ...   1.0
    8   16109192610270594760  ...   1.0
    9     575991153852634094  ...   1.0
    10  12710501389387547957  ...   1.0
    11  11057191840449583931  ...   1.0
    12   1633154844307977104  ...   1.0
    13  16651598197672198632  ...   1.0
    14   7148422744404787840  ...   1.0
    15  17721541317404051942  ...   1.0
    16   7097324763635429462  ...   1.0
    17   5836433310886898158  ...   1.0
    18  16354695118152391196  ...   1.0
    19  12247300828686850578  ...   1.0
    20  10824889868967783099  ...   1.0
    21  18018609611627989259  ...   1.0
    22   2355647363399832315  ...   1.0
    23   3789968352458346440  ...   1.0
    24   1164003485633814506  ...   1.0
    25   4789972660336247866  ...   1.0
    26  15271843213204319879  ...   1.0
    27   7682472335429925575  ...   1.0
    28   3691496458224753266  ...   1.0
    29   7529330476215893540  ...   1.0
    30  13697261117193152068  ...   1.0
    31   6870481525068342337  ...   1.0
    32   6776302579204205550  ...   1.0
    33  15723358398459734476  ...   1.0
    34   5299980654201715206  ...   1.0
    35   8061925757068798302  ...   1.0
    36  11992315908033369171  ...   1.0
    37  17421437417548529490  ...   1.0
    38  11430840246448740615  ...   1.0
    39   3031388281568985934  ...   1.0

    [40 rows x 6 columns] (40, 6)

    ####### Dsiplay ranking ########################################### 
    Display results: most_recent or by most_relevant (same in google search)
    

    ####### Format Docs prompt ########################################### 
    Doc appended: 4
    Full doc size:  17109 chars,  2302  words


    #######  LLM :Summarize #############################################
    openai gpt-4o-2024-08-06 <openai.OpenAI object at 0x3ad12d760>
    HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    ./ztmp/chat_log//year=2024/month=09/day=08/hour=22/chat_240908_22041725800671.json

    **Overall Summary:**
    In 2024, Microsoft has formed several strategic partnerships in the generative AI space, focusing o
    n diverse sectors such as process automation, renewable energy, fintech, and operational efficiency
    . Datamatics collaborates with Microsoft to develop copilot solutions for business transformation, 
    while Pivot Energy partners with Microsoft to create community-scale solar projects. Microsoft and 
    dLocal aim to enhance fintech solutions in emerging markets, and Danone teams up with Microsoft to 
    integrate AI across its operations. Additionally, Microsoft's partnership with Inflection AI is und
    er scrutiny by the UK antitrust watchdog.

    **Article Details:**

    1. **Title:** Datamatics partners with Microsoft to Build AI Solutions through Copilots
       - **Date:** 2024-08-27
       - **URL:** [Datamatics Partners with Microsoft](https://www.datamatics.com/press-release-list/da
    tamatics-partners-with-microsoft)
       - **Summary:** Datamatics has partnered with Microsoft to develop copilot solutions for process 
    automation, enhancing business transformation. The collaboration includes a Partner On-boarding Cop
    ilot on Microsoft Teams, integrating Azure OpenAI with Datamatics' platform. Datamatics is recogniz
    ed as a top ISV partner and part of Microsoft's "AI First Movers" series. The partnership aims to p
    rovide customized AI solutions for organizations.

    2. **Title:** Pivot Energy Collaborates with Microsoft to Develop Up to 500 MWac of Community-Scale
     Solar Projects
       - **Date:** 2024-08-08
       - **URL:** [Pivot Energy Collaborates with Microsoft](https://www.prnewswire.com/news-releases/p
    ivot-energy-collaborates-with-microsoft-to-develop-up-to-500-mwac-of-community-scale-solar-projects
    -that-will-deliver-significant-benefits-to-local-communities-302217093.html)
       - **Summary:** Pivot Energy and Microsoft have entered a 5-year agreement to develop 500 MWac of
     community-scale solar projects in the U.S. This collaboration supports Microsoft's goal to reduce 
    Scope 3 emissions and Pivot's largest REC agreement. The projects will benefit local communities th
    rough diverse subcontractor partnerships and energy savings for low-income subscribers.

    3. **Title:** Microsoft and dLocal Forge Strategic Partnership to Harness Artificial Intelligence i
    n Fintech in Uruguay
       - **Date:** 2024-08-06
       - **URL:** [Microsoft and dLocal Partnership](https://ffnews.com/newsarticle/fintech/microsoft-a
    nd-dlocal-forge-strategic-partnership-to-harness-artificial-intelligence-in-fintech-in-uruguay/)
       - **Summary:** Microsoft and dLocal have partnered to integrate AI solutions into the fintech se
    ctor, enhancing financial inclusion in emerging markets. The collaboration aims to provide efficien
    t payment solutions and drive digital transformation. The partnership has expanded Microsoft's cust
    omer involvement in several emerging economies since 2018.

    4. **Title:** Danone and Microsoft Partner to Drive AI Transformation Across Operations
       - **Date:** 2024-07-24
       - **URL:** [Danone and Microsoft Partnership](https://dairynews.today/global/news/danone-and-mic
    rosoft-partner-to-drive-ai-transformation-across-operations.html)
       - **Summary:** Danone and Microsoft have announced a multi-year partnership to integrate AI solu
    tions across Danone's operations. The focus is on creating an AI-enabled supply chain and launching
     the Danone Microsoft AI Academy to upskill employees. The partnership aims to enhance operational 
    efficiency and data-driven decision-making.

    5. **Title:** UK antitrust watchdog launches probe into Microsoft’s Inflection AI partnership
       - **Date:** 2024-07-16
       - **URL:** [UK Antitrust Probe](https://siliconangle.com/2024/07/16/uk-antitrust-watchdog-launch
    es-probe-microsofts-inflection-ai-partnership/)
       - **Summary:** The UK's Competition and Markets Authority is reviewing Microsoft's partnership w
    ith Inflection AI, focusing on workforce hiring and licensing agreements. The probe aims to determi
    ne if the partnership reduces market competition. Microsoft maintains that the hiring promotes comp
    etition and is cooperating with the investigation.











"""
