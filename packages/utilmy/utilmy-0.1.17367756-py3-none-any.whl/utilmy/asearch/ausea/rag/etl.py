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


from utils.util_text import (
  str_remove_html_tags, str_remove_smallword, str_find, str_contain_fuzzy_list,str_fuzzy_match_list,
  textid_create, pd_add_textid, hash_text, hash_textid

)


#####################################################################################
#####################################################################################
def data_rag_dump_v2():
        d1  = "ztmp/data/arag/emb/marketsize/241122a_clean/*.parquet"
        tag = "marketsize"
        tag = "overview"
        tag = "insight"
        d1  = f"ztmp/data/arag/question_generated/{tag}/241122/*.parquet"
        df  = pd_read_file(d1)

        ccols = Box({})
        ccols.cols_rag = [ 'url', 'content_type',  'L_cat',  'date', 'title', 'text_chunk', 
                           'chunk_id', 'chunk_id_int',   'emb', 'text_html', 'question_list', 'info'
                         ]
        df[ccols.cols_rag]                

        df['text_html']    =  df['text_full']
        df['chunk_id_int'] = df['chunk_id'].apply(hash_int32)
        df['emb'] = "" 

        df = pd_text_remove(df, coltext='text_chunk', word='chart id')                  
        df = pd_text_remove(df, coltext='text_html',  word='chart id')                  

        df['content_type'] = tag
        df['info']         = ''

        df['com_name']     = ""
        df['activity']     = ""

        df1 = df.drop_duplicates(['url', 'text_chunk'], keep='last')
        df1['chunk_id']

        dirout1 = "ztmp/data/arag/final/242225/"    
        pd_to_file( df1[ccols.cols_rag], dirout1 + f"/df_{tag}_rag.parquet" )


        df = pd_read_file("ztmp/data/arag/final/242225/*.parquet"   )
        df = pd_clean_industry(df, col='L_cat') 

        pd_to_file( df, dirout1 + f"/all/df_all_rag.parquet" )




def str_fuzzy_match_list_score(xstr:str, xlist:list, cutoff=50.0):
    from rapidfuzz import process, fuzz
    results = process.extract(xstr, xlist, scorer=fuzz.ratio, score_cutoff=cutoff)
    return [result[1] for result in results]




def data_rag_dump2():
    ##### TODO
    dirdata ="ztmp/aiui/data/rag/db_tmp/final/"

    dfa = pd_read_file(dirdata + "/industry_update_all.parquet" )

    dfa.columns

    ['L1_cat', 'L2_cat', 'L3_cat', 'L3_cat2', 'L3_catid', 'L4_cat',
           'com_name', 'content_id', 'dt', 'id', 'news_type', 'text', 'title',
           'url'],


    for ci in dfa.columns:
       dfa[ci] = dfa[ci].astype(str)

    'activity'. partnershop
    'content_type'. news industry update


    ###### Details
    dfa['L_cat'] = dfa.apply(lambda x:  " ".join( [x['L1_cat'], x['L2_cat'], x['L3_cat'],  x['L4_cat'] ]), axis=1  )
    dfa = pd_clean_industry(dfa, col='L_cat')


    df['text_chunk'] = df['text']

    df['chunk_id_int'] = pd_add_chunkid_int(df)

    df['chunk_id_int'] = pd_add_chunkid_int(df)


    ccols.cols_chunk =[ 'url', 'chunk_id', 'chunk_id_int', 'date', 'title', 'text_chunk', 'L_cat', 'title',
                        'content_type', 'emb', 'text_html', 'question_list',
                        'com_name', 'activity'
                      ]




def pd_text_remove(df, coltext='text_chunk', word='chartid'):
    log('Removing text in col:', coltext)
    def text_remove(x):
        l1 = x.split("\n")
        l2 = []
        for li in l1:
            if word in li.lower(): continue
            l2.append(li)

        l2 = "\n".join(l2)
        return l2     

    df[coltext] = df[coltext].apply(lambda x: text_remove(x))
    log(df[coltext])
    return df 




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



def pd_clean_industry(df, col='L_cat'):
    def clean_indus(x):
        x = x.replace(" & ", " ")

        x = str_replace_punctuation(x, val=" ")
        x = x.replace("CCUS", "CCUS Carbon Capture Utilization and Storage")
        x = x.replace("NFTs", "nfts nft Non Fungible Tokens Digital Assets")
        x = x.replace(" CRM", " Customer Relationship Management")
        x = x.replace(" Tech ", " ").replace(" tech ", " ")
        x = x.replace(";", " ")
        x = " ".join( [xi for xi in x.split(" ") if len(xi)>0 ] )
        return x 

    df[col] = df[col].apply(lambda x: clean_indus(x)  )
    log( df[col])
    return df  




def json_load2(x):
   try: 
      return json.loads(str(x))
   except Exception as e:
      log(e)
      return {}   




def pd_add_chunkid(df, coltextid="text_id2", colout='text_chunk', nchars=200, prefix="", nbucket=10**9):
    df['chunk_id'] = df.groupby(coltextid).cumcount()
    df['chunk_id'] = df.apply( lambda x: f"{x[coltextid]}-{x['chunk_id']}", axis=1 )
    log("Added chunk_id")
    return df


def pd_text_chunks(df, coltext='text2', colout='text_chunk', sentence_chunk=10):
    """ Split into block of 10 sentences. with title added

       'url', 'text_id', 'text', 'title'. --->.  'text_id', 'text',  'chunk_id',  'text_chunk'

    """
    def split_text_into_sentence_chunks(text, sentences_per_chunk=sentence_chunk):
        sentences = text.split('. ')
        return ['. '.join(sentences[i:i + sentences_per_chunk]) for i in range(0, len(sentences), sentences_per_chunk)]

    df['text_chunks'] = df[coltext].apply(split_text_into_sentence_chunks)

    df2 = df.explode('text_chunks').reset_index()
    df2 = df2.rename(columns={'text_chunks': 'text_chunk'})

    df2['text_id2'] = df2.apply( lambda x: textid_create(x[coltext], nchars=200, prefix="", nbucket=10**10) , axis=1 )
    df2['chunk_id'] = df2.groupby('text_id2').cumcount()
    df2['chunk_id'] = df2.apply( lambda x: f"{x['text_id2']}-{x['chunk_id']}", axis=1 )


    log(df2[['text_id2', 'chunk_id', 'text_chunk']])
    log("added cols:",['text_id2', 'chunk_id', 'text_chunk']  )
    return df2









###################################################################################################
if __name__ == "__main__":
    import fire

    fire.Fire()









