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


from utilmy import log,loge

from src.utils.utilmy_aws import (pd_to_file_s3, pd_read_file_s3)

##########################################################################
def test_lock():
    """
         pip install fire utilmy

         ### Concurrent lock simulation
             python util_s3.py  test_lock ;     python util_s3.py  test_lock ;   python util_s3.py  test_lock ; 

    Logs: 

         
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



def log(*s):
  print(os.getpid(),":", *s)



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
dir1= "s3://ztest"

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

    """
    flist = [ str(i*10) for i in  range(0, 12) ]
    index1 = S3Lock_csv( dir1+"/ztmp/myfile5.csv"
                        ,dirlock=dir1+"/ztmp/lock_hash", max_locktime= 90 )
    ifree = index1.get_free(flist , ttl= 1000) 
    log(ifree)



def testcsv_getfree2(add=1, npool=3):
      """
           python src/utils/utils_s3.py testcsv_getfree2  --npool 7 

      """
      npool   = npool
      pool    = mp.Pool(processes = npool)
      results = []
      for i in range(1, 1+npool):
         results.append(pool.apply_async(testcsv_getfree, (i * 10 ,))) 
      
      for r in results:
          log(r.get())



#####################################################################
class S3lock:
    def __init__(self, dirlock:str, ntry_max=10, ntry_sleep=1, delay_start=10, n_concurrent=10,
                 max_locktime= 300 ):
        """
           Atomic Read, Atomic write on S3 text file.
           Many readers, many writers ---> All atomic.

        """
        self.s3      = boto3.client('s3')
        self.dirlock = dirlock  #### where all the lock are stored.
        #self.bucket, self.lock_key = dirlock.replace("s3://", "").split('/', 1)
        self.ntry_max   = ntry_max
        self.ntry_sleep = ntry_sleep

        ### prevent race condition
        self.delay_start  = delay_start
        self.n_concurrent = n_concurrent

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
              log(lock_key,": last_udpate: ", unix_timestamp, last_modified )
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
      
        delay = random.uniform(1, 1 + self.n_concurrent*3 )
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
            #log("nowL:", datetime.fromtimestamp(time.time() ))
            #log("limit:", datetime.fromtimestamp(mtime ))            
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
        self.dircsv = dircsv
        self.s3lock = S3lock(dirlock, max_locktime= max_locktime)
        self.ntry_max = ntry_max
        self.max_locktime = max_locktime

        self.cols = ['key', 'val', 'ttl']


    def read_atomic(self, ntry_max):
        """
             https://aws-sdk-pandas.readthedocs.io/en/stable/ 

        """
        islock = self.s3lock.lock(self.dircsv, ntry_max= self.ntry_max)
        if not islock:
           return False

        df = wr.s3.read_csv(dir2, index=False, sep="\t" )
        df = df[ df['ttl'].apply(lambda x: x <= ttl ) ]

        self.s3lock.unlock(self.dircsv) 
        return df    


    def wait_unlock(self,):
        islock = self.s3lock.lock(self.dircsv, ntry_max=ntry_max)
        ntry = 0
        while islock and ntry < ntry_max : 
            time.sleep(5*ntry)
            islock = self.s3lock.lock(self.dircsv, ntry_max=ntry_max)
            ntry += 1

        return ntry 


    def add(self, newrows:list=None, ttl= 3600):

        if len(newrows)< 1: return False 
        if not isinstance(newrows[0], list) and not isinstance(newrows[0], tuple) :
             newrows = [ (x1, 1) for x1 in newrows ]

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
               df = pd.DataFrame([], columns=['key', 'val', 'ttl'])   

            log(df.shape) 


            newrows = [ [ str(x1), str(x2), time.time() + ttl ] for (x1,x2) in newrows      ]
            newrows = pd.DataFrame(newrows, columns= ["key", "val", "ttl" ] )
            df      = pd.concat((df, newrows)) if len(df) > 0 else newrows
            log(df.shape)

            t0 = time.time()
            df = df[ df['ttl'].apply(lambda x: x > t0 ) ]
            log(self.dircsv    ,'size: ', len(df))

            wr.s3.to_csv(df, self.dircsv, index=False, sep="\t" )
            log(self.dircsv, ': added: ', len(newrows))
        except Exception as e:
            log(e)
            self.s3lock.unlock(self.dircsv) 
            return False

        # self.s3.get_object(Bucket= bucket, Key= self.dircsv)["Body"].put(df)
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

            t0 = time.time()
            df = df[ df['ttl'].apply(lambda x: x > t0 ) ]

            notfree = set([  str(xi).strip() for xi in  df['key'].values])
            log('notfree: ', notfree)
            lfree   = [ xi for xi in keylist_ref if str(xi).strip() not in notfree ]
            log('free: ', lfree)

            if len(lfree)>0:
               idx = random.randint(0, len(lfree))-1
               log('idx:', idx)
               key1 = lfree[ idx ] 
               df = pd.concat((df, pd.DataFrame([[ key1, "2", time.time() + ttl ]], columns= self.cols) ))
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
