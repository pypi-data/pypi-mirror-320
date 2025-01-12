# -*- coding: utf-8 -*-
import warnings
warnings.filterwarnings("ignore")


import pandas
import numpy
import torch
import polars

import time, os, sys, pkgutil
import pandas as pd, numpy as np
from goose3 import Goose
from typing import Tuple
import requests
from bs4 import BeautifulSoup



from src.utils.utilmy_aws import (
  pd_to_file_s3,
  pd_read_file_s3, pd_read_file_s3_glob, pd_read_file_s3list,
  glob_glob_s3, glob_filter_dirlevel, glob_filter_filedate
)



from utilmy import (
   pd_read_file, pd_to_file,
   glob_glob, os_makedirs, log, log2, loge,
   date_now, 
)


from typing import Any, Callable, Sequence, Dict, List, Optional, Union
from copy import deepcopy
from collections import Counter
import fire, boto3, pandas as pd, numpy as np, time
from utilmy import (log, log_error, log_trace, logw, log2)

import time, json, re, os, pandas as pd, numpy as np, copy
from dataclasses import dataclass
from typing import Optional, Union
from box import Box

import datasets
from datasets import load_dataset, Dataset, load_metric
import evaluate

from transformers import (
    BitsAndBytesConfig,
    GenerationConfig,
    HfArgumentParser,
    TrainingArguments,
    Trainer,

    ###
    DataCollatorWithPadding,
    AutoTokenizer,

    ### Tokenizer / Sequence
    AutoModelForMultipleChoice,
    AutoModelForSemanticSegmentation,
    AutoModelForSequenceClassification,

    ### LLM
    AutoModelForCausalLM,
    PhiForCausalLM, DebertaForSequenceClassification,

)
# from transformers.models.qwen2.modeling_qwen2 import
from transformers.tokenization_utils_base import PreTrainedTokenizerBase, PaddingStrategy
from seqeval.metrics import f1_score, precision_score, recall_score, classification_report
from sklearn.metrics import f1_score

import spacy, torch, dateparser
# from pylab import cm, matplotlib

from utilmy import (date_now, date_now, pd_to_file, log, pd_read_file, os_makedirs,
                    glob_glob, json_save, json_load, config_load,
                    dict_merge_into
                    )

from src.utils.utilmy_base import diskcache_decorator, log_pd
from src.engine.usea.utils.util_exp import (exp_create_exp_folder, exp_config_override,
        exp_get_filelist, torch_device)

from src.utilsnlp.utils_base import (pd_add_textid2, pd_add_textid,
                                        str_fuzzy_match)

from transformers import pipeline
from accelerate import Accelerator



from src.utils.utilmy_base import (diskcache_decorator, config_load )


from src.utils.utilmy_aws import ( glob_glob_s3, pd_read_file_s3, aws_get_session,
                                pd_read_file_s3list)



##### Testing plw
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://playwright.dev")
    print(page.title())
    browser.close()



####
from newsapi import NewsApiClient
from src.envs.vars import ne_key
    
from src.fetchers import zcheck
from src.fetcher_auto import zcheck

###
from src.cats import zcheck 




import os 
os.system("pip freeze")


if __name__ == "__main__":
    print("all imports ok")


