#!/bin/bash
shopt -s expand_aliases
set -e
USAGE=$(
    cat <<-END

    ### CDK Build
      ./aws_task_update.sh  create/cdk_batch_dev.json


END
)
### No input, print doc
[ $# -eq 0 ] && echo -e "$USAGE" && exit 1 


cluster="edge-cluster"
cdk_base="create/cdk_batch_base.yaml"

cdk_json="$1"



########################################################################################################

   ls $cdk_base
   aws cloudformation validate-template --template-body "file://$cdk_base"


##### update of Update the stack  
   ##  The `--capabilities CAPABILITY_NAMED_IAM` flag is required if your stack includes IAM resources.
   stack="AiGenBatchStack"
   
   alias acf="aws cloudformation update-stack " 
   acf --stack-name $stack --template-body "file://$cdk_base" --parameters "file://$cdk_json" --capabilities CAPABILITY_NAMED_IAM



   ##### Picke up the taskarn
   sleep 40
   echo "sleep 40s"

   aws ecs list-task-definitions --family-prefix ai-gen-batch --sort DESC --query "taskDefinitionArns[0]" --output text



