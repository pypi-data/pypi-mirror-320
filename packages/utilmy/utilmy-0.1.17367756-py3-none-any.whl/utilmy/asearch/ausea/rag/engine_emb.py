# -*- coding: utf-8 -*-
"""
    #### Install
        pip install -r py39.txt
        pip install fastembed==0.2.6 loguru --no-deps

    https://blog.ouseful.info/2022/01/24/fuzzy-search-with-multiple-items-table-return-in-sqlite/

    fuzzy match with LIKE
   
"""
import warnings
warnings.filterwarnings("ignore")
import os, pathlib, uuid, time, traceback, pandas as pd, numpy as np, torch
from typing import Any, Callable, Dict, List, Optional, Sequence, Union
from box import Box  ## use dot notation as pseudo class



from fastembed import TextEmbedding
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForMaskedLM

from utilmy import (pd_read_file, os_makedirs, pd_to_file, date_now, glob_glob)
from utilmy import log, log2, os_system, hash_int32

########## Local import
from rag.dataprep import (pd_fake_data, )



######################################################################################
#####################################################################################
########## Dense Vector creation
class EmbeddingModel:
    def __init__(self, model_id, model_type, device: str = "", embed_size: int = 1024 , prompt_name=None):
        """

               modeltype='fastembed'
               modelid="snowflake/snowflake-arctic-embed-l"    ### 768

               modeltype='fastembed'
               modelid="thenlper/gte-large"

                model_id="snowflake/snowflake-arctic-embed-m",
                model_type="fastembed",


                model_type='stransformers'
                model_id="dunzhang/stella_en_400M_v5"

                https://huggingface.co/dunzhang/stella_en_400M_v5


        """
        self.model_id = model_id
        self.model_type = model_type
        self.prompt_name = prompt_name

        if model_id == "dunzhang/stella_en_400M_v5":
            self.prompt_name ="s2p_query" ### snetence to passage


        from utils.utils_base import torch_getdevice
        self.device = torch_getdevice(device)

        if model_type == "stransformers":
            self.model = SentenceTransformer(model_id, device=self.device,  trust_remote_code=True)
            self.model_size = self.model.get_sentence_embedding_dimension()

        elif model_type == "fastembed":
            self.model = TextEmbedding(model_name=model_id, max_length=embed_size)
            embeddings_generator = self.model.embed(['a'])
            embeddings_list = list(embeddings_generator)
            self.model_size = len(embeddings_list[0])  # Vector of 384 dimensions
            log('embed_size:', self.model_size)


        else:
            raise ValueError(f"Invalid model type: {model_type}")

    def embed(self, texts: List):
        if self.model_type == "stransformers":
            vectors = list(self.model.encode(texts, prompt_name= self.prompt_name))

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
        from utils.utils_base import torch_getdevice
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
def embed_create_dense(
        dirin: str,
        colscat: List = None,  ## list of categories field
        coltext: str = "text_chunk",
        model_id="snowflake/snowflake-arctic-embed-m",
        model_type="fastembed",
        kbatch=50,
        dirout="ztmp/data/emb/",
        tag="v1",
        add_date=1,
        nmax=1000
) -> None:
    """Create embedding from parquet file.
               https://qdrant.github.io/fasdtembed/examples/Supported_Models/
               https://huggingface.co/spaces/mteb/leaderboard


               modeltype='fastembed'
               modelid="snowflake/snowflake-arctic-embed-l"    ### 768

               modeltype='fastembed'
               modelid="thenlper/gte-large"


       alias  pye="python rag/engine_emb.py "
       dir1="ztmp/data/arag/"
       pye embed_create_dense --nmax 10000 --dirin "$dir1/question_generated/marketsize/241122a_clean/*.parquet" --dirout   "$dir1/emb/marketsize/241122a_clean/"    


    """
    # df = pd_read_file(path_glob=dirin, verbose=True)
    if isinstance(dirin, pd.DataFrame):
       df = dirin 
    else:   
       flist = glob_glob(dirin)
       log("Nfiles: ", len(flist))

    y,m,d,h = date_now(fmt="%y-%m-%d-%H").split("-")
    dirout1 = dirout + "/" + tag
    if add_date==1:
        dirout1 = dirout1 + f"/year={y}/month={m}/day={d}/"

    log("##### Load model      ")
    model = EmbeddingModel(model_id, model_type)
    dfa   = pd.DataFrame()

    log("#### Start embed generation")
    log('text col', coltext)
    for i, fi in enumerate(flist):
        dfi = pd_read_file(fi)
        log(dfi.shape, fi)

        ### Create embedding vectors batchwise
        dfa  = pd.DataFrame()
        kmax = int(len(dfi) // kbatch) + 1
        for k in range(0, kmax):
            dfk = dfi.iloc[k * kbatch: (k + 1) * kbatch, :]
            if len(dfk) <= 0: break

            dfk["emb"] = model.embed(dfk[coltext].values)
            dfa = pd.concat((dfa, dfk))
            log(dfa.shape)
     
        ### into string format 
        dfa['emb'] = dfa['emb'].apply(lambda x: ",".join([ str(xi) for xi in x      ])) 
        pd_to_file(dfa, dirout + f"/dfemb_{tag}_{i}_{len(dfa)}.parquet")
        if len(dfa)>= nmax:
            return dfa  

    return dfa 



#####################################################################################
def pd_add_chunkid_int(df, colid='chunk_id', colidnew='chunk_id_int'):
    log('Add colint col:', colid)
    from utilmy import hash_int32
    df[colidnew] = df[colid].apply(lambda x: hash_int32(x) )
    log(df[[ colid, colidnew]])
    return df 



def pd_apply_files(dirin, dirout=None, myfun=None, pars=None, dryrun=1, nfile=1):
    """
       dir1="ztmp/data/arag"

       pye pd_apply_files --dryrun 0  --nfile 100  --dirin "$dir1/question_generated/marketsize/241122a/*.parquet"  --dirout  "$dir1/question_generated/marketsize/241122a_clean/"  --myfun pd_text_remove 


       pye pd_apply_files --dryrun 0  --nfile 100  --dirin  "$dir1/question_generated/marketsize/241122a_clean/*.parquet"   --myfun pd_add_chunkid_int 


       pye pd_apply_files --dryrun 0  --nfile 100  --dirin  "$dir1/emb/marketsize/241122a_clean/*.parquet"   --myfun pd_add_chunkid_int 


    """
    flist = glob_glob(dirin)
    pars = {} if pars is None else pars
    dirout = os.path.dirname(dirin) if dirout is None else dirout
    log("dirout:", dirout)

    myfun1 = globals()[myfun]
    log('Using:', myfun1)
    for ii, fi in enumerate(flist):
        if ii >= nfile: break
        log(fi)
        fi2 = fi.split("/")[-1]
        dfi = pd_read_file(fi)
        log(dfi.shape)
        dfi = myfun1(dfi, **pars)
        dirouti = dirout + "/" + fi2

        log(dfi)
        log(dirouti)
        if dryrun ==0:
           pd_to_file(dfi, dirouti )
        else:
           log("dryrun")  



#####################################################################################

#### pip install apsw vectorlite_py
def check():
    import sqlite3
    from typing import List
    import struct
    import vectorlite_py
    import numpy as np
    import apsw



def np_serialize_f32(vector: List[float]) -> bytes:
    """serializes a list of floats into a compact "raw bytes" format"""
    import struct
    return struct.pack("%sf" % len(vector), *vector)



def sqlite_open_dbvector(dirdb="ztmp/db/db_sqlite/db_vector", isconn=0 ):
    """Insert vectors into SQLite database with vector support
            dirdb="ztmp/db/db_vector_test.db"
            dirdb=':memory:'
            import sqlite3
            import gc

            # Create connection
            connection = sqlite3.connect("database.db")

            # Close single connection
            connection.close()

            # Clear connection pools
            sqlite3.Connection.ClearAllPools()

            # Force cleanup
            gc.collect()

    """
    import apsw, vectorlite_py
    from utilmy import os_makedirs
    os_makedirs(dirdb)    
    dirdb = dirdb + "/sqlite.db"

    conn = apsw.Connection( dirdb )
    conn.enable_load_extension(True) # enable extension loading
    conn.load_extension(vectorlite_py.vectorlite_path()) # loads vectorlite

    if isconn == 1:
        log(conn)    
        return conn

    db = conn.cursor()
    log(db)    
    return db 


def sqlite_create_dbvector(dirdb="ztmp/db/db_sqlite/db_vector",
                              table="table_emb", emb_dim=768, n_vectors=10**6, sql=None     
                       ):
    """Insert vectors into SQLite database with vector support
       sql="
             # Create a virtual table to store the embeddings
             cursor.execute(f'create virtual table vector_table using vectorlite(article_embedding float32[{DIM}], hnsw(max_elements={NUM_ELEMENTS}))')

       export dirdb="ztmp/db/db_sqlite/db_vector"  
       pye sqlite_create_dbvector --dirdb $dirdb --table table_emb --emb_dim 768

       # If the index file path is not provided, the index will be stored in memory and will be lost when the database connection closes.
# The index file will be deleted if the table is dropped.
cur.execute(f'create virtual table x using vectorlite(my_embedding float32[{DIM}], hnsw(max_elements={NUM_ELEMENTS}), {index_file_path})')


    """
    from utilmy import os_system
    db = sqlite_open_dbvector(dirdb=dirdb)

    dbvec_path = dirdb + f"/{table}_{emb_dim}.db" 
    sql = f""" create virtual table {table} 
            using vectorlite(emb float32[{emb_dim}], 
                             hnsw(max_elements={n_vectors}),
                             {dbvec_path}
                            )
    """
    db.execute(sql)    
    print(db.execute('select vectorlite_info()').fetchall())
    db.close()
    log(os_system(f"ls -a {dirdb}"))
    log("Table created", table)


def sqlite_info(db, table, dirdb=None):
    """

       cid      name          type     notnull  dflt_value  pk    
        ss =  f"SELECT * FROM {table} WHERE 1 = 2";


    """
    db = sqlite_open_dbvector(dirdb=dirdb)
    ss = f" SELECT *  FROM pragma_table_info('{table}') "
    x00 = np.zeros(768, dtype='float32')
    res = db.execute(ss).fetchall()
    db.close()
    return res


def sqlite_get_all_rowid(db=None, dirdb=None, table="table_emb", ndim=768):
    """
       cid      name          type     notnull  dflt_value  pk    
        ss =  f"SELECT * FROM {table} WHERE 1 = 2";
    """
    if db is None:
        db = sqlite_open_dbvector(dirdb=dirdb)

    ss =   f'select rowid from {table} where knn_search(emb, knn_param(?, 100000000))'
    x00 = np.zeros(ndim, dtype='float32')
    res = db.execute(ss, (x00.tobytes(),)  ).fetchall()
    res = np.array([xi[0] for xi in res ])
    return res


def sqlite_get_nrows(db=None, dirdb=None, table="table_emb", ndim=None):
    """
       cid      name          type     notnull  dflt_value  pk    
        ss =  f"SELECT * FROM {table} WHERE 1 = 2";
    """
    if db is None:
        db = sqlite_open_dbvector(dirdb=dirdb)

    ss =   f'select rowid from {table} where knn_search(emb, knn_param(?, 100000000))'
    x00 = np.zeros(ndim, dtype='float32')
    res = db.execute(ss, (x00.tobytes(),)  ).fetchall()
    res = np.array([xi[0] for xi in res ])
    db.close()
    return len(res)



def test_insert(db):

   nmax=10
   data = np.float32(np.random.random((nmax, 768))) # Only float32 vectors are supported by vectorlite for now
   embeddings = [(i, data[i].tobytes()) for i in range(nmax)]
   db.executemany('insert into table_emb(rowid, emb) values (?, ?)', embeddings)



def sqlite_insert_vector(df, table='table_emb', colrowid="chunk_id_int", colemb='emb', 
                         dirdb="ztmp/db/db_sqlite/db_vector",  nmax=1, kbatch=1, dryrun=1):
    """Insert vectors into SQLite database with vector support



       dirin = "ztmp/data/arag/emb/marketsize/241122a_clean/*.parquet"  
       df    = pd_read_file(dirin)


       pye sqlite_insert_vector --df  $dirin    --colrowid chunk_id_int --colemb emb --nmax 1 --kbatch 1 --dryrun 0

         df = pd_read_file(dirin)
         data       = np.float32(np.random.random((NUM_ELEMENTS, DIM))) # Only float32 vectors are supported by vectorlite for now
         embeddings = [(i, data[i].tobytes()) for i in range(NUM_ELEMENTS)]
         cursor.executemany('insert into vector_table(rowid, article_embedding) values (?, ?)', embeddings)

    """
    if isinstance(df, str):
       dirin = df
       log('loading', dirin)
       df    = pd_read_file(dirin)
       log(df.shape)
 
    cols = [colrowid, colemb] 
    log(df[cols].shape, cols )
    #### SQL setup  ##########################################################
    db = sqlite_open_dbvector(dirdb= dirdb, isconn=1 )


    log("##### Exclude existing rowid ######################################")
    ndim   = len(df[colemb].values[0].split(","))
    rexist = sqlite_get_all_rowid(db=db, table=table, ndim= ndim)
    log(df.shape, "Existing rowid:", len(rexist) )
    df = df[ -df[colrowid].isin(rexist)] ; log(df.shape)
    log(df[colrowid].max())
    assert  is_int32(df[colrowid].max()) ,'not int32'    


    ### rowid, vector_float32
    df1  = df[cols].values
    df1  = [ [v[0],  np.array([ float(xi) for xi in v[1].split(",") ], dtype='float32')] for v in df1 ]
    assert sum([ len(vi[1]) == ndim for vi in df1]) == len(df1), f"Vector not all dim {ndim}"

    
    log("##### Insert vector data ########################", len(df1), ndim)
    #### 'insert into table_emb(rowid, emb) values (?, ?)'
    sql  = f""" INSERT INTO {table}(rowid, {colemb})    VALUES (?,?) ;  """
    nall = 0
    mbatch = int(len(df1) // kbatch) +1
    log(sql)
    for kk in range(0, mbatch) :
        log('Batch:', kk)
        if kk >= nmax: break
        vv = df1[ kk*kbatch:(kk+1)*kbatch]
        if len(vv) < 1: break 

        embs = []  
        for i in range(0, len(vv)):
             vfloat = vv[i][1]
             rowid  = vv[i][0]
             embs.append((rowid, vfloat.tobytes() ) )  

        if dryrun == 0:
            try:
                db.executemany(sql, embs)
                nall += len(embs)
                log('inserted', nall)
            except Exception as e:
                log(kk, e)    
        else:
            log(str(vv)[:50] )    

    log("Total Inserted:", nall)        
    db.close()
    log('Check Total',  sqlite_get_nrows(dirdb=dirdb, table=table, ndim=ndim)) 



def sqlite_insert_table(df, table='marketsize', cols=None,
                         dirdb="ztmp/db/db_sqlite/db_vector",  nmax=1, kbatch=1, dryrun=1, tag='marketsize'):
    """Insert vectors into SQLite database with vector support

       dirin="ztmp/data/arag/emb/marketsize/241122a_clean/*.parquet"  
       pye sqlite_insert_table --df  $dirin    --colrowid chunk_id_int --colemb emb --nmax 1 --kbatch 1 --dryrun 0

      cols = [ 'chunk_id_int',  'L_cat', 'title',  'text_chunk',  'L3_catid',  'chunk_id', 'date',  'question_list',   'url' ]


    """
    if isinstance(df, str):
       dirin = df
       log('loading', dirin)
       df    = pd_read_file(dirin)
       log(df.shape)
 
    from sqlalchemy import create_engine
    engine = create_engine(f'sqlite:///{dirdb}/sqlite.db')

    if 'content_type' not in df.columns:
       df['content_type'] = tag
       cols = cols +['content_type']

    df[cols].iloc[:nmax,:].to_sql(table, engine, if_exists='append', index=False)
    res = pd.read_sql(f'SELECT COUNT(1) FROM {table}', con=engine)
    log('Check Total:',  res.values ) 



def batch_insert(dirdb="ztmp/db/db_sqlite/db_vector"):

    dirin = "ztmp/data/arag/emb/marketsize/241122a_clean/*.parquet"  
    cols  = [ 'chunk_id_int',  'L_cat', 'title',  'text_chunk',  'L3_catid',  'chunk_id', 'date',  'question_list',   'url' ]
    tag   = 'marketsize'
    table = 'marketsize'
    df = pd_read_file(dirin)
    sqlite_insert_table(df, table=table, cols=cols, dirdb=dirdb,  nmax=10000, dryrun=1, tag=tag)


    dirin = "ztmp/data/arag/emb/overview/241122a_clean/*.parquet"  
    cols  = [ 'chunk_id_int',  'L_cat', 'title',  'text_chunk',  'L3_catid',  'chunk_id', 'date',  'question_list',   'url' ]
    tag   = 'marketsize'
    table = 'marketsize'
    df = pd_read_file(dirin)
    sqlite_insert_table(df, table=table, cols=cols, dirdb=dirdb,  nmax=10000, dryrun=1, tag=tag)




#############################################################################
#############################################################################
def sqlite_knn_vector_single(db, x0=None, sqlfilter=None, table="table_emb", topk=50, dryrun=1, tostring=1):

    """
          sqlfilter = '  select rowid from news where article like "1%" '
          xall = np.float32(np.random.random((5, 768)))
          x0   = xall[0,:]
          ##### vref = [ xi.tobytes() for xi in xall ]

    """
    if sqlfilter is not None:
        qq= f"""  SELECT rowid, distance from {table} 
                  where   knn_search(emb, knn_param(?, {topk})) 
                  and rowid in ( {sqlfilter}   )
        """
    else: 
        qq = f"""  SELECT rowid, distance from {table} 
                   where   knn_search(emb, knn_param(?, {topk})) 
        """

    vref = [ x0.tobytes()]
    vres = db.execute(qq, vref ).fetchall()  
    return vres 



def sqlite_get_allemb(db, x0=None, sqlfilter=None, table="table_emb", 
                             rowlist=None,dirdb=None):

    """
       sqlfilter = '  select rowid from news where article like "1%" '
       xall = np.float32(np.random.random((5, 768)))
       x0   = xall[0,:]
       where rowid = 1

    """
    if db is None:
        db  = sqlite_open_dbvector(dirdb=dirdb)

    rowlist = ",".join(rowlist)
    res = db.execute(f'select rowid, vector_to_json(emb) from {table} where rowid in ( {rowlist} )')
    res =res.fetchall()
    return res




def sqlite_dense_search(query="market size of Carbon capture and utilization",
                        topk: int = 20,
                        category_filter: dict = None,

                        db= None,
                        dirdb="ztmp/db/db_sqlite/db_vector",
                        table: str = "table_emb",

                        model: EmbeddingModel = None,
                        model_type="fastembed",
                        model_id= "snowflake/snowflake-arctic-embed-m"  ### 384,  50 Mb
                        ) -> List:
    """
        model_id="snowflake/snowflake-arctic-embed-m"
        model_type="fastembed"
        query= "market size of Carbon capture and utilization"

        query="TAM for indentify & Access market"
        category_filter = None 


       df[ df['chunk_id_int'].isin(resid) ]

       print( df['text_chunk'].values[0] )


       resid = [ x[0] for x in res2D ]
       df2 = pd_reorder(df, 'chunk_id_int', resid)       
       df2['chunk_id_int']

            df2[[ 'L_cat', 'text_chunk' ]]

            df2[[  'text_chunk' ]].values[0]
            df2[[  'text_chunk' ]].values[4]


        ### Clean Data.
            Chart ID: No Chart IDSource: /JEIDe/1/\n\nL



 Chart ID

         query= " SSO infrastructure and credential management ""


    """

    if db is None:
        db = sqlite_open_dbvector(dirdb) if db is None else db

    model    = EmbeddingModel(model_id, model_type) if model is None else model

    emb_list = model.embed([query])  ### List of numpy array

    #### SQL on L_cat,... matching
    qfilter = sqlite_query_createfilter(category_filter)

    #### List of chun_id_int, distance.
    res2D = sqlite_knn_vector_single(db, x0=emb_list[0], sqlfilter= qfilter, table= table, 
                                    topk=topk)    

    return res2D




def pd_reorder(df, col=None, colvalues=None):
    """ Reorder DataFrame rows based on colBlist while keeping all initial rows.    
    Args:
        df: pandas DataFrame
        colBlist: list of IDs to order by        
    """
    df['sort_order_'] = pd.Categorical(df[col], categories=colvalues, ordered=True)
    return df.sort_values('sort_order_').drop('sort_order_', axis=1)




def sqlite_query_vector_df(df, table='table_emb', colid="chunk_id", colemb='emb', 
                           dirdb="ztmp/db/sqlite/db_vector", nmax=1, dryrun=1, topk=1,
                           sqlfilter="",
                           ):
    """Insert vectors into SQLite database with vector support


       dirin="ztmp/data/arag/emb/marketsize/241122a_clean/*.parquet"  
       pye sqlite_insert_vector --df  $dir2 --cols chunk_id_int --colemb emb

         data       = np.float32(np.random.random((NUM_ELEMENTS, DIM))) # Only float32 vectors are supported by vectorlite for now
         embeddings = [(i, data[i].tobytes()) for i in range(NUM_ELEMENTS)]
         cursor.executemany('insert into vector_table(rowid, article_embedding) values (?, ?)', embeddings)

    """
    if isinstance(df, str):
      dirin = df
      df    = pd_read_file(dirin)
      log(df.shape, df.columns)

    cols = [colid, colemb] 
    log(df[cols].shape, cols )

    db = sqlite_open_dbvector(dirdb= dirdb )
    log(db)



    ##### Insert data ######################################################################
    df1 = df[cols].values
    vres= []
    for kk in range(0, len(df)) :
        if kk>=nmax: break
        x0   = df1[ kk ]
        vlist= sqlite_knn_vector_single(db, x0, sqlfilter= sqlfilter, table="table_emb",
                                             topk= topk, dryrun=1, tostring=1)
        vres.append(vlist)

    df['emb_topk'] = vres

    db.close()



def sqlite_version(dirdb):
  db = sqlite_open_dbvector(dirdb)
  sqlite_ver, vec_ver = db.execute( "select sqlite_version(), vec_version()").fetchone()
  print(f"sqlite_version={sqlite_ver}, vec_version={vec_ver}")




###################################################################################
def sqlite_query_createfilter(
        category_filter: Dict = None,
) :
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

    qfilter =" SELECT chunk_id_int as rowid FROM marketsize  "
    # catfilter = []
    # for catname, catval in category_filter.items():
    #     xi = models.FieldCondition(key   = catname,
    #                                match = models.MatchText(value=catval))
    #     catfilter.append(xi)
    # query_filter = models.Filter(should=catfilter)
    return qfilter




def pd_dense_search(df, llist=None,
                      query= "market size of Carbon capture and utilization",
                      topk: int = 10,
                      indus_list=None,
                      topic_list=None,  
                      category_filter: dict = None,
    ) -> List:
    """

           

    """
    global dfrag

    cols =['chunk_id', 'text_chunk', 'title', 'url']


    dfw = pd_search_keywords_fuzzy(dfrag[cols], 'text_chunk', keywords=llist, tag='_txt')
    dfw = pd_search_keywords_fuzzy(dfw, 'title', keywords=llist, tag='_tit')

    dfw['score'] = dfw.apply(lambda x: x['find_scores_txt'] + 0.2*x['find_scores_tit'], axis=1   )

    dfw = dfw.sort_values('score', ascending=0)    
    dfw = dfw[ dfw['score'] > 0.5  ]  
    dfw = dfw.iloc[:topk, :]

    return dfw





def pd_search_keywords_fuzzy(df, text_column, keywords, threshold=80, tag="", only_score=1, cutoff=70.0,):
    """ Perform fuzzy matching on dataframe text column against keywords list
        Returns matches and scores for each row


        ###### Example usage:
        keywords = ['mareting', 'dgital', 'seo']
        dfz = pd.DataFrame({'text': ['digital marketing services', 
                                     'seo optimization']})
    
        llist = "genenrative ai genai"
        dfw   = pd_search_keywords_fuzzy(df.iloc[:,:], 'text_chunk', keywords=llist, tag='_txt')

        dfw   = dfw.sort_values('find_scores_txt', ascending=0)    
        dfw[[ 'chunk_id', 'find_scores'  ]]
        dfw   = pd_search_keywords_fuzzy(dfw, 'title', keywords=llist, tag='_tit')


        dfw[[ 'L_cat', 'text_chunk', 'title'  ]]

        dfw['score'] =dfw.apply(lambda x: x['find_scores_txt'] + 0.2*x['find_scores_tit'], axis=1   )
        dfw   = dfw.sort_values('score', ascending=0)    


             word='market'
             str_fuzzy_match_list(word, xlist= llist, cutoff=80.0)

        ccols.cols_chunk =[ 'url', 'chunk_id', 'chunk_id_int', 'date', 'title', 'text_chunk', 'L_cat', 'title',
                            'content_type', 'emb', 'text_html', 'question_list'
                          ]

        ['L3_catid', 'L_cat', 'chunk_id', 'chunk_id_int', 'date', 'emb', 'index',
            'model', 'n', 'question_list', 'text', 'text2', 'text_chunk',
            'text_html', 'text_id', 'text_id2', 'title', 'url', 'matches',
            'score']
        

    """
    import pandas as pd, re

    keywords = keywords.split(" ") if isinstance(keywords, str) else keywords
    size     = [len(xi) for xi in keywords ]
    nkeywords = len(keywords)
    log(text_column, keywords)
    if nkeywords < 1:
        if only_score == 1:
            df['score' + tag] = 0.0
            return df
        else:
            df[['match' + tag, 'score' + tag]] = 0.0
            return df

    min_size = min(size) - 2
    max_size = max(size) + 2

    lblock = {'the', 'to', 'in', 'on', 'not', 'also', 'well', 'for', 'this', 'are', 'they', 'and', 'is',
              'an', 'as', 'at', 'be', 'by', 'do', 'go', 'he', 'if', 'in', 'were',
              'is', 'it', 'me', 'my', 'no', 'of', 'on', 'or', 'so', 'to', 'up',  'we' }

    if only_score ==1:
        def match_row(text):
            # Get best match and score for each word in text
            words = re.findall(r'\w+|[^\s\w]', str(text).lower())
            words = np_unique([xi for xi in words if len(xi) >= 2 and xi not in lblock])
            # log( str(words)[:100])

            scores = 0.0
            for word in words:
                sz = len(word)
                if sz < min_size or sz > max_size: continue

                match = str_fuzzy_match_list(word, xlist=keywords, cutoff= cutoff)
                if match:
                    # matches = matches + ",".join([xi[0] for xi in match]) + ","
                    scores += np.sum([xi[1] for xi in match])
            return scores

        #### Apply matching to each row
        df['score' + tag ] = df[text_column].apply(match_row)
        df[ 'score' + tag] = df['score'+tag] / nkeywords * 0.01
        return df

    def match_row(text):
        # Get best match and score for each word in text
        words = re.findall(r'\w+|[^\s\w]', str(text).lower() )
        words = np_unique([ xi for xi in words if len(xi) >= 2 and xi not in lblock ] ) 
        # log( str(words)[:100])

        matches = ""
        scores  = 0.0
        for word in words:
            sz = len(word)
            if sz < min_size or sz>max_size: continue 

            match = str_fuzzy_match_list(word, xlist= keywords, cutoff=70.0)
            if match:
                matches = matches + ",".join([xi[0] for xi in      match] ) + ","
                scores +=  np.sum([ xi[1] for xi in      match] )
                
        return pd.Series({'matches': matches,
                         'score':   scores })
    
    ##### Apply matching to each row
    results = df[text_column].apply(match_row)
    df[['match' + tag, 'score' + tag ]] = results
    df['score' + tag] = df['score'+tag] /nkeywords * 0.01
    return df


def pd_search_keywords_fullmatch(df, text_col, keywords, tag="", only_score=1, cutoff=70.0, ):
    """ Perform fuzzy matching on dataframe text column against keywords list
        Returns matches and scores for each row

    """
    import pandas as pd, re
    keywords = keywords.split(" ") if isinstance(keywords, str) else keywords
    keywords = [ xi for xi in keywords if len(xi.split(" ")) >=1  ]
    log(text_col,tag, keywords)

    if len(keywords)< 1:
        df['score' + tag ] = 0.0
        return df

    def match_row(text):
        text2  = " " + str(text).lower() + " "
        scores = 0.0
        for word in keywords:
            sci =  1.0 if word in text2 else 0.0
            scores += sci
        return scores

    df['score' + tag] = df[text_col].apply(lambda  x:  match_row(x) )
    df['score' + tag] = df['score' + tag] / len(keywords)
    return df


def pd_search_keywords_fullmatch_single(df, text_col, keywords, tag="", only_score=1, cutoff=70.0, ):
    """ Perform fuzzy matching on dataframe text column against keywords list
        Returns matches and scores for each row

    """
    import pandas as pd, re
    keywords = keywords.split(" ") if isinstance(keywords, str) else keywords
    keywords = [xi for xi in keywords if len(xi.split(" ")) >= 1]
    log(text_col,tag, keywords)

    if len(keywords)< 1:
        df['score'+tag] = 0.0
        return df

    nall =0.0
    for wi in keywords:
        nall += len(wi.split(" "))

    def match_row(text):
        text2 = " " + str(text).lower() + " "
        scores = 0.0
        for word in keywords:
            for wi in word.split(" "):
               sci = 1.0 if " " + wi +" " in text2 else 0.0
               scores += sci
        return scores

    df['score' + tag] = df[text_col].apply(lambda x: match_row(x))
    df['score' + tag] = df['score' + tag] / nall
    return df


##############################################################################
def str_remove_smallword(llist, unique_only=1):
    lblock = {'the', 'to', 'in', 'on', 'not', 'also', 'well', 'for', 'this', 'are', 'they', 'and', 'is',
               'an', 'as', 'at', 'be', 'by', 'do', 'go', 'he', 'if', 'in', 'were',
               'is', 'it', 'me', 'my', 'no', 'of', 'on', 'or', 'so', 'to', 'up',  'we' }    
        
    llist = [ xi for xi in llist if len(xi) >= 2 and xi not in lblock ] 
    if unique_only==1:
        llist = np_unique( llist )

    return llist



def str_replace_punctuation(text, val=" "):
    import re
    return re.sub(r'[^\w\s]', val, text)



def str_subsequence_score(sentence1, sentence2):
    """
        # Example usage
        print(is_subsequence_words("cat dog", "the cat runs fast dog"))  # True
        print(is_subsequence_words("cat bird", "the cat runs fast dog"))  # False
    """
    words1 = sentence1.lower().split()
    words2 = sentence2.lower().split()
    
    i = 0  # pointer for words1
    j = 0  # pointer for words2
    cnt =0
    while i < len(words1) and j < len(words2):
        if words1[i] == words2[j]:
            i += 1
            cnt += 1
        j += 1
        
    return cnt



def str_question_regex_norm(text):
    import re
    result = re.sub(r'(?<!\s)\?', ' ?', text)
    return result


    
def str_fuzzy_match_list_wordonly(xstr:str, xlist:list, cutoff=70.0):
    from rapidfuzz import process, fuzz
    results = process.extract(xstr, xlist, scorer=fuzz.ratio, score_cutoff=cutoff)
    return [result[0] for result in results]


def str_fuzzy_match_list(xstr:str, xlist:list, cutoff=70.0):
    from rapidfuzz import process, fuzz
    results = process.extract(xstr, xlist, scorer=fuzz.ratio, score_cutoff=cutoff)
    return results


def str_is_same_fuzzy(str1, str2, threshold=95):
    from rapidfuzz import fuzz
    score = fuzz.ratio( str(str1).lower(), str(str2).lower() )
    if score >= threshold : return True 
    return False


def str_split_lower(text):
    import re
    try:
        return  re.findall(r'\w+|[^\s\w]', str(text).lower() )
    except Exception as e:
        return [ text ] 


def np_unique(xlist):
    l2 = []
    for xi in xlist:
        if xi not in l2:
            l2.append(xi)
    return l2



def np_2darray_to_str(vres):
    ss=""
    for vi in vres:
        for xi in vi:
           ss = ss + ";".join([  str(ti) for ti in  xi]) + ","
    return ss[:-1]          


def test2():
    #### pip install apsw vectorlite_py
    import vectorlite_py
    import numpy as np
    import apsw


    dirdb="ztmp/db/db_vector_test.db"
    dirdb=':memory:'

    conn = apsw.Connection( dirdb )
    conn.enable_load_extension(True) # enable extension loading
    conn.load_extension(vectorlite_py.vectorlite_path()) # loads vectorlite

    cursor = conn.cursor()

    DIM = 32 # dimension of the vectors
    NUM_ELEMENTS = 1000 # number of vectors

    # In this example, we have a news table that stores article.
    cursor.execute(f'create table news(rowid integer primary key, article text)')



    cursor.executemany('insert into news(rowid, article) values (?, ?)', [(i, str(i)) for i in range(NUM_ELEMENTS)])

    # Create a virtual table to store the embeddings
    cursor.execute(f'create virtual table vector_table using vectorlite(article_embedding float32[{DIM}], hnsw(max_elements={NUM_ELEMENTS}))')



    data = np.float32(np.random.random((NUM_ELEMENTS, DIM))) # Only float32 vectors are supported by vectorlite for now
    embeddings = [(i, data[i].tobytes()) for i in range(NUM_ELEMENTS)]
    cursor.executemany('insert into vector_table(rowid, article_embedding) values (?, ?)', embeddings)

    qq= """
    SELECT rowid, distance from vector_table 

    where 
       knn_search(article_embedding, knn_param(?, 10)) 
      and rowid in ( 
             select rowid from news where article like "1%"
      )

    """
    vref =[data[0].tobytes()]
    result = cursor.execute(qq, vref ).fetchall()  
    print(result)


def is_int32(num):
    return isinstance(num, (int, np.integer)) and  num <= 2**32 - 1












#####################################################################################
######### Qdrant Sparse Vector Engine :
def emb_sparse_create(
        dirin: str,
        server_url: str = ":memory:",
        collection_name: str = "my-sparse-documents",
        colscat: list = None,
        coltext: str = "text",
        model_id: str = "naver/efficient-splade-VI-BT-large-doc",
        batch_size: int = 5,
        max_words: int = 256,
        db=None,
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











###################################################################################################
if __name__ == "__main__":
    import fire

    fire.Fire()













def sqlite_open_dbvector_v2(dirdb="ztmp/db/sqlite/db_vector" ):
    """Insert vectors into SQLite database with vector support"""
    db = sqlite3.connect(dirdb)
    db.enable_load_extension(True)
    sqlite_vec.load(db)
    log(db)
    return db



def sqlite_create_dbvector_v2(sql, dirdb="ztmp/db/sqlite/db_vector" ):
    """Insert vectors into SQLite database with vector support

  
       sql="
              create virtual table tb_text_chunk_emb using vec0(
                    chunk_id integer primary key,

                    -- Vector
                    text_chunk_emb float[768],

                    -- Columns appear in `WHERE` clause of KNN queries
                    text_type  text,
                    L_cat      text

                    -- Partition key on article published year
                    -- year integer partition key,


                    -- Auxiliary columns, unindexed but fast lookups
                    +title      text,
                    +text_chunk text,
                    +url        text
                    +date       text,
              );


    """
    db = sqlite3.connect(dirdb)
    db.enable_load_extension(True)
    sqlite_vec.load(db)
    log(db)
    log(sql)
    
    db.execute(sql)    
    db.close()
    log("Table created")


def sqlite_version_v2(dirdb):
  db = sqlite_open_dbvector(dirdb)
  sqlite_ver, vec_ver = db.execute( "select sqlite_version(), vec_version()").fetchone()
  print(f"sqlite_version={sqlite_ver}, vec_version={vec_ver}")



def sqlite_insert_vector_v2(df, table='mytable', cols=None, colemb='emb', dirdb="ztmp/mydb.db", nmax=1, dryrun=1):
    """Insert vectors into SQLite database with vector support


       dir2=" "ztmp/data/arag/emb/marketsize/241122a_clean/*.parquet"  
       pye sqlite_insert_vector --df  $dir2 --cols "text_type,L_cat,title,text_chunk,url,date"


    """
    if isinstance(df, str):
      dirin = df
      df    = pd_read_file_s3(dirin)
      log(df.shape, df.columns)

    log(df[cols + [colemb]].shape, cols, colemb )

    db = sqlite_open_dbvector(dirdb= dirdb )
        
    sscols   = ",".join( cols + [colemb]) 
    ssinsert = f"{table}({sscols})" # mytext(text_id, embed)
    ss2 = "?," * len(sscols)
    ss2 = "(" + ss2[:-1] + ")"  ### (?,?)

    ##### Insert data
    with db:
        for ii, row in df[ cols + [colemb]  ].iterrows():
            if ii>=nmax: break
            vv = [ row[ci] for ci in cols ] 
            vv = vv + [ serialize_float32(row[colemb]) ]
            sql = f"INSERT {ssinsert}  INTO  VALUES {ss2}"
            if dryrun == 0:
                db.execute(sql, vv)
            else:
                log(sql, vv)    
    db.close()








