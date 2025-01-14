"""Hadoop, hive related.
Doc:

    sspark  spark_config_check

    HDFS command
    cat: Copies source paths to stdout.
    Usage: hdfs dfs -cat URI [URI ?]

    Example:
        hdfs dfs -cat hdfs://<path>/file1
        hdfs dfs -cat file:///file2 /user/hadoop/file3

    chgrp: Changes the group association of files. With -R, makes the change recursively by way of path structure. The user must be the file owner or the superuser.
    Usage: hdfs dfs -chgrp [-R] GROUP URI [URI ?]

    chmod: Changes the permissions of files. With -R, makes the change recursively by way of path structure. The user must be the file owner or the superuser
    Usage: hdfs dfs -chmod [-R] <MODE[,MODE]? | OCTALMODE> URI [URI ?]
    Example: hdfs dfs -chmod 777 test/data1.txt

    chown: Changes the owner of files. With -R, makes the change recursively by way of path structure. The user must be the superuser.
    Usage: hdfs dfs -chown [-R] [OWNER][:[GROUP]] URI [URI ]
    Example: hdfs dfs -chown -R hduser2 /opt/hadoop/logs

    copyFromLocal: Works similarly to the put command, except that the source is restricted to a local file reference.
    Usage: hdfs dfs -copyFromLocal <localsrc> URI
    Example: hdfs dfs -copyFromLocal input/docs/data2.txt hdfs://localhost/user/rosemary/data2.txt

    copyToLocal: Works similarly to the get command, except that the destination is restricted to a local file reference.
    Usage: hdfs dfs -copyToLocal [-ignorecrc] [-crc] URI <localdst>
    Example: hdfs dfs -copyToLocal data2.txt data2.copy.txt

    count: Counts the number of directories, files, and bytes under the paths that match the specified file pattern.
    Usage: hdfs dfs -count [-q] <paths>
    Example: hdfs dfs -count hdfs://nn1.example.com/file1 hdfs://nn2.example.com/file2

    cp: Copies one or more files from a specified source to a specified destination. If you specify multiple sources, the specified destination must be a directory.
    Usage: hdfs dfs -cp URI [URI ?] <dest>
    Example: hdfs dfs -cp /user/hadoop/file1 /user/hadoop/file2 /user/hadoop/dir

    du: Displays the size of the specified file, or the sizes of files and directories that are contained in the specified directory. If you specify the -s option, displays an aggregate summary of file sizes rather than individual file sizes. If you specify the -h option, formats the file sizes in a �ghuman-readable�h way.
    Usage: hdfs dfs -du [-s] [-h] URI [URI ?]
    Example: hdfs dfs -du /user/hadoop/dir1 /user/hadoop/file1

    dus: Displays a summary of file sizes; equivalent to hdfs dfs -du ?s.
    Usage: hdfs dfs -dus <args>

    expunge: Empties the trash. When you delete a file, it isn�ft removed immediately from HDFS, but is renamed to a file in the /trash directory. As long as the file remains there, you can undelete it if you change your mind, though only the latest copy of the deleted file can be restored.
    Usage: hdfs dfs ?expunge

    get: Copies files to the local file system. Files that fail a cyclic redundancy check (CRC) can still be copied if you specify the ?ignorecrc option. The CRC is a common technique for detecting data transmission errors. CRC checksum files have the .crc extension and are used to verify the data integrity of another file. These files are copied if you specify the -crc option.
    Usage: hdfs dfs -get [-ignorecrc] [-crc] <src> <localdst>
    Example: hdfs dfs -get /user/hadoop/file3 localfile

    getmerge: Concatenates the files in src and writes the result to the specified local destination file. To add a newline character at the end of each file, specify the addnl option.
    Usage: hdfs dfs -getmerge <src> <localdst> [addnl]
    Example: hdfs dfs -getmerge /user/hadoop/mydir/ ~/result_file addnl

    ls: Returns statistics for the specified files or directories.
    Usage: hdfs dfs -ls <args>
    Example: hdfs dfs -ls /user/hadoop/file1

    lsr: Serves as the recursive version of ls; similar to the Unix command ls -R.
    Usage: hdfs dfs -lsr <args>
    Example: hdfs dfs -lsr /user/hadoop

    mkdir: Creates directories on one or more specified paths. Its behavior is similar to the Unix mkdir -p command, which creates all directories that lead up to the specified directory if they don�ft exist already.
    Usage: hdfs dfs -mkdir <paths>
    Example: hdfs dfs -mkdir /user/hadoop/dir5/temp

    moveFromLocal: Works similarly to the put command, except that the source is deleted after it is copied.
    Usage: hdfs dfs -moveFromLocal <localsrc> <dest>
    Example: hdfs dfs -moveFromLocal localfile1 localfile2 /user/hadoop/hadoopdir

    mv: Moves one or more files from a specified source to a specified destination. If you specify multiple sources, the specified destination must be a directory. Moving files across file systems isn�ft permitted.
    Usage: hdfs dfs -mv URI [URI ?] <dest>
    Example: hdfs dfs -mv /user/hadoop/file1 /user/hadoop/file2

    put: Copies files from the local file system to the destination file system. This command can also read input from stdin and write to the destination file system.
    Usage: hdfs dfs -put <localsrc> ? <dest>
    Example: hdfs dfs -put localfile1 localfile2 /user/hadoop/hadoopdir; hdfs dfs -put ? /user/hadoop/hadoopdir (reads input from stdin)


    rm: Deletes one or more specified files. This command doesn�ft delete empty directories or files. To bypass the trash (if it�fs enabled) and delete the specified files immediately, specify the -skipTrash option.
    Usage: hdfs dfs -rm [-skipTrash] URI [URI ?]
    Example: hdfs dfs -rm hdfs://nn.example.com/file9
    
    rmr: Serves as the recursive version of ?rm.
    Usage: hdfs dfs -rmr [-skipTrash] URI [URI ?]
    Example: hdfs dfs -rmr /user/hadoop/dir

    setrep: Changes the replication factor for a specified file or directory. With ?R, makes the change recursively by way of path structure.
    Usage: hdfs dfs -setrep <rep> [-R] <path>

    Example: hdfs dfs -setrep 3 -R /user/hadoop/dir1
    stat: Displays information about the specified path.

    Usage: hdfs dfs -stat URI [URI ?]
    Example: hdfs dfs -stat /user/hadoop/dir1
    tail: Displays the last kilobyte of a specified file to stdout. The syntax supports the Unix -f option, which enables the specified file to be monitored. As new lines are added to the file by another process, tail updates the display.

    Usage: hdfs dfs -tail [-f] URI
    Example: hdfs dfs -tail /user/hadoop/dir1

    test: Returns attributes of the specified file or directory. Specifies ?e to determine whether the file or directory exists; -z to determine whether the file or directory is empty; and -d to determine whether the URI is a directory.
    Usage: hdfs dfs -test -[ezd] URI
    Example: hdfs dfs -test /user/hadoop/dir1

    text: Outputs a specified source file in text format. Valid input file formats are zip and TextRecordInputStream.
    Usage: hdfs dfs -text <src>
    Example: hdfs dfs -text /user/hadoop/file8.zip  

    touchz: Creates a new, empty file of size 0 in the specified path.
    Usage: hdfs dfs -touchz <path>
    Example: hdfs dfs -touchz /user/hadoop/file12  

"""
import os,sys, subprocess, time, datetime, glob
import pandas as pd
from box import Box

def log(*s):
    print(*s, flush=True)



################################################################################################################
def hadoop_print_config(dirout=None):
  """ Print configuration variable for Hadoop, Spark

  """
  names =[
    'SPARK_HOME',
    'HADOOP_HOME'


  ]

  dd= []
  for ni in names:
    dd.append( [ni, os.environ.get(ni, '') ] )



###############################################################################################################
def glob_filter(flist, path_pattern):
    """  Filter flist  by path pattern

    """
    plist = path_pattern.split("*")

    flist2 =[]
    for fi in flist :
       flag= True
       for pi in plist :
          if  pi not in fi:
             flag= False
             break
       if flag :
          flist2.append(fi)

    return flist2



def hdfs_ls(path, flag="-h ", filename_only=False, use_regex=False, match_file=''):
    """
        flag=-R
        if use_regex == True
            1) can search for specific files using star *
            2) downloading files with specific patterns

    """
    import subprocess,re

    if "*" in path :
       root = path.split("*")[0]
       root = "/".join( root.split("/")[:-1] )
    else :
       root = path

    if use_regex:
        files = str(subprocess.check_output('hdfs dfs -ls -R ' + root, shell=True))
        flist_full_address = [re.search(' (/.+)', i).group(1) for i in str(files).split("\\n") if re.search(' (/.+)', i)]
        if match_file:
            return glob_filter(files, match_file)
        return flist_full_address 

    process = subprocess.Popen(f"hdfs dfs -ls {flag} '{root}'", shell=True, stdout= subprocess.PIPE, stderr=subprocess.PIPE)
    std_out, std_err = process.communicate()

    if filename_only:
       list_of_file_names = [fn.split(' ')[-1].split('/')[-1] for fn in std_out.decode().split('\n')[1:]][:-1]
       return list_of_file_names

    flist_full_address = [fn.split(' ')[-1] for fn in std_out.decode().split('\n')[1:]][:-1]
    return flist_full_address


     
def hdfs_mkdir(hdfs_dir):
    res = os_system( f"hdfs dfs -mkdir -p  '{hdfs_dir}' ", doprint=True)


def hdfs_copy_fromlocal(local_dir, hdfs_dir, overwrite=False):
    if overwrite: hdfs_dir_rm(hdfs_dir)
    res = os_system( f"hdfs dfs -copyFromLocal '{local_dir}'  '{hdfs_dir}' ", doprint=True)


def hdfs_copy_tolocal(hdfs_dir, local_dir):
    res = os_system( f"hdfs dfs -copyToLocal '{hdfs_dir}'  '{local_dir}' ", doprint=True)


def hdfs_dir_rm(path):
    if hdfs_dir_exists(path):
        log("removing old file "+path)
        cat = subprocess.call(["hdfs", "dfs", "-rm", path ])


def hdfs_dir_exists(path):
    return {0: True, 1: False}[subprocess.call(["hadoop", "fs", "-test", "-f", path ])]


def hdfs_file_exists(filename):
    ''' Return True when indicated file exists on HDFS.
    '''
    proc = subprocess.Popen(['hadoop', 'fs', '-test', '-e', filename])
    proc.communicate()

    if proc.returncode == 0:
        return True
    else:
        return False


def hdfs_dir_list(path,recursive=False):
    subprocess.call(["hdfs", "dfs", "-ls","-R", path]) if recursive else subprocess.call(["hdfs", "dfs", "-ls",path])


def hdfs_dir_info(path):
    """  HDFS DIR : {"last_modified":last_modified,"format":format1 'size'}


    """
    fdict = Box({})

    cmd_ls = f"hdfs dfs -ls {path}"
    stdout,stderr = os_system(cmd_ls, True)
    if stderr: return stderr
    lines = stdout.split("\n")
    for li in lines:
        if not li: continue
        tmp = []
        for v in li.split(" "):
            if v: tmp.append(v.strip())

            if len(tmp) < 8: continue
            k = tmp[-1].split("/")[-1]
            last_modified = " ".join(tmp[5:7])
            format1       = k.split(".")[-1] if "." in k else ""
            fdict[k] = {"last_modified":last_modified,"format":format1}


    cmd_du = f"hdfs dfs -du {path}"
    stdout,stderr = os_system(cmd_du, True)
    if stderr: return stderr
    lines = stdout.split("\n")
    for li in lines:
        if not li: continue
        tmp = []
        for v in li.split(" "):
            if v: tmp.append(v.strip())

            if len(tmp) < 3: continue
            k = tmp[-1].split("/")[-1]
            size_bytes = tmp[0]
            if k in fdict:
                fdict[k]["size"] = int(size_bytes)
            else:
                fdict[k]["size"] = -1

    return fdict

### alias   
hdfs_dir_stats = hdfs_dir_info


def hdfs_download(dirin="", dirout="./", verbose=False, n_pool=1, **kw):
    """  Donwload files in parallel using pyarrow
    Doc::

        path_glob: list of HDFS pattern, or sep by ";"
        :return:
    """
    import glob, gc,os
    from multiprocessing.pool import ThreadPool

    def log(*s, **kw):
        log(*s, flush=True, **kw)

    #### File ############################################
    import pyarrow as pa
    hdfs  = pa.hdfs.connect()
    flist = [t for t in hdfs.ls(dirin)]

    def fun_async(x):
        hdfs.download(x[0], x[1])


    ######################################################
    file_list = sorted(list(set(flist)))
    n_file    = len(file_list)
    if verbose: log(file_list)

    #### Pool count
    if   n_pool < 1  :  n_pool = 1
    if   n_file <= 0 :  m_job  = 0
    elif n_file <= 2 :
        m_job  = n_file
        n_pool = 1
    else  :
        m_job  = 1 + n_file // n_pool  if n_file >= 3 else 1
    if verbose : log(n_file,  n_file // n_pool )

    pool   = ThreadPool(processes=n_pool)

    res_list=[]
    for j in range(0, m_job ) :
        if verbose : log("Pool", j, end=",")
        job_list = []
        for i in range(n_pool):
            if n_pool*j + i >= n_file  : break
            filei = file_list[n_pool*j + i]

            xi    = (filei, dirout + "/" + filei.split("/")[-1])

            job_list.append( pool.apply_async(fun_async, (xi, )))
            if verbose : log(j, filei)

        for i in range(n_pool):
            if i >= len(job_list): break
            res_list.append( job_list[ i].get() )


    pool.close()
    pool.join()
    pool = None
    if m_job>0 and verbose : log(n_file, j * n_file//n_pool )
    return res_list

 



############################################################################################################### 
###############################################################################################################
def hive_get_tablelist(dbname):
    """Get Hive tables from database_name
    """
    cmd = f"hive -e 'show tables from {dbname}'"
    stdout,stderr = os_system(cmd)
    if stderr: return stderr
    lines = stdout.split("\n")
    ltable = []
    for li in lines :
        if not li: continue
        if 'tab_name' in li : continue
        ltable.append(li.strip())
    return ltable

def hive_get_dblist():
    """ Get  databases
    """
    cmd = f"hive -e  'show databases '"
    stdout,stderr = os_system(cmd)
    if stderr: return stderr
    lines = stdout.split("\n")
    ldb = []
    for li in lines :
        if not li: continue
        if 'database_name' in li : continue
        ldb.append(li.strip())
    return ldb



def hive_get_tablechema(tablename):
    """Get  databases
    """
    cmd = f"hive -e 'describe {tablename}'"
    stdout,stderr = os_system(cmd)
    if stderr: return stderr
    lines = stdout.split("\n")
    table_info = {}
    for li in lines :
        if not li: continue
        if 'col_name' in li : continue
        tmp = []
        for item in li.split(" "): # assume li = "id   int   comment '' "
            if item:
                tmp.append(item)
        col_name = item[0]
        data_type = item[1]
        comment = item[2] if len(item)>=3 else ""
        table_info[col_name] = {"data_type": data_type, "comment": comment}
    return table_info



def hive_get_tabledetails(table):
    """
    Doc::
    describe formatted table
    """
    cmd = f"hive -e 'describe formatted {table}'"
    stdout,stderr = os_system(cmd)
    if stderr: return stderr
    lines = stdout.split("\n")
    table_info = {}
    ltable = []
    for li in lines :
        if not li: continue
        if 'col_name' in li : continue
        ltable.append(li.strip())
    return ltable



def hive_get_tablelist(dbname):
    """Get Hive tables from database_name
    """
    cmd = f"hive -e 'show tables from {dbname}'"
    stdout,stderr = os_system(cmd)
    if stderr: return stderr
    lines = stdout.split("\n")
    ltable = []
    for li in lines :
        if not li: continue
        if 'tab_name' in li : continue
        ltable.append(li.strip())
    return ltable



def hive_db_dumpall():
    cmd = 'dump all db, table schema on disk'








#####################################################################################
def hdfs_put2(from_dir="", to_dir="",  verbose=True, n_pool=25, dirlevel=50,  **kw):
    """
     hdfs_put LocalFile into HDFS in multi-thread
    from_dir = "hdfs://nameservice1/user/
    to_dir   = "data/"

    """
    import glob, gc,os, time, pyarrow as pa
    from multiprocessing.pool import ThreadPool

    def log(*s, **kw):
      print(*s, flush=True)

    #### File ############################################
    hdfs      = pa.hdfs.connect()
    hdfs.mkdir(to_dir  )

    from utilmy import os_walk
    dd = os_walk(from_dir, dirlevel= dirlevel, pattern="*")
    fdirs, file_list = dd['dir'], dd['file']
    file_list = sorted(list(set(file_list)))
    n_file    = len(file_list)
    log('Files', n_file)

    file_list2 = []
    for i, filei in enumerate(file_list) :
        file_list2.append( (filei,   to_dir + filei.replace(from_dir,"")   )  )


    ##### Create Target dirs  ###########################
    fdirs = [ t.replace(from_dir,"") for t in fdirs]
    for di in fdirs :
        hdfs.mkdir(to_dir + "/" + di )

    #### Input xi #######################################
    xi_list = [ []  for t in range(n_pool) ]
    for i, xi in enumerate(file_list2) :
        jj = i % n_pool
        xi_list[jj].append( xi )

    #### function #######################################
    def fun_async(xlist):
      for x in xlist :
         try :
           with open(x[0], mode='rb') as f:
                hdfs.upload(x[1], f,)
         except :
            try :
               time.sleep(60)
               with open(x[0], mode='rb') as f:
                  hdfs.upload(x[1], f,)
            except : print('error', x[1])

    #### Pool execute ###################################
    pool     = ThreadPool(processes=n_pool)
    job_list = []
    for i in range(n_pool):
         job_list.append( pool.apply_async(fun_async, (xi_list[i], )))
         if verbose : log(i, xi_list[i] )

    res_list = []
    for i in range(n_pool):
        if i >= len(job_list): break
        res_list.append( job_list[ i].get() )
        log(i, 'job finished')


    pool.terminate() ; pool.join()  ;  pool = None
    log('n_processed', len(res_list) )




def hdfs_walk(path="hdfs://nameservice1/user/", dirlevel=3, hdfs=None):   ### python  prepro.py hdfs_walk
    import pyarrow as pa
    hdfs = pa.hdfs.connect() if hdfs is None else hdfs
    path = "hdfs://nameservice1/" + path if 'hdfs://' not in path else path

    def os_walk(fdirs):
        flist3 = []
        for diri  in fdirs :
            flist3.extend( [ t for t in hdfs.ls(diri) ]  )
        fdirs3 = [ t   for t in flist3 if hdfs.isdir(t) ]
        return flist3, fdirs3

    flist0, fdirs0   = os_walk([path])
    fdirs = fdirs0
    for i in range(dirlevel):
       flisti, fdiri = os_walk(fdirs)
       flist0 =  list(set(flist0  + flisti ))
       fdirs0 =  list(set(fdirs0  + fdiri ))
       fdirs  = fdiri
    return {'file': flist0, 'dir': fdirs0}



def hdfs_get2(from_dir="", to_dir="",  verbose=True, n_pool=20,   **kw):
    """
    import fastcounter
    counter = fastcounter.FastWriteCounter,()
    counter.increment(1)
    cnt.value
    """
    import glob, gc,os, time
    from multiprocessing.pool import ThreadPool

    def log(*s, **kw):
      print(*s, flush=True, **kw)

    #### File ############################################
    os.makedirs(to_dir, exist_ok=True)
    import pyarrow as pa
    hdfs      = pa.hdfs.connect()
    # file_list = [ t for t in hdfs.ls(from_dir) ]
    file_list = hdfs_walk(from_dir, dirlevel=10)['file']


    def fun_async(xlist):
      for x in xlist :
         try :
            hdfs.download(x[0], x[1])
            # ktot = ktot + 1   ### Not thread safe
         except :
            try :
               time.sleep(60)
               hdfs.download(x[0], x[1])
               # ktot = ktot + 1
            except : pass

    ######################################################
    file_list = sorted(list(set(file_list)))
    n_file    = len(file_list)
    log('Files', n_file)
    if verbose: log(file_list)

    xi_list = [ []  for t in range(n_pool) ]
    for i, filei in enumerate(file_list) :
        jj = i % n_pool
        xi_list[jj].append( (filei,   to_dir + "/" + filei.split("/")[-1]   )  )

    #### Pool count
    pool     = ThreadPool(processes=n_pool)
    job_list = []
    for i in range(n_pool):
         job_list.append( pool.apply_async(fun_async, (xi_list[i], )))
         if verbose : log(i, xi_list[i] )

    res_list = []
    for i in range(n_pool):
        if i >= len(job_list): break
        res_list.append( job_list[ i].get() )
        log(i, 'job finished')

    pool.terminate()  ;  pool.join()  ; pool = None
    log('n_processed', len(res_list) )
    log('n files', len(os.listdir(to_dir)) )





############################################################################################################### 
############################################################################################################### 
def pd_read_parquet_schema(uri: str) -> pd.DataFrame:
    """Return a Pandas dataframe corresponding to the schema of a local URI of a parquet file.

    The returned dataframe has the columns: column, pa_dtype
    """
    import pandas as pd, pyarrow.parquet
    # Ref: https://stackoverflow.com/a/64288036/
    schema = pyarrow.parquet.read_schema(uri, memory_map=True)
    schema = pd.DataFrame(({"column": name, "pa_dtype": str(pa_dtype)} for name, pa_dtype in zip(schema.names, schema.types)))
    schema = schema.reindex(columns=["column", "pa_dtype"], fill_value=pd.NA)  # Ensures columns in case the parquet file has an empty dataframe.
    return schema


def pd_read_parquet_hdfs(dirlist=None, ignore_index=True,  cols=None, verbose=False, nrows=-1, concat_sort=True, n_pool=1,
                      drop_duplicates=None, col_filter=None,  col_filter_val=None, dtype=None,  **kw)->pd.DataFrame:
  """  Read file in parallel from HDFS : very Fast
  Doc::

    Require: export CLASSPATH=`$HADOOP_HOME/bin/hdfs classpath --glob`

    dirin = "hdfs:///mypat/myparquet/"
    df = pd_read_csv_hdfs(dirlist=dirin, nfile=5000, n_pool=8, dirlevel=1, ignore_index=True,  cols=None, verbose=False, nrows=-1, concat_sort=True,
            drop_duplicates=None, col_filter=None,  col_filter_val=None, dtype=None)

  """
  import glob, gc,  pandas as pd, os
  import pyarrow as pa, gc,  pyarrow.parquet as pq
  def log(*s, **kw):
      log(*s, flush=True, **kw)

  log( "connect to HDFS" )
  try: hdfs = pa.hdfs.connect()
  except Exception as e:
     log(e, "\n,Require: export CLASSPATH=`$HADOOP_HOME/bin/hdfs classpath --glob`" ) ; 1/0


  def pd_reader_obj(fi, cols=None, **kw):
      try :
        table = pq.read_table(fi, columns=cols)
        df1   = table.to_pandas()
        # timestamp_as_object=True,
        # date_as_object= True ,
        # safe = False,
        # split_blocks =True, self_destruct=True)
        return df1
      except Exception as e:
        log( e)
        return None

  #### File  ################################
  dirlist   = dirlist.split(";") if isinstance(dirlist, str)  else dirlist
  file_list = []
  for fi in dirlist :
    log(fi)
    file_list.append( hdfs.ls(fi))

  file_list = sorted(list(set(file_list)))
  n_file    = len(file_list)
  if verbose: log(file_list)

  #### Pool count  ##########################
  from multiprocessing.pool import ThreadPool
  if n_pool < 1 :  n_pool = 1
  if n_file <= 0:  m_job  = 0
  elif n_file <= 2:
    m_job  = n_file
    n_pool = 1
  else  :
    m_job  = 1 + n_file // n_pool  if n_file >= 3 else 1
  if verbose : log(n_file,  n_file // n_pool )

  pool   = ThreadPool(processes=n_pool)
  dfall  = pd.DataFrame()
  for j in range(0, m_job ) :
      if verbose : log("Pool", j, end=",")
      job_list = []
      for i in range(n_pool):
         if n_pool*j + i >= n_file  : break
         filei         = file_list[n_pool*j + i]

         ### TODO : use with kewyword arguments
         job_list.append( pool.apply_async(pd_reader_obj, (filei, )))
         log(j, filei)

      for i in range(n_pool):
        if i >= len(job_list): break
        dfi   = job_list[ i].get()

        if dfi is None : continue

        if col_filter is not None : dfi = dfi[ dfi[col_filter] == col_filter_val ]
        if cols is not None :       dfi = dfi[cols]
        if nrows > 0        :       dfi = dfi.iloc[:nrows,:]
        if drop_duplicates is not None  : dfi = dfi.drop_duplicates(drop_duplicates)
        gc.collect()

        dfall = pd.concat( (dfall, dfi), ignore_index=ignore_index, sort= concat_sort)
        #log("Len", n_pool*j + i, len(dfall))
        del dfi; gc.collect()

  pool.terminate() ; pool.join()  ; pool = None
  if m_job>0 and verbose : log(n_file, j * n_file//n_pool )
  return dfall



def pd_read_csv_hdfs(dirlist=None, dirlevel=1, ignore_index=True,  cols=None, verbose=False, nfile=10000, nrows=-1, concat_sort=False, n_pool=1,
                      drop_duplicates=None, col_filter=None,  col_filter_val=None, dtype=None, 
                      compression='gzip', encoding='utf-8', sep=',', header=None, on_bad_lines='skip', 
                     **kw)->pd.DataFrame:
      """  Read file in parallel from HDFS using pyarrow
      Docs:

            Require: export CLASSPATH=`$HADOOP_HOME/bin/hdfs classpath --glob`

            dirin = "hdfs:///mypat/"
            df = pd_read_csv_hdfs(dirlist=dirin, nfile=5000, n_pool=8, dirlevel=1, ignore_index=True,  cols=None, verbose=False, nrows=-1, ,
                    drop_duplicates=None, col_filter=None,  col_filter_val=None, dtype=None)
      
      """
      import glob, gc,  pandas as pd, os, copy
      import pyarrow as pa, gc,  pyarrow.csv as pq
      def log(*s, **kw):
          log(*s, flush=True, **kw)

      log( "pd_read_file_hdfs" )
      hdfs = pa.hdfs.connect()

      def pd_reader_obj(fi, cols=None, **kw):
          try :
            with hdfs.open(fi) as fi2:
              dfi = pd.read_csv(fi2, encoding= encoding,compression= compression, names=cols, sep=sep,
                                on_bad_lines=on_bad_lines, header=header, dtype=dtype)


            if col_filter is not None : dfi = dfi[ dfi[col_filter] == col_filter_val ]
            if cols is not None :       dfi = dfi[cols]
            if nrows > 0        :       dfi = dfi.iloc[:nrows,:]
            if drop_duplicates is not None  : dfi = dfi.drop_duplicates(drop_duplicates)

            return dfi
          except Exception as e:
            log( e)
            return None

      #### File  ################################
      dirlist   = dirlist.split(";") if isinstance(dirlist, str)  else dirlist

      flist = dirlist
      for i in range(0, dirlevel):
        flist2 = []
        for fi in flist[:] :
          log(fi)
          flist2 = flist2 + hdfs.ls(fi)
        flist = copy.deepcopy(flist2)
        if len(flist) > nfile  : break

      flist = [ fi for fi in flist if "." in fi.split("/")[-1] ]  ### only .csv.gz files
      flist = sorted(list(set(flist)))
      flist = flist[:nfile] if nfile>0 else flist
      n_file    = len(flist)
      log('Nfile', n_file)
      if verbose: log(flist)
      # return flist

      #### Pool count  ##########################
      from multiprocessing.pool import ThreadPool
      if n_pool < 1 :  n_pool = 1
      if n_file <= 0:  return pd.DataFrame()
      elif n_file <= 2:
        m_job  = n_file
        n_pool = 1
      else  :
        m_job  = 1 + n_file // n_pool  if n_file >= 3 else 1
      if verbose : log(n_file,  n_file // n_pool )

      pool   = ThreadPool(processes=n_pool)
      dfall  = pd.DataFrame()
      for j in range(0, m_job ) :
          if verbose : log("Pool", j, end=",")
          job_list = []
          for i in range(n_pool):
             if n_pool*j + i >= n_file  : break
             filei         = flist[n_pool*j + i]

             ### TODO : use with kewyword arguments
             job_list.append( pool.apply_async(pd_reader_obj, (filei, )))
             if (j+100) % 100 == 0 : log(j, filei)

          for i in range(n_pool):
            if i >= len(job_list): break
            dfi   = job_list[ i].get()

            if dfi is None : continue

            if col_filter is not None : dfi = dfi[ dfi[col_filter] == col_filter_val ]
            if cols is not None :       dfi = dfi[cols]
            if nrows > 0        :       dfi = dfi.iloc[:nrows,:]
            if drop_duplicates is not None  : dfi = dfi.drop_duplicates(drop_duplicates)
            gc.collect()

            dfall = pd.concat( (dfall, dfi), ignore_index=ignore_index, sort= concat_sort)
            #log("Len", n_pool*j + i, len(dfall))
            del dfi; gc.collect()

      pool.terminate() ; pool.join()  ; pool = None
      if m_job>0 and verbose : log(n_file, j * n_file//n_pool )
      return dfall



def pd_read_json_hdfs(dirlist=None, ignore_index=True,  cols=None, verbose=False, nfile=10000, nrows=-1,
                      concat_sort=False, n_pool=1,   drop_duplicates=None, col_filter=None,  col_filter_val=None,
                      dtype=None, compression='gzip', encoding='utf-8', sep=',', header=None, on_bad_lines='skip', dirlevel=1,
                     **kw):
      """  Read file in parallel from HDFS : very Fast
      Docs::
      
          dir_list: list of pattern, or sep by ";"
         return:
      
      pip install python-snappy   ### hadoop snappy compressed
      from snappy.hadoop_snappy import StreamDecompressor
      
      """
      import gc, pandas as pd  
      def log(*s, **kw):
          print(*s, flush=True, **kw)

      log( "pd_read_file_hdfs" )
      hdfs = pa.hdfs.connect()

      def pd_reader_obj(fi, cols=None, **kw):
          try :
            if ".snappy" in fi:
                from snappy.hadoop_snappy import StreamDecompressor
                from io import BytesIO
                with hdfs.open(fi) as fi2:
                    bio = BytesIO(StreamDecompressor().decompress(fi2.read()))
                    dfi = pd.read_json(bio, lines=True, compression='infer')
            else :                                    
                with hdfs.open(fi) as fi2:
                    dfi = pd.read_json(fi2,lines=True,compression= compression)


            if col_filter is not None : dfi = dfi[ dfi[col_filter] == col_filter_val ]
            if cols is not None :       dfi = dfi[cols]
            if nrows > 0        :       dfi = dfi.iloc[:nrows,:]
            if drop_duplicates is not None  : dfi = dfi.drop_duplicates(drop_duplicates)

            return dfi
          except Exception as e:
            log( e)
            return None

      #### File  ################################
      dirlist   = dirlist.split(";") if isinstance(dirlist, str)  else dirlist

      flist = dirlist
      for i in range(0, dirlevel):
        flist2 = []
        for fi in flist[:] :
          log(fi)
          flist2 = flist2 + hdfs.ls(fi)
        flist = copy.deepcopy(flist2)
        if len(flist) > nfile  : break

      flist = [ fi for fi in flist if "." in fi.split("/")[-1] ]  ### only .csv.gz files
      flist = sorted(list(set(flist)))
      flist = flist[:nfile] if nfile>0 else flist
      n_file    = len(flist)
      log('Nfile', n_file)
      if verbose: log(flist)


      #### Pool count  ##########################
      from multiprocessing.pool import ThreadPool
      if n_pool < 1 :  n_pool = 1
      if n_file <= 0:  return pd.DataFrame()
      elif n_file <= 2:
        m_job  = n_file
        n_pool = 1
      else  :
        m_job  = 1 + n_file // n_pool  if n_file >= 3 else 1
      if verbose : log(n_file,  n_file // n_pool )

      pool   = ThreadPool(processes=n_pool)
      dfall  = pd.DataFrame()
      for j in range(0, m_job ) :
          if verbose : print("Pool", j, end=",")
          job_list = []
          for i in range(n_pool):
             if n_pool*j + i >= n_file  : break
             filei         = flist[n_pool*j + i]

             ### TODO : use with kewyword arguments
             job_list.append( pool.apply_async(pd_reader_obj, (filei, )))
             if (j+100) % 100 == 0 : log(j, filei)

          for i in range(n_pool):
            if i >= len(job_list): break
            dfi   = job_list[ i].get()

            if dfi is None : continue

            if col_filter is not None : dfi = dfi[ dfi[col_filter] == col_filter_val ]
            if cols is not None :       dfi = dfi[cols]
            if nrows > 0        :       dfi = dfi.iloc[:nrows,:]
            if drop_duplicates is not None  : dfi = dfi.drop_duplicates(drop_duplicates)
            gc.collect()

            dfall = pd.concat( (dfall, dfi), ignore_index=ignore_index, sort= concat_sort)
            #log("Len", n_pool*j + i, len(dfall))
            del dfi; gc.collect()

      pool.terminate() ; pool.join()  ; pool = None
      if m_job>0 and verbose : log(n_file, j * n_file//n_pool )
      return dfall




def pd_write_parquet_hdfs(df, hdfs_dir=  'hdfs:///user/pppp/clean_v01.parquet/', 
                 cols=None,n_rows=1000, partition_cols=None, overwrite=True, verbose=1, ) :
    """Pandas to HDFS
    Doc::

      pyarrow.parquet.write_table(table, where, row_group_size=None, version='1.0', use_dictionary=True, compression='snappy', write_statistics=True, use_deprecated_int96_timestamps=None, coerce_timestamps=None, allow_truncated_timestamps=False, data_page_size=None, flavor=None, filesystem=None, compression_level=None, use_byte_stream_split=False, data_page_version='1.0', **kwargs)
      
      https://arrow.apache.org/docs/python/generated/pyarrow.parquet.write_to_dataset.html#pyarrow.parquet.write_to_dataset
       
    """
    import pyarrow as pa
    import pyarrow.parquet as pq
    hdfs = pa.hdfs.connect()    
    n_rows = 999999999 if n_rows < 0  else n_rows
    df = df.iloc[:n_rows, :]
    
    table = pa.Table.from_pandas(df)
    
    if overwrite :
        hdfs.rm(hdfs_dir.replace("hdfs://", ""), recursive=True)
    hdfs.mkdir(hdfs_dir.replace("hdfs://", ""))
    pq.write_to_dataset(table, root_dir=hdfs_dir,
                        partition_cols=partition_cols, filesystem=hdfs)
    
    flist = hdfs.ls( hdfs_dir )  
    log(flist)



hdfs_pd_write_parquet =  pd_write_parquet_hdfs   
hdfs_pd_read_parquet  =  pd_read_parquet_hdfs 
hdfs_pd_read_csv      =  pd_read_csv_hdfs 





############################################################################################################### 
############################################################################################################### 
hive_header_template =  '''
        set  hive.vectorized.execution.enabled = true;  set hive.vectorized.execution.reduce.enabled = true;
        set  hive.execution.engine=tez; set  hive.cli.print.header=true;    
        set mapreduce.fileoutputcommitter.algorithm.version=2;
        set hive.exec.parallel=true;  set hive.metastore.try.direct.sql=true;   set hive.metastore.client.socket.timeout=90000;

        -- Speed up writing
        set mapreduce.fileoutputcommitter.algorithm.version=2;

        -- duplicate column names
        set hive.support.quoted.identifiers=none;

        set  hive.auto.convert.join=true;
        set  hive.mapjoin.smalltable.filesize= 990000000;
        SET  hive.optimize.skewjoin=true;


        -- Cost based Optimization
        set hive.cbo.enable=true;
        set hive.compute.query.using.stats=true;
        set hive.stats.fetch.column.stats=true;
        set hive.stats.fetch.partition.stats=true;


        -- Default Value: 20 in Hive 0.7 through 0.13.1; 600 in Hive 0.14.0 and later
        -- Added In: Hive 0.7.0; default changed in Hive 0.14.0 with HIVE-7140


        --  Container RAM ####################################################
        SET hive.tez.container.size=5856;
        SET hive.tez.java.opts=-Xmx4096m;

        set mapreduce.map.memory.mb=4096;
        SET mapreduce.map.java.opts=-Xmx3096m;

        set mapreduce.reduce.memory.mb=4096;
        SET mapreduce.reduce.java.opts=-Xmx3096m;


        -- Impact the number of nodes used for Map - Reduce : Low --> high number of reducers ############
        -- set hive.exec.reducers.bytes.per.reducer=512000000 ;
        set hive.exec.reducers.bytes.per.reducer=512100100 ;

        SET mapred.max.split.size=512100100 ; 
        SET mapred.min.split.size=128100100 ; 


        -- JAR SERDE

        
    '''.replace("    ", "")   ### Otherwise Hive queries failed



def hive_run(query, logdir="ztmp/loghive/", tag='v01', 
             dry=1,       ### only fake run 
             nohup=0,     ### background
             explain=0):  ### Explain query
    """ HIVE SQL RUN    
    Doc::

            cfg = Box(ConfigReader.from_yaml(config))
            logdir   = cfg.log_hive      
            start_dt = date_now('now', add_days= -1-30, fmt='%Y-%m-%d') if len(start_dt) < 7 else start_dt
            end_dt   = date_now('now', add_days= -1,    fmt='%Y-%m-%d') if len(end_dt)   < 7 else end_dt
            
            cv_start_dt = date_now('now', add_days= -1-120, fmt='%Y-%m-%d')


            qq = os_file_read('queries/myhive.sql')
            qq = qq.format(start_dt=start_dt, end_dt=end_dt,  )
            hive_run(qq, dry=1, logdir= logdir, tag=tag, explain=1)
        
    """
    # query =  header_sql0  + "\n" +  query  ### Default works well
    query = query_clean(query)

    if explain>0:
        for key in [  'CREATE ', 'INSERT '  ]:
          if key in query.upper() :  query = query.replace(key, "EXPLAIN "+key)        

        for key in [ 'DROP ', 'ALTER ',   ]:
          if key in query.upper() :  query = query.replace(key, "-- "+key)      
            
    tag2     = f"{tag}_" + str( int(time.time()) )
    hivefile = f"{logdir}/hiveql_{tag2}.sql"
    os.makedirs(os.path.dirname( os.path.abspath(hivefile)), exist_ok=True)
    with open (hivefile, mode='w') as fp :
        fp.write(query)


    logfile = f"{logdir}/hiveql_{tag2}_log.py"  
    with open(logfile, mode='a') as f:
        f.write(hivefile)
        f.write("\n\n\n\n###################################################################")
        f.write(query + "\n########################" )      

    cmd = f"hive -f {hivefile} >> {logfile})   "
    log(query, "\n\nCMD: ", cmd)

    if dry == 1 :
      return None


    if nohup > 0:
       os.system( f" nohup 2>&1   hive -f {hivefile} >> {logfile}   & " )
    else :
       os.system( f" hive -f {hivefile} >> {logfile}       " )

    log('finish')   



def hive_exec(query="", nohup:int=1, dry=False, end0=None, with_exception=False):
        """  

        """

        if with_exception:
            return_code, stdout, stderr = os_subprocess(['hive'] +  ['-e', query_clean_quote(query)])
            if return_code == 0 :
                log('query %s is updated with message %s', query, stdout)
            else:
                raise Exception('Error for hive query :{} code: {}, stdout: {}, stderr: {}'.format(query, return_code, stdout, stderr))
            return True

        hiveql = "./zhiveql_tmp.sql"
        log(query)    
        log(hiveql, flush=True) 

        with open(hiveql, mode='w') as f:
            f.write(query)      

        with open("nohup.out", mode='a') as f:
            f.write("\n\n\n\n###################################################################")
            f.write(query + "\n########################" )      

        if nohup > 0:
           os.system( f" nohup 2>&1   hive -f {hiveql}    & " )
        else :
           os.system( f" hive -f {hiveql}      " )        
        log('finish')   



def query_clean(q):
    q2    = ""
    qlist = q.split("\n")
    for x in qlist:
        if    x.startswith("    ") : q2 = q2 + x[4:].strip() + "\n"
        elif  x.startswith("   ") :  q2 = q2 + x[3:].strip() + "\n"
        elif  x.startswith("  ") :   q2 = q2 + x[2:].strip() + "\n"
        else : q2 = q2 + x + "\n"
    return q2



def query_clean_quote(query):
    return '"{}"'.format(query)



def hive_update_partitions_table( hr, dt, location, table_name):
    log('Updating latest partition location in {table_name} table'.format(table_name=table_name))
    drop_partition_query = f"ALTER TABLE {table_name} DROP IF EXISTS PARTITION (dt='{dt}', hr={hr})"
    add_partition_query  = f"ALTER TABLE {table_name} ADD PARTITION (dt='{dt}', hr={hr}) location '{location}'"
    hive_exec(drop_partition_query,args=['--hiveconf', 'hive.mapred.mode=unstrict'], with_exception=True )
    hive_exec(add_partition_query, args=['--hiveconf', 'hive.mapred.mode=unstrict'], with_exception=True)
    log(f'Updating latest partition location in {table_name} table completed successfully')



def hive_get_partitions(url="", user="myuser_hadoop",  table='mydb.mytable', dirout="myexport/" ):
    """Export Hive partition names on disk
     get_partitions


    """
    if "hdfs:" in url :
        fname = url.split("/")[-1].replace(".", "_")
        logfile  = dirout + f"/dt_{fname}.txt"
        cmd      = f"hadoop dfs -ls {url} |& tee -a    {logfile}"
        out,err  = os_system( cmd)
        return

    dbname, table = table.split(".")[0], table.split(".")[1]
    logfile  = f"ztmp/dt_{dbname}-{table}.txt"
    cmd      = f"hadoop dfs -ls hdfs://nameservice1/user/{user}/warehouse/{dbname}.db/{table}   |& tee -a    {logfile}"
    out,err  = os_system( cmd, doprint=True)



def hive_df_tohive(df, tableref="nono2.table2") :
    """ Export Dataframe to Hive table

    """
    ttable = tableref.replace(".", "_")
    ptmp   = "ztmp/ztmp_hive/" + ttable + "/"
    os.system("rm -rf " + ptmp )
    os.makedirs(ptmp, exist_ok=True )
    df.to_csv( ptmp + ttable + ".csv" , index=False, sep="\t")
    hive_csv_tohive( ptmp, tablename= tableref, tableref= tableref)



def hive_csv_tohive(folder, tablename="ztmp", tableref="nono2.table2"):
    """ Local CSV to Hive table

    """
    log("loading to hive ", tableref)
    try:
        hiveql   = "ztmp/hive_upload.sql"
        csvtable = tablename # + "_csv"
        foldr    = folder if folder[-1] == "/" else folder + "/"
        with open(hiveql, mode='w') as f:
            f.write( "DROP TABLE IF EXISTS {};\n".format(csvtable))
            f.write( "CREATE TABLE {0} ( ip STRING) ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde' WITH SERDEPROPERTIES ('separatorChar' = '\t') STORED AS TEXTFILE TBLPROPERTIES('skip.header.line.count' = '1');\n".format(csvtable))
            f.write( "LOAD DATA LOCAL INPATH '{}*.csv' OVERWRITE INTO TABLE {};\n".format( foldr, csvtable))

        log(hiveql)
        os.system("hive -f " + hiveql)
        log('finish')

    except Exception as e:
        log(e)



def hive_sql_todf(sql, header_hive_sql:str='', verbose=1, save_dir=None, **kwargs):
    """  Load SQL Query result to pandas dataframe


    """
    import subprocess, os, pandas as pd
    from collections import defaultdict
    sid = str(hash( str(sql) ))

    with open(header_hive_sql, mode='r') as fp:
        header_sql = fp.readlines()
    header_sql = "".join(header_sql)  + "\n"

    sql2 = header_sql + sql
    file1 = "ztmp/hive_receive.sql"
    with open( file1, 'w') as f1:
        f1.write(sql2)

    if verbose > 0 : log(sql2)

    cmd    = ["hive", '-f',  file1]
    result = subprocess.check_output(cmd)
    if verbose >= 1 : log( str(result)[:100] , len(result))
    n = len(result)

    try:
        result = result.decode("utf-8")  # bytes to string
        twod_list = [line.split('\t') for line in result.strip().split('\n')]
        columns = map(lambda x: x.split('.')[1] if '.' in x else x,
                      twod_list[0])

        # rename duplicated columns
        column_cnt = defaultdict(int)
        renamed_column = []
        for column in columns:
            column_cnt[column] += 1
            if column_cnt[column] > 1:
                renamed_column.append(column + '_' + str(column_cnt[column]))
            else:
                renamed_column.append(column)

        df = pd.DataFrame(twod_list[1:], columns=renamed_column)

        if save_dir is not None :
           fname = f'ztmp/hive_result/{sid}/'
           os.makedirs(os.path.dirname(fname), exist_ok=True)
           df.to_parquet( fname + '/table.parquet' )
           open(fname +'/sql.txt', mode='w').write(sql2)
           log('saved',  fname)

        log('hive table', df.columns, df.shape)
        return df

    except Exception as e:
        log(e)

 



###############################################################################################################
########## Hive parquet #######################################################################################
def parquet_to_hive_parquet(dirin=None, table=None, dirout=None):   ##  
    """  Need Pyarrow 3.0 to make it work.
            hive 1.2

            CREATE EXTERNAL TABLE n=st (
            siid   ,
            )
            STORED AS PARQUET TBLPROPERTIES ("parquet.compression"="SNAPPY")   ;


            hadoop dfs -put  /a/adigd_ranid_v15_140m_fast.parquet   /usload/


            hive -e "LOAD DATA LOCAL INPATH   '/us40m_fast.parquet'  OVERWRITE INTO TABLE  n  ;"

    """

    dirin2 = dirin if ".parquet" in dirin else dirin + "/*"
    log(dirin2, table)


    ########################################################################################################
    scheme = ""
    df, dirouti, fi = parquet_to_hive_parquet2(dirin2, dirout=dirout, nfile=1, verbose=True)
    scheme      = hive_schema(df)
    log(dirouti)

    log('\n ################# Creating hive table')
    ss= f"""  CREATE EXTERNAL TABLE {table} ( 
                {scheme} 
                ) 
                STORED AS PARQUET TBLPROPERTIES ("parquet.compression"="SNAPPY")   ;        
    """
    log(ss)
    to_file(ss, 'ztmp_hive_sql.sql', mode='w' )
    os_system('hive -f "ztmp_hive_sql.sql" ')


    log('\n ################# Metadata to Hive ')
    ss = f""" SET mapred.input.dir.recursive=true; SET hive.mapred.supports.subdirectories=true ;            
                LOAD DATA LOCAL INPATH   '{dirouti}'  OVERWRITE INTO TABLE  {table}   ;  describe   {table}  ;              
    """
    to_file(ss, 'ztmp_hive_sql.sql', mode='w' )
    os_system(  'hive -f "ztmp_hive_sql.sql" ')


def parquet_to_hive_parquet2(dirin, dirout="/ztmp_hive_parquet/", nfile=1, verbose=False):
    """  Hive parquet needs special headers  NEED PYARROW 3.0  for Hive compatibility
            Bug in fastparquet, cannot save float, int.,
    """
    import fastparquet as fp
    if isinstance(dirin, pd.DataFrame):
        fp.write(dirout, dirin, fixed_text=None, compression='SNAPPY', file_scheme='hive')
        return dirin.iloc[:10, :]

    flist = glob.glob(dirin)  ### only 1 file is for Meta-Data
    fi    = flist[-1]
    df    = pd.read_parquet( fi  )
    df    = df.iloc[:100, :]   ### Prevent RAM overflow
    if verbose: log(df, df.dtypes)

    # df = pd_schema_enforce_hive(df, int_default=0, dtype_dict = None)

    # df['p'] = 0

    df= df.rename(columns={ 'timestamp': 'timestamp1' })

    for c in df.columns :
        if c in ['shop_id', 'item_id', 'campaign_id', 'timekey'] :
            df[c] = df[c].astype('int64')
        else :
            df[c] = df[c].astype('str')


    os.system( f" rm -rf  {dirout}  ")
    os_makedirs(dirout)
    dirouti = dirout + "/" + fi.split("/")[-1]
    log('Exporting on disk', dirouti)
    fp.write(dirouti, df.iloc[:100,:], fixed_text=None, compression='SNAPPY', file_scheme='hive')


    ### Bug in Fastparquet with float, need to delete and replace by original files
    os.remove( f"{dirouti}/part.0.parquet"  )

    ### Replace by pyarrow 3.0
    df.to_parquet( f"{dirouti}/part.0.parquet"  )

    #### Need to KEEP ONE Parquet File, otherwise it creates issues
    dirout2 = dirouti +  '/' + fi.split("/")[-1]
    cmd = f"cp  {fi}    '{dirout2}' "
    # os_system( cmd   )

    return df.iloc[:10, :], dirouti, fi.split("/")[-1]


def hive_schema(df):
    if isinstance(df, str):
        df = pd_read_parquet_schema(df)

    tt = ""
    for ci in df.columns :
        ss = str(df[ci].dtypes).lower()
        if 'object'  in ss:   tt = tt +  f"{ci} STRING ,\n"
        elif 'int64' in ss:   tt = tt +  f"{ci} BIGINT ,\n"
        elif 'float' in ss:   tt = tt +  f"{ci} DOUBLE ,\n"
        elif 'int'   in ss:   tt = tt +  f"{ci} INT ,\n"
    #log(tt[:-2])
    return tt[:-2]







###############################################################################################################
###############################################################################################################
def os_rename_parquet(dir0=None):   ## py rename
        import glob
        flist  = []

        if dir0 is not None :
            flist = flist + glob.glob( dir0 + "/*"  )

        flist += sorted( list(set(glob.glob( dir0 + "/**/*" ))) )
        flist += sorted( list(set(glob.glob( dir0 + "/*/*/*" ))) )

        log(len(flist))
        for fi in flist :
            fend = fi.split("/")[-1]
            if ".sh" in fend or ".py"  in fend or "COPY" in fend :
                continue

            if  '.parquet' in fend    : continue
            if not os.path.isfile(fi) : continue

            if '.' not in fend:
                try :
                    log(fi)
                    os.rename(fi, fi + ".parquet")
                except Exception as e :
                    log(e)


def to_file(txt, dirout, mode='a'):
    with open(dirout, mode=mode) as fp:
        fp.write(txt)


def os_makedirs(path:str):
  """function os_makedirs in HDFS or local
  """
  if 'hdfs:' not in path :
    os.makedirs(path, exist_ok=True)
  else :
    os.system(f"hdfs dfs mkdir -p '{path}'")


def os_system(cmd, doprint=False):
    """ os.system  and retrurn stdout, stderr values
    """
    import subprocess
    try :
        p          = subprocess.run( cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, )
        mout, merr = p.stdout.decode('utf-8'), p.stderr.decode('utf-8')
        if doprint:
            l = mout  if len(merr) < 1 else mout + "\n\nbash_error:\n" + merr
            log(l)

        return mout, merr
    except Exception as e :
        log( f"Error {cmd}, {e}")


def date_format(datestr:str="", fmt="%Y%m%d", add_days=0, add_hours=0, timezone='Asia/Tokyo', fmt_input="%Y-%m-%d", 
                returnval='str,int,datetime'):
    """ One liner for date Formatter
    Doc::

        datestr: 2012-02-12  or ""  emptry string for today's date.
        fmt:     output format # "%Y-%m-%d %H:%M:%S %Z%z"

        date_format(timezone='Asia/Tokyo')    -->  "20200519" 
        date_format(timezone='Asia/Tokyo', fmt='%Y-%m-%d')    -->  "2020-05-19" 
        date_format(timezone='Asia/Tokyo', fmt='%Y%m%d', add_days=-1, returnval='int')    -->  20200518 


    """
    from pytz import timezone as tzone
    import datetime

    if len(str(datestr )) >7 :  ## Not None
        now_utc = datetime.datetime.strptime( str(datestr), fmt_input)       
    else:
        now_utc = datetime.datetime.now(tzone('UTC'))  # Current time in UTC

    now_new = now_utc + datetime.timedelta(days=add_days, hours=add_hours)

    if timezone != 'utc':
        now_new = now_new.astimezone(tzone(timezone))


    if   returnval == 'datetime': return now_new ### datetime
    elif returnval == 'int':      return int(now_new.strftime(fmt))
    else:                        return now_new.strftime(fmt)


def os_subprocess(args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE):
    import subprocess
    proc = subprocess.Popen(args_list, stdout=stdout, stderr=stderr)
    stdout, stderr = proc.communicate()
    return proc.returncode, stdout, stderr



###############################################################################################################
###############################################################################################################
def hivemall_getsqlheader(dir_hivemall_jar="/mypath/hivemall/hivemall-all-0.6.0.jar", dir_hivemall_conf="/mypath/define-all.hive "):
    hivemall_header_sql =  f"""
    -- Hive Mall extensions for SQL Hive
    add jar '{dir_hivemall_jar}' ;
    source  '{dir_hivemall_conf}'  ;


    -- Test if it works
    -- select  minhash(3, array("aaas")) as (clusterId, rowid);

    """
    return  hivemall_header_sql



def hivemall_getdefinition(dirout="./define-all.hive"):
    ss ="""
    -----------------------------------------------------------------------------
    -- Hivemall: Hive scalable Machine Learning Library
    -----------------------------------------------------------------------------

    drop temporary function if exists hivemall_version;
    create temporary function hivemall_version as 'hivemall.HivemallVersionUDF';

    ---------------------------
    -- binary classification --
    ---------------------------

    drop temporary function if exists train_classifier;
    create temporary function train_classifier as 'hivemall.classifier.GeneralClassifierUDTF';

    drop temporary function if exists train_perceptron;
    create temporary function train_perceptron as 'hivemall.classifier.PerceptronUDTF';

    drop temporary function if exists train_pa;
    create temporary function train_pa as 'hivemall.classifier.PassiveAggressiveUDTF';

    drop temporary function if exists train_pa1;
    create temporary function train_pa1 as 'hivemall.classifier.PassiveAggressiveUDTF$PA1';

    drop temporary function if exists train_pa2;
    create temporary function train_pa2 as 'hivemall.classifier.PassiveAggressiveUDTF$PA2';

    drop temporary function if exists train_cw;
    create temporary function train_cw as 'hivemall.classifier.ConfidenceWeightedUDTF';

    drop temporary function if exists train_arow;
    create temporary function train_arow as 'hivemall.classifier.AROWClassifierUDTF';

    drop temporary function if exists train_arowh;
    create temporary function train_arowh as 'hivemall.classifier.AROWClassifierUDTF$AROWh';

    drop temporary function if exists train_scw;
    create temporary function train_scw as 'hivemall.classifier.SoftConfideceWeightedUDTF$SCW1';

    drop temporary function if exists train_scw2;
    create temporary function train_scw2 as 'hivemall.classifier.SoftConfideceWeightedUDTF$SCW2';

    drop temporary function if exists train_adagrad_rda;
    create temporary function train_adagrad_rda as 'hivemall.classifier.AdaGradRDAUDTF';

    drop temporary function if exists train_kpa;
    create temporary function train_kpa as 'hivemall.classifier.KernelExpansionPassiveAggressiveUDTF';

    drop temporary function if exists kpa_predict;
    create temporary function kpa_predict as 'hivemall.classifier.KPAPredictUDAF';

    --------------------------------
    --  Multiclass classification --
    --------------------------------

    drop temporary function if exists train_multiclass_perceptron;
    create temporary function train_multiclass_perceptron as 'hivemall.classifier.multiclass.MulticlassPerceptronUDTF';

    drop temporary function if exists train_multiclass_pa;
    create temporary function train_multiclass_pa as 'hivemall.classifier.multiclass.MulticlassPassiveAggressiveUDTF';

    drop temporary function if exists train_multiclass_pa1;
    create temporary function train_multiclass_pa1 as 'hivemall.classifier.multiclass.MulticlassPassiveAggressiveUDTF$PA1';

    drop temporary function if exists train_multiclass_pa2;
    create temporary function train_multiclass_pa2 as 'hivemall.classifier.multiclass.MulticlassPassiveAggressiveUDTF$PA2';

    drop temporary function if exists train_multiclass_cw;
    create temporary function train_multiclass_cw as 'hivemall.classifier.multiclass.MulticlassConfidenceWeightedUDTF';

    drop temporary function if exists train_multiclass_arow;
    create temporary function train_multiclass_arow as 'hivemall.classifier.multiclass.MulticlassAROWClassifierUDTF';

    drop temporary function if exists train_multiclass_arowh;
    create temporary function train_multiclass_arowh as 'hivemall.classifier.multiclass.MulticlassAROWClassifierUDTF$AROWh';

    drop temporary function if exists train_multiclass_scw;
    create temporary function train_multiclass_scw as 'hivemall.classifier.multiclass.MulticlassSoftConfidenceWeightedUDTF$SCW1';

    drop temporary function if exists train_multiclass_scw2;
    create temporary function train_multiclass_scw2 as 'hivemall.classifier.multiclass.MulticlassSoftConfidenceWeightedUDTF$SCW2';

    --------------------------
    -- similarity functions --
    --------------------------

    drop temporary function if exists cosine_similarity;
    create temporary function cosine_similarity as 'hivemall.knn.similarity.CosineSimilarityUDF';

    drop temporary function if exists jaccard_similarity;
    create temporary function jaccard_similarity as 'hivemall.knn.similarity.JaccardIndexUDF';

    drop temporary function if exists angular_similarity;
    create temporary function angular_similarity as 'hivemall.knn.similarity.AngularSimilarityUDF';

    drop temporary function if exists euclid_similarity;
    create temporary function euclid_similarity as 'hivemall.knn.similarity.EuclidSimilarity';

    drop temporary function if exists distance2similarity;
    create temporary function distance2similarity as 'hivemall.knn.similarity.Distance2SimilarityUDF';

    drop temporary function if exists dimsum_mapper;
    create temporary function dimsum_mapper as 'hivemall.knn.similarity.DIMSUMMapperUDTF';

    ------------------------
    -- distance functions --
    ------------------------

    drop temporary function if exists popcnt;
    create temporary function popcnt as 'hivemall.knn.distance.PopcountUDF';

    drop temporary function if exists kld;
    create temporary function kld as 'hivemall.knn.distance.KLDivergenceUDF';

    drop temporary function if exists hamming_distance;
    create temporary function hamming_distance as 'hivemall.knn.distance.HammingDistanceUDF';

    drop temporary function if exists euclid_distance;
    create temporary function euclid_distance as 'hivemall.knn.distance.EuclidDistanceUDF';

    drop temporary function if exists cosine_distance;
    create temporary function cosine_distance as 'hivemall.knn.distance.CosineDistanceUDF';

    drop temporary function if exists angular_distance;
    create temporary function angular_distance as 'hivemall.knn.distance.AngularDistanceUDF';

    drop temporary function if exists jaccard_distance;
    create temporary function jaccard_distance as 'hivemall.knn.distance.JaccardDistanceUDF';

    drop temporary function if exists manhattan_distance;
    create temporary function manhattan_distance as 'hivemall.knn.distance.ManhattanDistanceUDF';

    drop temporary function if exists minkowski_distance;
    create temporary function minkowski_distance as 'hivemall.knn.distance.MinkowskiDistanceUDF';

    -------------------
    -- LSH functions --
    -------------------

    drop temporary function if exists minhashes;
    create temporary function minhashes as 'hivemall.knn.lsh.MinHashesUDF';

    drop temporary function if exists minhash;
    create temporary function minhash as 'hivemall.knn.lsh.MinHashUDTF';

    drop temporary function if exists bbit_minhash;
    create temporary function bbit_minhash as 'hivemall.knn.lsh.bBitMinHashUDF';

    ----------------------
    -- voting functions --
    ----------------------

    drop temporary function if exists voted_avg;
    create temporary function voted_avg as 'hivemall.ensemble.bagging.VotedAvgUDAF';

    drop temporary function if exists weight_voted_avg;
    create temporary function weight_voted_avg as 'hivemall.ensemble.bagging.WeightVotedAvgUDAF';

    --------------------
    -- misc functions --
    --------------------

    drop temporary function if exists max_label;
    create temporary function max_label as 'hivemall.ensemble.MaxValueLabelUDAF';

    drop temporary function if exists maxrow;
    create temporary function maxrow as 'hivemall.ensemble.MaxRowUDAF';

    drop temporary function if exists argmin_kld;
    create temporary function argmin_kld as 'hivemall.ensemble.ArgminKLDistanceUDAF';

    -----------------------
    -- hashing functions --
    -----------------------

    drop temporary function if exists mhash;
    create temporary function mhash as 'hivemall.ftvec.hashing.MurmurHash3UDF';

    drop temporary function if exists array_hash_values;
    create temporary function array_hash_values as 'hivemall.ftvec.hashing.ArrayHashValuesUDF';

    drop temporary function if exists prefixed_hash_values;
    create temporary function prefixed_hash_values as 'hivemall.ftvec.hashing.ArrayPrefixedHashValuesUDF';

    drop temporary function if exists feature_hashing;
    create temporary function feature_hashing as 'hivemall.ftvec.hashing.FeatureHashingUDF';

    -----------------------
    -- pairing functions --
    -----------------------

    drop temporary function if exists polynomial_features;
    create temporary function polynomial_features as 'hivemall.ftvec.pairing.PolynomialFeaturesUDF';

    drop temporary function if exists powered_features;
    create temporary function powered_features as 'hivemall.ftvec.pairing.PoweredFeaturesUDF';

    drop temporary function if exists feature_pairs;
    create temporary function feature_pairs as 'hivemall.ftvec.pairing.FeaturePairsUDTF';

    -----------------------
    -- scaling functions --
    -----------------------

    drop temporary function if exists rescale;
    create temporary function rescale as 'hivemall.ftvec.scaling.RescaleUDF';

    drop temporary function if exists zscore;
    create temporary function zscore as 'hivemall.ftvec.scaling.ZScoreUDF';

    drop temporary function if exists l1_normalize;
    create temporary function l1_normalize as 'hivemall.ftvec.scaling.L1NormalizationUDF';

    drop temporary function if exists l2_normalize;
    create temporary function l2_normalize as 'hivemall.ftvec.scaling.L2NormalizationUDF';

    ---------------------------------
    -- Feature Selection functions --
    ---------------------------------

    drop temporary function if exists chi2;
    create temporary function chi2 as 'hivemall.ftvec.selection.ChiSquareUDF';

    drop temporary function if exists snr;
    create temporary function snr as 'hivemall.ftvec.selection.SignalNoiseRatioUDAF';

    -----------------------------------
    -- Feature engineering functions --
    -----------------------------------

    drop temporary function if exists amplify;
    create temporary function amplify as 'hivemall.ftvec.amplify.AmplifierUDTF';

    drop temporary function if exists rand_amplify;
    create temporary function rand_amplify as 'hivemall.ftvec.amplify.RandomAmplifierUDTF';

    drop temporary function if exists add_bias;
    create temporary function add_bias as 'hivemall.ftvec.AddBiasUDF';

    drop temporary function if exists sort_by_feature;
    create temporary function sort_by_feature as 'hivemall.ftvec.SortByFeatureUDF';

    drop temporary function if exists extract_feature;
    create temporary function extract_feature as 'hivemall.ftvec.ExtractFeatureUDF';

    drop temporary function if exists extract_weight;
    create temporary function extract_weight as 'hivemall.ftvec.ExtractWeightUDF';

    drop temporary function if exists add_feature_index;
    create temporary function add_feature_index as 'hivemall.ftvec.AddFeatureIndexUDF';

    drop temporary function if exists feature;
    create temporary function feature as 'hivemall.ftvec.FeatureUDF';

    drop temporary function if exists feature_index;
    create temporary function feature_index as 'hivemall.ftvec.FeatureIndexUDF';

    ----------------------------------
    -- feature converting functions --
    ----------------------------------

    drop temporary function if exists conv2dense;
    create temporary function conv2dense as 'hivemall.ftvec.conv.ConvertToDenseModelUDAF';

    drop temporary function if exists to_dense_features;
    create temporary function to_dense_features as 'hivemall.ftvec.conv.ToDenseFeaturesUDF';

    -- alias
    drop temporary function if exists to_dense;
    create temporary function to_dense as 'hivemall.ftvec.conv.ToDenseFeaturesUDF';

    drop temporary function if exists to_sparse_features;
    create temporary function to_sparse_features as 'hivemall.ftvec.conv.ToSparseFeaturesUDF';

    -- alias
    drop temporary function if exists to_sparse;
    create temporary function to_sparse as 'hivemall.ftvec.conv.ToSparseFeaturesUDF';

    drop temporary function if exists quantify;
    create temporary function quantify as 'hivemall.ftvec.conv.QuantifyColumnsUDTF';

    drop temporary function if exists build_bins;
    create temporary function build_bins as 'hivemall.ftvec.binning.BuildBinsUDAF';

    drop temporary function if exists feature_binning;
    create temporary function feature_binning as 'hivemall.ftvec.binning.FeatureBinningUDF';

    drop temporary function if exists to_libsvm_format;
    create temporary function to_libsvm_format as 'hivemall.ftvec.conv.ToLibSVMFormatUDF';

    --------------------------
    -- feature transformers --
    --------------------------

    drop temporary function if exists vectorize_features;
    create temporary function vectorize_features as 'hivemall.ftvec.trans.VectorizeFeaturesUDF';

    drop temporary function if exists categorical_features;
    create temporary function categorical_features as 'hivemall.ftvec.trans.CategoricalFeaturesUDF';

    drop temporary function if exists ffm_features;
    create temporary function ffm_features as 'hivemall.ftvec.trans.FFMFeaturesUDF';

    drop temporary function if exists indexed_features;
    create temporary function indexed_features as 'hivemall.ftvec.trans.IndexedFeatures';

    drop temporary function if exists quantified_features;
    create temporary function quantified_features as 'hivemall.ftvec.trans.QuantifiedFeaturesUDTF';

    drop temporary function if exists quantitative_features;
    create temporary function quantitative_features as 'hivemall.ftvec.trans.QuantitativeFeaturesUDF';

    drop temporary function if exists binarize_label;
    create temporary function binarize_label as 'hivemall.ftvec.trans.BinarizeLabelUDTF';

    drop temporary function if exists onehot_encoding;
    create temporary function onehot_encoding as 'hivemall.ftvec.trans.OnehotEncodingUDAF';

    drop temporary function if exists add_field_indices;
    create temporary function add_field_indices as 'hivemall.ftvec.trans.AddFieldIndicesUDF';

    -- alias for backward compatibility
    drop temporary function if exists add_field_indicies;
    create temporary function add_field_indicies as 'hivemall.ftvec.trans.AddFieldIndicesUDF';

    ------------------------------
    -- ranking helper functions --
    ------------------------------

    drop temporary function if exists bpr_sampling;
    create temporary function bpr_sampling as 'hivemall.ftvec.ranking.BprSamplingUDTF';

    drop temporary function if exists item_pairs_sampling;
    create temporary function item_pairs_sampling as 'hivemall.ftvec.ranking.ItemPairsSamplingUDTF';

    drop temporary function if exists populate_not_in;
    create temporary function populate_not_in as 'hivemall.ftvec.ranking.PopulateNotInUDTF';

    --------------------------
    -- ftvec/text functions --
    --------------------------

    drop temporary function if exists tf;
    create temporary function tf as 'hivemall.ftvec.text.TermFrequencyUDAF';

    drop temporary function if exists bm25;
    create temporary function bm25 as 'hivemall.ftvec.text.OkapiBM25UDF';

    --------------------------
    -- Regression functions --
    --------------------------

    drop temporary function if exists train_regressor;
    create temporary function train_regressor as 'hivemall.regression.GeneralRegressorUDTF';

    drop temporary function if exists logress;
    create temporary function logress as 'hivemall.regression.LogressUDTF';

    drop temporary function if exists train_logistic_regr;
    create temporary function train_logistic_regr as 'hivemall.regression.LogressUDTF';

    drop temporary function if exists train_pa1_regr;
    create temporary function train_pa1_regr as 'hivemall.regression.PassiveAggressiveRegressionUDTF';

    drop temporary function if exists train_pa1a_regr;
    create temporary function train_pa1a_regr as 'hivemall.regression.PassiveAggressiveRegressionUDTF$PA1a';

    drop temporary function if exists train_pa2_regr;
    create temporary function train_pa2_regr as 'hivemall.regression.PassiveAggressiveRegressionUDTF$PA2';

    drop temporary function if exists train_pa2a_regr;
    create temporary function train_pa2a_regr as 'hivemall.regression.PassiveAggressiveRegressionUDTF$PA2a';

    drop temporary function if exists train_arow_regr;
    create temporary function train_arow_regr as 'hivemall.regression.AROWRegressionUDTF';

    drop temporary function if exists train_arowe_regr;
    create temporary function train_arowe_regr as 'hivemall.regression.AROWRegressionUDTF$AROWe';

    drop temporary function if exists train_arowe2_regr;
    create temporary function train_arowe2_regr as 'hivemall.regression.AROWRegressionUDTF$AROWe2';

    drop temporary function if exists train_adagrad_regr;
    create temporary function train_adagrad_regr as 'hivemall.regression.AdaGradUDTF';

    drop temporary function if exists train_adadelta_regr;
    create temporary function train_adadelta_regr as 'hivemall.regression.AdaDeltaUDTF';

    ---------------------
    -- array functions --
    ---------------------

    drop temporary function if exists float_array;
    create temporary function float_array as 'hivemall.tools.array.AllocFloatArrayUDF';

    drop temporary function if exists array_remove;
    create temporary function array_remove as 'hivemall.tools.array.ArrayRemoveUDF';

    drop temporary function if exists sort_and_uniq_array;
    create temporary function sort_and_uniq_array as 'hivemall.tools.array.SortAndUniqArrayUDF';

    drop temporary function if exists subarray_endwith;
    create temporary function subarray_endwith as 'hivemall.tools.array.SubarrayEndWithUDF';

    drop temporary function if exists subarray_startwith;
    create temporary function subarray_startwith as 'hivemall.tools.array.SubarrayStartWithUDF';

    drop temporary function if exists array_concat;
    create temporary function array_concat as 'hivemall.tools.array.ArrayConcatUDF';

    -- alias for backward compatibility
    drop temporary function if exists concat_array;
    create temporary function concat_array as 'hivemall.tools.array.ArrayConcatUDF';

    drop temporary function if exists subarray;
    create temporary function subarray as 'hivemall.tools.array.SubarrayUDF';

    drop temporary function if exists array_slice;
    create temporary function array_slice as 'hivemall.tools.array.ArraySliceUDF';

    drop temporary function if exists array_avg;
    create temporary function array_avg as 'hivemall.tools.array.ArrayAvgGenericUDAF';

    drop temporary function if exists array_sum;
    create temporary function array_sum as 'hivemall.tools.array.ArraySumUDAF';

    drop temporary function if exists to_string_array;
    create temporary function to_string_array as 'hivemall.tools.array.ToStringArrayUDF';

    drop temporary function if exists array_intersect;
    create temporary function array_intersect as 'hivemall.tools.array.ArrayIntersectUDF';

    drop temporary function if exists select_k_best;
    create temporary function select_k_best as 'hivemall.tools.array.SelectKBestUDF';

    drop temporary function if exists array_append;
    create temporary function array_append as 'hivemall.tools.array.ArrayAppendUDF';

    drop temporary function if exists element_at;
    create temporary function element_at as 'hivemall.tools.array.ArrayElementAtUDF';

    drop temporary function if exists array_union;
    create temporary function array_union as 'hivemall.tools.array.ArrayUnionUDF';

    drop temporary function if exists first_element;
    create temporary function first_element as 'hivemall.tools.array.FirstElementUDF';

    drop temporary function if exists last_element;
    create temporary function last_element as 'hivemall.tools.array.LastElementUDF';

    drop temporary function if exists array_flatten;
    create temporary function array_flatten as 'hivemall.tools.array.ArrayFlattenUDF';

    drop temporary function if exists array_to_str;
    create temporary function array_to_str as 'hivemall.tools.array.ArrayToStrUDF';

    drop temporary function if exists conditional_emit;
    create temporary function conditional_emit as 'hivemall.tools.array.ConditionalEmitUDTF';

    drop temporary function if exists argmin;
    create temporary function argmin as 'hivemall.tools.array.ArgminUDF';

    drop temporary function if exists argmax;
    create temporary function argmax as 'hivemall.tools.array.ArgmaxUDF';

    drop temporary function if exists arange;
    create temporary function arange as 'hivemall.tools.array.ArangeUDF';

    drop temporary function if exists argrank;
    create temporary function argrank as 'hivemall.tools.array.ArgrankUDF';

    drop temporary function if exists argsort;
    create temporary function argsort as 'hivemall.tools.array.ArgsortUDF';

    -----------------------------
    -- bit operation functions --
    -----------------------------

    drop temporary function if exists bits_collect;
    create temporary function bits_collect as 'hivemall.tools.bits.BitsCollectUDAF';

    drop temporary function if exists to_bits;
    create temporary function to_bits as 'hivemall.tools.bits.ToBitsUDF';

    drop temporary function if exists unbits;
    create temporary function unbits as 'hivemall.tools.bits.UnBitsUDF';

    drop temporary function if exists bits_or;
    create temporary function bits_or as 'hivemall.tools.bits.BitsORUDF';

    ---------------------------
    -- compression functions --
    ---------------------------

    drop temporary function if exists inflate;
    create temporary function inflate as 'hivemall.tools.compress.InflateUDF';

    drop temporary function if exists deflate;
    create temporary function deflate as 'hivemall.tools.compress.DeflateUDF';

    ---------------------
    -- map functions --
    ---------------------

    drop temporary function if exists map_get_sum;
    create temporary function map_get_sum as 'hivemall.tools.map.MapGetSumUDF';

    drop temporary function if exists map_tail_n;
    create temporary function map_tail_n as 'hivemall.tools.map.MapTailNUDF';

    drop temporary function if exists to_map;
    create temporary function to_map as 'hivemall.tools.map.UDAFToMap';

    drop temporary function if exists to_ordered_map;
    create temporary function to_ordered_map as 'hivemall.tools.map.UDAFToOrderedMap';

    drop temporary function if exists map_include_keys;
    create temporary function map_include_keys as 'hivemall.tools.map.MapIncludeKeysUDF';

    drop temporary function if exists map_exclude_keys;
    create temporary function map_exclude_keys as 'hivemall.tools.map.MapExcludeKeysUDF';

    drop temporary function if exists map_get;
    create temporary function map_get as 'hivemall.tools.map.MapGetUDF';

    drop temporary function if exists map_key_values;
    create temporary function map_key_values as 'hivemall.tools.map.MapKeyValuesUDF';

    drop temporary function if exists map_roulette;
    create temporary function map_roulette as 'hivemall.tools.map.MapRouletteUDF';

    ---------------------
    -- list functions --
    ---------------------

    drop temporary function if exists to_ordered_list;
    create temporary function to_ordered_list as 'hivemall.tools.list.UDAFToOrderedList';

    ---------------------
    -- Math functions --
    ---------------------

    drop temporary function if exists sigmoid;
    create temporary function sigmoid as 'hivemall.tools.math.SigmoidGenericUDF';

    drop temporary function if exists l2_norm;
    create temporary function l2_norm as 'hivemall.tools.math.L2NormUDAF';

    drop temporary function if exists infinity;
    create temporary function infinity as 'hivemall.tools.math.InfinityUDF';

    drop temporary function if exists is_infinite;
    create temporary function is_infinite as 'hivemall.tools.math.IsInfiniteUDF';

    drop temporary function if exists is_finite;
    create temporary function is_finite as 'hivemall.tools.math.IsFiniteUDF';

    drop temporary function if exists nan;
    create temporary function nan as 'hivemall.tools.math.NanUDF';

    drop temporary function if exists is_nan;
    create temporary function is_nan as 'hivemall.tools.math.IsNanUDF';

    -----------------------------
    -- Matrix/Vector functions --
    -----------------------------

    drop temporary function if exists transpose_and_dot;
    create temporary function transpose_and_dot as 'hivemall.tools.matrix.TransposeAndDotUDAF';

    drop temporary function if exists vector_add;
    create temporary function vector_add as 'hivemall.tools.vector.VectorAddUDF';

    drop temporary function if exists vector_dot;
    create temporary function vector_dot as 'hivemall.tools.vector.VectorDotUDF';

    ----------------------
    -- mapred functions --
    ----------------------

    drop temporary function if exists taskid;
    create temporary function taskid as 'hivemall.tools.mapred.TaskIdUDF';

    drop temporary function if exists jobid;
    create temporary function jobid as 'hivemall.tools.mapred.JobIdUDF';

    drop temporary function if exists rowid;
    create temporary function rowid as 'hivemall.tools.mapred.RowIdUDF';

    drop temporary function if exists rownum;
    create temporary function rownum as 'hivemall.tools.mapred.RowNumberUDF';

    drop temporary function if exists distcache_gets;
    create temporary function distcache_gets as 'hivemall.tools.mapred.DistributedCacheLookupUDF';

    drop temporary function if exists jobconf_gets;
    create temporary function jobconf_gets as 'hivemall.tools.mapred.JobConfGetsUDF';

    --------------------
    -- JSON functions --
    --------------------

    drop temporary function if exists to_json;
    create temporary function to_json as 'hivemall.tools.json.ToJsonUDF';

    drop temporary function if exists from_json;
    create temporary function from_json as 'hivemall.tools.json.FromJsonUDF';

    ----------------------------
    -- Sanity Check functions --
    ----------------------------

    drop temporary function if exists assert;
    create temporary function assert as 'hivemall.tools.sanity.AssertUDF';

    drop temporary function if exists raise_error;
    create temporary function raise_error as 'hivemall.tools.sanity.RaiseErrorUDF';

    --------------------
    -- misc functions --
    --------------------

    drop temporary function if exists generate_series;
    create temporary function generate_series as 'hivemall.tools.GenerateSeriesUDTF';

    drop temporary function if exists convert_label;
    create temporary function convert_label as 'hivemall.tools.ConvertLabelUDF';

    drop temporary function if exists x_rank;
    create temporary function x_rank as 'hivemall.tools.RankSequenceUDF';

    drop temporary function if exists each_top_k;
    create temporary function each_top_k as 'hivemall.tools.EachTopKUDTF';

    drop temporary function if exists try_cast;
    create temporary function try_cast as 'hivemall.tools.TryCastUDF';

    drop temporary function if exists sessionize;
    create temporary function sessionize as 'hivemall.tools.datetime.SessionizeUDF';

    drop temporary function if exists moving_avg;
    create temporary function moving_avg as 'hivemall.tools.timeseries.MovingAverageUDTF';

    -------------------------------
    -- Text processing functions --
    -------------------------------

    drop temporary function if exists tokenize;
    create temporary function tokenize as 'hivemall.tools.text.TokenizeUDF';

    drop temporary function if exists is_stopword;
    create temporary function is_stopword as 'hivemall.tools.text.StopwordUDF';

    drop temporary function if exists singularize;
    create temporary function singularize as 'hivemall.tools.text.SingularizeUDF';

    drop temporary function if exists split_words;
    create temporary function split_words as 'hivemall.tools.text.SplitWordsUDF';

    drop temporary function if exists normalize_unicode;
    create temporary function normalize_unicode as 'hivemall.tools.text.NormalizeUnicodeUDF';

    drop temporary function if exists base91;
    create temporary function base91 as 'hivemall.tools.text.Base91UDF';

    drop temporary function if exists unbase91;
    create temporary function unbase91 as 'hivemall.tools.text.Unbase91UDF';

    drop temporary function if exists word_ngrams;
    create temporary function word_ngrams as 'hivemall.tools.text.WordNgramsUDF';

    ---------------------------------
    -- Dataset generator functions --
    ---------------------------------

    drop temporary function if exists lr_datagen;
    create temporary function lr_datagen as 'hivemall.dataset.LogisticRegressionDataGeneratorUDTF';

    --------------------------
    -- Evaluating functions --
    --------------------------

    drop temporary function if exists f1score;
    create temporary function f1score as 'hivemall.evaluation.F1ScoreUDAF';

    drop temporary function if exists fmeasure;
    create temporary function fmeasure as 'hivemall.evaluation.FMeasureUDAF';

    drop temporary function if exists mae;
    create temporary function mae as 'hivemall.evaluation.MeanAbsoluteErrorUDAF';

    drop temporary function if exists mse;
    create temporary function mse as 'hivemall.evaluation.MeanSquaredErrorUDAF';

    drop temporary function if exists rmse;
    create temporary function rmse as 'hivemall.evaluation.RootMeanSquaredErrorUDAF';

    drop temporary function if exists r2;
    create temporary function r2 as 'hivemall.evaluation.R2UDAF';

    drop temporary function if exists ndcg;
    create temporary function ndcg as 'hivemall.evaluation.NDCGUDAF';

    drop temporary function if exists precision_at;
    create temporary function precision_at as 'hivemall.evaluation.PrecisionUDAF';

    drop temporary function if exists recall_at;
    create temporary function recall_at as 'hivemall.evaluation.RecallUDAF';

    drop temporary function if exists hitrate;
    create temporary function hitrate as 'hivemall.evaluation.HitRateUDAF';

    drop temporary function if exists mrr;
    create temporary function mrr as 'hivemall.evaluation.MRRUDAF';

    drop temporary function if exists average_precision;
    create temporary function average_precision as 'hivemall.evaluation.MAPUDAF';

    drop temporary function if exists auc;
    create temporary function auc as 'hivemall.evaluation.AUCUDAF';

    drop temporary function if exists logloss;
    create temporary function logloss as 'hivemall.evaluation.LogarithmicLossUDAF';

    --------------------------
    -- Matrix Factorization --
    --------------------------

    drop temporary function if exists mf_predict;
    create temporary function mf_predict as 'hivemall.factorization.mf.MFPredictionUDF';

    drop temporary function if exists train_mf_sgd;
    create temporary function train_mf_sgd as 'hivemall.factorization.mf.MatrixFactorizationSGDUDTF';

    drop temporary function if exists train_mf_adagrad;
    create temporary function train_mf_adagrad as 'hivemall.factorization.mf.MatrixFactorizationAdaGradUDTF';

    drop temporary function if exists train_bprmf;
    create temporary function train_bprmf as 'hivemall.factorization.mf.BPRMatrixFactorizationUDTF';

    drop temporary function if exists bprmf_predict;
    create temporary function bprmf_predict as 'hivemall.factorization.mf.BPRMFPredictionUDF';

    ---------------------------
    -- Factorization Machine --
    ---------------------------

    drop temporary function if exists fm_predict;
    create temporary function fm_predict as 'hivemall.factorization.fm.FMPredictGenericUDAF';

    drop temporary function if exists train_fm;
    create temporary function train_fm as 'hivemall.factorization.fm.FactorizationMachineUDTF';

    drop temporary function if exists train_ffm;
    create temporary function train_ffm as 'hivemall.factorization.fm.FieldAwareFactorizationMachineUDTF';

    drop temporary function if exists ffm_predict;
    create temporary function ffm_predict as 'hivemall.factorization.fm.FFMPredictGenericUDAF';

    ---------------------------
    -- Anomaly Detection ------
    ---------------------------

    drop temporary function if exists changefinder;
    create temporary function changefinder as 'hivemall.anomaly.ChangeFinderUDF';

    drop temporary function if exists sst;
    create temporary function sst as 'hivemall.anomaly.SingularSpectrumTransformUDF';

    --------------------
    -- Topic Modeling --
    --------------------

    drop temporary function if exists train_lda;
    create temporary function train_lda as 'hivemall.topicmodel.LDAUDTF';

    drop temporary function if exists lda_predict;
    create temporary function lda_predict as 'hivemall.topicmodel.LDAPredictUDAF';

    drop temporary function if exists train_plsa;
    create temporary function train_plsa as 'hivemall.topicmodel.PLSAUDTF';

    drop temporary function if exists plsa_predict;
    create temporary function plsa_predict as 'hivemall.topicmodel.PLSAPredictUDAF';

    ---------------------------
    -- Geo-Spatial functions --
    ---------------------------

    drop temporary function if exists tile;
    create temporary function tile as 'hivemall.geospatial.TileUDF';

    drop temporary function if exists map_url;
    create temporary function map_url as 'hivemall.geospatial.MapURLUDF';

    drop temporary function if exists lat2tiley;
    create temporary function lat2tiley as 'hivemall.geospatial.Lat2TileYUDF';

    drop temporary function if exists lon2tilex;
    create temporary function lon2tilex as 'hivemall.geospatial.Lon2TileXUDF';

    drop temporary function if exists tilex2lon;
    create temporary function tilex2lon as 'hivemall.geospatial.TileX2LonUDF';

    drop temporary function if exists tiley2lat;
    create temporary function tiley2lat as 'hivemall.geospatial.TileY2LatUDF';

    drop temporary function if exists haversine_distance;
    create temporary function haversine_distance as 'hivemall.geospatial.HaversineDistanceUDF';

    ----------------------------
    -- Smile related features --
    ----------------------------

    drop temporary function if exists train_randomforest_classifier;
    create temporary function train_randomforest_classifier as 'hivemall.smile.classification.RandomForestClassifierUDTF';

    drop temporary function if exists train_randomforest_regressor;
    create temporary function train_randomforest_regressor as 'hivemall.smile.regression.RandomForestRegressionUDTF';

    drop temporary function if exists train_randomforest_regr;
    create temporary function train_randomforest_regr as 'hivemall.smile.regression.RandomForestRegressionUDTF';

    drop temporary function if exists tree_predict;
    create temporary function tree_predict as 'hivemall.smile.tools.TreePredictUDF';

    -- for backward compatibility
    drop temporary function if exists tree_predict_v1;
    create temporary function tree_predict_v1 as 'hivemall.smile.tools.TreePredictUDFv1';

    drop temporary function if exists tree_export;
    create temporary function tree_export as 'hivemall.smile.tools.TreeExportUDF';

    drop temporary function if exists rf_ensemble;
    create temporary function rf_ensemble as 'hivemall.smile.tools.RandomForestEnsembleUDAF';

    drop temporary function if exists guess_attribute_types;
    create temporary function guess_attribute_types as 'hivemall.smile.tools.GuessAttributesUDF';

    drop temporary function if exists decision_path;
    create temporary function decision_path as 'hivemall.smile.tools.DecisionPathUDF';

    --------------------
    -- Recommendation --
    --------------------

    drop temporary function if exists train_slim;
    create temporary function train_slim as 'hivemall.recommend.SlimUDTF';

    -----------------
    -- Data Sketch --
    -----------------

    drop temporary function if exists approx_count_distinct;
    create temporary function approx_count_distinct as 'hivemall.sketch.hll.ApproxCountDistinctUDAF';

    ------------------
    -- Bloom Filter --
    ------------------

    drop temporary function if exists bloom;
    create temporary function bloom as 'hivemall.sketch.bloom.BloomFilterUDAF';

    drop temporary function if exists bloom_and;
    create temporary function bloom_and as 'hivemall.sketch.bloom.BloomAndUDF';

    drop temporary function if exists bloom_contains;
    create temporary function bloom_contains as 'hivemall.sketch.bloom.BloomContainsUDF';

    drop temporary function if exists bloom_not;
    create temporary function bloom_not as 'hivemall.sketch.bloom.BloomNotUDF';

    drop temporary function if exists bloom_or;
    create temporary function bloom_or as 'hivemall.sketch.bloom.BloomOrUDF';

    drop temporary function if exists bloom_contains_any;
    create temporary function bloom_contains_any as 'hivemall.sketch.bloom.BloomContainsAnyUDF';

    -----------------
    -- Aggregation --
    -----------------

    drop temporary function if exists max_by;
    create temporary function max_by as 'hivemall.tools.aggr.MaxByUDAF';

    drop temporary function if exists min_by;
    create temporary function min_by as 'hivemall.tools.aggr.MinByUDAF';

    drop temporary function if exists majority_vote;
    create temporary function majority_vote as 'hivemall.tools.aggr.MajorityVoteUDAF';


    --------------------------------------------------------------------------------------------------
    -- macros available from hive 0.12.0
    -- see https://issues.apache.org/jira/browse/HIVE-2655

    --------------------
    -- General Macros --
    --------------------

    create temporary macro java_min(x DOUBLE, y DOUBLE)
    reflect("java.lang.Math", "min", x, y);

    create temporary macro max2(x DOUBLE, y DOUBLE)
    if(x>y,x,y);

    create temporary macro min2(x DOUBLE, y DOUBLE)
    if(x<y,x,y);

    --------------------------
    -- Statistics functions --
    --------------------------

    create temporary macro idf(df_t DOUBLE, n_docs DOUBLE)
    log(10, n_docs / max2(1,df_t)) + 1.0;

    create temporary macro tfidf(tf FLOAT, df_t DOUBLE, n_docs DOUBLE)
    tf * (log(10, n_docs / max2(1,df_t)) + 1.0);



    """
    with open(dirout, mode='a') as fp:
        fp.writelines(ss)

    return ss




###############################################################################################################
###############################################################################################################
def hdfs_help():
 log("""
    cat: Copies source paths to stdout.
    Usage: hdfs dfs -cat URI [URI ?]

    Example:
        hdfs dfs -cat hdfs://<path>/file1
        hdfs dfs -cat file:///file2 /user/hadoop/file3

    chgrp: Changes the group association of files. With -R, makes the change recursively by way of path structure. The user must be the file owner or the superuser.
    Usage: hdfs dfs -chgrp [-R] GROUP URI [URI ?]

    chmod: Changes the permissions of files. With -R, makes the change recursively by way of path structure. The user must be the file owner or the superuser
    Usage: hdfs dfs -chmod [-R] <MODE[,MODE]? | OCTALMODE> URI [URI ?]
    Example: hdfs dfs -chmod 777 test/data1.txt

    chown: Changes the owner of files. With -R, makes the change recursively by way of path structure. The user must be the superuser.
    Usage: hdfs dfs -chown [-R] [OWNER][:[GROUP]] URI [URI ]
    Example: hdfs dfs -chown -R hduser2 /opt/hadoop/logs

    copyFromLocal: Works similarly to the put command, except that the source is restricted to a local file reference.
    Usage: hdfs dfs -copyFromLocal <localsrc> URI
    Example: hdfs dfs -copyFromLocal input/docs/data2.txt hdfs://localhost/user/rosemary/data2.txt

    copyToLocal: Works similarly to the get command, except that the destination is restricted to a local file reference.
    Usage: hdfs dfs -copyToLocal [-ignorecrc] [-crc] URI <localdst>
    Example: hdfs dfs -copyToLocal data2.txt data2.copy.txt

    count: Counts the number of directories, files, and bytes under the paths that match the specified file pattern.
    Usage: hdfs dfs -count [-q] <paths>
    Example: hdfs dfs -count hdfs://nn1.example.com/file1 hdfs://nn2.example.com/file2

    cp: Copies one or more files from a specified source to a specified destination. If you specify multiple sources, the specified destination must be a directory.
    Usage: hdfs dfs -cp URI [URI ?] <dest>
    Example: hdfs dfs -cp /user/hadoop/file1 /user/hadoop/file2 /user/hadoop/dir

    du: Displays the size of the specified file, or the sizes of files and directories that are contained in the specified directory. If you specify the -s option, displays an aggregate summary of file sizes rather than individual file sizes. If you specify the -h option, formats the file sizes in a �ghuman-readable�h way.
    Usage: hdfs dfs -du [-s] [-h] URI [URI ?]
    Example: hdfs dfs -du /user/hadoop/dir1 /user/hadoop/file1

    dus: Displays a summary of file sizes; equivalent to hdfs dfs -du ?s.
    Usage: hdfs dfs -dus <args>

    expunge: Empties the trash. When you delete a file, it isn�ft removed immediately from HDFS, but is renamed to a file in the /trash directory. As long as the file remains there, you can undelete it if you change your mind, though only the latest copy of the deleted file can be restored.
    Usage: hdfs dfs ?expunge

    get: Copies files to the local file system. Files that fail a cyclic redundancy check (CRC) can still be copied if you specify the ?ignorecrc option. The CRC is a common technique for detecting data transmission errors. CRC checksum files have the .crc extension and are used to verify the data integrity of another file. These files are copied if you specify the -crc option.
    Usage: hdfs dfs -get [-ignorecrc] [-crc] <src> <localdst>
    Example: hdfs dfs -get /user/hadoop/file3 localfile

    getmerge: Concatenates the files in src and writes the result to the specified local destination file. To add a newline character at the end of each file, specify the addnl option.
    Usage: hdfs dfs -getmerge <src> <localdst> [addnl]
    Example: hdfs dfs -getmerge /user/hadoop/mydir/ ~/result_file addnl

    ls: Returns statistics for the specified files or directories.
    Usage: hdfs dfs -ls <args>
    Example: hdfs dfs -ls /user/hadoop/file1

    lsr: Serves as the recursive version of ls; similar to the Unix command ls -R.
    Usage: hdfs dfs -lsr <args>
    Example: hdfs dfs -lsr /user/hadoop

    mkdir: Creates directories on one or more specified paths. Its behavior is similar to the Unix mkdir -p command, which creates all directories that lead up to the specified directory if they don�ft exist already.
    Usage: hdfs dfs -mkdir <paths>
    Example: hdfs dfs -mkdir /user/hadoop/dir5/temp

    moveFromLocal: Works similarly to the put command, except that the source is deleted after it is copied.
    Usage: hdfs dfs -moveFromLocal <localsrc> <dest>
    Example: hdfs dfs -moveFromLocal localfile1 localfile2 /user/hadoop/hadoopdir

    mv: Moves one or more files from a specified source to a specified destination. If you specify multiple sources, the specified destination must be a directory. Moving files across file systems isn�ft permitted.
    Usage: hdfs dfs -mv URI [URI ?] <dest>
    Example: hdfs dfs -mv /user/hadoop/file1 /user/hadoop/file2

    put: Copies files from the local file system to the destination file system. This command can also read input from stdin and write to the destination file system.
    Usage: hdfs dfs -put <localsrc> ? <dest>
    Example: hdfs dfs -put localfile1 localfile2 /user/hadoop/hadoopdir; hdfs dfs -put ? /user/hadoop/hadoopdir (reads input from stdin)


    rm: Deletes one or more specified files. This command doesn�ft delete empty directories or files. To bypass the trash (if it�fs enabled) and delete the specified files immediately, specify the -skipTrash option.
    Usage: hdfs dfs -rm [-skipTrash] URI [URI ?]
    Example: hdfs dfs -rm hdfs://nn.example.com/file9
    
    rmr: Serves as the recursive version of ?rm.
    Usage: hdfs dfs -rmr [-skipTrash] URI [URI ?]
    Example: hdfs dfs -rmr /user/hadoop/dir

    setrep: Changes the replication factor for a specified file or directory. With ?R, makes the change recursively by way of path structure.
    Usage: hdfs dfs -setrep <rep> [-R] <path>

    Example: hdfs dfs -setrep 3 -R /user/hadoop/dir1
    stat: Displays information about the specified path.

    Usage: hdfs dfs -stat URI [URI ?]
    Example: hdfs dfs -stat /user/hadoop/dir1
    tail: Displays the last kilobyte of a specified file to stdout. The syntax supports the Unix -f option, which enables the specified file to be monitored. As new lines are added to the file by another process, tail updates the display.

    Usage: hdfs dfs -tail [-f] URI
    Example: hdfs dfs -tail /user/hadoop/dir1

    test: Returns attributes of the specified file or directory. Specifies ?e to determine whether the file or directory exists; -z to determine whether the file or directory is empty; and -d to determine whether the URI is a directory.
    Usage: hdfs dfs -test -[ezd] URI
    Example: hdfs dfs -test /user/hadoop/dir1

    text: Outputs a specified source file in text format. Valid input file formats are zip and TextRecordInputStream.
    Usage: hdfs dfs -text <src>
    Example: hdfs dfs -text /user/hadoop/file8.zip  

    touchz: Creates a new, empty file of size 0 in the specified path.
    Usage: hdfs dfs -touchz <path>
    Example: hdfs dfs -touchz /user/hadoop/file12   """)
     




###############################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()

