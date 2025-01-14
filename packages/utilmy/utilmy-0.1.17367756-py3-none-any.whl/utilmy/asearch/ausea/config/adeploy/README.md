


###### Deploying with new dockerid ###########################
```bash

   ### Open 
     https://github.dev/zuu-usa/generate/blob/zdev/aigen/config/adeploy/create/cdk_batch_dev.json

   2) Pick up new dockerid
   
   3) Update this
             aigen/config/adeploy/create/cdk_batch_dev.json


   4) Commit /Push and update CDK  (or via UI)
      ##### Update Stack in DEV
      export AWS_PROFILE="dev"
      aws cloudformation update-stack --stack-name AiGenBatchStack --template-body file://create/cdk_batch_base.yaml --parameters file://create/cdk_batch_dev.json --capabilities CAPABILITY_NAMED_IAM
     
      in the AWS UI ECS, need to update 
          network_id VPC :   Not select the default one.
          security_group :     _ECS_

   5) Pick up with new CDK "aigen: version" after the CDK build update

   6) Update this  run/dev.json



```







###### Running job ###########################
```bash

#### Check in DEV
   taskid=$(cat run/dev.json)
   aws ecs describe-task-definition --task-definition $taskid --cluster "edge-clsuter" --query taskDefinition --output json

#### Run in Dev
     ./aws_task_run.sh    run/dev.json



#### Check in PRD
   taskid=$(cat run/dev.json)
   aws ecs describe-task-definition --task-definition $taskid --cluster "edge-clsuter" --query taskDefinition --output json

#### Run in PRD
     ./aws_task_run.sh    run/prd.json




```
















## Deploying the Stack with AWS CDK and AWS CLI
```bash


cd config/adeploy/




##############################################################################    
####   To deploy the stack using the `template.yaml` and the AWS CLI, follow these steps:

   ### Setup ENV in AWS CLI

   aws cloudformation validate-template --template-body file://create/cdk_batch_base.yaml



##### Create of Update the stack  ##########################################
   ##  The `--capabilities CAPABILITY_NAMED_IAM` flag is required if your stack includes IAM resources.

   # aws cloudformation create-stack --stack-name AiGenBatchStack --template-body file://config/deploy/cdk_fargate_batch.yaml --parameters file://config/deploy/cdk_fargate_batch_addon.json --capabilities CAPABILITY_NAMED_IAM



   ##### Update Stack in DEV
   export AWS_PROFILE="dev"
   aws cloudformation update-stack --stack-name AiGenBatchStack --template-body file://create/cdk_batch_base.yaml --parameters file://create/cdk_batch_dev.json --capabilities CAPABILITY_NAMED_IAM


   ##### Update Stack in PRD
   export AWS_PROFILE="prd"
   aws cloudformation update-stack --stack-name AiGenBatchStack --template-body file://create/cdk_batch_base.yaml --parameters file://create/cdk_batch_prd.json --capabilities CAPABILITY_NAMED_IAM



##### Check is the task is setup --> check if Docker ID is correct
      aws cloudformation describe-stacks --stack-name AiGenBatchStack



#### Get New task ARM
    aws ecs list-task-definitions --family-prefix ai-gen-batch --sort DESC --query "taskDefinitionArns[0]" --output text




#### Check current Launched
      aws cloudformation describe-stack-events --stack-name AiGenBatchStack



#### task ARM
aws ecs list-task-definitions --family-prefix ai-gen-batch --sort DESC --query "taskDefinitionArns[0]" --output text
### arn:aws:ecs:us-east-1:536922267020:task-definition/ai-gen-batch:23




CLUSTER_NAME="edge-cluster"
TASK_DEF_ARN=$(aws ecs list-task-definitions --output text --query 'taskDefinitionArns[0]')
TASK_ARNS=$(aws ecs list-tasks --cluster $CLUSTER_NAME --output text --query 'taskArns[]')


TASK_DEF_ARN=$(aws ecs list-task-definitions --output text --query 'taskDefinitionArns[0]')


### Full descniption tasl
aws ecs describe-tasks --cluster $CLUSTER_NAME --tasks "arn:aws:ecs:us-east-1:536922267020:task/edge-cluster/f169348f4be14ecaaf73a5dc94815799"



########## Isues
```bash
An error occurred (ValidationError) when calling the UpdateStack operation: Stack:arn:aws:cloudform
ation:us-east-1:710696934159:stack/AiGenBatchStack/a69185f0-2ec3-11ef-abf7-0affe09c20d1 is in ROLLB
ACK_COMPLETE state and can not be updated.
ROLLBACK_COMPLETE state:



#### Use the continue-update-rollback command to skip problematic resources:
export stackname="AiGenBatchStack"

aws cloudformation continue-update-rollback --stack-name <stack-name> --resources-to-skip <resource-name>
This allows you to skip specific failed resources and continue the rollback 3.


### Try to update the stack with --disable-rollback flag:
aws cloudformation update-stack --stack-name $stackname --use-previous-template --disable-rollback
This attempts to update the stack while disabling rollback 4.


### Use the rollback-stack command to roll back to the last stable state:
aws cloudformation rollback-stack --stack-name <stack-name>



```







#### Log available here
     https://app.datadoghq.com/logs?query=-service%3A%28edge-api%20OR%20financial-api%20OR%20edge-web%20OR%20cms%20OR%20error_job_monitor%20OR%20auth0%20OR%20edge-web-fluentd%20OR%20metabase%20OR%20job_elapsed_time_monitor%20OR%20disruptionSyncRunner%29&agg_m=count&agg_m_source=base&agg_t=count&cols=host%2Cservice&fromUser=true&messageDisplay=inline&refresh_mode=sliding&storage=hot&stream_sort=desc&viz=stream&from_ts=1718859774598&to_ts=1718860674598&live=true



##### Extra Tooling
   brew install jq yq
   yamllint --disable=max-line-length config/deploy/cdk_fargate_batch.yaml 




```
