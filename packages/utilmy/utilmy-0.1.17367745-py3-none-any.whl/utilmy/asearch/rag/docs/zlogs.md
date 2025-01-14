# kg query benchmarking
   ```bash
   # pyinstrument  engine_kg.py kg_benchmark_queries --dirin ztmp/kg/data/agnews_kg_question.csv --dirout ztmp/kg/data/agnews_kg_benchmark.csv --queries=5
   #ztmp/kg/data/agnews_kg_benchmark.csv
                                             question  ...        dt
   0  What is the relationship between Turner and Fe...  ...  2.298924
   1                What is the capital city of Canada?  ...  1.432849
   2  What is the connection between protein and ami...  ...  2.166291
   3  Who founded the Prediction Unit Helps Forecast...  ...  1.930334
   4  What jurisdiction does the smog-fighting agenc...  ...  1.739533

   [5 rows x 3 columns]
   Average time taken: 1.91 seconds

   _     ._   __/__   _ _  _  _ _/_   Recorded: 20:31:12  Samples:  6916
   /_//_/// /_\ / //_// / //_'/ //     Duration: 19.191    CPU time: 11.769
   /   _/                      v4.6.2

   Program: /home/ankush/workplace/fl_projects/myutil/.venv/bin/pyinstrument engine_kg.py kg_benchmark_queries --dirin ztmp/kg/data/agnews_kg_question.csv --dirout ztmp/kg/data/agnews_kg_benchmark.csv --queries=5

   19.185 <module>  engine_kg.py:1
   ├─ 10.191 Fire  fire/core.py:81
   │     [3 frames hidden]  fire
   │        10.139 _CallAndUpdateTrace  fire/core.py:661
   │        └─ 10.138 kg_benchmark_queries  engine_kg.py:502
   │           ├─ 9.568 kg_db_query  engine_kg.py:438
   │           │  ├─ 9.101 wrapper  llama_index/core/instrumentation/dispatcher.py:258
   │           │  │     [69 frames hidden]  llama_index, tenacity, openai, httpx,...
   │           │  │        4.789 _SSLSocket.read  <built-in>
   │           │  │        3.902 _SSLSocket.read  <built-in>
   │           │  └─ 0.311 KnowledgeGraphIndex.from_documents  llama_index/core/indices/base.py:105
   │           │        [10 frames hidden]  llama_index, tiktoken, tiktoken_ext
   │           └─ 0.382 pd_to_file  utilmy/ppandas.py:585
   │              └─ 0.359 collect  <built-in>
   ├─ 4.273 <module>  spacy/__init__.py:1
   │     [27 frames hidden]  spacy, thinc, torch, <built-in>, conf...
   ├─ 2.399 <module>  llama_index/core/__init__.py:1
   │     [39 frames hidden]  llama_index, openai, llama_index_clie...
   ├─ 1.957 <module>  spacy_component.py:1
   │  └─ 1.892 _LazyModule.__getattr__  transformers/utils/import_utils.py:1494
   │        [46 frames hidden]  transformers, importlib, accelerate, ...
   └─ 0.331 <module>  query.py:1
      └─ 0.320 <module>  dspy/__init__.py:1
            [6 frames hidden]  dspy, dsp, datasets

   To view this report with different options, run:
    pyinstrument --load-prev 2024-05-14T20-31-12 [options]
```







############ 15 May
```
# pykg kg_benchmark_queries --dirin ztmp/kg/data/agnews_kg_questions2.csv --dirout ztmp/kg/data/agnews_kg_benchmark2.csv --queries=20
ztmp/kg/data/agnews_kg_benchmark2.csv
                                             question  ... is_correct
0   Who founded the Prediction Unit that helps for...  ...      False
1   What jurisdiction does the smog-fighting agenc...  ...       True
2   What is an example of an instance of an open l...  ...       True
3                   What product does Sophos produce?  ...       True
4    How is FOAF used in the concept of web-of-trust?  ...       True
5   How does phishing relate to E-mail scam in ter...  ...       True
6    In which country is the Card fraud unit located?  ...       True
7   What type of product or material does STMicroe...  ...       True
8                  Who is the developer of Final Cut?  ...       True
9   Where is the headquarters of Free Record Shop ...  ...      False
10  Which country is the city of Melbourne located...  ...       True
11  How do socialites unite dolphin groups in term...  ...       True
12                 In what instance did the teenage T  ...      False
13  What is Ganymede an instance of within our sol...  ...       True
14  Which space agency operates the Mars Express s...  ...       True

[15 rows x 4 columns]
 Average time taken: 1.97 seconds
 Percentage accuracy: 80.00 %







 
```



#################################################################################
# Llama index graph query logs  using Nebula
```
# pykg kg_db_query --space_name "agnews_kg_relation" --query "Which country is the city of Melbourne located in?"

HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
** Messages: **
user: A question is provided below. Given the question, extract up to 10 keywords from the text. Focus on extracting the keywords that we can use to best lookup answers to the question. Avoid stopwords.
---------------------
Which country is the city of Melbourne located in?
---------------------
Provide keywords in the following comma-separated format: 'KEYWORDS: <keywords>'

**************************************************
** Response: **
assistant: KEYWORDS: country, city, Melbourne, located
**************************************************


Index was not constructed with embeddings, skipping embedding usage...
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
** Messages: **
system: You are an expert Q&A system that is trusted around the world.
Always answer the query using the provided context information, and not prior knowledge.
Some rules to follow:
1. Never directly reference the given context in your answer.
2. Avoid statements like 'Based on the context, ...' or 'The context information ...' or anything along those lines.
user: Context information is below.
---------------------
kg_schema: {'schema': "Node properties: [{'tag': 'entity', 'properties': [('name', 'string')]}]\nEdge properties: [{'edge': 'relationship', 'properties': [('relationship', 'string')]}]\nRelationships: ['(:entity)-[:relationship]->(:entity)']\n"}

The following are knowledge sequence in max depth 2 in the form of directed graph like:
`subject -[predicate]->, object, <-[predicate_next_hop]-, object_next_hop ...`
Melbourne{name: Melbourne} -[relationship:{relationship: country}]-> Australia{name: Australia} <-[relationship:{relationship: country}]- Virgin Blue{name: Virgin Blue}


Melbourne{name: Melbourne} -[relationship:{relationship: country}]-> Australia{name: Australia} <-[relationship:{relationship: country}]- CANBERRA{name: CANBERRA}

Melbourne{name: Melbourne} -[relationship:{relationship: country}]-> Australia{name: Australia} <-[relationship:{relationship: country}]- Dow Jones{name: Dow Jones}

Melbourne{name: Melbourne} -[relationship:{relationship: country}]-> Australia{name: Australia} <-[relationship:{relationship: country}]- Sons Of Gwalia{name: Sons Of Gwalia}

Melbourne{name: Melbourne} -[relationship:{relationship: country}]-> Australia{name: Australia} <-[relationship:{relationship: country of citizenship}]- Jana Pittman{name: Jana Pittman}

Melbourne{name: Melbourne} -[relationship:{relationship: country}]-> Australia{name: Australia} <-[relationship:{relationship: country}]- Australia Police to Trap Cyberspace Pedophiles{name: Australia Police to Trap Cyberspace Pedophiles}
Melbourne{name: Melbourne} -[relationship:{relationship: country}]-> Australia{name: Australia} <-[relationship:{relationship: member of sports team}]- Andrew Symonds{name: Andrew Symonds}
Melbourne{name: Melbourne} -[relationship:{relationship: country}]-> Australia{name: Australia} <-[relationship:{relationship: country of citizenship}]- Nathan Baggaley{name: Nathan Baggaley}
Melbourne{name: Melbourne} -[relationship:{relationship: country}]-> Australia{name: Australia} <-[relationship:{relationship: country}]- Sons of Gwalia{name: Sons of Gwalia}
Melbourne{name: Melbourne} -[relationship:{relationship: country}]-> Australia{name: Australia} <-[relationship:{relationship: country}]- Seven Network Ltd{name: Seven Network Ltd}
Melbourne{name: Melbourne} -[relationship:{relationship: country}]-> Australia{name: Australia} <-[relationship:{relationship: country}]- PERTH{name: PERTH}
Melbourne{name: Melbourne} -[relationship:{relationship: country}]-> Australia{name: Australia} <-[relationship:{relationship: country of citizenship}]- Rod Eddington{name: Rod Eddington}
Melbourne{name: Melbourne} -[relationship:{relationship: country}]-> Australia{name: Australia}
Melbourne{name: Melbourne} -[relationship:{relationship: country}]-> Australia{name: Australia} <-[relationship:{relationship: country}]- Qantas Airways{name: Qantas Airways}
Melbourne{name: Melbourne} -[relationship:{relationship: country}]-> Australia{name: Australia} <-[relationship:{relationship: country}]- SYDNEY{name: SYDNEY}
---------------------
Given the context information and not prior knowledge, answer the query.
Query: Which country is the city of Melbourne located in?
Answer: 
**************************************************
** Response: **
assistant: Australia
**************************************************


Australia
```














#########################################################################################

# neo4j triplet insertion
```
# pykg neo_db_insert_triplet_file --dirin ztmp/kg/data/kg_relation.csv --db_name "neo4j" 
 #triples: 1627, total time taken : 8.34 seconds
```

# neo4j + sqlite search
```
pykg neo4j_search --query "Who visited Chechnya?"
#results=16, neo4j query took: 0.01 seconds


query -->Keyword extraction --> Build a cypher query based on those keywords 
         --> Send the cypher query to neo4j
         ---> Get the triplets
         --> Extract the doc_id for each triplet, Score(doc_id)= Frequency of found triplet.
         --> Rank the doc by score
         --> Fetch actual text from the doc_id using SQL, Sqlite.
            --> return results SAME Format than Qdrant, tantiviy Engine
                    Engine 
                    TODO: Official return Format as DataClass.



{"id": "11374492112337794267", "text": "Putin Visits Chechnya Ahead of Election (AP) AP - Russian President Vladimir Putin made an unannounced visit to Chechnya on Sunday, laying flowers at the grave of the war-ravaged region's assassinated president a week before elections for a new leader.", "score": 8}

{"id": "10877731205540525455", "text": "New Chechen Leader Vows Peace, Poll Criticized  GROZNY, Russia (Reuters) - Chechnya's new leader vowed on  Monday to rebuild the shattered region and crush extremists,  after winning an election condemned by rights groups as a  stage-managed show and by Washington as seriously flawed.", "score": 4}

{"id": "12707266912853963705", "text": "Report: Explosion Kills 2 Near Chechyna (AP) AP - An explosion rocked a police building in the restive Dagestan region adjacent to Chechnya on Friday, and initial reports indicated two people were killed, the Interfax news agency said.", "score": 4}



```

# neo4j benchmarking indexing
```
   # pybench bench_v1_create_neo4j_indexes --nrows 20 --nqueries 20
   Model loaded in 6.82 seconds
   ./ztmp/bench/ag_news/kg_triplets/agnews_kg_relation_btest.csv
                     doc_id  ... info_json
   0   10031470251246589555  ...        {}
   1   10031470251246589555  ...        {}
   2   10031470251246589555  ...        {}
   3   13455116945363191971  ...        {}
   4   13380278105912448845  ...        {}
   5   13380278105912448845  ...        {}
   6    9690454179506583527  ...        {}
   7    9690454179506583527  ...        {}
   8    9690454179506583527  ...        {}
   9   13400249423693784533  ...        {}
   10  13400249423693784533  ...        {}
   11  13400249423693784533  ...        {}
   12  13400249423693784533  ...        {}
   13  13400249423693784533  ...        {}
   14  13400249423693784533  ...        {}
   15  10109972785024178695  ...        {}
   16  10572039232808661934  ...        {}
   17  12910890402456928629  ...        {}
   18  12910890402456928629  ...        {}
   19  12910890402456928629  ...        {}
   20  12910890402456928629  ...        {}
   21   9242928626256260421  ...        {}
   22  11247699813360322535  ...        {}
   23  11247699813360322535  ...        {}
   24  11247699813360322535  ...        {}
   25  11247699813360322535  ...        {}
   26  10088096453294362961  ...        {}
   27  10088096453294362961  ...        {}
   28   9276327214733141092  ...        {}
   29  10917529063570538043  ...        {}
   30  11675024175008667160  ...        {}
   31  11675024175008667160  ...        {}
   32  11675024175008667160  ...        {}
   33  11323664445954829208  ...        {}
   34  11323664445954829208  ...        {}
   35  12516784955453086101  ...        {}
   36  11404701768767769131  ...        {}
   37  11404701768767769131  ...        {}
   38  11404701768767769131  ...        {}
   39  11404701768767769131  ...        {}
   40  10480879870885068149  ...        {}
   41  12209054350654622309  ...        {}
   42  12209054350654622309  ...        {}
   43  12209054350654622309  ...        {}
   44  13086739540453328833  ...        {}

   [45 rows x 5 columns]
   Extracted triplets from #20,  dt exec: 20.385884046554565

   ####### Generate questions from triplets ############################
   HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
   HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
   HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
   HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
   ztmp/kg/data/agnews_kg_bquestion.csv
   (20, 5)
   Generated questions from triplets,  dt exec: 10.212386846542358

####### Save records to DBSQL ######################################
Saved #20 records to sqlite,  dt exec: 0.4380199909210205

####### Insert Triplet into neo4j ##################################
 #triplet inserted: 1 / 45,  time : 0.09 seconds
Inserted triplets into neo4j,  dt exec: 0.31346702575683594

```



#######################################################################
# neo4j benchmarking run
   ```


   # pybench bench_v1_neo4j_run --dirout "ztmp/bench" --topk 5 --dataset "ag_news" --dirquery "ztmp/kg/data/agnews_kg_bquestion.csv"

   {'name': 'bench_v1_neo4j_run', 'dirquery': 'ztmp/kg/data/agnews_kg_bquestion.csv', 'dirout2': 'ztmp/bench/ag_news/neo4j/20240531/200902/'}
   ztmp/bench/ag_news/neo4j/20240531/200902//dfmetrics.csv
                        id istop_k        dt
   0   10031470251246589555       1  0.339181
   1   10031470251246589555       1  0.015657
   2   10031470251246589555       1  0.015347
   3   13455116945363191971       0  0.015977
   4   13380278105912448845       1  0.018131
   5   13380278105912448845       1  0.016992
   6    9690454179506583527       1  0.017252
   7    9690454179506583527       1  0.016205
   8    9690454179506583527       1  0.016251
   9   13400249423693784533       1  0.016096
   10  13400249423693784533       1  0.016939
   11  13400249423693784533       1  0.017772
   12  13400249423693784533       0  0.014174
   13  13400249423693784533       0  0.014077
   14  13400249423693784533       1  0.014585
   15  10109972785024178695       1  0.016232
   16  10572039232808661934       1  0.017043
   17  12910890402456928629       0  0.015937
   18  12910890402456928629       1  0.014980
   19  12910890402456928629       1  0.016215
   Avg time per request 0.03225210905075073
   Percentage accuracy 80.0



   ```












#################################################################################
######## Benchmark with 20k text_id
   ```bash
   #### All alias/shorcuts
      source rag/zshorcuts.sh
      export dir0="ztmp/bench/ag_news"


   ########### Steps commands
   ##### Download data from drive
         #1.  download triplet files(*.parquet) from drive into ztmp/bench/ag_news/kg_triplets
               https://drive.google.com/drive/u/0/folders/1QEoR4YGBmoMS9hrZqmNqaqc5A02tllBw 

         # 2. Download corresponding data file(train_120000.parquet) from drive into ztmp/bench/ag_news/aparquet
               https://drive.google.com/drive/u/0/folders/1SOfvpVlIXDXCeMnRmk7B8xzZ3zRyNevl

   
      ##### neo4j  Insert/Indexing
         # 3. add data into sqlite
         pykg dbsql_save_records_to_db --dirin "$dir0/aparquet/*.parquet" --db_path "./ztmp/db/db_sql/datasets.db" --table_name "agnews"


         # 4. insert triplets into neo4j
         pykg neo4j_db_insert_triplet_file --dirin "$dir0/kg_triplets/*.parquet" --db_name "neo4j"


      ###### 5. generate questions from triplets
         pykg kg_generate_questions_from_triplets --dirin "$dir0/kg_triplets/*.parquet" --dirout="$dir0/kg_questions/common_test_questions.parquet" --nrows 100 --batch_size 5




      ###### 6. qdrant dense Insert indexing
         pybench bench_v1_create_dense_indexes --dirbench "$dir0" --dataset "ag_news" 


      ###### 7. qdrant sparse indexing
         pybench bench_v1_create_sparse_indexes --dirbench "$dir0" --dataset "ag_news" 



      ##### runs Benchmark 
         echo -e "\n\n####### Benchmark Results " >> rag/zlogs.md
         echo '```bash ' >> rag/zlogs.md 
   
   
         echo -e '\n########## sparse run' >> rag/zlogs.md 
         pybench bench_v1_sparse_run --dirquery "$dir0/kg_questions/common_test_questions.parquet" --topk 5 >> rag/zlogs.md


         echo -e '\n########## dense run' >> rag/zlogs.md 
         pybench bench_v1_dense_run --dirquery "$dir0/kg_questions/common_test_questions.parquet" --topk 5 >> rag/zlogs.md
         echo '```' >> rag/zlogs.md

         echo -e '\n########## neo4j run' >> rag/zlogs.md 
         pybench bench_v1_neo4j_run --dirquery "$dir0/kg_questions/common_test_questions.parquet" --topk 5 >> rag/zlogs.md


```




 ######  Benchmark Results with 20k text_id
 ```bash


      Comments:
         topk=20  ---> neo4J :  40% --> 60% icnrease
              Idea : some frequent keywords in triplets, go into the results at higher rank.
                   Issues with keywords and triplets matching,
                       --> Neo4J query:  list of doc_id with those triplet containing keyword.
                            keywords -->  fund all triplets where node == kwyrods

                           WITH {keywords} AS keywords
                                       MATCH (entity1)-[rel]-(entity2)
                                       WHERE any(keyword IN keywords WHERE entity1.name CONTAINS keyword 
                                                OR entity2.name CONTAINS keyword 
                                                OR type(rel) CONTAINS keyword)
                                       RETURN entity1, rel, entity2

                     High frequency keywords ---> Higher rank level.

                        TODO: TD-IDF for graph query.... --> reduce frequency frequency



             




      # neo4j run
      # pybench bench_v1_neo4j_run --dirquery ztmp/kg_questions/common_test_questions.parquet --topk 5
      {'name': 'bench_v1_neo4j_run', 'dirquery': 'ztmp/kg_questions/common_test_questions.parquet', 'dirout2': '$dir0/neo4j/20240606/212259/'}
      ztmp/bench/ag_news/neo4j/20240606/212259//dfmetrics.csv
                            id istop_k        dt
      0   14504362844448484081       0  1.780451
      1    5685638213467219607       1  0.157204
      2    5685638213467219607       1  0.141164
      3   13995111925969122086       0  0.106682
      4     638355261286711537       0  0.154347
      ..                   ...     ...       ...
      85  14651180087730350534       0  0.088991
      86  14114327028645677270       1  0.061864
      87  12985424926102133910       0  0.064829
      88   1217961636799403930       1  0.047790
      89   1217961636799403930       1  0.072322

      [90 rows x 3 columns]
      Avg time per request 0.1170915789074368
      Percentage accuracy 40.0



      ## sparse run
      # pybench bench_v1_sparse_run --dirquery ztmp/kg_questions/common_test_questions.parquet --topk 5
      {'name': 'bench_v1_sparse_run', 'server_url': 'http://localhost:6333', 'collection_name': 'hf-ag_news-sparse', 'model_type': 'stransformers', 'model_id': 'naver/efficient-splade-VI-BT-large-query', 'topk': 5, 'dataset': 'ag_news', 'dirquery': 'ztmp/kg_questions/common_test_questions.parquet', 'dirdata2': 'ztmp/bench/norm//ag_news/', 'dirout2': 'ztmp/bench/ag_news/sparse/20240606/212516/'}
      ztmp/bench/ag_news/sparse/20240606/212516//dfmetrics.csv
                            id istop_k        dt
      0   14504362844448484081       1  0.525815
      1    5685638213467219607       1  0.013314
      2    5685638213467219607       1  0.015434
      3   13995111925969122086       1  0.015568
      4     638355261286711537       1  0.014567
      ..                   ...     ...       ...
      85  14651180087730350534       0  0.013839
      86  14114327028645677270       1  0.011379
      87  12985424926102133910       0  0.013664
      88   1217961636799403930       0  0.011786
      89   1217961636799403930       1  0.011545

      [90 rows x 3 columns]
      Avg time per request 0.01991731325785319
      Percentage accuracy 70.0


      ## dense run
      # pybench bench_v1_dense_run --dirquery ztmp/kg_questions/common_test_questions.parquet --topk 5
      {'name': 'bench_v1_dense_run', 'server_url': 'http://localhost:6333', 'collection_name': 'hf-ag_news-dense', 'model_type': 'stransformers', 'model_id': 'sentence-transformers/all-MiniLM-L6-v2', 'topk': 5, 'dataset': 'ag_news', 'dirquery': 'ztmp/kg_questions/common_test_questions.parquet', 'dirdata2': 'ztmp/bench/norm//ag_news/', 'dirout2': 'ztmp/bench//ag_news/dense/20240606/212617/'}
      ztmp/bench//ag_news/dense/20240606/212617//dfmetrics.csv
                            id istop_k        dt
      0   14504362844448484081       0  0.567876
      1    5685638213467219607       1  0.011049
      2    5685638213467219607       1  0.013134
      3   13995111925969122086       1  0.013515
      4     638355261286711537       1  0.010795
      ..                   ...     ...       ...
      85  14651180087730350534       0  0.009513
      86  14114327028645677270       1  0.011034
      87  12985424926102133910       0  0.010191
      88   1217961636799403930       0  0.009401
      89   1217961636799403930       1  0.010396

      [90 rows x 3 columns]
      Avg time per request 0.016837151845296223
      Percentage accuracy 55.55555555555556









#######################################################################
### rerun topk=20 ; Neo-4J
topk=20 issues, 




{'name': 'bench_v1_neo4j_run', 'dirquery': 'ztmp/bench/ag_news/kg_questions/common_test_questions.parquet', 'dirout2': 'ztmp/bench/ag_news/neo4j/20240608/230004/'}
ztmp/bench/ag_news/neo4j/20240608/230004//dfmetrics.csv
                      id istop_k        dt
0   14504362844448484081       0  0.641470
1    5685638213467219607       1  0.107558
2    5685638213467219607       1  0.099028
3   13995111925969122086       0  0.083485
4     638355261286711537       0  0.238768
..                   ...     ...       ...
85  14651180087730350534       0  0.066895
86  14114327028645677270       1  0.052804
87  12985424926102133910       1  0.051527
88   1217961636799403930       1  0.037039
89   1217961636799403930       1  0.062341

[90 rows x 3 columns]
 Avg time per request 0.11823943191104465
 Percentage accuracy 62.22222222222222






```



####### Benchmark Results 2024-06-17
```bash 
# generate new set of question from recent triplets
# pykg kg_generate_questions_from_triplets --dirin "$dir0/kg_triplets/22000-110000/*.parquet" --dirout="$dir0/kg_questions/common_test_questions_2.parquet" --nrows 100 --batch_size 5
########## neo4j run

# pybench bench_v1_neo4j_run --dirquery "$dir0/kg_questions/common_test_questions_2.parquet" --topk 5
{'name': 'bench_v1_neo4j_run', 'db_name': 'neo4j', 'dirquery': 'ztmp/bench/ag_news/kg_questions/common_test_questions_2.parquet', 'topk': 5, 'dataset': 'ag_news', 'dirout2': 'ztmp/bench/ag_news/neo4j/20240617/172056/'}
ztmp/bench/ag_news/neo4j/20240617/172056//dfmetrics.csv
                      id  ...     topk_scores
0    7734731680092540458  ...       4;4;4;4;4
1   12853638687837549767  ...       4;4;4;4;2
2   12853638687837549767  ...       6;6;6;4;4
3   16463793264455698705  ...  30;20;20;20;20
4    9277218100981699866  ...  30;20;20;20;20
..                   ...  ...             ...
60  11777848068937089959  ...       4;4;4;2;2
61    140469146415434618  ...       2;0;0;0;0
62  16407429281338915589  ...       4;4;2;2;2
63   3831132033380471085  ...     12;10;2;0;0
64   2691452368464191376  ...      10;2;2;2;2

[65 rows x 5 columns]
 Avg time per request 0.7103601088890663
 Percentage accuracy 61.53846153846154
```

####### fusion search logs
```
# python3 -u rag/engine_tv.py fusion_search --engine "sparse;dense;neo4j" --query "Who visited Chechnya>" --sparse_collection_name "hf-ag_news-sparse" --neo4j_db "neo4j" --dense_collection_name "hf-ag_news-dense" >> zlogs.md
HTTP Request: POST http://localhost:6333/collections/hf-ag_news-sparse/points/search "HTTP/1.1 200 OK"
Load pretrained SentenceTransformer: sentence-transformers/all-MiniLM-L6-v2
HTTP Request: POST http://localhost:6333/collections/hf-ag_news-dense/points/search "HTTP/1.1 200 OK"
run1:{q1: {4042207707108614244: 15.631433, 5283639422326824928: 15.435244, 13197567356641911344: 14.992202, 14937375287959487855: 14.831325, 2346769977753868497: 14.691949, 9097903450681106261: 13.87503, 1741852716021254813: 13.555105, 6741625146711625673: 13.370424, 17772725353915623548: 13.11262, 10900184541790497595: 12.980857}}
run2:{q1: {16517502651416274317: 0.40867466, 17280717165267516960: 0.39047682, 9457184493632663730: 0.3875, 12397832442631840539: 0.3827278, 8923100775104352814: 0.37015992, 14146638733778411503: 0.34501606, 8595434367602701156: 0.33486956, 2808737594375873940: 0.33046424, 3060911402199620019: 0.32612884, 17272607382840065365: 0.31855467, 16745185348317506776: 0.31590015, 12009060545561261913: 0.3151488, 13379428298313459029: 0.31447226, 16304710489980316739: 0.3123745, 14000566064935350207: 0.310791, 13137402573555859559: 0.30485493, 5858419950996757231: 0.30179247, 989755633787334206: 0.3011472, 2068107485204052242: 0.300604, 2663934906491212978: 0.29956862}}
{q1: {4042207707108614244: 0.01639344262295082, 16517502651416274317: 0.01639344262295082, 5283639422326824928: 0.016129032258064516, 17280717165267516960: 0.016129032258064516, 13197567356641911344: 0.015873015873015872, 9457184493632663730: 0.015873015873015872, 14937375287959487855: 0.015625, 12397832442631840539: 0.015625, 8923100775104352814: 0.015384615384615385, 2346769977753868497: 0.015384615384615385, 9097903450681106261: 0.015151515151515152, 14146638733778411503: 0.015151515151515152, 1741852716021254813: 0.014925373134328358, 8595434367602701156: 0.014925373134328358, 6741625146711625673: 0.014705882352941176, 2808737594375873940: 0.014705882352941176, 17772725353915623548: 0.014492753623188406, 3060911402199620019: 0.014492753623188406, 17272607382840065365: 0.014285714285714285, 10900184541790497595: 0.014285714285714285, 16745185348317506776: 0.014084507042253521, 12009060545561261913: 0.013888888888888888, 13379428298313459029: 0.0136986301369863, 16304710489980316739: 0.013513513513513514, 14000566064935350207: 0.013333333333333334, 13137402573555859559: 0.013157894736842105, 5858419950996757231: 0.012987012987012988, 989755633787334206: 0.01282051282051282, 2068107485204052242: 0.012658227848101266, 2663934906491212978: 0.0125}}
run1:{q1: {4042207707108614244: 0.01639344262295082, 16517502651416274317: 0.01639344262295082, 5283639422326824928: 0.016129032258064516, 17280717165267516960: 0.016129032258064516, 13197567356641911344: 0.015873015873015872, 9457184493632663730: 0.015873015873015872, 14937375287959487855: 0.015625, 12397832442631840539: 0.015625, 8923100775104352814: 0.015384615384615385, 2346769977753868497: 0.015384615384615385, 9097903450681106261: 0.015151515151515152, 14146638733778411503: 0.015151515151515152, 1741852716021254813: 0.014925373134328358, 8595434367602701156: 0.014925373134328358, 2808737594375873940: 0.014705882352941176, 6741625146711625673: 0.014705882352941176, 17772725353915623548: 0.014492753623188406, 3060911402199620019: 0.014492753623188406, 17272607382840065365: 0.014285714285714285, 10900184541790497595: 0.014285714285714285, 16745185348317506776: 0.014084507042253521, 12009060545561261913: 0.013888888888888888, 13379428298313459029: 0.0136986301369863, 16304710489980316739: 0.013513513513513514, 14000566064935350207: 0.013333333333333334, 13137402573555859559: 0.013157894736842105, 5858419950996757231: 0.012987012987012988, 989755633787334206: 0.01282051282051282, 2068107485204052242: 0.012658227848101266, 2663934906491212978: 0.0125}}
run2:{q1: {17723054465584663280: 2.0, 10006659569642520126: 0.0, 3542599019457019555: 0.0, 5149981321830021713: 0.0, 5021084954091111846: 0.0}}
{q1: {4042207707108614244: 0.01639344262295082, 17723054465584663280: 0.01639344262295082, 16517502651416274317: 0.016129032258064516, 10006659569642520126: 0.016129032258064516, 5283639422326824928: 0.015873015873015872, 3542599019457019555: 0.015873015873015872, 17280717165267516960: 0.015625, 5149981321830021713: 0.015625, 5021084954091111846: 0.015384615384615385, 13197567356641911344: 0.015384615384615385, 9457184493632663730: 0.015151515151515152, 14937375287959487855: 0.014925373134328358, 12397832442631840539: 0.014705882352941176, 8923100775104352814: 0.014492753623188406, 2346769977753868497: 0.014285714285714285, 9097903450681106261: 0.014084507042253521, 14146638733778411503: 0.013888888888888888, 1741852716021254813: 0.0136986301369863, 8595434367602701156: 0.013513513513513514, 2808737594375873940: 0.013333333333333334, 6741625146711625673: 0.013157894736842105, 17772725353915623548: 0.012987012987012988, 3060911402199620019: 0.01282051282051282, 17272607382840065365: 0.012658227848101266, 10900184541790497595: 0.0125, 16745185348317506776: 0.012345679012345678, 12009060545561261913: 0.012195121951219513, 13379428298313459029: 0.012048192771084338, 16304710489980316739: 0.011904761904761904, 14000566064935350207: 0.011764705882352941, 13137402573555859559: 0.011627906976744186, 5858419950996757231: 0.011494252873563218, 989755633787334206: 0.011363636363636364, 2068107485204052242: 0.011235955056179775, 2663934906491212978: 0.011111111111111112}}


4042207707108614244:  0.01639344262295082
17723054465584663280: 0.01639344262295082
16517502651416274317: 0.016129032258064516
10006659569642520126: 0.016129032258064516
5283639422326824928:  0.015873015873015872
3542599019457019555:  0.015873015873015872
17280717165267516960: 0.015625
5149981321830021713:  0.015625
5021084954091111846:  0.015384615384615385
13197567356641911344: 0.015384615384615385
9457184493632663730:  0.015151515151515152
14937375287959487855: 0.014925373134328358
12397832442631840539: 0.014705882352941176
8923100775104352814:  0.014492753623188406
2346769977753868497:  0.014285714285714285
9097903450681106261:  0.014084507042253521
14146638733778411503: 0.013888888888888888
1741852716021254813:  0.0136986301369863
8595434367602701156:  0.013513513513513514
2808737594375873940:  0.013333333333333334
6741625146711625673:  0.013157894736842105
17772725353915623548: 0.012987012987012988
3060911402199620019:  0.01282051282051282
17272607382840065365: 0.012658227848101266
10900184541790497595: 0.0125
16745185348317506776: 0.012345679012345678
12009060545561261913: 0.012195121951219513
13379428298313459029: 0.012048192771084338
16304710489980316739: 0.011904761904761904
14000566064935350207: 0.011764705882352941
13137402573555859559: 0.011627906976744186
5858419950996757231:  0.011494252873563218
989755633787334206:   0.011363636363636364
2068107485204052242:  0.011235955056179775
2663934906491212978:  0.011111111111111112
```


##### Fusion Benchmarks 
```
# sparse + neo4j
# pybench bench_v1_fusion_run --engine "sparse;neo4j" --dirquery ztmp/bench/ag_news/kg_questions/common_test_questions.parquet >> rag/zlogs.md
{'name': 'bench_v1_fusion_run', 'engine': 'sparse;neo4j', 'qdrant_url': 'http://localhost:6333', 'sparse_collection_name': 'hf-ag_news-sparse', 'dense_collection_name': 'hf-ag_news-dense', 'tantivy_datapath': './ztmp/tantivy_index', 'neo4j_db': 'neo4j', 'model_type': 'stransformers', 'model_id': 'sentence-transformers/all-MiniLM-L6-v2', 'topk': 5, 'dataset': 'ag_news', 'dirquery': 'ztmp/bench/ag_news/kg_questions/common_test_questions.parquet', 'dirdata2': 'ztmp/bench/norm//ag_news/', 'dirout2': 'ztmp/bench//ag_news/sparse;neo4j/20240618/213340/'}
ztmp/bench//ag_news/sparse;neo4j/20240618/213340//dfmetrics.csv
                      id  ...                                        topk_scores
0   14504362844448484081  ...  0.01639344262295082;0.01639344262295082;0.0161...
1    5685638213467219607  ...  0.03278688524590164;0.016129032258064516;0.016...
2    5685638213467219607  ...  0.03278688524590164;0.016129032258064516;0.016...
3   13995111925969122086  ...  0.032266458495966696;0.03149801587301587;0.016...
4     638355261286711537  ...  0.01639344262295082;0.01639344262295082;0.0161...
..                   ...  ...                                                ...
85  14651180087730350534  ...  0.01639344262295082;0.01639344262295082;0.0161...
86  14114327028645677270  ...  0.03278688524590164;0.016129032258064516;0.016...
87  12985424926102133910  ...  0.031544957774465976;0.031054405392392875;0.03...
88   1217961636799403930  ...  0.01639344262295082;0.01639344262295082;0.0161...
89   1217961636799403930  ...  0.03278688524590164;0.03200204813108039;0.0161...

[90 rows x 5 columns]
 Avg time per request 2.2657978826098972
 Percentage accuracy 67.77777777777779


# dense + neo4j
# pybench bench_v1_fusion_run --engine "dense;neo4j" --dirquery ztmp/bench/ag_news/kg_questions/common_test_questions.parquet >> rag/zlogs.md
Load pretrained SentenceTransformer: sentence-transformers/all-MiniLM-L6-v2
{'name': 'bench_v1_fusion_run', 'engine': 'dense;neo4j', 'qdrant_url': 'http://localhost:6333', 'sparse_collection_name': 'hf-ag_news-sparse', 'dense_collection_name': 'hf-ag_news-dense', 'tantivy_datapath': './ztmp/tantivy_index', 'neo4j_db': 'neo4j', 'model_type': 'stransformers', 'model_id': 'sentence-transformers/all-MiniLM-L6-v2', 'topk': 5, 'dataset': 'ag_news', 'dirquery': 'ztmp/bench/ag_news/kg_questions/common_test_questions.parquet', 'dirdata2': 'ztmp/bench/norm//ag_news/', 'dirout2': 'ztmp/bench//ag_news/dense;neo4j/20240618/213600/'}
ztmp/bench//ag_news/dense;neo4j/20240618/213600//dfmetrics.csv
                      id  ...                                        topk_scores
0   14504362844448484081  ...  0.01639344262295082;0.01639344262295082;0.0161...
1    5685638213467219607  ...  0.03278688524590164;0.016129032258064516;0.016...
2    5685638213467219607  ...  0.03278688524590164;0.0315136476426799;0.03149...
3   13995111925969122086  ...  0.03252247488101534;0.032266458495966696;0.016...
4     638355261286711537  ...  0.01639344262295082;0.01639344262295082;0.0161...
..                   ...  ...                                                ...
85  14651180087730350534  ...  0.01639344262295082;0.01639344262295082;0.0161...
86  14114327028645677270  ...  0.03278688524590164;0.016129032258064516;0.016...
87  12985424926102133910  ...  0.03278688524590164;0.03225806451612903;0.0310...
88   1217961636799403930  ...  0.01639344262295082;0.01639344262295082;0.0161...
89   1217961636799403930  ...  0.03278688524590164;0.03225806451612903;0.0158...

[90 rows x 5 columns]
 Avg time per request 0.5660654544830322
 Percentage accuracy 70.0
```
# All benchmarks - 2024-06-19
```
## dense run



## sparse run



## neo4j run



## sparse+ neo4j run



## dense+ neo4j run



```
# All benchmarks - 2024-06-19
```
## dense run
Load pretrained SentenceTransformer: sentence-transformers/all-MiniLM-L6-v2
{'engine': 'dense', 'name': 'bench_v1_dense_run', 'server_url': 'http://localhost:6333', 'collection_name': 'hf-ag_news-dense', 'model_type': 'stransformers', 'model_id': 'sentence-transformers/all-MiniLM-L6-v2', 'topk': 5, 'dataset': 'ag_news', 'dirquery': 'ztmp/bench/ag_news/kg_questions/common_test_questions_all.parquet', 'dirdata2': 'ztmp/bench/norm//ag_news/', 'dirout2': 'ztmp/bench//ag_news/dense/20240619/194340/'}
ztmp/bench//ag_news/dense/20240619/194340//dfmetrics.csv
                       id  ...                                        topk_scores
0    14504362844448484081  ...  0.53952783;0.48844278;0.47226056;0.46422675;0....
1     5685638213467219607  ...  0.709211;0.53360486;0.5290079;0.52005786;0.508...
2     5685638213467219607  ...  0.7178594;0.588044;0.5843531;0.57684064;0.5757715
3    13995111925969122086  ...  0.7163174;0.71568155;0.69449115;0.6916677;0.49...
4      638355261286711537  ...  0.834062;0.77330923;0.74282277;0.74121946;0.73...
..                    ...  ...                                                ...
150  11777848068937089959  ...  0.5934332;0.59262526;0.58853275;0.57347167;0.5...
151    140469146415434618  ...  0.67307854;0.6489887;0.6475476;0.6260017;0.593...
152  16407429281338915589  ...  0.6174313;0.5965291;0.59492815;0.58440065;0.58...
153   3831132033380471085  ...  0.66686606;0.63516444;0.61545527;0.6036508;0.5...
154   2691452368464191376  ...  0.6255162;0.59899974;0.5858365;0.55939263;0.52...

[155 rows x 5 columns]
 Avg time per request 0.0135664124642649
 Percentage accuracy 43.87096774193549



## sparse run
{'engine': 'sparse', 'name': 'bench_v1_sparse_run', 'server_url': 'http://localhost:6333', 'collection_name': 'hf-ag_news-sparse', 'model_type': 'stransformers', 'model_id': 'naver/efficient-splade-VI-BT-large-query', 'topk': 5, 'dataset': 'ag_news', 'dirquery': 'ztmp/bench/ag_news/kg_questions/common_test_questions_all.parquet', 'dirdata2': 'ztmp/bench/norm//ag_news/', 'dirout2': 'ztmp/bench/ag_news/sparse/20240619/194352/'}
ztmp/bench/ag_news/sparse/20240619/194352//dfmetrics.csv
                       id  ...                                        topk_scores
0    14504362844448484081  ...    12.113992;11.945612;7.9292407;7.438615;6.955079
1     5685638213467219607  ...  23.448292;11.792427;11.779166;11.698137;10.744816
2     5685638213467219607  ...     23.936749;11.001982;10.24942;10.08684;9.850202
3    13995111925969122086  ...  22.407623;22.361982;22.152632;22.100557;18.218077
4      638355261286711537  ...     32.18488;30.686565;30.30815;30.30333;29.036858
..                    ...  ...                                                ...
150  11777848068937089959  ...  15.049902;14.510091;14.389432;13.681356;13.636914
151    140469146415434618  ...  16.327791;12.698099;12.315596;12.030142;11.737617
152  16407429281338915589  ...   13.410648;13.409648;13.35738;13.246634;13.141466
153   3831132033380471085  ...   16.95528;16.563923;15.671227;15.515245;15.178625
154   2691452368464191376  ...  15.468534;14.943535;12.8822155;12.737045;12.67...

[155 rows x 5 columns]
 Avg time per request 0.014946320749098255
 Percentage accuracy 60.0


# pybench bench_v1_tantivy_run --dirquery "ztmp/bench/ag_news/kg_questions/common_test_questions_all.parquet" --topk 5 >> rag/zlogs.md
{'name': 'bench_v1_tantivy_run', 'dirquery': 'ztmp/bench/ag_news/kg_questions/common_test_questions_all.parquet', 'dirdata2': 'ztmp/bench/norm//ag_news/', 'datapath': 'ztmp/bench/tantivy_index/hf-ag_news', 'dirout2': 'ztmp/bench/ag_news/tantivy/20240620/115646/'}
ztmp/bench/ag_news/tantivy/20240620/115646//dfmetrics.csv
                       id istop_k        dt
0    14504362844448484081       1  0.034295
1     5685638213467219607       1  0.009414
2     5685638213467219607       1  0.004276
3    13995111925969122086       1  0.006116
4      638355261286711537       1  0.005085
..                    ...     ...       ...
150  11777848068937089959       0  0.004595
151    140469146415434618       1  0.004656
152  16407429281338915589       0  0.004509
153   3831132033380471085       1  0.002989
154   2691452368464191376       1  0.003599

[155 rows x 3 columns]
 Avg time per request 0.005103046663345829
 Percentage accuracy 61.29032258064516



## neo4j run
{'engine': 'neo4j', 'name': 'bench_v1_neo4j_run', 'db_name': 'neo4j', 'dirquery': 'ztmp/bench/ag_news/kg_questions/common_test_questions_all.parquet', 'topk': 5, 'dataset': 'ag_news', 'dirout2': 'ztmp/bench/ag_news/neo4j/20240619/194525/'}
ztmp/bench/ag_news/neo4j/20240619/194525//dfmetrics.csv
                       id  ...     topk_scores
0    14504362844448484081  ...           4;4;0
1     5685638213467219607  ...      12;2;2;0;0
2     5685638213467219607  ...         8;2;2;0
3    13995111925969122086  ...       2;2;2;0;0
4      638355261286711537  ...  14;12;12;12;12
..                    ...  ...             ...
150  11777848068937089959  ...       4;4;4;2;2
151    140469146415434618  ...       2;0;0;0;0
152  16407429281338915589  ...       4;4;2;2;2
153   3831132033380471085  ...     12;10;2;0;0
154   2691452368464191376  ...      10;2;2;2;2

[155 rows x 5 columns]
 Avg time per request 0.552105809796241
 Percentage accuracy 58.70967741935483



## sparse+ neo4j run
{'name': 'bench_v1_fusion_run', 'engine': 'sparse_neo4j', 'qdrant_url': 'http://localhost:6333', 'sparse_collection_name': 'hf-ag_news-sparse', 'dense_collection_name': 'hf-ag_news-dense', 'tantivy_datapath': './ztmp/tantivy_index', 'neo4j_db': 'neo4j', 'model_type': 'stransformers', 'model_id': 'sentence-transformers/all-MiniLM-L6-v2', 'topk': 5, 'dataset': 'ag_news', 'dirquery': 'ztmp/bench/ag_news/kg_questions/common_test_questions_all.parquet', 'dirdata2': 'ztmp/bench/norm//ag_news/', 'dirout2': 'ztmp/bench//ag_news/sparse_neo4j/20240619/194715/'}
ztmp/bench//ag_news/sparse_neo4j/20240619/194715//dfmetrics.csv
                       id  ...                                        topk_scores
0    14504362844448484081  ...  0.03252247488101534;0.03252247488101534;0.0158...
1     5685638213467219607  ...  0.03278688524590164;0.016129032258064516;0.016...
2     5685638213467219607  ...  0.03278688524590164;0.0315136476426799;0.03149...
3    13995111925969122086  ...  0.032018442622950824;0.031746031746031744;0.01...
4      638355261286711537  ...  0.01639344262295082;0.01639344262295082;0.0161...
..                    ...  ...                                                ...
150  11777848068937089959  ...  0.01639344262295082;0.01639344262295082;0.0161...
151    140469146415434618  ...  0.03278688524590164;0.016129032258064516;0.016...
152  16407429281338915589  ...  0.01639344262295082;0.01639344262295082;0.0161...
153   3831132033380471085  ...  0.032018442622950824;0.030834914611005692;0.01...
154   2691452368464191376  ...  0.03252247488101534;0.032018442622950824;0.031...

[155 rows x 5 columns]
 Avg time per request 0.6424020951794039
 Percentage accuracy 75.48387096774194



## dense+ neo4j run
Load pretrained SentenceTransformer: sentence-transformers/all-MiniLM-L6-v2
{'name': 'bench_v1_fusion_run', 'engine': 'dense_neo4j', 'qdrant_url': 'http://localhost:6333', 'sparse_collection_name': 'hf-ag_news-sparse', 'dense_collection_name': 'hf-ag_news-dense', 'tantivy_datapath': './ztmp/tantivy_index', 'neo4j_db': 'neo4j', 'model_type': 'stransformers', 'model_id': 'sentence-transformers/all-MiniLM-L6-v2', 'topk': 5, 'dataset': 'ag_news', 'dirquery': 'ztmp/bench/ag_news/kg_questions/common_test_questions_all.parquet', 'dirdata2': 'ztmp/bench/norm//ag_news/', 'dirout2': 'ztmp/bench//ag_news/dense_neo4j/20240619/194905/'}
ztmp/bench//ag_news/dense_neo4j/20240619/194905//dfmetrics.csv
                       id  ...                                        topk_scores
0    14504362844448484081  ...  0.01639344262295082;0.01639344262295082;0.0161...
1     5685638213467219607  ...  0.03278688524590164;0.016129032258064516;0.016...
2     5685638213467219607  ...  0.03278688524590164;0.0315136476426799;0.03149...
3    13995111925969122086  ...  0.03252247488101534;0.032266458495966696;0.016...
4      638355261286711537  ...  0.01639344262295082;0.01639344262295082;0.0161...
..                    ...  ...                                                ...
150  11777848068937089959  ...  0.01639344262295082;0.01639344262295082;0.0161...
151    140469146415434618  ...  0.01639344262295082;0.01639344262295082;0.0161...
152  16407429281338915589  ...  0.028693528693528692;0.01639344262295082;0.016...
153   3831132033380471085  ...  0.032018442622950824;0.03128054740957967;0.016...
154   2691452368464191376  ...  0.03177805800756621;0.031054405392392875;0.030...

[155 rows x 5 columns]
 Avg time per request 0.6393318360851658
 Percentage accuracy 65.80645161290323


 
{'name': 'bench_v1_fusion_run', 'engine': 'tantivy_neo4j', 'qdrant_url': 'http://localhost:6333', 'sparse_collection_name': 'hf-ag_news-sparse', 'dense_collection_name': 'hf-ag_news-dense', 'tantivy_datapath': './ztmp/tantivy_index', 'neo4j_db': 'neo4j', 'model_type': 'stransformers', 'model_id': 'sentence-transformers/all-MiniLM-L6-v2', 'topk': 5, 'dataset': 'ag_news', 'dirquery': 'ztmp/bench/ag_news/kg_questions/common_test_questions_all.parquet', 'dirdata2': 'ztmp/bench/norm//ag_news/', 'dirout2': 'ztmp/bench//ag_news/tantivy_neo4j/20240620/120005/'}
ztmp/bench//ag_news/tantivy_neo4j/20240620/120005//dfmetrics.csv
                       id  ...     topk_scores
0    14504362844448484081  ...           4;4;0
1     5685638213467219607  ...      12;2;2;0;0
2     5685638213467219607  ...         8;2;2;0
3    13995111925969122086  ...       2;2;2;0;0
4      638355261286711537  ...  14;12;12;12;12
..                    ...  ...             ...
150  11777848068937089959  ...       4;4;4;2;2
151    140469146415434618  ...       2;0;0;0;0
152  16407429281338915589  ...       4;4;2;2;2
153   3831132033380471085  ...     12;10;2;0;0
154   2691452368464191376  ...      10;2;2;2;2

[155 rows x 5 columns]
 Avg time per request 0.5641395153537874
 Percentage accuracy 58.70967741935483

# All benchmarks - 2024-06-26
```
## dense run
Load pretrained SentenceTransformer: sentence-transformers/all-MiniLM-L6-v2
{'engine': 'dense', 'name': 'bench_v1_dense_run', 'server_url': 'http://localhost:6333', 'collection_name': 'hf-ag_news-dense', 'model_type': 'stransformers', 'model_id': 'sentence-transformers/all-MiniLM-L6-v2', 'topk': 10, 'dataset': 'ag_news', 'dirquery': 'ztmp/bench/ag_news/kg_questions/common_test_questions_all.parquet', 'dirdata2': 'ztmp/bench/norm//ag_news/', 'dirout2': 'ztmp/bench//ag_news/dense/20240626/165056/'}
ztmp/bench//ag_news/dense/20240626/165056//dfmetrics.csv
                       id  ...                                        topk_scores
0    14504362844448484081  ...  0.53952783;0.48844278;0.47226056;0.46422675;0....
1     5685638213467219607  ...  0.709211;0.53360486;0.5290079;0.52005786;0.508...
2     5685638213467219607  ...  0.7178594;0.588044;0.5843531;0.57684064;0.5757...
3    13995111925969122086  ...  0.7163174;0.71568155;0.69449115;0.6916677;0.49...
4      638355261286711537  ...  0.834062;0.77330923;0.74282277;0.74121946;0.73...
..                    ...  ...                                                ...
150  11777848068937089959  ...  0.5934332;0.59262526;0.58853275;0.57347167;0.5...
151    140469146415434618  ...  0.67307854;0.6489887;0.6475476;0.6260017;0.593...
152  16407429281338915589  ...  0.6174313;0.5965291;0.59492815;0.58440065;0.58...
153   3831132033380471085  ...  0.66686606;0.63516444;0.61545527;0.6036508;0.5...
154   2691452368464191376  ...  0.6255162;0.59899974;0.5858365;0.55939263;0.52...

[155 rows x 5 columns]
 Avg time per request 0.016872026074317193
 Percentage accuracy 49.03225806451613



## sparse run
{'engine': 'sparse', 'name': 'bench_v1_sparse_run', 'server_url': 'http://localhost:6333', 'collection_name': 'hf-ag_news-sparse', 'model_type': 'stransformers', 'model_id': 'naver/efficient-splade-VI-BT-large-query', 'topk': 10, 'dataset': 'ag_news', 'dirquery': 'ztmp/bench/ag_news/kg_questions/common_test_questions_all.parquet', 'dirdata2': 'ztmp/bench/norm//ag_news/', 'dirout2': 'ztmp/bench/ag_news/sparse/20240626/165110/'}
ztmp/bench/ag_news/sparse/20240626/165110//dfmetrics.csv
                       id  ...                                        topk_scores
0    14504362844448484081  ...  12.113992;11.945612;7.9292407;7.438615;6.95507...
1     5685638213467219607  ...  23.448292;11.792427;11.779166;11.698137;10.744...
2     5685638213467219607  ...  23.936749;11.001982;10.24942;10.08684;9.850202...
3    13995111925969122086  ...  22.407623;22.361982;22.152632;22.100557;18.218...
4      638355261286711537  ...  32.18488;30.686565;30.30815;30.30333;29.036858...
..                    ...  ...                                                ...
150  11777848068937089959  ...  15.049902;14.510091;14.389432;13.681356;13.636...
151    140469146415434618  ...  16.327791;12.698099;12.315596;12.030142;11.737...
152  16407429281338915589  ...  13.410648;13.409648;13.35738;13.246634;13.1414...
153   3831132033380471085  ...  16.95528;16.563923;15.671227;15.515245;15.1786...
154   2691452368464191376  ...  15.468534;14.943535;12.8822155;12.737045;12.67...

[155 rows x 5 columns]
 Avg time per request 0.020694471174670805
 Percentage accuracy 67.74193548387096



## tantivy run
{'name': 'bench_v1_tantivy_run', 'dirquery': 'ztmp/bench/ag_news/kg_questions/common_test_questions_all.parquet', 'dirdata2': 'ztmp/bench/norm//ag_news/', 'datapath': 'ztmp/bench/tantivy_index/hf-ag_news', 'dirout2': 'ztmp/bench/ag_news/tantivy/20240626/165118/'}
ztmp/bench/ag_news/tantivy/20240626/165118//dfmetrics.csv
                       id  ...                                        topk_scores
0    14504362844448484081  ...  36.92285919189453;36.48708724975586;13.8890409...
1     5685638213467219607  ...  37.13068771362305;19.659378051757812;18.005853...
2     5685638213467219607  ...  52.821739196777344;34.50028991699219;33.735122...
3    13995111925969122086  ...  28.97003936767578;28.97003936767578;28.7248153...
4      638355261286711537  ...  41.65299606323242;40.089019775390625;39.190383...
..                    ...  ...                                                ...
150  11777848068937089959  ...  25.40403175354004;20.097307205200195;19.006687...
151    140469146415434618  ...  20.43756675720215;15.863914489746094;15.264781...
152  16407429281338915589  ...  19.51242446899414;19.14638900756836;17.7129306...
153   3831132033380471085  ...  22.2706298828125;19.973997116088867;16.7383804...
154   2691452368464191376  ...  28.93495750427246;26.681381225585938;26.202831...

[155 rows x 5 columns]
 Avg time per request 0.0030258194092781313
 Percentage accuracy 66.45161290322581



## neo4j run
{'engine': 'neo4j', 'name': 'bench_v1_neo4j_run', 'db_name': 'neo4j', 'dirquery': 'ztmp/bench/ag_news/kg_questions/common_test_questions_all.parquet', 'topk': 10, 'dataset': 'ag_news', 'dirout2': 'ztmp/bench/ag_news/neo4j/20240626/165254/'}
ztmp/bench/ag_news/neo4j/20240626/165254//dfmetrics.csv
                       id  ...                    topk_scores
0    14504362844448484081  ...                          4;4;0
1     5685638213467219607  ...           12;2;2;0;0;0;0;0;0;0
2     5685638213467219607  ...                        8;2;2;0
3    13995111925969122086  ...            2;2;2;0;0;0;0;0;0;0
4      638355261286711537  ...  14;12;12;12;12;12;12;12;12;12
..                    ...  ...                            ...
150  11777848068937089959  ...            4;4;4;2;2;2;2;2;2;2
151    140469146415434618  ...                      2;0;0;0;0
152  16407429281338915589  ...            4;4;2;2;2;2;2;2;2;2
153   3831132033380471085  ...          12;10;2;0;0;0;0;0;0;0
154   2691452368464191376  ...           10;2;2;2;2;2;2;0;0;0

[155 rows x 5 columns]
 Avg time per request 0.5725490923850767
 Percentage accuracy 64.51612903225806



## sparse+ neo4j run
{'name': 'bench_v1_fusion_run', 'engine': 'sparse_neo4j', 'qdrant_url': 'http://localhost:6333', 'sparse_collection_name': 'hf-ag_news-sparse', 'dense_collection_name': 'hf-ag_news-dense', 'tantivy_datapath': './ztmp/tantivy_index', 'neo4j_db': 'neo4j', 'model_type': 'stransformers', 'model_id': 'sentence-transformers/all-MiniLM-L6-v2', 'topk': 10, 'dataset': 'ag_news', 'dirquery': 'ztmp/bench/ag_news/kg_questions/common_test_questions_all.parquet', 'dirdata2': 'ztmp/bench/norm//ag_news/', 'dirout2': 'ztmp/bench//ag_news/sparse_neo4j/20240626/165442/'}
ztmp/bench//ag_news/sparse_neo4j/20240626/165442//dfmetrics.csv
                       id  ...                                        topk_scores
0    14504362844448484081  ...  0.03252247488101534;0.03252247488101534;0.0158...
1     5685638213467219607  ...  0.03278688524590164;0.016129032258064516;0.016...
2     5685638213467219607  ...  0.03278688524590164;0.0315136476426799;0.03149...
3    13995111925969122086  ...  0.032018442622950824;0.031746031746031744;0.01...
4      638355261286711537  ...  0.01639344262295082;0.01639344262295082;0.0161...
..                    ...  ...                                                ...
150  11777848068937089959  ...  0.01639344262295082;0.01639344262295082;0.0161...
151    140469146415434618  ...  0.03278688524590164;0.016129032258064516;0.016...
152  16407429281338915589  ...  0.01639344262295082;0.01639344262295082;0.0161...
153   3831132033380471085  ...  0.032018442622950824;0.030834914611005692;0.01...
154   2691452368464191376  ...  0.03252247488101534;0.032018442622950824;0.031...

[155 rows x 5 columns]
 Avg time per request 0.6280407874814926
 Percentage accuracy 78.06451612903226



## dense+ neo4j run
Load pretrained SentenceTransformer: sentence-transformers/all-MiniLM-L6-v2
{'name': 'bench_v1_fusion_run', 'engine': 'dense_neo4j', 'qdrant_url': 'http://localhost:6333', 'sparse_collection_name': 'hf-ag_news-sparse', 'dense_collection_name': 'hf-ag_news-dense', 'tantivy_datapath': './ztmp/tantivy_index', 'neo4j_db': 'neo4j', 'model_type': 'stransformers', 'model_id': 'sentence-transformers/all-MiniLM-L6-v2', 'topk': 10, 'dataset': 'ag_news', 'dirquery': 'ztmp/bench/ag_news/kg_questions/common_test_questions_all.parquet', 'dirdata2': 'ztmp/bench/norm//ag_news/', 'dirout2': 'ztmp/bench//ag_news/dense_neo4j/20240626/165630/'}
ztmp/bench//ag_news/dense_neo4j/20240626/165630//dfmetrics.csv
                       id  ...                                        topk_scores
0    14504362844448484081  ...  0.01639344262295082;0.01639344262295082;0.0161...
1     5685638213467219607  ...  0.03278688524590164;0.016129032258064516;0.016...
2     5685638213467219607  ...  0.03278688524590164;0.0315136476426799;0.03149...
3    13995111925969122086  ...  0.03252247488101534;0.032266458495966696;0.016...
4      638355261286711537  ...  0.01639344262295082;0.01639344262295082;0.0161...
..                    ...  ...                                                ...
150  11777848068937089959  ...  0.01639344262295082;0.01639344262295082;0.0161...
151    140469146415434618  ...  0.01639344262295082;0.01639344262295082;0.0161...
152  16407429281338915589  ...  0.028693528693528692;0.01639344262295082;0.016...
153   3831132033380471085  ...  0.032018442622950824;0.03128054740957967;0.016...
154   2691452368464191376  ...  0.03177805800756621;0.031054405392392875;0.030...

[155 rows x 5 columns]
 Avg time per request 0.6242595672607422
 Percentage accuracy 70.96774193548387



## tantivy+ neo4j run
{'name': 'bench_v1_fusion_run', 'engine': 'tantivy_neo4j', 'qdrant_url': 'http://localhost:6333', 'sparse_collection_name': 'hf-ag_news-sparse', 'dense_collection_name': 'hf-ag_news-dense', 'tantivy_datapath': './ztmp/tantivy_index', 'neo4j_db': 'neo4j', 'model_type': 'stransformers', 'model_id': 'sentence-transformers/all-MiniLM-L6-v2', 'topk': 10, 'dataset': 'ag_news', 'dirquery': 'ztmp/bench/ag_news/kg_questions/common_test_questions_all.parquet', 'dirdata2': 'ztmp/bench/norm//ag_news/', 'dirout2': 'ztmp/bench//ag_news/tantivy_neo4j/20240626/165805/'}
ztmp/bench//ag_news/tantivy_neo4j/20240626/165805//dfmetrics.csv
                       id  ...     topk_scores
0    14504362844448484081  ...           4;4;0
1     5685638213467219607  ...      12;2;2;0;0
2     5685638213467219607  ...         8;2;2;0
3    13995111925969122086  ...       2;2;2;0;0
4      638355261286711537  ...  14;12;12;12;12
..                    ...  ...             ...
150  11777848068937089959  ...       4;4;4;2;2
151    140469146415434618  ...       2;0;0;0;0
152  16407429281338915589  ...       4;4;2;2;2
153   3831132033380471085  ...     12;10;2;0;0
154   2691452368464191376  ...      10;2;2;2;2

[155 rows x 5 columns]
 Avg time per request 0.5612505882017074
 Percentage accuracy 58.70967741935483


# Finetuning logs

```bash
# convert ag_news triplets into rebel like format
# python3 -u rag/finetune.py preprocessing_standardize_dataset --datadir "ztmp/bench/ag_news/kg_triplets/*/*.parquet" --outputdir "ztmp/bench/ag_news/ft_data.parquet"
ztmp/bench/ag_news/ft_data.parquet
                                                 context                                           triplets
0      Average techie starting salaries to remain sta...  <triplet> techie <subj> IT <obj> field of this...
1      Death toll from storm in Philippines rises to ...  <triplet> Death toll from storm in Philippines...
2      Action over global warming demanded The Govern...  <triplet> Action over global warming demanded ...
3      NFL: Philadelphia 27, NY Giants 6 The Philadel...  <triplet> NFL <subj> NFL East <obj> has part <...
4      Barcelona #39;s Eto #39;o goes from Villain to...  <triplet> Victor African Footballer of the Yea...
...                                                  ...                                                ...
49425  Prosecutor: Players, Fans To Be Held Accountab...  <triplet> brawl <subj> Pacers <obj> participat...
49426  Italians remember Canadians with fondness, gra...        <triplet> CESENA <subj> Italy <obj> country
49427  Ex-Polaroid exec takes top finance job at 3Com...  <triplet> Polaroid <subj> 3Com <obj> parent or...
49428  Government responds to anti-arms-deal activist...  <triplet> Government responds to anti-arms-dea...
49429  Allawi declares emergenct rule IRAQ declared a...  <triplet> declared a state of emergency <subj>...

[49430 rows x 2 columns]



# finetune
# python3 -u rag/finetune.py ft_train --datasetdir "ztmp/bench/ag_news/ft_data.parquet" --outputdir "ztmp/results" --nrows=1000

Using default tokenizer.
{'eval_loss': 0.2874205410480499, 'eval_rouge1': 100.0, 'eval_rouge2': 100.0, 'eval_rougeL': 100.0, 'eval_rougeLsum': 100.0, 'eval_gen_len': 27.0, 'eval_runtime': 4.8703, 'eval_samples_per_second': 0.205, 'eval_steps_per_second': 0.205, 'epoch': 1.0}
Using default tokenizer.
{'eval_loss': 0.2680197060108185, 'eval_rouge1': 0.0, 'eval_rouge2': 0.0, 'eval_rougeL': 0.0, 'eval_rougeLsum': 0.0, 'eval_gen_len': 200.0, 'eval_runtime': 4.9133, 'eval_samples_per_second': 0.204, 'eval_steps_per_second': 0.204, 'epoch': 2.0}
Using default tokenizer.
{'eval_loss': 0.15594030916690826, 'eval_rouge1': 81.39181286549707, 'eval_rouge2': 75.18162393162393, 'eval_rougeL': 79.5906432748538, 'eval_rougeLsum': 80.66666666666667, 'eval_gen_len': 25.0, 'eval_runtime': 5.8358, 'eval_samples_per_second': 1.714, 'eval_steps_per_second': 0.514, 'epoch': 1.0}

```

# Search and Summarize
```
# python3 -u rag/rag_summ.py search_summarize --query="Roger Federer in grand slams" --engine="sparse_neo4j" --llm_service="openai" --llm_model="gpt-4o-mini" --llm_max_tokens=1000

HTTP Request: POST http://localhost:6333/collections/hf-ag_news-sparse/points/search "HTTP/1.1 200 OK"
HTTP Request: POST http://localhost:6333/collections/hf-ag_news-sparse/points/search "HTTP/1.1 200 OK"
openai gpt-4o-mini <openai.OpenAI object at 0x7dc3a0ada710>

Generate a 10 line summary of the news articles below. It should cover all articles. 
Articles: 
``
Top Seed Federer, Andre Agassi Advance at US Open (Update5) Top seed Roger Federer beat Albert Costa in their first-round match at the US Open, and two-time champion Andre Agassi beat Robby Ginepri as the final Grand Slam tennis tournament of the year got under way.
---
Federer #39;s Games Dream Shattered ATHENS (Reuters) - Roger Federer was bundled out of the Olympic tennis tournament Tuesday by unheralded Czech Tomas Berdych. 
---
Tennis: Federer ready for Hewitt Roger Federer will go for his third Grand Slam title of 2004 against Lleyton Hewitt at the US Open on Sunday.
---
Federer and Henin-Hardenne Get the Top Spots for U.S. Open Roger Federer will open against Albert Costa, and Justine Henin-Hardenne will play a qualifier when the tournament begins Monday.
---
Federer Dominates U.S. Open Final Roger Federer became the first man since 1988 to win three Grand Slam tournaments in a year, thoroughly outclassing Lleyton Hewitt 6-0, 7-6 (3), 6-0.
---
Federer races to US Open last 16 NEW YORK, USA -- World number one and top seed Roger Federer stayed on course for his third grand slam title of the year with a straight sets victory over Fabrice Santoro of France in the US Open at Flushing Meadows on Saturday.
---
Sharapova falls; Agassi, Federer in fourth round Roger Federer, of Switzerland, returns to Fabrice Santoro, of France, at the US Open tennis tournament in New York on Saturday. NEW YORK - Maria Sharapovas drive to win another Grand Slam title got dashed 
---
Fed Express makes steady progress NEW YORK, Sept. 4. - Top-seed Roger Federer moved a step closer to becoming the first man in 16 years to win three Grand Slams in a season when he reached the US Open fourth round with a straight-sets win here today.
---
Federer, Hewitt Sweep Into Open Final NEW YORK - Roger Federer kept up his bid to become the first man since 1988 to win three Grand Slam titles in a year, beating Tim Henman 6-3, 6-4, 6-4 Saturday and cruising into the U.S. Open final against Lleyton Hewitt...
---
Record 13th straight mens title HOUSTON - Top-seeded Roger Federer of Switzerland won a record 13th straight final Sunday, beating Australian Lleyton Hewitt, 6-3, 6-2, in the title match of the Association of Tennis Professionals Masters Cup.
``
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
Roger Federer had a remarkable run at the US Open, advancing through the tournament with victories over Albert Costa and Fabrice Santoro, ultimately reaching the final against Lleyton Hewitt. He dominated the final match, winning in straight sets and becoming the first man since 1988 to secure three Grand Slam titles in a single year. Meanwhile, two-time champion Andre Agassi also progressed in the tournament, defeating Robby Ginepri. However, Federer's Olympic dreams were dashed earlier when he was eliminated by Czech player Tomas Berdych. Despite this setback, Federer continued to showcase his dominance in the sport, achieving a record 13th consecutive title at the ATP Masters Cup by defeating Hewitt again. The US Open highlighted Federer's exceptional talent and consistency throughout the year.


# python3 -u rag/rag_summ.py search_summarize --query="Russian economy" --engine="sparse_neo4j" --llm_service="openai" --llm_model="gpt-4o-mini" --llm_max_tokens=1000
HTTP Request: POST http://localhost:6333/collections/hf-ag_news-sparse/points/search "HTTP/1.1 200 OK"
HTTP Request: POST http://localhost:6333/collections/hf-ag_news-sparse/points/search "HTTP/1.1 200 OK"
openai gpt-4o-mini <openai.OpenAI object at 0x7ad2a2cea010>
Generate a 10 line summary of the news articles below. It should cover all articles. 
Articles: 
``
IMF Raises Outlook on Russia Economy International Monetary Fund said on Wednesday, September 29, that it raised its outlook for Russias economy, forecasting 6.6 percent GDP growth in 2005.
---
Putin aide warns of dangers to economy ECONOMIC POLICY President Vladimir Putin #39;s economic adviser has warned that Russia is jeopardising its economic growth by drifting away from liberal market reforms and moving towards increased state intervention.
---
Russia to take concrete steps in economic cooperation with &lt;b&gt;...&lt;/b&gt; The Russian government intends to take concrete efforts to develop trade and economic relations with Venezuela, Prime Minister Mikhail Fradkov said on Thursday, according to the Russian media.
---
Kyoto 'won't hit' Russian economy Russian economic growth is unlikely to suffer because of government support for the Kyoto Protocol on climate change, a leading analyst says.
---
RUSSIA * ECONOMY * OIL * AUCTION MOSCOW, November 30 (RIA Novosti) - Gazprom will bid in the Yuganskneftegaz auction, Gazpromneft chief executive officer (CEO) Sergei Bogdanchikov told the Russian Gas-2004 second international forum Tuesday.
---
IMF Says Russia Must Save Energy Windfall WASHINGTON -- The International Monetary Fund on Wednesday raised its outlook for Russia #39;s economy but warned Moscow to resist spending the extra oil revenues it has received as a result of record energy prices.
---
Russia to Curb Inflation, Manage Industry, PM Says (Update1) Russia #39;s government will take an active role in managing industry as it seeks to curb inflation and open markets to attract investment, Prime Minister Mikhail Fradkov said.
---
Russia Seeks to Boost Software Production (AP) AP - Russia is seeking to slow the brain-drain of computer specialists and increase software production, a top government official said Friday, in an effort that some hope will help diversify the country's oil-dependent economy.
---
Russia, Uzbekistan can make serious decisions on economy &lt;b&gt;...&lt;/b&gt; Dushanbe. (Interfax) - Russia and Uzbekistan may make serious decisions in the area of economy before the end of this year, Russian President Vladimir Putin said while meeting with his Uzbek counterpart Islam Karimov.
---
Asian group welcomes Russia A CENTRAL Asian economic group today formally approved Russia #39;s membership bid, giving Moscow a chance to restore its influence in this strategic, energy-rich region.
``
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
The International Monetary Fund (IMF) has raised its GDP growth forecast for Russia to 6.6% for 2005, highlighting a positive outlook for the economy. However, President Putin's economic adviser cautioned that the country risks jeopardizing this growth by moving away from liberal market reforms towards increased state intervention. The Russian government is also planning to enhance trade relations with Venezuela and is optimistic that support for the Kyoto Protocol will not negatively impact economic growth. Gazprom is set to participate in the Yuganskneftegaz auction, indicating ongoing activity in the oil sector. The IMF advised Russia to save its windfall from rising oil revenues rather than spend it. Prime Minister Mikhail Fradkov announced plans to actively manage industry to curb inflation and attract investment. Additionally, efforts are underway to boost software production and retain computer specialists to diversify the economy. Russia and Uzbekistan are expected to make significant economic decisions soon, while a Central Asian economic group has welcomed Russia's membership bid, aiming to restore its influence in the region.
```



########## Search and summarize with citation
```
# python3 -u rag/rag_summ.py search_summarize_with_citation --query="Russian economy" --engine="sparse_neo4j" --llm_service="openai" --llm_model="gpt-4o-mini" --llm_max_tokens=1000



HTTP Request: POST http://localhost:6333/collections/hf-ag_news-sparse/points/search "HTTP/1.1 200 OK"
HTTP Request: POST http://localhost:6333/collections/hf-ag_news-sparse/points/search "HTTP/1.1 200 OK"
openai gpt-4o-mini <openai.OpenAI object at 0x72b9a84aac90>
Summarize information from below articles using bullets points.
        Make sure the the summary contain factual information extracted from the articles.
        Provide inline citation by numbering the article information is fetched from.
        Add numbered article details(date, url, title) in footnotes.
Articles: 
``
title: IMF Raises Outlook on Russia
url:https://ag_news/article/197110401126301633
text:IMF Raises Outlook on Russia Economy International Monetary Fund said on Wednesday, September 29, that it raised its outlook for Russias economy, forecasting 6.6 percent GDP growth in 2005.
---
title: Putin aide warns of dangers
url:https://ag_news/article/7731856450048375966
text:Putin aide warns of dangers to economy ECONOMIC POLICY President Vladimir Putin #39;s economic adviser has warned that Russia is jeopardising its economic growth by drifting away from liberal market reforms and moving towards increased state intervention.
---
title: Russia to take concrete steps
url:https://ag_news/article/11701669738690911348
text:Russia to take concrete steps in economic cooperation with &lt;b&gt;...&lt;/b&gt; The Russian government intends to take concrete efforts to develop trade and economic relations with Venezuela, Prime Minister Mikhail Fradkov said on Thursday, according to the Russian media.
---
title: Kyoto 'won't hit' Russian economy
url:https://ag_news/article/1065438532386387923
text:Kyoto 'won't hit' Russian economy Russian economic growth is unlikely to suffer because of government support for the Kyoto Protocol on climate change, a leading analyst says.
---
title: RUSSIA * ECONOMY * OIL
url:https://ag_news/article/13391121980859296171
text:RUSSIA * ECONOMY * OIL * AUCTION MOSCOW, November 30 (RIA Novosti) - Gazprom will bid in the Yuganskneftegaz auction, Gazpromneft chief executive officer (CEO) Sergei Bogdanchikov told the Russian Gas-2004 second international forum Tuesday.
---
title: IMF Says Russia Must Save
url:https://ag_news/article/10019024039878483729
text:IMF Says Russia Must Save Energy Windfall WASHINGTON -- The International Monetary Fund on Wednesday raised its outlook for Russia #39;s economy but warned Moscow to resist spending the extra oil revenues it has received as a result of record energy prices.
---
title: Russia to Curb Inflation, Manage
url:https://ag_news/article/16017463766838804336
text:Russia to Curb Inflation, Manage Industry, PM Says (Update1) Russia #39;s government will take an active role in managing industry as it seeks to curb inflation and open markets to attract investment, Prime Minister Mikhail Fradkov said.
---
title: Russia Seeks to Boost Software
url:https://ag_news/article/3292891271804997143
text:Russia Seeks to Boost Software Production (AP) AP - Russia is seeking to slow the brain-drain of computer specialists and increase software production, a top government official said Friday, in an effort that some hope will help diversify the country's oil-dependent economy.
---
title: Russia, Uzbekistan can make serious
url:https://ag_news/article/2042753778883900973
text:Russia, Uzbekistan can make serious decisions on economy &lt;b&gt;...&lt;/b&gt; Dushanbe. (Interfax) - Russia and Uzbekistan may make serious decisions in the area of economy before the end of this year, Russian President Vladimir Putin said while meeting with his Uzbek counterpart Islam Karimov.
---
title: Asian group welcomes Russia A
url:https://ag_news/article/4020010286330063996
text:Asian group welcomes Russia A CENTRAL Asian economic group today formally approved Russia #39;s membership bid, giving Moscow a chance to restore its influence in this strategic, energy-rich region.
``
        
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
- The International Monetary Fund (IMF) has raised its outlook for Russia's economy, predicting a GDP growth of 6.6% in 2005【1】.
- An aide to President Putin has expressed concerns that Russia's economic growth is at risk due to a shift away from liberal market reforms towards increased state intervention【2】.
- The Russian government plans to enhance trade and economic relations with Venezuela, as stated by Prime Minister Mikhail Fradkov【3】.
- A leading analyst has indicated that Russia's economic growth is unlikely to be negatively impacted by the government's support for the Kyoto Protocol on climate change【4】.
- Gazprom is set to participate in the Yuganskneftegaz auction, according to the CEO of Gazpromneft【5】.
- The IMF has advised Russia to save its energy windfall from record oil prices rather than spending it【6】.
- Prime Minister Mikhail Fradkov announced that the Russian government will actively manage industry to curb inflation and attract investment【7】.
- Russia is working to increase software production and reduce the brain drain of computer specialists to diversify its oil-dependent economy【8】.
- President Putin mentioned that Russia and Uzbekistan could make significant economic decisions by the end of the year【9】.
- A Central Asian economic group has formally approved Russia's membership bid, allowing Moscow to regain influence in the energy-rich region【10】.

---

### Footnotes
1. September 29, 2005, https://ag_news/article/197110401126301633, IMF Raises Outlook on Russia
2. Date not specified, https://ag_news/article/7731856450048375966, Putin aide warns of dangers
3. Date not specified, https://ag_news/article/11701669738690911348, Russia to take concrete steps
4. Date not specified, https://ag_news/article/1065438532386387923, Kyoto 'won't hit' Russian economy
5. November 30, 2004, https://ag_news/article/13391121980859296171, RUSSIA * ECONOMY * OIL
6. Date not specified, https://ag_news/article/10019024039878483729, IMF Says Russia Must Save
7. Date not specified, https://ag_news/article/16017463766838804336, Russia to Curb Inflation, Manage Industry, PM Says (Update1)
8. Date not specified, https://ag_news/article/3292891271804997143, Russia Seeks to Boost Software
9. Date not specified, https://ag_news/article/2042753778883900973, Russia, Uzbekistan can make serious decisions on economy
10. Date not specified, https://ag_news/article/4020010286330063996, Asian group welcomes Russia A
```


```
# python3 -u rag/rag_summ.py search_summarize_with_citation --query="Nadal in grand slams" --engine="sparse_neo4j" --llm_service="openai" --llm_model="gpt-4o-mini" --llm_max_tokens=1000


HTTP Request: POST http://localhost:6333/collections/hf-ag_news-sparse/points/search "HTTP/1.1 200 OK"
HTTP Request: POST http://localhost:6333/collections/hf-ag_news-sparse/points/search "HTTP/1.1 200 OK"
openai gpt-4o-mini <openai.OpenAI object at 0x77560fdc0ad0>
Summarize information from below articles using bullets points.
        Make sure the the summary contain factual information extracted from the articles.
        Provide inline citation by numbering the article information is fetched from.
        Add numbered article details(date, url, title) in footnotes.
Articles: 
``
title: Nadal Wins in Poland for
url:https://ag_news/article/8515913065789312358
text:Nadal Wins in Poland for First ATP Title (AP) AP - Spain's Rafael Nadal won his first ATP singles title Sunday, beating Argentina's Jose Acasuso 6-3, 6-4 in the final at the Idea Prokom Open.
---
title: Top Seed Federer, Andre Agassi
url:https://ag_news/article/13081699345709984958
text:Top Seed Federer, Andre Agassi Advance at US Open (Update5) Top seed Roger Federer beat Albert Costa in their first-round match at the US Open, and two-time champion Andre Agassi beat Robby Ginepri as the final Grand Slam tennis tournament of the year got under way.
---
title: Hewitt: Grand Slammed, but optimistic
url:https://ag_news/article/9292059118207224253
text:Hewitt: Grand Slammed, but optimistic Lleyton Hewitt believes he can still win another grand slam title despite conceding Roger Federer has tennis history at his mercy after the world No1 #39;s one-sided victory in yesterday #39;s US Open final.
---
title: Tennis: Federer ready for Hewitt
url:https://ag_news/article/7237450868762445123
text:Tennis: Federer ready for Hewitt Roger Federer will go for his third Grand Slam title of 2004 against Lleyton Hewitt at the US Open on Sunday.
---
title: Sharapova falls; Agassi, Federer in
url:https://ag_news/article/4369101642019406242
text:Sharapova falls; Agassi, Federer in fourth round Roger Federer, of Switzerland, returns to Fabrice Santoro, of France, at the US Open tennis tournament in New York on Saturday. NEW YORK - Maria Sharapovas drive to win another Grand Slam title got dashed 
---
title: Defending champ upset by Petrova
url:https://ag_news/article/5369077489567724879
text:Defending champ upset by Petrova The top-seeded Belgian was upset in the fourth round of the year #39;s last Grand Slam tournament by 14th-seeded Nadia Petrova 6-3, 6-2.
---
title: Hewitt advances, Federer to face
url:https://ag_news/article/16479537587615023379
text:Hewitt advances, Federer to face Agassi NEW YORK, Sept. 7. - Former champion Lleyton Hewitt reached his third consecutive Grand Slam quarter-final by defeating Karol Beck of Slovakia 6-4, 6-2, 6-2, at the US Open today for his 14th consecutive victory.
---
title: Federer Is Too Much for
url:https://ag_news/article/8339615858572000104
text:Federer Is Too Much for Hewitt in U.S. Open Final Roger Federer won the U.S. Open over Lleyton Hewitt and became the first player since Mats Wilander in 1988 to win three Grand Slam titles in one year.
---
title: Tennis: US Open champion Federer
url:https://ag_news/article/12879676470333279058
text:Tennis: US Open champion Federer in Sampras record threat NEW YORK : Roger Federer, who has just won his first US Open, is in many people #39;s minds a threat to Pete Sampras #39; record of 14 Grand Slam titles.
---
title: Pierce, Rochus post wins Maria
url:https://ag_news/article/2090284450450652650
text:Pierce, Rochus post wins Maria Sharapova #39;s drive to win another grand slam tennis title was dashed when the Wimbledon champion lost to Mary Pierce 4-6 6-2 6-3 in the third round of the US Open on Saturday.
``
        
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
- Rafael Nadal won his first ATP singles title by defeating Argentina's Jose Acasuso with a score of 6-3, 6-4 at the Idea Prokom Open in Poland【1】.
- Roger Federer, the top seed, advanced in the US Open by beating Albert Costa in the first round【2】.
- Lleyton Hewitt expressed optimism about winning another Grand Slam title despite losing to Federer in the US Open final【3】.
- Federer aimed for his third Grand Slam title of 2004 against Lleyton Hewitt at the US Open【4】.
- Maria Sharapova's attempt to win another Grand Slam title ended when she lost to Mary Pierce in the third round of the US Open【5】【9】.
- Defending champion Justine Henin was upset by 14th-seeded Nadia Petrova in the fourth round of the US Open【6】.
- Lleyton Hewitt reached his third consecutive Grand Slam quarter-final by defeating Karol Beck【7】.
- Roger Federer won the US Open, marking him as the first player since Mats Wilander in 1988 to win three Grand Slam titles in a single year【8】.
- Following his US Open victory, Federer was considered a potential threat to Pete Sampras's record of 14 Grand Slam titles【9】.

---

### Footnotes
1. Nadal Wins in Poland for First ATP Title, AP, [Link](https://ag_news/article/8515913065789312358)
2. Top Seed Federer, Andre Agassi Advance at US Open, Update5, [Link](https://ag_news/article/13081699345709984958)
3. Hewitt: Grand Slammed, but optimistic, [Link](https://ag_news/article/9292059118207224253)
4. Tennis: Federer ready for Hewitt, [Link](https://ag_news/article/7237450868762445123)
5. Sharapova falls; Agassi, Federer in fourth round, [Link](https://ag_news/article/4369101642019406242)
6. Defending champ upset by Petrova, [Link](https://ag_news/article/5369077489567724879)
7. Hewitt advances, Federer to face Agassi, [Link](https://ag_news/article/16479537587615023379)
8. Federer Is Too Much for Hewitt in U.S. Open Final, [Link](https://ag_news/article/8339615858572000104)
9. Tennis: US Open champion Federer in Sampras record threat, [Link](https://ag_news/article/12879676470333279058)
10. Pierce, Rochus post wins Maria, [Link](https://ag_news/article/2090284450450652650)
```





########### NER extraction prompt logs
```python

#### 


What is  the fiscal earning of Mizuho ?

url, text_id,  question

Parse the question by 


1) Generate Questions
   LLM extract enti



#### Flow 

Question 
     ---> Extracty entity following format
           Fixed format --> convert into entities --> put into qdrant format --> qdramt

Question 
          Provide some data about XXX after jan 2024 ?


Response:
json_template:
          {'company': ['Mizuho'], 
            'category_tags': ['Earnings', 'Fiscal Report', 'Q1'], 
            'relation_tags': ['Snapshot'], 
            'date':         'Jan 2024',      
            'date_period':  'after',

            'task':  ['summarize', 'extract_from_database',   ]    ### more than 1 task.

          }


Prompt_use =""" you are extractor....

  use this template
     <json_response_template>

  <question>

"""

   replace("<json_response_template>", )

  Dynamically insert the json_template.


Agent base stuff
   Dispatcher/ Router the task to the correct Agent


Step2 :

   Input : cleanup( json_template_from_llm)

    qdrant_json: retrieve context

    redirect to the correct Task Prompt 
       { "summarize" :  {  Prompt + <context_generic> }

         "extract_from_database":  { create SQL, call the SQL,  get back...}
       }








     --> Create the JSON query for qdrant



    --> send the quuery to qdrant.




import os
from utilmy import pd_read_file
from rag.llm import LLM
from pydantic import BaseModel

llm1 = LLM('openai', 'gpt-4o-mini', api_key=os.environ['OPENAI_API_KEY'])
df = pd_read_file("../ztmp/df_LZ_merge_90k_tmp.parquet")
df = df[["text_id", "title", "text"]][:10]
# print(df[:2])
prompt_template = f"""
Analyze the key concepts of the given text.
-----------text-----------
<prompt_text>
"""
prompt_map_dict = {"<prompt_text>": "title"}

# outputs:
# text: Rohde & Schwarz Preps for IBC
# llm_msg:
# {'response': {'company': ['Rohde & Schwarz'], 'category_tags': ['Technology', 'Broadcasting', 'Event Preparation'], 'relation_tags': ['IBC', 'Event'], 'date_': '2023-10-01'}, 'prompt': '\nAnalyze the key concepts of the given text.\n-----------text-----------\nRohde & Schwarz Preps for IBC\n\nRespond with the following JSON schema: {json_schema}'}
# ==========
# text: Mizuho: Fiscal Q1 Earnings Snapshot
# llm_msg:
# {'response': {'company': ['Mizuho'], 'category_tags': ['Earnings', 'Financial Report', 'Quarterly Results'], 'relation_tags': ['Fiscal Q1', 'Earnings Snapshot'], 'date_': 'Not specified'}, 'prompt': '\nAnalyze the key concepts of the given text.\n-----------text-----------\nMizuho: Fiscal Q1 Earnings Snapshot\n\nRespond with the following JSON schema: {json_schema}'}
# ==========
# text: Mizuho: Fiscal Q1 Earnings Snapshot
# llm_msg:
# {'response': {'company': ['Mizuho'], 'category_tags': ['Earnings', 'Fiscal Report', 'Q1'], 'relation_tags': ['Snapshot'], 'date_': 'Not specified'}, 'prompt': '\nAnalyze the key concepts of the given text.\n-----------text-----------\nMizuho: Fiscal Q1 Earnings Snapshot\n\nRespond with the following JSON schema: {json_schema}'}
# ==========
# text: Mizuho: Fiscal Q1 Earnings Snapshot
# llm_msg:
# {'response': {'company': ['Mizuho'], 'category_tags': ['Earnings', 'Financial Report', 'Q1'], 'relation_tags': ['Fiscal', 'Snapshot'], 'date_': 'Q1'}, 'prompt': '\nAnalyze the key concepts of the given text.\n-----------text-----------\nMizuho: Fiscal Q1 Earnings Snapshot\n\nRespond with the following JSON schema: {json_schema}'}
# ==========
# text: Mizuho: Fiscal Q1 Earnings Snapshot
# llm_msg:
# {'response': {'company': ['Mizuho'], 'category_tags': ['Earnings', 'Financial Report', 'Q1'], 'relation_tags': ['Fiscal', 'Snapshot'], 'date_': 'Q1'}, 'prompt': '\nAnalyze the key concepts of the given text.\n-----------text-----------\nMizuho: Fiscal Q1 Earnings Snapshot\n\nRespond with the following JSON schema: {json_schema}'}
# ==========
# text: Mizuho: Fiscal Q1 Earnings Snapshot
# llm_msg:
# {'response': {'company': ['Mizuho'], 'category_tags': ['Earnings', 'Fiscal Q1'], 'relation_tags': ['Earnings Snapshot'], 'date_': 'N/A'}, 'prompt': '\nAnalyze the key concepts of the given text.\n-----------text-----------\nMizuho: Fiscal Q1 Earnings Snapshot\n\nRespond with the following JSON schema: {json_schema}'}
# ==========
# text: Ola Electric to Raise $734 Million in India's Biggest IPO This Year
# llm_msg:
# {'response': {'company': ['Ola Electric'], 'category_tags': ['IPO', 'Electric Vehicles', 'Finance', 'Investment'], 'relation_tags': ['raising funds', 'biggest IPO in India', '2023'], 'date_': '2023'}, 'prompt': "\nAnalyze the key concepts of the given text.\n-----------text-----------\nOla Electric to Raise $734 Million in India's Biggest IPO This Year\n\nRespond with the following JSON schema: {json_schema}"}
# ==========
# text: MapMyIndia Accuses Ola Of Stealing Its Data To Build Ola Maps, Sends Legal Notice
# llm_msg:
# {'response': {'company': ['MapMyIndia', 'Ola'], 'category_tags': ['legal', 'technology', 'data privacy'], 'relation_tags': ['accusation', 'data theft', 'legal notice'], 'date_': 'not specified'}, 'prompt': '\nAnalyze the key concepts of the given text.\n-----------text-----------\nMapMyIndia Accuses Ola Of Stealing Its Data To Build Ola Maps, Sends Legal Notice\n\nRespond with the following JSON schema: {json_schema}'}
# ==========
# text: Indian startups gut valuations ahead of IPO push
# llm_msg:
# {'response': {'company': ['Indian startups'], 'category_tags': ['valuations', 'IPO', 'startups', 'finance'], 'relation_tags': ['gut valuations', 'IPO push'], 'date_': ''}, 'prompt': '\nAnalyze the key concepts of the given text.\n-----------text-----------\nIndian startups gut valuations ahead of IPO push\n\nRespond with the following JSON schema: {json_schema}'}
# ==========

```



# JSON extraction from question

```bash
# generate triplets from text
python3 -u rag/engine_kg.py kg_triplets_extract_v2 --dirin "./ztmp/df_LZ_merge_90k_tmp.parquet" --dirout "./ztmp/df_LZ_merge_90k_tmp_relations.parquet" --istart 0 --nrows 25


# generate questions from triplets
python3 -u rag/engine_kg.py kg_generate_questions_from_triplets --dirin "./ztmp/df_LZ_merge_90k_tmp_relations_0_0_25.parquet" --dirout "./ztmp/df_LZ_merge_90k_tmp_questions_0_0_25.parquet"


```

```python
import os
from utilmy import pd_read_file
from rag.llm import LLM
from rag_summ import llm_generate_json_from_question
from pydantic import BaseModel

df = pd_read_file("../ztmp/df_LZ_merge_90k_tmp_questions_0_0_25.parquet")
llm1 = LLM('openai', 'gpt-4o', api_key=os.environ['OPENAI_API_KEY'])


for i, row in df.iterrows():
    print(row.question)
    json_output = llm_generate_json_from_question(query=row.question)
    print(json_output)
    print("="*20)

# output: 
# What is the parent organization of Ola?
# openai gpt-4o-mini <openai.OpenAI object at 0x7235ee2c9110>
# HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
# {'company': ['Ola'], 'category_tags': ['Transportation', 'Ride-sharing', 'Technology'], 'relation_tags': ['parent organization'], 'date': '', 'date_period': '', 'task': ['Identify the parent organization of Ola']}
# ====================
# Which company is a subsidiary of SoftBank?
# openai gpt-4o-mini <openai.OpenAI object at 0x7235e4f57450>
# HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
# {'company': [], 'category_tags': ['subsidiary', 'corporate structure', 'business'], 'relation_tags': ['SoftBank', 'subsidiary relationship'], 'date': '', 'date_period': '', 'task': ['Identify the subsidiary of SoftBank']}
# ====================
# What product or material is produced by Microsoft Corporation?
# openai gpt-4o-mini <openai.OpenAI object at 0x7235dab799d0>
# HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
# {'company': ['Microsoft Corporation'], 'category_tags': ['technology', 'software', 'hardware'], 'relation_tags': ['produces', 'manufactures'], 'date': '', 'date_period': '', 'task': ['analyze', 'identify', 'categorize']}
# ====================
# Who is the developer of Xbox?
# openai gpt-4o-mini <openai.OpenAI object at 0x7235dab7b6d0>
# HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
# {'company': ['Microsoft'], 'category_tags': ['gaming', 'technology'], 'relation_tags': ['developer', 'Xbox'], 'date': '', 'date_period': '', 'task': ['Identify the developer of Xbox']}
# ====================
# What platform is Microsoft 365 a part of?
# openai gpt-4o-mini <openai.OpenAI object at 0x7235dabb6410>
# HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
# {'company': ['Microsoft'], 'category_tags': ['software', 'cloud services', 'productivity suite'], 'relation_tags': ['Microsoft 365', 'platform'], 'date': '', 'date_period': '', 'task': ['Identify the platform associated with Microsoft 365']}
# ====================
# What is OneDrive's role as a part of Microsoft 365?
# openai gpt-4o-mini <openai.OpenAI object at 0x7235daba5b90>
# HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
# {'company': ['Microsoft'], 'category_tags': ['cloud storage', 'productivity', 'software'], 'relation_tags': ['Microsoft 365', 'OneDrive'], 'date': '', 'date_period': '', 'task': ["Analyze OneDrive's role", 'Identify components of Microsoft 365']}
# ====================
# How does SharePoint contribute to the services offered within Microsoft 365?
# openai gpt-4o-mini <openai.OpenAI object at 0x7235dab85d50>
# HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
# {'company': ['Microsoft'], 'category_tags': ['SharePoint', 'Microsoft 365', 'Cloud Services', 'Collaboration Tools'], 'relation_tags': ['Integration', 'Productivity', 'Team Collaboration'], 'date': '2023-10', 'date_period': 'Current', 'task': ["Analyze SharePoint's role", 'Identify contributions to Microsoft 365 services']}
# ====================
# What features does Commvault Cloud provide as a part of Microsoft 365?
# openai gpt-4o-mini <openai.OpenAI object at 0x7235dab9ecd0>
# HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
# {'company': ['Commvault', 'Microsoft'], 'category_tags': ['Cloud Services', 'Data Protection', 'Backup Solutions'], 'relation_tags': ['Microsoft 365 Integration', 'Cloud Features'], 'date': '', 'date_period': '', 'task': ['Analyze features', 'Identify integration capabilities']}
# ====================
# What products or materials does Microsoft offer through Azure?
# openai gpt-4o-mini <openai.OpenAI object at 0x7235dabc0950>
# HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
# {'company': ['Microsoft'], 'category_tags': ['cloud computing', 'Azure', 'products', 'materials'], 'relation_tags': ['offers', 'through'], 'date': '', 'date_period': '', 'task': ['analyze', 'identify products', 'identify materials']}
# ====================
# How is Microsoft involved in the development of Azure as a platform for developers?
# openai gpt-4o-mini <openai.OpenAI object at 0x7235dab795d0>
# HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
# {'company': ['Microsoft'], 'category_tags': ['cloud computing', 'platform development', 'software development'], 'relation_tags': ['involvement', 'development', 'platform'], 'date': '', 'date_period': '', 'task': ['analyze Microsoft’s role in Azure development', 'identify key components of Azure as a platform for developers']}
# ====================
# What are some of the components included in Microsoft Office Professional Plus?
# openai gpt-4o-mini <openai.OpenAI object at 0x7235daba7c90>
# HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
# {'company': ['Microsoft'], 'category_tags': ['Office Suite', 'Software'], 'relation_tags': ['Professional Plus', 'Components'], 'date': '', 'date_period': '', 'task': ['Identify components of Microsoft Office Professional Plus']}
# ====================
# What program is a part of Microsoft Office that allows users to manage emails and calendars?
# openai gpt-4o-mini <openai.OpenAI object at 0x7235dabf1290>
# HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
# {'company': ['Microsoft'], 'category_tags': ['Office Suite', 'Email Management', 'Calendar Management'], 'relation_tags': ['software', 'product'], 'date': '', 'date_period': '', 'task': ['manage emails', 'manage calendars']}
# ====================
# Which Microsoft Office program is used for taking notes and organizing information?
# openai gpt-4o-mini <openai.OpenAI object at 0x7235dabc0b10>
# HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
# {'company': ['Microsoft'], 'category_tags': ['Office Suite', 'Productivity', 'Note-taking'], 'relation_tags': ['software', 'application', 'information management'], 'date': '', 'date_period': '', 'task': ['taking notes', 'organizing information']}
# ====================
# What is the name of the program in Microsoft Office used for creating professional-looking publications?
# openai gpt-4o-mini <openai.OpenAI object at 0x7235d8f5cc10>
# HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
# {'company': ['Microsoft'], 'category_tags': ['Office Suite', 'Publishing'], 'relation_tags': ['program', 'publications'], 'date': '', 'date_period': '', 'task': ['identify program name', 'create publications']}
# ====================
# Which program in Microsoft Office is used for creating and managing databases?
# openai gpt-4o-mini <openai.OpenAI object at 0x7235d8f34910>
# HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
# {'company': ['Microsoft'], 'category_tags': ['Office Suite', 'Database Management'], 'relation_tags': ['program', 'database'], 'date': '', 'date_period': '', 'task': ['creating databases', 'managing databases']}
# ====================
# What software suite does Microsoft Office Professional Plus belong to?
# openai gpt-4o-mini <openai.OpenAI object at 0x7235d8f05150>
# HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
# {'company': ['Microsoft'], 'category_tags': ['software', 'office suite', 'product'], 'relation_tags': ['belongs to'], 'date': '', 'date_period': '', 'task': ['identify software suite', 'determine belonging']}
# ====================
# Which software program is a component of Microsoft Office?
# openai gpt-4o-mini <openai.OpenAI object at 0x7235dabf2550>
# HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
# {'company': ['Microsoft'], 'category_tags': ['software', 'office suite'], 'relation_tags': ['component', 'program'], 'date': '', 'date_period': '', 'task': ['identify software program', 'list components of Microsoft Office']}
# ====================
# What is one component of Microsoft Office besides Outlook?
# openai gpt-4o-mini <openai.OpenAI object at 0x7235dab86750>
# HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
# {'company': ['Microsoft'], 'category_tags': ['Office Suite', 'Productivity Software'], 'relation_tags': ['Software', 'Email Client'], 'date': '', 'date_period': '', 'task': ['Identify components of Microsoft Office']}
# ====================
# What program, in addition to Outlook, is included in Microsoft Office?
# openai gpt-4o-mini <openai.OpenAI object at 0x7235d8f34990>
# HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
# {'company': ['Microsoft'], 'category_tags': ['software', 'office suite'], 'relation_tags': ['Outlook', 'Microsoft Office'], 'date': '', 'date_period': '', 'task': ['Identify additional programs in Microsoft Office']}
# ====================
```