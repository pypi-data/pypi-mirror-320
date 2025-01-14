#!/bin/bash
USAGE=$(
      cat <<-END

       rag/scripts/run.sh         --> Print the doc

       ####  Run the benchmark
          rag/scripts/run.sh bench  --dirquery  /kg_questions/common_test_questions.parquet  --topk 5  --dirout "./ztmp/bench/ag_news"


       #### start the qdrant, neo4j DB
           ./rag/scripts/run.sh start_db


END
)




#### Global Config. ###############################################
    # set -x  # Output commands being run.
    set -e # Exit on error.å
    shopt -s expand_aliases


#### Global vars ##################################################
    FUNAME=$(basename "$0")
    YMD=$(date '+%Y%m%d')
    this_file_dir="$(dirname "$0")"





### Input Params and Defaults ##################################
    [ $# -eq 0 ] && echo -e "$USAGE" && exit ###  No input print doc
    task=$1 && [ -z $1 ] && task="size"      ###  task
    # dir0=$2 && [ -z $2 ] && dir0="$PWD"      ###  current path as default




### Core #######################################################
if [[ "$task" = bench ]]; then

      ###### Input params
      dirquery="ztmp/bench/ag_news/kg_questions/common_test_questions.parquet"
      dirout="ztmp/bench/ag_news/out"
      topk="5"
      
      while [[ $# -gt 0 ]]; do
        case $1 in
            --dirquery)  dirquery="$2";  shift 2 ;;
            --topk)      topk="$2";      shift 2 ;;
            --dirout)    dirout="$2";    shift 2 ;;

        esac
      done
      
      echo "dirquery: $dirquery"
      echo "dirout:   $dirout"
      echo "topk:     $topk"



    ###### Core Script
    alias pybench="python  rag/bench.py "
    alias pykg="   python  rag/engine_kg.py "
    
    
    export dirout1="rag/docs/zlogs.md"



    echo "# All benchmarks - `date -I`" >> "$dirout1"
    echo "\`\`\`" >> "$dirout1"

    echo "## dense run" >> "$dirout1"
    pybench bench_v1_dense_run --dirquery "$dirquery" --topk "$topk" | grep -v 'HTTP Request:'>> "$dirout1"
    echo -e "\n\n" >> "$dirout1"

    echo "## sparse run" >> "$dirout1"
    pybench bench_v1_sparse_run --dirquery "$dirquery" --topk "$topk" | grep -v 'HTTP Request:'>> "$dirout1"
    echo -e "\n\n" >> "$dirout1"

    echo "## tantivy run" >> "$dirout1"
    pybench bench_v1_tantivy_run --dirquery "$dirquery" --topk "$topk" >> "$dirout1"
    echo -e "\n\n" >> "$dirout1"


    echo "## neo4j run" >> "$dirout1"
    pybench bench_v1_neo4j_run --dirquery "$dirquery" --topk "$topk" >> "$dirout1"
    echo -e "\n\n" >> "$dirout1"

    echo "## sparse+ neo4j run" >> "$dirout1"
    pybench bench_v1_fusion_run --engine "sparse_neo4j" --dirquery "$dirquery" --topk "$topk" | grep -v 'HTTP Request:' >> "$dirout1"
    echo -e "\n\n" >> "$dirout1"

    echo "## dense+ neo4j run" >> "$dirout1"
    pybench bench_v1_fusion_run --engine "dense_neo4j" --dirquery "$dirquery" --topk "$topk" | grep -v 'HTTP Request:' >> "$dirout1"
    echo -e "\n\n" >> "$dirout1"

    echo "## tantivy+ neo4j run" >> "$dirout1"
    pybench bench_v1_fusion_run --engine "tantivy_neo4j" --dirquery "$dirquery" --topk "$topk"  >> "$dirout1"
    echo -e "\n\n" >> "$dirout1"

    # generate text from metrics
    pybench report_create_textsample --dirquery "$dirquery"
    echo "\`\`\`" >> "$dirout1"









########################################################################
exit 0
elif [[ "$task" = start_db ]]; then
      # ssize=$3 && [ -z $3 ] && ssize=20
      ###  ./rag/zrun.sh start_db


      echo -e "\n Starting Qdrant on port 6333"
      echo  "qdrant on  http://localhost:6333/dashboard"
        # ./ztmp/bins/qdrant --config-path ./rag/qdrant_config.yaml &
         sudo docker run -d -p 6333:6333     -v  ./ztmp/db//qdrant_storage:/qdrant/storage:     qdrant/qdrant   



      echo -e "\nStarting neo4j"
      echo -e "\n neo4j UI on http://localhost:7474/browser"
          sudo /opt/neo4j/bin/neo4j start    &






exit 0
elif [[ "$task" = qdrant ]]; then

        echo "download qdrant binary in asearch/ztmp/"
        .ztmp/qdrant --config-path "$(PWD)/rag/scripts/qdrant_config.yaml"



exit 0
elif [[ "$task" = task3 ]]; then
      ### recent file modified files + created
      ssize=$3 && [ -z $3 ] && ssize=20













exit 0
else
      echo $USAGE
fi









