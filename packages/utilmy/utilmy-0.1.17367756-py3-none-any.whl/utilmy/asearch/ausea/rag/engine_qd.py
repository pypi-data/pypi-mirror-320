# -*- coding: utf-8 -*-
"""
    #### Install
        pip install -r py39.txt
        pip install fastembed==0.2.6 loguru --no-deps

    ### How to run qdrant from binary file

        # download latest tar.gz package file from here, Linux:
            wget -c https://github.com/qdrant/qdrant/releases/download/v1.9.0/qdrant-x86_64-unknown-linux-gnu.tar.gz

        # extract tar.gz package
            tar -xvf qdrant-x86_64-unknown-linux-gnu.tar.gz

        # run qdrant on separate shell.
            cd download_folder
            ./qdrant --config-path /absolute/path/to/config.yaml &

            # Config Where to store all  data
            storage_path: ./ztmp/qdrant/storage



    #### ENV variables
        export HF=
        export
        export torch_device='cpu'
        #### Test

            python  rag/engine_kg.py test_qdrant_dense
            python  rag/engine_kg.py test_qdrant_sparse


    #### Benchmarks:
            sudo docker run -d -p 6333:6333     -v ~/.watchtower/qdrant_storage:/qdrant/storage:z     qdrant/qdrant
            alias py2="python rag/engine_kg.py "

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


    #### Dataset
        https://www.kaggle.com/datasets/gowrishankarp/newspaper-text-summarization-cnn-dailymail


        https://www.kaggle.com/datasets/gowrishankarp/newspaper-text-summarization-cnn-dailymail

        https://zenn.dev/kun432/scraps/1356729a3608d6


        https://huggingface.co/datasets/big_patent


        https://huggingface.co/datasets/ag_news


    #### Flow
        HFace Or Kaggle --> dataset in RAM--> parquet (ie same columns)  -->  parquet new columns (final)


        Custom per text data
        title  :   text
        text   :    text
        cat1   :    string   fiction / sport /  politics
        cat2   :    string     important / no-important
        cat3   :    string
        cat4   :    string
        cat5   :    string
        dt_ymd :    int     20240311


"""
import warnings
warnings.filterwarnings("ignore")
import os, pathlib, uuid, time, traceback, pandas as pd, numpy as np, torch
from typing import Any, Callable, Dict, List, Optional, Sequence, Union
from box import Box  ## use dot notation as pseudo class


from qdrant_client import QdrantClient, models
from qdrant_client.http.models import PointStruct

from fastembed import TextEmbedding
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForMaskedLM

from utilmy import (pd_read_file, os_makedirs, pd_to_file, date_now, glob_glob)
from utilmy import log, log2

########## Local import
from rag.dataprep import (pd_fake_data, )



######################################################################################
def test_all():
    ### python engine2.py test_all
    test_qdrant_dense()
    test_qdrant_sparse()


def test_qdrant_dense(nrows=20):
    """
    python rag/engine_kg.py test_qdrant_dense_create_index    
    """
    dirtmp = "ztmp/df_test.parquet"
    test_df = pd_fake_data(nrows=nrows, dirout=dirtmp, overwrite=False)

    model_type = "stransformers"
    model_id = "sentence-transformers/all-MiniLM-L6-v2"
    server_url = ":memory:"  ### "http://localhost:6333"
    collection_name = "my-documents"

    client = QdrantClient(server_url)

    qdrant_dense_create_index(
        dirin=dirtmp,
        server_url=server_url,
        collection_name=collection_name,
        coltext="text",
        model_id=model_id,
        model_type=model_type,
        client=client
    )
    model = EmbeddingModel(model_id, model_type)

    # pick random query from test dataframe
    query = test_df.sample(1)["text"].values[0]
    results = qdrant_dense_search(
        query,
        server_url=server_url,
        collection_name=collection_name,
        model=model,
        client=client
        # category_filter={"categories": "Fiction"},
    )
    results = [
        ((scored_point.payload), scored_point.score)
        for scored_point in results
        if scored_point.score > 0
    ]
    log(f"len(results):{len(results)}")
    assert len(results) > 0


def test_qdrant_sparse(nrows=30):
    """test function for sparse qdrant indexing"""
    dirtmp = "ztmp/df_test.parquet"
    test_df = pd_fake_data(nrows=nrows, dirout=dirtmp, overwrite=False)

    model_id = "naver/efficient-splade-VI-BT-large-doc"
    model_type = "stransformers"
    server_url = ":memory:"  ### "http://localhost:6333"
    collection_name = "my-documents"

    client = QdrantClient(server_url)

    qdrant_sparse_create_index(
        dirin=dirtmp,
        collection_name="my-sparse-documents",
        model_id=model_id,
        client=client
    )
    # pick random query from test dataframe
    query = test_df.sample(1)["text"].values[0]

    model = EmbeddingModelSparse(model_id)
    results = qdrant_sparse_search(
        query,
        # category_filter={"categories": "Fiction"},
        collection_name="my-sparse-documents",
        model=model,
        client=client
    )

    results = [
        ((scored_point.payload), scored_point.score)
        for scored_point in results
        if scored_point.score > 0
    ]
    # print(results)
    log(f"len(results):{len(results)}")
    assert len(results) > 0




#####################################################################################
########## Dense Vector creation
class EmbeddingModel:
    def __init__(self, model_id, model_type, device: str = "", embed_size: int = 128):
        self.model_id = model_id
        self.model_type = model_type

        from utilsr.utils_base import torch_getdevice
        self.device = torch_getdevice(device)

        if model_type == "stransformers":
            self.model = SentenceTransformer(model_id, device=self.device)
            self.model_size = self.model.get_sentence_embedding_dimension()

        elif model_type == "fastembed":
            self.model = TextEmbedding(model_name=model_id, max_length=embed_size)
            self.model_size = self.model.get_embedding_size()

        else:
            raise ValueError(f"Invalid model type: {model_type}")

    def embed(self, texts: List):
        if self.model_type == "stransformers":
            vectors = list(self.model.encode(texts))
        elif self.model_type == "fastembed":
            vectors = list(self.model.embed(texts))
        return vectors


class EmbeddingModelSparse:
    def __init__(self, model_id: str = "naver/efficient-splade-VI-BT-large-doc", max_length: int = 512):
        """ 

         ### Very fast
         "naver/efficient-splade-VI-BT-large-doc"


         ### New one
           https://huggingface.co/naver/splade-v3-lexical
 
           https://huggingface.co/naver/splade-v3

           https://goatstack.ai/topics/splade-v3-advanced-sparse-lexical-model-njcywz
                 
                 lexical is best

                SPLADE-v3-DistilBERT8
                , which instead starts training from DistilBERT – and thus has a
                smaller inference “footprint”.
                2. SPLADE-v3-Lexical9
                , for which we remove query expansion, thus reducing the retrieval
                FLOPS (and improving efficiency) [6].
                3. SPLADE-v3-Doc10, which starts training from CoCondenser, and where no computation is
                done for the query – which can be seen as a simple binary Bag-of-Words [4, 6].

                6
                cross-encoder/ms-marco-MiniLM-L-6-v2 7
                naver/trecdl22-crossencoder-debertav3
                8
                naver/splade-v3-distilbert 9
                naver/splade-v3-lexical 10 naver/splade-v3-doc



        """
        ### best/speed in 2024
        #model_id ="naver/splade-v3-lexical" 
        model_id =  "naver/efficient-splade-VI-BT-large-doc"

        # Initialize tokenizer and model
        from utilsr.utils_base import torch_getdevice
        self.device = torch_getdevice()
        self.max_length = max_length
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForMaskedLM.from_pretrained(
            model_id, device_map=self.device
        )

    def embed(self, texts):
        # Tokenize all texts
        if isinstance(texts, np.ndarray):
            # convert to list
            texts = texts.tolist()
        tokens_batch = self.tokenizer(
            texts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=self.max_length,
        )
        # Forward pass through  model
        tokens_batch.to(device=self.device)
        with torch.no_grad():
            output = self.model(**tokens_batch)

        # Extract logits and attention mask
        logits = output.logits
        attention_mask = tokens_batch["attention_mask"]

        # ReLU and weighting
        relu_log = torch.log(1 + torch.relu(logits))
        weighted_log = relu_log * attention_mask.unsqueeze(-1)

        # Compute max values
        max_vals, _ = torch.max(weighted_log, dim=1)
        # log(f"max_vals.shape: {max_vals.shape}")

        # for each tensor in  batch, get  indices of  non-zero elements
        indices_list = [torch.nonzero(tensor, as_tuple=False) for tensor in max_vals]
        indices_list = [
            indices.cpu().numpy().flatten().tolist() for indices in indices_list
        ]
        # for each tensor in  batch, get  values of  non-zero elements
        values = [
            max_vals[i][indices].cpu().numpy().tolist()
            for i, indices in enumerate(indices_list)
        ]

        return list(zip(indices_list, values))

    def decode_embedding(self, cols: list, weights) -> dict:
        """Decodes embedding from indices and values."""
        # Map indices to tokens and create a dictionary
        idx2token = {idx: token for token, idx in self.tokenizer.get_vocab().items()}
        token_weight_dict = {
            idx2token[idx]: round(weight, 2) for idx, weight in zip(cols, weights)
        }

        # Sort  dictionary by weights in descending order
        sorted_token_weight_dict = {
            k: v
            for k, v in sorted(
                token_weight_dict.items(), key=lambda item: item[1], reverse=True
            )
        }

        return sorted_token_weight_dict



#####################################################################################
########## Qdrant Dense Vector Indexing
def qdrant_collection_exists(qclient, collection_name):
    collections = qclient.get_collections()
    collections = {coll.name for coll in collections.collections}
    return collection_name in collections


def qdrant_dense_create_collection(
        qclient, collection_name="documents", size: int = None
):
    """
    Create a collection in qdrant
    :param qclient: qdrant client
    :param collection_name: name of  collection
    :param size: size of  vector
    :return: collection_name
    """
    if not qdrant_collection_exists(qclient, collection_name):
        qclient.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=size, distance=models.Distance.COSINE
            ),
        )
        log(f"created collection:{collection_name}")
    return collection_name


def qdrant_dense_index_documents(
        qclient,
        collection_name: str,
        df: pd.DataFrame,
        colscat: List = None,  ## list of categories field
) -> None:
    """Indexes documents from a pandas DataFrame into a qdrant collection.
    Args:
        qclient:  qdrant client.
        collection_name:  name of  collection.
        df:  DataFrame containing  documents.
        colscat: list of fields to be indexed

    """
    colscat = (
        [ci for ci in df.columns if ci not in ["vector"]]
        if colscat is None
        else colscat
    )

    assert df[["text_id", "vector"]].shape
    # log(df)

    # Convert documents to points for insertion into qdrant.
    points = [
        PointStruct(
            id=row["text_id"],  # Use existing id if available, else generate new one.
            vector=row["vector"].tolist(),  # Numpy ---> List, Vector of  document.
            payload={ci: row[ci] for ci in colscat},  ### Category filtering values
        )
        for i, row in df.iterrows()
    ]

    vector_size = len(points[0].vector)  # Get  size of  vectors.

    # Create collection if not existing.
    qdrant_dense_create_collection(
        qclient, collection_name=collection_name, size=vector_size)

    # Index documents.
    qclient.upsert(collection_name=collection_name, points=points)
    log("qdrant upsert done: ", collection_name, qclient.count(collection_name), )


def qdrant_dense_create_index(
        dirin: str,
        server_url: str = ":memory:",
        collection_name: str = "my-documents",
        colscat: List = None,  ## list of categories field
        coltext: str = "text",
        model_id=None,
        model_type=None,
        batch_size=100,
        client=None
) -> None:
    """Create a qdrant index from a parquet file.

    dirin: str: path to  parquet file
    server_url: str: url path to  qdrant server
    coltext: str: column name of  text column
    model_id: str: name of  embedding model to use
    model_type: str: type of  embedding model
    batch_size: int: batch size for embedding vectors
    (ID_k, text_k)

    """
    # df = pd_read_file(path_glob=dirin, verbose=True)
    flist = glob_glob(dirin)
    log("Nfiles: ", len(flist))

    ##### Load model
    model = EmbeddingModel(model_id, model_type)
    client = QdrantClient(server_url) if client is None else client
    qdrant_dense_create_collection(client, collection_name, size=model.model_size)
    for i, fi in enumerate(flist):
        dfi = pd_read_file(fi)

        ### Create embedding vectors batchwise
        kmax = int(len(dfi) // batch_size) + 1
        for k in range(0, kmax):
            dfk = dfi.iloc[k * batch_size: (k + 1) * batch_size, :]
            if len(dfk) <= 0:
                break
            # get document vectors
            dfk["vector"] = model.embed(dfk[coltext].values)

            # insert documents into qdrant
            assert dfk[["text_id", "vector"]].shape
            qdrant_dense_index_documents(
                client, collection_name, colscat=colscat, df=dfk
            )


def embed_create_dense(
        dirin: str,
        colscat: List = None,  ## list of categories field
        coltext: str = "text",
        model_id="snowflake/snowflake-arctic-embed-m",
        model_type="fastembed",
        batch_size=100,
        dirout="ztmp/data/emb/",
        tag="v1",
        add_date=1
) -> None:
    """Create embedding from parquet file.
       https://qdrant.github.io/fastembed/examples/Supported_Models/
       https://huggingface.co/spaces/mteb/leaderboard


       modeltype='fastembed'
       modelid="snowflake/snowflake-arctic-embed-m"    ### 768

       modeltype='fastembed'
       modelid="thenlper/gte-large"



    """
    # df = pd_read_file(path_glob=dirin, verbose=True)
    flist = glob_glob(dirin)
    log("Nfiles: ", len(flist))
    y,m,d,h= date_now("%y-%m-%d-%H").split("-")
    dirout1 = dirout + "/" + tag
    if add_date==1:
        dirout1 = dirout1 + f"/year={y}/month={m}/day={d}/"

    ##### Load model
    model = EmbeddingModel(model_id, model_type)
    for i, fi in enumerate(flist):
        dfi = pd_read_file(fi)

        ### Create embedding vectors batchwise
        dfa  = pd.DataFrame()
        kmax = int(len(dfi) // batch_size) + 1
        for k in range(0, kmax):
            dfk = dfi.iloc[k * batch_size: (k + 1) * batch_size, :]
            if len(dfk) <= 0: break

            dfk["emb"] = model.embed(dfk[coltext].values)
            dfa = pd.concat((dfa, dfk))
            log(dfa.shape)
     
        pd_to_file(df, dirout + f"/dfemb_{i}_{len(dfemb)}.parquet")





def qdrant_dense_search(query,
                        topk: int = 20,
                        category_filter: dict = None,
                        server_url: str = "",
                        collection_name: str = "my-documents",
                        model: EmbeddingModel = None,
                        client=None,
                        model_type_default="stransformers",
                        model_id_default="sentence-transformers/all-MiniLM-L6-v2"  ### 384,  50 Mb
                        ) -> List:
    """
    Search a qdrant index
    query: str: query to search
    server_url: str: url path to  qdrant server
    collection_name: str: name of  collection to search
    model_id: str: name of  embedding model to use

    Main issue with Category iS :

       How do we know the category in advance ?
          1)  User provide them.
          2)  We can guess easily by simple rules.
          3)  Train a BERT model to category the query.
          4)  New Qdrant way : Self Learning : using LLM to get the categories
          
              Category : Hard Filtering.            
              Embedding: soft fitlering ()

            
              3 query similarity query : retrieval, you dont missg
                  Cat News A, one with Cat News B, one with Cat news C   

               Final results: 30% of A, 30% of B, 30% of C
               
          Async launch of comppute; 
          
          wait      

        # query filter
        hits = client.search(
            collection_name="wine_reviews",
            query_vector=encoder.encode("Night Sky").tolist(),
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(key="metadata.country", match=models.MatchValue(value="US")),
                    models.FieldCondition(key="metadata.price", range=models.Range(gte=15.0, lte=30.0)),
                    models.FieldCondition(key="metadata.points", range=models.Range(gte=90, lte=100))
                ]
            ),
            limit=3,
        )

        for hit in hits:
            print(hit.payload['metadata']['title'], "\nprice:", hit.payload['metadata']['price'], "\npoints:", hit.payload['metadata']['points'], "\n\n")


            Schema
                 title, text ,  cat1, cat2, cat2
                  ("cat2name" : "myval"  )

    """
    if server_url == "":
        server_url = os.environ.get("QDRANT_URL", ":memory:")

    client = QdrantClient(server_url) if client is None else client

    model = EmbeddingModel(model_id_default, model_type_default) if model is None else model
    query_vector: list = model.embed([query])
    query_filter = qdrant_query_createfilter(category_filter)

    # log(client.count(collection_name))
    result: list = client.search(
        collection_name=collection_name,
        query_vector=query_vector[0],
        query_filter=query_filter,
        limit=topk
    )
    # log([scored_point.payload["categories"] for scored_point in search_result])
    # log(f"#search_results:{len(search_result)}")
    return result


def qdrant_query_createfilter(
        category_filter: Dict = None,
) -> Union[None, models.Filter]:
    """Create a query filter for Qdrant based on  given category filter.
    Args:
        category_filter (Dict[str, Any]): A dictionary representing  category filter.     : None.

    Returns:
        Union[None, models.Filter]:  query filter created based on  category filter, or None if  category filter is None.

    query_filter=models.Filter(
        must=[
            models.FieldCondition(
                key="category",
                match=models.MatchText(text="elec")
            )
        ]
    ),


    """
    if category_filter is None:
        return None

    catfilter = []
    for catname, catval in category_filter.items():
        xi = models.FieldCondition(key   = catname,
                                   match = models.MatchText(value=catval))
        catfilter.append(xi)
    query_filter = models.Filter(should=catfilter)
    return query_filter









###########################################################################################################
######### Qdrant Sparse Vector Engine :
def qdrant_sparse_create_collection(
        qclient=None, server_url: str = ":memory:", collection_name="documents", size: int = None
):
    """Create a collection in qdrant
    :param qclient: qdrant client
    :param collection_name: name of  collection
    :param size: size of  vector
    :return: collection_name
    """
    if qclient is None:
        qclient = QdrantClient(server_url)

    if not qdrant_collection_exists(qclient, collection_name):
        vectors_cfg = {}  # left blank in case of sparse indexing
        sparse_vectors_cfg = {
            "text": models.SparseVectorParams(
                index=models.SparseIndexParams(
                    on_disk=True,
                )
            )
        }
        qclient.create_collection(
            collection_name=collection_name,
            vectors_config=vectors_cfg,
            sparse_vectors_config=sparse_vectors_cfg,
        )
        log(f"created sparse collection:{collection_name}")
    return collection_name


def qdrant_update_payload_indexes(qclient=None, server_url: str = ":memory:",
                                  collection_name="my-test-collection", payload_settings: dict=None):
    for field_name, field_schema in payload_settings.items():
        # keyword - for keyword payload, affects Match filtering conditions.
        # integer - for integer payload, affects Match and Range filtering conditions.
        # float - for float payload, affects Range filtering conditions.
        # bool - for bool payload, affects Match filtering conditions (available as of v1.4.0).
        # geo - for geo payload, affects Geo Bounding Box and Geo Radius filtering conditions.
        # datetime - for datetime payload, affects Range filtering conditions (available as of v1.8.0).
        # text
        if qclient is None:
            qclient = QdrantClient(server_url)
        assert field_schema in ["keyword", "integer", "float", "bool", "geo", "datetime", "text"]
        if field_schema=="text":
            qclient.create_payload_index(
                collection_name=f"{collection_name}",
                field_name=f"{field_name}",
                field_schema=models.TextIndexParams(
                    type="text",
                    tokenizer=models.TokenizerType.WORD,
                    min_token_len=2,
                    max_token_len=15,
                    lowercase=True,
                ),
            )
        else:
            qclient.create_payload_index(
                collection_name=f"{collection_name}",
                field_name=f"{field_name}",
                field_schema=f"{field_schema}",
            )


def qdrant_sparse_index_documents(
        qclient, collection_name, df: pd.DataFrame, colscat: list = None
):
    # covert documents to points for insertion into qdrant

    colscat = (
        [ci for ci in df.columns if ci not in ["vector"]]
        if colscat is None
        else colscat
    )
    points = [
        models.PointStruct(
            id=doc["text_id"],
            payload={key: doc[key] for key in colscat},
            # Add any additional payload if necessary
            vector={
                "text": models.SparseVector(indices=doc.vector[0], values=doc.vector[1])
            },
        )
        for i, doc in df.iterrows()
    ]
    # Create collection if not existing
    # qdrant_sparse_create_collection(qclient, collection_name=collection_name)
    # Index documents

    try:
        qclient.upsert(collection_name=collection_name, points=points)
    except Exception as err:
        print(traceback.format_exc())


    ###### Asyncrhonous mini-batch
    # def worker(points):
    #      try:
    #          qclient.upsert(collection_name=collection_name, points=points)
    #      except Exception as err:
    #          print(traceback.format_exc())


    # points_all = []
    # n = len(df)
    # for i in range(0, len(df)):
    #     pi =  models.PointStruct(
    #         id=doc["text_id"],
    #         payload={key: doc[key] for key in colscat},
    #         # Add any additional payload if necessary
    #         vector={
    #             "text": models.SparseVector(indices=doc.vector[0], values=doc.vector[1])
    #         },
    #     )
    #     points_batch.append(  pi )
    #     if len(points_batch) < 16 != 0 or i < n-1 : continue
    #     points_all.append(point_batch)


    # from concurrent.futures import ThreadPoolExecutor as mp
    # with mp(max_workers=npool) as executor:
    #         # Submit all the tasks to the executor
    #         futures = [executor.submit(worker, row, **kwargs) for points_batch in points_all ]


    # ##### Collect the results as they become available
    # results = []
    # for future in futures:
    #     results.append(future.result())
    # return results


def qdrant_sparse_create_index(
        dirin: str,
        server_url: str = ":memory:",
        collection_name: str = "my-sparse-documents",
        colscat: list = None,
        coltext: str = "text",
        model_id: str = "naver/efficient-splade-VI-BT-large-doc",
        batch_size: int = 5,
        max_words: int = 256,
        client=None,
        imin=0,
        imax=10000000,
) -> None:
    """
    Create a qdrant sparse index from a parquet file
    dirin: str: path to  parquet file
    server_url: str: url path to  qdrant server
    coltext: str: column name of  text column
    model_id: str: name of  sparse embedding model to use
    """
    flist = glob_glob(dirin)
    log("Nfiles: ", len(flist))

    if isinstance(colscat, str):
        colscat = [ str(x).strip() for x in colscat.split(",") ]

    colscat = [ str(x).strip().replace("[","").replace("]","") for x in colscat ]
    cols    = list(colscat) + [coltext]
    log("cols", cols)    

    log("###### qdrant: Load model  ###############################")    
    model = EmbeddingModelSparse(model_id)
    client = QdrantClient(server_url) if client is None else client
    qdrant_sparse_create_collection(client, collection_name)


    log("###### qdrant: start embed+insert ########################")    
    for i, fi in enumerate(flist):
        log(i, fi)
        dfi = pd_read_file(fi)
        log(dfi[cols].shape)
        dfi = dfi.fillna("")
        dfi = dfi[ dfi[coltext].apply(lambda x: len(str(x)) > 10) ]
        log('dfi.dropna', dfi.shape)

        #dfi = dfi.dropna(subset= colscat +[coltext] )
        dfi = dfi.iloc[imin:imax,:]
        log(dfi, dfi.shape)

        ### Create embedding vectors batchwise
        nall = 0
        kmax = int(len(dfi) // batch_size) + 1
        for k in range(0, kmax):
            dfk = dfi.iloc[k * batch_size: (k + 1) * batch_size, :]
            if len(dfk) <= 0:
                break

            if max_words > 0:
                dfk[coltext] = dfk[coltext].apply(lambda x: " ".join(x.split()[:max_words]))
            dfk["vector"] = model.embed(dfk[coltext].to_list())

            # insert documents into qdrant
            log(k, dfk[["text_id", "vector"]].shape, nall)
            qdrant_sparse_index_documents(client, collection_name, colscat=colscat, df=dfk)
            nall += len(dfk)
        log("All inserted:", nall)    




##########################################################################################################
def pd_parallel_apply(df, myfunc, colout="llm_json", npool=4, ptype="process", **kwargs):
    """Apply a function to each row of a DataFrame using multithreading.
            Parameters:
            - df (pandas.DataFrame): The DataFrame on which to apply the function.
            - func (function): The function to apply to each row.
            - colout (str): The name of the column in which to store the results.
            - n_threads (int): Number of threads to use for parallel execution.

            Returns:
            - pandas.DataFrame: DataFrame with the results of the applied function as a new column.
    """
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")

    # Define a wrapper function to handle thread-safe operations
    def worker(row, **kwargs):
        return myfunc(row, **kwargs)

    results = []

    if ptype =="process":
         log('Using processes:', npool)
         from concurrent.futures import ProcessPoolExecutor as mp
         with mp(max_workers=npool) as executor:
                # Submit all the tasks to the executor
                futures = [executor.submit( myfunc, row, **kwargs) for _, row in df.iterrows()]


    else:
         log('Using threads:', npool)
         from concurrent.futures import ThreadPoolExecutor as mp
         with mp(max_workers=npool) as executor:
                # Submit all the tasks to the executor
                futures = [executor.submit(worker, row, **kwargs) for _, row in df.iterrows()]

    # Collect the results as they become available
    for future in futures:
        results.append(future.result())

    df[colout] = results
    return df






##########################################################################################################
def qdrant_query_createfilter_custom(query_tags:Dict):
    """
      query_tags ---> Map to Qdrant categories field
          --> query_tags ={

        tasks : ['Summarize']

        companies_name :  ['Microsoft'],
        industry_tags:    ['Generative AI', "Cloud" ],
        date_period:      ['2024'],
        context :         ['acquisition'], #### All others

        Mapping:
            task           -->  prompts-prompt_summarize (Pick up correct Prompt for the task we want).

            company_names  -->  qdrant-com_extract
            industry_tags  -->  qdrant-Lcat
            period         -->  qdrant-period
            relation       -->  qdrant-L0_catnews   text category
        }

         Qdrant columns:
              L_cat = L1_cat + L2_cat + L3_cat + L4_cat
              "['L0_catnews', 'com_extract',   'Lcat, 'text_id', 'title']"




    query_filter=Filter(
        should=[
            FieldCondition(key="category", match=MatchValue(value="electronics")),
            FieldCondition(key="brand", match=MatchValue(value="apple"))
        ]

    query_filter=models.Filter(
        must=[
            models.FieldCondition(
                key="category",
                match=models.MatchText(text="elec")
            )
        ]

    reasoning:     str = Field(description=" Summarize in 2 sentences your reasoning on this entity extraction.")

    task:          list = Field(description="predefined tasks like \"describe\", \"summarize\", \"summarize_with_citations\" \"unknown\"    )")

    date_period:   str  = Field(description="before/between/after/in")
    date:          str  = Field(description="Date: year and month information in the text")

    company_names: list = Field(description="Name of the corporate entities")
    industry_tags: list = Field(description="Industry/Company tags")

    relation_tags: list = Field(description="relations mentioned in the text")

    context:       list = Field(description="keywords that didnt get categorized anywhere else")



    """
    from qdrant_client.models import Filter, FieldCondition, MatchValue

    should = []
    must   = []
    for key, valist in query_tags.items():
        if key == "company_names":
            for val in valist:
               should.append(
                     FieldCondition(key="com_name", match=models.MatchText(text=val ) ) )

        if key == "industry_tags":
            for val in valist:
                should.append(
                    FieldCondition(key="L_cat", match=models.MatchText(text=val)))

        if key == "period":
            should.append(
                FieldCondition(key="period", match=models.MatchText(text=val)))

        if key == "activity":
            should.append(
                FieldCondition(key="activity", match=models.MatchText(text=val)))

        if key == "context":
            should.append(
                FieldCondition(key="context", match=models.MatchText(text=val)))

    query_filter = models.Filter(must=must, should=should)
    return query_filter




def qdrant_sparse_search(query: str,
                         category_filter: dict = None,
                         server_url: str = "",
                         collection_name: str = "my-sparse-documents",
                         model: EmbeddingModelSparse = None,
                         model_id_default: str = "naver/efficient-splade-VI-BT-large-doc",
                         topk: int = 10,
                         client=None,
                         query_tags=None,
                         query_filter=None,
                         ) -> List:
    """Search a qdrant index
        query: str: query to search
        server_url: str: url path to  qdrant server
        collection_name: str: name of  collection to search
        model_id: str: name of  embedding model to use

    """
    if server_url == "":
        server_url = os.environ.get("QDRANT_URL", ":memory:")

    client = QdrantClient(server_url) if client is None else client
    model  = EmbeddingModelSparse(model_id_default) if model is None else model
    result = model.embed([query])
    query_indices, query_values = result[0]

    query_dict = model.decode_embedding(query_indices, query_values)
    # log(f"query_dict:{query_dict}")

    if query_filter is None:
        if query_tags is not None:
           query_filter = qdrant_query_createfilter_custom(query_tags)
           # query_filter    = qdrant_query_createfilter(category_filter= category_filter)
           # pass

    query_vector = models.NamedSparseVector(name="text",
                                            vector=models.SparseVector(indices=query_indices, values=query_values, ),
                                            )

    # Searching for similar documents
    search_results: List = client.search(collection_name=collection_name,
                                         query_vector=query_vector,
                                         query_filter=query_filter,
                                         with_vectors=True,
                                         limit=topk,
                                         )
    return search_results







###################################################################################################
if __name__ == "__main__":
    import fire

    fire.Fire()


