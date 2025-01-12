""" 
Flow pipleine


  0) List of keywords in csv file 

  1)) step 1: 
          load 
         --> pick the keywords from csv file --> Google News by palywright --> fetch all the URLs
          -> save in dataframe on disk (parquet file)

  2) step2 : 
       Load the parquet file of URLs.

       --> One issue 
           Convert Google redirect URL ---> Real URL (real website)
           Before:   url_real = convert_base64(google_url). (not work anymore)
            Now:     url_real =. follow_redirect_getfinal(google_url)  (super slow...)

       for each News URL : 
           1) fetch content using Goose3 (it works 60% of the time,)
              --> title, date, text 
           2) If failed, use 3rd party paid Scraper (for 40% of failed) 
   
       --> save in dataframe, parquet file on disk



   .......    



### 
   export PYTHONPATH="$(pwd)"
   alias pyfet="python src/fetchers.py  "

   echo $PYTHONPATH

   ### Extract daily URL:
      pyfet run_urlist    --cfg $config


   ### Extract text content
      pyfet url_extract_all   --cfg $config


   262 URL ferches, 32 failed   --> 10% failed.


   TODO : date guesser
   https://github.com/mediacloud/date_guesser
   
    

"""
import warnings; warnings.filterwarnings("ignore")
import time, os, sys, pkgutil, json, requests, random, re
from typing import Tuple
import pandas as pd, numpy as np
from goose3 import Goose
from bs4 import BeautifulSoup


from src.utils.utilmy_base import (diskcache_decorator, config_load )


from src.utils.utilmy_aws import (
  pd_to_file_s3,
  pd_read_file_s3, pd_read_file_s3_glob, pd_read_file_s3list,
  glob_glob_s3, glob_filter_dirlevel, glob_filter_filedate
)



from src.utils.utilmy_log import (
    log, loge, log2, log3
)


from utilmy import (
   pd_read_file, pd_to_file,
   glob_glob, os_makedirs,    date_now, 
)

############################################################################################
global dirdata
dirdata="./ztmp/data"


def init():
   log('cache') 
   # os.environ['CACHE_ENABLE'] = "1"
   os.environ['CACHE_DIR']    = "ztmp/cache/mycache2"
   os.environ['CACHE_TTL']    = "9600"
   os.environ['CACHE_SIZE']   = "1000000000"


init()


def test13():

   df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})   
   #  pd_to_file_s3(df, "s3://edge-ml-dev/ztmp/test.parquet" , show=1)

   pd_to_file_s3(df, "s3://edge-ml-dev/ztmp/test/year=2024/month=03/day=02/hours=2/df.parquet" , show=1)





############################################################################################
######### URL Fetchers #####################################################################
def run_urlist(cfg=None, dirout="./ztmp/data/news_urls", name="url_search_keyword.csv", istest=None):
   """  Fetch URLS from 
       cfg="config/dev/cfg_dev.yaml"
       alias pyfet="python src/fetchers.py "

       pyfet run_urlist  --cfg "" 
       pyfet run_urlist --cfg config/dev/cfg_dev.yaml  --istest 1 
       pyfet test13


   """ 
   log("######## run_urlist ###############################################")
   global dirdata   
   cfg0, dirdata, istest =config_load_v2(cfg, istest=istest)

   dircache = "/mnt/efs/zcache/urls2"
   # dircache = "ztmp/efs/zcache/urls2"


   time.sleep(random.uniform(3, 60 )) ### for distributed system
 
   log("######## Load url_search_keyword config file ######################")
   fdefault = dirdata + "/config/url_search_keyword.csv"
   fused    = None
   try:
       from src.utils.utilmy_base import diskCache 
       dcache = diskCache(dircache, ttl= 60*15, size_limit = 1*10**9, shards=4, ntry_max=3 ) ##15mins per loop
       log(dcache)
       flist = glob_glob_s3( dirdata + "/config/*keyword*.csv" )
       for fi in flist :
            isexist = dcache.get(fi)
            if isexist is None:
                dcache.set(fused, 1) #### Lock the CSV file
                fused = fi
                log('furls input found:', fused)
                break 

   except Exception as e:
       log(e)
       dcache = {}
       
   if fused is None:
       log('All busy file, using default', fdefault)
       fused = fdefault
       # log("waiting 60s")
       # time.sleep(60)

   log("######## Load url_search_keyword csv #############################")
   log(fused)
   com_list= pd_read_file_s3(fused, sep=",")
   log(fused, com_list)
   
   
   if com_list is None:
       x = ["microsoft", "google cloud", "amazon web service", "oracle", "apple", "google",
            "ibm", "nvidia", 'meta', "microsoft azure" ]
       com_list = pd.DataFrame()
       com_list['com_name'] = x 
       com_list['keywords'] = x 
             
   com_list = com_list.iloc[:1,:] if istest == 1 else com_list
   cols0 = ['url','name', 'keywords', 'art_title', 'art_date']

   log('dirdata:', dirdata)       
   y,m,d,h = date_now(fmt="%Y-%m-%d-%H").split("-")
   HMS     = date_now(fmt="%y%m%s_%H%M%S")
   dirout2 = dirdata + f"/news_urls/year={y}/month={m}/day={d}/hours={h}"
   log('dirout2:', dirout2)
   

   dftoday = data_load_previous(dirdata + f"/news_urls", past_days=-10, cols=['url'])         
   if dftoday is not None and len(dftoday) > 0:
      dftoday =set(dftoday['url'].values)
   else:
      dftoday =set()   
   log('Today URLs:', len(dftoday))
   
   log("######## Start fetching ###############################################")
   log(str(com_list)[:100])
   urlall = []
   n      = len(com_list)
   ii     = -1
   for ii,x in com_list.iterrows():
       com_name = x['com_name']
       keywords = x['keywords']
       log("#### url-fetch:", ii, com_name, keywords)

       
       urls = urls_fetch_prnweswire(keywords=f"{keywords}", tag_filter= f'{com_name}', com_name=com_name, pagemax=2)
       urlall.extend(urls)
 
       urls  = urls_fetch_googlenews(keywords= f"{keywords} partner", com_name=com_name,  pagemax=2)
       urlall.extend(urls)
       if istest != 1: 
           urls  = urls_fetch_googlenews(keywords= f"{keywords} acquisition",   com_name=com_name,  pagemax=2)
           urlall.extend(urls)

           urls  = urls_fetch_googlenews(keywords= f"{keywords} collaboration", com_name=com_name,  pagemax=2)
           urlall.extend(urls)

           urls  = urls_fetch_googlenews(keywords= f"{keywords} funding",   com_name=com_name,  pagemax=2)
           urlall.extend(urls)

           urls  = urls_fetch_googlenews(keywords= f'{keywords} "investment"',   com_name=com_name,  pagemax=2)
           urlall.extend(urls)

           urls  = urls_fetch_googlenews(keywords= f'{keywords} "merger"',   com_name=com_name,  pagemax=2)
           urlall.extend(urls)


           ##### Custom URL ALL ######################################
           urlall = run_urlist_custom(urlall, com_name=com_name)


       if (ii % 5 == 0 and ii > 0) or (ii == n-1) :
          log('N URL fetch: ', len(urlall))
          urlall =[ xi for xi in urlall if xi['url'] not in dftoday ]
          log('N URL fetch Clean: ', len(urlall))
          if len(urlall) < 1:
              dcache.set(fused, 1) #### Lock the CSV file
              continue

          y,m,d,h = date_now(fmt="%Y-%m-%d-%H").split("-")
          ts      = date_now(fmt="%y%m%d_%H%M%S")
          dirout2 = dirdata + f"/news_urls/year={y}/month={m}/day={d}/hours={h}"
          diroutk = dirout2 + f"/df_{ts}_{ii}.parquet"
          urls_save(urlall, diroutk, dirout2)
          urlall = []
          dcache.set(fused, 1) #### Lock the CSV file
       
   log(f"#### URL Fetch End all  {ii} #########################################")



def urls_save(urlall, diroutk, dirout2):
    df = pd.DataFrame(urlall)
    df['url']       = df['url'].astype('str')
    df['origin_dt'] = date_now( returnval='unix' )

    df = pd_exclude_past(df, dirin0= dirout2 , past_days=0 )
    diroutk = diroutk.replace(".parquet", f"_{len(df)}.parquet")
    pd_to_file_s3(df, diroutk , show=1)
    urlall = []



def run_urlist_custom(urlall, com_name="microsoft"):

    if 'microsoft' in com_name :
        urls = urls_fetch_microsoftnews()
        urlall.extend(urls)

    return urlall



###################################################################################
def pd_exclude_past(df, dirin0= None , past_days=-1 ):
    # dirin0 = f"{dirdata}/news_znlp/L0_catnews"
    dfp    = data_load_previous(dirin0, past_days= past_days, ymd=None, cols=['url'])
    log('Before Past:', df.shape)
    if 'url' in dfp.columns and 'url' in df.columns :
       df = df[ -df['url'].isin(dfp['url'].values)]
    log('After Past:', df.shape)
    return df  


def data_load_previous(dirin, past_days=-5, ymd=None, cols=None, hourdata=0 ):

    if hourdata ==  1:
        dirin1 = "{dirin}/year={y}/month={m}/day={d}/**/*.parquet"
    else:
        dirin1 = "{dirin}/year={y}/month={m}/day={d}/*.parquet"


    dfall = pd.DataFrame()
    for iday in range(0, abs(past_days)+1, 1): 
           y,m,d   = date_now(ymd, fmt="%Y-%m-%d", add_days= -iday).split("-")
           dirin1a = dirin1.format(dirin=dirin, y=y,m=m,d=d)
           log(dirin1a)
           df    = pd_read_file_s3( dirin1a, npool=4, cols = cols   ) 
           if df is None or len(df) < 1: continue 

           log(df.shape)
           df = df.drop_duplicates(['url'])
           dfall = pd.concat((dfall, df)) 

    dfall = dfall.drop_duplicates('url')
    log(dfall.shape)
    return dfall


def url_get_final2(initial_url):
    """
      initial_url = "https://example.com/redirect"
      final_url   = get_final_url(initial_url)
      print(f"Final URL: {final_url}")

    """
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(initial_url)
        page.wait_for_load_state('networkidle')
        final_url = page.url
        browser.close()
        return final_url






####################################################################################
##### search URL ###################################################################
# @diskcache_decorator
def urls_fetch_prnweswire(keywords=" microsoft", tag_filter='microsoft', com_name=None, pagemax=2):

    keywords = keywords.replace(" ", "+")     

    prefix   = "https://www.prnewswire.com"
    url0     = 'https://www.prnewswire.com/search/news/?keyword={keywords}&page={k}&pagesize=200'
    url0     = url0.replace("{keywords}", keywords )
    
    urls2=[]
    for k in range(1, pagemax+1):
       urlk = url0.replace("{k}", str(k))
       urls = request_urls_extract(urlk)

       ### Custom Filter
       urls = [ link for link in urls if link.startswith('/news-releases/')]
       urls = [ prefix + url for url in urls if ".html" in url ]
       urls = [ x for x in urls if tag_filter in x ]
       # urls = [ x for x in urls if x not in set(urls2) ]

       urls2 = urls2 + urls

    urls3 = [ {"url": url, 'name': com_name, 'origin': 'prnewswire.com', 'keywords': com_name,
             'art_title': '', 'art_dt': ''  }  for url in urls2 ]
    log("N_prnewsire: ", len(urls2))   
    return urls3



# @diskcache_decorator
def urls_fetch_yahoonews( keywords="microsoft" ):

    val = { "microsoft":"MSFT"}.get(keywords)
    url = f"https://finance.yahoo.com/quote/{val}/press-releases/"
    DIV_QUERY_SELECTOR = 'div.content.svelte-j87knz'
    H3_TAG = 'h3.clamp.svelte-j87knz'
    DIV_PUBLISHING = 'div.publishing.font-condensed.svelte-1k3af9g'
    A_TAG = 'a.subtle-link'

    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(5000)

        url_list = []
        items = page.query_selector_all(DIV_QUERY_SELECTOR)

        for item in items:
            try:
                title_element = item.query_selector(H3_TAG)
                if title_element:
                    title = title_element.inner_text()
                    link  = item.query_selector(A_TAG).get_attribute('href')
                    date_element = item.query_selector(DIV_PUBLISHING)
                    if date_element:
                        date_text = date_element.inner_text()
                        url_list.append({
                            'title': title,
                            'link': link,
                            'date': date_text
                        })
            except Exception as e:
                print(f"Error: {e}")
                continue

        browser.close()

    url_list = pd.DataFrame(url_list)         
    return url_list



# @diskcache_decorator
def urls_fetch_googlenews(keywords="microsoft funding", com_name="microsoft", pagemax=2,):

    prefix = 'https://news.google.com'
    dt0 = date_now(fmt="%Y/%m/%d ")
    urlp = "https://news.google.com/search?q="
    keys = keywords.split(" ")
    keys = [  f"%22{x}%22" for x in keys   ]
    keys = "%20".join(keys)
    #keys = keywords.replace(" ", "%20" )
    url = f"{urlp}{keys}&hl=en-US&when%3A9d&gl=US&ceid=US%3Aen"         ##√
    ## https://news.google.com/search?q=%22microsoft%22%20%22partner%22%20when%3A7d&hl=en-US&gl=US&ceid=US%3Aen
    ## https://news.google.com/search?q=microsoft%20%22acquisition%22%20when%3A7d&hl=en-US&gl=US&ceid=US%3Aen
    ### "https://news.google.com/search?q=". &hl=en-US&gl=US&ceid=US%3Aen"
    log(url)

    ARTICLE_SELECTOR = 'article.IFHyqb'
    TITLE_SELECTOR = 'a.JtKRv'
    LINK_SELECTOR = 'a.JtKRv'
    DATE_SELECTOR = 'time.hvbAAd'

    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        try:
           browser = p.chromium.launch(headless=True)
           page = browser.new_page()
           page.goto(url)
           page.wait_for_timeout(9000)
           url_list = []
           items = page.query_selector_all(ARTICLE_SELECTOR)
        except Exception as e:
            log(e, url)
            log("Skipping ", url)
            urls2 = [ ]
            return urls2            

        for item in items:
            try:
                title_element = item.query_selector(TITLE_SELECTOR)
                link_element = item.query_selector(LINK_SELECTOR)
                date_element = item.query_selector(DATE_SELECTOR)
                #text_element = item.query_selector(TEXT_SELECTOR)

                if title_element and link_element and date_element:
                    title = title_element.inner_text().strip()
                    link = link_element.get_attribute('href')
                    date = date_element.inner_text().strip()
                    #text = TEXT_element.inner_text().strip()

                    url_list.append({
                        'title': title,
                        'url':   link,
                        'date':   date,
                        'origin': url
                    })
            except Exception as e:
                print(f"Error: {e}")
                continue

        browser.close()

    urls2 = [ {"url": str(prefix + x['url']), 'name': com_name,  'keywords': keywords, 
                 'art_title': x['title'], 'art_dt': dt0 + x['date'],
                 'origin': x['origin']
              }  for x in url_list   ]      
    return urls2



# @diskcache_decorator
def urls_fetch_googlenews_rss(url_rss):
    """    
    """
    from bs4 import BeautifulSoup
    import requests
    r = requests.get(url_rss)
    soup = BeautifulSoup(r.content, 'xml')
    
    id_alert = [x.text for x in soup.find_all("id")[1:len(soup.find_all("id"))]]
    title_alert = [x.text for x in soup.find_all("title")[1:len(soup.find_all("title"))]]
    published_alert = [x.text for x in soup.find_all("published")]
    update_alert = [x.text for x in soup.find_all("updated")[1:len(soup.find_all("updated"))]]
    link_alert = [[x["href"].split("url=")[1].split("&ct=")[0]] for x in soup.find_all("link")[1:len(soup.find_all("link"))]]
    content_alert = [x.text for x in soup.find_all("content")]

    llist = [


    ]



    #df = pd.DataFrame(compiled_list, columns = ["ID", "Title", "Published on:", "Updated on", "Link", "Content"])
    #return df
    # df.to_excel('new_alerts.xlsx', header=True, index=False)



def urls_fetch_bingnews(keywords="microsoft funding", com_name="microsoft", pagemax=2,):

    prefix = 'https://news.google.com'
    dt0 = date_now(fmt="%Y/%m/%d ")
    urlp = "https://news.google.com/search?q="
    keys = keywords.split(" ")
    keys = [  f"%22{x}%22" for x in keys   ]
    keys = "%20".join(keys)
    #keys = keywords.replace(" ", "%20" )
    url = f"{urlp}{keys}&hl=en-US&when%3A9d&gl=US&ceid=US%3Aen"         ##√
    ###   https://news.google.com/search?q=%22microsoft%22%20%22partner%22%20when%3A7d&hl=en-US&gl=US&ceid=US%3Aen
    ###   https://news.google.com/search?q=microsoft%20%22acquisition%22%20when%3A7d&hl=en-US&gl=US&ceid=US%3Aen
    ###   https://news.google.com/search?q=". &hl=en-US&gl=US&ceid=US%3Aen"
    log(url)

    ARTICLE_SELECTOR = 't_s'
    TITLE_SELECTOR = 'title'
    LINK_SELECTOR = 'title'
    DATE_SELECTOR =  'span[aria-label^=""]'

    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        try:
           browser = p.chromium.launch(headless=True)
           page = browser.new_page()
           page.goto(url)
           page.wait_for_timeout(9000)
           url_list = []
           items = page.query_selector_all(ARTICLE_SELECTOR)
        except Exception as e:
            log(e, url)
            log("Skipping ", url)
            urls2 = [ ]
            return urls2            

        for item in items:
            try:
                title_element = item.query_selector(TITLE_SELECTOR)
                link_element  = item.query_selector(LINK_SELECTOR)
                #date_element = item.query_selector(DATE_SELECTOR)
                #text_element = item.query_selector(TEXT_SELECTOR)
                date_element  = item.locator( DATE_SELECTOR )

                if title_element and link_element and date_element:
                    title = title_element.inner_text().strip()
                    link = link_element.get_attribute('href')
                    date = date_element.inner_text().strip()
                    #text = TEXT_element.inner_text().strip()

                    url_list.append({
                        'title': title,
                        'url':   link,
                        'date':   date,
                        'origin': url
                    })
            except Exception as e:
                print(f"Error: {e}")
                continue

        browser.close()

    urls2 = [ {"url": str(prefix + x['url']), 'name': com_name,  'keywords': keywords, 
                 'art_title': x['title'], 'art_dt': dt0 + x['date'],
                 'origin': x['origin']
              }  for x in url_list   ]      
    return urls2


####################################################################################
####### Custom URL #################################################################
#@diskcache_decorator
def urls_fetch_microsoftnews(url = "https://news.microsoft.com/category/press-releases/"):
    TAG_ARTICLE = 'article.category-press-releases'
    TAG_DIV     = 'div.c-paragraph-3.c-meta-text'
    A_TAG       = 'a.f-post-link.c-heading-6.m-chevron'

    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(5000)

        url_list = []
        items = page.query_selector_all(TAG_ARTICLE)

        for item in items:
            try:
                date_element = item.query_selector(TAG_DIV)
                title_element = item.query_selector(A_TAG)
                if title_element and date_element:
                    date  = date_element.inner_text().strip()
                    title = title_element.inner_text().strip()
                    link  = title_element.get_attribute('href')
                    url_list.append({
                        'title': title,
                        'url': link,
                        'date': date
                    })
            except Exception as e:
                print(f"Error: {e}")
                continue

        browser.close()

    urls2 = [ {"url": str(x['url']), 'name': 'microsoft', 
               'origin': 'news.microsoft.com/category/press-releases/', 'keywords': "",
               'art_title' : x['title'],
               'art_dt' :    x['date']
             }  for x in url_list ]       
    return urls2





#######################################################################################
####### Extract contetn ###############################################################
def run_extract_all(cfg=None,dirin=None, dirout=None, fetch_miss=1, nmax=0, istest=None,
                     past_days=-10, ymd=None):
   """

       cfg="config/dev/cfg_dev.yaml"
       alias pyfet="python src/fetchers.py "
       pyfet run_extract_all --cfg config/dev/cfg_dev.yaml     --nmax 30000 
       

   """ 
   log("####### run_extract_all ###########################################")
   global dirdata   
   cfg0, dirdata, istest =config_load_v2(cfg, istest=istest)   
   cfgd = cfg0.get("url_extract", {})
   chunk_size = 1500  ### 2000 is too long, 1000 is OK, but too small chunk
   if istest == 1:
       nmax= 20
       chunk_size = 5

   #### Dir Output
   y,m,d,h = date_now(fmt="%Y-%m-%d-%H").split("-")
   dirtmp  = dirdata +  "/news_tmp/url_extract_all"
   dirout1 = dirdata + f"/news_text/year={y}/month={m}/day={d}/hour={h}"
   dirout2 = dirdata + f"/news_urls_miss/year={y}/month={m}/day={d}/hour={h}"
   
      
   log("\n##### Url Loads   #############################################")
   dirin1 = dirdata + "/news_urls" 
   df     = data_load_previous(dirin1, past_days=past_days, ymd=ymd, cols=None, hourdata=1 )
   log(df[['url', 'name', 'keywords', 'art_title', 'art_dt', 'origin','origin_dt' ]].shape)


   log("\n##### Url Clean   #############################################")
   df = pd_clean_com_name(cfg, df, files="url_search_keyword.csv")
   df = pd_clean_previousfetched(cfg, df)  ### matching google URL with Final url !!
   df = pd_clean_previousmiss(cfg, df=df)   

   df = df if nmax == 0 else df.iloc[:nmax, :]


   ### extra:
   log(df.shape)
   df = df[ df.apply(lambda x:  True if x['name'].lower() in x['art_title'].lower() else False, axis=1 ) ]
   log('Filtering title:', df.shape)


   df = pd_add_date_extract_filter(df, coldt='art_dt2', past_days=-30, )   
   df = pd_clean_googlelink(df)
   df = df.drop_duplicates("url")   
   df = df.sort_values(['art_dt2',], ascending=0)


   log( df[['url', 'url2']].shape)
   dt = date_now(fmt="%y%m%d_%H%M%S")
   pd_to_file(df, dirtmp + f"/df_url_{dt}.parquet", show=1)


   log("\n##### Fetch Allchunk text   ################################")
   chunk_size = min( chunk_size, len(df)) 
   nall       = 0
   t0 = time.time()
   for i in range(0, len(df), chunk_size):
       df1  = df.iloc[i:i + chunk_size, :]
       if len(df1) <1 : break
       urls = df1['url'].to_list()
       nall += len(urls)
       log("###", i, len(df1), str(urls[0])[:50] )
       url_fetch_text_all(urls, df1, dirout1, dirtmp, dirout2)
       
       # os.system(f"rm -rf /tmp/*")
       log('Ntotal:', len(df), 'Nsubmit:', nall)
       #return None
       #if time.time() - t0 > 3600 * 5 :
       #    log('Ntotal:', len(df), 'Nsubmit:', nall)
       #    log("####### Ending ")
       #    return None
            

def pd_clean_com_name(cfg, df, files="url_search_keyword.csv"):
   log("\n##### Load com names Filter   ##############################")
   dfcom = pd_read_file_s3(dirdata + "/config/" + files )
   log('com', dfcom.shape, dfcom)
   dfcom = set(list(dfcom['com_name'].values)) 

   if len(dfcom) > 5:
       log("Before name filter", df.shape)
       df = df[df['name'].isin(dfcom)]
       log("After name filter", df.shape)
   return df 


def url_fetch_text_all(urls, df, dirout1, dirtmp, dirout2):
    log("\n##### Extract 1st URL ####################################")
    cols_extract= ['url', 'art2_title', 'art2_date', 'art2_text']
    ok_urls = []
    skip    = False
    df3     = pd.DataFrame()

    if not skip:
        df3, df3_miss   = url_extract_text_goose(urls=urls, timeout=90)

    if len(df3) > 0 :
        df3 = df3[['url', 'title', 'date', 'text']]
        df3.columns = cols_extract

        df     = pd_merge(df, df3[cols_extract], on=['url'], how='left')
        df3    = pd_remove_invalid_text(df, col="art2_text")
        df3    = pd_add_date_extract(df3, coldt='art2_date')
        ok_urls= np_remove_dup(df3['url'].values)

        log("\n##### Save on disk #####")
        if len(df3) > 0:
            dt     = date_now(fmt="%y%m%d_%H%M%S")
            pd_to_file(df3,     f"{dirout1}/df_text1_{dt}_{len(df3)}.parquet", show=1)
            pd_to_file(df3_miss,f"{dirout2}/df_miss1_{dt}_{len(df3_miss)}.parquet", show=0)


    log("\n##### Extract 2nd  URL #######################################")
    # miss_urls = [x for x in df['url'].values if x not in set(ok_urls)]
    # if len(miss_urls) < 1: return

    # if not skip:
    #     from src.fetcher_auto import run_fetch
    #     df3, df3_miss = run_fetch(miss_urls, cols_extract, dirout=dirtmp)

    # if len(df3) > 0  :
    #     df     = pd_merge(df, df3[cols_extract], on=['url'], how='left')
    #     df3    = pd_remove_invalid_text(df, col="art2_text")
    #     df3    = pd_add_date_extract(df3, coldt='art2_date')
    #     ok_urls= np_add_unique(ok_urls, df3['url'].values)

    #     if len(df3) > 0:
    #         dt     = date_now(fmt="%y%m%d_%H%M%S")
    #         pd_to_file(df3,     f"{dirout1}/df_text2_{dt}_{len(df3)}.parquet", show=1)
    #         pd_to_file(df3_miss,f"{dirout2}/df_miss2_{dt}_{len(df3_miss)}.parquet", show=0)


    log("\n##### Extract 3nd URL ########################################")
    miss_urls = [x for x in df['url'].values if x not in set(ok_urls)]
    if len(miss_urls) < 1: return

    from src.fetcher_auto import run_fetch_v3
    df3, df3_miss = run_fetch_v3(miss_urls, cols_extract, mode='level1', npool=5)
    df3 = pd_remove_invalid_text(df3, col="art2_text")
    if len(df3) > 0:
        df     = pd_merge(df, df3[cols_extract], on=['url'], how='left')
        df3    = pd_remove_invalid_text(df, col="art2_text")
        df3    = pd_add_date_extract(df3, coldt='art2_date')
        ok_urls= np_add_unique(ok_urls, df3['url'].values)

        if len(df3) > 0:
            dt     = date_now(fmt="%y%m%d_%H%M%S")
            pd_to_file(df3,     f"{dirout1}/df_text3_{dt}_{len(df3)}.parquet", show=1)
            pd_to_file(df3_miss,f"{dirout2}/df_miss3_{dt}_{len(df3_miss)}.parquet", show=0)


    log("\n##### Extract 4rd URL ########################################")
    #    miss_urls = [x for x in df['url'].values if x not in set(ok_urls) ]
    #    if len(miss_urls)< 1: return
    #    from src.fetcher_auto import run_fetch_v3
    #    df3    = run_fetch_v3(miss_urls, cols_extract, mode='level2')
    #    df3    = pd_remove_invalid_text(df3, col="art2_text" )
    #    ok_urls= np_add_unique(ok_urls, df3['url'].values )

    #    df     = pd_merge(df, df3[ cols_extract ], on=['url'], how='left')
    #    df3    = pd_remove_invalid_text(df, col="art2_text" )

    #    if len(df3)> 0:
    #       HMS = date_now(fmt="%H%M%S")
    #       diroutk = f"{dirout1}/df_text4_{HMS}_{len(df3)}.parquet"
    #       pd_to_file(df3, diroutk, show=1)
    #       pd_to_file(df[df['art2_text'].isna()], dirtmp +"/df_miss_4.parquet", show=0)

    log("\n##### Miss URL Save #########################################")
    dfmiss = df[-df['url'].isin(ok_urls)]
    log("N_OK", len(ok_urls), 'N_miss:', len(dfmiss))
    if len(dfmiss) > 0:
        dt     = date_now(fmt="%y%m%d_%H%M%S")
        diroutk= f"{dirout2}/df_miss_all_{dt}_{len(dfmiss)}_all.parquet"
        pd_to_file(dfmiss, diroutk, show=1)



def url_load_list(dirdata:str, distribute=0, source='news_urls')->pd.DataFrame:
    
   if source == 'prnews':  
       dirin1 = dirdata + "/news_urls/prnews/url/year={y}/month={m}/day={d}/*.parquet" 
       
   else :    
       dirin1 = dirdata + "/news_urls/year={y}/month={m}/day={d}/**/*.parquet" 

   for iday in range(0, 20, 1): 
      y,m,d   = date_now(fmt="%Y-%m-%d", add_days= -iday).split("-")
      dirin1a = dirin1.format(y=y,m=m,d=d)
      flist   = glob_glob_s3(dirin1a)
      if len(flist) > 0:
          break 
      log('flist empty:', dirin1a)
   
   df = pd_read_file_s3(dirin1a)
   log(df.shape, list(df.columns))   
   return df
   


##################################################################################
##################################################################################
#@diskcache_decorator
def pd_clean_googlelink(df, nmax=10000000, colgoogle='url2'):

    log("##### Google Link Renormalization #####################")
    log(df.shape)
    if colgoogle in df.columns and 'url' in df.columns :
        log('URL google already cleaned, passing')
        return df

    df[colgoogle] = df['url']    

    urls = df['url'].values[:nmax]
    res = []
    for url in urls: 
        if "google.com" in url:
           # res.append( url_getfinal_url(url) )
           url2 = url_gnews_decode(url) 
        else:   
           url2 = url

        if 'prnewswire' in url2 and url2.endswith('.htm'):
            url2 = url2 + "l" 

        url2 = url2.replace("Ò","")

        res.append( url2 )

    df['url'] = res

    log(df.shape)
    df = df[ df['url'].apply(lambda x:  True if str(x).startswith("http") else False    ) ] ###bad URL   
    log('URL correct:', df.shape)
    return df



#@diskcache_decorator
def pd_clean_previousfetched(cfg=None, df=None, source='news_text'):
    """
         dirdata
         cfg = "config/dev/cfg_dev.yaml"

    """
    global dirdata   
    cfg0     = config_load(cfg) if len(str(cfg)) > 4  else {}   
    dirdata  = cfg0.get('data', {}).get('dirdata',  dirdata)
    log("#### fetching past URL ")
    df = df.drop_duplicates("url")
    df = df[df['url'].str.startswith('http')]    
    log("Nurls All:", len(df))
    
    if 'prnews' in source :
        dfpast = url_load_previousfetched_v2(cfg=cfg,y=None,m=None)
        if dfpast is not None :
            dfpast = dfpast.drop_duplicates('url')  
            df     = df[ -df['url'].isin( dfpast['url'].values )] 
        log("Nurls News:", len(df))


    else:
        dfpast = url_load_previousfetched_v2(cfg, y=None, m=None)     

        if dfpast is not None :
           ### url2 is Google URL, 'url' is google URL from URL file
           df = df[ -df['url'].isin( dfpast['url2'].values )] 
        log("Nurls News:", len(df))
    return df 


@diskcache_decorator
def url_load_previousfetched_v2(cfg=None,y=None,m=None):
    """
         dirdata
         cfg = "config/dev/cfg_dev.yaml"
         dfold = url_load_previousfetched(cfg)

    """
    global dirdata   
    cfg0    = config_load(cfg) if len(str(cfg)) > 4  else {}   
    dirdata = cfg0.get('data', {}).get('dirdata',  dirdata)

    if y is None :
       y,m,d,h = date_now(fmt="%Y-%m-%d-%H").split("-")

    dirin1 = dirdata + f"/news_text/year={y}/month={m}/**/*.parquet"
    dfold  = pd_read_file_s3(dirin1,npool=4, cols=['url', 'url2'] )


    dirin1 = dirdata + f"/news_text/prnews/year={y}/month={m}/**/*.parquet"
    df2    = pd_read_file_s3(dirin1,  npool=4, cols= ['url', 'url2'])
    dfold  = pd.concat(( dfold, df2 )) if df2 is not None else dfold 


    #### Google URL
    dfold = dfold.drop_duplicates('url2') ### Google URL
    dfold = dfold.drop_duplicates('url')  ### Fina URL
    # dfold = dfold[ dfold[ 'url' ].apply(lambda  x: x.startswith("http"))]     
    log("dfpast: ", dfold.shape )
    return dfold[[ 'url', 'url2' ]]



def pd_clean_previousmiss(cfg=None, df=None, source='news_text'):
    """
         dirdata
         cfg = "config/dev/cfg_dev.yaml"

         pd_clean_previousmiss(cfg, df=None, source='news_text')

    """
    global dirdata   
    cfg0     = config_load(cfg) if len(str(cfg)) > 4  else {}   
    dirdata  = cfg0.get('data', {}).get('dirdata',  dirdata)
    log("#### fetching past miss ")
    log("Nurls Before_miss:", df.shape)
    
    dfpast = url_load_previousmiss_v2(cfg=cfg,y=None,m=None)
    if dfpast is not None :
        df     = df[ -df['url'].isin( dfpast['url'].values )] 
    log("Nurls After_miss:", df.shape)
    return df 



@diskcache_decorator
def url_load_previousmiss_v2(cfg=None,y=None,m=None):
    """
         dirdata
         cfg = "config/dev/cfg_dev.yaml"
         dfold = url_load_previousmiss_v2(cfg)

    """
    global dirdata   
    cfg0   = config_load(cfg) if len(str(cfg)) > 4  else {}   
    dirdata= cfg0.get('data', {}).get('dirdata',  dirdata)

    if y is None :
       y,m,d,h = date_now(fmt="%Y-%m-%d-%H").split("-")

    dirin1= dirdata + f"/news_urls_miss/year={y}/month={m}/**/*.parquet"
    dfold = pd_read_file_s3(dirin1,npool=4, cols=['url', ] )

    dirin1= dirdata + f"/news_urls_miss/prnews/year={y}/month={m}/**/*.parquet"
    df2   = pd_read_file_s3(dirin1,  npool=4, cols= ['url',])
    dfold = pd.concat(( dfold, df2 )) if df2 is not None else dfold 
    log(dfold.shape)
    
    
    #### Google URL ############################################
    dfold = dfold['url'].value_counts().reset_index()
    dfold.columns = ['url', 'count']
    dfold = dfold[ dfold['count'] >= 3.0 ] 
    dfold = dfold.drop_duplicates('url')  ### Fina URL
    log("dfpast_miss: ", dfold.shape )
    return dfold




def url_dump_debug(cfg="config/cfg/cfg_dev.yaml"):
    global dirdata   
    cfg0    = config_load(cfg) if len(str(cfg)) > 4  else {}   
    dirdata = cfg0.get('data', {}).get('dirdata',  dirdata)

    dirin1 = dirdata + "/news_text/year={y}/month={m}/**/*.parquet"
    df1 = pd_read_file_s3(dirin1,  npool=4)
    df1 = df1.drop_duplicates("art2_text")

    df1['text2'] = df1['art2_text'].apply(lambda x: x[:100])
    pd_to_file(df1[[  'text2' ]], "ztmp/data/news_text/debug.csv", sep="\t"  )



def np_add_unique(vref, vnew):
    vref = list(vref)    
    for x in vnew:
        if x not in vref:
            vref.append(x)
    return vref




# @diskcache_decorator
def url_extract_text_goose(urls=None, timeout=60) :
    '''run Goose3 benchmark in one thread


    '''
    miss = []; oks = [] 
    t0   = time.time()

    if isinstance(urls, str): 
        urls = urls.split("\n")
        urls = [x.strip().replace(" ", "") for x in urls if len(x)> 10 ]

    ii, n_urls = 0, len(urls)
    log(f"N URLS: {n_urls}")


    ##### Setup 
    from goose3 import Goose
    from goose3.configuration import Configuration

    ERRORS = ('Access Denied', 'Site Not Available',
        'Page not found', 'Unavailable for legal reasons','404 Error')

    config = Configuration()
    config.http_timeout = timeout ## secs    
    config.browser_user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1'
    config.enable_image_fetching = False
    config.strict = False

    g = Goose(config)
    ierr = 0
    for jj,url in enumerate(urls):
        dt = time.time() - t0
        try:
            article = g.extract(url=url)
            title = article.title 
            text  = article.cleaned_text

            try :
              #from htmldate import find_date
              #prdate = find_date(html)
              prdate = str(article.publish_date),
            except :
              log('date_article issue: ', url)  
              prdate = ""

            # goose3 return exception message as article.title rather than rising an exception
            if title in ERRORS  or  not text_is_valid_v1(text) or not text_is_valid_title(title) :
                miss.append( (url, text, 'error invalid') )  
                log(jj, url, title)
            else:
                dd = { 'url' :  str(url),
                      'title':  str(article.title),
                      'date' :  prdate,
                      'text' :  str(text)
                }
                oks.append( dd )
                ii = ii +1

        except Exception as e :
             log(ii, url,  e)
             miss.append( (url, '', str(e) ) )        
             ierr += 1      
             if ierr > 20 : 
                 g.close()
                 g = Goose(config)
                 ierr =0 
    g.close()

    miss = pd.DataFrame(miss, columns=['url', 'info', 'err_msg'])
    oks  = pd.DataFrame(oks,  columns=['url', 'title', 'date', 'text']) 

    dt = time.time()-t0 
    log( f"Fetched step 1: {ii} / {n_urls}", dt )
    return oks, miss



def text_is_valid_v1(txt):
    ll =["please enable cookies",
         "unfortunately the page that you",
         "why have i been blocked",
         "performance & security by",
         "waiting for www.",
         "this page appears",
         "this site http",
         "about this page our systems have detected",
         "experiencing technical difficulty",
         "you can register for free by",
         "error with your",
         "unable to find the page",
         "sorry we can't find",
         "sorry, this page",
         "we use cookies ",
         "font-weight:",
         "page you are trying",
         "page is no longer available",
         "page not found",
         "404 page",
         "404 error "
    ]

    if len(txt) < 100: 
        return False

    txt = txt.lower().strip()
    for ss in ll:      
        if ss in txt:
            return False
    return True     


def text_is_valid_title(txt):
    ll =["please enable cookies",
         "unfortunately the page that you",
         "why have i been blocked",
         "performance & security by",
         "waiting for www.",
         "this page appears",
         "this site http",
         "about this page our systems have detected",
         "experiencing technical difficulty",
         "you can register for free by",
         "error with your",
         "unable to find the page",
         "sorry we can't find",
         "sorry, this page",
         "we use cookies ",
         "font-weight:",
         "page you are trying",
         "page is no longer available",
         "page not found",
         "404 page",
         "404 error "
    ]

    txt = txt.lower().strip()
    for ss in ll:      
        if ss in txt:
            return False
    return True 


def pd_remove_invalid_text(df, col="art2_text" ):
    df[col] = df[col].astype("str")
    dfok    = df[col].apply(lambda x: text_is_valid_v1(str(x)) )
    df = df[dfok]
    df = df.drop_duplicates(col)
    return df



def pd_get_invalid_text(df, col="art2_text" ):
    dfnotok = df[col].apply(lambda x: not text_is_valid_v1(str(x)) )
    return df[dfnotok]


def url_clean_list(urls):
   res = []
   for x in urls:
      x = x.replace("./", "/")
      res.append(x)
   return res 


def url_getfinal_url_list(urls, timeout=20, npool=5):
   import concurrent.futures

   res1  = []
   urls2 = []
   for url in urls:
       if "google.com/articles" in url :
          urls2.append(url)
       else:
          res1.append(url) 


   res2 =[]
   with concurrent.futures.ThreadPoolExecutor(max_workers=npool) as executor:
       futures = [executor.submit(url_getfinal_url, url) for url in urls]
       for future in concurrent.futures.as_completed(futures):
         res2.append( future.result() ) 

   res = res1 + res2
   return res




##########################################################################################
def url_gnews_decode(source_url):
    """

        url_gnews_decode( url1 )

        url1="https://news.google.com./articles/CBMinQFodHRwczovL3d3dy5saXZlbWludC5jb20vY29tcGFuaWVzL2NvbXBhbnktcmVzdWx0cy9oZGZjLWJhbmstcTQtcmVzdWx0cy1saXZlLXVwZGF0ZXMtaW5kaWFzLWJpZ2dlc3QtcHJpdmF0ZS1sZW5kZXItdG8tcG9zdC1lYXJuaW5ncy10b2RheS0xMTcxMzU4Njg1MjM1NC5odG1s0gGhAWh0dHBzOi8vd3d3LmxpdmVtaW50LmNvbS9jb21wYW5pZXMvY29tcGFueS1yZXN1bHRzL2hkZmMtYmFuay1xNC1yZXN1bHRzLWxpdmUtdXBkYXRlcy1pbmRpYXMtYmlnZ2VzdC1wcml2YXRlLWxlbmRlci10by1wb3N0LWVhcm5pbmdzLXRvZGF5L2FtcC0xMTcxMzU4Njg1MjM1NC5odG1s?hl=en-US&gl=US&ceid=US%3Aen"

        aa="AU_yqLPGoUDR6oJIVNfTBjDHjp8EjxFvWyGXOQAk04NBURzQdkl-bZrn-IiPNykwMkWKIK1bNiE2BaHFgCQRtmyLKg8-lLpRlQlH3BjFSc17YJy_NXkUlZUNYsEtsPn3RproRcsvwgUKdtTsPu67ZuNr1Zfgaz5giSI6cfFZBZ9RF6VuY8O03JtpR1e175ll_8_dqajo1XNx6UgxhuzYPRiw"



    """ 
    import base64
    from urllib.parse import urlparse

    source_url = source_url.replace("com./", "com/", )

    url = urlparse(source_url)
    path = url.path.split('/')
    if (
        url.hostname == "news.google.com" and
        len(path) > 1 and
        path[len(path) - 2] == "articles"
    ):
        base64_str = path[len(path) - 1]
        decoded_bytes = base64.urlsafe_b64decode(base64_str + '==')
        decoded_str = decoded_bytes.decode('latin1')

        prefix = bytes([0x08, 0x13, 0x22]).decode('latin1')
        if decoded_str.startswith(prefix):
            decoded_str = decoded_str[len(prefix):]

        suffix = bytes([0xd2, 0x01, 0x00]).decode('latin1')
        if decoded_str.endswith(suffix):
            decoded_str = decoded_str[:-len(suffix)]

        bytes_array = bytearray(decoded_str, 'latin1')
        length = bytes_array[0]
        if length >= 0x80:
            decoded_str = decoded_str[2:length+1 + 1] ### needed
        else:
            decoded_str = decoded_str[1:length+1 + 1]

        if decoded_str.startswith("AU_yqL"):
            log(decoded_str)
            url2 = fetch_decoded_batch_execute(base64_str)
            if url2 != "" : return url2 
            else:
               return url_getfinal_url(source_url)
        else:
            return decoded_str
    else:
        return source_url


def url_remove_bad_char(url):
    # Remove invalid characters
    url = re.sub(r'[^\w\-\.\:/]', '', str(url))
    
    # Ensure protocol is present
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    return url
    

def fetch_decoded_batch_execute(id1):
    """
          
        fetch_decoded_batch_execute(aa)  
        aa="AU_yqLPGoUDR6oJIVNfTBjDHjp8EjxFvWyGXOQAk04NBURzQdkl-bZrn-IiPNykwMkWKIK1bNiE2BaHFgCQRtmyLKg8-lLpRlQlH3BjFSc17YJy_NXkUlZUNYsEtsPn3RproRcsvwgUKdtTsPu67ZuNr1Zfgaz5giSI6cfFZBZ9RF6VuY8O03JtpR1e175ll_8_dqajo1XNx6UgxhuzYPRiw"

        AU_yqLPS5w9-fjLJCEsPQ3s7j9SwUsDlpeVLSRxso0u2slXwGIrkx90eDK64bpXSr7FvAcVSOxN4-Ws535L1HsFBak6t0J5yJGy81aae3hNljiEdMuaryUZVW9TaLydCu_56HilYTy-oYFgwi8KrpBZl1J24heGw52-XUxK06ip4imi03oEiIV9f9JYbJpz0EO8Qs4ir4oDajznIIPKI6y1CDVlDzSN6-s4
        AU_yqLM_xoczp5Qd5bX0yrkIN1LlT2kwzF2gOpxs0tMPtvdbA48Cm3UUeRKO4IGpt7lcdozOHmm003zOXUasjQTuSFh_2jVTMdnHbUk8st_m6ZGGnnfrFGvY7yNmXlzSPhmuSWxoi6TrRwhSPqmJbmp1Z8Y3NKQUhLR0NSboKwr0Hk3xkmpvOK3GVzojksWg4dD9pM5Mo6Zn0x2Kfg

        url1="https://news.google.com./articles/CBMinQFodHRwczovL3d3dy5saXZlbWludC5jb20vY29tcGFuaWVzL2NvbXBhbnktcmVzdWx0cy9oZGZjLWJhbmstcTQtcmVzdWx0cy1saXZlLXVwZGF0ZXMtaW5kaWFzLWJpZ2dlc3QtcHJpdmF0ZS1sZW5kZXItdG8tcG9zdC1lYXJuaW5ncy10b2RheS0xMTcxMzU4Njg1MjM1NC5odG1s0gGhAWh0dHBzOi8vd3d3LmxpdmVtaW50LmNvbS9jb21wYW5pZXMvY29tcGFueS1yZXN1bHRzL2hkZmMtYmFuay1xNC1yZXN1bHRzLWxpdmUtdXBkYXRlcy1pbmRpYXMtYmlnZ2VzdC1wcml2YXRlLWxlbmRlci10by1wb3N0LWVhcm5pbmdzLXRvZGF5L2FtcC0xMTcxMzU4Njg1MjM1NC5odG1s?hl=en-US&gl=US&ceid=US%3Aen"


       url1="https://news.google.com./articles/CBMi4wFBVV95cUxQUzV3OS1makxKQ0VzUFEzczdqOVN3VXNEbHBlVkxTUnhzbzB1MnNsWHdHSXJreDkwZURLNjRicFhTcjdGdkFjVlNPeE40LVdzNTM1TDFIc0ZCYWs2dDBKNXlKR3k4MWFhZTNoTmxqaUVkTXVhcnlVWlZXOVRhTHlkQ3VfNTZIaWxZVHktb1lGZ3dpOEtycEJabDFKMjRoZUd3NTItWFV4SzA2aXA0aW1pMDNvRWlJVjlmOUpZYkpwejBFTzhRczRpcjRvRGFqem5JSVBLSTZ5MUNEVmxEelNONi1zNNIB6AFBVV95cUxOQ1hfa25rT0hNYmFFX1pPSzhzNTZiUFVfVzN5N3F6Y21LT0pPaFpRMlpVWWZkZlFtcmh3cG5CdjcyV3BVRTFoS2JKVHVMM1cyV1BPNWc0OUczWEhoaEZaVTdFNFpoY2xmUkV1YkRWeFFZWmZ4LXRpSk54N0tyejNENXNlcmdIUUsyakJOMkJhZXlKREpYRkdDWDhtaUkyNjY2bFd5RGNMN3BJNkI0b0Yzai10REJlaW9MRUtWdklhM0hVb2Zzbk1oUlE0MGkyTVRoQXpzblAwQ0hRNXJTcUdlbVdtM1QyQ0p2?hl=en-US&gl=US&ceid=US%3Aen"
       url_getfinal_url(url1)

            https://news.google.com./articles/CBMi2AFBVV95cUxQR29VRFI2b0pJVk5mVEJqREhqcDhFanhGdld5R1hPUUFrMDROQlVSelFka2wtYlpybi1JaVBOeWt3TWtXS0lLMWJOaUUyQmFIRmdDUVJ0bXlMS2c4LWxMcFJsUWxIM0JqRlNjMTdZSnlfTlhrVWxaVU5Zc0V0c1BuM1Jwcm9SY3N2d2dVS2R0VHNQdTY3WnVOcjFaZmdhejVnaVNJNmNmRlpCWjlSRjZWdVk4TzAzSnRwUjFlMTc1bGxfOF9kcWFqbzFYTng2VWd4aHV6WVBSaXfSAeABQVVfeXFMUHExdlI3RHdVem5oeXNsSFY0T1l3TUFUWGF5TkJFSVc5ekFNSy1iWTBQWWgxU0NrZGJnSjhXeHkxa0VrTThXM1ZPSkU5aHU1NEFBTElNa1lxZUVlTnpYMnpQYkdQSHA5UVJEMGpmWFEtV2tzODI0S19fb05UQTBPRFdnbVE2ZmlyUi1hcmJzblVSNjN1aTcydjdIeEZ0OXBkbnBFVnI2d2lfVFZlUXdhSTI0cmxtZFNvR01qRjJqUk1nbnVGbzNoU1pOcGRVMVRtd1ZPTkc5dlZWY1N4WEpCVTg?hl=en-US&gl=US&ceid=US%3Aen
            https://news.google.com./articles/CBMi4wFBVV95cUxQUzV3OS1makxKQ0VzUFEzczdqOVN3VXNEbHBlVkxTUnhzbzB1MnNsWHdHSXJreDkwZURLNjRicFhTcjdGdkFjVlNPeE40LVdzNTM1TDFIc0ZCYWs2dDBKNXlKR3k4MWFhZTNoTmxqaUVkTXVhcnlVWlZXOVRhTHlkQ3VfNTZIaWxZVHktb1lGZ3dpOEtycEJabDFKMjRoZUd3NTItWFV4SzA2aXA0aW1pMDNvRWlJVjlmOUpZYkpwejBFTzhRczRpcjRvRGFqem5JSVBLSTZ5MUNEVmxEelNONi1zNNIB6AFBVV95cUxOQ1hfa25rT0hNYmFFX1pPSzhzNTZiUFVfVzN5N3F6Y21LT0pPaFpRMlpVWWZkZlFtcmh3cG5CdjcyV3BVRTFoS2JKVHVMM1cyV1BPNWc0OUczWEhoaEZaVTdFNFpoY2xmUkV1YkRWeFFZWmZ4LXRpSk54N0tyejNENXNlcmdIUUsyakJOMkJhZXlKREpYRkdDWDhtaUkyNjY2bFd5RGNMN3BJNkI0b0Yzai10REJlaW9MRUtWdklhM0hVb2Zzbk1oUlE0MGkyTVRoQXpzblAwQ0hRNXJTcUdlbVdtM1QyQ0p2?hl=en-US&gl=US&ceid=US%3Aen


    """
    s = (
        '[[["Fbv4je","[\\"garturlreq\\",[[\\"en-US\\",\\"US\\",[\\"FINANCE_TOP_INDICES\\",\\"WEB_TEST_1_0_0\\"],'
        'null,null,1,1,\\"US:en\\",null,180,null,null,null,null,null,0,null,null,[1608992183,723341000]],'
        '\\"en-US\\",\\"US\\",1,[2,3,4,8],1,0,\\"655000234\\",0,0,null,0],\\"'
        + id1
        + '\\"]",null,"generic"]]]'
    )

    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        "Referer": "https://news.google.com/",
    }

    try:
        log('batch')
        response = requests.post(
          "https://news.google.com/_/DotsSplashUi/data/batchexecute?rpcids=Fbv4je",
               headers=headers,
               data={"f.req": s},
        )

        if response.status_code != 200:
           log("gnews_decode: response code != 200")
           return ""

        text = response.text
        header = '[\\"garturlres\\",\\"'
        footer = '\\",'
        if header not in text:
            log(f"gnews_decode Header not found in response: {text}")
            return ""

        start = text.split(header, 1)[1]
        if footer not in start:
            log("gnews_Footer not found in response.")

        url = start.split(footer, 1)[0]
        return url

    except Exception as e:
        log(e)
        return ""


def url_getfinal_url(url):

   response = None
   try :
      ### Only the header without body Failed in 40% of time.
      response = requests.head(url, allow_redirects=True, verify=False, timeout=5)
      return  str(response.url)

   except Exception as e:
      log(e)
      try:
         if response is None:
            url = response.connection.url
         return str(url)
      except Exception as e2 :
         log(e2)  

   return url



def url_getfinal_url2(url):
    ### have switche to Bing news: Real URL 
    ### only need to get header : scraping is ok because Goose3+ 3rd arty paid PAID
    ### Real URL:  50,000 day --> in 15-20 hours...
    try:  ### Super slow.... faster way..... ??    50,000 URLS  / day. --> 
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            response = page.goto(url, wait_until="networkidle")
            final_url = page.url
            browser.close()
            return final_url
    except Exception as e:
        log(e)
        return url












###################################################################################################
####### Extract News PR ###########################################################################
def run_urlist_prnews(cfg=None, istest=None, name="url_prnews.csv", npool=1):
   """  Fetch URLS from 
       cfg="config/dev/cfg_dev.yaml"
       alias pyfet="python src/fetchers.py "

       pyfet run_urlist_prnews --cfg config/dev/cfg_dev.yaml  --istest 0  --npool 1 
  
  
   """ 
   log("####### run_urlist_prnews")   
   global dirdata   
   cfg0, dirdata, istest =config_load_v2(cfg, istest=istest)
 
   log("######## Load companies ###########################################")
   dircsv   = dirdata + f"/config/{name}"
   com_list = pd_read_file_s3(dircsv, sep=",")
   log(com_list)

   if com_list is None:
       com_list = pd.DataFrame({'url': ['NEC', "ORACLE"] , 
                                'com_name': [ "https://www.nec.com/en/global/corporateblog/index.html",     
                                              "https://www.oracle.com/news/",] })
            
   com_list = com_list.iloc[:2,:] if istest == 1 else com_list
   log('dirdata:', dirdata)       
       
    
   log("######## Start fetching ###########################################")
   from src.fetcher_auto import url_prnews_get_urlist
   urls, coms = [], []   
   n = len(com_list)
   save=1 
   # kbatch = int(n // npool)
   kbatch = 10

   ##### Generate Pool of arguments ##################
   args_tuple_list = []
   for ii, x in com_list.iterrows():
       com_name = x['com_name']
       url      = x['url']
       log(ii, com_name, url)
       urls.append(url)
       coms.append(com_name)

       if (ii % kbatch == 0 or ii >= n-1 ) and ii >0 :
          log(ii, len(args_tuple_list))
          args_tuple_list.append([ urls, dirdata, coms, save    ])
          urls, coms = [], []   

   log("##### Run Fetching ##########################")
   if npool == 1:
      for ii, args in enumerate(args_tuple_list):
          log(ii, )
          urls, dirdata, coms, save = args 
          df, dfmiss = url_prnews_get_urlist(urls= urls,  dirdata = dirdata, 
                                             coms= coms, save=save )
   else:
      # import concurrent.futures.ThreadPoolExecutor  as pool1
      import concurrent
      from concurrent.futures import ProcessPoolExecutor as pool1
      ### npool == len( args_tuple_list )
      with pool1(max_workers=npool) as executor:
              futures = [executor.submit(url_prnews_get_urlist_sync, args) for args in args_tuple_list ]
       
      try:
            done, not_done = concurrent.futures.wait(futures, timeout=120*kbatch, 
                                                     return_when=concurrent.futures.ALL_COMPLETED)            
            for future in not_done:
                future.cancel()
            
            for future in done:
                try:
                    x = future.result(timeout=1)
                except Exception as e:
                    print(f"An error occurred: {str(e)}")
        
      except Exception as e :
            log("Timeout occurred while waiting for all tasks to complete", e)

   log("#### Fetch prnews end")




def url_prnews_get_urlist_sync(args_tuple):
  from src.fetcher_auto import url_prnews_get_urlist         
  import time, random 
  time.sleep(random.uniform(5, 20))
  urls, dirdata, coms, save = args_tuple
  return url_prnews_get_urlist(urls= urls,  dirdata = dirdata, 
                               coms= coms, save=save )




def run_extract_prnews(cfg=None,dirin=None, dirout=None, fetch_miss=1, nmax=0, istest=None):
   """   
       cfg="config/dev/cfg_dev.yaml"
       alias pyfet="python src/fetchers.py "

       pyfet run_extract_prnews --cfg config/dev/cfg_dev.yaml --nmax 1000 

        
   """ 
   log("####### run_extract_prnews")      
   global dirdata   
   cfg0, dirdata, istest =config_load_v2(cfg, istest=istest)   
   cfgd    = cfg0.get("prnews", {})
   if istest == 1:  nmax= 5

   #### Dir Output
   y,m,d,h = date_now(fmt="%Y-%m-%d-%H").split("-")
   dirtmp  = dirdata +"/news_tmp/prnews"

   dirout1 = dirdata + f"/news_text/prnews/year={y}/month={m}/day={d}/hour={h}"
   dirout2 = dirdata + f"/news_urls_miss/prnews/year={y}/month={m}/day={d}/hour={h}"


   log("\n##### Url Loads   #########################################")
   df = url_load_list(dirdata, source='prnews')
   assert df[['url', 'com_name', ]].shape


   log("\n##### Url Clean   #########################################")
   df = pd_clean_previousfetched(cfg, df, source='prnews')  ### matching google URL with Final url !!
   df = pd_clean_previousmiss(cfg, df=df)
   df = pd_add_date_extract_filter(df, coldt='art_dt2')

   df = df if nmax == 0 else df.iloc[:nmax, :]
   df = pd_clean_googlelink(df, colgoogle='url2')
   df = df.drop_duplicates("url")   
   log( df[['url', 'url2']].shape)
   dt     = date_now(fmt="%y%m%d_%H%M%S")
   pd_to_file(df, dirtmp + f"/df_url_{dt}.parquet", show=1)
   urls = df['url'].values


   log("\n##### Url Clean   #########################################")
   url_fetch_text_all(urls, df, dirout1, dirtmp, dirout2)
   




#######################################################################################
def pd_merge(df, right, on='url', how='left', delete_left=1, **kwargs,) :
   if delete_left ==1 : 
      cols = [ coli for coli in df.columns if coli not in right.columns or coli in on ] 
      df2 = df[cols].merge(right, on=on, how=how, **kwargs)

      for ci in right.columns:
         if ci not in on :
            #### To handle NA
            df2[ci] = df2[ci].astype( "str"  )
      return df2 

   else :
      log("deleting right df") 
      return df



def pd_add_date_extract(df, coldt='art2_date',):
    """
        url = 'https://www.nytimes.com/2023/07/18/world/europe/ukraine-russia-war-counteroffensive.html'
        html = '<html><body>Article content...</body></html>'
        print(f"Date: {guess.date}")
        print(f"Accuracy: {guess.accuracy}")
        print(f"Method: {guess.method}")

        dateparser.search.search_dates(text, languages='en', settings=None, add_detected_language=False, detect_languages_function=None)[source]

        oopen(    dft[ [ 'art_dt', 'art2_date', 'dt3' ] ] )
        from date_guesser import guess_date    
        def add1(url, html, dt_current=''):
            try :
               guess = guess_date(url=url, html=html)
               return date_now(guess.date, fmt="%Y-%m-%d")
            except Exception as e :
               log(e)
               return dt_current

        df[coldt] =df.apply( lambda x: add1(x['url'], x['art2_text'], x['art2_date']), axis=1)

        #dirdata="s3://edge-ml-dev/data"
        #dft = pd_read_file_s3(dirdata + "/news_text/year=2024/month=07/day=18/hour=14/*.parquet" )
        #dft[ [ 'art_dt', 'art2_date', 'dt3' ] ]

        # reference_date = datetime(2023, 1, 1)
        # date_string = "5 days ago"
        # parse(, settings={'RELATIVE_BASE': reference_date})
        # text="2024/07/18 Oct 12, 2023"
        # text="2024/07/18 13 days ago"

    """ 
    log("### pd_add_date_extract")
    from dateparser import search, parse

    def dt_google(text):

       xx = str(text).strip()
       if len(xx) <=4 :
          return ""

       xx   = xx.split(" ")
       dt1s = ""

       try : 
         dt1  = xx[0] 
         dt1  = parse(dt1)
         dt1s = date_now(dt1, fmt="%Y-%m-%d") 

         if len(xx) >0 : 
           dt2  = " ".join( xx[1:] )
           if len(dt2) > 3 :
              dt2  = parse(dt2, settings={'RELATIVE_BASE': dt1})      
              dt2s = date_now(dt2, fmt="%Y-%m-%d") 
           else:
              dt2s = ""

         if len(dt2s.split("-")) == 3:
             return dt2s 


         if len(dt1s.split("-")) == 3:
             return dt1s 

         return ""  
       except Exception as e:
         return "" 


    def dt_parse(text, dtref=None):
        dtref2 = date_now(dtref, returnval='datetime')
        ll = search.search_dates(text, languages=['en']) #, settings={'RELATIVE_BASE': dtref} )
        if ll is None or len(ll) < 1: return ""
        else : 
            dts = date_now(ll[0][1], fmt="%Y-%m-%d" )
            return dts

    # dft['dt4'] = dft.apply( lambda x:  dt_parse( x['art2_text']) , axis=1)

    if 'art_dt' in df.columns:
         df[coldt] = df.apply( lambda x:  dt_google( x['art_dt']) , axis=1)

    return df


def to_int(x, val=-1):
    try:
        return int(x)
    except :
        return val     


def pd_add_date_extract_filter(df, coldt='art_dt2', past_days=-30, doextract=1):
    """
        pd_add_date_extract_filter(dfv, coldt='art_dt2')

            2024/07/19 Mar 7  ...  2024-07-19
            2024/07/19 May 8  ...  2024-07-19
            2024/07/19 Jun 6  ...  2024-07-19
          s="Apr 5"
          parse(s)

    """ 
    log("### pd_add_date_extract_filter")

    if doextract == 1:
       log('extract date into', coldt)
       df  = pd_add_date_extract(df, coldt= coldt )

    dt0 = date_now(fmt="%Y%m%d" , add_days= past_days, returnval='int')

    def dt_filter(x):
       ll = str(x).split("-")
       if len(ll) < 3: return True #### Unknown true by default
       di = to_int(x.replace("-",""), 9999999999)
       if di < dt0: return False        
       return True 

    if coldt in  df.columns:
        log('## Before date:', df.shape)      
        df = df[ df[ coldt ].apply(lambda x: dt_filter(x) ) ]
        log('## After date < ', dt0, ': ', df.shape)
    else:
        log('No date filtering', coldt, list(df.columns))

    return df



def newstext_date_fix():
  """
      python src/fetchers.py newstext_date_fix 
      Fix the dates backward

  """
  dirin = "s3://edge-ml-dev/data/news_text/year=2024/month=07/**/*.parquet"
  # dirin = "s3://edge-ml-dev/data/news_znlp/L0_catnews/year=2024/month=07/**/*.parquet"

  flist = glob_glob_s3(dirin)
  log(len(flist))
  for fi in flist:
      log(fi)
      try :
         df = pd_read_file_s3(fi)
         log(df.shape)
         
         # df = df[ -df['art2_text'].str.contains(".shr-debug{font-weight:bolder;") ]
         df = pd_add_date_extract(df, coldt='art2_date')
         log(df[[ 'art_dt', 'art2_date' ]])
         pd_to_file_s3(df, fi , show=0)    
      except Exception as e:
         log(e)
      # break














#######################################################################################
####### Extract content from other ####################################################
def run_newstext(cfg= None, q='partnership ', dirout=None, start=None, end=None, npast=-4,
                 istest=0):
    """ 

       python src/fetchers.py run_newstext --cfg "config/dev/cfg_dev.yaml"               


    """
    cc, dirdata, istest = config_load_v2(cfg, istest=istest)
    
    from newsapi import NewsApiClient
    from src.envs.vars import ne_key
    newsapi = NewsApiClient(api_key= ne_key)
    ssource ='abc-news,abc-news-au,al-jazeera-english,ars-technica,associated-press,australian-financial-review,axios,bbc-news,bbc-sport,bleacher-report,bloomberg,breitbart-news,business-insider,business-insider-uk,buzzfeed,cbc-news,cbs-news,cnn,crypto-coins-news,engadget,entertainment-weekly,espn,espn-cric-info,financial-post,football-italia,fortune,four-four-two,fox-news,fox-sports,google-news,google-news-au,google-news-ca,google-news-in,google-news-uk,hacker-news,ign,independent,mashable,medical-news-today,msnbc,mtv-news,mtv-news-uk,national-geographic,national-review,nbc-news,news24,new-scientist,news-com-au,newsweek,new-york-magazine,next-big-future,nfl-news,nhl-news,politico,polygon,recode,reddit-r-all,reuters,rte,talksport,techcrunch,techradar,the-american-conservative,the-globe-and-mail,the-hill,the-hindu,the-huffington-post,the-irish-times,the-jerusalem-post,the-lad-bible,the-next-web,the-sport-bible,the-times-of-india,the-verge,the-wall-street-journal,the-washington-post,the-washington-times,time,usa-today,vice-news,wired'


    y,m,d,h = date_now(fmt="%Y-%m-%d-%H").split("-")
    dirout2 = dirdata +"/news_text_v2/year={y}/month={m}/day={d}"
    dirout2 = dirout2.format(y=y, m=m,d=d )

    start = date_now(fmt="%Y-%m-%d", add_days= npast ) if start is None else start 
    end   = date_now(fmt="%Y-%m-%d") if end is None else end  


    wlist = [ "company acquisition", "company partnership", "company funding",
              "startup acquisition",
            ]
    
    dfall = pd.DataFrame()
    for word in wlist:
        for pi in range(1, 2):
            log("page:",word,  pi)
            dd = newsapi.get_everything(q= f' {word} ',
                                      sources= ssource,
                                      # category='business',
                                      #searchIn='title',
                                      #domains='bbc.co.uk,techcrunch.com',
                                      from_param=start,
                                      to=end,
                                      language='en',
                                      sort_by='relevancy',
                                      page_size=100,                                   
                                      page=pi)
        

            if dd['totalResults'] < 1: 
                break

            df1 = dd['articles']
            df1 = pd.DataFrame(df1)
            df1['keywords'] = word 
            df1['origin']   = "newspaper"
            dfall = pd.concat((dfall, df1))
            log(df1)


    ts = date_now(fmt="%y%m%d_%H%m%S" ) 
    # q2 =word.strip().lower().replace(" ", "_").replace('"', '')
    dfall = dfall.drop_duplicates("content")
    n =len(dfall)

    dirout1 = dirout2 + f"/text_{ts}_{n}.parquet"
    pd_to_file(dfall, dirout1, show=1)
            



##############################################################
def config_load_v2(cfg= None, istest=None):
   from box import Box 
   global dirdata   
   cfg0    = config_load(cfg) if len(str(cfg)) > 4  else {}   
   dirdata = cfg0.get('data', {}).get('dirdata',  dirdata)   
   istest1 = cfg0.get('istest', 0) if istest is  None else istest
   log(dirdata)
   cfg0 = Box(cfg0)
   log(cfg0)
   log("istest: ", istest1)
   return cfg0, dirdata, istest1






######################################################################################
######################################################################################
def url_extract_text_play(url):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        # browser = pw.chromium.launch(headless=True)  # Launch browser in headless mode
        browser = pw.webkit.launch(headless=True)  # Launch browser in headless mode

        page = browser.new_page()  # Open a new page
        page.goto(url)  # Navigate to the URL
        page.wait_for_selector("selector")  # Wait for the content to load

        # Extract data using locators
        data = page.locator("locator").all_text_contents()
        
        browser.close()  # Close the browser
        return data


def url_extract_text_newspaper(urls=""):
    import newspaper
    from newspaper import news_pool
    if isinstance(urls, str):
       urls = urls.split("\n")

    urls = [url for url in urls if len(url) > 10 and url.startswith("http") ]
    urls = np_remove_dup(urls)  

    papers = [newspaper.build(url) for url in urls]
    news_pool.set(papers, threads_per_source=2)  # Set 2 threads per source
    news_pool.join()  # Start the download process

    results = []
    for paper in papers:
        for article in paper.articles:
            try:
                article.parse()  # Parse the article to access the text
                results.append({
                    'url': article.url,
                    'title': article.title,
                    'date' : article.date,
                    'text': article.text
                })
            except Exception as e:
                results.append({
                    'url': article.url,
                    'error': str(e)
                })

    return results




#####################################################################################
def np_remove_dup(xlist):
    l2= []
    for x in xlist:
        if x not in l2:
              l2.append(x)
    return l2


def request_urls_extract(base_url ):
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a', href=True)
    urls = [link['href'].lower() for link in links ]

    urls = np_remove_dup(urls)
    log(str(urls)[:100] )
    log("N_urls:", len(urls))
    return urls





#####################################################################################
def test2():
    # Example usage
    urlstr = "https://www.bbc.com/news/world-us-canada-59944889\nhttps://news.microsoft.com/category/press-releases/"
    results = url_extract_text_newspaper(urlstr)
    print(results)


def test3():
    urls = urls_fetch_prnweswire( keywords=" microsoft", tag_filter='microsoft')


def test4():
    from utilmy import pd_to_file ### pip instlal utilmy
    df_urls = urls_fetch_yahoonews()
    pd_to_file(df_urls,'finance_url_list.csv', index=False, show=1)

    df_urls = urls_fetch_microsoftnews()
    pd_to_file(df_urls,'finance_url_list.csv', index=False, show=1)

    df_urls = urls_fetch_googlenews()
    pd_to_file(df_urls,'finance_url_list.csv', index=False, show=1)


def test8():
    urls = [ "http://www.example.com" ]
    oks, miss = url_extract_text_goose(urls) 

    df = pd.DataFrame(oks )
    dt0 = date_now(fmt="%Y/%m/%d %H:%M:%S")

    miss_url = [x[0] for x in miss ]
    log(oks)
    log(miss)


def test5():
    source_url = 'https://news.google.com/rss/articles/CBMiLmh0dHBzOi8vd3d3LmJiYy5jb20vbmV3cy9hcnRpY2xlcy9jampqbnhkdjE4OG_SATJodHRwczovL3d3dy5iYmMuY29tL25ld3MvYXJ0aWNsZXMvY2pqam54ZHYxODhvLmFtcA?oc=5'
    print(url_gnews_decode(source_url))





        

def zcheck():
    log("Ok")



###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()




"""

URLS Samples: 

    #### Redirect process



    https://finance.yahoo.com/news/nvidia-microsoft-google-and-others-partner-with-us-government-on-ai-research-program-160111850.html


    https://www.businesswire.com/news

    https://www.prnewswire.com



    https://news.google.com/search?q="Microsoft".%20partnership%20site%3Aprnewswire.com&hl=en-US&gl=US&ceid=US%3Aen


    https://www.prnewswire.com/news-releases/unicef-announces-new-partnership-with-microsoft-to-address-education-crisis-affecting-displaced-and-refugee-children-and-young-people-300719648.html


    https://www.prnewswire.com/news-releases/cognizant-and-microsoft-announce-global-partnership-to-expand-adoption-of-generative-ai-in-the-enterprise-and-drive-industry-transformation-302123026.html


    https://news.google.com/search?q="Microsoft"%20%20"partnership"%20site%3Aprnewswire.com&hl=en-US&gl=US&ceid=US%3Aen



    https://finance.yahoo.com/quote/MSFT/press-releases/


    https://news.microsoft.com/category/press-releases/


    https://www.prnewswire.com/search/news/?keyword=partnership&pagesize=25&page=7


    https://www.prnewswire.com/search/news/?keyword=Microsoft&page=1&pagesize=100

    


url="https://news.google.com/articles/CBMiiQFodHRwczovL3d3dy5taWNyb3NvZnQuY29tL2VuLXVzL3NlY3VyaXR5L2Jsb2cvMjAyNC8wNS8yOC9tb29uc3RvbmUtc2xlZXQtZW1lcmdlcy1hcy1uZXctbm9ydGgta29yZWFuLXRocmVhdC1hY3Rvci13aXRoLW5ldy1iYWctb2YtdHJpY2tzL9IBAA?hl=en-US&gl=US&ceid=US%3Aen"

import requests

response = requests.get(url, allow_redirects=True)
final_url = response.url
print(final_url)



"""



