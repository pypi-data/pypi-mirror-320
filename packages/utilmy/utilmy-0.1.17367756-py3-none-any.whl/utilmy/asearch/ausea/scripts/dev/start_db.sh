#!/bin/bash
shopt -s expand_aliases



#### Start Qdrant ############################
cd /opt/aigen/src/engine/usea/         
mkdir -p static   
mv /opt/work/static/* static/            
ls -a static 
which qdrant


qdrant --config-path "$(pwd)/rag/scripts/qdrant_config.yaml" 




