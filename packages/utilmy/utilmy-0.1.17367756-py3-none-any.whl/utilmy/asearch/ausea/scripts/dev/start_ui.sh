#!/bin/bash
shopt -s expand_aliases
source scripts/bins/utils.sh


   echo "####  Quick check"
         export OPENAI_API_KEY=""
         export GEMINI_API_KEY=""

         echo "key"

         alias pysum="python3 -u rag/rag_summ2.py "
         # modelid="gpt-4o-2024-08-06"
         pysum search_run --query "What are the microsoft partnerships in 2024 ?"   --topk 1



   source scripts/bins/env.sh
   # loadenv "dev"


   echo "####  Start UI"

         export AISEARCH_ANSWER="rag"
         python ui/run_ui.py 



