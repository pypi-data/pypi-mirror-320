
Usage 
```
##########################################################################################
Docker :
  in mldock bucket

  App Docker Example :  OS + repo  , only for Prod Release

        mldock:app_{configname}_{YMD}_{GITCOMMIT_HASH_7char}


        export DNAME="$ECR/mldock:app_test_20230105_4282075"
        
        docker pull  $DNAME
        docker run -itd --rm  -n ml2 --platform linux/amd64  $DNAME
        docker exec -it  ml2  /bin/bash

        cd /opt/mlb/    #### App root

        #### Batch mode
        scripts/local/run_abatch.sh


        #### Service mode
        scripts/local/run_aservice.sh



  Base Docker Slim:  (for testing)
  .dkr.ecr.us-east-1.amazonaws.com/mldock:base_slim_20230105_e92

        git clone          ml 
        git checkout BRANCH
        cd ml/mlb






```



