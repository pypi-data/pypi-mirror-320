#!/bin/bash
shopt -s expand_aliases
set -e
USAGE=$(
    cat <<-END

    ### To prevent mis-launch of task
      cd config/deploy/
      ./aws_task_run.sh  run/dev.json

      ./aws_task_run.sh  run/prd.json


    ### Latest batch
      cd config/deploy/
      aws_task_run.sh  latest


    ENI ID: eni-0d83a8e829c593c68 
    Subnet: subnet-291ddc4f 
    Security groups:  sg-6d94bc4e (default) 



END
)
### No input, print doc
[ $# -eq 0 ] && echo -e "$USAGE" && exit 1 


cluster="edge-cluster"


########################################################################################################
# Fetching subnets
# echo "Fetching subnets..."
SUBNET_IDS=$(aws ec2 describe-subnets --query "Subnets[*].SubnetId" --output text)
FIRST_SUBNET=$(echo $SUBNET_IDS | awk '{print $1}')
echo "Selected subnet: $FIRST_SUBNET"

# # Fetching security groups
echo "Fetching security groups..."
SECURITY_GROUP_IDS=$(aws ec2 describe-security-groups --query "SecurityGroups[*].GroupId" --output text)
FIRST_SECURITY_GROUP=$(echo $SECURITY_GROUP_IDS | awk '{print $1}')
echo "Selected security group: $FIRST_SECURITY_GROUP"



taskdef="$1"
if [[ "$taskdef" = latest ]]; then  

    # Fetching the latest task definition version
    echo "Fetching the latest task definition version..."
    TASK_DEFINITION_ARN=$(aws ecs list-task-definitions --family-prefix ai-gen-batch --sort DESC --query "taskDefinitionArns[0]" --output text)
    TASK_DEFINITION_VERSION=$(echo $TASK_DEFINITION_ARN | awk -F: '{print $7}')

    taskdef1="ai-gen-batch:$TASK_DEFINITION_VERSION"

else 

       ###  ./awx_task_run.sh run/dev.json     contains ai-gen-batch:24 
       filename=$taskdef  
       taskdef1="$(cat $filename)"
fi

echo "Selected task definition: $taskdef1"

if [ -z "$taskdef1" ]; then
  echo "$taskdef is empty taskid, exiting"
  exit 1
fi


echo $(aws ecs list-task-definitions --family-prefix ai-gen-batch --sort DESC --query "taskDefinitionArns[0]" --output text)


# exit

# Running ECS task
echo "AWS_PROFILE $AWS_PROFILE"
echo "Running ECS task..."
runtask=$(aws ecs run-task \
  --cluster edge-cluster \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$FIRST_SUBNET],securityGroups=[$FIRST_SECURITY_GROUP]}" \
  --task-definition "$taskdef1" \
  --count 1)

echo "Task started successfully. $taskdef1"
echo $runtask

  

#############################################################################
#### for test 
# runtask='{ "tasks": [ { "attachments": [ { "id": "9d0a3da6-f282-43a3-b1a1-66eaab4996ba", "type": "ElasticNetworkInterface", "status": "PRECREATED", "details": [ { "name": "subnetId", "value": "subnet-0f9d409e76e2d98dc" } ] } ], "attributes": [ { "name": "ecs.cpu-architecture", "value": "x86_64" } ], "availabilityZone": "us-east-1a", "clusterArn": "arn:aws:ecs:us-east-1:536922267020:cluster/edge-cluster", "containers": [ { "containerArn": "arn:aws:ecs:us-east-1:536922267020:container/edge-cluster/d369e1e1a17b4be18506166b16b75f4e/e40bdb02-c250-433c-a198-e18d86b5d900", "taskArn": "arn:aws:ecs:us-east-1:536922267020:task/edge-cluster/d369e1e1a17b4be18506166b16b75f4e", "name": "datadog-agent", "image": "536922267020.dkr.ecr.us-east-1.amazonaws.com/datadog-agent:latest", "lastStatus": "PENDING", "networkInterfaces": [], "cpu": "0" }, { "containerArn": "arn:aws:ecs:us-east-1:536922267020:container/edge-cluster/d369e1e1a17b4be18506166b16b75f4e/b4742667-931f-44d5-8d25-9844ab87eed3", "taskArn": "arn:aws:ecs:us-east-1:536922267020:task/edge-cluster/d369e1e1a17b4be18506166b16b75f4e", "name": "log-router", "image": "536922267020.dkr.ecr.us-east-1.amazonaws.com/aws-for-fluent-bit:latest", "lastStatus": "PENDING", "networkInterfaces": [], "cpu": "0", "memoryReservation": "50" }, { "containerArn": "arn:aws:ecs:us-east-1:536922267020:container/edge-cluster/d369e1e1a17b4be18506166b16b75f4e/7e5d6847-d033-469b-83c4-fa559a2be079", "taskArn": "arn:aws:ecs:us-east-1:536922267020:task/edge-cluster/d369e1e1a17b4be18506166b16b75f4e", "name": "ai-gen-batch", "image": "536922267020.dkr.ecr.us-east-1.amazonaws.com/ai-gen:c74441d9542b95cb9efa85ab9579bb690bf4814a", "lastStatus": "PENDING", "networkInterfaces": [], "cpu": "0" } ], "cpu": "4096", "createdAt": 1718875271.162, "desiredStatus": "RUNNING", "enableExecuteCommand": false, "group": "family:ai-gen-batch", "lastStatus": "PROVISIONING", "launchType": "FARGATE", "memory": "30720", "overrides": { "containerOverrides": [ { "name": "log-router" }, { "name": "ai-gen-batch" }, { "name": "datadog-agent" } ], "inferenceAcceleratorOverrides": [] }, "platformVersion": "1.4.0", "platformFamily": "Linux", "tags": [], "taskArn": "arn:aws:ecs:us-east-1:536922267020:task/edge-cluster/d369e1e1a17b4be18506166b16b75f4e", "taskDefinitionArn": "arn:aws:ecs:us-east-1:536922267020:task-definition/ai-gen-batch:19", "version": 1, "ephemeralStorage": { "sizeInGiB": 20 } } ], "failures": [] }'


export taskarn='echo "$runtask" | jq -r ".tasks[0].taskArn" '
export taskarn="$(eval $taskarn)"
echo "$taskarn" 

echo "Waiting container to start 180s: $taskarn"
echo $(aws ecs describe-tasks --cluster "$cluster" --tasks "$taskarn" --query "tasks[*].lastStatus")
sleep 180



echo "Status: "
jobstatus=$(aws ecs describe-tasks --cluster "$cluster" --tasks "$taskarn" --query "tasks[*].lastStatus")
echo $jobstatus


if [[ "$jobstatus" != *"RUNNING"* ]]; then
    echo "Error: Status does not contain 'RUNNING' --> Failed launched"

    echo $(aws ecs describe-tasks --cluster "$cluster" --tasks "$taskarn" --query "tasks[*].lastStatus")

    exit 1
fi





