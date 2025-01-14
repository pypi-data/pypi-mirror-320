"""
    #### Install
        # NEbula installation
        Option 0 for machines with Docker: `curl -fsSL nebula-up.siwei.io/install.sh | bash`
        Option 1 for Desktop: NebulaGraph Docker Extension https://hub.docker.com/extensions/weygu/nebulagraph-dd-ext






"""

if "import":
    import os, time, traceback, warnings, logging, sys, sqlite3
    warnings.filterwarnings("ignore")


    from collections import Counter
    import json, warnings, spacy, pandas as pd, numpy as np
    from dataclasses import dataclass

    ### KG
    from neo4j import GraphDatabase

    # NLP
    from transformers import (pipeline)
    import spacy
    spacy_model = None


    ## Uncomment this section for llamaindex llm call logs
    # logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    # logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
    import llama_index.core
    llama_index.core.set_global_handler("simple")

    ############################################
    from utilmy import pd_read_file, os_makedirs, pd_to_file
    from utilmy import log


    ############################################
    from rag.llm import llm_get_answer
    from utils.utils_base import torch_getdevice, pd_append


################################################################################
def test_create_test_data(dirout="./ztmp/testdata/myraw.parquet"):
    """
    usage: pythpn3 -u enging_kg test_create_test_data --dirout myraw.parquet
    """
    from llama_index.readers.wikipedia import WikipediaReader
    loader = WikipediaReader()
    documents = loader.load_data(
        pages=["Guardians of  Galaxy Vol. 3"], auto_suggest=False
    )
    text_list = documents[0].text.split("\n")
    # remove short lines
    text_list = [text for text in text_list if len(text) > 20]
    text_df = pd.DataFrame(text_list, columns=["text"], dtype=str)
    pd_to_file(text_df, dirout, show=1)


def test0():
    triplet_extractor = pipeline('translation_xx_to_yy', model='Babelscape/mrebel-base',
                                 tokenizer='Babelscape/mrebel-base')

    # We need to use  tokenizer manually since we need special tokens.
    msg = " Red Hot Chili Peppers were formed in Los Angeles by Kiedis, Flea"
    extracted_text = triplet_extractor.tokenizer.batch_decode([triplet_extractor(msg,
                                                                                 src_lang="en", return_tensors=True,
                                                                                 return_text=False)[0][
                                                                   "translation_token_ids"]])  # change __en__ for  language of  source.
    log(extracted_text[0])



####################################################################################################
#### Triplet using LLM
def llm_triplet():
    """
      LLM Extraction:

      groq API KEY
      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


https://towardsdatascience.com/relation-extraction-with-llama3-models-f8bc41858b9e

    
    """

######################################################################################################
#######  NLP Tools: triplet, keywords ################################################################
class SpacyModel:
    def __init__(self, model_id="en_core_web_sm"):
        self.model_id = model_id
        self.nlp = spacy.load(model_id)
        self.nc_exceptions = ["-", "—", "What"]

        # exception added due to obseverved misbehaviour in  spacy model 3.7.1
        ruler = self.nlp.get_pipe("attribute_ruler")
        patterns = [[{"ORTH": "-"}]]
        attrs = {"TAG": "HYPH", "POS": "PUNCT"}
        ruler.add(patterns=patterns, attrs=attrs)

    def extract_keywords(self, text_list: list) -> list:
        """Extracts keywords from a list of text using spaCy library.
        Args:
            text_list (list): A list of text strings from which to extract keywords.

        Returns:
            list: A list of lists, where each inner list contains keywords extracted 
            
        """
        result = []
        docs = self.nlp.pipe(text_list)

        for doc in docs:
            keywords = [nc.text for nc in doc.noun_chunks if nc.text not in self.nc_exceptions]
            result.append(keywords)
        return result


class TripletExtractorModel:
    def __init__(self, model_id='Babelscape/rebel-large', model_type="mrebel"):
        """Initializes  TripletExtractorModel with  specified model_id and model_type.
         Args:
            model_id (str):  ID of  model to be used. Default is 'Babelscape/rebel-large'.
            model_type (str):  type of  model. Default is "mrebel".

        """
        self.model_id = model_id
        self.model_type = model_type

        if model_type == "mrebel":
            s_time = time.time()
            device = torch_getdevice()
            self.pipeline = pipeline('text2text-generation', model=model_id,
                                     tokenizer=model_id, device=device)
            log(f"Model loaded in {time.time() - s_time:.2f} seconds")
        else:
            raise ValueError(f"Invalid model type: {model_type}")

    def extract_triplets(self, text) -> list:
        """Extracts triplets from  given text.

        Args:
            text (str):  text from which to extract triplets.

        Returns:
            list: A list of dictionaries representing  extracted triplets. 
            Each dictionary contains  keys 'head', 'type', and 'tail', representing  subject, predicate, and object of  triplet.

        """
        triplets = []
        relation, subject, relation, object_ = '', '', '', ''
        text = text.strip()
        current = 'x'
        for token in text.replace("<s>", "").replace("<pad>", "").replace("</s>", "").split():
            if token == "<triplet>":
                current = 't'
                if relation != '':
                    triplets.append({'head': subject.strip(), 'type': relation.strip(), 'tail': object_.strip()})
                    relation = ''
                subject = ''
            elif token == "<subj>":
                current = 's'
                if relation != '':
                    triplets.append({'head': subject.strip(), 'type': relation.strip(), 'tail': object_.strip()})
                object_ = ''
            elif token == "<obj>":
                current = 'o'
                relation = ''
            else:
                if current == 't':
                    subject += ' ' + token
                elif current == 's':
                    object_ += ' ' + token
                elif current == 'o':
                    relation += ' ' + token
        if subject != '' and relation != '' and object_ != '':
            triplets.append({'head': subject.strip(), 'type': relation.strip(), 'tail': object_.strip()})
        return triplets

    def extract(self, text_list: list) -> list:
        """Extracts information from a list of texts and returns a list of extracted triplets.
        
         Args:
            text_list (list): A list of texts for which information needs to be extracted.
        
        Returns:
            list: A list of extracted triplets containing  head, type, and tail of each triplet.
        """

        # result = []
        from datasets import Dataset

        data = {'id': np.arange(0, len(text_list)),
                'text': text_list
                }
        dataset = Dataset.from_dict(data)
        # log(dataset)

        text_list2 = self.pipeline(dataset["text"], return_tensors=True, return_text=False)
        text_list2 = self.pipeline.tokenizer.batch_decode([x["generated_token_ids"] for x in text_list2])

        # log(f"extracted_text: {extracted_text}")
        # result = [[] for _ in range(len(text_list2))]
        list_list_triplets = []
        for i, text in enumerate(text_list2):
            triplet_list = self.extract_triplets(text)
            list_list_triplets.append(triplet_list)
        return list_list_triplets


    def extract_pandas(self, df) -> pd.DataFrame:
        """Extracts information from a list of texts and returns a list of extracted triplets.
        
         Args:
            text_list (list): A list of texts for which information needs to be extracted.
        
        Returns:
            list: A list of extracted triplets containing  head, type, and tail of each triplet.
        """

        # result = []
        from datasets import Dataset

        data = {'id': np.arange(0, len(text_list)),
                'text': text_list
                }
        dataset = Dataset.from_dict(data)
        # log(dataset)

        text_list2 = self.pipeline(dataset["text"], return_tensors=True, return_text=False)
        text_list2 = self.pipeline.tokenizer.batch_decode([x["generated_token_ids"] for x in text_list2])

        # log(f"extracted_text: {extracted_text}")
        # result = [[] for _ in range(len(text_list2))]
        list_list_triplets = []
        for i, text in enumerate(text_list2):
            triplet_list = self.extract_triplets(text)
            list_list_triplets.append(triplet_list)
        return list_list_triplets






class SpacyTripletExtractorModel:

    def __init__(self, model_id='Babelscape/rebel-large'):
        self.model_id = model_id
        self.nlp = spacy.load("en_core_web_sm")
        self.nlp.add_pipe("rebel", after="senter", config={
            'device': -1,  # Number of GPU, -1 if want to use CPU
            'model_name': model_id}  # Model used, will default to 'Babelscape/rebel-large' if not given
                          )

    def post_process(self, extracted_triplets):
        post_processed = []
        for triplet in extracted_triplets:
            p_triplet = {}
            p_triplet['head'] = triplet['head_span'].lemma_  # span => lemmatized str
            p_triplet['tail'] = triplet['tail_span'].lemma_  # span => lemmatized str
            p_triplet['type'] = triplet['relation']  # already str
            post_processed.append(p_triplet)
        return post_processed

    def extract(self, text_list: list) -> list:
        result = []
        docs = self.nlp.pipe(text_list)
        for doc in docs:
            for value, rel_dict in doc._.rel.items():
                result.append(rel_dict)

        result = self.post_process(result)
        return result


##################################################################################################
###### Triplets  tasks   #########################################################################
# @dataclass
# class TripletSchema:
#    doc_id:int 
#    head:str 
#    tail:str
#    type:str
#    info_json:str





def kg_triplets_extract_v2(cfg=None, dirin="./ztmp/bench/ag_news/aparquet/*.parquet",
                           dirout="ztmp/bench/ag_news/kg_triplets/kg_relation.parquet",
                           model_id="Babelscape/rebel-large",
                           istart=20000,
                           nrows=1000000,
                           colid="text_id", coltxt="text",
                           batch_size=1000):
    """Extract triplets from raw text, using Rebel and save to csv
       
       export pykg="python -u rag/engine_kg.py  "
       pykg kg_triplets_extract_v2  --dirin myraw.parquet --model_id Babelscape/rebel-large -- dirout .ztmp/data/kg/kg_relation.parquet
            Processed docs/Time taken:
            10/5.56 seconds
            20/9.66 seconds
            30/14.06 seconds

    """
    df = pd_read_file(dirin)
    assert coltxt in df.columns

    log(df)
    # pick nrows rows from df
    df = df.iloc[istart:istart + nrows, :]
    log(df)

    extractor = TripletExtractorModel(model_id=model_id)
    # extractor = SpacyTripletExtractorModel(model_id=model_id)

    kmax = 1 + int(len(df) // batch_size)
    for k in range(0, kmax):
        log(k)


        dfk = df.iloc[k * batch_size:(k + 1) * batch_size, :]

        idx0 = dfk.index[0]
        text_ids: list = dfk[colid].values.tolist()
        txt_list: list = dfk[coltxt].values.tolist()
        diroutk = dirout.replace(".parquet", f"_{idx0}_{k}_{len(dfk)}.parquet")
        del dfk

        log("####### Start model triplet exraction ##############")
        extracted_triplets: list = extractor.extract(txt_list)

        log("####### Save triplet exraction #####################")
        # log(f"len(extracted_triplets): {len(extracted_triplets)}")
        result = zip(text_ids, extracted_triplets)
        kg_triplets_save(result, dirout=diroutk)


def kg_triplets_save(textid_triplets_tuple: list, dirout=",/ztmp/bench/ag_news/kg_triplets/kg_triplet.parquet"):
    """ Save triplets extracted from documents to file

    Args:
        doc_id_triplets (list): A list of tuples containing document IDs and their corresponding triplets.
            Each tuple consists of a document ID (str) and a list of triplets (dict).
            Each triplet is a dictionary with keys "head" (str), "type" (str), and "tail" (str).
        dirout (str ): path to output CSV file.     : ",/ztmp/out/kg/kg_relation.parquet".

    """
    df = pd.DataFrame(columns=['text_id', 'head', 'type', 'tail', "info_json"])
    if os.path.exists(dirout):
        df = pd_read_file(dirout)
        df = df[['text_id', 'head', 'type', 'tail', "info_json"]]

    row_list = []
    for text_id, triplets in textid_triplets_tuple:
        for triplet_dict in triplets:
            row_list.append([str(text_id), triplet_dict["head"],
                             triplet_dict["type"],
                             triplet_dict["tail"],
                             triplet_dict.get("info_json", "")])  # dummy field added to avoid parquet error

    df = pd_append(df, row_list)
    df = df.drop_duplicates(subset=['text_id', 'head', 'type', 'tail'], keep='first')
    log(df[['head', 'type', 'tail']])
    pd_to_file(df, dirout, show=0)




######################################################################################################
##############  NEO4J DB   ###########################################################################

#### Insert triplet Mode   ################################################
def neo4j_create_db(db_name="neo4j"):
    """Creates a Neo4j database with specified name.
    Args:
        db_name (str ):  name of Neo4j database.     : "neo4j".

        python rag/engine_kg.py neo4j_create_db --db_name "neo4j"


        Installation steps (https://neo4j.com/docs/operations-manual/current/installation/linux/tarball/):
            1. Download tar file from https://neo4j.com/deployment-center
            2. tar zxf neo4j-enterprise-5.19.0-unix.tar.gz
            3. mv neo4j-community-5.19.0 /opt/
            ln -s /opt/neo4j-community-5.19.0 /opt/neo4j
            4.  groupadd neo4j
                useradd -g neo4j neo4j -s /bin/bash
            5. chown -R neo4j:adm /opt/neo4j-community-5.19.0

            Run in background:
            1. /opt/neo4j/bin/neo4j start
            2. Web UI: http://localhost:7474

        Docker run:    





    """
    # URI = "neo4j://localhost:7687"
    # AUTH = ("neo4j", "hell0neo")

    driver = neo4j_get_client()

    # with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    # create db
    # Note: community edition supports only single database
    # query = f"CREATE DATABASE {db_name} IF NOT EXISTS;"
    # add constraint to avoid duplicates
    # driver.execute_query(query_=query)
    query = f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:Entity) REQUIRE n.name IS UNIQUE"
    driver.execute_query(query_=query, database_=db_name)

    driver.close()


def neo4j_db_insert_triplet_file(dirin="ztmp/kg/data/kg_relation.parquet", db_name="neo4j",
                                 nrows: int = -1, ntry_max=3):
    """Inserts triplets from a CSV file into a Neo4j database.
  
       #triples: 1627, total time taken : 8.34 seconds  

       Args:
            dirin (str ):    path to CSV file containing triplets.     : "ztmp/data/kg_relation.parquet".
            db_name (str ):  name of Neo4j database.     : "neo4j".
            nrows (int ):    number of rows to process from CSV file.     : -1 (process all rows).

        Returns:
            None: If an exception occurs during execution of query.
    """
    df = pd_read_file(dirin)
    nrows = len(df) if nrows < 0 else nrows

    df = df.iloc[:nrows, :]

    # URI = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
    # expects NEO4J_USERNAME and NEO4J_PASSWORD in env
    # AUTH = (os.environ.get("NEO4J_USERNAME", "username"), os.environ.get("NEO4J_PASSWORD", "password"))

    driver = neo4j_get_client()
    # with GraphDatabase.driver(URI, auth=AUTH) as driver:
    s_time = time.time()
    for row in df.itertuples():
        # pro: single query for all insertions
        # con: docids may contain duplicates
        query = f"""
                MERGE (head:Entity {{name: $head}})
                ON CREATE SET head.name = $head
                MERGE (tail:Entity {{name: $tail}})
                ON CREATE SET tail.name = $tail
                MERGE (head)-[relation:Relationship {{name: $type__}}]->(tail)
                ON CREATE 
                    SET 
                        relation.textids = [$text_id]
                ON MATCH 
                    SET 
                        relation.textids = relation.textids + [$text_id]
                """
        params = {"head": row.head, "tail": row.tail, "type__": row.type, "text_id": row.text_id}
        # pro: keeps docids unique in db
        # con: run 2 queries for 1 insertion
        # check if relation already exists
        # query = f"MATCH (n:Entity {{id: '{head}'}})-[r:RELATIONSHIP {{name: '{relation}'}}]->(m:Entity {{id: '{tail}'}}) RETURN r"
        # result, _, _ = driver.execute_query(query_=query, database_="neo4j")
        # if len(result) > 0:
        #     # log(result[0]["r"]["docids"])
        #     if docid not in result[0]["r"]["docids"]:
        #         # update relationship with new docid
        #         query = f"MATCH (n:Entity {{id: '{head}'}})-[r:RELATIONSHIP {{name: '{relation}'}}]->(m:Entity {{id: '{tail}'}}) SET r.docids = r.docids + [{docid}] RETURN r"
        #         driver.execute_query(query_=query, database_="neo4j")
        #     return
        #
        # query = f"""CREATE (e1:Entity {{id: '{head}'}}),
        # (e2:Entity {{id: '{tail}'}}),
        # (e1)-[:RELATIONSHIP {{name: '{relation}', docids: {[docid]}}}]->(e2);"""

        # log(query)
        ntry = 0
        ii = 0
        ntry = 0
        while ntry < ntry_max:
            try:
                driver.execute_query(query_=query, **params, database_=db_name)
                ii += 1
                break
            except Exception as e:
                log(traceback.format_exc())
                log(query)
                ntry += 1
                time.sleep(5 * ntry)

    log(f" #triplet inserted: {ii} / {nrows},  time : {(time.time() - s_time):.2f} seconds")
    driver.close()


#### Search Mode   ###################################################
def neo4j_search_triplets_bykeyword(cfg=None, db_name="neo4j", keywords: list = None):
    from neo4j import GraphDatabase
    # query = f"""
    #         WITH {keywords} AS keywords
    #         MATCH (entity1)-[rel]-(entity2)
    #         WHERE any(keyword IN keywords WHERE entity1.name CONTAINS keyword
    #                   OR entity2.name CONTAINS keyword
    #                   OR type(rel) CONTAINS keyword)
    #         RETURN entity1, rel, entity2
    # """
    # leads to 41.1% accuracy
    query = f"""
                WITH {keywords} AS keywords
                MATCH (entity1)-[rel]-(entity2)
                WHERE any(keyword IN keywords WHERE toLower(entity1.name) CONTAINS toLower(keyword)
                          OR toLower(entity2.name) CONTAINS toLower(keyword)
                          OR toLower(rel.name) CONTAINS toLower(keyword))
                RETURN entity1, rel, entity2
        """
    # leads to 42.2% accuracy

    # query = f"""
    #             WITH {keywords} AS keywords
    #             MATCH (entity1)-[rel]-(entity2)
    #             WHERE any(keyword IN keywords WHERE toLower(entity1.name) = toLower(keyword)
    #                       OR toLower(entity2.name) = toLower(keyword)
    #                       OR toLower(rel.name) = toLower(keyword))
    #             RETURN entity1, rel, entity2
    #      """
    # leads to 38.8% accuracy

    driver = neo4j_get_client()
    # log(query)
    # URI = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
    # expects NEO4J_USERNAME and NEO4J_PASSWORD in env
    # AUTH = (os.environ.get("NEO4J_USERNAME", "username"), os.environ.get("NEO4J_PASSWORD", "password"))
    # with GraphDatabase.driver(URI, auth=AUTH) as driver:
    s_time = time.time()
    records, summary, keys = driver.execute_query(query_=query, database_=db_name)
    # log(f"#results={len(records)}, neo4j query took: {time.time() - s_time:.2f} seconds")
    driver.close()
    return records


def neo4j_convert_result_triplets_to_df(triplets: list):
    triplet_rows = []
    for ent1, rel, ent2 in triplets:
        triplet = [item._properties['name'] for item in [ent1, rel, ent2]]
        r_textids = list(set(rel._properties["textids"]))
        triplet_rows.append([r_textids, *triplet])

    triplet_df = pd.DataFrame(triplet_rows, columns=["text_id", "head", "relation", "tail"])

    triplet_df = triplet_df.explode("text_id")
    return triplet_df




def neo4j_triplet_scorer(dfi, question):
    """
        Assign score to triplet based on overlapping components with question
        """
    score = 0
    for i, row in dfi.iterrows():
        triplet = (row["head"], row["relation"], row["tail"])
        intersection_score_map = {
            (1, 1, 1): 10,
            (1, 1, 0): 5,
            (0, 1, 1): 5,
            (1, 0, 1): 2,
            (1, 0, 0): 1,
            (0, 1, 0): 1,
            (0, 0, 1): 1,
        }
        question = question.lower()
        triplet_intersection = tuple([1 if item.lower() in question else 0 for item in triplet])
        score += intersection_score_map.get(triplet_intersection, 0)
    return score


def neo4j_triplet_rerankscorer(triplet_df, question, topk=-1):
    """
        Assign score to triplet based on overlapping components with question
    """
    if len(triplet_df) == 0:
        return pd.DataFrame()
    df_score         = triplet_df.groupby("text_id").apply(lambda dfi: neo4j_triplet_scorer(dfi, question=question)).reset_index()
    df_score = df_score.rename(columns={0: "score_rerank"})
    df_score = df_score.sort_values(by="score_rerank", ascending=False)
    topk = topk if topk > 0 else len(df_score)
    df_score = df_score.iloc[:topk, :]
    return df_score




def neo4j_search_docids(cfg=None, db_name="neo4j", query: str = "", model_keyword="en_core_web_sm", topk: int = 5):
    """Performs a search of (docid, doc_text) in a Neo4j database based on given query.
    Docs:
        Args:
            db_name (str ):  name of Neo4j database.     : "neo4j".
            query (str ):  search query.     : "".

        Returns:
            list: A list of dictionaries representing search results. Each dictionary contains following keys:
                - "id" (str):  ID of document.
                - "text" (str):  text content of document.
                - "score" (float):  score indicating relevance of document to search query.

        Notes:
            query -->Keyword extraction --> Build a cypher query based on those keywords 
                    --> Send cypher query to neo4j
                    ---> Get triplets
                    --> Extract doc_id for each triplet, Score(doc_id)= Frequency of found triplet.
                    --> Rank doc by score
                    --> Fetch actual text from doc_id using SQL, Sqlite.
                        --> return results SAME Format than Qdrant, tantiviy Engine
                                Engine 
                                TODO: Official return Format as DataClass



            -  search is performed by extracting keywords from query using `nlp_extract_keywords_from_text` function.
            -  search is performed in specified Neo4j database using `neo4j_search_triplets_bykeyword` function.
            -  search results are processed to retrieve document IDs and their corresponding scores using `neo4j_get_docs_from_triplets` function.
            -  text content of documents is fetched from a local database using `dbsql_fetch_text_by_doc_ids` function.
            -  relevance scores are assigned to records.
            -  records are sorted based on relevance scores in descending order.

        Example:
            >>> neo4j_search_docids(db_name="my_database", query="search query")
            [
                {
                    "id": "document1_id",
                    "text": "document1_text",
                    "score": 8
                },
                {
                    "id": "document2_id",
                    "text": "document2_text",
                    "score": 6
                },
                ...
            ]
    """
    global spacy_model
    if spacy_model is None:
        spacy_model = SpacyModel("en_core_web_sm")
    keyword_list = spacy_model.extract_keywords([query])
    keywords = keyword_list[0]

    triplet_list = neo4j_search_triplets_bykeyword(db_name=db_name, keywords=keywords)
    if len(triplet_list) == 0:
        return []

    triplet_df = neo4j_convert_result_triplets_to_df(triplet_list)  ### textid, head, rel, tail
    assert triplet_df[["text_id", "head", "relation", "tail"]].shape

    ##### re-ranking  ###########################
    df_textid_score = neo4j_triplet_rerankscorer(triplet_df, question=query, topk=topk)
    # df_doc_id_score = triplet_df.groupby("textid").apply(lambda dfi: neo4j_triplet_scorer(dfi, question=query))
    # docid_score_map = {doc_id: score for doc_id, score in df_textid_score.items()}

    textid_score_map = df_textid_score.set_index('text_id').to_dict(orient='index')
    textid_score_map = {str(k): v['score_rerank'] for k, v in textid_score_map.items()}
    text_ids = list(df_textid_score["text_id"].values)
    # log(f"text_ids: {text_ids}")

    #### Doc list
    doc_list = dbsql_fetch_text_by_doc_ids(text_ids=text_ids)
    for x in doc_list:
        x["score"] = textid_score_map[x["text_id"]]

    doc_list = sorted(doc_list, key=lambda x: x["score"], reverse=True)
    # doc_list = doc_list[:topk]
    # log(doc_list)
    return doc_list


# def z_neo4j_get_fuzzy_intersection_score(triplet: list, question: str):
#     """
#     Assign score to triplet based on overlapping components with question
#     """
#     assert len(triplet) == 3
#     intersection_score_map = {
#         (1, 1, 1): 10,
#         (1, 1, 0): 5,
#         (0, 1, 1): 5,
#         (1, 0, 0): 1,
#         (0, 1, 0): 1,
#         (0, 0, 1): 1,
#     }
#     question = question.lower()
#     triplet_intersection = tuple([1 if item.lower() in question else 0 for item in triplet])
#     final_score = intersection_score_map.get(triplet_intersection, 0)
#     return final_score


# def z_neo4j_rerank_docs_from_triplets(triplet_list: list, question: str, topk: int = -1) -> list:
#     """Get document IDs from neo4j results.
#     Args:
#         results (list): A list of tuples containing results.
#         topk (int ):  maximum number of document IDs to return.     : -1, which returns all document IDs.
#
#     Returns:
#         list: A list of document IDs.
#     """
#     text_ids = []
#     # log(f"len(results): {len(results)}")
#     for ent1, rel, ent2 in triplet_list:
#         triplet = [item._properties['name'] for item in [ent1, rel, ent2]]
#         fuzzy_intersection = neo4j_get_fuzzy_intersection_score(triplet, question)
#         r_textids = list(set(rel._properties["textids"]))
#
#         # increase corresponding docid count by their score. equivalent to weighting the docid when applying Counter
#         text_ids.extend(r_textids * fuzzy_intersection)
#
#     ###### Re-Rank by total weight accumulated  #################################
#     textid_counter = Counter(text_ids)
#     topk = len(textid_counter) if topk == -1 else topk
#
#     ### Scoring of doc_id by frequency.
#     text_ids = [(k, v) for k, v in textid_counter.most_common(topk)]
#     return text_ids

def neo4j_get_docs_from_triplets_v2(triplet_list: list, question: str, topk: int = -1) -> list:
    """Get document IDs from neo4j results.
    Args:
        results (list): A list of tuples containing results.
        topk (int ):  maximum number of document IDs to return.     : -1, which returns all document IDs.
        
        
        dataframe :
        
      ### normalize triplets into dataframe     
      df[[ "textid", "ent1", "rel", "ent2"]] 
        
        
      ### Re-ranking score
      df[[ "textid", "ent1", "rel", "ent2", "score_rerank]] 
      
      
      ### Topk  
      df =  df.sort_values(by="score_rerank", ascending=False)[["textid", "ent1", "rel", "ent2", "score_rerank"]][:topk]

      ### list of doc ids
      text_ids =  [(textid, score ) for  df[["textid", 'score_rerank']].values


    Returns:
        list: A list of document IDs.
    """
    text_ids = []
    # log(f"len(results): {len(results)}")
    for ent1, rel, ent2 in triplet_list:
        triplet = [item._properties['name'] for item in [ent1, rel, ent2]]
        fuzzy_intersection = neo4j_get_fuzzy_intersection_score(triplet, question)
        r_textids = list(set(rel._properties["textids"]))

        # increase corresponding docid count by their score. equivalent to weighting the docid when applying Counter
        text_ids.extend(r_textids * fuzzy_intersection)

    ###### Re-Rank by frequency  #################################
    textid_counter = Counter(text_ids)
    topk = len(textid_counter) if topk == -1 else topk

    ### Scoring of doc_id by frequency.    
    text_ids = [(k, v) for k, v in textid_counter.most_common(topk)]
    return text_ids




############ Client    ####################################
def neo4j_get_client(cfg=None, user=None, passw=None):
    from neo4j import GraphDatabase
    URI = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
    # expects NEO4J_USERNAME and NEO4J_PASSWORD in env
    AUTH = (os.environ.get("NEO4J_USERNAME", "username"), os.environ.get("NEO4J_PASSWORD", "password"))
    return GraphDatabase.driver(URI, auth=AUTH)








####################################################################################
#######  doc_id Storage  ###########################################################
def dbsql_fetch_text_by_doc_ids(db_path="./ztmp/db/db_sqlite/datasets.db",
                                table_name: str = "agnews",

                                cols=None,
                                text_ids: list = None) -> list:
    """Fetches text from a local SQLite database based on given document IDs.

    Args:
        db_name (str):  name of SQLite database file.     : "datasets.db".
        table_name (str):  name of table in database.     : "agnews".
        text_ids (list):  list of text IDs to fetch text for.     : None.

    Returns:
        list: A list of text strings corresponding to fetched document IDs.

    """
    cols = ['text_id, text'] if cols is None else cols
    colss = ",".join(cols)

    conn = sqlite3.connect(f"{db_path}")
    c = conn.cursor()

    text_ids = tuple([str(text_id) for text_id in text_ids])
    if len(text_ids) == 1:
        query = f"SELECT {colss} FROM {table_name} WHERE text_id = '{text_ids[0]}'"
    else:
        query = f"SELECT {colss} FROM {table_name} WHERE text_id IN {text_ids}"
    log(query)
    c.execute(query)

    # log(doc_ids)
    # query = f"SELECT id, text FROM {table_name} WHERE id IN {doc_ids}"
    headers = c.description
    results = c.fetchall()
    # zip headers with results
    results = [{headers[i][0]: row[i] for i in range(len(headers))} for row in results]
    # convert results to dict
    conn.close()
    # sort by original order of text_ids
    results = sorted(results, key=lambda x: text_ids.index(x["text_id"]))
    return results


def dbsql_fetch_text_by_doc_ids_sqlachemy(db_name="sqlite:///ztmp/db/db_sqlite/datasets.db",
                                          table_name="agnews", doc_ids=None, ):
    """Fetches text from a local SQL database based on given document IDs.

    Args:
        db_name (str):  name of SQLite database file.     : "datasets.db".
        table_name (str):  name of table in database.     : "agnews".
        doc_ids (list):  list of document IDs to fetch text for.     : None.

    Returns:
        list: A list of text strings corresponding to fetched document IDs.
    """
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.sql import select, column, table
    engine = create_engine(db_name)
    Session = sessionmaker(bind=engine)
    session = Session()

    # doc_ids     = tuple(doc_ids)  # Ensure doc_ids is a tuple
    # query_table = table(table_name, column('id'), column('text'))
    # query       = select([query_table]).where(column('id').in_(doc_ids))

    doc_ids = tuple([str(docid) for docid in doc_ids])  # Ensure doc_ids is a tuple
    raw_sql = text(f"SELECT id, text FROM {table_name} WHERE id IN :doc_ids")

    result = session.execute(raw_sql, {'doc_ids': doc_ids})
    results = [{column: value for column, value in zip(result.keys(), row)} for row in result.fetchall()]

    session.close()
    return results



def dbsql_table_exists(conn, table_name):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    existing_tables = [row[0] for row in cursor.fetchall()]
    return table_name in existing_tables


def dbsql_create_table(db_path="./ztmp/db/db_sqlite/datasets.db", table_name: str = "agnews", columns: dict = None):
    """
    Create a table in SQLite with the specified columns.
    Parameters:
    db_name (str): The name of the SQLite database file.
    table_name (str): The name of the table to create.
    columns (dict): A dictionary where keys are column names and values are the data types (e.g., "TEXT", "INTEGER").

    Example:
    create_table("example.db", "students", {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT",
        "age": "INTEGER",
        "grade": "REAL"
    })
    """
    conn = None
    from utilmy import os_makedirs
    os_makedirs(db_path) ### create if no exist
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        if columns is None:
            sql_query = f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        text_id VARCHAR(255) PRIMARY KEY,
                        text TEXT
                    )
                """
        else:
            # Create the SQL statement for creating the table
            columns_def = ", ".join([f"{col_name} {col_type}" for col_name, col_type in columns.items()])
            sql_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def});"
        cursor.execute(sql_query)

        conn.commit()
        print(f"Table '{table_name}' created successfully.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()


def dbsql_save_records_to_db(dirin="ztmp/bench/norm/ag_news/*/*.parquet",
                             db_path="./ztmp/db/db_sqlite/datasets.db",
                             table_name="agnews", coltext="text",
                             colscat:list = None,
                             colid="text_id", nrows: int = -1):
    """Saves records from a path of Parquet files to a local SQLite database.

    Args:
        dirin (str )     : path containing Parquet files.     : "ztmp/bench/norm/ag_news/*/*.parquet".
        db_path (str )   : path to SQLite database.     : "./ztmp/db/db_sqlite/datasets.db".
        table_name (str ): name of table in database.     : "agnews".
        coltext (str )   : name of column containing text. 
        colid (str )     : name of column containing text ID. 

    """
    df = pd_read_file(dirin)

    if colscat is None:
        colscat = []

    df = df[[colid, coltext, *colscat]]

    # log(len(df))
    if nrows > 0:
        df = df[:nrows]
    # create mysqlite instance
    os_makedirs(db_path)

    conn = sqlite3.connect(f"{db_path}")
    if dbsql_table_exists(conn, table_name) is False:
        dbsql_create_table(conn, table_name)

    # record_df.to_sql(table_name, conn, if_exists="append", index=False)
    # df = df.rename(columns={colid: "id", coltext: "text"})
    df["text_id"] = df["text_id"].astype("string")
    df.drop_duplicates(subset=["text_id"], keep="first", inplace=True)
    df.to_sql(table_name, conn, if_exists="append", index=False, chunksize=1000)




def dbsql_create_conn(db_uri="sqlite:///ztmp/db/db_sqlite/datasets.db"):
    if "sqlite:///" in db_uri:
        from sqlalchemy import create_engine
        engine = create_engine(db_uri)
        return engine

    elif ".db" in db_uri:
        conn = sqlite3.connect(db_uri)
        return conn








######################################################################################################
#######  Query generator from KG db triplet ##########################################################
def kg_generate_questions_from_triplets(dirin="ztmp/bench/ag_news/kg_triplets/agnews_kg_relation_test.parquet",
                                        dirout="ztmp/bench/ag_news/kg_questions/agnews_kg_question.parquet",
                                        nrows: int = 1000, batch_size: int = 5):
    """ Generate questions based on triplets extracted from a file --> Send to LLM  --> Get the questions
        dirin: Input file path containing triplets
        dirout: Output file path to save generated questions

           text_id          ,    Triplets                , question generated
        12276780668924807370,Turner,parent organization,Federal Mogul,  --->  Who is the parent organization of Federal Mogul?
        12276780668924807370,Federal Mogul,subsidiary,Turner,   -->  What is the subsidiary of Turner?
        12083816893608411777,TORONTO,country,Canada,            -->  What is the capital of Canada?

    """
    df = pd_read_file(dirin)
    df = df[["text_id", "head", "type", "tail"]]  ### Triplet Format
    df = df.drop_duplicates()
    df = df[:nrows]


    dfall = pd.DataFrame(columns=["text_id", "head", "type", "tail", "question"])
    for i in range(0, len(df), batch_size):
        df_subset = df[i:i + batch_size]

        #### Example for LLM Prompt :  |head|type|tail   |head|type|tail   
        triplet_str = "\n".join([f"{'|'.join([row.head, row.type, row.tail])}" for row in df_subset.itertuples()])

        #### Send Prompt + Triplets reference --> Generate questions from those triplets.
        prompt = f"For each triplet, generate a question based on triplet(head|type|tail):\n{triplet_str}"


        #### log(f"prompt: {prompt}")
        time.sleep(.6)  # sleep added to prevent ratelimiting
        response = llm_get_answer(prompt, model="gpt-3.5-turbo", max_tokens=1000)
        questions = response.split("\n")
        # log(f"questions: {questions}")


        #### clean up : remove preceeding numerical number
        questions = [q.split(".")[1].strip() if "." in q else q for q in questions]
        if len(questions) == len(df_subset):
            df_subset["question"] = questions
            dfall = pd.concat([dfall, df_subset])

    pd_to_file(dfall, dirout)
    # pd_to_file(dfall, dirout, index=False)  #### only for csv



######################################################################################################
#######  Metrics /benchmark ##########################################################
def metrics_kg_is_triplet_covered(triplet_tuple, question, answer):
    return all([k in question or k in answer for k in triplet_tuple])


def kg_benchmark_queries(dirin="ztmp/kg/data/agnews_kg_question.parquet",
                         dirout="ztmp/kg/data/agnews_kg_benchmark.parquet",
                         queries=1000):
    """
    Average time taken per query: 1.82 seconds
        Accuracy: 80% 

    """
    question_df = pd_read_file(dirin)
    result = []
    for row in question_df[:queries].itertuples():
        s_time = time.time()
        response = nebula_db_query(query=row.question)
        dt = time.time() - s_time

        is_correct = metrics_kg_is_triplet_covered([row.head, row.tail], row.question, response)
        result.append([row.question, response, dt, is_correct])

    df = pd.DataFrame(result, columns=["question", "response", "dt", "is_correct"])
    pd_to_file(df, dirout, index=False, show=1)
    log(f" Average time taken: {df.dt.mean():.2f} seconds")
    log(f" Percentage accuracy: {df.is_correct.mean() * 100:.2f} %")





###################################################################################################
if __name__ == "__main__":
    import fire

    fire.Fire()
    # results = neo4j_search_triplets_bykeyword(db_name="neo4j", keywords=["Casio Computer", 'magazine', 'United States'])
    # log(results)
    # df = pd_read_file("ztmp/bench/norm/ag_news/test/df_1.parquet")
    # log(df["id"])

