""" Data input processing
Docs::


"""
import warnings
warnings.simplefilter(action='ignore')
import os, sys, time, traceback,copy, gc
from copy import deepcopy
from typing import Any, Callable, Sequence, Dict, List, Optional, Union

import fire, boto3, pandas as pd, numpy as np
from box import Box
import awswrangler as wr
from sqlalchemy import create_engine
# import quadkey
# from pyquadkey2 import quadkey as quadkey2

##########################################
from src.utils.utilmy_base import (load_function_uri, date_now, pd_to_file, pd_read_file,
hash_int32, log_pd, to_int, json_load, json_save,
glob_glob, diskcache_decorator)

from src.utils.utilmy_config import config_load
from src.utils.utilmy_log import log, log2, logw, loge, log3
from src.utils.utilmy_aws import (aws_get_session, s3_pd_read_json2, s3_sync_tolocal, s3_path_norm,
                                  pd_read_file_s3, glob_glob_s3, pd_to_file_s3, os_copy_s3
                                  )




from sqlalchemy import create_engine
from sshtunnel import SSHTunnelForwarder
import pymysql
import os
from sqlalchemy import create_engine
from sshtunnel import SSHTunnelForwarder
import pymysql

import os
from sqlalchemy import create_engine
from sshtunnel import SSHTunnelForwarder
import pymysql
import pandas as pd


def test1():
    # Fetch credentials from environment variables
    bastion_host = os.environ.get('BASTION_HOST')
    bastion_user = os.environ.get('BASTION_USER')
    bastion_private_key = os.environ.get('BASTION_PRIVATE_KEY')

    rds_host = os.environ.get('RDS_HOST')
    rds_port = int(os.environ.get('RDS_PORT', 3306))
    rds_user = os.environ.get('RDS_USER')
    rds_password = os.environ.get('RDS_PASSWORD')
    rds_db = os.environ.get('RDS_DB')

    # Create the SSH tunnel
    tunnel = SSHTunnelForwarder(
        (bastion_host),
        ssh_username=bastion_user,
        ssh_pkey=bastion_private_key,
        remote_bind_address=(rds_host, rds_port)
    )

    # Start the tunnel
    tunnel.start()

    try:
        conn_str = f'mysql+pymysql://{rds_user}:{rds_password}@127.0.0.1:{tunnel.local_bind_port}/{rds_db}'
        engine = create_engine(conn_str)
        
        # Example pandas read_sql query
        query = "SELECT * FROM your_table LIMIT 5"
        df = pd.read_sql(query, engine)
        
        print(df)

    finally:
        # Make sure to stop the tunnel
        tunnel.stop()

            
            
            


###################################################################################################
if __name__ == "__main__":
    fire.Fire()




























