#!/bin/bash
shopt -s expand_aliases
source "scripts/bins/utils.sh"
source "scripts/bins/env.sh"
# source "scripts/bins/prod.sh"    ### Cannot be used due to issue in python import
###   scripts/dev/run_batch.sh config/dev/cfg_dev_istest.yaml logging_debug 



########## Local LOGS #####################################################
export LOGDIR="ztmp/log/"
mkdir -p $LOGDIR
export LOGFILE="${LOGDIR}_log.log"


########## LOGS ###########################################################
###   base, logging_info, logging_debug
logmode="$2"
if [[ -z $2 ]]; then 
   logmode="base"
fi 
source "scripts/bins/log.sh" $logmode
echo "log_config: $log_config"
# export log_verbosity=3
# export log_type="base"
# export log_config="log_level:DEBUG;log_file:ztmp/log/log;rotate_time:s;rotate_interval:30"
# export log_type="logging"
# export log_config="log_level:DEBUG"

########## Config ########################################################
cconfig="$1"
if [[ -z $1 ]]; then 
   cconfig="config/dev/cfg_dev.yaml"
fi 
echo  "config:  $cconfig"



function init_check() {
   echo "##### Docker check ##########"
   which python
   aws sts get-caller-identity
   echo $PYTHONPATH
   aws s3 ls s3://edge-ml-dev  
   df -h
   echo "EFS Mount:"
   ls /mnt/efs
   echo "HOME SIZE"
   du -h --max-depth=1 ~

}



##########################################################################
echo  -e "### Start  $(date_now)  \n" 2>&1 | tee  "${LOGFILE}"



   #### memory 
   monitor_cpu_ram & 
   monitor_python  &
   monitor_topc    &
   # monitor_purge_tempfs  14000 &  ### Delete in tmp/ to prevent overflow



   
   alias pyfet="python src/fetchers.py  "

   
   export CACHE_ENABLE="0"
   export log_prefix='--URL:'


  while true; do 

         echo  -e "### Start run_extract Loop  $(date_now)  \n" 
         init_check 


         ########################################################
         # echo "###### News  Extra"
         # pyfet  run_newstext --cfg  $cconfig &



         ########################################################
         echo "###### Fetch googleNews URL List:"
             pyfet run_urlist        --cfg $cconfig



         ########################################################
         #### Need PR website
         #echo "###### Fetch PR website"
         #   pyfet  run_urlist_prnews --cfg  $cconfig 


           

         clean_tempfs &  

        
done ;









###### Wating last process to finish ##############################################################
# while true; do
#   if ! pgrep -x "python" > /dev/null; then
#     echo "No Python processes running. Breaking loop."
#     break
#   fi
#   sleep 120
# done





##################################################################################################
# next_hour_ts=$(date +%s)

# while true; do
#    current_ts=$(date +%s)
#    #next_hour_ts=$(date_get_next_hour_ts 03 )    # unix  in the next hour at exactly 03 minutes.

#             #### Run Once Config ONLY
#             echo "run_service_pred_replay Start at:  $(date_now)"
#             #python src/run.py  run_service_pred_replay  --config $cconfig
#             python src/run.py  run_service_pred_replay  --config $cconfig

#   #next_ymd=$(date_unix_todate $next_hour_ts ) 
#   echo "###now: $(date_now) "
#   sleep 10

# done


echo -e $LINE_END  2>&1 | tee  -a "${LOGFILE}"






