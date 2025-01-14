#!/bin/bash
echo "S3 role input: $1"


if [[ -z $1  ]];  then
   echo " not selected prd, dev, stg"
   exit 
fi

if [[ $1 == 'prd' ]];  then
   profile='prd-backend'
   profle_role='PrdDeveloperRole'
fi 

if [[ $1 == 'stg' ]];  then
   profile='stg-backend'
   profle_role='StgBackendDeveloperRole'
fi


if [[ $1 == 'dev' ]];  then
   profile='dev-backend'
   profle_role='DevBackendDeveloperRole'
fi 


if [[ $1 == 'local' ]];  then
   profile='dev-backend'
   profle_role='DevBackendDeveloperRole'

   echo "starting localstack S3+mySQL"
   docker compose    --file  config/test/docker_localstack.yml   up   -d


   #########
   sleep 7
   echo "  to_awsmock   ;   echo USE_LOCALSTACK_S3=1 "
   #to_awsmock
   awslocal s3api create-bucket --bucket  'test--ml-team'  
   awslocal s3api create-bucket --bucket  'dev-bucket'  


   exit 

fi 



echo   "profile: $profile"
echo   "profile-role: $profile_role" 





######################################################################################
### Get Credentials
aws sts get-caller-identity --profile $profile


#### Caching
CRED_FILE=$(grep -l -R $profle_role  ~/.aws/cli/cache | tee /dev/tty);


#### Parse with JQuery store in Env variable
export AWS_ACCESS_KEY_ID=$(cat ${CRED_FILE} |     jq -r .Credentials.AccessKeyId)
export AWS_SECRET_ACCESS_KEY=$(cat ${CRED_FILE} | jq -r .Credentials.SecretAccessKey)
export AWS_SESSION_TOKEN=$(cat ${CRED_FILE} |     jq -r .Credentials.SessionToken)


echo "\nRole Expiry"
echo $(cat ${CRED_FILE} | jq -r .Credentials.Expiration)
echo "-------------------------------------------------------------------"


