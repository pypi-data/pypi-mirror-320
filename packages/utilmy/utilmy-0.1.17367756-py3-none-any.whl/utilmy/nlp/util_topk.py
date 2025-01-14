# coding=utf-8
MNAME='utilmy.nlp.util_topk'
"""  Top-K retrieval


"""
import os, sys, itertools, time, pandas as pd, numpy as np, pickle, gc, re, random, glob
from typing import Callable, Tuple, Union
from box import Box

from utilmy import pd_read_file, pd_to_file, os_makedirs


### NLP
import faiss


#################################################################################################
from utilmy import log, log2, help_create
def help():
    print( help_create(MNAME))


#################################################################################################
def test_all():
   test1()


def test1():
    pass



################################################################################################
def embedding_model_to_parquet(model_vector_path="model.vec", nmax=500):
    from gensim.models import KeyedVectors
    from collections import OrderedDict
    def isvalid(t):
        return True

    log("loading model.vec")  ## [Warning] Takes a lot of time
    en_model = KeyedVectors.load_word2vec_format(model_vector_path)

    # Limit number of tokens to be visualized
    limit = nmax if nmax > 0 else len(en_model.vocab)  # 5000
    vector_dim = en_model[list(en_model.vocab.keys())[0]].shape[0]

    jj = 0
    words = OrderedDict()
    embs = np.zeros((limit, vector_dim))
    for i, word in enumerate(en_model.vocab):
        if jj >= limit: break
        if isvalid(word):
            words[word] = jj  # .append(word)
            embs[jj, :] = en_model[word]
            jj = jj + 1

    embs = embs[:len(words), :]

    df_label = pd.DataFrame(words.keys(), columns=['id'])
    return embs, words, df_label


def embedding_to_parquet(dirin=None, dirout=None, skip=0, nmax=10 ** 8,
                         is_linevalid_fun=None):  ##   python emb.py   embedding_to_parquet  &
    #### FastText/ Word2Vec to parquet files    9808032 for purhase

    log(dirout);
    os_makedirs(dirout);
    time.sleep(4)

    if is_linevalid_fun is None:  #### Validate line
        def is_linevalid_fun(w):
            return len(w) > 5  ### not too small tag

    i = 0;
    kk = -1;
    words = [];
    embs = [];
    ntot = 0
    with open(dirin, mode='r') as fp:
        while i < nmax + 1:
            i = i + 1
            ss = fp.readline()
            if not ss: break
            if i < skip: continue

            ss = ss.strip().split(" ")
            if not is_linevalid_fun(ss[0]): continue

            words.append(ss[0])
            embs.append(",".join(ss[1:]))

            if i % 200000 == 0:
                kk = kk + 1
                df = pd.DataFrame({'id': words, 'emb': embs})
                log(df.shape, ntot)
                if i < 2: log(df)
                pd_to_file(df, dirout + f"/df_emb_{kk}.parquet", show=0)
                ntot += len(df)
                words, embs = [], []

    kk = kk + 1
    df = pd.DataFrame({'id': words, 'emb': embs})
    ntot += len(df)
    dirout2 = dirout + f"/df_emb_{kk}.parquet"
    pd_to_file(df, dirout2, show=1)
    log('ntotal', ntot, dirout2)
    return os.path.dirname(dirout2)


def embedding_load_parquet(dirin="df.parquet", nmax=500):
    """  id, emb (string , separated)
    
    """
    log('loading', dirin)
    col_embed = 'pred_emb'
    colid = 'id'
    # nmax    = nmax if nmax > 0 else  len(df)   ### 5000

    flist = list(glob.glob(dirin))

    df = pd_read_file(flist, npool=max(1, int(len(flist) / 4)))
    df = df.iloc[:nmax, :]
    df = df.rename(columns={col_embed: 'emb'})

    df = df[df['emb'].apply(lambda x: len(x) > 10)]  ### Filter small vector
    log(df.head(5).T, df.columns, df.shape)
    log(df, df.dtypes)

    ###########################################################################
    ###### Split embed numpy array, id_map list,  #############################
    embs = np_str_to_array(df['emb'].values, l2_norm=True, mdim=200)
    id_map = {name: i for i, name in enumerate(df[colid].values)}
    log(",", str(embs)[:50], ",", str(id_map)[:50])

    #####  Keep only label infos  ####
    del df['emb']
    return embs, id_map, df



################################################################################################
def faiss_create_index(df_or_path=None, col='emb', dir_out="", db_type="IVF4096,Flat", nfile=1000, emb_dim=200):
        """
          1 billion size vector creation 
        """
        import faiss
        # nfile      = 1000
        emb_dim = 200

        if df_or_path is None:  df_or_path ="emb/erquet"
        dirout = "/".join(os.path.dirname(df_or_path).split("/")[:-1]) + "/faiss/"  # dir
        os.makedirs(dirout, exist_ok=True);
        log('dirout', dirout)
        log('dirin', df_or_path);
        time.sleep(10)

        if isinstance(df_or_path, str):
            flist = sorted(glob.glob(df_or_path))[:nfile]
            log('Loading', df_or_path)
            df = pd_read_file(flist, n_pool=20, verbose=False)
        else:
            df = df_or_path
        # df  = df.iloc[:9000, :]        
        log(df)

        tag = f"_" + str(len(df))
        df = df.sort_values('id')
        df['idx'] = np.arange(0, len(df))
        pd_to_file(df[['idx', 'id']].rename(columns={"id": 'item_tag_vran'}),
                   dirout + f"/map_idx{tag}.parquet", show=1)  #### Keeping maping faiss idx, item_tag

        log("### Convert parquet to numpy   ", dirout)
        X = np.zeros((len(df), emb_dim), dtype=np.float32)
        vv = df[col].values
        del df;
        gc.collect()
        for i, r in enumerate(vv):
            try:
                vi = [float(v) for v in r.split(',')]
                X[i, :] = vi
            except Exception as e:
                log(i, e)

        log("Preprocess X")
        faiss.normalize_L2(X)  ### Inplace L2 normalization
        log(X)

        nt = min(len(X), int(max(400000, len(X) * 0.075)))
        Xt = X[np.random.randint(len(X), size=nt), :]
        log('Nsample training', nt)

        ####################################################    
        D = emb_dim  ### actual  embedding size
        N = len(X)  # 1000000

        # Param of PQ for 1 billion
        M = 40  # 16  ###  200 / 5 = 40  The number of sub-vector. Typically this is 8, 16, 32, etc.
        nbits = 8  ### bits per sub-vector. This is typically 8, so that each sub-vec is encoded by 1 byte
        nlist = 6000  ###  # Param of IVF,  Number of cells (space partition). Typical value is sqrt(N)
        hnsw_m = 32  ###  # Param of HNSW Number of neighbors for HNSW. This is typically 32

        # Setup  distance -> similarity in uncompressed space is  dis = 2 - 2 * sim, https://github.com/facebookresearch/faiss/issues/632
        quantizer = faiss.IndexHNSWFlat(D, hnsw_m)
        index = faiss.IndexIVFPQ(quantizer, D, nlist, M, nbits)

        log('###### Train indexer')
        index.train(Xt)  # Train

        log('###### Add vectors')
        index.add(X)  # Add

        log('###### Test values ')
        index.nprobe = 8  # Runtime param. The number of cells that are visited for search.
        dists, ids = index.search(x=X[:3], k=4)  ## top4
        log(dists, ids)

        log("##### Save Index    ")
        dirout2 = dirout + f"/faiss_trained{tag}.index"
        log(dirout2)
        faiss.write_index(index, dirout2)
        return dirout2


def faiss_topk(df=None, root=None, colid='id', colemb='emb', faiss_index=None, topk=200, npool=1, nrows=10 ** 7,
               nfile=1000):  ##
    """ id, dist_list, id_list ex

       https://github.com/facebookresearch/faiss/issues/632

       This represents the quantization error for vectors inside the dataset.
        For vectors in denser areas of the space, the quantization error is lower because the quantization centroids are bigger and vice versa.
        Therefore, there is no limit to this error that is valid over the whole space. However, it is possible to recompute the exact distances once you have the nearest neighbors, by accessing the uncompressed vectors.

        distance -> similarity in uncompressed space is

        dis = 2 - 2 * sim

   """
    # nfile  = 1000      ; nrows= 10**7
    # topk   = 500

    if faiss_index is None:
        faiss_index = ""
        # index       = root + "/faiss/faiss_trained_1100.index"
        # faiss_index = root + "/faiss/faiss_trained_13311813.index"
        # faiss_index = root + "/faiss/faiss_trained_9808032.index"
    log('Faiss Index: ', faiss_index)
    if isinstance(faiss_index, str):
        faiss_path = faiss_index
        faiss_index = faiss_load_index(db_path=faiss_index)
    faiss_index.nprobe = 12  # Runtime param. The number of cells that are visited for search.

    ########################################################################
    if isinstance(df, list):  ### Multi processing part
        if len(df) < 1: return 1
        flist = df[0]
        root = os.path.abspath(os.path.dirname(flist[0] + "/../../"))  ### bug in multipro
        dirin = root + "/df/"
        dir_out = root + "/topk/"

    elif df is None:  ## Default
        # root =  dir_rec + "/emb/emb/ichiba_clk_202006_202012d_itemtagb_202009_12/seq_merge_2020_2021_pur/"
        root = dir_cpa2 + "/emb/emb/ichiba_order_20210901b_itemtagb2/seq_1000000000/"
        dirin = root + "/df/*.parquet"
        dir_out = root + "/topk/"
        flist = sorted(glob.glob(dirin))

    else:  ### df == string path
        root = os.path.abspath(os.path.dirname(df) + "/../")
        log(root)
        dirin = root + "/df/*.parquet"
        dir_out = root + "/topk/"
        flist = sorted(glob.glob(dirin))

    log('dir_in', dirin);
    log('dir_out', dir_out);
    time.sleep(2)
    flist = flist[:nfile]
    if len(flist) < 1: return 1
    log('Nfile', len(flist), flist)
    # return 1

    ####### Parallel Mode ################################################
    if npool > 1 and len(flist) > npool:
        log('Parallel mode')
        from utilmy.parallel import multiproc_run
        ll_list = multiproc_tochunk(flist, npool=npool)
        multiproc_run(faiss_topk, ll_list, npool, verbose=True, start_delay=5,
                      input_fixed={'faiss_index': faiss_path}, )
        return 1

    ####### Single Mode #################################################
    dirmap = faiss_path.replace("faiss_trained", "map_idx").replace(".index", '.parquet')
    map_idx_dict = db_load_dict(dirmap, colkey='idx', colval='item_tag_vran')

    chunk = 200000
    kk = 0
    os.makedirs(dir_out, exist_ok=True)
    dirout2 = dir_out
    flist = [t for t in flist if len(t) > 8]
    log('\n\nN Files', len(flist), str(flist)[-100:])
    for fi in flist:
        if os.path.isfile(dir_out + "/" + fi.split("/")[-1]): continue
        # nrows= 5000
        df = pd_read_file(fi, n_pool=1)
        df = df.iloc[:nrows, :]
        log(fi, df.shape)
        df = df.sort_values('id')

        dfall = pd.DataFrame();
        nchunk = int(len(df) // chunk)
        for i in range(0, nchunk + 1):
            if i * chunk >= len(df): break
            i2 = i + 1 if i < nchunk else 3 * (i + 1)

            x0 = np_str_to_array(df[colemb].iloc[i * chunk:(i2 * chunk)].values, l2_norm=True)
            log('X topk')
            topk_dist, topk_idx = faiss_index.search(x0, topk)
            log('X', topk_idx.shape)

            dfi = df.iloc[i * chunk:(i2 * chunk), :][[colid]]
            dfi[f'{colid}_list'] = np_matrix_to_str2(topk_idx, map_idx_dict)  ### to item_tag_vran
            # dfi[ f'dist_list']  = np_matrix_to_str( topk_dist )
            dfi[f'sim_list'] = np_matrix_to_str_sim(topk_dist)

            dfall = pd.concat((dfall, dfi))

        dirout2 = dir_out + "/" + fi.split("/")[-1]
        # log(dfall['id_list'])
        pd_to_file(dfall, dirout2, show=1)
        kk = kk + 1
        if kk == 1: dfall.iloc[:100, :].to_csv(dirout2.replace(".parquet", ".csv"), sep="\t")

    log('All finished')
    return os.path.dirname(dirout2)





####################################################################################################
if 'utils':
    def np_matrix_to_str2(m, map_dict):
        res = []
        for v in m:
            ss = ""
            for xi in v:
                ss += str(map_dict.get(xi, "")) + ","
            res.append(ss[:-1])
        return res


    def np_matrix_to_str(m):
        res = []
        for v in m:
            ss = ""
            for xi in v:
                ss += str(xi) + ","
            res.append(ss[:-1])
        return res


    def np_vector_to_str(m, sep=","):
        ss = ""
        for xi in m:
            ss += f"{xi}{sep}"
        return ss[:-1]


    def np_matrix_to_str_sim(m):  ### Simcore = 1 - 0.5 * dist**2
        res = []
        for v in m:
            ss = ""
            for di in v:
                ss += str(1 - 0.5 * di) + ","
            res.append(ss[:-1])
        return res


    def np_str_to_array(vv, l2_norm=True, mdim=200):
        ### Extract list into numpy
        # log(vv)
        # mdim = len(vv[0].split(","))
        # mdim = 200
        from sklearn import preprocessing
        import faiss
        X = np.zeros((len(vv), mdim), dtype='float32')
        for i, r in enumerate(vv):
            try:
                vi = [float(v) for v in r.split(',')]
                X[i, :] = vi
            except Exception as e:
                log(i, e)

        if l2_norm:
            # preprocessing.normalize(X, norm='l2', copy=False)
            faiss.normalize_L2(X)  ### Inplace L2 normalization
        log("Normalized X")
        return X


    def np_get_sample(lname, lproba=None, pnorm=None, k=5):
     if pnorm is None :
        pnorm = lproba / np.sum(lproba)

     ll = np.random.choice(lname, size=k,  p= pnorm )
     # ll = [ lname[0] for i in range(k) ]
     # log(ll)
     return ll


    def np_intersec(va, vb):
      return [  x  for x in va if x in set(vb) ]




###################################################################################################
if __name__ == "__main__":
    import fire ;
    fire.Fire()




