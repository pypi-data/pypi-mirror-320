# -*- coding: utf-8 -*-
""" Pandas utils
Doc::

    l1 = [1,2,3]
    l2 = [2,3,4]
    l  = np_list_intersection(l1,l2)
    assert len(l) == 2, "Intersection failed"

    l = np_add_remove(set(l1),[1,2],4)
    assert l == set([3,4]), "Add remove failed"

    to_timeunix(datex="2018-01-16")
    to_timeunix(datetime.datetime(2018,1,16))
    to_datetime("2018-01-16")
    from utilmy import os_makedirs
    os_makedirs("testdata/ppandas")

    df1 = pd_random(100)
    df2 = pd_random(100)
    df3 = pd.DataFrame({"a":[1,1,2,2,2]})
    df_str = pd.DataFrame({"a": ["A", "B", "B", "C", "C"],
                           "b": [1, 2, 3, 4, 5]})

    pd_plot_histogram(df1["a"],path_save="testdata/ppandas/histogram")

    pd_merge(df1, df2, on="b")

    df = pd_filter(df3, filter_dict="a>1")
    assert df.shape[0] == 3, "not filtered properly"

    pd_to_file(df1, "testdata/ppandas/file.csv")
    pd_sample_strat(df1, col="a", n=10)

    bins = pd_col_bins(df1, "a", 5)
    assert len(np.unique(bins)) == 5, "bins not formed"

    pd_dtype_reduce(df1)
    pd_dtype_count_unique(df1,col_continuous=['b'])

    df = pd_dtype_to_category(df_str, col_exclude=["b"], treshold=0.7)
    assert df.dtypes["a"] == "category", "Columns was not converted to category"

    pd_dtype_getcontinuous(df_str,cols_exclude=["a"])
    pd_add_noise(df1,level=0.01,cols_exclude=["a"])

    pd_cols_unique_count(df_str)
    pd_del(df_str,cols=["a"])

    # pd_plot_multi function needs to be fixed before writing test case
    # ax = m.pd_plot_multi(df1,plot_type='pair',cols_axe1=['a','b'])

    a = pd.DataFrame({"a":[1,2,3,4,5]})
    b = pd.DataFrame({"b":[1,2,3,4,5]})
    pd_cartesian(a,b)

    pd_show(df_str)


"""
import os, sys, time, datetime,inspect, json, yaml, gc, glob, pandas as pd, numpy as np

from utilmy.parallel import pd_read_file, pd_read_file2



###################################################################################
from utilmy.utilmy_base import log, log2, os_module_name
MNAME= os_module_name(__file__) 

def help():
    from utilmy import help_create
    ss = help_create(__file__) 
    print(ss)


###################################################################################
def test_all():
    test1()
    test2()
    test_pd_col_bins()
    test_pd_to_hiveparquet()


def test1():
    
    import utilmy as uu
    from utilmy import os_makedirs
    os_makedirs("testdata/ppandas")

    drepo, dirtmp = uu.dir_testinfo()

    df1 = pd_random(100)
    df2 = pd_random(100)
    df3 = pd.DataFrame({"a":[1,1,2,2,2]})
    df_str = pd.DataFrame({"a": ["A", "B", "B", "C", "C"],
                           "b": [1, 2, 3, 4, 5]})


    pd_plot_histogram(df1["a"],path_save="testdata/ppandas/histogram")
   
    pd_merge(df1, df2, on="b")

    log("####### pd_filter() ..")
    df = pd_filter(df3, filter_dict="a>1")
    assert df.shape[0] == 3, "not filtered properly"


    log( "####### pd_col_bins() ..")
    pd_to_file(df1, "testdata/ppandas/file.csv")
    pd_sample_strat(df1, col="a", n=10)

    ## you int64
    bins = pd_col_bins(df1, col="a", nbins= 5)
    assert len(np.unique(bins)) == 5, "bins not formed"

    log( "####### pd_dtype_to_category() ..")
    pd_dtype_reduce(df1)
    pd_dtype_count_unique(df1,col_continuous=['b'])

    df = pd_dtype_to_category(df_str, col_exclude=["b"], treshold=0.7)
    assert df.dtypes["a"] == "category", "Columns was not converted to category"

    pd_dtype_getcontinuous(df_str,cols_exclude=["a"])
    pd_add_noise(df1,level=0.01,cols_exclude=["a"])

    pd_cols_unique_count(df_str)
    pd_del(df_str,cols=["a"])

    # pd_plot_multi function needs to be fixed before writing test case
    # ax = m.pd_plot_multi(df1,plot_type='pair',cols_axe1=['a','b'])
    
    a = pd.DataFrame({"a":[1,2,3,4,5]})
    b = pd.DataFrame({"b":[1,2,3,4,5]})
    pd_cartesian(a,b)

    pd_show(df_str)

    log("####### pd_schema_enforce() ..")
    test_dictionary = dict(
        name=["Mathew", "sarah", "michael"], 
        age=[21, 21, 35],
    )   
    dataframe = pd.DataFrame(test_dictionary)
    previous_dtype = str(dataframe["age"].dtypes)
    log("Previous dtype:",previous_dtype)
    dtype1 = {
        "age":"string",
    }
    parsed_dataframe = pd_schema_enforce(df=dataframe,dtype_dict = dtype1)
    log("dtype now:", str(parsed_dataframe["age"].dtypes))
    assert str(parsed_dataframe["age"].dtypes) == "string", "Incorrect dtype"

    log("####### pd_to_mapdict() ..")
    test_dict = dict(
        name=["mathew", "sarah", "michael"], 
        age=[21, 21, 35]
    )
    expected_dict = dict(
        mathew=21,
        sarah=21,
        michael=35
    )
    df = pd.DataFrame(test_dict)
    result_dict = pd_to_mapdict(
        df=df,colkey="name",
        colval="age",
        colval_type="int"
    )
    assert result_dict == expected_dict, "The dictionaries aren't the same"
    
def test2():

    log( "####### np_list_intersection() ..")
    l1 = [1,2,3]
    l2 = [2,3,4]
    l  = np_list_intersection(l1,l2)
    assert len(l) == 2, "Intersection failed"


    log( "####### np_add_remove() ..")
    l = np_add_remove(set(l1),[1,2],4)
    assert l == set([3,4]), "Add remove failed"

    to_timeunix(datex="2018-01-16")
    to_timeunix(datetime.datetime(2018,1,16))
    to_datetime("2018-01-16")

def test_pd_col_bins():
    import utilmy as uu
    import pandas as pd
    import numpy as np

    log( "####### pd_col_bins() ..")
    np.random.seed(42)

    normal_col = np.random.normal(loc=666, scale=10, size=1000)
    geo_col = np.random.geometric(p=0.1, size=1000)
    df = pd.DataFrame({'norm': normal_col, 'geo': geo_col})

    binned_norm = uu.pd_col_bins(df, 'norm', 10)
    binned_geo = uu.pd_col_bins(df, 'geo', 10)

    assert len(binned_norm.unique()) == 10, "bins not formed for normal distribution"
    assert len(binned_geo.unique()) == 9, "bins not formed for geometric distribution"

def test_pd_to_hiveparquet():
    import utilmy as uu
    log("####### pd_to_hiveparquet() ..")

    drepo, dirtmp = uu.dir_testinfo()
    test_dictionary = dict(
        name=["Mathew", "sarah", "michael"], 
        age=[21, 21, 35]
    )
    test_dirout = dirtmp + "hiveparquet"
    dataframe = pd.DataFrame(test_dictionary)
    df = pd_to_hiveparquet(dirin=dataframe,dirout=test_dirout)
    parquet_path = test_dirout + "/part.0.parquet"
    parquet_df = pd.read_parquet(parquet_path)
    assert parquet_df.equals(df), "The dataframes aren't the same"

    data = uu.pd_getdata(False)

    dataframe = data['titanic.csv']
    test_dirout = drepo + 'temp/'
    df = pd_to_hiveparquet(dirin=dataframe,dirout=test_dirout)
    parquet_path = test_dirout + "/part.0.parquet"
    parquet_df = pd.read_parquet(parquet_path)
    assert parquet_df.equals(dataframe), "The dataframes aren't the same"
    # df = pd_to_hiveparquet(dirin=test_dirout,dirout=test_dirout+'2')
    # parquet_path = test_dirout +'2' + "/part.0.parquet"
    # parquet_df = pd.read_parquet(parquet_path)
    # assert parquet_df.equals(dataframe), "The dataframes aren't the same"

    dataframe = data['housing.csv']
    test_dirout = drepo + 'temp/'
    df = pd_to_hiveparquet(dirin=dataframe,dirout=test_dirout)
    parquet_path = test_dirout + "/part.0.parquet"
    parquet_df = pd.read_parquet(parquet_path)
    assert parquet_df.equals(dataframe), "The dataframes aren't the same"

    dataframe = data['stock_data.csv']
    test_dirout = drepo + 'temp/'
    df = pd_to_hiveparquet(dirin=dataframe,dirout=test_dirout)
    parquet_path = test_dirout + "/part.0.parquet"
    parquet_df = pd.read_parquet(parquet_path)
    assert parquet_df.equals(dataframe), "The dataframes aren't the same"

    dataframe = data['cars.csv']
    test_dirout = drepo + 'temp/'
    df = pd_to_hiveparquet(dirin=dataframe,dirout=test_dirout)
    parquet_path = test_dirout + "/part.0.parquet"
    parquet_df = pd.read_parquet(parquet_path)
    assert parquet_df.equals(dataframe), "The dataframes aren't the same"

    dataframe = data['sales.csv']
    test_dirout = drepo + 'temp/'
    df = pd_to_hiveparquet(dirin=dataframe,dirout=test_dirout)
    parquet_path = test_dirout + "/part.0.parquet"
    parquet_df = pd.read_parquet(parquet_path)
    assert parquet_df.equals(dataframe), "The dataframes aren't the same"

    dataframe = data['weatherdata.csv']
    test_dirout = drepo + 'temp/'
    df = pd_to_hiveparquet(dirin=dataframe,dirout=test_dirout)
    parquet_path = test_dirout + "/part.0.parquet"
    parquet_df = pd.read_parquet(parquet_path)
    assert parquet_df.equals(dataframe), "The dataframes aren't the same"



###################################################################################################
###### Pandas #####################################################################################
def pd_schema_enforce(df, int_default:int=0, dtype_dict:dict=None):
        """   dtype0= {'brand': 'int64',
                 'category': 'int64',
                 'chain': 'int64',
              }

            Docs::

                Args:
                    df (df or str)    : df or path to a file that can be loaded as a df(ex: CSV).
                    int_default (int) : number if data is an int, dtype_dict isn't given, and it can't be parsed to itself again. (Defaults to 0.)
                    dtype_dict (dict) : Contains the datatype of each column to parse.
                        Example
                            dtype1 = {
                                'name': 'string',
                                'age': 'int',
                            }
                Return: df with the parsed data.
                Example:
                    import pandas as pd
                    from utilmy import ppandas
                    test_dictionary = dict(
                        name=["Mathew", "Sarah", "Michael"], 
                        age=[21, 21, 35]
                    )
                    dataframe = pd.DataFrame(test_dictionary)
                    dtype = {
                        "age":"string",
                    }
                    parsed_dataframe = ppandas.pd_schema_enforce(dataframe)
                    print(str(parsed_dataframe["age"].dtypes)) # Displays string
        """
        if isinstance(df, str):
            df = pd_read_file(df)


        if dtype_dict is not None :
           return df.astype(dtype_dict)    


        def to_int(x):
            try : return int(x)
            except : return int_default

        for ci in df.columns :
            ss = str(df[ci].dtypes).lower()
            if 'object'  in ss:   df[ci] = df[ci].astype('str')  
            elif 'int64' in ss:   df[ci] = df[ci].apply( lambda x : to_int(x)) 
            elif 'float' in ss:   df[ci] = df[ci].apply( lambda x : float(x))
            elif 'int'   in ss:   df[ci] = df[ci].apply( lambda x : to_int(x)).astype('int32') 
        return df           

    

def pd_to_mapdict(df, colkey='ranid', colval='item_tag', naval='0', colkey_type='str', colval_type='str', npool=5, nrows=900900900, verbose=True):
    """function pd_to_mapdict.
        Load a Pandas Dataframe to a Dictionary.
        
    Docs::
            
        Args:
            df (df or str)             : pd, directory path with files, or a file path that can be loaded as a dataframe (ex: CSV).
            colkey (str)               : Column name that will be the key of the items. (Default to "ranid".)
            colval (str)               : Column name that will be the value of the items. (Default to "item_tag".)
            naval (str, int, or float) : Value for cells that don't have any value. (Default to "0".)  
            colkey_type (str)          : Data type of the column that will be the key of the itms. (Default to "str".)
            colval_type (str)          : Data type of the column that will be the value of the itms. (Default to "str".)
            npool (int)                : Number of workers that will be loading the dataframes. (Default to 5.)
            nrows (int)                : Number of rows to load in the df. (Default to 900900900.)
            verbose (bool)             : true to show logs. (Default to True.)  
        Returns: Dict.
        Example:
            import pandas as pd
            from utilmy import ppandas
            test_dictionary = dict(
                name=["Mathew", "sarah", "michael"], 
                age=[21, 21, 35]
            )
            dataframe = pd.DataFrame(test_dictionary)
            dictionary = ppandas.pd_to_mapdict(dataframe,colkey="name",colval="age")
            print(dictionary) #{'Mathew': '21', 'sarah': '21', 'michael': '35'}
    """
    ### load Pandas into key-val dict, for apply-map
    if isinstance(df, str):
       dirin = df
       log('loading', dirin)
       flist = glob.glob( dirin ) 
       df    = pd_read_file(flist, cols=[ colkey, colval  ], nrows=nrows,  n_pool=npool, verbose= verbose)

    if verbose: log( df, df.dtypes )
    #Cleaning data
    df = df.drop_duplicates(colkey)
    df = df.fillna(naval)    

    #colkey will be the key of each item of the dictionary
    df[colkey] = df[colkey].astype(colkey_type)
    #colval will be the value of each item of the dictionary
    df[colval] = df[colval].astype(colval_type)

    #The index will be the key of each item of the dictionary
    df = df.set_index(colkey)     
 
    df = df[[ colval ]].to_dict()
    df = df[colval] ### dict
    if verbose: log('Dict Loaded', len(df), str(df)[:100])
    return df


def pd_to_hiveparquet(dirin, dirout="/ztmp_hive_parquet/df.parquet", verbose=False):
    """  Hive parquet needs special headers to read, only fastparquet can do it.
    Doc::
            
                      fastparquet.write(filename, data, row_group_offsets=50000000, compression=None, file_scheme='simple', open_with=<built-in function open>, mkdirs=<function default_mkdirs>, has_nulls=True, write_index=None, partition_on=[], fixed_text=None, append=False, object_encoding='infer', times='int64', custom_metadata=None)[source]
    """
    import fastparquet as fp   
    from utilmy import glob_glob
    from utilmy import os_makedirs

    if isinstance(dirin, pd.DataFrame):
        
        fp.write(dirout, dirin, fixed_text=None, compression='SNAPPY', file_scheme='hive')    
        return dirin.iloc[:10, :]

    os_makedirs(dirout)
    dirout = "/".join( dirout.split("/")[-1] )

    flist = glob_glob(dirin, 10000)
    for fi in flist :
        df = fp.ParquetFile(flist )
        df = df.to_pandas()
        if verbose: log(df, df.dtypes)                
        dirouti = dirout + "/" + fi.split("/")[-1]    
        fp.write(dirouti, df, fixed_text=None, compression='SNAPPY', file_scheme='hive')       
    return df.iloc[:10, :]
    
    
def pd_random(nrows=100):
   """function pd_random.
   Doc::
           
          Args:
              nrows:   
          Returns:
              
   """
   df = pd.DataFrame(np.random.randint(0, 10, size=(nrows, 4)), 
                     columns=list('abcd'))
   return df 


def pd_merge(df1, df2, on=None, colkeep=None):
  """function pd_merge.
  Doc::
          
        Args:
            df1:   
            df2:   
            on:   
            colkeep:   
        Returns:
            
  """
  ### Faster merge
  cols = list(df2.columns) if colkeep is None else on + colkeep
  return df1.join( df2[ cols   ].set_index(on), on=on, how='left', rsuffix="2")


def pd_plot_multi(df, plot_type=None, cols_axe1:list=[], cols_axe2:list=[],figsize=(8,4), spacing=0.1, **kwargs):
    """function pd_plot_multi.
    Doc::
            
            Args:
                df:   
                plot_type:   
                cols_axe1 ( list ) :   
                cols_axe2 ( list ) :   
                figsize:   
                4:   
            Returns:
                
    """
    from pandas import plotting
    from pandas.plotting import _matplotlib
    from matplotlib import pyplot as plt


    plt.figure(figsize= figsize )
    # Get default color style from pandas - can be changed to any other color list
    if cols_axe1 is None: cols_axe1 = df.columns
    if len(cols_axe1) == 0: return
    
    # _get_standard_colors is not an attribute of _matplotlib this code might require some changes
    colors = getattr(getattr(plotting, '_matplotlib').style, '_get_standard_colors')(num_colors=len(cols_axe1 + cols_axe2))
    
    # Displays subplot's pair in case of plot_type defined as `pair`
    if plot_type=='pair':
        ax = df.plot(subplots=True, figsize=figsize, **kwargs)
        plt.show()
        return
    
    # First axis
    ax = df.loc[:, cols_axe1[0]].plot(label=cols_axe1[0], color=colors[0], **kwargs)
    ax.set_ylabel(ylabel=cols_axe1[0])
    ##  lines, labels = ax.get_legend_handles_labels()
    lines, labels = [], []

    i1 = len(cols_axe1)
    for n in range(1, len(cols_axe1)):
        df.loc[:, cols_axe1[n]].plot(ax=ax, label=cols_axe1[n], color=colors[(n) % len(colors)], **kwargs)
        line, label = ax.get_legend_handles_labels()
        lines  += line
        labels += label

    for n in range(0, len(cols_axe2)):
        ######### Multiple y-axes
        ax_new = ax.twinx()
        ax_new.spines['right'].set_position(('axes', 1 + spacing * (n - 1)))
        df.loc[:, cols_axe2[n]].plot(ax=ax_new, label=cols_axe2[n], color=colors[(i1 + n) % len(colors)], **kwargs)
        ax_new.set_ylabel(ylabel=cols_axe2[n])

        ######### Proper legend position
        line, label = ax_new.get_legend_handles_labels()
        lines += line
        labels += label

    ax.legend(lines, labels, loc=0)
    plt.show()
    return ax


def pd_plot_histogram(dfi, path_save=None, nbin=20.0, q5=0.005, q95=0.995, nsample= -1, show=False, clear=True) :
    """function pd_plot_histogram.
    Doc::
            
            Args:
                dfi:   
                path_save:   
                nbin:   
                q5:   
                q95:   
                nsample:   
                show:   
                clear:   
            Returns:
                
    """
    ### Plot histogram
    from matplotlib import pyplot as plt
    import numpy as np, os, time
    q0 = dfi.quantile(q5)
    q1 = dfi.quantile(q95)

    if nsample < 0 :
        dfi.hist( bins=np.arange( q0, q1,  (  q1 - q0 ) /nbin  ) )
    else :
        dfi.sample(n=nsample, replace=True ).hist( bins=np.arange( q0, q1,  (  q1 - q0 ) /nbin  ) )
    plt.title( path_save.split("/")[-1] )

    if show :
      plt.show()

    if path_save is not None :
      os.makedirs(os.path.dirname(path_save), exist_ok=True)
      plt.savefig( path_save )
      print(path_save )
    if clear :
        # time.sleep(5)
        plt.close()


def pd_filter(df, filter_dict="shop_id=11, l1_genre_id>600, l2_genre_id<80311," , verbose=False) :
    """.
    Doc::
            
             dfi = pd_filter2(dfa, "shop_id=11, l1_genre_id>600, l2_genre_id<80311," )
             dfi2 = pd_filter(dfa, {"shop_id" : 11} )
             ### Dilter dataframe with basic expr
    """
    #### Dict Filter
    if isinstance(filter_dict, dict) :
       for key,val in filter_dict.items() :
          df =   df[  (df[key] == val) ]
       return df

    # pd_filter(df,  ss="shop_id=11, l1_genre_id>600, l2_genre_id<80311," )
    ss = filter_dict.split(",")
    def x_convert(col, x):
      x_type = str( dict(df.dtypes)[col] )
      if "int" in x_type or "float" in x_type :
         return float(x)
      else :
          return x
    for x in ss :
       x = x.strip()
       if verbose : print(x)
       if len(x) < 3 : continue
       if "=" in x :
           coli= x.split("=")
           df = df[ df[coli[0]] == x_convert(coli[0] , coli[1] )   ]

       if ">" in x :
           coli= x.split(">")
           df = df[ df[coli[0]] > x_convert(coli[0] , coli[1] )   ]

       if "<" in x :
           coli= x.split("<")
           df = df[ df[coli[0]] < x_convert(coli[0] , coli[1] )   ]
    return df


def pd_to_file(df, filei,  check=0, verbose=True, show='shape', index=False, sep="\t",   **kw):
  """function pd_to_file.
  Doc::
          
        Args:
            df:   
            filei:   
            check:   
            verbose:   
            show:   
            **kw:   
        Returns:
            
  """
  import os, gc
  from pathlib import Path
  parent = Path(filei).parent
  os.makedirs(parent, exist_ok=True)
  ext  = os.path.splitext(filei)[1]
  if   ext == ".pkl" :       df.to_pickle(filei,  **kw)
  elif ext == ".parquet" :   df.to_parquet(filei, **kw)
  elif ext in [".csv" ,".txt"] :  
    df.to_csv(filei, index=False, sep=sep, **kw)       

  elif ext in [".json" ] :  
    df.to_json(filei, **kw)       

  else :
      log('No Extension, using parquet')
      df.to_parquet(filei + ".parquet", **kw)

  if verbose in [True, 1] :  log(filei)        
  if show == 'shape':        log(df.shape)
  if show in [1, True] :     log(df)
     
  if check in [1, True, "check"] : log('Exist', os.path.isfile(filei))
  #  os_file_check( filei )

  # elif check =="checkfull" :
  #  os_file_check( filei )
  #  dfi = pd_read_file( filei, n_pool=1)   ### Full integrity
  #  log("#######  Reload Check: ",  filei, "\n"  ,  dfi.tail(3).T)
  #  del dfi; gc.collect()
  gc.collect()


def pd_sample_strat(df, col, n):
  """function pd_sample_strat.
  Doc::
          
        Args:
            df:   
            col:   
            n:   
        Returns:
            
  """
  ### Stratified sampling
  # n   = min(n, df[col].value_counts().min())
  df_ = df.groupby(col).apply(lambda x: x.sample(n = n, replace=True))
  df_.index = df_.index.droplevel(0)
  return df_


def pd_cartesian(df1, df2) :
  """function pd_cartesian.
  Doc::
          
        Args:
            df1:   
            df2:   
        Returns:
            
  """
  ### Cartesian preoduct
  import pandas as pd
  col1 =  list(df1.columns)
  col2 =  list(df2.columns)
  df1['xxx'] = 1
  df2['xxx'] = 1
  df3 = pd.merge(df1, df2,on='xxx')[ col1 + col2 ]
  try:
        del df3['xxx']
  except:pass

  return df3


def pd_col_bins(df, col: str, nbins: int = 5):
  """Shortcut for easy binning of numerical values.
  Doc::

    np.random.seed(42)

    normal_col = np.random.normal(loc=666, scale=10, size=1000)
    geo_col = np.random.geometric(p=0.1, size=1000)
    df = pd.DataFrame({'norm': normal_col, 'geo': geo_col})

    binned_norm = uu.pd_col_bins(df, 'norm', 10)
    binned_geo = uu.pd_col_bins(df, 'geo', 10)

    assert len(binned_norm.unique()) == 10, "bins are not formed for normal distribution"
    assert len(binned_geo.unique()) == 9, "bins are not formed for geometric distribution"

    Args:
        df (pandas.DataFrame):   The dataframe.
        col (str):    The name of the column for cutting. Column should be of numeric type.
        nbins (int):  The number of bins (default 5).

    Returns:
        pandas.Series of type int16.
  """
  import pandas as pd
  # assert nbins < 256, 'nbins< 255'
  return pd.qcut(df[col], q=nbins, labels=False, duplicates='drop').astype('int16')


def pd_colcat_toint(dfref, colname, colcat_map=None, suffix=None):

    ### to ensure dataframe
    colname = [colname] if isinstance(colname, str) else colname

    df = dfref[colname]
    # if colname is single value df will be series type not a dataframe so we convert it to dataframe to be sure it is a dataframe type
    df = pd.DataFrame(df)

    suffix = "" if suffix is None else suffix
    colname_new = []

    if colcat_map is not None:
        for col in colname:
            print(col, col + suffix)
            ddict            = colcat_map[col]["encode"]
            # print(ddict)
            df[col + suffix] = df[col].apply(lambda x: ddict.get(x))
            colname_new.append(col + suffix)

        return df[colname_new], colcat_map

    colcat_map = {}
    
    # old: for col in colname:
    # update: for col in [colname] >> if colname is just single value it will loop through string not the list, so we convert to list before looping
    for col in colname:
        
        colcat_map[col]           = {}
        df[col + suffix], label   = df[col].factorize()
        colcat_map[col]["decode"] = {i: t for i, t in enumerate(list(label))}
        colcat_map[col]["encode"] = {t: i for i, t in enumerate(list(label))}
        colname_new.append(col + suffix)

    return df[colname_new], colcat_map



def pd_dtype_reduce(dfm, int0 ='int32', float0 = 'float32') :
    """ Reduce dtype.
    Doc::
            
        
        
    """
    import numpy as np
    for c in dfm.columns :
        if dfm[c].dtype ==  np.dtype(np.int32) :       dfm[c] = dfm[c].astype( int0 )
        elif   dfm[c].dtype ==  np.dtype(np.int64) :   dfm[c] = dfm[c].astype( int0 )
        elif dfm[c].dtype ==  np.dtype(np.float64) :   dfm[c] = dfm[c].astype( float0 )
    return dfm


def pd_dtype_count_unique(df, col_continuous=[]):
    """Learns the number of categories in each variable and standardizes the data..
    Doc::
            
                ----------
                data: pd.DataFrame
                continuous_ids: list of ints
                    List containing the indices of known continuous variables. Useful for
                    discrete data like age, which is better modeled as continuous.
                Returns
                -------
                ncat:  number of categories of each variable. -1 if the variable is  continuous.
    """
    import numpy as np
    def gef_is_continuous(data, dtype):
        """ Returns true if data was sampled from a continuous variables, and false
        """
        if str(dtype) == "object":
            return False

        observed = data[~np.isnan(data)]  # not consider missing values for this.
        rules = [np.min(observed) < 0,
                 np.sum((observed) != np.round(observed)) > 0,
                 len(np.unique(observed)) > min(30, len(observed)/3)]
        if any(rules):
            return True
        else:
            return False

    cols = list(df.columns)
    ncat = {}

    for coli in cols:
        is_cont = gef_is_continuous( df[coli].sample( n=min(3000, len(df)) ).values , dtype = df[coli].dtype )
        if coli in col_continuous or is_cont:
            ncat[coli] =  -1
        else:
            ncat[coli] =  len( df[coli].unique() )
    return ncat


def pd_dtype_to_category(df, col_exclude, treshold=0.5):
  """.
  Doc::
          
          Convert string to category
  """
  import pandas as pd
  if isinstance(df, pd.DataFrame):
    for col in df.select_dtypes(include=['object']):
        if col not in col_exclude :
            num_unique_values = len(df[col].unique())
            num_total_values  = len(df[col])
            if float(num_unique_values) / num_total_values < treshold:
                df[col] = df[col].astype('category')
        else:
            df[col] = pd.to_datetime(df[col])
    return df
  else:
    print("Not dataframe")


def pd_dtype_getcontinuous(df, cols_exclude:list=[], nsample=-1) :
    """function pd_dtype_getcontinuous.
    Doc::
            
            Args:
                df:   
                cols_exclude ( list ) :   
                nsample:   
            Returns:
                
    """
    ### Return continuous variable
    clist = {}
    for ci in df.columns :
        ctype   = df[ci].dtype
        if nsample == -1 :
            nunique = len(df[ci].unique())
        else :
            nunique = len(df.sample(n= nsample, replace=True)[ci].unique())
        if 'float' in  str(ctype) and ci not in cols_exclude and nunique > 5 :
           clist[ci] = 1
        else :
           clist[ci] = nunique
    return clist


def pd_del(df, cols:list):
    """function pd_del.
    Doc::
            
            Args:
                df:   
                cols ( list ) :   
            Returns:
                
    """
    ### Delete columns without errors
    for col in cols :
        try:
            del df[col]
        except : pass
    return df


def pd_add_noise(df, level=0.05, cols_exclude:list=[]) :
    """function pd_add_noise.
    Doc::
            
            Args:
                df:   
                level:   
                cols_exclude ( list ) :   
            Returns:
                
    """
    import numpy as np, pandas as pd
    df2 = pd.DataFrame()
    colsnum = pd_dtype_getcontinuous(df, cols_exclude)
    for ci in df.columns :
        if ci in colsnum :
           print(f'adding noise {ci}')
           sigma = level * (df[ci].quantile(0.95) - df[ci].quantile(0.05)  )
           df2[ci] = df[ci] + np.random.normal(0.0, sigma, [len(df)])
        else :
           df2[ci] = df[ci]
    return df2


def pd_cols_unique_count(df, cols_exclude:list=[], nsample=-1) :
    """function pd_cols_unique_count.
    Doc::
            
            Args:
                df:   
                cols_exclude ( list ) :   
                nsample:   
            Returns:
                
    """
    ### Return cadinat=lity
    clist = {}
    for ci in df.columns :
        ctype   = df[ci].dtype
        if nsample == -1 :
            nunique = len(df[ci].unique())
        else :
            nunique = len(df.sample(n= nsample, replace=True)[ci].unique())

        if 'float' in  str(ctype) and ci not in cols_exclude and nunique > 5 :
           clist[ci] = 0
        else :
           clist[ci] = nunique

    return clist


def pd_show(df, nrows=100, reader='notepad.exe', **kw):
    """ Show from Dataframe.
    Doc::
            
    """
    import pandas as pd
    from utilmy import os_makedirs
    fpath = 'ztmp/ztmp_dataframe.csv'
    os_makedirs(fpath)
    df.iloc[:nrows,:].to_csv(fpath, sep=",", mode='w')






###########################################################################################################
class dict_to_namespace(object):
    #### Dict to namespace
    def __init__(self, d):
        """ dict_to_namespace:__init__.
        Doc::
                
                    Args:
                        d:     
                    Returns:
                       
        """
        self.__dict__ = d


def to_dict(**kw):
  """function to_dict.
  Doc::
          
        Args:
            **kw:   
        Returns:
            
  """
  ## return dict version of the params
  return kw


def to_timeunix(datex="2018-01-16"):
  """function to_timeunix.
  Doc::
          
        Args:
            datex:   
        Returns:
            
  """
  if isinstance(datex, str)  :
     return int(time.mktime(datetime.datetime.strptime(datex, "%Y-%m-%d").timetuple()) * 1000)

  if isinstance(datex, datetime.datetime)  :
     return int(time.mktime( datex.timetuple()) * 1000)


def to_datetime(x) :
  """function to_datetime.
  Doc::
          
        Args:
            x:   
        Returns:
            
  """
  import pandas as pd
  return pd.to_datetime( str(x) )


def np_list_intersection(l1, l2) :
  """function np_list_intersection.
  Doc::
          
        Args:
            l1:   
            l2:   
        Returns:
            
  """
  return [x for x in l1 if x in l2]


def np_add_remove(set_, to_remove, to_add):
    """function np_add_remove.
    Doc::
            
            Args:
                set_:   
                to_remove:   
                to_add:   
            Returns:
                
    """
    # a function that removes list of elements and adds an element from a set
    result_temp = set_.copy()
    for element in to_remove:
        result_temp.remove(element)
    result_temp.add(to_add)
    return result_temp


def to_float(x):
    """function to_float.
    Doc::
            
            Args:
                x:   
            Returns:
                
    """
    try :
        return float(x)
    except :
        return float("NaN")


def to_int(x):
    """function to_int.
    Doc::
            
            Args:
                x:   
            Returns:
                
    """
    try :
        return int(x)
    except :
        return float("NaN")


def is_int(x):
    """function is_int.
    Doc::
            
            Args:
                x:   
            Returns:
                
    """
    try :
        int(x)
        return True
    except :
        return False    

def is_float(x):
    """function is_float.
    Doc::
            
            Args:
                x:   
            Returns:
                
    """
    try :
        float(x)
        return True
    except :
        return False   




########################################################################################################






###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()




