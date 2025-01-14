if "######## import":
    import json, os, warnings, random, string
    warnings.filterwarnings("ignore")
    import pandas as pd, numpy as np
    from pydantic import BaseModel, Field
    from typing import List, Dict, Union, Tuple
    from copy import deepcopy
    from functools import lru_cache

    from utilmy import log, log2, pd_read_file, pd_to_file, json_save, date_now
    from utilmy import diskcache_load, diskcache_decorator
    from utilmy import json_load

    from rag.engine_tv import fusion_search
    from rag.engine_qd import QdrantClient
    from rag.engine_sql import dbsql_fetch_text_by_doc_ids
    from rag.engine_qd import EmbeddingModelSparse
    from rag.llm import LLM, llm_cleanup_gpt_jsonformat, promptRequest
    import pandas as pd
    from utilmy import log

    from utils.utilmy_aws import pd_to_file_s3
    from utils.utils_base import date_get



ppdict= { "01": """






"""

}


#################################################################
def test_searchrun(name="01"):
    from rag.rag_summ2 import search_run

    pp =ppdict[name]
    pp = [ pi.strip() for pi in pp.split("\n") ]
    pp = [ pi for pi in pp if len(pi)>5 and pi[0] != "#"   ]

    dirdata = "ztmp/"
    y,m,d,h,ts= date_get()
    dirout = dirdata + f"/tests/year={y}/month={y}/day={d}"

    res = []
    for pi in pp:
        log(pi)
        try:
           dd = search_run(query=pi)
        except Exception as e:
           dd= {'status': str(e) }

        res.append([ pi, json.dumps(dd)      ])

    res = pd.DataFrame(res, columns=['query', 'answer'])
    res['date'] = date_now(fmt="%Y-%m-%d")

    dirouti = dirout + f"/df_test_{name}_{ts}.parquet"
    pd_to_file_s3(res, dirouti)






#################################################################
def test_retrieval_keywords(name="01"):
    from rag.rag_summ2 import search_run

    pp = ppdict[name]
    pp = [pi.strip() for pi in pp.split("\n")]
    pp = [pi for pi in pp if len(pi) > 5 and pi[0] != "#"]

    dirdata = "ztmp/"
    y, m, d, h, ts = date_get()
    dirout = dirdata + f"/tests/year={y}/month={y}/day={d}"

    res = []
    for pi in pp:
        log(pi)
        try:
            dd = search_run(query=pi)
        except Exception as e:
            dd = {'status': str(e)}

        res.append([pi, json.dumps(dd)])

    res = pd.DataFrame(res, columns=['query', 'answer'])
    res['date'] = date_now(fmt="%Y-%m-%d")

    dirouti = dirout + f"/df_test_{name}_{ts}.parquet"
    pd_to_file_s3(res, dirouti)





