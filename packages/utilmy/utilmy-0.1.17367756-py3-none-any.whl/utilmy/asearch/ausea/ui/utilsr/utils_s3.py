""" Utils for S3

  

##### Install LocalStack:
      pip install localstack

      Start LocalStack: Use the following command to start LocalStack with S3 service:
      localstack start --services=s3
      Configure AWS CLI and Boto3: Set up AWS CLI and Boto3 to use the LocalStack endpoint for S3. Typically, LocalStack runs on http://localhost:4566.


      aws configure


      # Use access key: test, secret key: test, region: us-east-1, output format: json
      Python Example: Here’s a Python script using boto3 to interact with S3 on LocalStack:

      import boto3

      # Configure boto3 to use LocalStack
      s3 = boto3.client('s3', endpoint_url='http://localhost:4566', aws_access_key_id='test', aws_secret_access_key='test', region_name='us-east-1')

      # Create a bucket
      s3.create_bucket(Bucket='my-test-bucket')

      # Upload a file
      s3.put_object(Bucket='my-test-bucket', Key='testfile.txt', Body=b'Hello LocalStack!')

      # Retrieve the file
      response = s3.get_object(Bucket='my-test-bucket', Key='testfile.txt')
      data = response['Body'].read().decode('utf-8')
      log(data)



"""
import boto3, os, sys
import pandas as pd
from io import StringIO
import time
import random
from datetime import datetime
import multiprocessing as mp
import awswrangler as wr


#from utilmy import log,loge
from src.utils.utilmy_log import (   log)


from src.utils.utilmy_aws import (pd_to_file_s3, pd_read_file_s3)

##########################################################################
def test_lock():
    """
         pip install fire utilmy

         ### Concurrent lock simulation
             python util_s3.py  test_lock ;     python util_s3.py  test_lock ;   python util_s3.py  test_lock ; 


         
    """
    cmd = " aws s3 mb s3://bucket "
    os.system( cmd )

    s3lock = S3lock('s3://bucket/mylock/')
    s3lock.lock('s3://bucket/path1/csv_file.csv')

    ### Do Something
    time.sleep(random.random(3))

    s3lock.unlock('s3://bucket/path1/csv_file.csv')


    s3_csv = S3Lock_csv('s3://bucket/csv_file.csv', 's3://bucket')
    s3_csv.update_csv(newrow=['Rohn', 75])


def test2():
  """
     Logs


  """  
  # Usage for S3
  s3lock = cloudLock(dirlock=dir1+"/ztmp/lock_hash")
  s3lock.lock(dir1+"/ztmp//myfile.csv")
   # do something
  s3lock.unlock(dir1+"/ztmp//myfile.csv")

  # Usage for GCS
  gcslock = cloudLock(dirlock="gs://mybucket/ztmp/lock_hash")
  gcslock.lock("gs://myotherbucket/myfile.csv")
  # do something
  gcslock.unlock("gs://myotherbucket/myfile.csv")

  # Usage for Local Filesystem
  locallock = cloudLock(dirlock="/local/path/ztmp/lock_hash")
  locallock.lock("/local/path/myfile.csv")
  # do something
  locallock.unlock("/local/path/myfile.csv")



#########################################################################
dir1= "s3://edge-ml-dev"
dir2="s3://edge-version-dev--use1-az4--x-s3"

def test_s3lock_fun(x):
  from src.utils.utilmy_aws import pd_read_file_s3, pd_to_file_s3
  import awswrangler as wr 
  dir2 = dir1+"/ztmp/myfile4.csv"

  s3lock = S3lock(dirlock=dir1+"/ztmp/lock_hash", n_concurrent=10)
  s3lock.lock(dir2)
  log(x, time.time())
  time.sleep(5)

  try:
      df0 = pd_read_file_s3(dir2)
  except:
      df0 = pd.DataFrame([], columns=['file'])


  flist = [ str(x) ]
  df = pd.DataFrame(flist,  columns=['file'])
  df = pd.concat((df0, df))
  wr.s3.to_csv(df, dir2, index=False, sep="\t" )

  s3lock.unlock(dir2)
  return x



def test_s3lock():
    """
          python src/utils/utils_s3.py test_lock_adds
    """
    npool = 5
    pool = mp.Pool(processes = npool)
    results = []

    for i in range(0, npool):
       results.append(pool.apply_async(test_s3lock_fun, (i * 10 ,))) 
    
    for r in results:
        log(r.get())



######################################################################
def testcsv1(x=2 ):
  index1 = S3Lock_csv( dir1+"/ztmp/myfile5.csv"
                      ,dirlock=dir1+"/ztmp/lock_hash", max_locktime= 600 )
  index1.add( [ x ], ttl= 600 ) 



def testcsv2(x=2 ):
  index1 = S3Lock_csv( dir1+"/ztmp/myfile5.csv"
                      ,dirlock=dir1+"/ztmp/lock_hash", max_locktime= 600 )
  index1.delete( [ x] ) 
  time.sleep(40)



def testcsv_all(add=1, npool=5):
    """

          python src/utils/utils_s3.py testcsv_all  --add 1  --npool 10 &

          python src/utils/utils_s3.py testcsv_all  --add 0  --npool 20 &


    """
    if add == 1:
        npool   = npool
        pool    = mp.Pool(processes = npool)
        results = []
        for i in range(1, 1+npool):
           results.append(pool.apply_async(testcsv1, (i * 10 ,))) 
        
        for r in results:
            log(r.get())

    else:  
        npool   = npool
        pool    = mp.Pool(processes = npool)
        results = []
        for i in range(1, 1+npool):
           results.append(pool.apply_async(testcsv2, (i * 10 ,))) 
        
        for r in results:
            log(r.get())



def testcsv_getfree(add=1, npool=5):
    """
      python src/utils/utils_s3.py testcsv_getfree   


      locktime ; 1800 : 60*30 + 7  mins
      ttl insert:  60*15 + 7--> auto-expire x3 frequenct: lose
      update value:  60*5 + 3


    """
    flist = [ str(i*10) for i in  range(0, 12) ]
    index1 = S3Lock_csv( dir1+"/ztmp/myfile5.csv"
                        ,dirlock=dir2+"/ztmp/lock_hash", max_locktime= 150 )
    ifree = index1.get_free(flist , ttl= 80) 
    log(ifree)



def testcsv_getfree2(add=1, npool=3):
      """
           python src/utils/utils_s3.py testcsv_getfree2  --npool 50

      """
      npool   = npool
      pool    = mp.Pool(processes = npool)
      results = []
      for i in range(1, 1+npool):
         results.append(pool.apply_async(testcsv_getfree, (i * 10 ,))) 
      
      for r in results:
          log(r.get())



def testcsv_getfree4(add=1, npool=5):
    """
      python src/utils/utils_s3.py testcsv_getfree4   


      locktime ; 1800 : 60*30 + 7  mins
      ttl insert:  60*15 + 7--> auto-expire x3 frequenct: lose
      update value:  60*5 + 3


    """
    flist = [ str(i*10) for i in  range(0, 12) ]
    index1 = S3Lock_csv( dir1 + "/ztmp/news_urls/index.csv"
                        ,dirlock= dir2+"/ztmp/lock_hash", max_locktime= 60*1 )

    #### At start
    ifree = index1.get_free(flist , ttl= 60* 15 ) 
    log(ifree)

    #### During process cycletime=
    keynew = ['1']  
    cycletime= 60*5
    index1.add(keynew, ttl= cycletime*3, unique_key=1)



#######################################################################
class S3lock:
    def __init__(self, dirlock:str, ntry_max=20, ntry_sleep=1,
                 delay_start=10, n_concurrent=10, min_latency =2,
                 max_locktime= 300 ):
        """
           Atomic Read, Atomic write on S3 text file.
           Many readers, many writers ---> All atomic.

        """
        self.s3      = boto3.client('s3')
        self.dirlock = dirlock  #### where all the lock are stored.

        self.ntry_max   = ntry_max
        self.ntry_sleep = ntry_sleep

        ### prevent race condition
        self.delay_start  = delay_start
        self.n_concurrent = n_concurrent
        self.min_latency = min_latency

        self.max_locktime = max_locktime


    def to_int(self, x):
        try:
            return int(x)
        except:  
            return -1


    def hashx(self, xstr:str, seed=123)->int:
        """ Computes xxhash value """
        #import xxhash
        #return xxhash.xxh64_intdigest(str(xstr), seed=seed)
        xstr2 = str(xstr).replace("s3://", "").replace("/","-").replace(".","_")
        return xstr2


    def sleept(self, ntry=0, msg=""):
        tsleep = self.ntry_sleep * 2**ntry + random.uniform(2, 2+self.n_concurrent)
        log( os.getpid(), msg, f": Retry - {ntry}, {tsleep} ")      
        time.sleep( tsleep )              


    def s3_file_mtime(self, bucket, lock_key):
          from datetime import timezone
          from tzlocal import get_localzone
          local_tz = get_localzone() ### Need to conver to local timezone; othermismtch

          try:
              response = self.s3.head_object(Bucket= bucket, Key= lock_key )
              last_modified  = response['LastModified'].astimezone(local_tz)
              unix_timestamp = int(time.mktime(last_modified.timetuple()))
              # log(lock_key,": last_udpate: ", unix_timestamp, last_modified )
              #log("nowL:", datetime.fromtimestamp(time.time() ))
              return unix_timestamp
          except Exception as e:
              log(e)
              dt = time.time() - 3600 *10 
              return dt

    def s3_path_split(self, dirfile2):
        dirfile2 = dirfile2.replace("s3://", "").replace('//', "/").split('/')
        bucket, lock_key = dirfile2[0],  "/".join(dirfile2[1:] )
        return bucket, lock_key

    def s3_reset_lock(self, bucket, lock_key):
        ### create file
        try:
            self.s3.put_object(Bucket=bucket, Key=lock_key, Body='0')
            lock_code = 0
        except:    
            lock_code = 0

        return lock_code


    def lock(self, dirfile:str):
        """  Wait until we can lock the file.
             path1/path2/path2/dirlock/

        """
        dirfile2         = self.dirlock + "/" + str(self.hashx(dirfile))
        bucket, lock_key = self.s3_path_split(dirfile2)
      
        delay = random.uniform(1, 1 + self.n_concurrent*self.min_latency )
        log(dirfile, ': start locking', delay)
        time.sleep(delay)      
          

        ##### Wait until the file is Un-locked --> ntry_max
        ntry = 0
        while ntry < self.ntry_max:
            try: 
                #self.s3.head_object(Bucket= bucket, Key= lock_key)
                lock_code = self.s3.get_object(Bucket= bucket, Key= lock_key)["Body"].read().decode()
            except Exception as e:
                log(dirfile, bucket, lock_key, e)
                lock_code = self.s3_reset_lock(bucket, lock_key)

            mtime = self.s3_file_mtime(bucket, lock_key)
            dt    = time.time() - (mtime + self.max_locktime)
            log('lock overtime', dt)
            if dt > 0.0 :
                log(dirfile, ": reset lockfile to zero, overtime")
                lock_code = self.s3_reset_lock(bucket, lock_key)


            #### File has zero value: Not locked --> we can lock it
            if self.to_int(lock_code) == 0:
                break

            ntry+=1
            msg = f"{dirfile} :waiting unlock"
            self.sleept( ntry, msg) ### wait a bit untl the file is unlocked

        if  ntry >= self.ntry_max:
            log("Maximum retries reached. File has been locked by someone else.")
            return False


        ##### Insert Lock into the file with timestamp ############################
        ntry = 0
        while ntry < self.ntry_max:
            try:
                lock_code1 = str(time.time_ns())
                self.s3.put_object(Bucket= bucket, Key= lock_key, Body=lock_code1)

                ### Check if the write was done properly
                lock_code2 = self.s3.get_object(Bucket= bucket, Key= lock_key)["Body"].read().decode()
                if lock_code2 == lock_code1:
                    log(dirfile ,": Locked: ", lock_code2)
                    return True

                ntry+=1
                self.sleept(ntry)
            except Exception as e:
                log(e)
                time.sleep(1)

        if  ntry >= self.ntry_max:
            log("Maximum retries reached. The File is in use.")
            return False

        return False
    

    def unlock(self, dirfile:str):
        dirfile2         = self.dirlock + "/" + str(self.hashx(dirfile))
        bucket, lock_key = self.s3_path_split(dirfile2)

        ntry = 0
        while ntry < self.ntry_max:
            try:
                self.s3.put_object(Bucket= bucket, Key= lock_key, Body='0')
                lock_code = self.s3.get_object(Bucket= bucket, Key= lock_key)["Body"].read().decode()
                if self.to_int(lock_code) == 0:
                    log(dirfile ,": Unlocked")
                    return True

                ntry+=1
                self.sleept(self, ntry)

            except Exception as e:
                log(e)

        if  ntry >= self.ntry_max:
            log("Maximum retries reached. Unable to unlock file after update.")
            return False
        
        return False





######################################################################
class S3Lock_csv:
    def __init__(self, dircsv:str, dirlock:str, ntry_max=20, max_locktime= 200):
        # self.s3 = boto3.client('s3',)
        self.dircsv  = dircsv
        self.dirlock = dirlock
        self.s3lock  = S3lock(dirlock, max_locktime= max_locktime)
        self.ntry_max     = ntry_max
        self.max_locktime = max_locktime
        self.cols = ['key', 'val', 'ttl']
        log('dirlock', self.dirlock)
        log('dircsv',  self.dircsv)


    def read_atomic(self, ttl=600):
        """
             https://aws-sdk-pandas.readthedocs.io/en/stable/ 

        """
        islock = self.s3lock.lock(self.dircsv, ntry_max= self.ntry_max)
        if not islock:
           return False

        df = wr.s3.read_csv(dir2, index=False, sep="\t" )

        tnow = time.time()
        df = df[ df['ttl'].apply(lambda x: x > tnow ) ]

        self.s3lock.unlock(self.dircsv) 
        return df    


    def wait_unlock(self,):
        islock = self.s3lock.lock(self.dircsv, ntry_max= self.ntry_max)
        ntry = 0
        while islock and ntry < self.ntry_max :
            time.sleep(5*ntry)
            islock = self.s3lock.lock(self.dircsv, ntry_max= self.ntry_max)
            ntry += 1

        return ntry 


    def add(self, newrows:list=None, ttl= 3600, unique_key=1):

        if len(newrows)< 1: return False 
        if not isinstance(newrows[0], list) and not isinstance(newrows[0], tuple) :
             newrows = [ (x1, f"1-{os.getpid()}") for x1 in newrows ]

        islock = self.s3lock.lock(self.dircsv)
        if not islock:
           return False

        try:
            try :
               df   = pd_read_file_s3(self.dircsv, sep="\t")
            except Exception as e:
               log(self.dircsv, e)
               df = None 
          
            if df is None :   
               df = [ [ str(x1), str(x2), time.time() + ttl ] for (x1,x2) in newrows      ]
               df = pd.DataFrame(newrows, columns= ["key", "val", "ttl" ] )
               df = df.drop_duplicates("key")  if unique_key == 1 else df
               wr.s3.to_csv(df, self.dircsv, index=False, sep="\t" )
               log(self.dircsv, ': added: ', len(newrows))
               self.s3lock.unlock(self.dircsv) 
               return None
      

            log(df.shape) 
            newrows = [ [ str(x1), str(x2), time.time() + ttl ] for (x1,x2) in newrows      ]
            newrows = pd.DataFrame(newrows, columns= ["key", "val", "ttl" ] )
            df      = pd.concat((df, newrows)) if len(df) > 0 else newrows
            log(df.shape)

            t0 = time.time()
            df = df[ df['ttl'].apply(lambda x: x > t0 ) ]

            if unique_key == 1:
               df = df.drop_duplicates("key")
            log(self.dircsv    ,'size: ', len(df))

            wr.s3.to_csv(df, self.dircsv, index=False, sep="\t" )
            log(self.dircsv, ': added: ', len(newrows))
        except Exception as e:
            log(e)
            self.s3lock.unlock(self.dircsv) 
            return False

        self.s3lock.unlock(self.dircsv) 
        return True


    def delete(self, keylist:list):
        log(self.dircsv, ": deleting start")
        islock = self.s3lock.lock(self.dircsv)
        if not islock:
           return False


        try :
            df = wr.s3.read_csv(self.dircsv, sep="\t")
            log(df.shape)

            for xi in keylist:
               df = df[ df["key"] != xi ]

            t0 = time.time()
            df = df[ df['ttl'].apply(lambda x: x > t0 ) ]

            wr.s3.to_csv(df, self.dircsv, index=False, sep="\t" )
            log(self.dircsv, ': deleted end: ', df.shape)

        except Exception as e:
            log(e)
            self.s3lock.unlock(self.dircsv) 
            return False

        self.s3lock.unlock(self.dircsv) 
        return True


    def get_free(self, keylist_ref:list, ttl=600, dowait=1):
        log(self.dircsv, ": get_free start")
        import random, awswrangler as wr

        ntry = -1
        while ntry < self.ntry_max:
            ntry += 1

            islock = self.s3lock.lock(self.dircsv)
            if not islock:
               return None

            try:
               df = wr.s3.read_csv(self.dircsv, sep="\t")
            except Exception as e:
               log(e)
               df = pd.DataFrame([], columns= self.cols )   


            if len(df) > 0:
                t0 = time.time()
                df = df[ df['ttl'].apply(lambda x: x > t0 ) ]

                notfree = set([  str(xi).strip() for xi in  df['key'].values]) if len(df)>0 else set()
                lfree   = [ xi for xi in keylist_ref if str(xi).strip() not in notfree ]
                log('notfree: ', notfree)
                log('free: '   , lfree)
            else:
                lfree = keylist_ref            


            if len(lfree)>0:
               idx  = random.randint(1, len(lfree))-1 ### both are included
               key1 = lfree[ idx ] 
               # log('idx:', idx)
               df1 = pd.DataFrame([[ key1, f"2-{os.getpid()}", time.time() + ttl ]], columns= self.cols)               
               df  = pd.concat((df, df1 )) if len(df)>0 else df1
                   
               wr.s3.to_csv(df, self.dircsv, index=False, sep="\t" )
               log(self.dircsv, ': added : ', key1)
               self.s3lock.unlock(self.dircsv) 
               return key1

            self.s3lock.unlock(self.dircsv) 

            #### Wait long time
            tsleep = 30 + ntry*ntry*5 + random.uniform(1, 1+ntry*2 )
            log(self.dircsv, ": get_free : waiting for a free key", tsleep)
            time.sleep(tsleep)


        log("get_free: not more free key, expiring")
        return None







#######################################################################
class cloudLock:
    def __init__(self, dirlock="s3://bucket", ntry_max=20, ntry_sleep=5):
        import fsspec, os
        self.dirlock      = dirlock if dirlock[-1] != "/" else dirlock[:-1]

        storage_type= "local"
        if "s3://" in dirlock:  storage_type= "s3"
        elif "gs://" in dirlock:  storage_type= "gcs"

        self.storage_type = storage_type
        if storage_type == 'local':
            self.fs = fsspec.filesystem('file')
        else:
            self.fs = fsspec.filesystem(storage_type, anon=False)

        self.ntry_max   = ntry_max   
        self.ntry_sleep = ntry_sleep  


    def lock(self, file_path:str):
        lock_path = self._get_lock_path(file_path)
                
        ntry = 0
        while ntry < self.ntry_max:
            try:
               time0 = str(time.time_ns()) 
               with self.fs.open(lock_path, 'wb') as lock_file:
                   lock_file.write(time0)

                   val = self.read_file(lock_path) ### check if writing is correct
                   if str(val) == str(time0) : 
                      break 

            except Exception as e :       
               log(lock_path, "blocked")


            ntry+=1
            self.sleept(self, ntry)

        if  ntry >= self.ntry_max:
            log("Maximum retries reached. The File is blocked")
            return False

        return True
    

    def unlock(self, file_path:str):
        lock_path   = self._get_lock_path(file_path)
                
        ntry = 0
        while ntry < self.ntry_max:
            try:
                val = self.read_file(lock_path) ### check if writing is correct
                if val is None or len(val)== "":
                   self.delete_file(lock_path)
                   return True

            except Exception as e :       
               log(lock_path, "blocked")

            ntry+=1
            self.sleept(self, ntry)

        if  ntry >= self.ntry_max:
            log("Maximum retries reached. The File is blocked")
            return False

        return True

    def read_file(self, file_path):
        lock_path = self._get_lock_path(file_path)
        ntry= 0
        while ntry < self.ntry_max:
          try :  
               with self.fs.open(lock_path, 'rb') as lock_file:
                   val = lock_file.read()
                   return val

          except Exception as e :
            pass

          ntry +=1
          self.sleept(ntry)


    def delete_file(self, file_path):
        lock_path = self._get_lock_path(file_path)
        ntry= 0
        while ntry < self.ntry_max:
          try :  
             if self.fs.exists(lock_path):
                  self.fs.rm(lock_path)
          except Exception as e :
             ntry +=1
             self.sleept(ntry)


    def _get_lock_path(self, file_path):
        return self.dirlock + "/" + str(self.hashx(file_path))

    def hashx(self, xstr:str, seed=123)->int:
        """ Computes xxhash value """
        import xxhash
        return xxhash.xxh64_intdigest(str(xstr), seed=seed)

    def sleep(self, ntry):
        dtsleep = 2.0 + self.ntry_sleep * ntry + random.uniform(0, 1)
        log(f"Retry - {ntry}, retry in {dtsleep}")      
        time.sleep( dtsleep )              

            



if __name__ == "__main__":
    import fire 
    fire.Fire()




"""


    2521: None
    (py39) \W$            python src/utils/utils_s3.py testcsv_getfree2  --npool 50                     
    72806: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72806: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72806: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72806: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 13.16026551281297
    72807: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72807: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72807: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72807: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 18.501124271092102
    72802: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72802: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72802: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72802: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 26.965862187395384
    72799: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72799: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72799: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72799: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 3.2237954709390904
    72800: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72800: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72800: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72800: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 23.65347252386913
    72797: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72797: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72797: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72797: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 7.600205208815586
    72809: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72809: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72809: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72809: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 21.459343867896592
    72808: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72808: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72808: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72808: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 4.696381441823206
    72812: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72812: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72812: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72812: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 20.114843501591913
    72814: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72814: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72814: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72814: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 12.050693329944032
    72796: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72796: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72796: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72796: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 10.616809664274339
    72817: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72817: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72817: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72817: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 23.908401779109578
    72811: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72811: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72811: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72811: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 19.26854853308978
    72803: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72803: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72801: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72803: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72801: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72801: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72795: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72803: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 21.17858467464476
    72801: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 8.534752095806027
    72805: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72795: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72805: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72795: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72805: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72798: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72795: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 3.8905535336811528
    72805: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 25.127489112269778
    72798: dircsv s3://72818: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72816: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72818: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72816: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72818: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72816: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72810: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72810: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72818: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 4.8136991696411995
    72816: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 11.42264609661829
    72813: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72823: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72810: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72823: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72810: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 5.37646833812779
    72823: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72813: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72813: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72813: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 12.193919708239479
    72840: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72823: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 27.236592989348328
    72840: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72840: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72840: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 10.111911703581189
    72820: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72820: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72820: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72820: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 28.32003439139043
    72824: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72824: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72824: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72824: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 28.749504297153415
    72828: dirlock s3://72822: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72827: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72829: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72835: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72819: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    edge-ml-dev/ztmp/myfile5.csv
    72815: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72819: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72837: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72829: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72827: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72829: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72819: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72827: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72837: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72837: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72829: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 12.231941197256111
    72804: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72822: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72837: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 3.5599895234215895
    72827: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 9.897154399923613
    72822: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72831: dirlock s3://edge-version-dev--use1-az4-72835: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72822: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 13.471747338753014
    -x-s3/ztmp/lock_hash
    72828: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72835: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72828: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72826: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72819: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 10.866303037591287
    72831: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72831: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72826: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72826: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72831: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 29.71453641255825
    72835: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 14.351348447547274
    72828: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 26.6529635579056
    72826: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 27.687467929597847
    72815: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72804: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72804: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72798: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72804: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 27.75254035779374
    72798: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 6.877077414635961
    72815: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72815: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 6.798720516936269
    72839: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72839: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72839: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72839: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 26.34076879325059
    72843: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72843: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72843: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72843: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 2.6895793871756606
    72825: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72825: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72825: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72825: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 15.17695311212308
    72841: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72841: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72841: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72841: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 28.573717144630105
    72830: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72830: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72830: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72830: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 2.9532811691737386
    72842: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72842: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72842: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72842: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 5.930913846725529
    72834: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72834: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72834: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72834: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 9.755201411197781
    72821: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72821: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72821: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72821: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 19.40142668662981
    72838: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72838: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72838: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72838: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 8.857592468006938
    72833: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72833: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72833: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72833: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 6.4946651417365295
    72832: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72832: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72832: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72832: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 6.647043085656463
    72836: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72836: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72836: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72836: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 28.71836072422114
    72844: dirlock s3://edge-version-dev--use1-az4--x-s3/ztmp/lock_hash
    72844: dircsv s3://edge-ml-dev/ztmp/myfile5.csv
    72844: s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    72844: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 7.385450283152567
    72843: lock overtime -127.03782200813293
    72830: lock overtime -126.92893600463867
    72799: lock overtime -126.90441608428955
    72843: 72843  : Retry - 1, 10.10608944842623 
    72830: 72830  : Retry - 1, 6.127968000985074 
    72799: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395384095610000
    72837: lock overtime -149.33212995529175
    72837: 72837 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 8.771583458599126 
    72795: lock overtime -149.1834909915924
    72795: 72795 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 10.94412529791402 
    72808: lock overtime -148.38636589050293
    72808: 72808 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 10.026562658019717 
    72799: notfree:  {'40', '50', '110', '20', '30'}
    72799: free:  ['0', '10', '60', '70', '80', '90', '100']
    72818: lock overtime -148.18799805641174
    72818: 72818 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 6.331076553977843 
    72810: lock overtime -147.61959195137024
    72810: 72810 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 5.991629663915372 
    72799: s3://edge-ml-dev/ztmp/myfile5.csv : added :  60
    72799: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72799: 60
    72842: lock overtime -148.95289492607117
    72842: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395387047132000
    72833: lock overtime -149.38844299316406
    72833: 72833 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 12.749723629630948 
    72832: lock overtime -149.25245690345764
    72832: 72832 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 11.696572519027246 
    72815: lock overtime -149.1973340511322
    72815: 72815 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 13.517275450232507 
    72798: lock overtime -149.08019614219666
    72798: 72798 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 8.746569955808123 
    72797: lock overtime -148.54947781562805
    72797: 72797 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 12.121749396320514 
    72844: lock overtime -148.49937510490417
    72844: 72844 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 11.467847952883748 
    72842: notfree:  {'30', '110', '60', '20', '50', '40'}
    72842: free:  ['0', '10', '70', '80', '90', '100']
    72842: s3://edge-ml-dev/ztmp/myfile5.csv : added :  80
    72801: lock overtime -147.5690369606018
    72801: 72801 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 9.587910425527562 
    72842: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72842: 80
    72838: lock overtime -149.0473988056183
    72838: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395389952636000
    72834: lock overtime -149.12107491493225
    72834: 72834 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 6.642592201259987 
    72827: lock overtime -149.03933000564575
    72827: 72827 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 6.996223087441731 
    72840: lock overtime -148.84825086593628
    72840: 72840 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 8.78270583418401 
    72830: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395390733013000
    72838: notfree:  {'80', '50', '40', '110', '60', '20', '30'}
    72838: free:  ['0', '10', '70', '90', '100']
    72796: lock overtime -148.48243188858032
    72796: 72796 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 13.70428968531666 
    72819: lock overtime -148.11384201049805
    72819: 72819 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 7.7899032476235925 
    72830: notfree:  {'40', '20', '80', '50', '30', '110', '60'}
    72830: free:  ['0', '10', '70', '90', '100']
    72838: s3://edge-ml-dev/ztmp/myfile5.csv : added :  90
    72816: lock overtime -147.59312891960144
    72816: 72816 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 12.720331426009498 
    72810: lock overtime -149.27656507492065
    72810: 72810 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 2, 14.03036872405898 
    72838: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72838: 90
    72814: lock overtime -149.03048610687256
    72830: s3://edge-ml-dev/ztmp/myfile5.csv : added :  10
    72818: lock overtime -148.9585678577423
    72813: lock overtime -148.8027060031891
    72829: lock overtime -148.74639320373535
    72814: 72814  : Retry - 1, 7.832682802800034 
    72830: unsupported operand type(s) for ** or pow(): 'int' and 'S3lock'
    72818: 72818  : Retry - 1, 7.530148176115815 
    72813: 72813  : Retry - 1, 5.7612349987861755 
    72829: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395393253630000
    72806: lock overtime -149.10343194007874
    72806: 72806 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 9.504489910957187 
    72830: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72830: 10
    72837: lock overtime -148.6613209247589
    72822: lock overtime -148.47344589233398
    72829: notfree:  {'110', '80', '10', '40', '50', '30', '60', '20'}
    72829: free:  ['0', '70', '90', '100']
    72837: 72837  : Retry - 1, 9.110900381670739 
    72822: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395394526589000
    72835: lock overtime -148.60662698745728
    72835: 72835 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 13.81267291663211 
    72829: s3://edge-ml-dev/ztmp/myfile5.csv : added :  70
    72843: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395394590627000
    72829: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72829: 70
    72822: notfree:  {'10', '70', '40', '30', '110', '60', '20', '50', '80'}
    72822: free:  ['0', '90', '100']
    72825: lock overtime -148.82127404212952
    72808: lock overtime -149.41605186462402
    72795: lock overtime -149.37768077850342
    72843: notfree:  {'60', '20', '30', '110', '40', '70', '10', '80', '50'}
    72843: free:  ['0', '90', '100']
    72825: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395396178766000
    72822: s3://edge-ml-dev/ztmp/myfile5.csv : added :  90
    72795: 72795  : Retry - 1, 4.440592283229359 
    72808: 72808  : Retry - 1, 6.938970822605985 
    72822: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72822: 90
    72843: s3://edge-ml-dev/ztmp/myfile5.csv : added :  90
    72798: lock overtime -149.45748090744019
    72825: notfree:  {'50', '110', '60', '10', '20', '90', '80', '70', '30', '40'}
    72825: free:  ['0', '100']
    72843: unsupported operand type(s) for ** or pow(): 'int' and 'S3lock'
    72798: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395397542548000
    72825: s3://edge-ml-dev/ztmp/myfile5.csv : added :  100
    72834: lock overtime -149.57502794265747
    72834: 72834 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 2, 13.592443506956988 
    72843: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72843: 90
    72827: lock overtime -149.1308159828186
    72825: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72825: 100
    72798: notfree:  {'80', '40', '30', '90', '70', '10', '110', '20', '60', '100', '50'}
    72798: free:  ['0']
    72807: lock overtime -148.7941439151764
    72827: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395398869232000
    72807: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395399205882000
    72798: s3://edge-ml-dev/ztmp/myfile5.csv : added :  0
    72801: lock overtime -149.07676601409912
    72801: 72801 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 2, 6.9875758818904 
    72813: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395399494493000
    72811: lock overtime -149.85308384895325
    72811: 72811 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 13.581219690677438 
    72798: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72798: 0
    72832: lock overtime -149.65668106079102
    72827: notfree:  {'50', '110', '20', '80', '10', '100', '90', '60', '70', '0', '40', '30'}
    72827: free:  []
    72821: lock overtime -149.50446891784668
    72819: lock overtime -149.41657090187073
    72807: notfree:  {'90', '80', '40', '100', '70', '0', '20', '60', '110', '10', '50', '30'}
    72807: free:  []
    72840: lock overtime -149.13907194137573
    72832: 72832  : Retry - 1, 6.409231433612831 
    72844: lock overtime -149.1174280643463
    72827: unsupported operand type(s) for ** or pow(): 'int' and 'S3lock'
    72812: lock overtime -149.0510070323944
    72813: notfree:  {'50', '70', '40', '60', '0', '90', '80', '20', '10', '110', '30', '100'}
    72813: free:  []
    72821: 72821  : Retry - 1, 8.44537952838519 
    72819: 72819  : Retry - 1, 4.165007914259117 
    72807: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72807: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    72833: lock overtime -149.77754712104797
    72840: 72840  : Retry - 1, 12.549165509065345 
    72827: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72827: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    72844: 72844  : Retry - 1, 10.83103889067411 
    72797: lock overtime -149.53837490081787
    72797: 72797 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 2, 15.865145457786944 
    72812: 72812  : Retry - 1, 6.9252415214719205 
    72813: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72813: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    72833: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395401222472000
    72803: lock overtime -148.9475290775299
    72803: 72803 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 11.329213057031334 
    72795: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395401585190000
    72815: lock overtime -148.8093068599701
    72815: 72815 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 2, 10.009482179051151 
    72809: lock overtime -149.66910004615784
    72809: 72809 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 7.348067179391326 
    72814: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395401335298000
    72833: notfree:  {'30', '60', '90', '0', '20', '40', '50', '100', '70', '80', '110', '10'}
    72833: free:  []
    72818: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395401108874000
    72795: notfree:  {'60', '0', '10', '80', '40', '90', '50', '110', '30', '100', '70', '20'}
    72795: free:  []
    72833: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72833: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    72814: notfree:  {'20', '10', '70', '0', '80', '100', '30', '90', '50', '60', '110', '40'}
    72814: free:  []
    72795: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72795: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    72818: notfree:  {'10', '90', '40', '70', '0', '50', '20', '110', '30', '80', '100', '60'}
    72818: free:  []
    72814: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72814: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    72818: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72818: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    72806: lock overtime -149.68472003936768
    72800: lock overtime -149.4889841079712
    72817: lock overtime -149.18750405311584
    72806: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395404315304000
    72800: 72800  : Retry - 1, 11.63744305999802 
    72837: 72837  : Retry - 2, 14.918160888202832 
    72808: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395404081649000
    72817: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395404812604000
    72819: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395405286899000
    72806: notfree:  {'50', '10', '80', '0', '70', '110', '60', '90', '30', '100', '40', '20'}
    72806: free:  []
    72805: lock overtime -149.00750994682312
    72805: 72805 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 10.419767249788485 
    72816: lock overtime -148.9705889225006
    72816: 72816 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 2, 6.6323600824086935 
    72808: notfree:  {'70', '0', '40', '90', '10', '20', '30', '60', '100', '110', '80', '50'}
    72808: free:  []
    72796: lock overtime -148.88838601112366
    72796: 72796 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 2, 12.465385277983346 
    72817: notfree:  {'10', '40', '60', '80', '70', '0', '100', '20', '50', '30', '90', '110'}
    72817: free:  []
    72806: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72806: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    72808: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72808: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    72819: notfree:  {'10', '60', '100', '70', '20', '40', '50', '30', '0', '90', '110', '80'}
    72819: free:  []
    72817: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72817: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    72819: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72819: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    72839: lock overtime -149.57274913787842
    72828: lock overtime -149.33412289619446
    72810: lock overtime -149.32658410072327
    72802: lock overtime -149.234472990036
    72801: lock overtime -149.18359303474426
    72839: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395407427274000
    72828: 72828  : Retry - 1, 8.626825732397355 
    72810: 72810  : Retry - 1, 8.835878810565623 
    72802: 72802  : Retry - 1, 9.571053037930653 
    72823: lock overtime -149.6607129573822
    72823: 72823 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 4.966359010741914 
    72832: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395407291300000
    72801: 72801  : Retry - 1, 11.358133828784535 
    72826: lock overtime -149.3000340461731
    72826: 72826 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 5.556051973920019 
    72804: lock overtime -149.2802770137787
    72804: 72804 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 8.701540551135636 
    72839: notfree:  {'0', '90', '20', '10', '110', '70', '30', '80', '40', '50', '60', '100'}
    72839: free:  []
    72820: lock overtime -148.69425415992737
    72820: 72820 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 4.252210788426948 
    72832: notfree:  {'110', '90', '0', '40', '70', '20', '50', '30', '60', '80', '10', '100'}
    72832: free:  []
    72812: 72812  : Retry - 2, 9.88945275057294 
    72839: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72839: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    72841: lock overtime -149.42311191558838
    72824: lock overtime -149.25808215141296
    72836: lock overtime -149.2457399368286
    72832: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72832: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    72835: lock overtime -148.91498708724976
    72841: 72841  : Retry - 1, 5.121421014229017 
    72824: 72824  : Retry - 1, 10.374613117524376 
    72836: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395409754284000
    72821: 72821  : Retry - 2, 6.6729549042488205 
    72809: lock overtime -149.40400886535645
    72809: 72809 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 2, 14.795838278667285 
    72835: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395410085132000
    72831: lock overtime -149.29551792144775
    72831: 72831 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 10.001900087558052 
    72836: notfree:  {'90', '80', '0', '70', '50', '10', '20', '100', '60', '30', '40'}
    72836: free:  ['110']
    72835: notfree:  {'100', '90', '0', '40', '20', '80', '60', '30', '10', '50', '70'}
    72835: free:  ['110']
    72836: s3://edge-ml-dev/ztmp/myfile5.csv : added :  110
    72835: s3://edge-ml-dev/ztmp/myfile5.csv : added :  110
    72836: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72836: 110
    72834: lock overtime -149.0851809978485
    72835: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72835: 110
    72815: lock overtime -148.88345003128052
    72844: 72844  : Retry - 2, 8.610292305091415 
    72834: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395412914865000
    72816: lock overtime -149.41415405273438
    72816: 72816 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 3, 13.951728938751408 
    72815: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395413116581000
    72823: lock overtime -149.32147312164307
    72823: 72823 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 2, 8.781578823333843 
    72820: lock overtime -149.08289694786072
    72820: 72820 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 2, 12.322363531716455 
    72803: lock overtime -148.71546697616577
    72803: 72803 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 2, 12.376399261108645 
    72834: notfree:  {'100', '0', '40', '50', '90', '80', '30', '60', '70', '20', '10', '110'}
    72834: free:  []
    72826: lock overtime -148.39422416687012
    72826: 72826 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 2, 14.058136325516346 
    72815: notfree:  {'70', '60', '20', '100', '80', '40', '50', '30', '10', '0', '90', '110'}
    72815: free:  []
    72811: lock overtime -148.3397397994995
    72811: 72811 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 2, 13.344484937675364 
    72834: unsupported operand type(s) for ** or pow(): 'int' and 'S3lock'
    72840: 72840  : Retry - 2, 13.753357934294339 
    72815: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72815: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    72834: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72834: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    72841: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395415240404000
    72841: notfree:  {'80', '50', '10', '60', '20', '110', '100', '0', '30', '90', '70', '40'}
    72841: free:  []
    72841: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72841: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    72805: lock overtime -149.68946194648743
    72800: 72800  : Retry - 2, 7.714211394297384 
    72805: 72805  : Retry - 1, 4.597229231141877 
    72828: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395416828879000
    72810: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395417061591000
    72797: lock overtime -148.71989393234253
    72797: 72797 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 3, 14.211295249026975 
    72804: lock overtime -148.66757082939148
    72804: 72804 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 2, 10.730061639867657 
    72828: notfree:  {'100', '60', '50', '10', '40', '80', '90', '70', '30', '0', '110'}
    72828: free:  ['20']
    72802: 72802  : Retry - 2, 14.397246567134456 
    72821: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395417216101000
    72810: notfree:  {'40', '0', '50', '60', '10', '110', '100', '90', '80', '30', '70'}
    72810: free:  ['20']
    72796: lock overtime -148.52665901184082
    72796: 72796 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 3, 11.46393624081325 
    72828: s3://edge-ml-dev/ztmp/myfile5.csv : added :  20
    72810: s3://edge-ml-dev/ztmp/myfile5.csv : added :  20
    72821: notfree:  {'20', '0', '80', '60', '10', '70', '110', '100', '40', '30', '90', '50'}
    72821: free:  []
    72828: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72828: 20
    72810: unsupported operand type(s) for ** or pow(): 'int' and 'S3lock'
    72821: unsupported operand type(s) for ** or pow(): 'int' and 'S3lock'
    72812: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395419391020000
    72801: 72801  : Retry - 2, 6.186508041523848 
    72810: unsupported operand type(s) for ** or pow(): 'int' and 'S3lock'
    72821: unsupported operand type(s) for ** or pow(): 'int' and 'S3lock'
    72837: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395420018081000
    72812: notfree:  {'60', '10', '90', '50', '100', '110', '0', '40', '30', '20', '70', '80'}
    72812: free:  []
    72810: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72810: 20
    72821: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72821: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    72831: lock overtime -149.38449501991272
    72824: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395420654708000
    72812: unsupported operand type(s) for ** or pow(): 'int' and 'S3lock'
    72837: notfree:  {'110', '100', '50', '80', '10', '90', '60', '30', '0', '20', '40', '70'}
    72837: free:  []
    72831: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395421615527000
    72812: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72812: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    72837: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72837: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    72824: notfree:  {'60', '30', '50', '0', '80', '40', '110', '90', '10', '100', '70', '20'}
    72824: free:  []
    72805: 72805  : Retry - 2, 7.311004270049628 
    72844: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395421928747000
    72831: notfree:  {'60', '70', '50', '30', '80', '10', '110', '0', '90', '40', '100', '20'}
    72831: free:  []
    72824: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72824: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    72823: lock overtime -148.65157413482666
    72831: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72831: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    72823: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395423348453000
    72844: notfree:  {'110', '60', '80', '10', '90', '100', '0', '20', '70', '50', '40', '30'}
    72844: free:  []
    72844: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72844: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    72823: notfree:  {'50', '70', '80', '0', '110', '30', '60', '90', '10', '100', '20'}
    72823: free:  ['40']
    72823: s3://edge-ml-dev/ztmp/myfile5.csv : added :  40
    72823: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72823: 40
    72809: lock overtime -148.70289516448975
    72800: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395425507111000
    72809: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395426297134000
    72820: lock overtime -148.8743748664856
    72820: 72820 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 3, 17.657961473430202 
    72801: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395426994593000
    72803: lock overtime -149.42438197135925
    72803: 72803 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 3, 16.313133223619776 
    72800: notfree:  {'110', '90', '100', '70', '60', '10', '20', '30', '0', '80', '40', '50'}
    72800: free:  []
    72809: notfree:  {'40', '100', '50', '20', '90', '70', '60', '0', '110', '10', '80'}
    72809: free:  ['30']
    72800: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72800: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    72801: notfree:  {'90', '40', '110', '80', '20', '60', '10', '70', '100', '50', '0'}
    72801: free:  ['30']
    72816: lock overtime -148.4163839817047
    72809: s3://edge-ml-dev/ztmp/myfile5.csv : added :  30
    72811: lock overtime -149.05927205085754
    72809: unsupported operand type(s) for ** or pow(): 'int' and 'S3lock'
    72816: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395428583645000
    72801: s3://edge-ml-dev/ztmp/myfile5.csv : added :  30
    72811: 72811  : Retry - 1, 11.847550710539606 
    72826: lock overtime -149.42191696166992
    72826: 72826 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 3, 15.609488525548619 
    72809: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72809: 30
    72801: unsupported operand type(s) for ** or pow(): 'int' and 'S3lock'
    72840: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395428806338000
    72804: lock overtime -149.01988816261292
    72804: 72804 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 3, 14.371927665384437 
    72816: notfree:  {'10', '80', '90', '70', '100', '50', '60', '30', '40', '110', '0', '20'}
    72816: free:  []
    72801: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72801: 30
    72816: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72816: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    72840: notfree:  {'70', '60', '40', '100', '50', '10', '90', '20', '30', '80', '110', '0'}
    72840: free:  []
    72840: unsupported operand type(s) for ** or pow(): 'int' and 'S3lock'
    72805: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395430270361000
    72796: lock overtime -149.1391417980194
    72796: 72796 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 4, 20.350344115004443 
    72840: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72840: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    72807: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 30.072339757863084
    72805: notfree:  {'100', '0', '40', '50', '80', '20', '90', '110', '10', '60', '30', '70'}
    72805: free:  []
    72827: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 15.84583612601974
    72813: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 9.68227119211292
    72805: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72805: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    72797: lock overtime -148.55056309700012
    72797: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395433449565000
    72833: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 7.504608565694277
    72802: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395433330335000
    72795: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 28.248747202400715
    72814: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 8.338421121055841
    72797: notfree:  {'10', '80', '40', '110', '30', '60', '100', '50', '0', '90', '20', '70'}
    72797: free:  []
    72818: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 30.893637441446515
    72802: notfree:  {'50', '70', '90', '10', '0', '60', '110', '100', '20', '80', '30', '40'}
    72802: free:  []
    72797: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72797: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    72802: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72802: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    72806: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 14.007001489338279
    72808: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 20.956194656877326
    72817: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 25.47135535267957
    72819: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 30.97908447399247
    72839: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 29.34549020330715
    72832: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 14.123653679614154
    72811: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395441329905000
    72833: lock overtime -149.29457092285156
    72833: 72833 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 7.627897884246185 
    72813: lock overtime -148.87242794036865
    72813: 72813 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 10.694213719569337 
    72811: notfree:  {'110', '100', '70', '90', '40', '10', '20', '0', '60', '80', '30'}
    72811: free:  ['50']
    72814: lock overtime -147.8668029308319
    72814: 72814 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 9.131894988176121 
    72811: s3://edge-ml-dev/ztmp/myfile5.csv : added :  50
    72811: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72811: 50
    72803: lock overtime -149.15093207359314
    72804: lock overtime -149.71679997444153
    72803: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395444849102000
    72820: lock overtime -149.30223107337952
    72820: 72820 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 4, 24.543462103468904 
    72804: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395445283311000
    72826: lock overtime -148.9239308834076
    72826: 72826 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 4, 23.491322446511305 
    72815: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 14.51190332948456
    72803: notfree:  {'0', '60', '80', '70', '50', '40', '10', '90', '110', '100', '30', '20'}
    72803: free:  []
    72834: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 4.026896145406458
    72804: notfree:  {'50', '20', '10', '90', '100', '80', '40', '30', '110', '70', '60', '0'}
    72804: free:  []
    72803: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72803: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    72804: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72804: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    72841: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 9.670980502402188
    72827: lock overtime -147.80445003509521
    72827: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395449195608000
    72827: notfree:  {'50', '110', '80', '20', '10', '100', '90', '60', '70', '0', '40', '30'}
    72827: free:  []
    72827: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72827: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 37.30923270804
    72833: lock overtime -149.68137001991272
    72834: lock overtime -149.5768609046936
    72833: 72833  : Retry - 1, 10.91598139801565 
    72834: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395451423168000
    72806: lock overtime -148.71553111076355
    72806: 72806 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 4.783075561498069 
    72821: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 14.645541210528199
    72834: notfree:  {'100', '0', '40', '50', '90', '80', '30', '60', '70', '20', '10', '110'}
    72834: free:  []
    72796: lock overtime -147.84521389007568
    72796: 72796 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 5, 41.54399552820059 
    72834: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72834: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 37.415685476224745
    72812: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 30.05294017115666
    72837: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 20.73436237217597
    72814: lock overtime -148.82796597480774
    72824: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 4.593333580916051
    72831: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 8.458814476007817
    72814: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395454172150000
    72813: lock overtime -149.2704141139984
    72813: 72813 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 2, 14.791815106960945 
    72844: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 7.72090696361982
    72814: notfree:  {'70', '10', '20', '0', '80', '100', '90', '30', '50', '60', '110', '40'}
    72814: free:  []
    72832: lock overtime -148.15848803520203
    72832: 72832 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 5.930716788438767 
    72814: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72814: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 36.836129546170255
    72806: lock overtime -147.56047892570496
    72806: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395457439623000
    72841: lock overtime -148.07226395606995
    72841: 72841 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 6.760552737326827 
    72806: notfree:  {'50', '10', '80', '0', '70', '60', '110', '90', '30', '100', '40', '20'}
    72806: free:  []
    72800: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 28.58344540085951
    72806: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72806: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 36.63664416147824
    72808: lock overtime -149.4864809513092
    72824: lock overtime -149.2483310699463
    72808: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395459513610000
    72824: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395459751778000
    72808: notfree:  {'70', '0', '40', '90', '10', '20', '30', '60', '100', '110', '80', '50'}
    72808: free:  []
    72824: notfree:  {'60', '30', '50', '0', '80', '110', '40', '90', '10', '100', '70', '20'}
    72824: free:  []
    72815: lock overtime -149.39519906044006
    72815: 72815 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 4.901190854675251 
    72808: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72808: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 37.760172537426016
    72816: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 25.510664421481827
    72824: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72824: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 36.791934630664045
    72840: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 10.205190802147044
    72807: lock overtime -147.80157208442688
    72832: lock overtime -147.5763030052185
    72807: 72807  : Retry - 1, 10.294367128376024 
    72795: lock overtime -149.22053980827332
    72795: 72795 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 9.516508718352842 
    72833: 72833  : Retry - 2, 9.230887246707809 
    72805: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 8.988815963053097
    72832: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395463423730000
    72831: lock overtime -148.92315483093262
    72831: 72831 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 8.635150095571902 
    72844: lock overtime -148.7991979122162
    72844: 72844 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 11.64093834228792 
    72817: lock overtime -148.75300812721252
    72817: 72817 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 9.02396361184731 
    72832: notfree:  {'110', '90', '0', '40', '70', '20', '50', '30', '60', '80', '10', '100'}
    72832: free:  []
    72832: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72832: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 37.09012392129854
    72841: lock overtime -148.94383692741394
    72797: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 8.781823978018501
    72841: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395466056251000
    72815: lock overtime -149.13311004638672
    72815: 72815 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 2, 11.757518359548687 
    72802: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 28.891583578837228
    72818: lock overtime -148.8818600177765
    72818: 72818 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 8.049768536577105 
    72841: notfree:  {'80', '50', '10', '20', '110', '100', '0', '30', '90', '70', '40'}
    72841: free:  ['60']
    72821: lock overtime -147.91704392433167
    72821: 72821 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 5.606504222574655 
    72841: s3://edge-ml-dev/ztmp/myfile5.csv : added :  60
    72841: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72841: 60
    72819: lock overtime -147.82272505760193
    72813: lock overtime -147.5508279800415
    72826: lock overtime -147.5166220664978
    72819: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395470177395000
    72839: lock overtime -149.18617296218872
    72839: 72839 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 6.687121649732318 
    72813: 72813  : Retry - 1, 10.506434476104294 
    72826: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395470483401000
    72820: lock overtime -148.83384609222412
    72820: 72820 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 5, 41.93695311356036 
    72819: notfree:  {'100', '60', '70', '20', '40', '30', '50', '0', '90', '110', '10'}
    72819: free:  ['80']
    72826: notfree:  {'70', '10', '20', '40', '30', '0', '100', '60', '90', '110', '50'}
    72826: free:  ['80']
    72819: s3://edge-ml-dev/ztmp/myfile5.csv : added :  80
    72826: s3://edge-ml-dev/ztmp/myfile5.csv : added :  80
    72819: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72819: 80
    72826: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72826: 80
    72831: lock overtime -149.36273097991943
    72805: lock overtime -149.1751720905304
    72840: lock overtime -149.0268189907074
    72821: lock overtime -148.9587869644165
    72831: 72831  : Retry - 1, 8.863881733883668 
    72817: lock overtime -149.80946683883667
    72817: 72817 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 2, 8.31917648957748 
    72833: 72833  : Retry - 3, 16.44214910278545 
    72795: lock overtime -149.763286113739
    72795: 72795 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 2, 8.403982101176478 
    72805: 72805  : Retry - 1, 8.669207128764882 
    72840: 72840  : Retry - 1, 10.689517674939376 
    72821: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395474041237000
    72807: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395474034692000
    72837: lock overtime -148.7458620071411
    72837: 72837 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 11.754141941970328 
    72821: notfree:  {'20', '0', '80', '60', '110', '100', '40', '30', '90', '50'}
    72821: free:  ['10', '70']
    72818: lock overtime -147.94482517242432
    72818: 72818 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 2, 8.418304929020792 
    72807: notfree:  {'90', '80', '40', '0', '110', '20', '60', '100', '50', '30'}
    72807: free:  ['10', '70']
    72797: lock overtime -147.76275086402893
    72797: 72797 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 12.8416486806395 
    72821: s3://edge-ml-dev/ztmp/myfile5.csv : added :  10
    72844: lock overtime -149.1991889476776
    72844: 72844 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 2, 9.585006389678078 
    72821: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72821: 10
    72807: s3://edge-ml-dev/ztmp/myfile5.csv : added :  70
    72807: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72807: 70
    72803: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 19.372056857227992
    72804: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 11.517407759044108
    72839: lock overtime -148.56795692443848
    72839: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395478432099000
    72815: lock overtime -148.44054698944092
    72815: 72815 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 3, 12.578662580518548 
    72839: notfree:  {'20', '110', '70', '30', '80', '40', '50', '60'}
    72839: free:  ['0', '10', '90', '100']
    72839: s3://edge-ml-dev/ztmp/myfile5.csv : added :  0
    72839: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72839: 0
    72813: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395481498125000
    72817: lock overtime -148.53344106674194
    72817: 72817 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 3, 16.176683338375817 
    72795: lock overtime -148.46935296058655
    72795: 72795 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 3, 17.806738611657185 
    72813: notfree:  {'50', '70', '40', '60', '0', '80', '20', '110', '30'}
    72813: free:  ['10', '90', '100']
    72831: 72831  : Retry - 2, 13.26884412915387 
    72805: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395483036467000
    72813: s3://edge-ml-dev/ztmp/myfile5.csv : added :  100
    72812: lock overtime -148.45369291305542
    72812: 72812 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 8.28919638341553 
    72813: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72813: 100
    72805: notfree:  {'0', '100', '40', '50', '80', '20', '110', '70', '30', '60'}
    72805: free:  ['10', '90']
    72818: lock overtime -148.61268496513367
    72818: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395485387336000
    72805: s3://edge-ml-dev/ztmp/myfile5.csv : added :  90
    72840: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395485186140000
    72805: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72805: 90
    72818: notfree:  {'90', '40', '70', '0', '50', '20', '110', '30', '80', '100', '60'}
    72818: free:  ['10']
    72840: notfree:  {'70', '40', '60', '100', '50', '20', '90', '30', '80', '110', '0'}
    72840: free:  ['10']
    72844: lock overtime -148.69763207435608
    72818: s3://edge-ml-dev/ztmp/myfile5.csv : added :  10
    72844: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395487302400000
    72837: lock overtime -149.1008050441742
    72837: 72837 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 2, 7.662752762786312 
    72840: s3://edge-ml-dev/ztmp/myfile5.csv : added :  10
    72816: lock overtime -148.96040081977844
    72816: 72816 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 5.089158099060853 
    72818: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72818: 10
    72840: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72840: 10
    72827: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 1.180385453300238
    72800: lock overtime -149.3440670967102
    72844: notfree:  {'110', '60', '80', '10', '90', '100', '0', '20', '70', '50', '40', '30'}
    72844: free:  []
    72800: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395488655953000
    72844: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72844: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 36.8218093146112
    72797: lock overtime -149.0002739429474
    72800: notfree:  {'110', '90', '100', '70', '60', '10', '20', '30', '0', '80', '40', '50'}
    72800: free:  []
    72797: 72797  : Retry - 1, 10.545999437617114 
    72800: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72800: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 36.11671859149691
    72827: lock overtime -149.2356560230255
    72804: lock overtime -149.20376706123352
    72834: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 9.247555399590793
    72804: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395490796258000
    72827: 72827  : Retry - 1, 7.623622684202755 
    72833: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395490648231000
    72804: notfree:  {'50', '10', '90', '40', '30', '60', '80', '100', '70', '20', '0'}
    72804: free:  ['110']
    72833: notfree:  {'30', '60', '90', '0', '20', '40', '50', '100', '70', '80', '10'}
    72833: free:  ['110']
    72815: lock overtime -147.94658207893372
    72815: 72815 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 4, 24.26845759736034 
    72804: s3://edge-ml-dev/ztmp/myfile5.csv : added :  110
    72814: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 4.679461250993691
    72833: s3://edge-ml-dev/ztmp/myfile5.csv : added :  110
    72816: lock overtime -149.5035240650177
    72816: 72816 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 2, 10.272010167072605 
    72804: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72804: 110
    72812: lock overtime -149.2296588420868
    72833: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72833: 110
    72812: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395493770418000
    72812: notfree:  {'60', '90', '100', '50', '10', '110', '0', '40', '30', '20', '70', '80'}
    72812: free:  []
    72796: lock overtime -148.39427995681763
    72796: 72796 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 6, 71.20450781978477 
    72812: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72812: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 36.554729001339524
    72806: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 24.384331442713393
    72837: lock overtime -148.52546405792236
    72802: lock overtime -149.13333296775818
    72837: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395496474613000
    72802: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395496866802000
    72837: notfree:  {'110', '100', '50', '80', '10', '0', '60', '30', '90', '20', '40', '70'}
    72837: free:  []
    72803: lock overtime -148.73275113105774
    72803: 72803 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 9.450926036844628 
    72802: notfree:  {'50', '70', '90', '10', '0', '60', '110', '100', '20', '80', '30', '40'}
    72802: free:  []
    72837: unsupported operand type(s) for ** or pow(): 'int' and 'S3lock'
    72831: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395497421981000
    72824: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 6.374482115208666
    72814: lock overtime -149.34063410758972
    72814: 72814 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 8.333005311245408 
    72802: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72802: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 37.08256763552298
    72837: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72837: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 37.87971550503314
    72808: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 10.283089139811288
    72831: notfree:  {'60', '70', '50', '30', '80', '10', '110', '0', '90', '40', '100'}
    72831: free:  ['20']
    72827: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395498941481000
    72831: s3://edge-ml-dev/ztmp/myfile5.csv : added :  20
    72817: lock overtime -148.40199303627014
    72817: 72817 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 4, 18.62444690635952 
    72831: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72831: 20
    72827: notfree:  {'50', '110', '80', '20', '10', '100', '90', '60', '70', '0', '40', '30'}
    72827: free:  []
    72834: lock overtime -148.95154881477356
    72827: unsupported operand type(s) for ** or pow(): 'int' and 'S3lock'
    72834: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395501048504000
    72827: unsupported operand type(s) for ** or pow(): 'int' and 'S3lock'
    72797: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395501089459000
    72795: lock overtime -148.732106924057
    72795: 72795 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 4, 18.477185513580192 
    72834: notfree:  {'100', '0', '50', '40', '90', '80', '30', '60', '70', '20', '10', '110'}
    72834: free:  []
    72832: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 22.489552924666153
    72827: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72827: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 54.03024459310082
    72834: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72834: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 53.18388639153443
    72797: notfree:  {'10', '80', '40', '30', '110', '60', '100', '50', '0', '90', '20', '70'}
    72797: free:  []
    72797: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72797: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 36.00492223338985
    72816: lock overtime -148.09205508232117
    72816: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395504908023000
    72824: lock overtime -149.07143187522888
    72824: 72824 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 13.41394240588728 
    72816: notfree:  {'10', '80', '90', '70', '100', '50', '60', '30', '110', '0', '20'}
    72816: free:  ['40']
    72816: s3://edge-ml-dev/ztmp/myfile5.csv : added :  40
    72816: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72816: 40
    72814: lock overtime -149.06643891334534
    72814: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395507933591000
    72803: lock overtime -149.32296919822693
    72803: 72803 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 2, 13.246068948399603 
    72814: notfree:  {'70', '10', '20', '0', '80', '100', '90', '50', '60', '110', '40'}
    72814: free:  ['30']
    72814: s3://edge-ml-dev/ztmp/myfile5.csv : added :  30
    72808: lock overtime -147.37960505485535
    72808: 72808 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 9.322366333141002 
    72814: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72814: 30
    72820: lock overtime -145.95173811912537
    72820: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395514048356000
    72820: notfree:  {'50', '100', '60', '110', '40', '80', '20', '0', '10', '70', '90', '30'}
    72820: free:  []
    72820: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72820: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    72815: lock overtime -146.73519110679626
    72815: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395518264828000
    72815: notfree:  {'70', '60', '20', '100', '80', '40', '50', '30', '10', '0', '90', '110'}
    72815: free:  []
    72817: lock overtime -149.8281741142273
    72817: 72817 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 5, 37.87345562602344 
    72824: lock overtime -149.73761582374573
    72824: 72824 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 2, 10.355370932945904 
    72815: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72815: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 37.83653967608605
    72808: lock overtime -149.11813497543335
    72808: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395520881959000
    72806: lock overtime -149.5594379901886
    72806: 72806 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 5.467179978156306 
    72795: lock overtime -149.33534216880798
    72795: 72795 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 5, 35.52692518571307 
    72808: notfree:  {'70', '0', '40', '90', '10', '20', '30', '60', '100', '110', '80', '50'}
    72808: free:  []
    72803: lock overtime -148.17937397956848
    72803: 72803 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 3, 12.394626813427596 
    72808: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72808: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 52.96627232048239
    72832: lock overtime -145.99753499031067
    72844: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 12.640410210197963
    72832: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395526002559000
    72800: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 22.248842819154667
    72806: lock overtime -148.72636008262634
    72806: 72806 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 2, 15.64229277106785 
    72832: notfree:  {'110', '0', '90', '40', '70', '20', '30', '60', '100', '10', '80'}
    72832: free:  ['50']
    72832: s3://edge-ml-dev/ztmp/myfile5.csv : added :  50
    72832: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72832: 50
    72824: lock overtime -146.44212198257446
    72824: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395531557973000
    72812: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 16.278805654769876
    72824: notfree:  {'60', '30', '50', '0', '80', '110', '40', '90', '10', '100', '70', '20'}
    72824: free:  []
    72824: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72824: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 53.28537837975146
    72802: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 17.8127141367708
    72803: lock overtime -146.82347798347473
    72803: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395536176611000
    72837: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 24.056193510213824
    72803: notfree:  {'0', '60', '80', '70', '50', '40', '10', '90', '110', '100', '30', '20'}
    72803: free:  []
    72803: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72803: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 36.7376822247615
    72797: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 27.926795244672622
    72844: lock overtime -148.22899508476257
    72844: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395539771032000
    72844: notfree:  {'110', '60', '80', '10', '90', '0', '20', '70', '50', '100', '40', '30'}
    72844: free:  []
    72844: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72844: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 54.88262300205156
    72806: lock overtime -147.12167501449585
    72806: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395543878443000
    72806: notfree:  {'50', '10', '80', '0', '70', '60', '110', '90', '30', '100', '40', '20'}
    72806: free:  []
    72806: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72806: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 51.68878864959661
    72820: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 20.183604114724098
    72812: lock overtime -145.41395092010498
    72800: lock overtime -149.00033402442932
    72812: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395549586165000
    72800: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395549999785000
    72812: notfree:  {'90', '100', '10', '110', '50', '0', '40', '20', '30', '70', '80'}
    72812: free:  ['60']
    72800: notfree:  {'80', '110', '70', '10', '20', '30', '0', '100', '40', '90', '50'}
    72800: free:  ['60']
    72812: s3://edge-ml-dev/ztmp/myfile5.csv : added :  60
    72800: s3://edge-ml-dev/ztmp/myfile5.csv : added :  60
    72812: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72812: 60
    72800: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72800: 60
    72802: lock overtime -147.18701696395874
    72802: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395554813120000
    72834: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 27.65728401394833
    72802: notfree:  {'50', '90', '10', '0', '110', '60', '100', '20', '30', '40'}
    72802: free:  ['70', '80']
    72827: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 19.397252580786986
    72802: s3://edge-ml-dev/ztmp/myfile5.csv : added :  70
    72802: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72802: 70
    72792: None
    72792: None
    72792: None
    72795: lock overtime -148.85596585273743
    72815: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 18.62892062006906
    72795: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395558144153000
    72817: lock overtime -149.0598258972168
    72817: 72817 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 6, 67.1667948416883 
    72795: notfree:  {'60', '0', '10', '40', '90', '50', '110', '30', '100', '70', '20'}
    72795: free:  ['80']
    72795: s3://edge-ml-dev/ztmp/myfile5.csv : added :  80
    72795: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72795: 80
    72837: lock overtime -148.11002492904663
    72837: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395561890109000
    72837: notfree:  {'110', '100', '50', '80', '10', '90', '60', '30', '20', '40', '70'}
    72837: free:  ['0']
    72837: s3://edge-ml-dev/ztmp/myfile5.csv : added :  0
    72837: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72837: 0
    72796: lock overtime -146.25089192390442
    72820: lock overtime -149.71114897727966
    72796: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395567749257000
    72797: lock overtime -149.43172407150269
    72797: 72797 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 11.325446330760172 
    72820: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395568288964000
    72796: notfree:  {'50', '40', '0', '110', '80', '70', '60', '30', '20'}
    72796: free:  ['10', '90', '100']
    72820: notfree:  {'50', '60', '110', '40', '20', '80', '0', '70', '30'}
    72820: free:  ['10', '90', '100']
    72796: s3://edge-ml-dev/ztmp/myfile5.csv : added :  90
    72820: s3://edge-ml-dev/ztmp/myfile5.csv : added :  10
    72796: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72796: 90
    72820: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72820: 10
    72803: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 28.56050026166013
    72808: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 28.851159721925598
    72827: lock overtime -142.92708086967468
    72827: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395577073005000
    72815: lock overtime -149.28452897071838
    72815: 72815 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 11.134883737790014 
    72827: notfree:  {'50', '20', '80', '10', '60', '70', '0', '40', '30'}
    72827: free:  ['90', '100', '110']
    72827: s3://edge-ml-dev/ztmp/myfile5.csv : added :  110
    72827: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72827: 110
    72797: lock overtime -148.18827295303345
    72797: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395580811801000
    72797: notfree:  {'10', '40', '80', '30', '110', '60', '50', '0', '70'}
    72797: free:  ['20', '90', '100']
    72797: s3://edge-ml-dev/ztmp/myfile5.csv : added :  100
    72797: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72797: 100
    72834: lock overtime -148.0816810131073
    72834: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395584918593000
    72834: notfree:  {'100', '0', '50', '80', '30', '60', '70', '10', '110'}
    72834: free:  ['20', '40', '90']
    72824: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 23.604919388567254
    72834: s3://edge-ml-dev/ztmp/myfile5.csv : added :  40
    72834: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72834: 40
    72815: lock overtime -147.20343899726868
    72815: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395589796654000
    72815: notfree:  {'70', '60', '100', '80', '40', '50', '10', '0', '110'}
    72815: free:  ['20', '30', '90']
    72815: s3://edge-ml-dev/ztmp/myfile5.csv : added :  30
    72815: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72815: 30
    72844: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 20.933499228952503
    72806: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 14.691789093545218
    72803: lock overtime -137.3922209739685
    72803: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395604607894000
    72808: lock overtime -148.20822596549988
    72808: 72808 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 12.262054220990171 
    72803: notfree:  {'0', '60', '80', '50', '70', '40', '10', '110', '100', '30'}
    72803: free:  ['20', '90']
    72803: s3://edge-ml-dev/ztmp/myfile5.csv : added :  90
    72803: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72803: 90
    72824: lock overtime -145.5322859287262
    72824: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395611467836000
    72824: notfree:  {'60', '30', '0', '80', '110', '40', '90', '10', '100', '70'}
    72824: free:  ['20', '50']
    72806: lock overtime -147.70117712020874
    72806: 72806 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 13.334527655007168 
    72824: s3://edge-ml-dev/ztmp/myfile5.csv : added :  20
    72824: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72824: 20
    72844: lock overtime -145.27709484100342
    72808: lock overtime -144.9959681034088
    72844: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395618722978000
    72808: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395619004253000
    72844: notfree:  {'110', '60', '80', '10', '90', '0', '20', '70', '100', '40', '30'}
    72844: free:  ['50']
    72808: notfree:  {'0', '40', '90', '10', '20', '30', '60', '80', '100', '110', '70'}
    72808: free:  ['50']
    72844: s3://edge-ml-dev/ztmp/myfile5.csv : added :  50
    72808: s3://edge-ml-dev/ztmp/myfile5.csv : added :  50
    72844: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72844: 50
    72808: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72808: 50
    72817: lock overtime -143.83385491371155
    72806: lock overtime -149.4255440235138
    72817: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395627166239000
    72806: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395627574530000
    72817: notfree:  {'10', '40', '60', '80', '70', '0', '100', '20', '30', '50', '90', '110'}
    72817: free:  []
    72806: notfree:  {'50', '10', '80', '0', '70', '60', '110', '90', '30', '100', '40', '20'}
    72806: free:  []
    72817: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72817: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 36.99509703069373
    72806: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72806: s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 81.0895675835681
    72817: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 9.279600576576561
    72817: lock overtime -102.15205979347229
    72817: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395676848030000
    72817: notfree:  {'90', '20', '50'}
    72817: free:  ['0', '10', '30', '40', '60', '70', '80', '100', '110']
    72817: s3://edge-ml-dev/ztmp/myfile5.csv : added :  30
    72817: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72817: 30
    72806: s3://edge-ml-dev/ztmp/myfile5.csv : start locking 10.143601720121694
    72806: lock overtime -106.92413377761841
    72806: s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723395722075982000
    72806: notfree:  {'30'}
    72806: free:  ['0', '10', '20', '40', '50', '60', '70', '80', '90', '100', '110']
    72806: s3://edge-ml-dev/ztmp/myfile5.csv : added :  10
    72806: s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    72806: 10
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None
    72792: None













                                                                                                    
    (py39) \W$            python src/utils/utils_s3.py testcsv_getfree2  --npool 12                            
    68010 : s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    68010 : s3://edge-ml-dev/ztmp/myfile5.csv : start locking 2.976962745869951
    68009 : s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    68009 : s3://edge-ml-dev/ztmp/myfile5.csv : start locking 2.1223798827701237
    68014 : s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    68014 : s3://edge-ml-dev/ztmp/myfile5.csv : start locking 6.2615448618896234
    68008 : s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    68008 : s3://edge-ml-dev/ztmp/myfile5.csv : start locking 6.387128499967236
    68011 : s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    68011 : s3://edge-ml-dev/ztmp/myfile5.csv : start locking 4.9272490773751425
    68007 : s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    68007 : s3://edge-ml-dev/ztmp/myfile5.csv : start locking 30.199761259671856
    68012 : s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    68012 : s3://edge-ml-dev/ztmp/myfile5.csv : start locking 5.8513103625342175
    68015 : s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    68015 : s3://edge-ml-dev/ztmp/myfile5.csv : start locking 4.632883005207948
    68016 : s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    68016 : s3://edge-ml-dev/ztmp/myfile5.csv : start locking 23.711834181146124
    68013 : s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    68013 : s3://edge-ml-dev/ztmp/myfile5.csv : start locking 4.149967125298235
    68017 : s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    68017 : s3://edge-ml-dev/ztmp/myfile5.csv : start locking 19.877910164743593
    68006 : s3://edge-ml-dev/ztmp/myfile5.csv : get_free start
    68006 : s3://edge-ml-dev/ztmp/myfile5.csv : start locking 23.77249541965058
    68009 : lock overtime -101.8190929889679
    68009 : s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723274891181008000
    68010 : lock overtime -119.98442506790161
    68010 : 68010 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 4.24104245015651 
    68009 : notfree:  {'10', '30', '80', '50', '20', '100', '0', '60', '70', '40', '90', '110'}
    68009 : free:  []
    68013 : lock overtime -118.77589821815491
    68013 : 68013 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 13.958864158574256 
    68009 : s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    68009 : s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    68015 : lock overtime -120.35674500465393
    68011 : lock overtime -120.0611789226532
    68015 : s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723274893643290000
    68011 : s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723274893938845000
    68012 : lock overtime -120.09099793434143
    68012 : 68012 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 5.577857798319454 
    68015 : notfree:  {'90', '0', '70', '80', '30', '10', '100', '110', '40', '60', '20', '50'}
    68015 : free:  []
    68008 : lock overtime -119.70109701156616
    68008 : 68008 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 10.471148923558143 
    68014 : lock overtime -119.60473394393921
    68014 : 68014 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 8.884954987953464 
    68011 : notfree:  {'20', '80', '100', '90', '110', '50', '60', '0', '70', '10', '30', '40'}
    68011 : free:  []
    68015 : s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    68015 : s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    68011 : s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    68011 : s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    68010 : lock overtime -119.35354495048523
    68010 : s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723274896646532000
    68010 : notfree:  {'30', '0', '90', '100', '80', '60', '110', '10', '50', '40', '20'}
    68010 : free:  ['70']
    68010 : idx: 0
    68010 : s3://edge-ml-dev/ztmp/myfile5.csv : added :  70
    68010 : s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    68010 : 70
    68004 : None
    68012 : lock overtime -119.04958486557007
    68012 : s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723274900950518000
    68012 : notfree:  {'110', '100', '10', '60', '80', '40', '30', '90', '0', '70', '20'}
    68012 : free:  ['50']
    68012 : idx: -1
    68012 : s3://edge-ml-dev/ztmp/myfile5.csv : added :  50
    68012 : s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    68012 : 50
    68014 : lock overtime -118.94666504859924
    68014 : s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723274905053476000
    68008 : lock overtime -119.40651202201843
    68008 : 68008 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 2, 13.053380465599846 
    68014 : notfree:  {'90', '0', '40', '60', '80', '10', '50', '70', '30', '100', '20'}
    68014 : free:  ['110']
    68014 : idx: 0
    68014 : s3://edge-ml-dev/ztmp/myfile5.csv : added :  110
    68013 : lock overtime -117.89688396453857
    68013 : 68013 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 2, 15.500579181013881 
    68014 : s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    68014 : 110
    68017 : lock overtime -119.08583498001099
    68017 : s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723274908914271000
    68017 : notfree:  {'70', '60', '40', '30', '20', '90', '50', '0', '10', '110', '80', '100'}
    68017 : free:  []
    68017 : s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    68017 : s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    68016 : lock overtime -118.03865694999695
    68006 : lock overtime -118.02188014984131
    68016 : 68016  : Retry - 1, 4.18153773517586 
    68006 : s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723274912978169000
    68006 : notfree:  {'100', '40', '110', '0', '50', '80', '20', '70', '90', '10', '30', '60'}
    68006 : free:  []
    68006 : s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    68006 : s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    68016 : s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723274917852475000
    68007 : lock overtime -118.72854089736938
    68007 : 68007 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 4.0889471629502 
    68016 : notfree:  {'90', '80', '40', '10', '70', '110', '50', '60', '0', '30', '20'}
    68016 : free:  ['100']
    68016 : idx: 0
    68016 : s3://edge-ml-dev/ztmp/myfile5.csv : added :  100
    68008 : lock overtime -117.5475971698761
    68008 : 68008 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 3, 17.593449917519884 
    68016 : s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    68016 : 100
    68007 : lock overtime -117.18749809265137
    68013 : lock overtime -119.54955911636353
    68013 : 68013 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 3, 12.95693561167667 
    68007 : s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723274923812612000
    68009 : s3://edge-ml-dev/ztmp/myfile5.csv : start locking 8.612100027141594
    68007 : notfree:  {'100', '60', '10', '40', '110', '70', '20', '50', '80', '90', '30'}
    68007 : free:  ['0']
    68007 : idx: -1
    68007 : s3://edge-ml-dev/ztmp/myfile5.csv : added :  0
    68015 : s3://edge-ml-dev/ztmp/myfile5.csv : start locking 4.071565749989714
    68007 : s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    68007 : 0
    68011 : s3://edge-ml-dev/ztmp/myfile5.csv : start locking 3.0744466334686775
    68011 : lock overtime -116.04424095153809
    68011 : s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723274930955851000
    68015 : lock overtime -120.30297303199768
    68015 : 68015 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 1, 10.023652905030856 
    68011 : notfree:  {'20', '80', '100', '110', '50', '60', '0', '70', '40', '30'}
    68011 : free:  ['10', '90']
    68011 : idx: 0
    68011 : s3://edge-ml-dev/ztmp/myfile5.csv : added :  10
    68011 : s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    68011 : 10
    68009 : lock overtime -119.9529800415039
    68009 : s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723274934047047000
    68009 : notfree:  {'10', '80', '30', '50', '20', '100', '0', '60', '70', '40', '110'}
    68009 : free:  ['90']
    68009 : idx: -1
    68009 : s3://edge-ml-dev/ztmp/myfile5.csv : added :  90
    68009 : s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    68009 : 90
    68004 : None
    68004 : None
    68004 : None
    68013 : lock overtime -118.75860404968262
    68013 : s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723274938241659000
    68008 : lock overtime -120.13706803321838
    68008 : 68008 s3://edge-ml-dev/ztmp/myfile5.csv :waiting unlock : Retry - 4, 20.45956198963454 
    68013 : notfree:  {'70', '60', '20', '0', '100', '40', '30', '90', '110', '80', '50', '10'}
    68013 : free:  []
    68013 : s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    68013 : s3://edge-ml-dev/ztmp/myfile5.csv : get_free : waiting for a free key 31.0
    68017 : s3://edge-ml-dev/ztmp/myfile5.csv : start locking 7.075009005670729
    68015 : lock overtime -118.47273182868958
    68015 : s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723274942527323000
    68015 : notfree:  {'90', '0', '70', '30', '10', '100', '40', '110', '60', '20', '50'}
    68015 : free:  ['80']
    68015 : idx: -1
    68015 : s3://edge-ml-dev/ztmp/myfile5.csv : added :  80
    68015 : s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked
    68015 : 80
    68006 : s3://edge-ml-dev/ztmp/myfile5.csv : start locking 13.653675686604945
    68017 : lock overtime -115.874107837677
    68017 : s3://edge-ml-dev/ztmp/myfile5.csv : Locked:  1723274950125991000
    68017 : notfree:  {'70', '60', '30', '20', '90', '50', '0', '110', '10', '80', '100'}
    68017 : free:  ['40']
    68017 : idx: -1
    68017 : s3://edge-ml-dev/ztmp/myfile5.csv : added :  40
    68017 : s3://edge-ml-dev/ztmp/myfile5.csv : Unlocked


"""
