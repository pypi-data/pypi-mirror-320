# -*- coding: utf-8 -*-
"""
    #### Install
        pip install -r pip/py39_full.txt
        pip install tantivy fastembed ranx fastembed==0.2.6 loguru --no-deps


    #### ENV variables
       cd asearch
        export PYTHONPATH="$(pwd):$PYTHONPATH"
        export torch_device='cpu'

    #### Test
            python rag/engine_tv.py test_tantivy



    #### Dataset
        https://www.kaggle.com/datasets/gowrishankarp/newspaper-text-summarization-cnn-dailymail

        https://www.kaggle.com/datasets/gowrishankarp/newspaper-text-summarization-cnn-dailymail

        https://zenn.dev/kun432/scraps/1356729a3608d6

        https://huggingface.co/datasets/big_patent
        https://huggingface.co/datasets/ag_news


"""
import warnings
warnings.filterwarnings("ignore")
import os, pathlib, uuid, time, traceback, pandas as pd, numpy as np, torch, functools
from typing import Any, Callable, Dict, List, Optional, Sequence, Union
from box import Box  ## use dot notation as pseudo class

import tantivy
from fastembed import TextEmbedding
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForMaskedLM
from ranx import Qrels, Run, fuse

from utilmy import pd_read_file, os_makedirs, pd_to_file, date_now, glob_glob
from utilmy import log, log2, log3, log_error, log_warning


########## Local import
from rag.dataprep import (pd_fake_data, dataset_hf_to_parquet)
from rag.engine_qd import EmbeddingModel


######################################################################################
def test_all():
    ### python engine2.py test_all
    # test_fusion_search()
    pass



def test_fusion_search():
    """test function for fusion search"""

    from rag.engine_qd import QdrantClient, qdrant_sparse_search, qdrant_sparse_create_index
    # get results from qdrant sparse search
    dirtmp = "ztmp/df_test.parquet"
    test_df = pd_read_file(dirtmp)
    # pick random query from test dataframe
    query = test_df.sample(1)["text"].values[0]
    query = query.replace("\n", " ")

    server_url = ":memory:"
    # index in memory data for later retrieval
    client = QdrantClient(server_url)
    qdrant_sparse_create_index(dirin=dirtmp, client=client)
    v1_results = qdrant_sparse_search(query, client=client)
    v1 = fusion_postprocess_qdrant(v1_results)
    # collect ids from  results
    v1_ids = list(v1.keys())


    # get results from tantivy search
    v2_results = tantivy_search(query=query)
    v2 = fusion_postprocess_tantivy(v2_results)
    # collect ids from  results
    v2_ids = list(v2.keys())

    fusion_results = fusion_search(query=query, method="rrf", client=client)


    search_ids = set(v1_ids).union(v2_ids)
    fusion_ids = set(fusion_results["q1"].keys())
    # check if  ids from  two search results are  same as ids from fusion search
    # log(f"{search_ids.difference(fusion_ids)}")
    assert search_ids.difference(fusion_ids) == set()






###############################################################################
######## Fusion Rank ##########################################################
def fusion_search(query="the", engine: str = "", method="rrf", client=None,
                  sparse_collection_name="", dense_collection_name="", tantivy_datapath="", neo4j_db="",
                  sparse_model: EmbeddingModel = None, dense_model: EmbeddingModel = None,
                  query_tags=None, query_filter=None, topk=50,

                  ) -> Dict:
    """Perform a fusion search using  given query and method.
    Args:
        query (str):  query to search for.     : "the".
        engine (str): underscore separated engines to use.
        method (str):  method to use for merging  results.     : "rrf".

    Returns:
        Dict:  merged ranking results.

     Loose Coupling and Clear/Indentify coupling  between  code components.
     "id"  columns must in  dataframe

    """
    from rag.engine_qd import qdrant_sparse_search, qdrant_dense_search
    from rag.engine_kg import neo4j_search_docids

    engines = [en for en in engine.split("_") if en in ("dense", "sparse", "tantivy", "neo4j")]
    if not engines:
        engines = ("sparse", "tantivy")

    log('engines', engines)
    results = []
    for en in engines:
        log('Using:', en)
        if en == "sparse":
            v1_results = qdrant_sparse_search(query, client=client, collection_name=sparse_collection_name,
                                              model=sparse_model, query_tags= query_tags, query_filter=query_filter,
                                              topk=topk)
            result = fusion_postprocess_qdrant(v1_results, colid="text_id")
            results.append(result)

        elif en == "tantivy":
            v2_results = tantivy_search(query=query, datapath=tantivy_datapath)
            result = fusion_postprocess_tantivy(v2_results)
            results.append(result)

        elif en == "dense":
            v3_results = qdrant_dense_search(query=query, collection_name=dense_collection_name, model=dense_model)
            result = fusion_postprocess_qdrant(v3_results, colid="text_id")
            results.append(result)

        elif en == "neo4j":
            v4_results = neo4j_search_docids(query=query, db_name=neo4j_db)  # , db_name=neo4j_db)
            result = fusion_postprocess_neo4j(v4_results)
            results.append(result)

    # log(f"results:{results}")
    results = [res for res in results if len(res) > 0]
    if len(results) == 0:
        vmerge = {}
    elif len(results) == 1:
        vmerge = results[0]
    else:
        vmerge: Dict = ranx_merge_ranking(results, method=method)
    # log(f"vmerge: {vmerge}")
    return vmerge


def fusion_postprocess_qdrant(results: List, colid="id") -> Dict:
    """Postprocess  search results from a sparse qdrant search.
    Args:
        results (List):  search results.

    Returns: { doc_id: score }
    """
    v1 = {
        str(scored_point.payload[colid]): scored_point.score for scored_point in results
    }
    # log(f"v1:{v1}")
    return v1


def fusion_postprocess_tantivy(results: List, colid="id") -> Dict:
    """Postprocess  search results from a tantivy search.
    Args: results (List):  search results.

    Returns: { doc_id: score }
    """
    v2 = {str(doc.get_all(colid)[0]): score for score, doc in results}
    # log(f"v2:{v2}")
    return v2


def fusion_postprocess_neo4j(results: List, colid="text_id") -> Dict:
    """Postprocess  search results from a neo4j search.
    Args: results (List):  search results.

    Returns: { doc_id: score }
    """
    v4 = {str(doc[colid]): doc["score"] for doc in results}
    # log(f"v4:{v4}")
    return v4


def ranx_merge_ranking(vs: List, method="rrf") -> Dict:
    """Merge two rankings using  specified fusion method.

    Args:
        method (str):  fusion method to use.     : "rrf".
        v1 (Dict):  first ranking to merge.     : None.
        v2 (Dict):  second ranking to merge.     : None.

    Returns:Dict:  {'q1': {'d1': 0.5, 'd2': 0.8, 'd3': 0.3}}


    Example:
        >>> v1 = {"d1": 0.5, "d2": 0.8, "d3": 0.3}
        >>> v2 = {"d1": 0.9, "d2": 0.2, "d3": 0.7}
        >>> ranx_merge_ranking(vs=[v1,v2], method="rrf")
        {'q1': {'d1': 0.5, 'd2': 0.8, 'd3': 0.3}}
    """
    runs = [Run.from_dict({"q1": v}) for v in vs]
    # Fuse rankings using Reciprocal Rank Fusion (RRF)
    fused_run = fuse(runs, method=method)
    # log3(f"run1:{run1}")
    # log3(f"run2:{run2}")
    # log3(fused_run)
    fused_run: dict = dict(fused_run)

    #   {'q1': {'d1': 0.5, 'd2': 0.8, 'd3': 0.3}}
    return fused_run["q1"]






###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()




"""

    #### Benchmarks:
            sudo docker run -d -p 6333:6333     -v ~/.watchtower/qdrant_storage:/qdrant/storage:z     qdrant/qdrant
            alias py2="python rag/engine_tv.py "

            py2 bench_v1_create_indexes --dirdata_root ztmp/bench/
            py2 bench_v1_run  --dirout ztmp/bench/   --topk 5


            ### Bench
            tantivy : v1  6ms
            Sparse :      23ms
            Dense:        30 ms
            
            ag_news index timings:
            records: 127600
            dense stransformers vectors: 9m28s
            dense fastembed vectors:
            sparse vectors: 9819/12760


"""

