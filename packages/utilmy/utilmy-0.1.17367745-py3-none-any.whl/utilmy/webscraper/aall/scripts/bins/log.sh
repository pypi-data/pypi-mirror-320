#!/bin/bash
## Usage      base ,   base_1 ,  logging_info  , logging_debug 
logmode="$1"
if [[ -z $1 ]]; then 
   logmode="base"
fi 


if [[ $logmode == 'base' ]]; then
    export log_verbosity=3
    export log_type="base"
    export log_config="log_level:INFO"
fi

if [[ $logmode == 'base_1' ]]; then
    export log_verbosity=1
    export log_type="base"
    export log_config="log_level:INFO"
fi


if [[ $logmode == 'logging_base' ]]; then
    export log_verbosity=3
    # export log_config="log_level:DEBUG;log_file:ztmp/log/log;rotate_time:s;rotate_interval:30"
    export log_type="base"
    export log_config="log_level:DEBUG"
    # export log_format=""
fi

if [[ $logmode == 'logging_debug' ]]; then
    export log_verbosity=10
    # export log_config="log_level:DEBUG;log_file:ztmp/log/log;rotate_time:s;rotate_interval:30"
    export log_type="base"
    export log_config="log_level:DEBUG"
    # export log_format=""
fi


if [[ $logmode == 'logging_info' ]]; then
    export log_verbosity=3
    # export log_config="log_level:DEBUG;log_file:ztmp/log/log;rotate_time:s;rotate_interval:30"
    export log_type="logging"
    export log_config="log_level:INFO"
    # export log_format=""
fi

if [[ $logmode == 'logging_info_1' ]]; then
    export log_verbosity=1
    # export log_config="log_level:DEBUG;log_file:ztmp/log/log;rotate_time:s;rotate_interval:30"
    export log_type="logging"
    export log_config="log_level:INFO"
    # export log_format=""
fi

if [[ $logmode == 'logging_info_2' ]]; then
    export log_verbosity=2
    # export log_config="log_level:DEBUG;log_file:ztmp/log/log;rotate_time:s;rotate_interval:30"
    export log_type="logging"
    export log_config="log_level:INFO"
    # export log_format=""
fi

if [[ $logmode == 'logging_info_3' ]]; then
    export log_verbosity=3
    # export log_config="log_level:DEBUG;log_file:ztmp/log/log;rotate_time:s;rotate_interval:30"
    export log_type="logging"
    export log_config="log_level:INFO"
    # export log_format=""
fi

echo "log_type: $log_type "
# exit 



