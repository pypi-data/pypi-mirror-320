#!/bin/bash
### source scripts/bins/env.sh

shopt -s expand_aliases

export root=$(pwd)
echo "root:  $root"



######## PYTHON ######################################
# export PYTHONPATH="$root/../aigen"
# export PYTHONPATH="$root/../aigen/src/frame/:$PYTHONPATH"

export PYTHONPATH="$root"
export PYTHONPATH="$root/src/engine/usea:$PYTHONPATH"

echo "PYTHONPATH:  $PYTHONPATH"


export AWS_DEFAULT_REGION='us-east-1'




