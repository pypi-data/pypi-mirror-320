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


########## LOGS ############################################################
###   base, logging_info, logging_debug
logmode="$2"  && [ -z $2 ] &&  logmode="base"

source "scripts/bins/log.sh" $logmode
echo "log_config: $log_config"
# export log_verbosity=3
# export log_type="base"
# export log_config="log_level:DEBUG;log_file:ztmp/log/log;rotate_time:s;rotate_interval:30"
# export log_type="logging"
# export log_config="log_level:DEBUG"


########## Config #########################################################
cconfig="$1"   && [ -z $1 ] &&  cconfig="config/dev/cfg_dev.yaml"
echo  "config:  $cconfig"



######### Max rows ############################################################
nmax=$3   && [ -z $3 ] && nmax="10"



##########################################################################
function init_check() {
   echo "##### Docker check ##########"
   which python
   aws sts get-caller-identity
   echo $PYTHONPATH
   aws s3 ls s3://edge-ml-dev  
   df -h
   ls /mnt/efs
}

function echo2 () {   
    echo -e "--INFER: $1" 
}



###########################################################################
echo2 "### Start  $(date_now)  \n" 2>&1 | tee  "${LOGFILE}"

   #### Check If all are OK
   # init_check

   #### memory 
   monitor_cpu_ram   & 
   monitor_python    &
   monitor_topc      &
   # monitor_purge_tempfs  14000 &  ### Delete in tmp/ to prevent overflow


   export  log_prefix='--INFER:'

   alias   pycat="python src/cats.py  "

   export  CACHE_ENABLE="0"

   export  cfg=$cconfig


  # while true; do 

         echo2   "### Start run_batch_infer.sh  $(date_now)  \n" 
         init_check 

                 
         ########################################################
         echo2 "###### AWS sync to EFS"

              mkdir -p /mnt/efs/models/latest
              aws s3 sync s3://edge-ml-dev/models/latest/   /mnt/efs/models/latest

              ls -a /mnt/efs/models/latest

              ls -a /mnt/efs/models/latest/L1_cat



         ########################################################
         echo2 "###### Infer Level 0"
               python src/cats.py pipe_predict_L0_catnews --cfg $cfg --past_days -5



         echo2 "###### com_extraction"
               python src/cats.py  pipe_predict_com --cfg $cfg  --nmax  $nmax  --save_kbatch 50  --past_days -2  --only_partner 1  --mode 2  &


         echo2 "###### Infer cat level"

               python src/cats.py pipe_predict_Li_cat   --cfg $cfg  --nmax  $nmax   --catin "L0_catnews"   --catout  L1_cat

               python src/cats.py pipe_predict_Li_cat   --cfg $cfg  --nmax  $nmax   --catin "L1_cat"       --catout  L2_cat

               python src/cats.py pipe_predict_Li_cat   --cfg $cfg  --nmax  $nmax   --catin L2_cat         --catout  L3_cat


               ###### Need transformers :   4.42.3  tokeinizer 0.19
               python src/cats.py pipe_predict_Li_cat   --cfg $cfg  --nmax  $nmax  --catin L3_cat          --catout  L4_cat     

              

         echo2 "###### Merge All"

               python src/cats.py  pipe_merge_final --cfg $cfg  --nmax  $nmax --past_days "-3"



         #######    Waiting all processes to finish   
         while true; do
            if ! pgrep -x "python" > /dev/null; then
               echo2 "No Python processes found. Exiting."
               break
            fi

            echo2 "Waiting for Python processes to finish..."
            #echo2 $(pgrep -x "python")
            sleep 300
         done



        # clean_tempfs &  



# done ;




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


echo2  $LINE_END  2>&1 | tee  -a "${LOGFILE}"






