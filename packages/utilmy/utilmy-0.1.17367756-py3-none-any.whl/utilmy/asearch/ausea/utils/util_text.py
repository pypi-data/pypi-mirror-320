# -*- coding: utf-8 -*-
""" Hugging Face utilities
    #### Install
        cd myutil 
        cd utilmy/webapi/asearch/
        #pip install -r pip/py39_full.txt
        pip install fire python-box utilmy
        pip install fastembed==0.2.6 loguru --no-deps


"""
import string, re, json, pandas as pd, numpy as np,os,sys

from utilmy import (date_now, log, log2, pd_read_file, pd_to_file, json_save, diskcache_load,
                    diskcache_decorator, json_load, pd_read_file)





####################################################################################
################### string helper ##################################################
def date_get(ymd=None, add_days=0):
    y, m, d, h = date_now(ymd, fmt="%y-%m-%d-%H", add_days=add_days).split("-")
    ts = date_now(ymd, fmt="%Y%m%d_%H%M%S")
    return y, m, d, h, ts




def json_loads(x):
    try: 
        return json.loads(str(x))
    except Exception as e:
        log(e)
        return {}   


def str_remove_html_tags(html_string):
    import re
    try:
        # Compile the regex pattern once for efficiency
        CLEANR = re.compile('<.*?>')    
        cleantext = re.sub(CLEANR, '', html_string)
        return cleantext
    except Exception as e:
        log(e)
        return html_string 
        


def textid_create(x, nchars=200, prefix="", nbucket=10**9):
        from utilmy import hash_int64
        x1 = hash_int64(str(x)[:nchars]) % nbucket

        if len(str(prefix)) > 0:
            x2 = f"{prefix}-{x1}-{len(str(x))}"
        else:
            x2 = f"{x1}-{len(str(x))}"

        return x2


def pd_add_textid(df, coltext='text', colid='text_id', nchars=200, prefix="", nbucket=10**9):
    df[colid] = df.apply( lambda x: textid_create(x[coltext], nchars=200, prefix="", nbucket=10**9) , axis=1 )
    return df


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



def pd_add_chunkid_int(df, colid='chunk_id', colidnew='chunk_id_int'):
    log('Add colint col:', colid)
    from utilmy import hash_int32
    df[colidnew] = df[colid].apply(lambda x: hash_int32(x) )
    log(df[[ colid, colidnew]])
    return df


def pd_add_Lcat_industry(df, ):
    import string

    def clean1(x):
        s = ""
        for ci in ['L1_cat', 'L2_cat', 'L3_cat', 'L4_cat', ]:
            if ci in x:
                s = s + " : " + x[ci]

        s = s.replace(" & ", " ").replace(" and ", " ")
        s = s.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation)))
        s = ' '.join(s.split(" "))  ### mutiple space with single

        s = s.replace("CCUS", "CCUS Carbon Capture Utilization and Storage")
        s = s.replace("NFTs", "nfts nft Non Fungible Tokens Digital Assets")
        s = s.replace(" CRM", " Customer Relationship Management")
        s = s.replace(" Tech ", " ").replace(" tech ", " ")

        s = s.lower()
        return s

    df['L_cat'] = df.apply(lambda x: clean1(x), axis=1)
    log(df['L_cat'])
    return df





########### String helper #########################################################
def str_remove_smallword(llist, unique_only=1):
    lblock = {'the', 'to', 'in', 'on', 'not', 'also', 'well', 'for', 'this', 'are', 'they', 'and', 'is',
               'an', 'as', 'at', 'be', 'by', 'do', 'go', 'he', 'if', 'in', 'were',
               'is', 'it', 'me', 'my', 'no', 'of', 'on', 'or', 'so', 'to', 'up',  'we' }    
        
    llist = [ xi for xi in llist if len(xi) >= 2 and xi not in lblock ] 
    if unique_only==1:
        llist = np_unique( llist )

    return llist
##
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



def str_contain_fuzzy_list(word, wlist, threshold=80):
    """
    Check if word fuzzy matches any string in wlist using rapidfuzz
    """
    from rapidfuzz import fuzz
    w0 = str(word.lower())
    return any(fuzz.partial_ratio(w0, w.lower()) >= threshold for w in wlist)


def str_contain_fuzzy_wsplit(word, sentence, sep=" ", threshold=80):
    """
    Check if word fuzzy matches any string in wlist using rapidfuzz
    """
    from rapidfuzz import fuzz
    w0 = str(word.lower())
    wlist = str(sentence).lower().split(sep)
    return any(fuzz.partial_ratio(w0, w.lower()) >= threshold for w in wlist)


def str_match_fuzzy(word, word2="", sep=" ", threshold=80):
    """
    Check if word fuzzy matches any string in wlist using rapidfuzz
    """
    from rapidfuzz import fuzz
    w0 = str(word.lower())
    w2 = str(word2).lower()
    return fuzz.partial_ratio(w0, w2) >= threshold



def json_save2(llg, dirout):
    y,m,d,h = date_now(fmt="%Y-%m-%d-%H").split("-")
    ts      = date_now(fmt="%y%m%d_%H%M%s")
    json_save(llg.to_dict(), dirout + f"/year={y}/month={m}/day={d}/hour={h}/chat_{ts}.json" )


def str_remove_punctuation(text):
    return str(text).translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation)))


def str_find(x:str,x2:str, istart=0):
    try:
        i1 = x.find(x2, istart)
        return i1
    except Exception as e:
        return -1


def str_docontain(words, x):
    x2 = str(x).lower()
    for wi in words.split(" "):
        if wi.lower() not in x2 : return False
    return True


def str_fuzzy_match_list_val(xstr:str, xlist:list, cutoff=70.0):
    from rapidfuzz import process, fuzz
    results = process.extract(xstr, xlist, scorer=fuzz.ratio, score_cutoff=cutoff)
    return [result[0] for result in results]


def str_fuzzy_match_list_score(xstr:str, xlist:list, cutoff=50.0):
    from rapidfuzz import process, fuzz
    results = process.extract(xstr, xlist, scorer=fuzz.ratio, score_cutoff=cutoff)
    return [result[1] for result in results]



def str_fuzzy_match_is_same(str1, str2, threshold=95):
    from rapidfuzz import fuzz
    score = fuzz.ratio( str(str1).lower(), str(str2).lower() )
    if score >= threshold : return True
    return False


def str_fuzzy_match_score(str1, str2, threshold=95):
    from rapidfuzz import fuzz
    score = fuzz.ratio( str(str1).lower(), str(str2).lower() )
    return score


def do_exists(var_name):
    return var_name in locals() or var_name in globals()





#######################################################################################
######## Hash  #######################################################################
def hash_text(x, nchars=200):
    from utilmy import hash_int64
    x1 = str(hash_int64(str(x)[:nchars] + f"-{len(str(x))}"))
    return x1



def hash_textid(xstr:str, n_chars=1000, seed=123)->int:
  """ Computes  xxhash value: Unique ID of a text.
  
  Args:
      xstr (str):  input string.
      n_chars (int): Maximum number of characters to consider for hashing. Defaults to 1000.
      seed (int): Seed value for xxhash. Defaults to 123.
  
  Returns:
      int:  xxhash value calculated based on  input string.
  """
  import xxhash  
  return xxhash.xxh64_intdigest(str(xstr)[:n_chars], seed=seed) - len(xstr)


def hash_text_minhash(text:str, sep=" ", ksize:int=None, n_hashes:int=4)->np.array:
    """Computes  MinHash hash values for  given text using  specified ksize and number of hashes.
       Args:
          text (str):  input text to hash.
          ksize (int):  size of  k-mer to use for hashing, defaults to 4.
          n_hashes (int):  number of hashes to use, defaults to 2.

    Example:
       hash_text_minhash("my very long string text ", n_hashes=4)
       ### array([1136865025,  675357709,  253868148, 1471015800]

       hash_text_minhash("my very very small string text almost equal "
       ### [594334164, 675357709, 253868148, 921427594], dtype=uint64)

    """
    from datasketch import MinHash
    m = MinHash(num_perm=n_hashes)

    if ksize is None :
        for token in text.split(sep):
            m.update(token.encode('utf8'))
    else:
        for k in range(0,  1+ len(text)// ksize ):
            m.update(text[k*ksize: (k+1)*ksize ].encode('utf8'))

    return m.hashvalues


def hash_xxhash(xstr:str, seed=123)->int:
  """ Computes  xxhash value
  
  Args:
      xstr (str):  input string.
      n_chars (int): Maximum number of characters to consider for hashing. Defaults to 1000.
      seed (int): Seed value for xxhash. Defaults to 123.
  
  Returns:
      int:  xxhash value calculated based on  input string.
  """
  import xxhash  
  return xxhash.xxh64_intdigest(str(xstr), seed=seed)


def hash_mmh64(xstr: str) -> int:
    # pylint: disable=E1136
    import mmh3
    return mmh3.hash64(str(xstr), signed=False)[0]


def uuid_int64():
    """## 64 bits integer UUID : global unique"""
    import uuid
    return uuid.uuid4().int & ((1 << 64) - 1)




def pd_add_textid_v1(df, coltext="text", colid="text_id"):
    df[colid] = df[coltext].apply(lambda x : hash_textid(x) )
    return df


def hash_textid_v2(xstr:str, n_chars=1000, seed=123):
    """Generate a UNIQUE hash value for a given text string.
       2 same Exact texts with different lengths --> 2 different hash values.
    Args:
        xstr (str): The input text string.
        n_chars (int, optional): The number of characters to consider from the input string. Defaults to 1000.
        seed (int, optional): The seed value for the hash function. Defaults to 123.
    Returns:
        int: The hash value generated by the xxhash.xxh64_intdigest function.
    """
    import xxhash
    xstr = str(xstr).strip()[:n_chars]
    unique_hash_per_text= xxhash.xxh64_intdigest(xstr, seed=seed) - len(xstr)
    return unique_hash_per_text




def hash_simhash(xstr: str, sep=" "):
    """ Applies the SimHash for text text tokens -->
        Similar text --> Similar hash
        vv="Microsoft, Aurora"
        h1 = hash_textid_eng_v3(vv,)
        vv="Microsoft, Weather.."
        h2 = hash_textid_eng_v3(vv,)
    """
    from floc_simhash import SimHash
    return SimHash(n_bits=64, tokenizer=lambda x: x.lower().split(sep) ).inthash(xstr)


def hash_simhash_dist(a: int, b: int, f = 64):
    """ Calculate the hamming distance between int_a and int_b
        i.e. number of bits by which two inputs of the same length differ
    """
    x = (a ^ b) & ((1 << f) - 1)
    ans = 0
    while x:
        ans += 1
        x &= x - 1
    return ans



def pd_add_textid2(df, coltext="text", colid="text_id"):
    df[colid] = df[coltext].apply(lambda x : hash_textid_v2(x) )
    return df



###################################################################################
def box_to_dict(box_obj):

    from box import (Box, BoxList,  )
    if isinstance(box_obj, Box):
        box_obj = {k: box_to_dict(v) for k, v in box_obj.items()}

    elif isinstance(box_obj, dict):
        return {k: box_to_dict(v) for k, v in box_obj.items()}
    elif isinstance(box_obj, list):
        return [box_to_dict(v) for v in box_obj]

    return str(box_obj) 

def np_str(v):
    return np.array([str(xi) for xi in v])


def np_jaccard_sim(hashes1, hashes2):
    set2 = set(hashes2)
    intersection = 0
    union        = len(hashes1)
    for x in hashes1:
        if x in set2:
            intersection += 1
        else : 
            union += 1
            
    return intersection / union


###################################################################################
###################################################################################
def dataset_kaggle_to_parquet(name, dirout: str = "./ztmp/kaggle/", 
     mapping: dict = None, overwrite=False):
    """Converts a Kaggle dataset to a Parquet file.
    Args:
        dataset_name (str):  name of  dataset.
        dirout (str):  output directory.
        mapping (dict):  mapping of  column names. Defaults to None.
        overwrite (bool, optional):  whe r to overwrite existing files. Defaults to False.
    """
    import kaggle
    # download dataset and decompress
    kaggle.api.dataset_download_files(name, path=dirout, unzip=True)

    df = pd_read_file(dirout + "/**/*.csv", npool=4)
    if mapping is not None:
        df = df.rename(columns=mapping)

    pd_to_file(df, dirout + f"/{name}/parquet/df.parquet")




##########################################################################
def pd_to_file_split(df, dirout, ksize=1000):
    kmax = int(len(df) // ksize) + 1
    for k in range(0, kmax):
        log(k, ksize)
        dirout = f"{dirout}/df_{k}.parquet"
        pd_to_file(df.iloc[k * ksize : (k + 1) * ksize, :], dirout, show=0)



def pd_check_ram_usage(df):
    # Determine  proper batch size
    min_batch_size = 1000
    max_batch_size = 100000
    test_df = df.iloc[:10, :]
    test_memory_mb = test_df.memory_usage(deep=True).sum() / (1024 * 1024)
    log("first 10 rows memory size: ", test_memory_mb)
    batch_size = min (max( int(1024 * 10 // test_memory_mb // 1000 * 1000 ), min_batch_size ), max_batch_size)


def pd_fake_data(nrows=1000, dirout=None, overwrite=False, reuse=True) -> pd.DataFrame:
    from faker import Faker

    if os.path.exists(str(dirout)) and reuse:
        log("Loading from disk")
        df = pd_read_file(dirout)
        return df

    fake = Faker()
    dtunix = date_now(returnval="unix")
    df = pd.DataFrame()

    ##### id is integer64bits
    df["id"] = [uuid_int64() for i in range(nrows)]
    df["dt"] = [int(dtunix) for i in range(nrows)]

    df["title"] = [fake.name() for i in range(nrows)]
    df["body"] = [fake.text() for i in range(nrows)]
    df["cat1"] = np_str(np.random.randint(0, 10, nrows))
    df["cat2"] = np_str(np.random.randint(0, 50, nrows))
    df["cat3"] = np_str(np.random.randint(0, 100, nrows))
    df["cat4"] = np_str(np.random.randint(0, 200, nrows))
    df["cat5"] = np_str(np.random.randint(0, 500, nrows))

    if dirout is not None:
        if not os.path.exists(dirout) or overwrite:
            pd_to_file(df, dirout, show=1)

    log(df.head(1), df.shape)
    return df


def pd_fake_data_batch(nrows=1000, dirout=None, nfile=1, overwrite=False) -> None:
    """Generate a batch of fake data and save it to Parquet files.

    python engine.py  pd_fake_data_batch --nrows 100000  dirout='ztmp/files/'  --nfile 10

    """

    for i in range(0, nfile):
        dirouti = f"{dirout}/df_text_{i}.parquet"
        pd_fake_data(nrows=nrows, dirout=dirouti, overwrite=overwrite)


###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()



