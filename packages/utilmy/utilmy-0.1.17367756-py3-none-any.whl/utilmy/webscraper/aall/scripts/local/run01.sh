#!/bin/bash

source "scripts/bins/utils.sh"
source "scripts/bins/env.sh"

########## LOGS ################################################
export LOGDIR="ztmp/log/"
mkdir -p $LOGDIR
export LOGFILE="${LOGDIR}/_log1.py"


########## LOGS ################################################
export log_verbosity=3
#export log_type="logging"
export log_type="base"
#export log_config="log_level:DEBUG;log_file:ztmp/log/log;rotate_time:midnight;rotate_interval:1"
export log_config="log_level:DEBUG;log_file:ztmp/log/log;rotate_time:s;rotate_interval:30"





###################################################################################
echo  -e "###Start\n" 2>&1 | tee  "${LOGFILE}"


###### Models
#python src/frame/mab_torch/tsampling.py  test1    2>&1 | tee -a "${LOGFILE}"
#echo -e  $LINE_SEP
#

#python src/frame/mab_torch/tsampling.py  test2   2>&1 | tee  -a "${LOGFILE}"
#echo -e  $LINE_SEP
#
#
#python src/frame/mab_torch/tsampling.py  test3   2>&1 | tee  -a "${LOGFILE}"
#echo -e  $LINE_SEP
#
#
#
#
#
#echo -e  $LINE_END
#echo "######  Driver Model"
# python test/driver.py test_driver_fun1         2>&1 | tee  -a "${LOGFILE}"
#
#
 python test/driver.py test_driver_fun2         2>&1 | tee  -a "${LOGFILE}"

#
# python test/driver.py test_driver_pipe1 --source_data simul        2>&1 | tee  -a "${LOGFILE}"




 python src/run.py run_batch  --config config/test/config.yaml     2>&1 | tee  -a "${LOGFILE}"



#
#
#
#
#echo -e  $LINE_END
#echo "######  Driver Model"
#
# python test/driver.py test_data1 --source_data test        2>&1 | tee  -a "${LOGFILE}"
#
# python test/driver.py test_data2 --source_data test        2>&1 | tee  -a "${LOGFILE}"
#
# python test/driver.py test_data3 --source_data test        2>&1 | tee  -a "${LOGFILE}"
#




echo -e $LINE_END  2>&1 | tee  -a "${LOGFILE}"




