"""
    #### Install
        # NEbula installation
        Option 0 for machines with Docker: `curl -fsSL nebula-up.siwei.io/install.sh | bash`
        Option 1 for Desktop: NebulaGraph Docker Extension https://hub.docker.com/extensions/weygu/nebulagraph-dd-ext


    #### USAGE:
        cd asearch
        export PYTHONPATH="$(pwd)"  ### relative import issue
        alias pykg="python3 -u rag/engine_kg.py  "

        ###############################################
        ###### Triplet extractions
            #### Create test data using Wikipedia/LlamaIndex
            pykg test_create_test_data --dirout ztmp/kg/testraw.parquet

            ### Extract  triplets From raw text and save to csv
            pykg  kg_triplets_extract_v2  --dirin myraw.parquet --model_id Babelscape/rebel-large -- dirout ztmp/kg/data/kg_relation.parquet


            ### Extract triplet from  agnews Data --> Store in csv file  ( Need Rebel-Large to prevent empty triplet....)
            pykg  kg_triplets_extract_v2  --model_id Babelscape/rebel-large  --dirin ztmp/bench/norm/ag_news/test/df_*.parquet  --dirout ztmp/kg/data/agnews_kg_relation_test.parquet --coltxt body --nrows 1000000 --batch_size 25


        ###############################################
        ##### neo4j DB as KG
            #### Init

                export NEO4J_URI="neo4j://localhost:7687"
                export NEO4J_USERNAME="username"
                export NEO4J_PASSWORD="password"

                pykg neo4j_create_db --db_name "neo4j"


                #### Storage of text in SQL database: (long document is splitted into small chunks)
                   doc_id, text_id, text
                   ####
                      doc_id, cat1, cat2, cat3


            #### Generate test questions from Inverting from triplets (using LlamaIndex and GPT3.5 )
               pykg kg_generate_questions_from_triplets --dirin ztmp/kg/data/agnews_kg_relation.parquet --dirout ztmp/kg/data/agnews_kg_questions.parquet --batch_size 20


            #### Insert Triplet
            pykg neo4j_db_insert_triplet_file --dirin ztmp/kg/data/kg_relation.parquet --db_name "neo4j"  --nrows -1


            #### Neo4j Query
            https://github.com/neo4j/NaLLM




        ###############################################
        ##### Using Nebula DB as KG
            ##### Create schema : in Nebula   DB
                pykg nebula_db_create_schema  --space_name kg_relation

            ##### insert triplets to Nebula Graph
                pykg  nebula_db_insert_triplet_file --dirin ztmp/kg/data/kg_relation.parquet   --space_name kg_relation


            ##### search kg:  using LlamaIndex and nebula Graph
                pykg nebula_db_query --space_name "agnews_kg_relation" --query "What is capital of mexico ?"

            ##### benchmark queries using Nebula Graph
                 pykg kg_benchmark_queries --dirin ztmp/kg/data/agnews_kg_questions.parquet --dirout ztmp/kg/data/agnews_kg_benchmark.parquet --queries=1000



          #######################################
          ##### Data Model

                      text_cat1
                          modelid, task, ts, text_id, cat1, cat2, cat3, cat4,

                      text_cat2


    #### Data Format:

     triplet storage : df[["doc_id", "head", "type", "tail"]]
     question storage : df[["doc_id", "head", "type", "tail", "questions]



    #### Docs Info:
        KG has 2 query modes :
           A) Return list of triplets and ask LLM to generate answers from tiplets.

           B) Return List of documents doc_id and merge Fusion with other rankers
               neo4j_search_docids(db_name="neo4j", query: str = ""):


       B) Search on docid:
           pykg neo4j_search_docids --query "Who visited Chechnya?"
                #results=16, neo4j query took: 0.01 seconds


           query -->Keyword extraction --> Build a cypher query based on those keywords
                --> Send cypher query to neo4j
                ---> Get triplets
                --> Extract doc_id for each triplet, Score(doc_id)= Frequency of found triplet.
                --> Rank doc by score
                --> Fetch actual text from doc_id using SQL, Sqlite.
                    --> return results SAME Format than Qdrant, tantiviy Engine
                            Engine
                            TODO: Official return Format as DataClass.






   ### Docs
      Good Recipes for KG building
       https://faircookbook.elixir-europe.org/content/recipes/interoperability/nlp2kg/creating-knowledge-graph-from-text.html

   ### TODO :
      We want to fetch some documents ID, related to triplet of initial Question.

        Current with LllamaIndex :
             Natural Query --> NebulaGraph Cypher query --> Response in triplet --> Converted back in Natural questions (hallucination)


        ----> Use KG as Document Retriever (instead)
        What we to do (ie integrate with other engine)
             Natural Query --> NebulaGraph Cypher query --> Response in triplet
                    --> Add document related to triplets. ????

               (triplet:  (Person, president, Country) ) ---> List of Doc_id per triplet. (list)

                Check in Nebula to find doc_id related to triplet

                    Or we do external storage (ie parquet or sqlmy, duckdb like sqlite).


         A) Goal attache doc_id to edge A --> B : when can we can retrieve doc_id for RAG part (as retriever)

         B) You are saying:   we need just to retrieve triplets directly from KG query.

             Open discussion, dont worry:  Be good or bad, --> to find something reasonable.

           --> difference is
                  A) we have dense text (ie full sentences)  to feed LLM.
                  B) we have only relation  A do B) : "sparse info"  for LLM.

                  LLnm is better at transforming Dense text.

            My end goal is
              Use LLM with this prompt
                     you are a writer.

                     Reply to question
                          { my question }

                     Using ONLY context below
                          { context from RAG}
                                Doc_id --> Dense text all concatenated.

                                Graph -->  Sparse ()

           Did not have time to google search/phind how other people are doing....

           How LlamaIndex does ???
               Query to feed LLM: ???

                  List of Triplets, (by keywords)  --> Graph Schema and records as below

                  In LLM prompt

                     { queestion}

                     {graph Schema} : All relations and node type defintion.

                     {List of triples}

                   --> enough for LLm to repply...


            I think from my experience:
               graph DB can be used in both ways:
                   1) Only triplets and provide grpah triple to LLM.

                   2) Dense Doc_id retriever and provide doc_id + text to LLM.
                         Search Engine can be useful.

                    Investigate quickly and propose  a  simple plan
                       1)
                       2)
                       3)

                    will create different milestone


             Issues is database
                Nebulagraph looks incomplete, lack of funcitionnalities

                Neo4J : old DB but full of funcitonnalities + community support for bugs/workaround
                         (ie slower)

                 Need to check
                 You can ask phind to convert stuff...


                 Just double check if Neo4J can accept docid to edge...

                 List of edges --> docid    simple merge ( --> re-rank by frequency --> take top-10 docis)



   ### Insert agnews, create some test queries

       "what is capital of mexico ?"

        Method 1:
            ---> Go by triple extractor,  ---> get some triplet --> query directly triple


        def kg_query_...


        Method 2:
            ---> Extract keyword :
                    capital, mexico






    #### Goal to small proptopye of KG retrieval

    A) Indexer :  Extract Triplet (A, relation, B) from raw text --> store in database/NebulaGraph
                Alot of connected keyword. : normalize keywords, extra triplets


    B) query  :
        query --> extract keyword from query --> search in KG datas using keyword and relation around keyword
                --> hybrid with emebdding  -->

    ####
    Groq Engine : Cloud service Host llama3,
        very fast very cheap,  500 token/seconds,  Alternative to GPT 3.5  (cheaper/faster)



   ######## Re-ranking of KG results:


    Here are 10 re-ranking methodologies used for knowledge graph retrieval of documents and re-ranking of results:

    Query Graph Reranking - Refines the initial search results by reranking query graphs for improved knowledge base question answering 1.
    Embedding-based Models - Utilize embeddings to capture semantic and structural knowledge for re-ranking 412.
    Rule-induction and Subgraph-induction Methods - Employ rules and subgraphs to re-rank results 4.
    Language-based Models - Leverage language models to re-rank by calculating probabilities of candidates 412.
    Generative Relevance Feedback - Uses adaptive re-ranking with different first stages to find optimal graph traversal points 9.
    Normalized Relevance Score Display - Shows normalized [0..100] relevance scores next to each search result to indicate ranking distribution 10.
    Query Clarity Evaluation - Assesses clarity of document sets for re-ranking, regardless of how they are obtained 10.
    BERT-based Re-ranking - Applies BERT to score candidates by concatenating their textual forms with the query 12.
    Generative LLM-based Re-ranking - Utilizes generative language models to model the re-ranking process and generate candidate rankings 1213.
    Hybrid Search and Re-rank - Combines various search technologies and uses a rerank model to calculate relevance scores between query and documents for improved semantic sorting 14.
    The key is to refine initial search results using techniques like graph traversal, embeddings, rules, language models, relevance feedback, and hybrid approaches to deliver more accurate and relevant information 23514.


    ######################################################################################################
    #### Entity Extractor :

    https://github.com/zjunlp/DeepKE

    https://github.com/thunlp/OpenNRE

    https://github.com/zjunlp/KnowLM

    https://maartengr.github.io/BERTopic/getting_started/representation/representation.html#maximalmarginalrelevance



    1)
    Llamax -- use LLM + Prompt

    2) BERt like model to extract.(faster/cheaper)
    https://medium.com/nlplanet/building-a-knowledge-base-from-texts-a-full-practical-example-8dbbffb912fa

    pre-trained model.  --> with huggingFae directlyt.
        https://huggingface.co/Babelscape/mrebel-large


    3) ... NER extraction...



    Llama Index --> Nebula Graph




    without LLM, one way:
    https://medium.com/nlplanet/building-a-knowledge-base-from-texts-a-full-practical-example-8dbbffb912fa


    ####Groq is cheap/Fast for Llama3 Enitry extraction
        https://towardsdatascience.com/relation-extraction-with-llama3-models-f8bc41858b9e



    #### Questions Pairs
        https://huggingface.co/datasets/databricks/databricks-dolly-15k



    REBEL model

    https://huggingface.co/Babelscape/mrebel-large



    Building  KG graph index is  trickier part....

    https://github.com/wenqiglantz/llamaindex_nebulagraph_phillies/tree/main

    https://towardsdatascience.com/12-rag-pain-points-and-proposed-solutions-43709939a28c


    hacked  coedium engine to access by CLI (ie auto generate  docstring)


# Findings:
1. Number of triplets not dependent on text length but number of entities present in document.
2. Some times same information is being indexed in 2 triplets
Eg:
[[{'head': 'NASA', 'type': 'subsidiary', 'tail': 'Ames Research Center'}, {'head': 'Ames Research Center', 'type': 'parent organization', 'tail': 'NASA'}]]
This might lead to skewness in scoring.


##### REBEL findings:
        BAse model:  BART-large model
        Dataset: finetuning using REBEL-dataset.
        REBEL-dataset was prepared from wikipedia abstracts, Entities in the
        abstracts were linked to their corresponding  Wikidata entries. Candidate relations between those entities were picked
        from wikidata. Relations relevant to text were selected using Roberta model framing as text entailment problem.
        Eg:
        text <sep> relation_i  => entailment score
        if entailment score >0.75 then relation_i is relevant and becomes part of dataset else discarded and new candidate
        relation between those entities is considered.

        due to this method, we have *standard names* for relations:
        For eg:
        text: "Spain announce Davis Cup line-up Spain have named an unchanged team for the Davis Cup final against the United States in Seville on 3-5 December."
        relation: Davis Cup, Spain, participating team
        text: "Best Asian Tourism Destinations The new APMF survey of the best Asian tourism destinations has just kicked off,
        but it's crowded at the top, with Chiang Mai in Thailand just leading from perennial favourites Hong Kong,
        Bangkok and Phuket in Thailand, and Bali in  Indonesia."
        relation: Indonesia	Bali contains administrative territorial entity

        Due to use of standard relation, we get enough triplets per relation despite differnt text being used to represent that
        relation. Hence better fit as well as generalization in comparison to if we would have created relation just by using phrases
        in text.

        My opinion:
        Knowledge graphs are supposed to store facts about entities. For this to be done, the interpretation of entities need to
        be same across entire corpus. "Entity1"  should be grounded and represent same real world concept in all the triplets.
        This leads to triplet generation being heavily dependent on the named entities in the text. Named entities that are widely known
        and agreed upon. Common words like cat , city are often leftout in the triplet generation as their meaning is contextual
        and may differ across different tripets. Words like USA, Saudi, NASA etc are considered as named entities.
        Due to this constraint, KG retrieval is lossy in comparison to other search engines and their low performance is neither
        surprising nor does it mean that model isn"t performing enough. It means text doesnt have enough named entities due to
        which KG engine is blind to most of the information in text, which is very well captured in other search engines
        especially sparse.

##### Fine Tuning
    Input:
       The Philippine one hundred-peso note ( Filipino: "Sandaang Piso" ) ( ₱100 ) is a denomination of Philippine currency .

    Output:
                     entityA                         entityB ,   Relation
    <triplet> Philippine one hundred-peso note <subj> 100 <obj> face value</Tokytriplet>

    Create a dataset like this


    Many ways:
        Useful use case:

        1) Pick the bad sample, and ask GPT-4 to generate the triplets.
              List of scores from neo4J
                 top-k text
                 raw text


        3) unknown relation:
           1) sentences --> NER ---> (entA, entB, entC, entD)
                 (entA, entC) --> unknow_relation [ doc_id ]
               classify entX is relation or not.



            1) Create report
                looad darframe and topk > 5
                df_bad = df.topk> 5
                re-ranking is bias :

             2) minimal 5 samples dataset to fine rebel :
                 code running for fine tuning.




        2) Pre-defined database of data:  Reverse Engineer from the databse.
               How to generate the ground through, even imperfect.

            Domain field/knowledge:
               Databse
                    entitt ; Yes or NO
                    very rare word --> Databse --> indenfity as entiy
                    Biologu, Pharma: complicated word.
                      but you have the list of medical word --> entity

            Relation :
                 Fake relation, pseudi-true relation from database.
                 --> sample to FORCE the model to recognize those words AS entity.

               Force the entity artificallly.
               Force the relation artifically.

            database of event:
                    A  happens at th

            colA, colB, colC  (definition)  SQL to generate cola, colb, colc.
                 colA: entiy A
                 colab: entity B
                 colC: relation

            triplets --> sentences.
                Template sentence:
                    {Period}, {PersonA} visited {location}.
                    ....

               Ask GPT to reformulate while keeping same mearning.
               --> many sentences --> fine tuning.
               --> Know the ground thrught --> evaluate easily.



        3)  NER: un-supservised NER.
           sentences --> NER -->   {PersonA},  {actionB}  {locationC} .

             Classify the NER tag : 500 NER tags.. : classifty using GPT-4
                 NER-tag1 --> entity
                 NER-tag3 --> relation

            Parse the NER sentence :  remove the entiy {personA}
                 --> remaining NER : relation ot no.

        Example:
              Cat sat on the mat. : Un-parsed. by NER and Rebel.


        Step 1:
        Generate Text from Triplet in Database, using Manuakl Human Template

        Step 2:
        Generate variation of this text using GPt-4 (ie but meaning is SAME).



        Step3
        Feed all in the fine tuning model,

        Key idea is Step 1:
        We reverse generate sentence : Database --> Manual sentence using template.

        {Period}, {Person} visited {location} .

        Period: last year, yesterday,
        person; Obama, Clinton,/..
        location: USA, india, London,...

        We need to have some manual template,
        which FORCE the triplets and entity we want...

        ---> Force Rebel to recognize our domain field.









"""

if "import":
    import os, time, traceback, warnings, logging, sys, sqlite3
    from collections import Counter

    warnings.filterwarnings("ignore")

    import json, warnings, spacy, pandas as pd, numpy as np
    from dataclasses import dataclass

    ### KG
    from nebula3.Config import Config
    from nebula3.gclient.net import ConnectionPool
    from nebula3.common import *
    from neo4j import GraphDatabase

    # NLP
    from transformers import (pipeline)
    import spacy

    spacy_model = None

    ############################################
    from rag.llm import llm_get_answer

    from utilsr.utils_base import torch_getdevice, pd_append

    ## Uncomment this section for llamaindex llm call logs
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
    import llama_index.core

    llama_index.core.set_global_handler("simple")

    ############################################
    from utilmy import pd_read_file, os_makedirs, pd_to_file
    from utilmy import log




######################################################################################################
#######  DB Nebula Graph #############################################################################
def test_nebula_db_insert_triplet_file():
    """ A function to test if data is inserted into KKG DB

    """
    # check if data is inserted
    space_name = "test_kg_relation"
    client = nebula_db_get_client()
    nebula_db_create_schema(client=client, space_name=space_name)
    time.sleep(10)

    resp = client.execute(f"USE {space_name};")
    nebula_db_insert_triplet_file(dirin="data/kg_relation.parquet", space_name=space_name, nrows=10)
    time.sleep(10)

    resp_json = client.execute_json(f"MATCH (s)-[e]->(o) RETURN count(e) as count;")
    json_obj = json.loads(resp_json)
    # {'errors': [{'code': 0}], 'results': [{'spaceName': 'test_kg_relation', 'data': [{'meta': [None], 'row': [10]}], 'columns': ['count'], 'errors': {'code': 0}, 'latencyInUs': 4081}]}
    assert json_obj["results"][0]["data"][0]["row"][0] == 10
    # drop space
    resp = client.execute(f"DROP SPACE {space_name};")


def nebula_db_get_client(engine_name="nebula"):
    config = Config()
    connection_pool = ConnectionPool()
    assert connection_pool.init([('127.0.0.1', 9669)], config)
    # get session from  pool
    client = connection_pool.get_session('root', 'nebula')
    assert client is not None
    return client


def nebula_db_create_schema(client=None, space_name="kg_relation"):
    if client is None:
        client = nebula_db_get_client()
    resp = client.execute(
        f"CREATE SPACE {space_name}(vid_type=FIXED_STRING(256), partition_num=1, replica_factor=1);"
        f"USE {space_name};"
        "CREATE TAG entity(name string);"
        "CREATE EDGE relationship(relationship string);"
        "CREATE TAG INDEX entity_index ON entity(name(256));"
    )
    assert resp.is_succeeded(), resp.error_msg()


def nebula_db_insert_triplet(client=None, space_name="kg_relation", row=None):
    """
    Findings:
    https://docs.nebula-graph.io/2.6.1/3.ngql-guide/3.data-types/6.list/#opencypher_compatibility
    A composite data type (i.e., set, map, and list) CAN NOT be stored as properties for vertices or edges.
    It is recommended to modify graph modeling method.  composite data type should be modeled as an adjacent edge of a vertex, rather than its property. Each adjacent edge can be dynamically added or deleted.  rank values of adjacent edges can be used for sequencing.


    """
    resp = client.execute(f"USE {space_name};")
    assert resp.is_succeeded(), resp.error_msg()

    vertex_query = f"""INSERT VERTEX entity(name) VALUES "{row.head}":("{row.head}"), "{row.tail}":("{row.tail}")"""
    # log(vertex_query)
    resp = client.execute(vertex_query)
    assert resp.is_succeeded(), resp.error_msg()

    # edge query
    edge_query = f"""INSERT EDGE relationship(relationship) VALUES "{row.head}"->"{row.tail}":("{row.type}")"""

    # log(edge_query)
    resp = client.execute(edge_query)
    assert resp.is_succeeded(), resp.error_msg()


def nebula_db_insert_triplet_file(dirin="data/kg_relation.parquet", space_name="kg_relation", nrows: int = -1):
    """

    """
    df = pd_read_file(dirin)
    nrows = len(df) if nrows < 0 else nrows

    # create nebula client
    client = nebula_db_get_client()
    assert client is not None

    log("#### create schema ")
    client.execute(f"""USE {space_name};""")

    log("#### insert ")
    for row in df[:nrows].itertuples():
        nebula_db_insert_triplet(client=client, space_name=space_name, row=row)


##############  Query DB
def nebula_db_query(space_name="agnews_kg_relation", query="", db_type="nebula"):
    """A function to query knowledge graph database with specified space name and query string.

    LlamaIndex uses LLM GPt3.5
          Naturaal Query ---> KG Nebula queries.
          Required OPENAI TOKEN in env variable.

        Digged deeper into llama-index query calls.
        For each query it is calling llm 2 times:
        1. Extract keywords from llm query
        2. Fetch answer from db output triplets


    Issues: LLM is called every time to convert Natural Queries --> KG Nebula queries

            Find a way to generate Nebula query from llama Index.



    Args:
    - space_name (str):  name of space in knowledge graph database to query.
    - query (str):  query string to search in knowledge graph.

    """
    from llama_index.core import KnowledgeGraphIndex, StorageContext
    from llama_index.graph_stores.nebula import NebulaGraphStore

    if not query:
        return

    edge_types, rel_prop_names = ["relationship"], ["relationship"]
    tags = ["entity"]

    ### Init Databse
    # expects NEBULA_USER, NEBULA_PASSWORD, NEBULA_ADDRESS in environment variables
    graph_store = NebulaGraphStore(
        space_name=space_name,
        edge_types=edge_types,
        rel_prop_names=rel_prop_names,
        tags=tags,

    )
    # create storage context
    storage_context = StorageContext.from_defaults(graph_store=graph_store, )

    # fetch KG database index
    index = KnowledgeGraphIndex.from_documents(
        [],
        storage_context=storage_context,
        max_triplets_per_chunk=2,
        space_name=space_name,
        edge_types=edge_types,
        rel_prop_names=rel_prop_names,
        tags=tags,
    )
    query_engine = index.as_query_engine()

    # llm call here. adds network overhead to each query
    ### LLM is called to generate Natural query --> KG Query
    response = query_engine.query(query)
    return response.response

