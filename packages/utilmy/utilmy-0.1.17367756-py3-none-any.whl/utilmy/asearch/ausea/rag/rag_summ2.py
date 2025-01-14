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
if "######## import":
    import sys, json, os, warnings, random, string
    warnings.filterwarnings("ignore")
    import pandas as pd, numpy as np
    from pydantic import BaseModel, Field
    from typing import List, Dict, Union, Tuple
    from copy import deepcopy
    from functools import lru_cache

    from utilmy import log, log2, pd_read_file, pd_to_file, json_save, date_now
    from utilmy import diskcache_load, diskcache_decorator
    from utilmy import json_load

    from rag.engine_tv import fusion_search
    # from rag.engine_qd import QdrantClient
    # from rag.engine_sql import dbsql_fetch_text_by_doc_ids
    # from rag.engine_qd import EmbeddingModelSparse
    from rag.llm import LLM, llm_cleanup_gpt_jsonformat, promptRequest
    from utils.util_text import str_fuzzy_match_is_same, date_get




#########################################################################################
if '####### datafeed':
    from box import Box
    ccols = Box({})


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

global dfacti, dfcom, dfcom2, COM_DICT, dfragall, dirdb, dfinvest
dfacti, dfcom, dfcom2,dfragall = None, None, None, None
ddata = {}
COM_DICT = None

os.environ['istest'] = "0"




#########################################################################################
def test1(q="""  Recent Partnership of Microsoft     """):

    res = search_run(q, server_url="http://127.0.0.1:6333",
                                         engine="sparse",
                                         topk=10, llm_model="gpt-4o-mini", llm_max_tokens=1000)
    log(res)



@lru_cache(maxsize=None)
def jload_cache(dirin):
    dd= json_load(dirin)
    dd["question_list"] = []
    return dd



#########################################################################################
if "###### error message ################":
    msg_error0 = jload_cache("ui/static/answers/zfallback_error/data.json")


    msg_no_enough = deepcopy(msg_error0)
    msg_no_enough['html_tags']['summary'] = "No answers, please enlarge the scope of your question"


    msg_error = deepcopy(msg_error0)
    msg_error['html_tags']['summary'] = "No answers, Internal System issues"


    msg_too_many = deepcopy(msg_error0)
    msg_too_many['html_tags']['summary'] = "Our apologies. There are too many results related to this question. Please refine the question scope."
    log('msg loaded')



#########################################################################################
@lru_cache(maxsize=None)
def load_all_dataset(dname="com,indus,overview,insight,marketsize,industry_comlist,rag,invest"):
    global dfacti, dfcom, dfcom2, dfover, dfinsight, dfmarketsize, ddata, dfragall, dfinvest
    global COM_DICT

    global dirdb
    dirdb ="ztmp/db"
    if 'darwin' in str(sys.platform):
        dirdb = "ztmp/aiui/data/zlocal/db"
    log("Using dirdb", dirdb)


    if "com" in dname:
        dfcom   = pd_read_file(dirdb + "/db_sqlite/df_com_all.parquet")
        # ['L_cat', 'com_id', 'com_type', 'description', 'name', 'url']
        log("dfcom:", dfcom.shape, dfcom.columns)

        dfcom2 = pd_read_file(dirdb + "/db_sqlite/df_com_all_info.parquet")
        dfcom2 = dfcom2.fillna("")
        # ['com_id', 'country', 'description', 'founded_date', 'name', 'number_of_employees_min', 'total_funding_amount']
        log("dfcom2:",  dfcom2.shape,  dfcom2.columns)


        COM_DICT = { name.lower():idi for name, idi in zip(dfcom['name'], dfcom['com_id']) }
        for name, idi in zip(dfcom2['name'], dfcom2['com_id']):
            COM_DICT[name.lower()] = idi

        ddata['com_disrup'] = pd_read_file(dirdb + "/db_sqlite/com_disrup.parquet")
        log("com_disrup:",  ddata['com_disrup'].shape,  ddata['com_disrup'].columns)

        ddata['com_incum'] = pd_read_file(dirdb + "/db_sqlite/com_incum.parquet")
        log("com_incum:",  ddata['com_incum'].shape,  ddata['com_incum'].columns)


    if "indus" in dname:
        colstxt = ['text_id', 'url', 'date', 'title', 'text', 'score', 'L0_catnews', 'L_cat', 'com_extract', 'L2_cat', 'L3_cat', 'L3_catid' ]
        dfacti  = pd_read_file(dirdb + "/db_sqlite/df_edge_industry_activity.parquet")
        dfacti = dfacti[colstxt]
        log("dfindus:",  dfacti.shape,  dfacti.columns)


    if "overview" in dname:
        cols2  = ['text_id', 'url', 'date', 'title', 'text',  'L_cat' ]
        dfover = pd_read_file(dirdb + "/db_sqlite/df_edge_industry_overview.parquet", cols=cols2)
        log("dfover:",  dfover.shape,  dfover.columns)


    if "insight" in dname:
        cols2  = ['text_id', 'url', 'date', 'title', 'text',  'L_cat' ]
        dfinsight = pd_read_file(dirdb + "/db_sqlite/df_edge_industry_insight.parquet", cols=cols2)
        log("dfinsight:",  dfinsight.shape,  dfinsight.columns)


    if "marketsize" in dname:
        # cols2 = ['text_id', 'url', 'date', 'title', 'text',  'L_cat' ]
        cols2     = [ 'text_id', 'url', 'date', 'title', 'text',  'L_cat',   'text_html',]
        dfmarketsize = pd_read_file(dirdb + "/db_sqlite/df_edge_industry_marketsize.parquet", cols=cols2)
        log("dfmarketsize:",  dfmarketsize.shape,  dfmarketsize.columns)


    if "industry_comlist" in dname:
        ddata['indus_comlist'] = pd_read_file(dirdb + "/db_sqlite/df_edge_industry_comlist.parquet")
        log("indus_comlist:", ddata['indus_comlist'].shape,  ddata['indus_comlist'].columns)


    if "rag" in dname:
        dfragall = pd_read_file(dirdb + "/db_sqlite/df_rag_all.parquet")
        log("dfragall", dfragall.shape,  dfragall.columns)


    if "invest" in dname:
        dfinvest = pd_read_file(dirdb + "/db_sqlite/edge_investment_activity.parquet")
        log("invest:", dfinvest.shape,  dfinvest.columns)


class Tasks:
  find_company      = "find_company"
  marketsize_industry   = "marketsize_industry"
  describe_industry     = "describe_industry"
  compare_activity      = "compare_activity"
  search_activity       = "search_activity"
  search_open           = "search_open"

  industry_company_list = "industry_company_list"
  full_company_list     = "full_company_list"

  invest_investorlist   = "invest_investorlist"
  invest_receiverlist   = "invest_receiverlist"
  com_industry_list     = "com_industrylist"



################### Main ############################################################
def search_run(cfg=None, cfg_name="test", query: str = "",
            dirout="./ztmp/chat_log/",
            topk=5,
            meta= None, ):
    """Search and summarize text based on the given query using a sparse model and LLM.

       export OPENAI_KEY=""
       alias pysum="python3 -u rag/rag_summ.py "

       modelid="gpt-4o-2024-08-06"
       pysum search_run --query "What are the microsoft partnerships in 2024 ?"  --llm_model $modelid --topk 20

       pysum search_run --query "What are the partnerships between Amazon and  Microsoft in generative ai in 2024 ? show the most relevant at first"  --llm_model $modelid --topk 5

       source ../../../scripts/bins/env.sh

      {'task': [], 'date_period': '', 'date': [], 'company_names': ['trade desk'], 
       'industry_tags': [], 'activity_tags': ['partnership'], 'context': [],
            'data_source': 'Eindustry'}


    """
    log("\n######### New query ###################################################")
    log(query)
    global sparse_model, dfcom
    llg = Box({'query_id': date_now(fmt="%Y%m%d_%H%M%S") + "-" + str(int(random.uniform(1000,9999)))  })
    llg.meta             = {} if meta is None else meta
    llg.query_input_user = query
    llg.dirout           = dirout
    llg.answer_type      = llg.meta.get("answer_type", "")

    llg.llm_service    = "openai"
    llg.llm_model      = "gpt-4o"
    llg.llm_max_tokens = 4000
    # llg.llm_service  = "gemini"
    # llg.llm_model    = 'gemini-2.0-flash-exp'   ### too casual
    # llg.llm_model    = 'gemini-exp-1206'   ### too much summary...


    #llg.query_llm_service  = "openai"
    #llg.query_llm_model    = "gpt-4o-mini"
    llg.query_llm_service  = "gemini"
    llg.query_llm_model    = 'gemini-2.0-flash-exp'


    prefix     = query.split("@@")[0]
    llg.query1 = query.split("@@")[-1]

    if "gpt" in prefix  or 'definition' in llg.query1 or llg.answer_type == "gpt": 
        llg.query2 = llg.query1
        msg_dict   = task_gpt_answer(llg)
        return msg_dict


    debug = False
    if "debug" in llg.query1:
        llg.query1 = llg.query1.replace("debug", "").replace("debug.", "")
        debug  = True

    llg.query2 = question_normalize(llg.query1)


    log("######## Extract tags from question    ############################### ")
    llg.query_tags = question_extract_NER(question=llg.query2, llm_service= llg.query_llm_service,
                                          llm_model=llg.query_llm_model, llm_max_tokens=1000)
    if llg.query_tags is None :
       return msg_no_enough
    llg.task   = llg.query_tags['task']
    log('## TASK:', llg.task)

    if os.environ.get('DEBUG_query', "") == "1":
        dd =  llg.query_tags
        dd['question'] = query
        return dd


    msg1 = question_error_handle(llg.query2, llg.query_tags)
    if msg1 is not None:
       log(msg1); return msg_no_enough

    llg.query2 = question_rewrite(llg.query2, llg.query_tags)
    load_all_dataset()
    # llg.task = ['extra']


    ####### Task ###########################################################
    if   Tasks.find_company      in llg.task :
        ddict = task_com_find(llg)
        return ddict


    #elif Tasks.describe_industry     in llg.task :
    #    ddict = task_indus_overview(llg)
    #    return ddict


    elif Tasks.marketsize_industry   in llg.task :
        pass
        #ddict = task_indus_marketsize(llg)
        #return ddict


    elif Tasks.compare_activity      in llg.task :
        if len(llg.query_tags['company_names']) >= 2 :
           ddict = task_compare_activity(llg, topk= topk)
           return ddict


    elif Tasks.industry_company_list in llg.task :
        ddict = task_indus_comlist(llg)
        return ddict


    elif Tasks.full_company_list     in llg.task :
        ddict = task_full_comlist(llg)
        return ddict


    elif Tasks.search_activity       in llg.task :
         ddict= task_search_activity(llg, topk=topk)
         return ddict


    elif Tasks.com_industry_list     in llg.task:
        ddict = task_com_indulist(llg, )
        return ddict


    elif Tasks.invest_investorlist   in llg.task :
         ddict= task_invest_investorlist(llg,)
         return ddict


    elif Tasks.invest_receiverlist   in llg.task :
         ddict= task_invest_receiverlist(llg,)
         return ddict




    log("####### Default case: open question #########################################")
    #ddict= task_search_activity(llg, topk=topk)
    ddict= task_search_ext(llg, topk=10)
 
    return ddict



######### Task Definition ###########################################################
def task_gpt_answer(llg):
    log("########task_gpt_answer ############################")
    try:
        dout = jload_cache("ui/static/answers/gpt_answer/data.json")
        log("loaded data.json")

        query          = llg.query2
        llm_service    = "openai"
        llm_model      = "gpt-4o-mini"
        llm_max_tokens = 16000
        istest = 1

        llm_1      = LLM(llm_service, llm_model, max_tokens=llm_max_tokens)
        llg.prompt = query
        query2   = query.replace("open mode.", "").replace("open mode", "")
        query2   = query.replace("gpt mode.", "").replace("gpt mode", "")
        llm_json = llm_1.get_save_sync(prompt=query2, output_schema=None, dirout=None)
        msg = llm_json["choices"][0]["message"]["content"]

        llg.msg_answer = msg

        dout['html_tags']['summary'] = msg

        json_save2(llg, llg.dirout)
        return dout
    except Exception as e:
        log(e)
    return msg_no_enough




if "######### Task Company  #########################################################":
    def task_com_find(llg)->Dict:
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
        dfkall  = pd_find_com(dfcom,  llg, )
        dfkall2 = pd_find_com(dfcom2, llg, )

        if len(dfkall)>0 and len(dfkall2)>0:
           dfkall = pd.concat((dfkall, dfkall2 ))

        elif len(dfkall2)>0:
            dfkall = dfkall2

        if len(dfkall) < 1:
              dout = task_search_ext(llg)
              return dout

        dfkall = dfkall.drop_duplicates(['name'], keep='first')

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


        ##### Clean up ######################
        llg.msg_answer  = dout
        json_save2(llg, llg.dirout)
        return dout



    def task_com_network(llg):
        """ Provide network view of

        """
        log("#### Doc Keyword filtering ###################################")
        # def str_docontain(w, x):
        #     x2 = str(x).lower()
        #     for wi in w.split(" "):
        #         if wi.lower() not in x2 : return False
        #     return True
        log("company_names: ", llg.query_tags['company_names'])
        for w in llg.query_tags['company_names']:
            dftxt = dftxt[dftxt['com_extract'].apply(lambda x: str_docontain(w, x))]
            log(w, dftxt.shape)
            log(dftxt)

        log("activity_tags: ", llg.query_tags['activity_tags'])
        for w in llg.query_tags['activity_tags']:
            dftxt = dftxt[dftxt['L0_catnews'].apply(lambda x: str_docontain(w, x))]
            log(w, dftxt.shape)
            # if len(dftxt) < 1: return msg_no_enough

        log("industry_tags: ", llg.query_tags['industry_tags'])
        for w in llg.query_tags['industry_tags']:
            dftxt = dftxt[dftxt['L_cat'].apply(lambda x: str_docontain(w, x))]
            log(w, dftxt.shape)
            # if len(dftxt) < 1: return msg_no_enough


    def com_getid(name):
        global COM_DICT
        return COM_DICT.get(str(name).lower(), -1)




if "######### Task Industry details #################################################":
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
        log("########## Start task_indus_overview  #####################")
        global dfacti, dfover, dfinsight

        #dout = jload_cache('ui/static/answers/indus_overview/data.json' )
        dout = jload_cache('ui/static/answers/indus_overview/data.json' )

        if len(llg.query_tags['industry_tags']) < 1:
            ddict = task_search_ext(llg, topk=10)
            return ddict

        log("##### Overview ###############################################")
        dfi = deepcopy(dfover)
        for w in llg.query_tags['industry_tags']:
           w1 = str(w).lower().strip()
           for wi in w1.split(" "):
              log(wi)
              dfi = dfi[ dfi['title'].apply(lambda x:  wi in str_norm(x).split(" ")   ) ]
              log(dfi, dfi.shape)
              if len(dfi)<1:
                  ddict = task_search_ext(llg, topk=10)
                  return ddict


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

        if len(dfi)<1:
            ddict = task_search_ext(llg, topk=10)
            return ddict

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


    def task_indus_marketsize(llg):
        """


        """
        log("########## Start task_indus_marketsize  #####################")
        global dfmarketsize
        dout = jload_cache('ui/static/answers/indus_marketsize/data.json' )

        log("##### Overview ###############################################")
        dfi = deepcopy(dfmarketsize)
        for w in llg.query_tags['industry_tags']:
           w1 = str(w).lower().strip()
           for wi in w1.split(" "):
              log(wi)
              dfi = dfi[ dfi['L_cat'].apply(lambda x:  wi in  str(x).lower().split(" ")  ) ]
              log(dfi, dfi.shape )

        log(dfi)
        if len(dfi)<1:
           dout = task_search_ext(llg)
           return dout

        dd = []
        txt= ""
        for k, x in dfi.iterrows():
           xout = {
              #'name':  x['title'],
              'title': x['title'],
              'url':   x['url'],
              'date':  x['date'],
              'text':  x['text'],
           }
           dd.append(xout)
           txt = txt + f""" \n *Title*: {x['title']}  \n *Text*: {x['text']}   """

        llg.llm_prompt_id ="summarize_simple"
        ptext = promptlist[ llg.llm_prompt_id]
        ptext = ptext.replace("<question>", llg.query2)
        ptext = ptext.replace("<context>",  txt)
        llg.prompt = ptext

        msg = fun_get_summary(llg, llg.prompt)
        dout['html_tags']["summary"] = markdown_to_html(msg)
        dout['html_tags']["overview_list"] = dd
        log("##### Final html ####################################")
        llg.msg_answer  = dout
        json_save2(llg, llg.dirout)
        return dout


    def fun_get_summary(llg, ptext):
        log("\n#######  LLM :Summarize #######################################")
        llm_1 = LLM(llg.llm_service, llg.llm_model, max_tokens= llg.llm_max_tokens)


        log("######## LLM call #####################################")
        llm_json = llm_1.get_save_sync(prompt=ptext, output_schema=None, dirout=None)
        # log(llm_json)
        msg  = llm_json["choices"][0]["message"]["content"]
        return msg




if "######### Task News/Activity ####################################################":
    def task_search_activity(llg, topk=5):
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


        llm_service    = llg.llm_service  # "openai"
        llm_model      = llg.llm_model    # "gpt-4o-mini"
        llm_max_tokens = 8000
        query = llg.query2
        dout = jload_cache('ui/static/answers/search_activity_html/data.json' )

        log("########## Start task_search_activity  ############################")
        dftxt, multi_doc_str = fun_search_activity(llg, topk=500, topkstr=10, output_merge_str=1)

        if len(dftxt) < 1:
            dout = task_search_ext(llg)
            return dout


        log("\n#######  LLM :Summarize #########################################")
        llm_1 = LLM(llm_service, llm_model, max_tokens=llm_max_tokens)

        llg.llm_prompt_id = "summarize_03_bullet_noref"  ###  "summarize_02_noref"   #"summarize_01"
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

        msg2= ""
        for li in msg.split("\n"):
            #if "Overview Summary" in li: continue
            if "Market Trend" in li: continue
            if "Summary" in li: continue
            msg2 = msg2 + li + "\n"

        #msg2 = msg2.replace("**Overview Summary:**", "")
        #msg2 = msg2.replace("**Market Trend Analysis:**", "")
        # msg2 = answer_format(msg)
        llg.msg_display = msg2
        log(str(msg2)[:100])


        log("\n#######  MSG json ############################################")
        msg2 = markdown_to_html(msg2)
        dout['html_tags']["summary"] = msg2


        dftxt = dftxt.sort_values("dt", ascending=False)


        dftxt['title2'] = dftxt.apply(lambda x: f"""<a href='{x["url"]}'>{x['title']}</a>""", axis=1  )
        dftxt['text']   = dftxt['text'].apply(lambda x:  ". ".join(str(x).split(". ")[:2]) + "."  )
        dftxt['L3_cat'] = dftxt['L3_cat'].apply(lambda x: x.capitalize()  )


        cols1 = ['date', 'L3_cat',   'title2', 'text', ]
        cols2 = ['Date', 'Industry', "Title", 'Summary']

        dd = dout['html_tags']["table_list"][0]

        dd['columns'] = cols2
        dd['values']  = dftxt[cols1].values
        dd['summary'] = ""
        dd['title']   = ""
        dout['html_tags']["table_list"] = [dd]


        log("##### Final html ##############################################")
        llg.msg_answer  = dout
        json_save2(llg, llg.dirout)

        return dout


    def task_compare_activity(llg, topk=1):
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


            What are the advantages of Tesla electric cars compared to Toyota electric cars ?



        """
        log("########## Start task_compare_activity  ############################")
        llm_service    = llg.llm_service  # "openai"
        llm_model      = llg.llm_model    # "gpt-4o-mini"
        llm_max_tokens = 4000
        query = llg.query2

        #dout = jload_cache('ui/static/answers/compare_activity/data.json' )
        dout = jload_cache('ui/static/answers/answer_v1/data.json' )

        llg.llm_prompt_id = "compare_02"   #"summarize_01"

        if len(llg.query_tags['company_names'])<2:
              return msg_no_enough

        llg2 = deepcopy(llg)
        llg1 = deepcopy(llg)
        company1 = llg1.query_tags['company_names'][0]
        company2 = llg2.query_tags['company_names'][-1]
        activity = ",".join(llg.query_tags['activity_tags'])
        industry = ",".join(llg.query_tags['industry_tags'])
        tsk0 = ",".join(llg.query_tags['task'])
        log("tasks: ", tsk0)

        llg1.query_tags['company_names'] = [company1]
        llg2.query_tags['company_names'] = [company2]


        log("########## Start fun_search_activity  ###########################")
        dftxt1, multi_doc_str1 = fun_search_edge(llg1, topk=10, output_merge_str=1)

        dftxt2, multi_doc_str2 = fun_search_edge(llg2, topk=10, output_merge_str=1)

        dftxt3, multi_doc_str3 = fun_search_ext(llg2, output_merge_str=1)


        if len(dftxt2)<1 or len(dftxt1)<1:
            return msg_no_enough


        log("\n#######  LLM :Summarize #######################################")
        llm_1 = LLM(llm_service, llm_model, max_tokens= llm_max_tokens)

        if 'report' in tsk0:
            llm_prompt_id = "report_compare_02"

        log("Prompt used:", llg.llm_prompt_id)
        ptext = promptlist[ llg.llm_prompt_id]
        ptext = ptext.replace("<question>", query)
        # ptext = ptext.replace("<activity>", activity)

        ptext = ptext.replace("<company1>", company1)
        ptext = ptext.replace("<company2>", company2)

        ptext = ptext.replace("<multi_doc_string1>", multi_doc_str1)
        ptext = ptext.replace("<multi_doc_string2>", multi_doc_str2)
        ptext = ptext.replace("<multi_doc_string3>", multi_doc_str3)
        llg.prompt = ptext


        log("######## LLM call #####################################")
        llm_json = llm_1.get_save_sync(prompt=ptext, output_schema=None, dirout=None)
        # log(llm_json)
        msg  = llm_json["choices"][0]["message"]["content"]
        msg2 = markdown_to_html(msg)
        llg.msg_answer  = msg
        llg.msg_display = msg2

        dout['html_tags']["summary"]  = msg2



        log("######## Add Article sources #########################")
        dftxt1 = dftxt1.drop_duplicates(['title'], keep='first')
        dftxt2 = dftxt2.drop_duplicates(['title'], keep='first')
        title1 = dftxt1['title'].values[:7]

        dd1 = [ { "title": doc['title'],   "url":   doc['url'],  }
               for ii, doc in dftxt1.iloc[:7, :].iterrows() ]

        dd2 = [ { "title": doc['title'],   "url":   doc['url'],  }
               for ii, doc in dftxt2.iloc[:7, :].iterrows()  if doc['title'] not in title1 ]

        #dd3 = [ { "title": doc['title'],   "url":   doc['url'],  }
        #       for ii, doc in dftxt3.iloc[:1, :].iterrows() ]

        dout['html_tags']["source_list"] = dd1 + dd2


        log("##### Final html ####################################")
        llg.msg_answer  = dout
        json_save2(llg, llg.dirout)
        log(dout['html_tags'].keys())

        return dout




if "######### Task Generic Search ###################################################":
    def task_search_ext(llg, topk=11):
        """
               "html_tags": {
            "summary": "Tesla (NASDAQ: TSLA) is an American multinational automotive and clean energy company. It designs and manufactures electric vehicles (EVs; including cars and trucks), battery energy storage systems, solar panels, solar roof tiles, and other related products and services. Tesla was incorporated in 2003 as Tesla Motors, named after the inventor and electrical engineer Nikola Tesla. Entrepreneur and investor Elon Musk became the largest shareholder of the company following an investment in 2004 and has been serving as the CEO of Tesla since 2008. Even though Tesla accounts for only around 1% of the global vehicle market share (as of March 2022), it is one of the largest listed companies globally. The company reported revenue of USD 96.8 billion in 2023 and hit a market cap of USD 1 trillion in October 2021 for the first time, after 11 years since listing—joining only a handful of companies to have done so. Tesla steered its way to the top 100 of the Fortune 500 list for the first time in 2021 and remained within the cluster in 2023 as well.",
            "activity_list": [



        """
        llm_service    = llg.llm_service # "openai"
        llm_model      = llg.llm_model   # "gpt-4o-mini"
        llm_max_tokens = 8000
        topkall = 9
        query   = llg.query2

        dout = jload_cache('ui/static/answers/answer_v1/data.json' )
        dout['html_tags']["summary"]     = " I am sorry, please enlarge the scope of your question."
        dout['html_tags']["source_list"] = []
        dout["question_list"]            = []


        log("########## Start task_search_external  ############################")
        cols1 = [  'url', 'title'  ]

        dftxt, multi_doc_str = fun_search_edge(llg, topk=8, output_merge_str=1)

        dftxt = dftxt.drop_duplicates(['title'], keep='first')
        dftxt = dftxt.iloc[:8, :]

        dftxt2,  multi_doc_str2  = fun_search_ext(llg, topk=8,  output_merge_str=1)


        ######## Add extra docs  ###############################
        # dftxt2 = dftxt2.iloc[:1, :]
        #log(dftxt['title'].values[5])
        # dftxt2['title'] = dftxt2['title'].apply(lambda x: str_split_right_last(x)[0] )

        # dftxt = pd.concat((  dftxt[cols1], dftxt2[cols1].iloc[:,:],   ))
        # dftxt = dftxt.drop_duplicates(['url'], keep='first')
        #log(dftxt['title'])
        #log(dftxt['title'].values[9])

        if len(dftxt) < 1:  return msg_no_enough
        # if len(dftxt) > 100:return msg_too_many

        multi_doc_str = multi_doc_str + "\n\n\n########\n\n" + multi_doc_str2


        log("\n#######  LLM :Summarize #########################################")
        llm_1 = LLM(llm_service, llm_model, max_tokens=llm_max_tokens)

        llg.llm_prompt_id = "question_answer_ext_01"   #"summarize_01"
        tsk0 = ",".join(llg.query_tags['task'])
        log("tasks: ", tsk0)
        log("Prompt used:", llg.llm_prompt_id)

        ptext = promptlist[ llg.llm_prompt_id]
        ptext = ptext.replace("<question>", query)
        ptext = ptext.replace("<multi_doc_string>", multi_doc_str)
        llg.prompt = ptext


        log("LLM call")
        llm_json = llm_1.get_save_sync(prompt=ptext, output_schema=None, dirout=None)
        # log(llm_json)
        msg = llm_json["choices"][0]["message"]["content"]
        llg.msg_answer = msg    # log(msg
        msg2 = markdown_to_html(msg)
        llg.msg_display = ""
        # log(msg2)

        log("\n#######  MSG json ############################################")
        dout['html_tags']["summary"] = msg2
        dd = [ { "title": doc['title'],    ### Remove extra URL
                 "url":   doc['url'],
                 #"date":  doc['date'],
                 #"text":  doc['text']
               }
                for ii, doc in dftxt.iloc[:topkall, :].iterrows()
             ]
        dout['html_tags']["source_list"] = dd

        log("##### Final html ##############################################")
        llg.msg_answer  = dout
        json_save2(llg, llg.dirout)

        return dout




if "######## Task: Output List of companies / industries ############################":
    def task_indus_comlist(llg):
        """
                Country and funding
                Major Industry Group, Minor Industry Group,  Industry, Segments

        """
        log("########## Start task_indus_comlist  #####################")
        global ddata
        dout = jload_cache('ui/static/answers/ageneric/table_html/data.json')

        log("##### Disruptor ###############################################")
        dfi = deepcopy(ddata['com_disrup'])

        dfi = pd_find_concat(dfi,  colsearch='L_cat', keywordlist=llg.query_tags['industry_tags'], threshold=100.0, fullword_only=0)
        dfi = pd_find_country(dfi, col_comid='com_id', country_list=llg.query_tags['country_tags'], )

        if len(dfi) < 1:
            ddict = task_search_ext(llg, )
            return ddict


        log("##### Prepare List ###################")
        com_prev = dfi['com_id'].values.tolist()

        dfi = dfi.sort_values([ 'L3_cat2', 'L1_cat', 'total_funding_amount' ], ascending=[1,1,0])

        dfi = dfi[[ 'com_name2',  'total_funding_amount',    'L2_cat', 'L3_cat2',
                     'product_stage',
                     "operational_presence", 'product_or_service','unique_value', 'target_audience', 'number_of_employees_max',
                 ]]  ## 'disruptor_type',  'business_model', 'L1_cat',

        dfi.columns = [ 'Name', 'Total Funding',    "Indus. Group", "Industry",
                          "stage",
                        "Presence",'Service', 'Value', 'Audience', 'Employees Max'
                      ]  ## "Type", 'Business Model', 'Indus. Group 1',

        dfi = pd_format_table_html(dfi)

        dd = {'format_output': 'table_html' }
        dd['title']   = "Disruptor companies"
        dd['columns'] = list(dfi.columns)
        dd['values']  = list(dfi.values.tolist())
        # log(str(dd)[:1000])
        dout['html_tags']["table_list"] = [ dd ]


        log("##### Incumbent List ###############################################")
        dfi = deepcopy(ddata['com_incum'])

        dfi = pd_find_concat(dfi, colsearch='L_cat', keywordlist=llg.query_tags['industry_tags'], threshold=100.0, fullword_only=0)
        dfi = pd_find_country(dfi, col_comid='com_id', country_list=llg.query_tags['country_tags'], )

        if len(dfi)>0:
            log("##### Prepare List ############################################")
            com_prev = com_prev + dfi['com_id'].values.tolist()

            dfi =  dfi[['com_name2',   'L2_cat', 'L3_cat2', 'L4_catid_segment_summery',
                        'incumbent_description', ]]  # 'L1_cat',

            dfi.columns = [ 'Name',    "Industry Group", "Industry",  'Segment',
                            "Description",   ]  ## 'Industry Group 1',

            dfi = pd_format_table_html(dfi)

            dd = {'format_output': 'table_html' }
            dd['title']   = "Incumbent companies"
            dd['columns'] = list(dfi.columns)
            dd['values']  = list(dfi.values.tolist())
            # log(str(dd)[:1000])
            dout['html_tags']["table_list"].append(dd )



        log("##### All company List ###############################################")
        tags = llg.query_tags['industry_tags'] + llg.query_tags['context']

        dfi = deepcopy(dfcom2)

        dfi = pd_find_reduce(dfi, colsearch='description', keywordlist=tags, threshold=100.0, fullword_only=0)
        dfi = pd_find_country_v2(dfi, col_country='country', country_list=llg.query_tags['country_tags'], )
        dfi = dfi[ -dfi['com_id'].isin(com_prev)]



        log("##### Final html ###################################################")
        llg.msg_answer = dout
        json_save2(llg, llg.dirout)
        return dout



    def task_full_comlist(llg):
        """
                Country and funding
                Major Industry Group, Minor Industry Group,  Industry, Segments

        """
        log("########## Start task_indus_comlist_full  #####################")
        global ddata
        dout = jload_cache('ui/static/answers/ageneric/table_html/data.json')


        log("##### All company List ###############################################")
        tags = llg.query_tags['industry_tags'] + llg.query_tags['context']

        dfi = deepcopy(dfcom2)

        dfi = pd_find_reduce(dfi, colsearch='description', keywordlist=tags, threshold= 90.0, fullword_only=0)
        dfi = pd_find_country_v2(dfi, col_country='country', country_list=llg.query_tags['country_tags'], )


        if len(dfi) < 1:
            ddict = task_search_ext(llg, )
            return ddict


        log("##### Prepare List ###################")
        # com_prev = dfi['com_id'].values.tolist()
        # ['com_id', 'country', 'description', 'founded_date', 'name', 'number_of_employees_min', 'total_funding_amount']

        dfi = dfi.sort_values([  'number_of_employees_min',  'country' ], ascending=[0,0])
        dfi['name2'] = dfi.apply(lambda x: f"""<a href="https://eeddge.com/companies/{x['com_id']}" >{x['name']}</a>""" , axis=1)


        dfi = dfi[[ 'name2', 'country', 'description',  'total_funding_amount', 'number_of_employees_min', 'founded_date', ]]

        dfi.columns = [ 'Name', 'Country', 'Description',  'Total funding', 'Employee count', 'Date creation',
                      ]  ## "Type", 'Business Model', 'Indus. Group 1',


        dfi = pd_format_table_html(dfi)

        dd = {'format_output': 'table_html' }
        dd['title']   = "Companies found"
        dd['columns'] = list(dfi.columns)
        dd['values']  = list(dfi.values.tolist())
        # log(str(dd)[:1000])
        dout['html_tags']["table_list"] = [ dd ]


        log("##### Final html ###################################################")
        llg.msg_answer = dout
        json_save2(llg, llg.dirout)
        return dout




    def task_com_indulist(llg):
        """

            Comparison year to year: Funding.

                https://jsfiddle.net/api/post/library/pure/



        """
        log("########## Start task_com_industlist  #####################")
        global dfacti
        dout = jload_cache('ui/static/answers/ageneric/table_chart_html/data.json')


        log("##### Overview ############################################")
        dfi = deepcopy(dfacti)

        log(dfi.columns)
        if len(llg.query_tags['company_names']) > 0:
            comtag = llg.query_tags['company_names'][0].lower()
            dfi =pd_find_com_v2(dfi, colcom='com_extract', comlist=[ comtag ], threshold=90)
            # dfi    = dfi[ dfi['com_extract'].apply(lambda x : comtag in str(x).lower() ) ]

        if len(dfi) < 1:
            return msg_no_enough
        log(dfi, dfi.shape)



        ######################################################
        dfi['link']   = dfi.apply(lambda  x: "http://www.eeddge.com/industry/" + f"{x['L3_catid']}" , axis=1 )
        dfi['L3_cat'] = dfi.apply(lambda x : f"<a href='{x['link']}'>{x['L3_cat'].capitalize()}</a>", axis=1 )

        cols = [ 'L2_cat' ,  'L3_cat'   ]

        dfi = dfi.groupby(cols).agg({'url':'count'}).reset_index()
        #dfi = dfi[cols]
        dfi.columns = ['Indus. Group', 'Industry',  'Activity count' ]
        dfi = dfi.sort_values(['Activity count'], ascending=[0])
       # dfi = dfi.drop_duplicates()
        dfi = pd_format_table_html(dfi, colnum=None, coldate=None)

        dd = { 'output_format': 'table_html'
                # ,'summary': s0
                ,'columns': list(dfi.columns)
                ,'values' : dfi.values.tolist() }
        dout['html_tags']["table_list"] = [dd]

        dout['html_tags']["chart_html"] = []


        #############################################################
        dout['html_tags']["source_list"]   = None
        dout['html_tags']["question_list"] = []

        log("##### Final html ####################################")
        llg.msg_answer = dout
        json_save2(llg, llg.dirout)
        return dout



    def task_invest_investorlist(llg):
        """

            Comparison year to year: Funding.

                https://jsfiddle.net/api/post/library/pure/



        """
        log("########## Start task_com_investlist  #####################")
        global dfinvest
        dout = jload_cache('ui/static/answers/funding_html/data_sankey.json')


        log("##### Filter ############################################")
        dfi = None
        if len(llg.query_tags['company_names']) > 0:
            comtag = llg.query_tags['company_names'][0].lower()
            dfi    = pd_find_com_v2(dfinvest, colcom='receiver_name', comlist=[comtag], threshold=90)
            log(comtag, dfi.shape)

        if   len(llg.query_tags['industry_tags']) > 0:
            Ltag =  llg.query_tags['industry_tags'][0]
            dfi = dfinvest if dfi is None else dfi
            dfi  = dfi[ dfi['L_cat'].apply(lambda x :  Ltag in str(x).lower() ) ]
            log(Ltag, dfi.shape)

        if dfi is None or  len(dfi) < 1:
            log('No investment for those industries')
            ddict = task_search_ext(llg)
            return ddict

        log(dfi, dfi.shape)
        dfi = dfi.sort_values(['receiver_name', 'date'], ascending=[1, 0])

        ########################################################################
        s0   = ""
        dfi2 = dfi.groupby(['receiver_name',]).agg({'amount': 'sum'}).reset_index()
        if len(dfi2) < 3:
           dfi2 = dfi2.values
           for vv in dfi2:
              s0 = s0 + f"{vv[0].capitalize()} received {vv[1]}  USD  in total funding.<br>"

        dfi = dfi[-dfi['funding_stage_name'].str.contains('debt')]
        dfi['date'] = dfi['date'].apply(lambda  x  : str(x).split(" ")[0])


        log("########## Sankey Graph ###########################################")
        topk = 10
        dfi2 =  dfi[dfi['date'].str.contains("2024")]
        dfi2 = dfi2.drop_duplicates([ 'receiver_name', 'date', 'amount'])
        dfi2 =  dfi2.groupby(['receiver_name',]).agg({'amount':'sum'}).reset_index().sort_values(['amount'], ascending=False)
        topname = dfi2['receiver_name'].values[:topk]
        df2  = dfi[dfi['receiver_name'].isin(topname)]
        log(topname)

        topk2 = 20
        if len(df2) > 0:
            dd = dout['html_tags']["chart_html"][1]['data_highcharts']["series"][0]

            # nlist = [{ "id": xi,
            #            "color": color_get_random(),
            #            "column": 1
            #          } for xi in df2['L3_cat'].unique()]
            # dd['nodes'] = nlist

            nlist = [{ "id": xi,  "color": color_get_random(),
                       "column": 1
                     } for xi in df2['receiver_name'].unique()][:topk]
            dd['nodes'] += nlist

            nlist = [{ "id": xi,  "color": color_get_random(),
                       "column": 2
                     } for xi in df2['investor_name'].unique()][:topk2]
            dd['nodes'] += nlist


            ### PairLinks  ###############################################
            df2['L3_cat2'] = df2['L3_cat'].apply(lambda x: x.split(";")[0] )
            df3   = df2.groupby(["L3_cat2", 'receiver_name']).agg({"total_funding": "count"}).reset_index()
            nlist = [list(vv) for vv in df3.values][:topk]
            dd['data'] = nlist


            df3 = df2.groupby(["receiver_name", 'investor_name']).agg({'amount': "count"}).reset_index()
            df3 = df3.sort_values('amount', ascending=False).groupby(['receiver_name', 'investor_name']).head(4)

            nlist = [list(vv) for vv in df3.values][:topk2]
            dd['data'] += nlist

            dout['html_tags']["chart_html"][1]['data_highcharts']["series"][0] = dd
            dout['html_tags']["chart_html"][1]['data_highcharts']['title']["text"]= "Top funding in 2024"
            #log(dd)

        log(dout['html_tags']["chart_html"][1])


        log("########## Time Series Histogram ##################################")
        dfi2 = dfi.drop_duplicates([  'date', 'amount'  ], keep='first')
        if len(dfi2)>0:
            dfi2['date2']  = pd.to_datetime(dfi2['date'])
            dfiq           = dfi.groupby(   dfi2['date2'].dt.to_period('Q'))['amount'].sum().reset_index()
            dfiq.columns   = ['date2', 'amount']
            dfiq['date2']  = dfiq['date2'].apply(lambda x: x.strftime('%Y-Q%q'))
            dfiq['amount'] = np.round(dfiq['amount'] / 10**6, 1)
            # log(dfiq)

            dd = dout['html_tags']["chart_html"][0]["data_highcharts"]
            dd["xAxis"]["categories"] = dfiq['date2'].values.tolist()
            dd["series"][0]['name']   = "Total Funding (USD)"
            dd["series"][0]['data']   = dfiq['amount'].values.tolist()
            dout['html_tags']["chart_html"][0]["data_highcharts"] = dd
            log(dd)
        else:
            dout['html_tags']["chart_html"][0]={}


        log("########## Funding Table  ########################################")
        cols = [ 'receiver_name' ,  'investor_name', 'date', 'funding_stage_name', 'amount','total_funding', 'L3_cat',]
        ##    'segment_name' , 'edge_link',
        dfi = dfi[cols]
        dfi = pd_format_table_html(dfi, colnum=None, coldate=None)
        dfi.columns = ['Investee', 'Investor', "date", 'Stage', "Amount", "Total Funding", 'Industries' ]
        dd    = {  'output_format': 'table_html'

                  # ,'summary': s0
                  ,'columns': list(dfi.columns)
                  ,'values' : dfi.values.tolist() }
        dout['html_tags']["table_list"] = [dd]



        ###########################################################
        dout['html_tags']["source_list"]   = None
        dout['html_tags']["question_list"] = []

        log("##### Final html ####################################")
        llg.msg_answer = dout
        json_save2(llg, llg.dirout)
        return dout


    def task_invest_receiverlist(llg):
        """


        """
        log("########## Start task_invest_receiverlist  ########################")
        global dfinvest
        dout = jload_cache('ui/static/answers/funding_html/data.json')
        log(dout)


        log("##### Overview ####################################################")
        dfi = None
        if len(llg.query_tags['company_names']) > 0:
            comtag = llg.query_tags['company_names'][0].lower()
            dfi    = dfinvest[ dfinvest['investor_name'].apply(lambda x :  str_fuzzy_match_is_same(comtag, str(x).lower(), 99 )) ]
            dfi = dfi.sort_values(['investor_name', 'date'], ascending=[1,0])

        if   len(llg.query_tags['industry_tags']) > 0:
            Ltag =  llg.query_tags['industry_tags'][0]
            dfi  = dfinvest if dfi is None else dfi
            dfi  = dfi[ dfi['L_cat'].apply(lambda x :  Ltag in str(x).lower() ) ]
            dfi  = dfi.sort_values(['receiver_name', 'date'], ascending=[1,0])
            tot_amt = dfi['amount'].sum()

        if dfi is None or len(dfi)<1:
            dout = task_search_ext(llg)
            return dout

        log(dfi, dfi.shape)
        log("########## Sankey Graph ##########################################")
        # df2 = dfi[-dfi['funding_stage_name'].str.contains('debt')]
        # if len(df2) > 0:
        #     log(dout)
        #
        #     # log(dout['html_tags']["chart_html"][0]["data_highcharts"].keys())
        #     # dd = dout['html_tags']["chart_html"][0]["data_highcharts"]["series"][0]
        #     #
        #     # #nlist = [{ "id": xi,
        #     # #           "color": color_get_random(),
        #     # #           "column": 1
        #     # #         } for xi in df2['L3_cat'].unique()]
        #     # #dd['nodes'] = nlist
        #     #
        #     # nlist = [{ "id": xi,
        #     #            "color": color_get_random(),
        #     #            "column": 2
        #     #          } for xi in df2['receiver_name'].unique()]
        #     # dd['nodes'] = nlist
        #     #
        #     # nlist = [{ "id": xi,
        #     #            "color": color_get_random(),
        #     #            "column": 3
        #     #          } for xi in df2['investor_name'].unique()]
        #     # dd['nodes'] += nlist
        #     #
        #     # ### PairLinks  ###############################################
        #     # #df3   = df2.groupby(["L3_cat", 'receiver_name']).agg({"total_funding": "sum"}).reset_index()
        #     # #nlist = [list(vv) for vv in df3.values]
        #     # #dd['data'] = nlist
        #     #
        #     # df3   = df2.groupby(["receiver_name", 'investor_name']).agg({'amount': "count"}).reset_index()
        #     # nlist = [list(vv) for vv in df3.values]
        #     # dd['data'] += nlist
        #
        #     # dout['html_tags']["chart_html"][0]["data_highcharts"]["series"][0] = dd
        #     #log(dd)


        ########## Time Series Histogram #####################
        dfi2 = dfi[-dfi['funding_stage_name'].str.contains('debt')].drop_duplicates(['date', 'amount'], keep='first')
        if len(dfi2) > 0:
            dfi2['date2'] = pd.to_datetime(dfi2['date'])
            dfiq = dfi.groupby(dfi2['date2'].dt.to_period('Q'))['amount'].sum().reset_index()
            dfiq.columns   = ['date2', 'amount']
            dfiq['date2']  = dfiq['date2'].apply(lambda x: x.strftime('%Y-Q%q'))
            dfiq['amount'] = np.round(dfiq['amount'] / 10 ** 6, 1)
            # log(dfiq)

            dd = dout['html_tags']["chart_html"][0]["data_highcharts"]
            dd["xAxis"]["categories"] = dfiq['date2'].values.tolist()
            dd["series"][0]['name']   = "Total Funding (USD)"
            dd["series"][0]['data']   = dfiq['amount'].values.tolist()
            dout['html_tags']["chart_html"][0]["data_highcharts"] = dd

        else:
            dout['html_tags']["chart_html"][0] = {}


        ###############################
        s0 = ""
        dfi2 = dfi.groupby(['investor_name',]).agg({'amount': 'sum'}).reset_index()
        if len(dfi2) < 3:
           dfi2 = dfi2.values
           for vv in dfi2:
              s0 = s0 + f"{vv[0].capitalize()} invested {vv[1]}  USD  in total funding.<br>"

        dout['html_tags']["summary"]    = s0

        ###############################
        ##    'segment_name' , 'edge_link',
        cols = [ 'receiver_name' ,  'investor_name', 'date', 'funding_stage_name', 'amount', 'total_funding', 'L3_cat', ]
        dfi  = dfi[cols]

        dfi = pd_format_table_html(dfi, colnum=None, coldate=None)

        dfi.columns = ['Investee', 'Investor', "date", 'Stage', "Amount", "Total Funding", 'Industries' ]
        dd    = {  'output_format': 'table_html'
                  ,'columns':       list(dfi.columns)
                  ,'values' :       dfi.values.tolist() }
        dout['html_tags']["table_list"]    = [dd]

        ##################################
        dout['html_tags']["source_list"]   = None
        dout['html_tags']["question_list"] = []

        log("##### Final html ####################################")
        llg.msg_answer = dout
        json_save2(llg, llg.dirout)
        return dout




########### Formatting #############################################################
def pd_format_table_html(dfi, colnum=None, coldate=None):

    def isfloat(x):
        try:
           float(x)
           return True
        except Exception as e:
           return False

    def str_format_str(x, maxsentence=3):
        if pd.isna(x): return ''
        x = str(x).lower().replace("_", " ")
        x = x.replace(";", " , ")

        li = [xi.capitalize() for xi in x.split(". ")]
        x = ". ".join(li[:maxsentence])
        return x

    def str_format_number(x):
        if pd.isna(x): return ''
        try:
            if float(x) > 1000.0:
                x = '{:,.0f}'.format(x)
        except Exception as e:
            log(e)
        return x

    if colnum is None:
        colnum = []
        for ci in dfi.columns:
            # Detect currency/large numbers
            vali = dfi[ci].values[-1]
            dtypei = str(dfi[ci].dtypes)
            if isfloat(vali) or 'float' in dtypei:
                colnum.append(ci)

    for ci in colnum :
       dfi[ci] = dfi[ci].apply(lambda x: str_format_number(x))

    for ci in [ ci for ci in dfi.columns if ci not in colnum    ]:
        dfi[ci] = dfi[ci].apply(lambda x: str_format_str(x) )

    return dfi





if "######### Search Retrieval #####################################################":
    def fun_search_ext(llg, topk=5, output_merge_str=0):
        """
               "html_tags": {
            "summary": "Tesla (NASDAQ: TSLA) is an American multinational automotive and clean energy company. It designs and manufactures electric vehicles (EVs; including cars and trucks), battery energy storage systems, solar panels, solar roof tiles, and other related products and services. Tesla was incorporated in 2003 as Tesla Motors, named after the inventor and electrical engineer Nikola Tesla. Entrepreneur and investor Elon Musk became the largest shareholder of the company following an investment in 2004 and has been serving as the CEO of Tesla since 2008. Even though Tesla accounts for only around 1% of the global vehicle market share (as of March 2022), it is one of the largest listed companies globally. The company reported revenue of USD 96.8 billion in 2023 and hit a market cap of USD 1 trillion in October 2021 for the first time, after 11 years since listing—joining only a handful of companies to have done so. Tesla steered its way to the top 100 of the Fortune 500 list for the first time in 2021 and remained within the cluster in 2023 as well.",
            "activity_list": [

        """
        log("########## Start fun_search_external  ##########################")

        log("\n####### Fetch actual text from DataSource ################### ")
        #### match date pattern here
        #global dfalltext
        #if dfalltext is None:
            # cols = ['text_id', 'url', 'date', 'title', 'text', 'score', 'L0_catnews', 'L_cat', 'com_extract']
            # dfacti = dbsql_fetch_text_by_doc_ids(db_path=llg.db_path_sql,
            #                                     table_name=llg.table_name_sql, cols=cols, text_ids=[])
            # dfacti = pd.DataFrame(dfacti)
            #load_all_dataset()

        #dftxt = deepcopy(dfalltext)
        #log('Doc retrieved:', dftxt, dftxt.shape)

        from utilsnlp.utils_base import get_data_v3, get_data_v4

        dftxt = get_data_v3(llg.query2, topk=topk, returnval='df')
        log(dftxt.shape)

        llist=["cbinsight", 'tracxn', 'crunchbase', 'alpha-sense', 'pitchbook', 'ourcrowd.com', 'financecharts' ]
        for namei in llist:
            dftxt = dftxt[ -dftxt['url'].str.contains(namei) ]


        if len(dftxt) < 1:
            return dftxt if output_merge_str ==0 else dftxt,""


        log("#### Doc Re-Ranking #########################################")
        t0 = date_now(returnval='unix')


        # log("\n####### Dsiplay ranking ################################## ")
        # dftxt = ranking_display(dftxt, llg.query_tags)
        # if output_merge_str ==0 :
        #     return dftxt

        log("\n####### Format Docs prompt ############################### ")
        #topk = min(7, topk)
        #url   = x['url']
        multi_dftxt = [ f"""## Title: {x['title']}\n## Text:{x['text']}"""
                        for ii, x in dftxt.iloc[:topk, :].iterrows() ]
        multi_doc_str = "\n---\n".join(multi_dftxt)
        log('Doc appended:', topk)
        log('Full doc size: ', len(multi_doc_str), 'chars, ', len(multi_doc_str.split(" ")), ' words')

        #if os.environ.get('istest', "0") == "1":
        #    return multi_doc_str
        return dftxt, multi_doc_str



    def fun_search_edge(llg, topk=5, output_merge_str=0):
        """
            "html_tags": {
            "summary": "Tesla (NASDAQ: TSLA) is an American multinational automotive and clean energy company. It designs and manufactures electric vehicles (EVs; including cars and trucks), battery energy storage systems, solar panels, solar roof tiles, and other related products and services. Tesla was incorporated in 2003 as Tesla Motors, named after the inventor and electrical engineer Nikola Tesla. Entrepreneur and investor Elon Musk became the largest shareholder of the company following an investment in 2004 and has been serving as the CEO of Tesla since 2008. Even though Tesla accounts for only around 1% of the global vehicle market share (as of March 2022), it is one of the largest listed companies globally. The company reported revenue of USD 96.8 billion in 2023 and hit a market cap of USD 1 trillion in October 2021 for the first time, after 11 years since listing—joining only a handful of companies to have done so. Tesla steered its way to the top 100 of the Fortune 500 list for the first time in 2021 and remained within the cluster in 2023 as well.",
            "activity_list": [

        """
        log("########## Start fun_search_edge  ##########################")
        query = llg.query2
        log("llg", llg)

        log("\n####### Fetch  text from Edge ########################## ")
        global dfragall, ddata

        cols = [ 'text_chunk', 'url', 'text_html', 'L_cat','title', 'L0_catnews', 'com_extract', 'date', 'info']
        dftxt = fun_search_edge_score(dfragall, llg=llg, cols=cols)

        if len(dftxt)<1:
            log('No edge results')
            return pd.DataFrame([], columns=cols  + ['score']), ""

        log(dftxt[[ 'L_cat', 'title', 'text_chunk', 'score'   ]])


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

        log("\n####### Dsiplay ranking ################################## ")
        # dftxt = ranking_display(dftxt, llg.query_tags)
        # if output_merge_str ==0 :
        #     return dftxt

        log("\n####### Format Docs prompt ############################### ")
        topk = min(7, topk)
        #url   = x['url']
        multi_dftxt = [ f"""## Title: {x['title']}\n## Text:{x['text_chunk']}"""
                        for ii, x in dftxt.iloc[:topk, :].iterrows() ]
        multi_doc_str = "\n---\n".join(multi_dftxt)
        log('Doc appended:', topk)
        log('Full doc size: ', len(multi_doc_str), 'chars, ', len(multi_doc_str.split(" ")), ' words')

        #if os.environ.get('istest', "0") == "1":
        #    return multi_doc_str
        return dftxt, multi_doc_str



    def query_expand_clean( query2 ):
        lblock = {'the', 'to', 'in', 'on', 'not', 'also', 'well', 'for', 'this', 'are', 'they', 'and', 'is',
                  'an', 'as', 'at', 'be', 'by', 'do', 'go', 'he', 'if', 'in', 'were',
                  'is', 'it', 'me', 'my', 'no', 'of', 'on', 'or', 'so', 'to', 'up',  'we',
                  'describe', 'explain',  'provide', 'what', 'are', 'how', 'why', 'companies', 'company',
                  'offering', 'providing','giving', 'solutions', 'solution'
                  }

        lblock = lblock | {

            "provide", "describe", "explain", 'summarize', "details", "recent",

            "extra", "details", "particular", "specific",
            "their", "these", "those", "them", "they", "this", "that", "whose", "whom",

            # Prepositions
            "through", "between", "among", "within", "without", "beside", "beyond", "during", "across", "along",

            # Question/Relative words
            "where", "which", "what", "when", "why", "how", "whoever", "whatever", "whenever", "wherever",

            # Conjunctions
            "although", "because", "unless", "while", "whereas", "whether", "since", "before", "after", "until",

            # Determiners
            "each", "every", "some", "any", "many", "much", "few", "several", "both", "either",

            # Adverbs
            "then", "there", "here", "now", "soon", "later", "often", "always", "never", "sometimes",

            # Auxiliary verbs
            "could", "would", "should", "might", "must", "shall", "will", "may", "can", "does",

            # Preposition combinations
            "into", "onto", "upon", "throughout", "underneath", "inside", "outside", "beneath", "behind", "besides",

            # Relative pronouns
            "wherein", "whereby", "whereof", "whereon", "wherefore", "whence", "whither", "whilst", "thence", "thither",

            # Miscellaneous function words
            "thus", "hence", "else", "yet", "still", "just", "even", "only", "quite", "rather",

            # Conjunctions
            "moreover", "furthermore", "nevertheless", "however", "therefore", "meanwhile", "consequently", "albeit", "whereas", "besides",

            # Transitional phrases
            "accordingly", "subsequently", "alternatively", "similarly", "likewise", "namely", "specifically", "indeed", "certainly", "notably",

            # Subordinating conjunctions
            "although", "provided", "assuming", "lest", "unless", "whenever", "wherever", "whichever", "inasmuch", "insofar",

            # Correlative conjunctions
            "neither", "either", "whether", "notwithstanding", "albeit", "despite", "regardless", "though", "while", "whilst",

            # Prepositions
            "amid", "amongst", "betwixt", "concerning", "regarding", "respecting", "excluding", "including", "pending", "considering",

            # Relative adverbs
            "whereby", "wherein", "whereof", "whereon", "wherefore", "whence", "whither", "whereafter", "whereat", "whereto",

            # Modal auxiliaries
            "ought", "shall", "should", "would", "might", "must", "needn't", "shan't", "won't", "mightn't",

            # Determiners
            "another", "certain", "various", "sundry", "whichever", "whatever", "whose", "whosever", "whatsoever", "whosoever",

            # Pronouns
            "oneself", "thyself", "yourselves", "ourselves", "themselves", "myself", "itself", "himself", "herself", "whomever",

            # Miscellaneous connectors
            "herein", "thereof", "therein", "herewith", "therewith", "hereby", "thereby", "heretofore", "thenceforth", "hitherto"
        }

        llsyno =[ ('electric cars', 'electric cars electric vehicule EV '),
                  ('embodied ', 'embodied robot '),
                  ('market size', 'market size tam'),
        ]

        x = str_replace_punctuation(str(query2))
        for xi in llsyno :
            x = x.replace(xi[0], xi[1])

        llist = x.split(" ")
        llist = [xi for xi in llist if len(xi)>=2  and xi not in lblock]
        llist = np_unique(llist)
        log('llist:', llist)
        return llist



    def fun_search_edge_score(dfragall, llg, cols=None):
        from rag.engine_emb import (pd_search_keywords_fuzzy, pd_search_keywords_fullmatch, pd_search_keywords_fullmatch_single
                                    )

        cols =[ 'text_chunk', 'url', 'text_html', 'L_cat','title', 'L0_catnewa', 'com_extract'] if cols is None else cols

        q = ""
        for ci in [  'activity_tags', 'company_names', 'industry_tags', 'context', 'country_tags'    ]:
           q = q + ' ' + " ".join(llg.query_tags[ci])

        # llist = query_expand_clean(llg.query2)
        llist = query_expand_clean(q)

        dfw = deepcopy(dfragall[cols])
        dfw = pd_search_keywords_fuzzy(dfw, 'text_chunk', keywords=llist, tag='_txt', cutoff= 75)
        dfw = pd_search_keywords_fuzzy(dfw, 'title',      keywords=llist, tag='_tit', cutoff= 75)
        #dfw = pd_search_keywords_fuzzy(dfw, 'L_cat',      keywords=llg.query_tags['industry_tags']  ,tag='_ind',  cutoff=90)


        dfw = pd_search_keywords_fullmatch_single(dfw, 'L_cat',      keywords=llg.query_tags['industry_tags']  ,tag='_ind',  cutoff=90)

        # dfw = pd_search_keywords_fuzzy(dfw, 'text_html',   keywords=llg.query_tags['industry_tags'] , tag='_htm')
        # dfw = pd_search_keywords_fuzzy(dfw, 'L0_catnews',  keywords=llg.query_tags['activity_tags'] , tag='_act',  cutoff=80)
        dfw = pd_search_keywords_fullmatch_single(dfw, 'L0_catnews',  keywords=llg.query_tags['activity_tags'] ,tag='_act',  cutoff=80)


        dfw = pd_search_keywords_fuzzy(dfw, 'com_extract', keywords=llg.query_tags['company_names'] ,tag='_com',  cutoff=70)
        dfw = pd_search_keywords_fuzzy(dfw, 'date',        keywords=llg.query_tags['date']          ,tag='_date', cutoff=70)

        # dfw = pd_search_keywords_fullmatch(dfw, 'text_chunk', keywords=llist, tag="_full", only_score=1,  )
        # log(dfw.sort_values(['score_full'], ascending=0)[['title', 'score_full' ]] )

        #### 0.5
        dfw['score'] = dfw.apply(lambda x: x['score_txt'] + 0.7*x['score_tit'] + 1.5*x['score_ind']  + 1.2*x['score_com']  + 0.7*x['score_act'] + 1.2*x['score_date'], axis=1   )
        # dfw['score'] = dfw.apply(lambda x: x['score_txt'] + 0.2*x['score_tit'] + 1.2*x['score_ind']  + 1.2*x['score_com'] + 1.2*x['score_date'] + 1.2*x['score_full'] , axis=1   )

        dfw   = dfw.sort_values('score', ascending=0)

        log(dfw[[ 'score_tit', 'score_txt', 'score_ind', 'score_act' ]])
        dftxt = dfw[ dfw['score'] > 0.6  ]
        return dftxt



    def fun_search_activity(llg, topk=1000, topkstr=5, output_merge_str=0):
        """
            "html_tags": {
            "summary": "Tesla (NASDAQ: TSLA) is an American multinational automotive and clean energy company. It designs and manufactures electric vehicles (EVs; including cars and trucks), battery energy storage systems, solar panels, solar roof tiles, and other related products and services. Tesla was incorporated in 2003 as Tesla Motors, named after the inventor and electrical engineer Nikola Tesla. Entrepreneur and investor Elon Musk became the largest shareholder of the company following an investment in 2004 and has been serving as the CEO of Tesla since 2008. Even though Tesla accounts for only around 1% of the global vehicle market share (as of March 2022), it is one of the largest listed companies globally. The company reported revenue of USD 96.8 billion in 2023 and hit a market cap of USD 1 trillion in October 2021 for the first time, after 11 years since listing—joining only a handful of companies to have done so. Tesla steered its way to the top 100 of the Fortune 500 list for the first time in 2021 and remained within the cluster in 2023 as well.",
            "activity_list": [


        """
        log("########## Start fun_search_activity  #########################")
        query = llg.query2

        log("\n####### Fetch actual text from DataSource ################### ")
        #### match date pattern here
        # text_ids = [res["text_id"] for res in llg.results ]
        global dfacti
        if dfacti is None:
            # cols = ['text_id', 'url', 'date', 'title', 'text', 'score', 'L0_catnews', 'L_cat', 'com_extract']
            # dfacti = dbsql_fetch_text_by_doc_ids(db_path=llg.db_path_sql,
            #                                     table_name=llg.table_name_sql, cols=cols, text_ids=[])
            # dfacti = pd.DataFrame(dfacti)
            load_all_dataset()

        dftxt = deepcopy(dfacti)
        log('Doc retrieved:', dftxt, dftxt.shape)


        log("#### Doc Keyword filtering ###################################")
        # def str_docontain(w, x):
        #     x2 = str(x).lower()
        #     for wi in w.split(" "):
        #         if wi.lower() not in x2 : return False
        #     return True
        log("company_names: ", llg.query_tags['company_names'])
        for w in llg.query_tags['company_names']:
            dftxt = dftxt[dftxt['com_extract'].apply(lambda x: str_docontain(w, x))]
            log(w, dftxt.shape)
            # break
            #log(dftxt)


        log("activity_tags: ", llg.query_tags['activity_tags'])
        for w in llg.query_tags['activity_tags']:
            if 'news' in w or  'activit' in w : continue
            dftxt = dftxt[dftxt['L0_catnews'].apply(lambda x: str_docontain(w, x))]
            log(w, dftxt.shape)
            # if len(dftxt) < 1: return msg_no_enough


        log("industry_tags: ", llg.query_tags['industry_tags'])
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
            # for w in llg.query_tags['industry_tags']:
            #     dftxt = dftxt[dftxt['text'].apply(lambda x: w in x)]
            #     log(w, dftxt.shape)

            for w in llg.query_tags['company_names']:
                dftxt = dftxt[dftxt['text'].apply(lambda x: w in x)]
                log(w, dftxt.shape)

            if len(dftxt) == len(dfacti):
                return pd.DataFrame() if output_merge_str == 0 else pd.DataFrame(), ""


        if len(dftxt) < 1:
            return dftxt if output_merge_str ==0 else dftxt,""

        #if len(dftxt) > 500:
        #    return dftxt if output_merge_str ==0 else dftxt,""

        log("#### Doc Re-Ranking #########################################")
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

        log("\n####### Dsiplay ranking ################################## ")
        # dftxt = ranking_display(dftxt, llg.query_tags)
        # log(dftxt['date'])
        dftxt['dt'] = dftxt['date'].apply(lambda x: to_int(str(x).replace("-", "")) )
        dftxt       = dftxt.sort_values(['dt'], ascending=[False] )
        #vlog(dftxt['dt'])

        if output_merge_str ==0 :
            return dftxt

        log("\n####### Format Docs prompt ############################### ")
        topkstr = min(10, topkstr)
        #url   = x['url']
        multi_doc_str = [ f"""title: {x['title']}\ndate:{x['date']}\ntext:{x['text']}"""
                          for ii, x in dftxt.iloc[:topkstr, :].iterrows() ]
        n = len(multi_doc_str)
        multi_doc_str = "\n---\n".join(multi_doc_str)

        log('Doc appended:', n )
        log('Full doc size: ', len(multi_doc_str), 'chars, ', len(multi_doc_str.split(" ")), ' words')


        #if os.environ.get('istest', "0") == "1":
        #    return multi_doc_str
        return dftxt, multi_doc_str




if "######### Search Dataframe #################################################":
    def fun_search_edge_com(llg, topk=7, output_merge_str=0):
        global dfcom2
        dftxt = pd_find_com_v2(dfcom2, colcom='name', comlist=llg.query_tags['company_tags'], threshold=90)
        return dftxt


    def pd_find_com(dfcom, llg, threshold=90, full=0):
        dfkall = pd.DataFrame()

        def mmatch(wi, wref):
            for w0 in str(wref).split(" "):
                if str_fuzzy_match( wi,  w0, threshold= threshold ) : return True
            return False

        def mmatch2(wshort, wlong):

            wlong = str(wlong).lower().strip()
            ll = [  ci for ci in str(wshort).split(" ")  if len(ci)>2 and ci not in {"&", "and", 'the'}   ]
            nall =0
            for wk in ll:
                if wk in wlong :
                    nall += 1
            return True if (nall == len(ll)) else False


        for wfull in llg.query_tags['company_names']:
           com = str(wfull).lower().strip()
           dfk = dfcom[dfcom['name'].apply(lambda x: mmatch2(com, x))  ]
           if len(dfk)>0:
               dfkall = pd.concat((dfkall, dfk))


        if full == 1:
           lwords = llg.query_tags['industry_tags'] + llg.query_tags['context']
           lwords = keywords_clean(lwords)

           dfk = None
           for word in lwords:
               word = str(word).lower().strip()
               if dfk is None or len(dfk)<1:
                  dfk = dfcom[dfcom['description'].apply(lambda x: mmatch2(word, x))  ]
               else:
                   dfk = dfk[dfk['description'].apply(lambda x: mmatch2(word, x))]

        return dfkall



    def pd_find_com_v2(dfcom, colcom='com_extract', comlist=None, threshold=90):

        if comlist is None or len(comlist) == 0:
            return dfcom

        def mmatch2(wshort, wlong):
            wlong = str(wlong).lower().strip()
            ll = [  ci for ci in str(wshort).lower().split(" ")  if len(ci)>2 and ci not in {"&", "and", 'the'}   ]
            nall =0
            for wk in ll:
                if wk in wlong :
                    nall += 1
            return True if (nall == len(ll)) else False


        dfkall = pd.DataFrame()
        for com in comlist:
           com = str(com).lower().strip()
           dfk = dfcom[dfcom[colcom].apply(lambda x: mmatch2(com, x))  ]
           if len(dfk)>0:
               dfkall = pd.concat((dfkall, dfk))

        return dfkall



    def pd_find_concat(dfcom, colsearch='com_extract', keywordlist=None, threshold=100.0, fullword_only=0):
        """
            # log("#### Doc Keyword filtering ###################################")
        # # def str_docontain(w, x):
        # #     x2 = str(x).lower()
        # #     for wi in w.split(" "):
        # #         if wi.lower() not in x2 : return False
        # #     return True
        # log("company_names: ", llg.query_tags['company_names'])
        # for w in llg.query_tags['company_names']:
        #     dftxt = dftxt[dftxt['com_extract'].apply(lambda x: str_docontain(w, x))]
        #     log(w, dftxt.shape)
        #     log(dftxt)


            for w in llg.query_tags['industry_tags']:
                w1 = str(w).lower().strip()
                for wi in w1.split(" "):
                    log(wi)
                    if len(dfi)<1:break
                    dfi = dfi[dfi['L_cat'].apply(lambda x: wi in str(x).lower().split(" "))]
                    log(dfi.shape)


        """
        if dfcom is None or len(dfcom)< 1:
            return dfcom

        if keywordlist is None or len(keywordlist) == 0:
            return dfcom

        keywordlist = keywords_clean(keywordlist)
        threshold = threshold*0.01 if threshold > 10.0 else  threshold

        def mmatch2(wordlist, text, threshold=1.0):
            if fullword_only == 1:
                text = [   xi for xi in  str(text).lower().strip().split(" ") if len(xi) > 1 ]
            else:
                text  = str(text).lower().strip()

            ### Match each sub keyword
            # wordlist = str(wordlist).lower().strip()
            # ll    = [  ci for ci in wordlist.split(" ")  if len(ci)>2 and ci not in nglist  ]
            nall  = 0
            for wk in wordlist:
                if wk in text :
                    nall += 1

            return True if (nall >= threshold* len(wordlist)) else False


        dfkall = pd.DataFrame()
        for com in keywordlist:
           com = str(com).lower().strip()
           ll  = str_split_no_quotes(com) ### nuclear fusion ---> 'nuclear', 'fusion',
           ll  = [ci for ci in ll if len(ci) > 2 ]

           dfk = dfcom[dfcom[colsearch].apply(lambda x: mmatch2(ll, x))]
           log(com, dfk)
           if len(dfk)>0:
               dfkall = pd.concat((dfkall, dfk))

        return dfkall


    def pd_find_reduce(dfcom, colsearch='com_extract', keywordlist=None, threshold=100.0, fullword_only=0):
        """
            # log("#### Doc Keyword filtering ###################################")
        # # def str_docontain(w, x):
        # #     x2 = str(x).lower()
        # #     for wi in w.split(" "):
        # #         if wi.lower() not in x2 : return False
        # #     return True
        # log("company_names: ", llg.query_tags['company_names'])
        # for w in llg.query_tags['company_names']:
        #     dftxt = dftxt[dftxt['com_extract'].apply(lambda x: str_docontain(w, x))]
        #     log(w, dftxt.shape)
        #     log(dftxt)


            for w in llg.query_tags['industry_tags']:
                w1 = str(w).lower().strip()
                for wi in w1.split(" "):
                    log(wi)
                    if len(dfi)<1:break
                    dfi = dfi[dfi['L_cat'].apply(lambda x: wi in str(x).lower().split(" "))]
                    log(dfi.shape)


        """
        if dfcom is None or len(dfcom)< 1:
            return dfcom

        if keywordlist is None or len(keywordlist) == 0:
            return dfcom

        keywordlist = keywords_clean(keywordlist)
        threshold   = threshold*0.01 if threshold > 10.0 else  threshold


        def mmatch2(wlist, text, threshold=1.0):
            if fullword_only == 1:
                text = {   xi for xi in  str(text).lower().strip().split(" ") if len(xi) >= 2 }
            else:
                text  = str(text).lower().strip()

            ### Match each sub keyword
            nall  = 0
            for wk in wlist:
                if text.startswith(wk) or text.endswith(wk) or f" {wk} " in text  :
                    nall += 1

            return True if (nall >= threshold* len(wlist)) else False


        dfk = dfcom
        for com in keywordlist:
           com = str(com).lower().strip()
           ll  = str_split_no_quotes(com) ### nuclear fusion ---> 'nuclear', 'fusion',
           ll  = [ci for ci in ll if len(ci) >= 2 ]

           dfk = dfk[dfk[colsearch].apply(lambda x: mmatch2(ll, x))]
           log(com, dfk)

        return dfk


    def pd_find_country(dfi, col_comid='com_id', country_list=None, ):
        """

            if len(llg.query_tags['country_tags'])>0:
                ticker = country_find(llg.query_tags['country_tags'][0])
                if ticker != "":
                    lcomid = dfcom2[ dfcom2['country'].str.contains(ticker)]['com_id'].values
                    dfi = dfi[dfi['com_id'].isin(lcomid)]


        """
        global dfcom2
        if dfi is None or len(dfi)< 1:
            return dfi

        if country_list is None or len(country_list) == 0:
            return dfi

        dfall = pd.DataFrame()
        for cntry_name in country_list:
            ticker = country_find(cntry_name)
            if ticker != "":
                lcomid = dfcom2[dfcom2['country'].str.contains(ticker)]['com_id'].values
                dfi2   = dfi[dfi[col_comid].isin(lcomid)]
                if len(dfi2) > 0:
                   dfall = pd.concat((dfi2, dfall))

        return dfall


    def pd_find_country_v2(dfi, col_country='country', country_list=None, ):
        """

            if len(llg.query_tags['country_tags'])>0:
                ticker = country_find(llg.query_tags['country_tags'][0])
                if ticker != "":
                    lcomid = dfcom2[ dfcom2['country'].str.contains(ticker)]['com_id'].values
                    dfi = dfi[dfi['com_id'].isin(lcomid)]


        """
        global dfcom2
        if dfi is None or len(dfi)< 1:
            return dfi

        if country_list is None or len(country_list) == 0:
            return dfi

        dfall = pd.DataFrame()
        for cntry_name in country_list:
            ticker = country_find(cntry_name)
            if ticker != "":
                dfi   = dfi[dfi[col_country].str.contains(ticker)]
                if len(dfi) > 0:
                   dfall = pd.concat((dfi, dfall))

        return dfall


    def keywords_clean(llist):
        lblock = {  'the', 'to', 'in', 'on', 'not', 'also', 'well', 'for', 'this', 'are', 'they', 'and', 'is',
                    'an', 'as', 'at', 'be', 'by', 'do', 'go', 'he', 'if', 'in', 'were',
                    'is', 'it', 'me', 'my', 'no', 'of', 'on', 'or', 'so', 'to', 'up', 'we',
                    'industry','industries', 'technical', 'tech', '&'
                 }

        llist2 = []
        for ti in llist:
            y    = ti.lower().strip()
            ynew = ""
            for yi in y.split(" "):
                if yi in lblock: continue
                ynew = ynew + yi + " "

            if len(ynew)>0:
                llist2.append(ynew[:-1])

        return llist2



if "######### RAG Embedding Search ############################################":
    def ranking_display(dftxt, query_tags=None):

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

        llm_model: str = "gpt-4o-mini",
        llm_max_tokens: int = 16000, istest=1,

        # llg.sparse_collection_name = llg.query_tags['data_source']
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



    def rag_reranking(dftxt, llg):
        log("#### Doc Re-Ranking #########################################")
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




if "######### Question Noramalization #########################################":
    def question_normalize(q):

      q = q.replace("Give me",  "Provide")
      q = q.replace("What are", "Describe")
      q = q.replace("What is",  "Describe")
      q = q.replace("Who",      "Provide ")
      q = q.replace("Provide details on", "Provide")
      q = q.replace("startup",            "disruptor")
      log("new query", q)

      return q


    def question_error_handle(query, query_tags):
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


    def question_rewrite(query, query_tags):
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




if "######### Question Entity Extraction #####################################":
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

        #display_tags:  list = Field(description="list of tags to describe how the results should be searched or analyzed ")


        country_tags:  list = Field(description="list of tags mentioning countries such : Israel, Canada, Japan ")



    def question_extract_NER(question="Summarize the news", llm_service="openai",
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

               industry_company_list

        """
        prompt = promptlist['query_analysis_01']
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
        dd['question0'] = question
        log('\n###### msg_dict_raw: ', dd)


        def cclean(ti):
            return str(ti).lower().replace("&", " ")

        #### Data Source  #############################################
        lsource = {'news': 'LZnews', 'industry':  'Eindustry'}
        ti = dd.get('data_source', 'industry')
        if 'activi' in ti:      ti = 'news'

        dd['data_source'] = lsource.get(ti, 'Eindustry')



        #### Post process date ########################################
        ll2 = []
        for ti in dd.get('date', ['2024']):
              ll2.append( ti.lower() )
        dd['date'] = ll2


        #### Post process date #######################################
        ll2 = []
        for ti in dd.get('country_tags', ['US']):
              ll2.append( ti.lower() )
        dd['country_tags'] = ll2

        #### Post process activity ###################################
        ll2 = []
        log(dd['activity_tags'] )
        for ti in dd.get('activity_tags', []):

           ti2 = NER_activity_norm(ti)

           if  'partner' in ti2 or 'collabo'  in ti2:
              ll2.append( 'partnership')

           elif  'acqui' in ti2 or 'merge'  in ti2:
              ll2.append( 'm and a')

           #elif  'activi'   in ti2:
           #   pass
           else:
              ll2.append(ti2)
           log(ti, ti2)

        ll2 = list(set(ll2))
        dd['activity_tags'] = ll2


        log("#### Industry ######################")
        ll2 = []
        for ti in dd.get('industry_tags', []):
           log(ti)
           ti2 = NER_industry_norm(ti, question)
           log(ti2)
           ll2 = ll2 + ti2

        ll2 = list(set(ll2))
        dd['industry_tags'] = ll2


        #### Company tags  ###################################
        ll2 = []
        for ti in dd.get('company_names', []):
              ll2.append( NER_company_norm(ti) )
        dd['company_names'] = ll2


        #### Context tags ###################################
        ll2 = []
        for ti in dd.get('context', []):
              ll2.append( NER_context_norm(ti) )
        dd['context'] = ll2


        #### Post process display ###################################
        #ll2 = []
        #for ti in dd.get('display_tags', ['most_recent']):
        #      ll2.append( cclean(ti) )
        #dd['display_tags'] = ll2

        # assert len(dd[ questionNER.keys()])>0, 'Missing keys'

        log("#### Task ################################")
        ll2 = []
        for ti in dd.get('task', ['summarize']):
           ti2 = NER_task_norm(ti, dd)
           ll2.append(ti2)
           log(ti, "-->", ti2)

        dd['task'] = ll2

        log("\n##### query_tags_dict:", dd)
        return dd



if "######### Question Entity normalization ##################################":
    def NER_task_norm(ti, dd: dict):
        """

               List of investment received by Anthropic.

               Funding list in Generative AI.

               List of investment round made by Amazon.



        """
        ti2 = ti.lower()
        query = str(dd.get("question0", "")).lower()
        def lend(w ):
          return len(dd.get(w, []))

        def str_contain_tags(key, ll)->bool:
            for ti2 in ll:
                ti2= str(ti2).lower()
                for ti in dd.get(key, []):
                    if ti2 in str(ti).lower():
                        return True
            return False

        def str_contain(word, ll)->bool:

            word = str(word).lower()
            for ti2 in ll:
                ti2= str(ti2).lower()
                if ti2 in word:
                        return True
            return False

        ti2 = ti2.replace('write report', 'report')
        ti2 = ti2.replace('what are', 'summarize')
        ti2 = ti2.replace('find company', 'find_company')
        ti2 = ti2.replace("provide", "describe")

        if lend('context') == 0:

            if ((lend('company_names') <= 1 and lend('industry_tags') <= 2)
                 and ('fund' in ti2 or 'invest' in ti2) and 'company' in ti2
                ):
                  log("####query:", query, ['investor', "provide", "give", "receive"] )
                  if str_contain(query, ['investor', "receive", "investments in", "investment in", "raise" ]):
                       ti2 = Tasks.invest_investorlist
                  else:
                       ti2 = Tasks.invest_receiverlist  ### startup


            elif lend('activity_tags')== 0 and lend('company_names') == 1 and lend('industry_tags') ==0 and str_contain(query, [' indu', ' segment']):
                ti2 = Tasks.com_industry_list


            elif lend('activity_tags')== 0 and lend('company_names') >= 1 and lend('industry_tags') ==0 and ' indus' not in query:
                ti2 = Tasks.find_company


            elif 'company' not in ti2 and lend('activity_tags')== 0  and lend('company_names')==0 and lend('industry_tags') >= 1:
                if 'market' in ti:
                    ti2 = Tasks.marketsize_industry
                else:
                    ti2 = Tasks.describe_industry

            elif lend('industry_tags') >= 0 and lend('company_names') == 2 and 'compare' in query :
                ti2 = Tasks.compare_activity

            elif ( (lend('industry_tags')>= 1 or lend('context') >= 1) and 'find_full_company_list' in ti)  :
                ti2 = Tasks.full_company_list


            elif lend('industry_tags') > 0 and lend('company_names') == 0 and lend('activity_tags') == 0 and "company" in ti:
                ti2 = Tasks.industry_company_list

            elif (lend('activity_tags') >= 1 and (lend('industry_tags') >= 1 or lend('company_names')>=1 ) and
                  str_contain_tags('activity_tags', ['partner', 'acqui', 'merge', 'product', 'activi', 'm and a', 'news' ])
                 )  :
                ti2 = Tasks.search_activity

            else:
                pass

            return ti2

        else:
            if  ((  lend('company_names') <= 1 and lend('industry_tags') <= 1 )
                    and ('fund' in ti2 or 'invest' in ti2) and 'company' in ti2
                ):
                  if str_contain(query, ['investor', "provide", "give", "receive"]):
                       ti2 = Tasks.invest_investorlist
                  else:
                       ti2 = Tasks.invest_receiverlist  ### startup


            elif (lend('activity_tags') >= 1 and (lend('industry_tags') > 0 or lend('company_names')>0 ) and
                  str_contain_tags('activity_tags', ['partner', 'acqui', 'merge', 'product', 'activi', 'news','m and a' ])
                  and lend('context') <= 2
                 )  :
                ti2 = Tasks.search_activity

            elif ( (lend('industry_tags')>= 1 or lend('context') >= 1) and 'find_full_company_list' in ti)  :
                ti2 = Tasks.full_company_list

            else:
                ti2 = Tasks.search_open

            return ti2


    def NER_activity_norm(ti):
        ll = """partnership
        funding
        m and a
        acquisition
        merger
        news
        activities
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
        strategy
        market size
        investment
        """
        ll = [xi.strip() for xi in ll.split("\n")]
        ti2 = ti.lower()
        ti2 = ti2.replace('investment', 'funding')
        ti2 = ti2.replace('investments', 'funding')
        ti2 = ti2.replace('activities', 'news')
        tlist = str_fuzzy_match_list(ti2, ll, cutoff=70.0)

        if len(tlist) < 1:
            return ""
        return ti2


    def NER_industry_norm(ti, query=""):

        y = ti.lower()

        #log(ti, query)
        #log('in quote',  f'"{ti.lower()}"' in query )
        if str_is_in_quotes(y, query.lower() ):
            ll =  [ f'"{y}"' ]
            log('double_quotes:', ll)
            return ll

        # y = y.replace(" tech ", " ").strip()
        y = y.replace("industries", " ").strip()
        y = y.replace("industry", " ").strip()
        y = y.replace('artificial intelligence', 'ai;artificial intelligence')
        y = y.replace('technology', 'tech')
        y = y.replace('genai', 'genai;generative ai')
        y = y.replace('healthcare', 'health')
        y = y.replace('electric cars', 'ev;transportation')
        y = y.replace('electric vehicule', 'ev;transportation')
        y = y.replace('ev', 'ev;transportation')
        y = y.replace('embodied ai', 'embodied ai;robot')
        y = str_replace_fullword(y, word="tech", newval=" ")
        # ti2 = ti2.replace('automobile', 'auto')

        y = [xi.strip() for xi in y.split(";")]
        return y


    def NER_company_norm(ti):
        y = ti.replace("Company", " " ).replace("company", " " ).replace("companies", " " )
        y = y.strip()
        return y


    def NER_context_norm(ti):
        y = ti.lower()
        y = str_replace_fullword(y, word="industry",   newval=" ")
        y = str_replace_fullword(y, word="industries", newval=" ")
        y = str_replace_fullword(y, word="technical",  newval=" ")
        y = str_replace_fullword(y, word="tech",      newval=" ")
        y = y.strip()
        return y






#############################################################################
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

    , 'summarize_03_bullet_noref': f"""You are a market researcher and leading fact checker writing a memo. 
  Provide an overview summary from below articles in 5 bullet points maximum.  
  Provide a market trend analysis  in 2 lines.
  Summary should only contain only facts extracted only from the articles.
  Take a big breath and re-read the above task question again.

 \n\nArticles\n\n:
 ```\n<multi_doc_string>\n```
 """

    , 'summarize_simple': f"""You are a market researcher. 
          Provide an an overview answer to this question, using the context below:
          <question>
    


 \n\nContext\n\n:
 ```\n<multi_doc_string>\n```
 """




    ,'report_00':        f"""You are a market researcher. Write a report of one page.
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


    ,'summarize_01':     f""" You are a businesss intelligence researcher writing a memo about <question>  for business executives.
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


    ,'P03':              f"""Write down a small introduction, replying to the question, Summarize each news article individually using bullets point and attach URL and article date.
     Make sure the summaries contain factual information extracted from the article.
     Write down a conclusion for the overall news articles and topics. \nArticles: \n```\n<multi_doc_string>\n```
     """


    ,'compare_01': f"""You are a market researcher writing a report for business executives
      on this question: "<question>".

      Provide a summary comparison between <company1> and <company2> on the topic: "<actitivity>", "<industry>".
      Use only below list of articles.

      Summary must follow this template:        
         **Overall summary**

         **Common Trend**: explain the common part in "<activity>" between the two companies.
         **Differences**:  explain the differences in "<activity>" between the two companies.
       
      * Important *:
         Summary must contain only facts extracted only from the articles below.
         Do not use your personal knowledge.
         Think step by step and fact check before answering.

      Take a big breath and re-read the above question again.
      
     \n\nArticles for company: <company1> \n\n:
     ```\n<multi_doc_string1>\n```


     \n\nArticles for company: <company2> \n\n:
     ```\n<multi_doc_string2>\n```

      """

    , 'compare_02': f"""You are a market researcher and lead fact checker writing a report for business executives.
    
  Provide an answer to this question   "<question>",  by comparing  "<company1>" and "<company2>".
  Use only below list of articles.

  Summary must follow this template:        
     **Overall summary**
     **Common Trend**:  explain the common trend  between the two companies.
     **Differences**:  explain the differences  between the two companies.

  * Important *:
     Summary must contain only facts extracted only from the articles below.
     Do not use your personal knowledge.
     Think step by step and fact check before answering.

  Take a big breath and re-read the above question again.

 \n\nCommon Articles \n\n:
 ```\n<multi_doc_string3>\n```


 \n\nArticles for company: <company1> \n\n:
 ```\n<multi_doc_string1>\n```


 \n\nArticles for company: <company2> \n\n:
 ```\n<multi_doc_string2>\n```





  """



    ,'question_answer_ext_01': f"""You are a leading market researcher and fact-checker writing a report for Business Executives.
      Provide a summary answer of this "<question>"
      using bullet points and using information extracted from below CONTEXT.
       
      * Important *:
         Summary must contain facts extracted only from the CONTEXT below.
         Do not use your personal knowledge.
         Be concise and  only provide facts from the CONTEXT below.
         Think step by step and Make sure you fact check and verify your answer with the CONTEXT below.
         Fact Accuracy of the answer is of upmost importance for Business Executives.


      Think step by step and re-read the above question again before providing the answer.
      
     ### CONTEXT :
     ```\n<multi_doc_string>\n```



      """


    ,'query_analysis_01': """
    Extract specific tags from the question below:
    ## question:
    {question1}


    Reread the question again:
    ## question:
    {question1}
    
    
    Make sure that the extracted tags are extracted from the sentence.
    Do not invent tags which is not in the question.

    ### Example of task:
      find_company
      describe_industry
      marketsize_industry
      provide_activities
      provide_acquisitions
      provide_partnerships      
      provide_news
      describe_news      
      compare_activity
      find_industry_company_list
      find_full_company_list      
      find_company_industry_list
      make_invest_funding_company_list
      describe     
      summarize
      unknown


    ### Example of context:
       expected CAGR 
       

    ### Example of activity_tags:
        partnership
        funding
        m and a
        acquisition
        merger
        news
        activities
        industry news
        product
        service launch
        earning
        listing
        expansion
        management
        approval
        regulation
        strategy
        market size
        investment

    
    
    ### Example of industry_tags :
    Generative AI Applications
    Generative AI Infrastructure
    Generative AI
    AI data center
    genAI
    Renewables
    Smart Factory
    Alternative Energy
    Additive Manufacturing
    Digital Twin
    Cybersecurity
    Supply Chain Tech
    Foundation Models
    Carbon Capture
    Carbon Management Software    
    AI Drug Discovery
    AI Drug
    Hydrogen Economy
    B2B SaaS
    Age Tech
    Remote Work
    Bio based Materials
    Humanoid Robots
    Financial Wellness
    Neobanks
    Longevity Tech
    Remote Work Infrastructure
    InsurTech Personal Lines
    Data Infrastructure
    EV Economy
    Retail Industry Robots
    Preventive Healthcare
    Auto Tech
    Identity Access Management
    Smart Building Technology
    Climate Risk Analytics
    Quantum Computing
    Workflow Automation Platforms
    Edge Computing
    Oil and Gas Tech
    Vertical Farming
    Satellites
    Last mile Delivery Automation
    Logistics Tech
    Waste Recovery Management
    FinTech Infrastructure
    Space Travel and Exploration
    Precision Medicine
    InsurTech: Commercial Lines
    Sustainable Aquaculture
    Customer Service Platforms
    Energy Optimization
    Nuclear fusion
        
    5g
    accelerator
    access
    additive
    advertising
    aerospace
    agri
    agricultural
    ai
    air
    aircraft
    airline
    airport
    alternative
    alternative living
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
    climate
    clinical trial
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
    electric vehicule
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
    fintech infrastructure
    fitness
    fleet
    food
    foods
    foundation
    foundation models
    freelancing
    gaming
    gas
    gene
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
    rail
    railway
    real estate
    reality
    recognition
    relationship
    remote work
    research
    residential
    resorts
    resource
    restaurant
    retail
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
    space
    space travel
    sport
    storage
    streaming
    supply chain
    sustainable
    system
    telecom
    testing
    textile
    therapeutic
    therapy
    tourism
    trading
    transformation
    transportation
    travel
    trial
    truck
    twin
    vaccine
    vehicle
    venture capital
    virtual reality
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

      ## question 1: provide NTT Data activities in data and in 2024 and in 2023
      ## answer 1: {{'reasoning': 'The question specifically asks for activities related to NTT Data in the year 2024', 'task': ['provide_news' ], 'date_period': 'in', 'date': ['2024', '2023'], 'company_names': ['NTT Data'], 'industry_tags': ['Data'], 'activity_tags': ['activities'], 'context': [], 'display_tags': ['most_recent', 'most_relevant'], 'country_tags': [] }}

     
      ## question 28:  Describe the recent news or activities in climate tech industry ?
         answer 28:  {{'reasoning': 'The question specifically asks for a description of recent news or activities in the climate tech industry, indicating a need for information gathering related to developments in this sector. The relevant tags extracted include the task of providing news and the industry tag related to climate tech.', 'task': ['provide_news'], 'date_period': '', 'date': [], 'company_names': [], 'industry_tags': ['climate tech'], 'activity_tags': ['news', 'activities'], 'context': ['recent'], 'country_tags': [] }}

      ## question 2: Provide list of companies in generative ai
         answer 2:  {{'reasoning': 'The question specifically asks for a list of companies involved in generative AI, indicating a need for information gathering in this specific industry. The relevant tags extracted include the task of listing companies and the industry tag related to generative AI.', 'task': ['industry_company_list'], 'date_period': '', 'date': [], 'company_names': [], 'industry_tags': ['generative ai'], 'activity_tags': [], 'context': [], 'country_tags': []}}


      ## question 3: What is the overall GenAI infrastructure strategy and roadmap ? 
      ## answer   3: {{'reasoning': 'The question is focused on describing the overall strategy and roadmap for GenAI infrastructure, which indicates a need for understanding the strategic planning in this specific area. The relevant tags extracted include the task of describing and the industry tag related to generative AI.', 'task': ['describe'], 'date_period': '', 'date': [], 'company_names': [], 'industry_tags': ['genai', 'generative ai'], 'activity_tags': [], 'context': ['overall', 'strategy and roadmap'], 'country_tags': [] }}

      ## question 4: What is the expected CAGR for the Brain-computer Interfaces market from 2024 to 2030 ?
      ## answer 4: {{'reasoning': 'The question specifically asks for the expected CAGR (Compound Annual Growth Rate) of the Brain-computer Interfaces market over a defined period, which indicates a focus on market growth metrics. The relevant tags extracted include the task of describing and the industry tag related to brain-computer interfaces.', 'task': ['describe'], 'date_period': 'between', 'date': ['2024', '2030'], 'company_names': [], 'industry_tags': ['brain-computer interfaces'], 'activity_tags': [], 'context': ["expected CAGR", "market" ], 'country_tags': [] }}
 
      ## question 5: Describe the projected market size of the global electric cars market by 2030  ?
      ## answer 5:  {{'reasoning': 'The question is focused on describing the projected market size of the Global Electric Cars Market by the year 2030, indicating a need for market analysis in this specific industry. The relevant tags extracted include the task of describing and the industry tag related to electric cars.', 'task': ['describe'], 'date_period': 'by', 'date': ['2030'], 'company_names': [], 'industry_tags': ['electric cars'], 'activity_tags': [], 'context': [ 'projected', 'market size', 'global'  ], 'country_tags': [] }}

      ## question 6: What is the impact of stringent emissions regulations on the Carbon Capture, Utilization & Storage (CCUS) market ?
         answer 6:  {{'reasoning': 'The question is focused on understanding the impact of stringent emissions regulations on the Carbon Capture, Utilization & Storage (CCUS) market, indicating a need for analysis in this specific area. The relevant tags extracted include the task of describing and the industry tag related to carbon capture and emissions regulations.', 'task': ['describe'], 'date_period': '', 'date': [], 'company_names': [], 'industry_tags': ['carbon capture'], 'activity_tags': ['stringent', 'emissions regulations' ], 'context': [], 'country_tags': [] }}


      ## question 7: Explain the strategy of Microsoft in generative ai through their partnerships ? Provide extra details. Only include partnerships from 2024 and in United States.
         answer 7:   {{'reasoning': "The question is focused on explaining Microsoft's strategy in generative AI through its partnerships, indicating a need for strategic analysis and collaboration insights. The relevant tags extracted include the task of describing, the industry tag related to generative AI, and the activity tag for partnerships.", 'task': ['describe'], 'date_period': '', 'date': ["2024"], 'company_names': ['Microsoft'], 'industry_tags': ['generative ai'], 'activity_tags': ['partnership'], 'context': ['strategy', 'through', 'their'], 'display_tags': ['Provide', 'extra details'], 'country_tags': ["United States"] }}


      ## question 8: Provide some details and summary about recent climate tech in 2024
         answer 8:  {{'reasoning': 'The question is focused on obtaining details and a summary about developments in climate technology in 2024, indicating a need for information gathering in this specific area. The relevant tags extracted include the task of providing information and the industry tag related to climate tech and in 2024.', 'task': ['provide', 'summarize'], 'date_period': '', 'date': ["2024"], 'company_names': [], 'industry_tags': ['climate'], 'activity_tags': [], 'context': ['details', 'summary', 'recent'], 'country_tags': []}}

      ## question 9: List of investment received by Anthropic.
         answer 9:  {{'reasoning': 'The question specifically asks for a list of investments received by Anthropic, indicating a need for information gathering related to funding. The relevant tags extracted include the task of listing investments and the company name Anthropic.', 'task': ['make_invest_funding_company_list'], 'date_period': '', 'date': [], 'company_names': ['Anthropic'], 'industry_tags': [], 'activity_tags': ['investment'], 'context': [], 'country_tags': [] }}

      ## question 10: Funding list in Generative AI in United States.
         answer 10:   {{'reasoning': 'The question specifically asks for a funding list related to Generative AI, indicating a need for information gathering in this specific industry. The relevant tags extracted include the task of listing funding and the industry tag related to generative AI.', 'task': ['make_invest_funding_company_list'], 'date_period': '', 'date': [], 'company_names': [], 'industry_tags': ['generative ai'], 'activity_tags': ['funding'], 'context': [], 'country_tags': ["United States"]}}
 
      ## question 11: List of investors in generative ai
         answer 11: {{'reasoning': 'The question specifically asks for a list of investors involved in generative AI, indicating a need for information gathering in this specific industry. The relevant tags extracted include the task of listing investors and the industry tag related to generative AI.', 'task': ['make_invest_funding_company_list'], 'date_period': '', 'date': [], 'company_names': [], 'industry_tags': ['generative ai'], 'activity_tags': [], 'context': [], 'country_tags': []}}

      ## question 12: Have companies developed any GenAI solutions in smart factory ? 
         answer 12:  {{'reasoning': 'The question specifically inquires about the development of GenAI solutions within the context of smart factories, indicating a focus on technological advancements in manufacturing. The relevant tags extracted include the task of describing and the industry tags related to generative AI and smart factories.', 'task': ['find_industry_company_list'], 'date_period': '', 'date': [], 'company_names': [], 'industry_tags': [ 'smart factory'], 'activity_tags': [], 'context': ['GenAI', 'solutions', 'develop' ], 'country_tags': [] }}

      ## question 13: Describe the leading companies offering AR surgical guidance solutions
         answer 13:  {{'reasoning': 'The question specifically asks for a description of leading companies that provide AR surgical guidance solutions, indicating a need for information gathering in this specific industry. The relevant tags extracted include the task of describing and the industry tag related to AR surgical guidance.', 'task': ['find_industry_company_list'], 'date_period': '', 'date': [], 'company_names': [], 'industry_tags': ['AR surgical guidance'], 'activity_tags': [], 'context': ['leading' 'companies', 'solutions' ], 'country_tags': [] }}

      ## question 14: find smith company
         answer 14: {{'reasoning': "The question is focused on finding a company containing 'smith'. The relevant tags extracted include the task of finding a company, called 'smith' .", 'task': ['find_company'], 'date_period': '', 'date': [], 'company_names': ['nephew smith', ], 'industry_tags': [], 'activity_tags': [], 'context': [], 'country_tags': [], }}

      ## question 15: List of industries for NTT data.
         answer 15:  {{'reasoning': 'The question specifically asks for a list of industries related to NTT Data, indicating a need for information gathering about the sectors in which the company operates. The relevant tags extracted include the task of listing and the company name NTT Data.', 'task': ['find_company_industry_list'], 'date_period': '', 'date': [], 'company_names': ['NTT Data'], 'industry_tags': [], 'activity_tags': [], 'context': [], 'country_tags': []}}

      ## question 16: which company develops CAR-T therapies ?
         answer 16: {{'reasoning': 'The question specifically asks for information about companies that develop CAR-T therapies, indicating a focus on the biotechnology industry. The relevant tags extracted include the task of finding a company and the industry tag related to CAR-T therapies.', 'task': ['search_open'], 'date_period': '', 'date': [], 'company_names': [], 'industry_tags': [], 'activity_tags': [], 'context': [ 'develop', 'CAR-T', 'therapies'], 'country_tags': [] }}

      ## question 17: Market size of cybersecurity industry ?
         answer 17:  {{'reasoning': 'The question specifically asks for the market size of the cybersecurity industry, indicating a focus on market analysis within this sector. The relevant tags extracted include the task of describing market size and the industry tag related to cybersecurity.', 'task': ['describe'], 'date_period': '', 'date': [], 'company_names': [], 'industry_tags': ['cybersecurity'], 'activity_tags': ['market size'], 'context': [], 'country_tags': [], }}

      ## question 18: What are companies offering GPUaaS solutions ?
         answer 18: {{'reasoning': 'The question specifically asks for a description of companies that offer GPUaaS solutions, indicating a need for information gathering in this specific industry. The relevant tags extracted include the task of describing and the industry tag related to GPUaaS.', 'task': ['find_industry_company_list'], 'date_period': '', 'date': [], 'company_names': [], 'industry_tags': ['GPUaaS'], 'activity_tags': [], 'context': ['solutions', 'offering' ], 'country_tags': [] }}

      ## question 19: Explain the drivers for Web3 industry
         answer 19:   {{'reasoning': 'The question specifically asks for an explanation of the drivers for the Web3 industry, indicating a need for understanding the factors influencing this sector. The relevant tags extracted include the task of explaining and the industry tag related to Web3.', 'task': ['explain'], 'date_period': '', 'date': [], 'company_names': [], 'industry_tags': ['Web3'], 'activity_tags': [], 'context': ['drivers'], 'country_tags': [], }}

      ## question 20: Provide some insights on sustainability
         answer 20 : {{'reasoning': 'The question seeks insights on sustainability, indicating a need for information gathering in this specific area. The relevant tags extracted include the task of providing insights and the industry tag related to sustainability.', 'task': ['provide'], 'date_period': '', 'date': [], 'company_names': [], 'industry_tags': ['sustainability'], 'activity_tags': [], 'context': ['insight'], 'country_tags': []}}

      ## question 21: Who are the key players in the Generative AI infrastructure industry ?
         answer 21: {{'reasoning': 'The question specifically asks for the key players in the Generative AI infrastructure industry, indicating a need for information gathering about the companies involved in this sector. The relevant tags extracted include the task of finding companies and the industry tag related to Generative AI infrastructure.', 'task': ['find_industry_company_list'], 'date_period': '', 'date': [], 'company_names': [], 'industry_tags': ['Generative AI infrastructure'], 'activity_tags': [], 'context': ['key' 'players'], 'country_tags': [] }}
 
      ## question 22: explain the business model of companies in Food Waste industry
         answer 22: {{'reasoning': 'The question specifically asks for an explanation of the business model of companies in the food waste industry, indicating a need for understanding the operational and financial strategies within this sector. The relevant tags extracted include the task of explaining and the industry tag related to food waste.', 'task': ['explain'], 'date_period': '', 'date': [], 'company_names': [], 'industry_tags': ['Food Waste'], 'activity_tags': [], 'context': ["business model", "companies" ], 'country_tags': [] }}

      ## question 23: Provide list of startup companies and their funding in "AI Agent" industry and provide details on their product ?
         answer 23:  {{'reasoning': "The question specifically asks for a list of startup companies in the 'AI Agent' industry along with their funding details and product descriptions. This indicates a need for information gathering related to companies, funding, and product details in the specified industry.", 'task': ['make_invest_funding_company_list'], 'date_period': '', 'date': [], 'company_names': [], 'industry_tags': ['AI Agent'], 'activity_tags': ['funding', 'product', 'startup' ], 'context': [], 'country_tags': []}}

      ## question 24: Compare Quantinuum and Rigetti Computing on funding and other important product metrics.
         answer 24:  {{'reasoning': 'The question is focused on comparing Quantinuum and Rigetti Computing in terms of funding and other important product metrics, indicating a need for a detailed analysis of these two companies. The relevant tags extracted include the task of comparison and the company names involved.', 'task': ['compare_activity'], 'date_period': '', 'date': [], 'company_names': ['Quantinuum', 'Rigetti Computing'], 'industry_tags': [], 'activity_tags': ['funding', 'product metrics'], 'context': [], 'country_tags': [] }}

      ## question 27: Describe the investments in auto tech or healthcare industry in 2024  and in United States ?
         answer 27: {{'reasoning': 'The question specifically asks for a description of investments in the auto tech industry or healthcare for the year 2024 and in United States, indicating a need for information gathering related to funding in this sector. The relevant tags extracted include the task of describing list of investment and the industry tag related to auto tech and healthcare, country tag is United States and year is 2024 ', 'task': ['make_invest_funding_company_list'], 'date_period': 'in', 'date': ['2024'], 'company_names': [], 'industry_tags': ['auto tech', 'healthcare'], 'activity_tags': ['investment'], 'context': [], 'country_tags': ['United States'] }}
  
      ## question 28: List of companies in alternative data and in united states
         answer 28:  {{'reasoning': 'The question specifically asks for a list of companies involved in alternative data within the United States, indicating a need for information gathering in this specific industry and geographical location. The relevant tags extracted include the task of listing companies, the industry tag related to alternative data, and the country tag for the United States.', 'task': ['find_industry_company_list'], 'date_period': '', 'date': [], 'company_names': [], 'industry_tags': ['alternative data'], 'activity_tags': [], 'context': [], 'country_tags': ['United States'] }}

      ## question 29:  List of companies in united states 
         answer 29:  {{'reasoning': 'The question specifically asks for a list of companies located in the United States, indicating a need for information gathering related to businesses in that geographical area. The relevant tags extracted include the task of finding companies and the country tag for the United States.', 'task': ['find_industry_company_list'], 'date_period': '', 'date': [], 'company_names': [], 'industry_tags': [], 'activity_tags': [], 'context': [], 'country_tags': ['United States'] }}
     
    """



}







#############################################################################
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





if "########## Utils #####################################################":

    def str_is_in_quotes(ss, txt):
        """
            # Example usage:
            txt = 'This is a "sample" text with "quoted" words'
            print(is_in_quotes("sample", txt))  # True
            print(is_in_quotes("text", txt))  # False

        :param ss:
        :param txt:
        :return:
        """
        return f'"{ss}"' in txt or f"'{ss}'" in txt


    def str_split_no_quotes(s):
        """
            # Example usage
            s = 'one "two three" four'
            result = split_ignore_quotes(s)
            print(result)  # ['one', '"two three"', 'four']

        :param s:
        :return:
        """
        import re
        ll = re.findall(r'[^\s\'\"]+|\'[^\']*\'|\"[^\"]*\"', s)
        ll = [xi.replace('"', '') for xi in ll ]
        return ll


    def country_find(x):
        """
                dd = {}
                for key, val in country_to_code.items():
                    dd[key.lower()]=val
        """
        country_to_code = {'india': 'IND', 'united states': 'USA', 'japan': 'JPN', 'france': 'FRA', 'china': 'CHN',
                           'united kingdom': 'GBR', 'finland': 'FIN', 'germany': 'DEU', 'switzerland': 'CHE',
                           'ireland': 'IRL', 'sweden': 'SWE', 'hong kong': 'HKG', 'israel': 'ISR', 'taiwan': 'TWN',
                           'south korea': 'KOR', 'mexico': 'MEX', 'canada': 'CAN', 'russia': 'RUS', 'spain': 'ESP',
                           'netherlands': 'NLD',
                           'usa': 'USA',
                           'us': 'USA',
                           'australia': 'AUS', 'liechtenstein': 'LIE', 'norway': 'NOR', 'singapore': 'SGP',
                           'brazil': 'BRA', 'greece': 'GRC', 'denmark': 'DNK', 'chile': 'CHL', 'south africa': 'ZAF',
                           'argentina': 'ARG', 'luxembourg': 'LUX', 'united arab emirates': 'ARE', 'belgium': 'BEL',
                           'hungary': 'HUN', 'qatar': 'QAT', 'poland': 'POL', 'italy': 'ITA', 'austria': 'AUT',
                           'philippines': 'PHL', 'turkey': 'TUR', 'croatia': 'HRV', 'saudi arabia': 'SAU',
                           'nigeria': 'NGA', 'portugal': 'PRT', 'jamaica': 'JAM', 'malaysia': 'MYS', 'pakistan': 'PAK',
                           'kuwait': 'KWT', 'thailand': 'THA', 'sri lanka': 'LKA', 'new zealand': 'NZL',
                           'indonesia': 'IDN', 'venezuela': 'VEN', 'latvia': 'LVA'}

        res = str_fuzzy_match_list(x, list(country_to_code.keys()), cutoff=80.0)
        if len(res) > 0:
            ticker = country_to_code[res[0]]
            return ticker
        return ""


    def str_replace_fullword(text, word, newval):
        import re
        pattern = rf'\b{re.escape(word)}\b|\b{re.escape(word)}$'
        return re.sub(pattern, newval, text)


    def markdown_to_html(markdown_text):
        import markdown2
        try:
            return markdown2.markdown(markdown_text, extras=['fenced-code-blocks', 'tables', 'break-on-newline'])
        except Exception as e:
            log(e)
            return markdown_text

    def color_get_random():
        import seaborn as sns
        # colors = sns.color_palette('husl', n_colors=20)

        # colors = [
        #     '#e6194B',  # Red
        #     '#3cb44b',  # Green
        #     '#ffe119',  # Yellow
        #     '#4363d8',  # Blue
        #     '#f58231',  # Orange
        #     '#911eb4',  # Purple
        #     '#42d4f4',  # Cyan
        #     '#f032e6',  # Magenta
        #     '#bfef45',  # Lime
        #     '#fabed4',  # Pink
        #     '#469990',  # Teal
        #     '#dcbeff',  # Lavender
        #     '#9A6324',  # Brown
        #     '#fffac8',  # Beige
        #     '#800000',  # Maroon
        #     '#aaffc3',  # Mint
        #     '#808000',  # Olive
        #     '#ffd8b1',  # Apricot
        #     '#000075',  # Navy
        #     '#a9a9a9'  # Grey
        # ]
        colors = [
            '#1f77b4',  # blue
            '#ff7f0e',  # orange
            '#2ca02c',  # green
            '#d62728',  # red
            '#9467bd',  # purple
            '#8c564b',  # brown
            '#e377c2',  # pink
            '#7f7f7f',  # gray
            '#bcbd22',  # yellow-green
            '#17becf'  # cyan
        ]

        ix = random.randint(0, len(colors) - 1)
        return colors[ix]


    def np_unique(ll):
        ll2 = []
        for xi in ll:
            if xi not in ll2:
                ll2.append(xi)
        return ll2

    def str_replace_punctuation(text, val=" "):
        import re
        return re.sub(r'[^\w\s]', val, text)


    def str_split_right_first(s: str, charlist=None) -> tuple:
        charlist = [ "|", "-" ] if charlist is None else charlist
        imax= -1
        s = str(s)
        for ci in charlist:
            ix = s.rfind(ci)
            if ix != -1:
                imax = max(imax, ix)

        if -1 < imax < len(s) :
            log(imax)
            return s[:imax], s[imax + len(ci):]

        return s, ""


    def str_split_right_last(s: str, charlist=None) -> tuple:
        charlist = [ "|", "-" ] if charlist is None else charlist
        imin= 999999999
        s = str(s)
        for ci in charlist:
            ix = s.rfind(ci)
            if ix != -1:
                imin = min(imin, ix)

        if -1 < imin < len(s) :
            log(imin)
            return s[:imin], s[imin + len(ci):]

        return s, ""


    def str_contain_fuzzy_list(word, wlist, threshold=80):
        """
        Check if word fuzzy matches any string in wlist using rapidfuzz
        """
        from rapidfuzz import fuzz
        w0 = str(word.lower())
        return any(fuzz.partial_ratio(w0, w.lower()) >= threshold for w in wlist)


    def str_contain_fuzzy_wsplit(word, sentence, sep=" ", threshold=80):
        """
        Check if word fuzzy matches any string in wlist using rapidfuzz
        """
        from rapidfuzz import fuzz
        w0 = str(word.lower())
        wlist = str(sentence).lower().split(sep)
        return any(fuzz.partial_ratio(w0, w.lower()) >= threshold for w in wlist)


    def str_match_fuzzy(word, word2="", sep=" ", threshold=80):
        """
        Check if word fuzzy matches any string in wlist using rapidfuzz
        """
        from rapidfuzz import fuzz
        w0 = str(word.lower())
        w2 = str(word2).lower()
        return fuzz.partial_ratio(w0, w2) >= threshold


    def json_save2(llg, dirout):
        y,m,d,h = date_now(fmt="%Y-%m-%d-%H").split("-")
        ts      = date_now(fmt="%y%m%d_%H%M%s")
        json_save(llg.to_dict(), dirout + f"/year={y}/month={m}/day={d}/hour={h}/chat_{ts}.json" )


    def str_norm(text):
        return str(text).lower().translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation)))


    def str_find(x:str,x2:str, istart=0):
        try:
            i1 = x.find(x2, istart)
            return i1
        except Exception as e:
            return -1


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


    def do_exists(var_name):
        return var_name in locals() or var_name in globals()


    def to_int(x, val=-1):
        try:
            return int(x)
        except Exception as e:
            return val



    def word_ng_generation():
        import nltk
        from nltk.corpus import words
        from nltk.tag import pos_tag

        # Download required NLTK data
        nltk.download('words')
        nltk.download('averaged_perceptron_tagger')

        def get_grammar_words():
            word_list = words.words()
            # Get words with grammar tags
            tagged_words = pos_tag(word_list)

            grammar_words = {
                'DT': [],  # Determiners
                'IN': [],  # Prepositions
                'CC': [],  # Coordinating conjunctions
                'PRP': [],  # Personal pronouns
                'WDT': [],  # Wh-determiners
                'WP': [],  # Wh-pronouns
                'WRB': []  # Wh-adverbs
            }

            grammar = []
            for word, tag in tagged_words:
                if tag in grammar_words and len(grammar_words[tag]) <1000:  # Limit to 50 words per category
                    grammar.append(word.lower())

            return grammar

        grammar_words = get_grammar_words()



if "########## External Tools ############################################":
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






#######################################################
KEYW = Box({})
KEYW.industry= """
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
    Carbon Capture
    AI Drug Discovery
    Hydrogen Economy
    B2B SaaS Management Platforms
    Age Tech
    Remote Work Tools
    Bio-based Materials
    Humanoid Robots
    Financial Wellness Tools
    Neobanks
    Longevity Tech
    Remote Work Infrastructure
    InsurTech: Personal Lines
    Data Infrastructure & Analytics
    EV Economy
    Retail Industry Robots
    Preventive Healthcare
    Auto Tech
    Identity & Access Management
    Smart Building Technology
    Climate Risk Analytics
    Carbon Management Software
    Quantum Computing
    Workflow Automation Platforms
    Edge Computing
    Oil & Gas Tech
    Vertical Farming
    Next-gen Satellites
    Last-mile Delivery Automation
    Logistics Tech
    Waste Recovery & Management Tech
    FinTech Infrastructure
    Space Travel and Exploration Tech
    Precision Medicine
    InsurTech: Commercial Lines
    Sustainable Aquaculture
    Customer Service Platforms
    Energy Optimization & Management Software
    Digital Wellness
    Threat Prevention Toolchain
    Smart Farming
    Passenger eVTOL Aircraft
    Military Tech
    Smell Tech
    Sales Engagement Platforms
    Extended Reality
    Crop Biotech
    Metaverse Platforms
    Natural Language Processing Tools
    HR Tech
    Content Creation Tools
    Automated Stores
    Buy Now, Pay Later
    Hospital-at-Home
    Mental Health Tech
    EdTech: K-12
    Capital Markets Tech
    Decentralized Finance (DeFi)
    Conservation Tech
    Beauty Tech
    Cell & Gene Therapy
    Cloud-native Tech
    Truck Industry Tech
    Digital Privacy Tools
    Telehealth
    Alternative Ingredients
    DevOps Toolchain
    Next-gen Medical Devices
    Natural Fertilizers
    Next-gen Displays
    Retail Trading Infrastructure
    Psychedelic Medicine
    Ecommerce Platforms
    Digital Humans
    EdTech: Corporate Learning
    Hospital Management
    Mining Tech
    Regenerative Agriculture Platforms
    Commercial PropTech
    Higher EdTech
    Health Benefits Platforms
    Smart Security Tech
    Functional Nutrition
    Serverless Computing
    Biopesticides
    P2P Financial Platforms
    Next-gen Semiconductors
    Next-gen Email Security
    Clinical Trial Technology
    InsurTech: Infrastructure
    SME CRM
    Digital Retail Enhancement Platforms
    Cold Chain Innovation
    Contract Management Tools
    Plant-based Dairy & Egg
    Healthcare Resourcing Platforms
    Cloud Optimization Tools
    Wearable Tech
    Facial Recognition
    Human Gene Editing
    Travel Tech
    Smart Homes: Energy & Water Solutions
    Marketing Automation
    Residential PropTech
    Neurostimulation Tech
    Plant-based Meat
    Hygiene Tech
    Biometric Payments
    Cell-cultured Meat
    Alternative Data
    Cyber Insurance
    Enterprise Blockchain Solutions
    Clinical Decision Support Systems
    Smart Packaging Tech
    Commercial Drone Tech
    Neuromorphic Computing
    Low-code Platforms
    Creator Economy
    Shipping Tech
    Convenience Foods
    Cannabis
    Online Freelancing Platforms
    Machine Learning Infrastructure
    Next-gen Private Mobile Networks
    Online Food Delivery
    Connected Fitness
    Sustainable Finance
    Hospital Interoperability
    Bioprinting
    Business Expense Management
    Prefab Tech
    Alternative Living
    Restaurant Industry Robotics
    Sports Tech
    Web3 Ecosystem
    Infectious Disease Tech
    Functional Ingredients
    Cloud Kitchens
    No-code Software
    Legal Tech
    Brain-computer Interfaces
    Pollution Management Tech
    Fertility Tech
    Large-molecule Therapeutics
    Smart Mobility Information
    Furniture Tech
    Animal Therapeutics
    Food Waste
    Digital Wallets
    Shared Mobility
    Esports
    Pet Care Tech
    Livestock Biotech
    Initial
    Biosimilars
    Construction Tech
    Tissue Targeting Therapeutics
    Automated Content Moderation
    Custom hub mock: Consumer lending
    Custom Hub Mock: The Mills Fabrica
    NFT
    Smart Packaging
    Next-gen Environmental Services
    Media Tech
    Social Commerce
    Cryptocurrencies
    Radiopharmaceuticals
    RNA Therapeutics
"""




########################################################################################
if __name__ == '__main__':
    import fire
    fire.Fire()






########################################################################################
def zzold_task_compare_activity_old(llg, topk=1):
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


        What are the advantages of Tesla electric cars compared to Toyota electric cars ?



    """
    log("########## Start task_compare_activity  ############################")
    llg.llm_service = "openai"
    llg.llm_model = "gpt-4o-mini"
    llg.llm_max_tokens = 4000
    query = llg.query2

    # dout = jload_cache('ui/static/answers/compare_activity/data.json' )
    dout = jload_cache('ui/static/answers/report_v1/data.json')

    llg.llm_prompt_id = "compare_01"  # "summarize_01"

    if len(llg.query_tags['company_names']) < 2:
        return msg_no_enough

    llg2 = deepcopy(llg)
    llg1 = deepcopy(llg)
    company1 = llg1.query_tags['company_names'][0]
    company2 = llg2.query_tags['company_names'][-1]
    activity = ",".join(llg.query_tags['activity_tags'])
    industry = ",".join(llg.query_tags['industry_tags'])
    tsk0 = ",".join(llg.query_tags['task'])
    log("tasks: ", tsk0)

    llg1.query_tags['company_names'] = [company1]
    llg2.query_tags['company_names'] = [company2]

    log("########## Start fun_search_activity  ###########################")
    dftxt1, multi_doc_str1 = fun_search_activity(llg1, output_merge_str=1)

    dftxt2, multi_doc_str2 = fun_search_activity(llg2, output_merge_str=1)

    if len(dftxt2) < 1 or len(dftxt1) < 1:
        return msg_no_enough

    log("\n#######  LLM :Summarize #######################################")
    llm_1 = LLM(llg.llm_service, llg.llm_model, max_tokens=llg.llm_max_tokens)

    if 'report' in tsk0:
        llm_prompt_id = "report_compare_01"

    log("Prompt used:", llg.llm_prompt_id)
    ptext = promptlist[llg.llm_prompt_id]
    ptext = ptext.replace("<question>", query)
    ptext = ptext.replace("<activity>", activity)

    ptext = ptext.replace("<company1>", company1)
    ptext = ptext.replace("<company2>", company2)

    ptext = ptext.replace("<multi_doc_string1>", multi_doc_str1)
    ptext = ptext.replace("<multi_doc_string2>", multi_doc_str2)
    llg.prompt = ptext

    log("######## LLM call #####################################")
    llm_json = llm_1.get_save_sync(prompt=ptext, output_schema=None, dirout=None)
    # log(llm_json)
    msg = llm_json["choices"][0]["message"]["content"]
    msg2 = markdown_to_html(msg)
    llg.msg_answer = msg
    llg.msg_display = msg2

    dout['html_tags']["summary"] = msg2

    log("######## Add Article sources #########################")
    dd = [{"title": doc['title'],  ### Remove extra URL
           "url": doc['url'],
           # "date":  doc['date'],
           # "text":  doc['text']
           }
          for ii, doc in dftxt.iloc[:topkall, :].iterrows()
          ]
    dout['html_tags']["source_list"] = dd

    log("######## Add Article sources #########################")
    dd = [{"title": doc['title'], "url": doc['url'], "date": doc['date'], "text": doc['text']}
          for ii, doc in dftxt1.iloc[:topk, :].iterrows()]
    dout['html_tags']["activity_list1"] = dd

    dd = [{"title": doc['title'], "url": doc['url'], "date": doc['date'], "text": doc['text']}
          for ii, doc in dftxt2.iloc[:topk, :].iterrows()]
    dout['html_tags']["activity_list2"] = dd

    log("##### Final html ####################################")
    llg.msg_answer = dout
    json_save2(llg, llg.dirout)
    log(dout['html_tags'].keys())

    return dout





def fun_search_edge_score_vold(dfragall, llg, cols=None):
    from rag.engine_emb import pd_search_keywords_fuzzy

    cols = [ 'text_chunk', 'url', 'text_html', 'L_cat','title', 'L0_catnews', 'com_extract'  ] if cols is None else cols

    llist = query_expand_clean(llg.query2)

    dfw = deepcopy(dfragall[cols])


    #### Score Calc  ##############################
    dfw = pd_search_keywords_fuzzy(dfw, 'text_chunk',  keywords=llist, tag='_txt', cutoff=75)
    dfw = pd_search_keywords_fuzzy(dfw, 'title',       keywords=llist, tag='_tit', cutoff= 75)

    dfw = pd_search_keywords_fuzzy(dfw, 'L_cat',       keywords=llg.query_tags['industry_tags']  ,tag='_ind', cutoff=90)
    dfw = pd_search_keywords_fuzzy(dfw, 'L0_catnews',  keywords=llg.query_tags['activity_tags']  ,tag='_act', cutoff=80)

    dfw = pd_search_keywords_fuzzy(dfw, 'com_extract', keywords=llg.query_tags['company_names']  ,tag='_com', cutoff=70)

    dfw['score'] = dfw.apply(lambda x: x['score_txt'] + 0.2*x['score_tit'] + 1.2*x['score_ind'] + 0.5*x['score_act']  + x['score_com']   , axis=1   )
    dfw          = dfw.sort_values('score', ascending=0)


    dftxt = dfw[ dfw['score'] > 0.7  ]
    return dftxt



def zzthot_prompting(context, question):
    # Stage 1: Analysis
    analysis_prompt = f"""
    Context: {context}
    Question: {question}
    Walk me through this context in manageable parts step by step, summarizing and analyzing as we go.
    """
    analysis = llm(analysis_prompt)

    # Stage 2: Final Answer
    answer_prompt = f"""
    Based on this analysis:
    {analysis}

    Provide the final answer to: {question}
    """
    final_answer = llm(answer_prompt)

    return final_answer


"""

You are an expert fact-checker with deep expertise in detecting misinformation. Your task is to:
1. Only include information explicitly supported by the retrieved documents
2. Cite specific sources for each claim
3. Express uncertainty when evidence is incomplete
4. Focus on accuracy over comprehensiveness


1. Generate initial summary
2. Create verification questions about key claims
3. Answer each verification question using only retrieved documents
4. Revise summary to only include verified claims
5. Explicitly state if any claims cannot be verified




“ You Mike, a world renown specialist in the topic. You have been passionate about this topic your entire life, went to Stanford to study, and now have dedicated your life’s work to topic. 



Think step by step. Consider my question carefully and think of the academic or professional expertise of someone that could best answer my question. You have the experience of someone with expert knowledge in that area. 
Be helpful and answer in detail while preferring to use information from reputable sources.

"""


def zztask_indus_comlist_old(llg):
    """


    """
    log("########## Start task_indus_comlist  #####################")
    global ddata
    dout = jload_cache('ui/static/answers/report_v1/data.json')

    log("##### Overview ###############################################")
    dfi = deepcopy(ddata['indus_comlist'])
    for w in llg.query_tags['industry_tags']:
        w1 = str(w).lower().strip()
        for wi in w1.split(" "):
            log(wi)
            dfi = dfi[dfi['L_cat'].apply(lambda x: wi in str(x).lower().split(" "))]
            log(dfi, dfi.shape)

    if len(dfi) < 1:
        ddict = task_search_ext(llg, )
        return ddict
        ## return msg_no_enough

    log(dfi)
    dfi['coms'] = dfi['coms'].apply(lambda x: [(name, com_getid(name)) for name in x.split(";")])
    dfi = dfi.explode('coms')
    dfi['com_name'] = dfi['coms'].apply(lambda x: x[0])
    dfi['com_id'] = dfi['coms'].apply(lambda x: x[1])
    dfi = dfi.drop_duplicates(['com_name'])
    dfi = dfi.sort_values(['L_cat', 'com_name'])
    dfi['url'] = dfi['com_id'].apply(lambda x: f"https://eeddge.com/companies/{x}")

    ss = ""
    lcat = ""
    for k, x in dfi.iterrows():
        if lcat != x['L_cat']:
            if len(ss) > 0:
                ss = ss + """</ul> <hr> \n"""

            ss = ss + f"""<h3><b>{x['L3_cat'].capitalize()} </b></h3> <ul> """
        else:
            ss = ss + f""" <li> <a href="{x['url']}">{x['com_name']}</a> </li> """
        lcat = x['L_cat']

    ss = ss + """</ul> \n"""

    dout['html_tags']["summary"] = ss
    dout['html_tags']["source_list"] = None
    dout['html_tags']["question_list"] = []

    log("##### Final html ####################################")
    llg.msg_answer = dout
    json_save2(llg, llg.dirout)
    return dout




def zztask_invest_investorlist_old(llg):
    """


    """
    log("########## Start task_com_investlist  #####################")
    global dfinvest
    dout = jload_cache('ui/static/answers/report_v1/data.json')


    log("##### Overview ############################################")
    from utils.util_text import str_fuzzy_match_is_same

    if len(llg.query_tags['company_names']) > 0:
        comtag = llg.query_tags['company_names'][0].lower()
        dfi    = dfinvest[ dfinvest['receiver_name'].apply(lambda x : str_fuzzy_match_is_same(comtag, str(x).lower(), 90 )) ]
        dfi = dfi.sort_values(['receiver_name', 'date'], ascending=[1,1])

    elif   len(llg.query_tags['industry_tags']) > 0:
        Ltag =  llg.query_tags['industry_tags'][0]
        dfi    = dfinvest[ dfinvest['L_cat'].apply(lambda x :  Ltag in str(x).lower() ) ]
        dfi = dfi.sort_values(['receiver_name', 'date'], ascending=[1,1])
    else:
        return msg_no_enough

    log(dfi, dfi.shape)
    if len(dfi) < 1:
        return msg_no_enough


    cols = [ 'receiver_name' ,  'investor_name', 'date', 'funding_stage_name', 'amount',
             'total_funding', 'L3_cat',
           ]   ##    'segment_name' , 'edge_link',

    dfi = dfi[cols]     # One
    for ci in ['amount', 'total_funding'] :
       dfi[ci] = dfi[ci].apply(lambda x: '{:,.3f}'.format(x))

    dfi.columns = [ ]

    ss_html = dfi[cols].to_html(classes='table01', index=False)


    ss = ""
    dfi2 = dfi.groupby(['receiver_name',]).agg({'amount': 'sum'}).reset_index()
    dfi2 = dfi2.values
    for vv in dfi2:
        ss = ss + f"{vv[0].capitalize()} received {vv[1]}  USD  in total funding.<br>"

    ss = ss  + "<br>" + ss_html
    dout['html_tags']["summary"] = ss

    dout['html_tags']["source_list"] = None
    dout['html_tags']["question_list"] = []

    log("##### Final html ####################################")
    llg.msg_answer = dout
    json_save2(llg, llg.dirout)
    return dout




def zztask_invest_receiverlist_old(llg):
    """


    """
    log("########## Start task_invest_receiverlist  ##################")
    global dfinvest
    dout = jload_cache('ui/static/answers/report_v1/data.json')


    log("##### Overview ###############################################")
    if len(llg.query_tags['company_names']) > 0:
        comtag = llg.query_tags['company_names'][0].lower()
        dfi    = dfinvest[ dfinvest['investor_name'].apply(lambda x :  comtag in str(x).lower() ) ]
        dfi = dfi.sort_values(['investor_name', 'date'], ascending=[1,1])

    elif   len(llg.query_tags['industry_tags']) > 0:
        Ltag =  llg.query_tags['industry_tags'][0]
        dfi    = dfinvest[ dfinvest['L_cat'].apply(lambda x :  Ltag in str(x).lower() ) ]
        dfi = dfi.sort_values(['receiver_name', 'date'], ascending=[1,1])
        tot_amt = dfi['amount'].sum()

    else:
        return msg_no_enough

    log(dfi, dfi.shape)
    if len(dfi) < 1:
        return msg_no_enough


    cols = [   'investor_name', 'receiver_name' , 'date', 'funding_stage_name', 'amount', 'total_funding', 'L3_cat', ]

    dfi = dfi[cols]
    dfi.columns =  [   'Investor', 'Receiver' , 'date', 'funding stage', 'amount', 'Total funding', 'Industry', ]
    ss_html = dfi.to_html(classes='table01', index=False)


    dout['html_tags']["summary"] = ss_html
    dout['html_tags']["source_list"] = None
    dout['html_tags']["question_list"] = []

    log("##### Final html ####################################")
    llg.msg_answer = dout
    json_save2(llg, llg.dirout)
    return dout




def task_search_activity_old(llg, topk=5):
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
    llm_service    = "openai"
    llm_model      = "gpt-4o-mini"
    llm_max_tokens = 8000
    query = llg.query2
    dout = jload_cache('ui/static/answers/search_activity/data.json' )

    log("########## Start task_search_activity  ############################")
    dftxt, multi_doc_str = fun_search_activity(llg, topk=5, output_merge_str=1)

    if len(dftxt) < 1:
        return msg_no_enough

    if len(dftxt) > 500:
        return msg_too_many


    log("\n#######  LLM :Summarize #########################################")
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

    log("\n#######  MSG json ############################################")
    dout['html_tags']["summary"] = msg2

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


    log("##### Final html ##############################################")
    llg.msg_answer  = dout
    json_save2(llg, llg.dirout)

    return dout



