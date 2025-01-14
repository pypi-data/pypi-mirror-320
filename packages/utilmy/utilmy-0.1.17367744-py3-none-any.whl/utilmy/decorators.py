from threading import Thread
import cProfile, pstats, io, os, errno, signal, time
from functools import wraps
from contextlib import contextmanager
from utilmy.debug import log



def test_all():
    """function test_all.
    """
    test_decorators()	
    test_decorators2()

def test_decorators():
    """.
    Doc::            
            #### python test.py   test_decorators
    """
    from utilmy.decorators import thread_decorator, timeout_decorator, profiler_context,profiler_decorator, profiler_decorator_base

    @thread_decorator
    def thread_decorator_test():
        log("thread decorator")


    @profiler_decorator_base
    def profiler_decorator_base_test():
        log("profiler decorator")

    @timeout_decorator(10)
    def timeout_decorator_test():
        log("timeout decorator")

    profiler_decorator_base_test()
    timeout_decorator_test()
    thread_decorator_test()



def test_decorators2():
    """function test_decorators2.
    Doc::

    """
    from utilmy.decorators import profiler_decorator, profiler_context

    @profiler_decorator
    def profiled_sum():
       return sum(range(100000))

    profiled_sum()

    with profiler_context():
       x = sum(range(1000000))
       print(x)


    from utilmy import profiler_start, profiler_stop
    profiler_start()
    print(sum(range(1000000)))
    profiler_stop()


    ###################################################################################
    from utilmy.decorators import timer_decorator
    @timer_decorator
    def dummy_func():
       time.sleep(2)

    class DummyClass:
       @timer_decorator
       def method(self):
           time.sleep(3)

    dummy_func()
    a = DummyClass()
    a.method()




########################################################################################################################
########################################################################################################################
def thread_decorator(func):
    """ A decorator to run function in background on thread.
    Doc::
            
        	Return:
        		background_thread: ``Thread``
    """
    @wraps(func)
    def wrapper(*args, **kwags):
        background_thread = Thread(target=func, args=(*args,))
        background_thread.daemon = True
        background_thread.start()
        return background_thread

    return wrapper





########################################################################################################################
class _TimeoutError(Exception):
    """Time out error"""
    pass


########################################################################################################################
def timeout_decorator(seconds=10, error_message=os.strerror(errno.ETIME)):
    """Decorator to throw timeout error, if function doesnt complete in certain time.
    Doc::
            
            Args:
                seconds:``int``
                    No of seconds to wait
                error_message:``str``
                    Error message
                    
    """
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise _TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator


def timer_decorator(func):
    """.
    Doc::
            
            Decorator to show the execution time of a function or a method in a class.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f'function {func.__name__} finished in: {(end - start):.2f} s')
        return result

    return wrapper



########################################################################################################################
@contextmanager
def profiler_context():
    """.
    Doc::
            
            Context Manager the will profile code inside it's bloc.
            And print the result of profiler.
            Example:
                with profiler_context():
                    # code to profile here
    """
    from pyinstrument import Profiler
    profiler = Profiler()
    profiler.start()
    try:
        yield profiler
    except Exception as e:
        raise e
    finally:
        profiler.stop()
        print(profiler.output_text(unicode=True, color=True))


def profiler_decorator(func):
    """.
    Doc::
            
            A decorator that will profile a function
            And print the result of profiler.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        from pyinstrument import Profiler
        profiler = Profiler()
        profiler.start()
        result = func(*args, **kwargs)
        profiler.stop()
        print(profiler.output_text(unicode=True, color=True))
        return result
    return wrapper



def profiler_decorator_base(fnc):
    """.
    Doc::
            
            A decorator that uses cProfile to profile a function
            And print the result
    """
    def inner(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        retval = fnc(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = "cumulative"
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        return retval

    return inner



def test0():
    """function test0.
    Doc::
            
            Args:
            Returns:
                
    """
    with profiler_context():
        x = sum(range(1000000))
        print(x)
    from utilmy import profiler_start, profiler_stop
    profiler_start()
    print(sum(range(1000000)))
    profiler_stop()

@thread_decorator
def thread_decorator_test():
    """function thread_decorator_test.
    Doc::
            
            Args:
            Returns:
                
    """
    log("thread decorator")

@profiler_decorator_base
def profiler_decorator_base_test():
    """function profiler_decorator_base_test.
    Doc::
            
            Args:
            Returns:
                
    """
    log("profiler decorator")

@timeout_decorator(10)
def timeout_decorator_test():
    """function timeout_decorator_test.
    Doc::
            
            Args:
            Returns:
                
    """
    log("timeout decorator")


@profiler_decorator
def profiled_sum():
    """function profiled_sum.
    Doc::
            
            Args:
            Returns:
                
    """
    return sum(range(100000))

@timer_decorator
def dummy_func():
    """function dummy_func.
    Doc::
            
            Args:
            Returns:
                
    """
    time.sleep(2)




def diskcache_load( db_path_or_object="", size_limit=100000000000, verbose=True ):    
    """ val = cache[mykey]
    """
    import diskcache as dc
    from utilmy import os_makedirs
    global cache_diskcache37

    if not isinstance(db_path_or_object, str ) :
       return db_path_or_object

    os_makedirs(db_path_or_object) 

    cache_diskcache37 = dc.Cache(db_path_or_object, size_limit= size_limit)
    log(f"cache_dir: {db_path_or_object}")
    log('Cache size/limit', len(cache_diskcache37), cache_diskcache37.size_limit, str(cache_diskcache37))
    return cache_diskcache37



def hash_int64(xstr:str, n_chars=10000, seed=123):
  import xxhash  
  return xxhash.xxh64_intdigest(str(xstr)[:n_chars], seed=seed)

def diskcache_decorator(func, ttl_sec=None):
    """ Caching of data
    Docs:

       os.environ['CACHE_ENABLE'] = "1"
       os.environ['CACHE_DIR']    = "ztmp/cache/mycache2"
       os.environ['CACHE_TTL']    = "3600"
       os.environ['CACHE_SIZE']    = "1000000000"
       os.environ['CACHE_DEBUG']    = "0"       
       
       ## pip install --upgrade utilmy
       from utilmy import diskcache_decorator


       @diskcache_decorator
       def myvery_slow_sql(dirin=""):

         return df



       dirin= "ztmp/ctr/latest/data/*.parquet"
       df1 = pd_read_file_s3(path_s3= dirin)
       df2 = pd_read_file_s3(path_s3= dirin)
    """ 
    #from src.utils.utilmy_base import hash_int64
    import os
    def wrapper(*arg, **args):
        debug = True if os.environ.get('CACHE_DEBUG', "0") =="1" else False
        if debug : log('cache: start')
        flag = os.environ.get('CACHE_ENABLE', '')
        
        if len(flag) < 1 or flag=='0' :
           # log(os.environ)
           return func(*arg, **args)

        if debug : log('cache: load')
        ttl_sec    = int( os.environ.get('CACHE_TTL', 7200))
        dir0       = os.environ.get('CACHE_DIR', "ztmp/zcache/")
        size_limit = int(os.environ.get('CACHE_SIZE', 10**9) )
        global cache_diskcache37
        try :
           len(cache_diskcache37)
        except : 
           cache_diskcache37 = diskcache_load(dir0, size_limit= size_limit, verbose=True)


        argid = hash_int64( str(arg) + str(args))
        try :
           dfx= cache_diskcache37[argid]
           log("cache: fetched from:", dir0, argid, )
           return dfx
        except :
            dfx = func(*arg, **args)
            cache_diskcache37.set(argid, dfx, expire= ttl_sec)
            log("cache: data from Real, saved in ", argid, )
            return dfx

    return wrapper












#####################################################################################################
if __name__ == '__main__':
    import fire
    fire.Fire()

