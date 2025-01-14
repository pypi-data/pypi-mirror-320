
############################################################################################
### Install
```bash

    ### Qdrant (docker or local one)

    ### How to run qdrant from binary file
        # download latest tar.gz package file from here, Linux: 
            wget -c https://github.com/qdrant/qdrant/releases/download/

        # extract tar.gz package
            tar -xvf qdrant-x86_64-unknown-linux-gnu.tar.gz
           
                    
            dircurr=$(PWD)
            .ztmp/qdrant --config-path "$(PWD)/rag/scripts/qdrant_config.yaml"
            
            ### Download the web UI files:
               ./tools/sync-web-ui.sh
            
            ### If issues persist, use Docker:            
               docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
                        

            #### Need Spacy model                        
               python -m spacy download en_core_web_sm
            



    ### Running from docker 
       ### How to run
        sudo docker run -d -p 6333:6333     -v  ./ztmp/db/qdrant_storage:/qdrant/storage     qdrant/qdrant



    ### Neo4J

     #### Local Neo4j Install (less memory)
        installation steps (https://neo4j.com/docs/operations-manual/current/installation/linux/tarball/):
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

        ### Docker version:
            docker run --publish=7474:7474 --publish=7687:7687 --volume=$HOME/neo4j/data:/data --volume=$HOME/neo4j/logs:/logs neo4j:4.4.34-community

            http://localhost:7474/browser/
            neo4j / neo4j




    ###
````







#################################################################################
##### LZ dataset indexing
```bash
    

    from utilmy import pd_read_file, pd_to_file, hash_int64
    # preprocessing
    df = pd_read_file("../ztmp/df_LZ_merge_90k.parquet")
    df["text_id"] = df["url"].apply(lambda x:hash_int64(x))
    df.rename(columns={"pred-L1_cat":"L1_cat", "pred-L2_cat":"L2_cat", "pred-L3_cat":"L3_cat", "pred-L4_cat":"L4_cat"}, inplace=True)
    df.fillna("", inplace=True)
    pd_to_file(df, "../ztmp/df_LZ_merge_90k_tmp.parquet")

    
    
    
    ## qdrant sparse indexing
    alias pyqd="python3 -u rag/engine_qd.py  "
    alias pykg="python3 -u rag/engine_kg.py"
    export dirtmp="./ztmp"
    
    # create collection
    pyqd  qdrant_sparse_create_collection --server_url "http://localhost:6333" --collection_name "LZnews"
    
    # set payload settings
    pyqd  qdrant_update_payload_indexes --server_url "http://localhost:6333" --collection_name "LZnews" --payload_settings "{'L0_catnews': 'text', 'L1_cat': 'text', 'L2_cat': 'text', 'L3_cat': 'text', 'L4_cat': 'text'}"
    
    # index documents
    pyqd  qdrant_sparse_create_index --dirin "$dirtmp/df_LZ_merge_90k_tmp.parquet" --server_url "http://localhost:6333" --collection_name "LZnews" --colscat "['L0_catnews', 'L1_cat', 'L2_cat', 'L3_cat', 'L4_cat', 'text_id', 'title']" --coltext "text" --batch_size 1 --max_words 256 --imax 10
    
    
    
    ####################################
    # sqlite data saving
    # create table with column settings
    pykg dbsql_create_table --db_path "$dirtmp/db/db_sqlite/datasets.db" --table_name "LZnews" --columns '{"text_id": "VARCHAR(255) PRIMARY KEY","url": "VARCHAR(255)", "title": "VARCHAR(255)", "date": "VARCHAR(255)", "text": "TEXT", "text_summary": "TEXT", "L0_catnews": "VARCHAR(255)", "L1_cat": "VARCHAR(255)", "L2_cat": "VARCHAR(255)", "L3_cat": "VARCHAR(255)", "L4_cat": "VARCHAR(255)", "com_extract": "VARCHAR(255)"}'
    
    
    # insert records in sqlite
    pykg dbsql_save_records_to_db --db_path "$dirtmp/db/db_sqlite/datasets.db" --table_name "LZnews" --coltext "text" --colscat '["url", "date", "title","text", "text_summary", "L0_catnews", "L1_cat", "L2_cat", "L3_cat", "L4_cat", "com_extract"]' --colid "text_id" --nrows -1








```


















############################################################################################
### Generate Prompt, query from Answers using GPT-3.5
```
  ### generate prompt via DSPy
     export PYTHONPATH="$(pwd)"
     python rag/llm.py prompt_find_best --dirdata "./ztmp/bench/norm/"  --dataset "ag_news"  --dirout ./ztmp/exp  

          --> Add 1 prompt to PromptStorage Saved in ztmp/prompt_hist.csv
          --> Pick up manually promptid from ztmp/prompt_hist.csv


  ### Generate synthetic from specific Prompt-id (using default promptStorage path)
     python rag/dataprep.py generator_synthetic_question --dirdata "./ztmp/bench/ag_news/norm/" --nfile 70 --nquery 100 --prompt_id "20240507-671"

          -->  saves queries in ztmp/bench/ag_news/query/df_synthetic_queries_{dt}.parquet

          export dirquery="ztmp/bench/ag_news/query/df_synthetic_queries_20240509_171632.parquet" 








############################################################################################
###### Benchmark Engine  ###################################################################
    export PYTHONPATH="$(pwd)"
    alias pybench=" python3 -u rag/bench.py ";
    function echo2() { echo -e "$1" >> zresults.md; }


    #### Runs:

       ./rag/zruns.sh bench  contains the  starting script




#### Prepare parquet data to feed Engine Indexes 
   # pybench bench_v1_data_convert  --dirin "./ztmp/hf_dataset/ag_news/"    --dirout "./ztmp/bench/ag_news"


#### Create Engine Indexes for later retrieval
   dataset=="ag_news"
   dirdata="ztmp/bench"

   ### Load data from f"ztmp/bench/norm/ag_news/" 
   pybench bench_v1_create_sparse_indexes  --dirdata_root $dirdata

   pybench bench_v1_create_dense_indexes   --dirdata_root $dirdata

   pybench bench_v1_create_tantivy_indexes --dirdata_root $dirdata



#### Generate bechnmark of retrieval engine using query file.

    dirquery="ztmp/bench/ag_news/query/df_synthetic_queries_20240509_171632.parquet" 

    echo2 `date`
    echo2 "\`\`\`" ;

    echo2 "### dense run"
    pybench bench_v1_dense_run   --dirquery $dirquery  >> zresults.md

    
    echo2 "### sparse run"
    pybench bench_v1_sparse_run  --dirquery $dirquery  >> zresults.md;
    
    echo2 "### tantivy run"
    pybench bench_v1_tantivy_run --dirquery $dirquery  >> zresults.md;


    echo2 "\`\`\`"
    echo2 "---" 



#### Create Analysis report
    pybench create_error_report --dirin "ztmp/bench/"  --dataset $dataset --dirquery $dirquery 






###### kg search #################################################################################

      ### Nebula KG DB
        cd asearch
        export PYTHONPATH="$(pwd)"  ### relative import issue
        alias pykg="python3 -u rag/engine_kg.py  "

        ###############################################
        #### Create test data using Wikipedia/LlamaIndex
           pykg test_create_test_data --dirout ztmp/kg/testraw.csv
                
        ### Extract  triplets From raw text and save to csv 
           pykg  kg_model_extract --dirin myraw.csv --model_id Babelscape/rebel-large -- dirout ztmp/kg/data/kg_relation.csv
        

        ### Extract the triplet from  agnews Data --> Store in csv file  ( Need Rebel-Large to prevent empty triplet....)
           pykg  kg_model_extract --model_id Babelscape/rebel-large  --dirin ztmp/bench/norm/ag_news/test/df_*.parquet  --dirout ztmp/kg/data/agnews_kg_relation_test.csv --coltxt body --nrows 1000000 --batch_size 25 


        ################################################
        # generate Query from Inverting from triplets (using LlamaIndex and GPT3.5 )
           pykg kg_generate_questions_from_triplets --dirin ztmp/kg/data/agnews_kg_relation.csv --dirout ztmp/kg/data/agnews_kg_questions.csv --batch_size 20

        # benchmark queries using Nebula Graph
           pykg kg_benchmark_queries --dirin ztmp/kg/data/agnews_kg_questions.csv --dirout ztmp/kg/data/agnews_kg_benchmark.csv --queries=1000



        ###############################################
        ## neo4j insert
            pykg neo4j_db_insert_triplet_file --dirin ztmp/kg/data/kg_relation.csv --db_name "neo4j"  --nrows -1




     #### Neo4j Install
        installation steps (https://neo4j.com/docs/operations-manual/current/installation/linux/tarball/):
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

        docker run --publish=7474:7474 --publish=7687:7687 --volume=$HOME/neo4j/data:/data --volume=$HOME/neo4j/logs:/logs neo4j:4.4.34-community

        http://localhost:7474/browser/
           neo4j / neo4j


     #### Insert / Query sample with neo4J
        export PYTHONPATH="$(pwd)"  ### relative import issue
        alias pykg=" python3 -u rag/engine_kg.py ";


        # extract triplets from dataset and store to csv
        pykg kg_model_extract --dirin "ztmp/bench/norm/ag_news/*/*.parquet", model_id="Babelscape/rebel-large", dirout="ztmp/kg/data/kg_relation.csv",
                            nrows=100000,
                            colid="id", coltxt="text"): 

        # store dataset id, text in localdb
        pykg localstorage_save_records_to_db --dirin "ztmp/bench/norm/ag_news/*/*.parquet" --table_name "agnews" --coltext "body" --colid "id"



        # create neo4j db with constraints
        pykg neo4j_create_db --db_name "neo4j"


        # store triplets along with doc_ids in neo4j db
        pykg neo4j_db_insert_triplet_file --dirin "ztmp/kg/data/kg_relation.csv" --db_name "neo4j"

        # search documents in neo4j
        pykg neo4j_search_docs --db_name "neo4j" --query "Who visited Chechnya?"






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
         pykg dbsql_save_records_to_db --dirin "$dir0/aparquet/*.parquet" --db_path "./ztmp/db/db_sqlite/datasets.db" --table_name "agnews"


         # 4. insert triplets into neo4j
         pykg neo4j_db_insert_triplet_file --dirin "$dir0/kg_triplets/*.parquet" --db_name "neo4j"


      ###### 5. generate questions from triplets
         pykg kg_generate_questions_from_triplets --dirin "$dir0/kg_triplets/*.parquet" --dirout="$dir0/kg_questions/common_test_questions.parquet" --nrows 100 --batch_size 5




      ###### 6. qdrant dense Insert indexing
         pybench bench_v1_create_dense_indexes --dirbench "$dir0" --dataset "ag_news" 


      ###### 7. qdrant sparse indexing
         pybench bench_v1_create_sparse_indexes --dirbench "$dir0" --dataset "ag_news" 



      ##### runs Benchmark 
         echo -e "\n\n####### Benchmark Results `date -I`" >> rag/zlogs.md
         echo '```bash ' >> rag/zlogs.md 
   
   
         echo -e '\n########## sparse run' >> rag/zlogs.md 
         pybench bench_v1_sparse_run --dirquery "$dir0/kg_questions/common_test_questions.parquet" --topk 5 >> rag/zlogs.md


         echo -e '\n########## dense run' >> rag/zlogs.md 
         pybench bench_v1_dense_run --dirquery "$dir0/kg_questions/common_test_questions.parquet" --topk 5 >> rag/zlogs.md
         echo '```' >> rag/zlogs.md

         echo -e '\n########## neo4j run' >> rag/zlogs.md 
         pybench bench_v1_neo4j_run --dirquery "$dir0/kg_questions/common_test_questions.parquet" --topk 5 >> rag/zlogs.md


```

