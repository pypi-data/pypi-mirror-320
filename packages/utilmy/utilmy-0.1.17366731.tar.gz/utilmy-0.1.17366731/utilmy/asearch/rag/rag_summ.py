"""

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
import json
import os
import warnings

warnings.filterwarnings("ignore")
from rag.engine_tv import fusion_search
from rag.engine_qd import QdrantClient

from utilmy import log, pd_read_file, pd_to_file, json_save
from utilmy.asearch.rag.engine_kg import dbsql_fetch_text_by_doc_ids
from utilmy.asearch.rag.engine_qd import EmbeddingModelSparse
from utilmy.asearch.rag.llm import LLM, llm_cleanup_gpt_jsonformat
from pydantic import BaseModel, Field


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
    df.rename(columns={"pred-L1_cat":"L1_cat", "pred-L2_cat":"L2_cat", "pred-L3_cat":"L3_cat", "pred-L4_cat":"L4_cat"}, inplace=True)
    df.fillna("", inplace=True)
    pd_to_file(df, "../ztmp/df_LZ_merge_90k_tmp.parquet")






#########################################################################################
global sparse_model
sparse_model = None

def search_summarize_with_citation(query: str = "", engine="sparse",
                                   server_url: str = "http://localhost:6333",
                                   sparse_collection_name: str = "LZnews",

                                   table_name_sql="LZnews",
                                   db_path_sql="./ztmp/db/db_sqlite/datasets.db",

                                   llm_prompt_id="P01",
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

    """
    global sparse_model

    log("######## Extract tags from question    ################################### ")
    query_tags_dict = None
    query_tags_dict = llm_question_extract_NER(question=query, llm_service=llm_service,
                                               llm_model="gpt-4o-mini", llm_max_tokens=1000)

    query_filter = qdrant_query_createfilter_custom(query_tags_dict)


    log("######## Get results from fusion search   ############################### ")
    client = QdrantClient(server_url)
    if sparse_model is None:
        sparse_model = EmbeddingModelSparse("naver/efficient-splade-VI-BT-large-doc")


    fusion_output = fusion_search(query=query, engine=engine, client=client,
                                  sparse_collection_name=sparse_collection_name,
                                  neo4j_db="neo4j", sparse_model=sparse_model,
                                  query_tags=query_tags_dict, query_filter=query_filter
                                  )


    results = [{"text_id": text_id, "score": score} for text_id, score in fusion_output.items()]
    results = sorted(results, key=lambda doc: doc["score"], reverse=True)
    text_ids = [res["text_id"] for res in results[:topk]]


    log("\n####### Fetch actual text from SQL DB ################################# ")
    cols = ['text_id', 'url', 'title', 'text']
    doc_texts = dbsql_fetch_text_by_doc_ids(db_path=db_path_sql,
                                            table_name=table_name_sql,
                                            cols=cols,
                                            text_ids=text_ids)


    log("\n####### Format Docs prompt ########################################### ")
    # use dummy titles and urls
    log(doc_texts[0].keys())

    multi_doc_texts = []
    for doc in doc_texts:
        url = doc['url']
        title = doc['title']
        text = doc['text']

        txt = f""" title: {title}\nurl:{url}\ntext:{text}"""
        multi_doc_texts.append(txt)

    multi_doc_string = "\n---\n".join(multi_doc_texts)


    log("\n#######  LLM :Summarize #############################################")
    llm_1 = LLM(llm_service, llm_model, max_tokens=llm_max_tokens)
    ptext = promptlist[llm_prompt_id]
    ptext = ptext.replace("<question>", query)
    ptext = ptext.replace("<multi_doc_string>", multi_doc_string)

    #### prompt.history
    # print(prompt_text)

    llm_response = llm_1.get_save_sync(prompt=ptext, output_schema=None, dirout=None)
    result = llm_response["choices"][0]["message"]["content"]
    # print(result)
    return result







promptlist = {

    'P01': f"""Summarize information from below articles using bullets points.
        Make sure the the summary contain factual information extracted from the articles.
        Provide inline citation by numbering the article information is fetched from.
        Add numbered article details(date, url, title) in footnotes.\nArticles: \n```\n<multi_doc_string>\n```
        """


    , 'P02': f"""
        You are a researcher writing a memo about <question>  for executives.
        The memo contains the following:

        At the beginning, provide overall summary of all the articles in 5 lines.      
        Keep only factual information.   

        Then, for each news article below, provide those information as follow:
                Article title and date
                Article URL
                Summary of the article in 4 lines. Keep only factual information and concise text.

        News articles are below:

       ```\n<multi_doc_string>\n``` 
        """


    , 'P03': f"""Write down a small introduction, replying to the question, Summarize each news article individually using bullets point and attach URL and article date.
     Make sure the summaries contain factual information extracted from the article.
     Write down a conclusion for the overall news articles and topics. \nArticles: \n```\n<multi_doc_string>\n```
     """


}






################################################################################################
######## Question Entity Extraction ############################################################

def test_question_ner_extraction():
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

    for test_query in test_queries[-1:]:
        q = test_query[0]
        expected = test_query[1]
        query_tags_dict = llm_question_extract_NER(question=q, llm_service="openai",
                                                   llm_model="gpt-4o-mini", llm_max_tokens=1000)
        # print(query_tags_dict)
        for k, v in expected.items():
            assert query_tags_dict[k] == v




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
                "relation_tags": ["acquisition"],
              "context": ["companies in America",  "not in canada" ]
        }
    """
    ### Trick to improve accuracy.
    reasoning: str = Field(description=" Summarize in 2 sentences your reasoning on this entity extraction.")

    task: list = Field(description="predefined tasks like \"compare\", \"summarize\", \"unknown\"    )")

    date_period: str = Field(description="before/between/after/in")
    date: list = Field(description="Dates year information in the text")

    company_names: list = Field(description="Names of the corporate entities")
    industry_tags: list = Field(description="tags related to company or business industries")

    activity_tags: list = Field(description="company activity or actions mentioned in the text")

    context: list = Field(description="keywords that didnt get categorized anywhere else")


def llm_question_extract_NER(question="", llm_service="openai", llm_model="gpt-4o-mini", llm_max_tokens=1000) -> dict:

    prompt = f"""
    Analyze the key components of the given text.
    -----------text-----------
    {question}
    """

    llm_1 = LLM(llm_service, llm_model, max_tokens=llm_max_tokens)
    llm_res = llm_1.get_save_sync(prompt=prompt, output_schema=questionNER, dirout=None)
    msg = llm_res["choices"][0]["message"]["content"]
    msg = llm_cleanup_gpt_jsonformat(msg)
    d_json = json.loads(msg)
    return d_json




def qdrant_query_createfilter_custom(query_tags: dict):
    """
      query_tags ---> Map to Qdrant categories field


         Qdrant columns:
              L_cat = L1_cat + L2_cat + L3_cat + L4_cat
              "['L0_catnews', 'com_extract',   'Lcat, 'text_id', 'title']"

        query_filter=Filter(
            should=[
                FieldCondition(key="category", match=MatchValue(value="electronics")),
                FieldCondition(key="brand", match=MatchValue(value="apple"))
            ]

        query_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="category",
                    match=models.MatchText(text="elec")
                )
            ]

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
    from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchText

    must = []
    for key, valist in query_tags.items():
        if key == "company_names":
            for val in valist:
                must.append(FieldCondition(key="com_name", match=MatchText(text=val)))


    should = []
    for key, valist in query_tags.items():
        if key == "industry_tags":
            for val in valist:  #### concatenated
                should.append(FieldCondition(key="L_cat", match=MatchText(text=val)))

        if key == "date":
            for val in valist:
                should.append(FieldCondition(key="period", match=MatchText(text=val)))

        if key == "activity_tags":  ### acquisition
            for val in valist:
                should.append(FieldCondition(key="activity", match=MatchText(text=val)))

        if key == "context":
            for val in valist:
                should.append(FieldCondition(key="context", match=MatchText(text=val)))

    query_filter = Filter(must=must, should=should)
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
def jsonl_save(records, dirout="ztmp/gpt_train/mydata.jsonl"):
    import json
    with open(dirout, "w") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")
    log(dirout)


def llm_create_json(dirin, question_col="question", label_col="label", dirout="ztmp/gpt_train/mydata.jsonl"):
    """
    Takes prompt, answer pairs and prepare openai compatible format for finetuning.
    """
    from llm import prompt_fun_addprefix_jsonformat
    df = pd_read_file(dirin)

    def create_prompt(x):
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

        schema_json = prompt_fun_addprefix_jsonformat(questionNER)
        final_prompt = f"{x}\nRespond with the following JSON schema: \n{schema_json}"
        return final_prompt

    def create_data_example(x):
        # ensure that all columns are strings
        if not isinstance(x[question_col], str):
            x[question_col] = str(x[question_col])
        if isinstance(x[label_col], dict):
            x[label_col] = json.dumps(x[label_col])

        return {
            "messages": [{"role": "user", "content": x[question_col]}, {"role": "assistant", "content": x[label_col]}]}

    df['prompt'] = df[question_col].apply(lambda x: create_prompt(x))

    df["example"] = df.apply(lambda x: create_data_example(x), axis=1)

    # df.rename(columns={label_col:"label"}, inplace=True)
    djson = df["example"].to_list()
    jsonl_save(djson, dirout)


def llm_finetune(dirin="ztmp/gpt_train/mydata.jsonl", dirout="ztmp/gpt_train"):
    """
            5 rows csv with \t  tab separated
    """
    import openai
    from utilmy import date_now

    openai.api_key = os.environ["OPENAI_KEY"]

    # upload training file

    client = openai.OpenAI()
    file_response = client.files.create(
        file=open(dirin, "rb"),
        purpose="fine-tune"
    )
    training_file_id = file_response.id

    # create the training job
    response = client.fine_tuning.jobs.create(
        training_file=training_file_id,
        model="gpt-4o-mini-2024-07-18"
    )

    ts = date_now(fmt="%Y%m%d_%H%M%S", returnval="str")
    json_save(response.to_dict(), dirout + f"/finetune_{ts}.json")
    return response

    # # Use the fine-tuned model
    # completion = openai.Completion.create(
    #     model=response.fine_tuned_model,
    #     prompt="Your prompt here"
    # )
    # print(completion.choices[0].text)



def test_finetune():
    """



    :return:
    """








if __name__ == '__main__':
    import fire
    fire.Fire()
















def zzz_search_summarize_with_citation(query: str = "", engine="sparse_neo4j",
                                       server_url: str = "http://localhost:6333",
                                       sparse_collection_name: str = "LZnews",
                                       table_name_sql="LZnews",
                                       db_path_sql="./ztmp/db/db_sqlite/datasets.db",
                                       topk: int = 10, llm_service: str = "openai", llm_model: str = "gpt-4o-mini",
                                       llm_max_tokens: int = 1000):
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
    """
    # 1.  get results from fusion search
    client = QdrantClient(server_url)
    sparse_model = EmbeddingModelSparse("naver/efficient-splade-VI-BT-large-doc")
    fusion_output = fusion_search(query=query, engine=engine, client=client,
                                  sparse_collection_name=sparse_collection_name,
                                  neo4j_db="neo4j", sparse_model=sparse_model)

    results = [{"text_id": text_id, "score": score} for text_id, score in fusion_output.items()]
    results = sorted(results, key=lambda doc: doc["score"], reverse=True)
    text_ids = [res["text_id"] for res in results[:topk]]
    # get text from text_id
    doc_texts = dbsql_fetch_text_by_doc_ids(db_path=db_path_sql,
                                            table_name=table_name_sql,
                                            text_ids=text_ids)

    # 2.  summarize results via LLM
    llm_1 = LLM(llm_service, llm_model, max_tokens=llm_max_tokens)
    multi_doc_texts = [f"{doc['text']}" for idx, doc in enumerate(doc_texts)]
    multi_doc_string = "\n---\n".join(multi_doc_texts)
    prompt_text = f"Generate a 10 line summary of the news articles below. It should cover all articles. \nArticles: \n```\n{multi_doc_string}\n```"
    # print(prompt_text)
    llm_response = llm_1.get_save_sync(prompt=prompt_text, output_schema=None, dirout=None)
    result = llm_response["choices"][0]["message"]["content"]
    return result



def create_dummy_traning_examples():
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
