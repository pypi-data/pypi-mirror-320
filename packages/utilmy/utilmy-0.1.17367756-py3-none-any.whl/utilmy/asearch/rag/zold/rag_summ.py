"""

    ##### 
        mkdir -p ./ztmp/db//qdrant_storage
        mkdir -p ./ztmp/db//qdrant_snapshots


       docker run -d -p 6333:6333     -v  ./ztmp/db//qdrant_storage:/qdrant/storage     qdrant/qdrant   


       http://localhost:6333/dashboard



    ##### Summarization with Qdrant

        #### Prepare data
            ## qdrant sparse indexing
                alias pyqd="python3 -u rag/engine_qd.py  "
                alias pykg="python3 -u rag/engine_kg.py"
                export dirtmp="./ztmp"

            ### create collection
                pyqd  qdrant_sparse_create_collection --server_url "http://localhost:6333" --collection_name "LZnews"

            ### set payload settings
                pyqd  qdrant_update_payload_indexes --server_url "http://localhost:6333" --collection_name "LZnews" --payload_settings "{'L0_catnews': 'text', 'L1_cat': 'text', 'L2_cat': 'text', 'L3_cat': 'text', 'L4_cat': 'text'}"

            ### index documents
                pyqd  qdrant_sparse_create_index --dirin "$dirtmp/df_LZ_merge_90k_tmp.parquet" --server_url "http://localhost:6333" --collection_name "LZnews" --colscat "['L0_catnews', 'L1_cat', 'L2_cat', 'L3_cat', 'L4_cat', 'text_id', 'title']" --coltext "text" --batch_size 16 --max_words 512 --imax 10000




            ### Create SQL table with column settings
                pykg dbsql_create_table --db_path "$dirtmp/db/db_sqlite/datasets.db" --table_name "LZnews" --columns '{"text_id": "VARCHAR(255) PRIMARY KEY","url": "VARCHAR(255)", "title": "VARCHAR(255)", "date": "VARCHAR(255)", "text": "TEXT", "text_summary": "TEXT", "L0_catnews": "VARCHAR(255)", "L1_cat": "VARCHAR(255)", "L2_cat": "VARCHAR(255)", "L3_cat": "VARCHAR(255)", "L4_cat": "VARCHAR(255)", "com_extract": "VARCHAR(255)"}'

            ### Insert in sqlite
                pykg dbsql_save_records_to_db   --dirin "$dirtmp/df_LZ_merge_90k_tmp.parquet"    --db_path "$dirtmp/db/db_sqlite/datasets.db" --table_name "LZnews" --coltext "text" --colscat '["url", "date", "title","text", "text_summary", "L0_catnews", "L1_cat", "L2_cat", "L3_cat", "L4_cat", "com_extract"]' --colid "text_id" --nrows 1000


            python -m spacy download en_core_web_sm

            chmod 777  ztmp/db/db_sqlite/datasets.db


    #### Generate Summary
        alias pysum="python3 -u rag/rag_summ.py
        export dname="LZnews"

        pysum search_summarize_with_citation --query="Nadal in grand slams"  --llm_max_tokens=1000


    #### Test
        # generate triplets from text
        python3 -u rag/engine_kg.py kg_triplets_extract_v2 --dirin "./ztmp/df_LZ_merge_90k_tmp.parquet" --dirout "./ztmp/df_LZ_merge_90k_tmp_relations.parquet" --istart 0 --nrows 25


        # generate questions from triplets
        python3 -u rag/engine_kg.py kg_generate_questions_from_triplets --dirin "./ztmp/df_LZ_merge_90k_tmp_relations_0_0_25.parquet" --dirout "./ztmp/df_LZ_merge_90k_tmp_questions_0_0_25.parquet"



        os.environ["PYTHONPATH"] = "/Users/kevin.noel/gitdev/agen/gen_dev/aigen/ztmp/myutil_dev/utilmy/asearch:" +os.environ["PYTHONPATH"]



        from utilmy import pd_read_file, pd_to_file, hash_int64
        # preprocessing
        df = pd_read_file("../ztmp/df_LZ_merge_90k.parquet")
        df["text_id"] = df["url"].apply(lambda x:hash_int64(x))
        df.rename(columns={"pred-L1_cat":"L1_cat", "pred-L2_cat":"L2_cat", "pred-L3_cat":"L3_cat", "pred-L4_cat":"L4_cat"}, inplace=True)
        df.fillna("", inplace=True)
        pd_to_file(df, "../ztmp/df_LZ_merge_90k_tmp.parquet")



    ####################################
    #### Summary Tests:
        export PYTHONPATH="$(PWD)"
         export OPENAI_KEY=""

        python rag/rag_summ.py test1


"""
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


<<<<<<< HEAD
def search_summarize(query: str = "", engine="sparse_neo4j", server_url: str = "",
                     sparse_collection_name: str = "hf-ag_news-sparse",
                     topk: int = 10, llm_service: str = "openai", llm_model: str = "gpt-4o-mini", llm_max_tokens: int = 1000):
    """Search and summarize text based on the given query using a sparse model and LLM.

       alias pysum="python3 -u rag/rag_summ.py "
       pysum search_summarize_with_citation --query="Russian economy" --engine="sparse_neo4j" --llm_max_tokens=1000

    Parameters:
        query (str): The query to search and summarize.
        engine (str): The _ separated search engine(s) to use. can be combination of sparse,dense,tantivy, neo4j
        server_url (str): The URL of the server.
        sparse_collection_name (str): The name of the collection to search.
        topk (int): The number of top results to consider.
        llm_max_tokens (int): The maximum number of tokens for the LLM model.

        Returns:
        None
=======
##########################################################################################
def test1(q="""  Recent Partnership of Microsoft     """):

    res = search_summarize_with_citation(q, server_url="http://127.0.0.1:6333",
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
ccols.cols_sqlite = ["url", "date", "L0_catnews", "L_cat", "com_extract", "title", "text", "text_summary", "info"]


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



      ##### Staring with docker:
        download https://drive.google.com/drive/folders/1qpApV24nye8d7dZ3VgYoLG0HBNJzvD5C
        into  asearch/ztmp/db/

        mkdir -p ./ztmp/db/qdrant_storage
        # mkdir -p ./ztmp/db/qdrant_snapshots

        cd asearch/
        docker run -d -p 6333:6333     -v  ./ztmp/db//qdrant_storage:/qdrant/storage     qdrant/qdrant

        ### tbale Lznews
        http://localhost:6333/dashboard




     http://localhost:6333/dashboard#/collections/LZnews

>>>>>>> 3c9ac9bf2c2bf05a5dfddfe933b2ca22b93d19a7
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

def search_summarize_with_citation(cfg=None, cfg_name="test", query: str = "", engine="sparse",
                                   server_url: str = "http://localhost:6333",
                                   sparse_collection_name: str = "LZnews",

                                   table_name_sql="LZnews",
                                   db_path_sql="./ztmp/db/db_sqlite/datasets.db",

                                   llm_prompt_id="summarize_01",
                                   topk: int = 10,  


                                   qdrant_topk = 100,
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
       pysum search_summarize_with_citation --query "What are the microsoft partnerships in august 2024 ?"  --llm_model $modelid --topk 20


       pysum search_summarize_with_citation --query "What are the microsoft partnerships in generative ai in 2024 ?"  --llm_model $modelid --topk 5


       pysum search_summarize_with_citation --query "What are the microsoft partnerships in generative ai in 2024 ? show the most relevant at first"  --llm_model $modelid --topk 5


       pysum search_summarize_with_citation --query "What are the partnerships between Amazon and  Microsoft in generative ai in 2024 ? show the most relevant at first"  --llm_model $modelid --topk 5


 

    """

    global sparse_model
    llg = Box({'query_id': date_now(fmt="%Y%m%d_%H%M%S") + "-" + str(int(random.uniform(1000,9999)))  })
    llg.input_query_user = query


    log("######## Extract tags from question    ################################### ")
    llg.query_tags = llm_question_extract_NER(question=query, llm_service=llm_service,
                                              llm_model=llm_model, llm_max_tokens=1000)
    log("query_tags_dict:", llg.query_tags) 
    msg = summary_question_error_handle(query, llg.query_tags)
    if msg is not None:
       log(msg); return msg 

    llg.query_qdrant = summary_question_rewrite(query, llg.query_tags)

    # llg.query_tags = summary_tags_expansion(query, llg.query_tags)


    log("######## Get results from fusion search   ############################### ")
    query_filter = qdrant_query_createfilter_custom(llg.query_tags)
    client       = QdrantClient(server_url)
    if sparse_model is None:
        sparse_model = EmbeddingModelSparse()


    results = fusion_search(query= llg.query_qdrant, engine=engine, client=client,
                                  sparse_collection_name=sparse_collection_name,
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
    


    if len(llg.results)> 50:
        llg.results =  [ x for x in llg.results if x['score'] > qdrant_score_min ]  
    log('Retrie Filter: ', len(llg.results))
    if len(llg.results)< 1:
       msg = 'Empty results'
       json_save2(llg, dirout)
       log2(msg); return msg 


    log("\n####### Fetch actual text from SQL DB ################################# ")
    #### match date pattern here
    text_ids = [res["text_id"] for res in llg.results ]
    cols     = ['text_id', 'url', 'date', 'title', 'text', 'score' ]
    doc_texts = dbsql_fetch_text_by_doc_ids(db_path=db_path_sql,
                                            table_name=table_name_sql,
                                            cols=cols,
                                            text_ids=text_ids)
    doc_texts = pd.DataFrame(doc_texts)
    log('Doc retrieved:', doc_texts, doc_texts.shape)


    log("#### Doc Keyword filtering ##############################")
    def docontain(w, x):
        x2 = str(x).lower()
        for wi in w.split(" "):
            if wi not in x2 : return False
        return True

    for w in llg.query_tags['activity_tags']:
       dftxt = dftxt[ dftxt['L0_catnews'].apply(lambda x :  docontain(w, x)) ]
       log(w, dftxt.shape)

    for w in llg.query_tags['industry_tags']:
       dftxt = dftxt[ dftxt['L_cat'].apply(lambda x :       docontain(w, x)) ]
       log(w, dftxt.shape)

    for w in llg.query_tags['date']:
       dftxt = dftxt[ dftxt['date'].apply(lambda x :        docontain(w, x)) ]
       log(w, dftxt.shape)

    if len(dftxt) < 1:
        log("empty")
        return " No answers, please enlarge the scope of your question"


    log("#### Doc Re-Ranking ##############################")
    ### Re rank based on doc individual relevance
    """
    
    
    """
    dfqd = pd.DataFrame(llg.results)
    dfqd.columns =['text_id', 'score_qd']
    doc_texts    = doc_texts.merge(dfqd, on=['text_id'], how='left')
    

    t0 = date_now(returnval='unix')
    def rerank_score(x):
      return float(x['score']) * x['score_qd']

    doc_texts['score2'] = doc_texts.apply(lambda x: rerank_score(x), axis=1  )
    doc_texts = doc_texts.sort_values(['score2'], ascending=[0])



    log("\n####### Dsiplay ranking ############################################## ")
    doc_texts = summary_display_ranking(doc_texts, llg.query_tags)


    log("\n####### Format Docs prompt ########################################### ")
    topk = min(10, topk)
    multi_doc_texts = []
    for ii, doc in doc_texts.iloc[:topk,:].iterrows() :
        url   = doc['url']
        title = doc['title']
        text  = doc['text']
        date  = doc['date']

        txt = f""" title: {title}\ndate:{date}url:{url}\ntext:{text}"""
        multi_doc_texts.append(txt)

    multi_doc_str = "\n---\n".join(multi_doc_texts)
    log('Doc appended:', ii)
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

    json_save2(llg, dirout)
    return msg



promptlist = {

    'summarize_00': f"""Summarize information from below articles using bullets points.
        Make sure the the summary contain factual information extracted from the articles.
        Provide inline citation by numbering the article information is fetched from.
        Add numbered article details(date, url, title) in footnotes.\nArticles: \n```\n<multi_doc_string>\n```
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




################################################################################################
######## Question Entity Extraction ############################################################
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


def summary_question_error_handle(query, query_tags):
    try:
        if len(query_tags['company_names']) < 1:
             return "Question should contain at least one company."

    except Exception as e:
        log(e)
        return "Question cannot be analyzed"
    return None    




def summary_question_rewrite(query, query_tags):
  """
      A) Question ---> List of 5 sentences,  and list of 10 keyword tags related.
            Prompt be specific:  Contraints the generation a bit.


      B) Eval the retrieval by qdrant : Sparse Embedding only
           Ground thruth... ???  --->     Recall:
                parquet file of news.

           Relative eval:
               Baseline:  question without expansion (ref) ---> list of text_id  top-10.

               New:   ---> top-10 ---> extract the new ones on top_10,
                       Human eval on some eexample: copy paste : looks OK, or spot bad one.
                        News Title




  """
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


def summary_display_ranking(doc_texts, query_tags):
    display_tag = query_tags['display_tags'][0]
    log("Display results:", display_tag)
    if 'most_recent' in display_tag: 
        # doc_texts  = sorted(doc_texts, key=lambda doc: doc["date"], reverse=True)
        doc_texts  = doc_texts.sort_values('date', ascending=0)

    elif 'most_relevant' in display_tag: 
        # doc_texts  = sorted(doc_texts, key=lambda doc: doc["date"], reverse=True)
        doc_texts  = doc_texts.sort_values('date', ascending=0)

    doc_texts.index = np.arange(0, len(doc_texts)) 
    return doc_texts




####################################################################
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

    task: list          = Field(description="Example of tasks like \"compare\", \"summarize\", \"what are\", \"unknown\" ")

    data_source: str   = Field(description="Example of data source \"news\", \"industry\",  ")


    date_period: str    = Field(description="before/between/after/in")
    date: list          = Field(description="Dates information in the text in this format:  YYYY  or YYYY-MM")

    company_names: list = Field(description="Names of the corporate entities")
    industry_tags: list = Field(description="tags related to company or business industries such as generative ai")

    activity_tags: list = Field(description="company activity or actions mentioned in the text. Example: partnership, acquisition, collaboration")

    context:       list = Field(description="words of the text that did not get categorized in other fields")

    display_tags:  list = Field(description="list of tags to describe how the results should be ranked: 'most_recent', 'most_relevant' ")



def llm_question_extract_NER(question="Summarize the news", llm_service="openai", llm_model="gpt-4o-mini",
                             llm_max_tokens=1000) -> dict:
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
"precision medicine"                                                                                            
"generative ai"
"foundation models"
"extended reality"
"waste recovery"
"plant based meat"
"auto tech"
"supply chain tech"
"web ecosystem"
"ai drug"
"decentralized finance"
"aircraft"
"additive manufacturing"
"space travel"
"health"
"cybersecurity"
"ev economy"
"truck industry"
"quantum computing"
"plant based dairy egg"
"machine learning"
"data infrastructure"
"travel"
"bio materials"
"carbon"
"last mile"
"smart farming"
"preventive healthcare"
"neobanks"
"logistics"
"alternative energy"
"cloud native"
"business expense"
"alternative ingredients"
"marketing automation"
"insurtech personal lines"
"edge computing"
"fintech"
"cell cultured meat"
"hydrogen economy"
"metaverse"
"cell gene therapy"
"workflow automation"
"human gene editing"
"automated stores"
"pay later"
"esports"
"remote work"
"psychedelic"
"clinical trial"
"remote work"
"creator economy"
"vertical farming"
"age tech"
"smart factory"
"smart mobility"
"food delivery"
"edtech"
"next gen satellites"
"digital twin"
"mental health"
"carbon management"
"retail trading"
"digital privacy"
"longevity"
"insurtech"
"food waste"
"sales engagement"
"crm"
"blockchain"
"no code"
"digital wellness"
"financial wellness"
"climate"
"biometric"
"cloud optimization"
"retail robots"
"restaurant robotics"
"biotech"
"residential tech"
"online freelancing"
"conservation"
"natural fertilizers"
"beauty tech"
"facial recognition"
"smart packaging"
"serverless computing"
"pet care"
"fertility"
"cloud kitchens"
"cyber insurance"
"livestock biotech"
"prefab"
"connected fitness"
"identity access"
"low code"
"edtech"
"insurtech"
"devops"
"natural language processing"
"digital retail"      

    """

    llm_1 = LLM(llm_service, llm_model, max_tokens=llm_max_tokens)
    llm_res = llm_1.get_save_sync(prompt=prompt, output_schema=questionNER, dirout=None)
    msg = llm_res["choices"][0]["message"]["content"]
    dd = llm_cleanup_gpt_jsonformat(msg)
    log('\n###### msg_dict_raw: ', dd)

    #### Post process task ###################################
    lsource = {'news': 'LZnews', 'industry': 'Eindustry'}
    ti = dd.get('data_source', 'industry')
    if 'activi' in ti:      ti = 'news'

    dd['data_source'] = lsource.get(ti, 'Eindustry')

    #### Post process task ###################################
    ll2 = []
    for ti in dd.get('task', ['summarize']):
        if 'what are' in ti.lower():
            ll2.append('summarize')

        else:
            ll2.append(ti)
    dd['task'] = ll2

    #### Post process date ###################################
    ll2 = []
    for ti in dd.get('date', ['2024']):
        ll2.append(ti.lower())
    dd['date'] = ll2

    #### Post process activity ###############################
    ll2 = []
    log(dd['activity_tags'])
    for ti in dd.get('activity_tags', ['partnership']):
        if ti.split(" ")[0] not in question:
            continue

        ti2 = NER_norm(ti)

        if 'partner' in ti2 or 'collabo' in ti2:
            ll2.append('partnership')

        elif 'acqui' in ti2 or 'merge' in ti2:
            ll2.append('m and a')

        elif 'activi' in ti2:
            pass
        else:
            ll2.append(ti2)
        log(ti, ti2)

    dd['activity_tags'] = ll2

    #### Industry ###########################################
    ll2 = []
    for ti in dd.get('industry_tags', []):
        if ti.split(" ")[0] not in question:
            continue

        ti2 = NER_norm(ti)
        ll2.append(ti2)
    dd['industry_tags'] = ll2

    #### Post process Company ###############################
    ll2 = []
    for ti in dd.get('company_names', []):
        ll2.append(ti.lower())
    dd['company_names'] = ll2

    #### Post process display ###############################
    ll2 = []
    for ti in dd.get('display_tags', ['most_recent']):
        ll2.append(ti.lower())
    dd['display_tags'] = ll2

    # assert len(dd[ questionNER.keys()])>0, 'Missing keys'

    log("\n##### query_tags_dict:", dd)
    return dd


def NER_norm(ti):
    ti2 = ti.lower()
    ti2 = ti2.replace('artificial intelligence', 'ai')
    ti2 = ti2.replace('technology', 'tech')
    ti2 = ti2.replace('automobile', 'auto')
    return ti2


##############################################################
def NER_norm(ti):
    ti2 = ti.lower()
    ti2 = ti2.replace('artificial intelligence', 'ai')
    ti2 = ti2.replace('technology', 'tech')
    ti2 = ti2.replace('automobile', 'auto')
    return ti2









##############################################################
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


        Before we send to qdrant, we need to normalize all filtering tags.
         only word token matching --->
                   send "partnership": normalize before putting in filtering.


         How to find the correct tags ?
              qdrant fields: com_extract, industry_tags, activtity_tags
                  from parquet file data.





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
def json_records_save(records, dirout="ztmp/gpt_train/mydata.json"):
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
    fire.Fire({
        'llm_generate_sample_questions': llm_generate_sample_questions,
        'llm_question_extract_NER': llm_question_extract_NER,
        'pd_add_actvy_tag2': pd_add_actvy_tag2,
        'pd_add_industry_tag2': pd_add_industry_tag2

    })




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
