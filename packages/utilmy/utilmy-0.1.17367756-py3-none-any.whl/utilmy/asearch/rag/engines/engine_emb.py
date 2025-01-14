
#### pip install apsw vectorlite_py
import vectorlite_py
import numpy as np
import apsw



def np_serialize_f32(vector: List[float]) -> bytes:
    """serializes a list of floats into a compact "raw bytes" format"""
    return struct.pack("%sf" % len(vector), *vector)



def db_sqlite_open_dbvector(dirdb="ztmp/db/db_sqlite/db_vector.db" ):
    """Insert vectors into SQLite database with vector support
            dirdb="ztmp/db/db_vector_test.db"
            dirdb=':memory:'

    """
    conn = apsw.Connection( dirdb )
    conn.enable_load_extension(True) # enable extension loading
    conn.load_extension(vectorlite_py.vectorlite_path()) # loads vectorlite
    db = conn.cursor()
    return db 


def db_sqlite_create_dbvector(dirdb="ztmp/db/db_sqlite/db_vector.db",
                              , table="table_emb", emb_dim=768, n_vectors=10**6, sql=None     
                       ):
    """Insert vectors into SQLite database with vector support
       sql="
             # Create a virtual table to store the embeddings
             cursor.execute(f'create virtual table vector_table using vectorlite(article_embedding float32[{DIM}], hnsw(max_elements={NUM_ELEMENTS}))')

    """
    db = db_sqlite_open_dbvector(dirdb=dirdb)
    log(db)
    sql = f""" create virtual table {table} 
            using vectorlite(emb float32[{emb_dim}], hnsw(max_elements={n_vectors}))
    """
    db.execute(sql)    
    db.close()
    log("Table created", table)



def db_sqlite_insert_vector(df, table='table_emb', colid="chunk_id", colemb='emb', 
                            dirdb="ztmp/db/db_sqlite/db_vector.db", nmax=1, dryrun=1):
    """Insert vectors into SQLite database with vector support


       dirin="ztmp/data/arag/emb/marketsize/241122a_clean/*.parquet"  
       pye db_sqlite_insert_vector --df  $dir2 --cols text_chunk_id --colemb emb

         data       = np.float32(np.random.random((NUM_ELEMENTS, DIM))) # Only float32 vectors are supported by vectorlite for now
         embeddings = [(i, data[i].tobytes()) for i in range(NUM_ELEMENTS)]
         cursor.executemany('insert into vector_table(rowid, article_embedding) values (?, ?)', embeddings)


            qq= 
            SELECT rowid, distance from vector_table 

            where 
               knn_search(article_embedding, knn_param(?, 10)) 
              and rowid in ( 
                     select rowid from news where article like "1%"
              )

            vref =[data[0].tobytes()]
            result = cursor.execute(qq, vref ).fetchall()  
            print(result)



    """
    if isinstance(df, str):
       dirin = df
       df    = pd_read_file(dirin)
       log(df.shape, df.columns)

    cols = [colid, colemb] 
    log(df[cols].shape, cols )
    df1  = df[cols].values
    assert isinstance( df1[0,1], str), "Vector should in string  comma form"
    assert isinstance( df1[0,0], int), "rowid  should in integer form"


    #### SQL setup  ##############################
    db = db_sqlite_open_dbvector(dirdb= dirdb )
    ssinsert = f"{table}(rowid, {colemb})" 
    ss2      = "(?, ?)"  ### (?,?)
    #### 'insert into table_emb(rowid, emb) values (?, ?)'
    sql = f"INSERT INTO {ssinsert}   VALUES {ss2}"



    ##### Insert data #################################################################
    embs = []  
    mbatch = int(len(df) // kbatch) +1
    for kk in range(0, mbatch) :
        if kk >= nmax: break
        vv = df1[ kk*kbatch:(kk+1)*kbatch, : ]
        if len(vv) < 1: break 

        for i in range(0, len(vv)):
            vfloat = np.array([ float(xi) for xi in vv[i,1].split(",") ], dtype='float32')
            embs.append((rowid, vfloat.tobytes() ) )  

        if dryrun == 0:
            try:
                db.executemany(sql, embs)
            except Exception as e:
                log(e)    

        else:
            log(sql, vv)    
    db.close()




def db_sqlite_query_vector_single(db, x0, sqlfilter="", table="table_emb", topk=50, dryrun=1, tostring=1):

    """
          sqlfilter = '  select rowid from news where article like "1%" '

          xall = np.float32(np.random.random((5, 768)))
          x0   = xall[0,:]
          ##### vref = [ xi.tobytes() for xi in xall ]


    """
    if len(sqliter) != 0:
        qq= f"""  SELECT rowid, distance from {table_emb} 

                  where 
                      knn_search(emb, knn_param(?, {topk})) 
                  and rowid in ( {sqlfiter}
                               )
        """
    else: 
        qq = f"""  SELECT rowid, distance from {table} 
                  where 
                          knn_search(emb, knn_param(?, {topk})) 
        """

    vref = [ x0.tobytes()]
    vres = db.execute(qq, vref ).fetchall()  


    return vres 



def np_2darray_to_str(vres):
    ss=""
    for vi in vres:
        for xi in vi:
           ss = ss + ";".join([  str(ti) for ti in  xi]) + ","
    return ss[:-1]          



def db_sqlite_query_vector_df(df, table='table_emb', colid="chunk_id", colemb='emb', 
                            dirdb="ztmp/db/db_sqlite/db_vector.db", nmax=1, dryrun=1):
    """Insert vectors into SQLite database with vector support


       dirin="ztmp/data/arag/emb/marketsize/241122a_clean/*.parquet"  
       pye db_sqlite_insert_vector --df  $dir2 --cols chunk_id_int --colemb emb

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

    db = db_sqlite_open_dbvector(dirdb= dirdb )
    log(db)



    ##### Insert data ######################################################################
    df1 = df[cols].values
    vres= []
    for kk in range(0, len(df)) :
        if kk>=nmax: break
        x0   = df1[ kk ]
        vlist= db_sqlite_query_vector_single(db, x0, sqlfilter= sqlfilter, table="table_emb", 
                                             topk= topk, dryrun=1, tostring=1)
        vres.append(vlist)

    df['emb_topk'] = vres

    db.close()





def db_sqlite_version(dirdb):
  db = db_sqlite_open_dbvector(dirdb)
  sqlite_ver, vec_ver = db.execute( "select sqlite_version(), vec_version()").fetchone()
  print(f"sqlite_version={sqlite_ver}, vec_version={vec_ver}")






###################################################################################################
if __name__ == "__main__":
    import fire

    fire.Fire()







