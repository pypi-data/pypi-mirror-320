""" 

### 
   export PYTHONPATH="$(pwd)"
   alias pyfet="python src/fetchers.py  "

   echo $PYTHONPATH

   ### Extract daily URL:
      pyfet run_urlist    --cfg $config


   ### Extract text content
      pyfet url_extract_all   --cfg $config


   262 URL ferches, 32 failed   --> 10% failed.



"""
import warnings
warnings.filterwarnings("ignore")
import time, os, sys, pkgutil
import pandas as pd, numpy as np
from goose3 import Goose
from typing import Tuple
import requests
from bs4 import BeautifulSoup

from src.utils.utilmy_base import (diskcache_decorator, config_load )


from src.utils.utilmy_aws import (
  pd_to_file_s3,
  pd_read_file_s3, pd_read_file_s3_glob, pd_read_file_s3list,
  glob_glob_s3, glob_filter_dirlevel, glob_filter_filedate
)



from utilmy import (
   pd_read_file, pd_to_file,
   glob_glob, os_makedirs, log, log2, loge,
   date_now, 
)

############################################################################################
global dirdata
dirdata="./ztmp/data"


def init():
   log('cache') 
   os.environ['CACHE_ENABLE'] = "1"
   os.environ['CACHE_DIR']    = "ztmp/cache/mycache2"
   os.environ['CACHE_TTL']    = "9600"
   os.environ['CACHE_SIZE']    = "1000000000"


init()


def test13():

   df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})   
   #  pd_to_file_s3(df, "s3://edge-ml-dev/ztmp/test.parquet" , show=1)

   pd_to_file_s3(df, "s3://edge-ml-dev/ztmp/test/year=2024/month=03/day=02/hours=2/df.parquet" , show=1)



   
   
############################################################################################
######### URL Fetchers #####################################################################
def run_urlist(cfg=None, dirout="./ztmp/data/news_urls"):
   """  Fetch URLS from 

       alias pyfet="python src/fetchers.py "

       pyfet run_urlist  --cfg "" 

       pyfet run_urlist --cfg config/dev/cfg_dev.yaml  

       pyfet test13


   """ 
   global dirdata   
   cfg0     = config_load(cfg) if len(str(cfg)) > 4  else {}   
   dirdata  = cfg0.get('data', {}).get('dirdata',  dirdata)
   com_list = cfg0.get('news', {}).get('com_list', ["microsoft" ])

   com_list = ["microsoft", "google cloud", "amazon web service", "oracle", "apple", "google",
               "ibm", "nvidia", 'meta', "azure"               
             ]

   log('dirdata:', dirdata)       
   y,m,d,h = date_now(fmt="%Y-%m-%d-%H").split("-")
   HMS     = date_now(fmt="%H%M%S")

   dirout2 = dirdata + f"/news_urls/year={y}/month={m}/day={d}/hours={h}"
   log('dirout2:', dirout2)
   
   
   log("######## Start fetching ###########################################")
   log(str(com_list)[:100])
   urlall = []
   for com_name in com_list:
       urls = urls_fetch_prnweswire(keywords=f"{com_name}", tag_filter='{com_name}', com_name=com_name, pagemax=2)
       urlall.extend(urls)

       urls  = urls_fetch_googlenews(keywords= f"{com_name} partner", com_name=com_name,  pagemax=2)
       urlall.extend(urls)

       urls  = urls_fetch_googlenews(keywords= f"{com_name} acquisition", com_name=com_name,  pagemax=2)
       urlall.extend(urls)

       urls  = urls_fetch_googlenews(keywords= f"{com_name} collaboration", com_name=com_name,  pagemax=2)
       urlall.extend(urls)

   #### Custom pages
   urls = urls_fetch_microsoftnews()
   urlall.extend(urls)

   df = pd.DataFrame(urlall)
   df['url'] = df['url'].astype('str')

   df['origin_dt'] = date_now( returnval='unix')
   diroutk = dirout2 + f"/df_{HMS}_{len(df)}.parquet"
   pd_to_file_s3(df, diroutk , show=1)





##########################################################
@diskcache_decorator
def urls_fetch_prnweswire(keywords=" microsoft", tag_filter='microsoft', com_name=None, pagemax=2):

    keywords = keywords.replace(" ", "+")     

    prefix   = "https://www.prnewswire.com"
    url0     = 'https://www.prnewswire.com/search/news/?keyword={keywords}&page={k}&pagesize=200'
    url0     = url0.replace("{keywords}", keywords )
    
    urls2=[]
    for k in range(1, pagemax+1):
       urlk = url0.replace("{k}", str(k))
       urls = urls_extract(urlk)

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



@diskcache_decorator
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



@diskcache_decorator
def urls_fetch_microsoftnews(url = "https://news.microsoft.com/category/press-releases/"):
    TAG_ARTICLE = 'article.category-press-releases'
    TAG_DIV = 'div.c-paragraph-3.c-meta-text'
    A_TAG = 'a.f-post-link.c-heading-6.m-chevron'

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

    urls2 = [ {"url": str(x['url']), 'name': 'microsoft', 'origin': 'news.microsoft.com/category/press-releases/', 'keywords': "",
               'art_title' : x['title'],
               'art_dt' :    x['date']
             }  for x in url_list ]       
    return urls2


@diskcache_decorator
def urls_fetch_googlenews(keywords="microsoft funding", com_name="microsoft", pagemax=2,):

    prefix = 'https://news.google.com'
    dt0 = date_now(fmt="%Y/%m/%d ")
    urlp = "https://news.google.com/search?q="
    keys = keywords.split(" ")
    keys = [  f"%22{x}%22" for x in keys   ]
    keys = "%20".join(keys)
    #keys = keywords.replace(" ", "%20" )
    url = f"{urlp}{keys}&hl=en-US&when%3A15d&gl=US&ceid=US%3Aen"         ##√
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
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(5000)

        url_list = []
        items = page.query_selector_all(ARTICLE_SELECTOR)

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

    urls2 = [ {"url": str(prefix + x['url']), 'name': com_name,  'keywords': com_name, 
                 'art_title': x['title'], 'art_dt': dt0 + x['date'],
                 'origin': x['origin']
              }  for x in url_list   ]      
    return urls2


@diskcache_decorator
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









#######################################################################################
####### Extract contetn ###############################################################
def url_extract_all(cfg=None,dirin=None, dirout=None, fetch_miss=1, nmax=0):
   """
   
       cfg="config/dev/cfg_dev.yaml"
       alias pyfet="python src/fetchers.py "
       pyfet url_extract_all --cfg config/dev/cfg_dev.yaml --nmax 100 

       


   """ 
   global dirdata   
   cfg0    = config_load(cfg) if len(str(cfg)) > 4  else {}   
   dirdata = cfg0.get('data', {}).get('dirdata',  dirdata)
   cfgd    = cfg0.get("url", {})


   #### Dir Input
   dirin1 = dirdata + "/news_urls/year={y}/month={m}/day={d}/**/*.parquet"


   #### Dir Output
   y,m,d,h = date_now(fmt="%Y-%m-%d-%H").split("-")
   dirtmp  = dirdata +"/news_tmp/url_extract_all"

   dirout1 = dirdata + "/news_text/year={y}/month={m}/day={d}/hour={h}"
   dirout1 = dirout1.format(y=y,m=m,d=d,h=h)

   dirout2 = dirdata + "/news_urls_miss/year={y}/month={m}/day={d}/hour={h}"
   dirout2 = dirout2.format(y=y,m=m,d=d,h=h)


   log("\n##### Url Loads   #########################################")
   for iday in range(0, 20, 1): 
      y,m,d   = date_now(fmt="%Y-%m-%d", add_days= -iday).split("-")
      dirin1a = dirin1.format(y=y,m=m,d=d)
      flist   = glob_glob_s3(dirin1a)
      if len(flist) > 0:
          break 
      log('flist empty:', dirin1a)
   
   df = pd_read_file_s3(dirin1a)
   log(df.shape, list(df.columns))


   log("\n##### Url Clean   #########################################")
   df = df.drop_duplicates("url")
   df = df[df['url'].str.startswith('http')]
   df = pd_clean_previousfetched(cfg, df)
   df = df if nmax == 0 else df.iloc[:nmax, :]
   df = pd_clean_googlelink(df)
   df = df.drop_duplicates("url")

   urls = df['url'].values
   pd_to_file(df, dirtmp +"/df.parquet", show=1) 


   log("\n##### Extract 1st round ##################################")
   cols_extract = ['url', 'art2_title', 'art2_date', 'art2_text']
   oks, miss    = url_extract_text_goose(urls=urls, timeout=90)        


   #### Valid ones
   dfok = pd.DataFrame(oks)
   dfok = dfok[['url', 'title', 'date', 'text' ]]
   dfok.columns = cols_extract   
   df   = df.merge(dfok, on=['url'], how='left')
   for coli in [ 'url', 'art2_title', 'art2_date', 'art2_text' ]:
      df[coli]= df[coli].astype('str')

   df2    = pd_remove_invalid_text(df, col="art2_text" )
   ok_urls= np_remove_dup( df2['url'].values )


   log("\n##### Save on disk #####")
   if len(df2)> 0:   
      HMS = date_now(fmt="%H%M%S")
      diroutk = f"{dirout1}/df_text_{HMS}_{len(df2)}.parquet"
      pd_to_file(df2, diroutk, show=1) 
      pd_to_file(df[df['art2_text'].isna()], dirtmp +"/df_miss_1.parquet", show=0) 



   log("\n##### Extract 2nd  URL #################################")
   miss_urls = [x for x in df['url'].values if x not in set(ok_urls) ]
   if len(miss_urls)< 1: return 

   from src.fetcher_auto import run_fetch
   df3, df3_miss = run_fetch(miss_urls, cols_extract)
   df3    = pd_remove_invalid_text(df3, col="art2_text" )
   ok_urls= np_add_unique(ok_urls, df3['url'].values )

   df  = pd_merge(df, df3[ cols_extract ], on=['url'], how='left')
   df3 = pd_remove_invalid_text(df, col="art2_text" )

   if len(df3)> 0:
      HMS = date_now(fmt="%H%M%S")
      diroutk = f"{dirout1}/df_text2_{HMS}_{len(df3)}.parquet"
      pd_to_file(df3, diroutk, show=1) 
      pd_to_file(df[df['art2_text'].isna()], dirtmp +"/df_miss_2.parquet", show=0) 



   log("\n##### Extract 3nd URL #################################")
   miss_urls = [x for x in df['url'].values if x not in set(ok_urls) ]
   if len(miss_urls)< 1: return 

   from src.fetcher_auto import run_fetch_v3
   df3    = run_fetch_v3(miss_urls, cols_extract)
   df3    = pd_remove_invalid_text(df3, col="art2_text" )
   ok_urls= np_add_unique(ok_urls, df3['url'].values )

   df     = pd_merge(df, df3[ cols_extract ], on=['url'], how='left')
   df3    = pd_remove_invalid_text(df, col="art2_text" )

   if len(df3)> 0:
      HMS = date_now(fmt="%H%M%S")
      diroutk = f"{dirout1}/df_text3_{HMS}_{len(df3)}.parquet"
      pd_to_file(df3, diroutk, show=1) 
      pd_to_file(df[df['art2_text'].isna()], dirtmp +"/df_miss_3.parquet", show=0) 



   log("\n##### Extract 4rd URL #################################")
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
   dfmiss = df[ -df['url'].isin(ok_urls)]
   log("N_OK", len(ok_urls), 'N_miss:', len(dfmiss))
   if len(dfmiss)>0:
     HMS = date_now(fmt="%H%M%S")
     diroutk = f"{dirout2}/df_miss_{HMS}_{len(dfmiss)}_all.parquet"
     pd_to_file(dfmiss, diroutk, show=1) 




##################################################################################
##################################################################################
def pd_merge(df, right, on='url', how='left', delete_left=1, **kwargs,) :
   if delete_left ==1 : 
      cols = [ coli for coli in df.columns if coli not in right.columns or coli in on ] 
      df2 = df[cols].merge(right, on=on, how=how, **kwargs)
      return df2 


#@diskcache_decorator
def pd_clean_googlelink(df, nmax=10000000):
    log("##### Google Link Renormalization #####################")
    log(df.shape)
    df['url2'] = df['url']
    urls = df['url'].values[:nmax]
    res = []
    for url in urls: 
        if "google.com" in url:
           # res.append( url_getfinal_url(url) )
           res.append( url_gnews_decode(url) )
        else:   
           res.append( url )

    df['url'] = res
    return df


@diskcache_decorator
def pd_clean_previousfetched(cfg=None, df=None):
    """
         dirdata
         cfg = "config/dev/cfg_dev.yaml"

    """
    global dirdata   
    cfg0     = config_load(cfg) if len(str(cfg)) > 4  else {}   
    dirdata  = cfg0.get('data', {}).get('dirdata',  dirdata)

    y,m,d,h = date_now(fmt="%Y-%m-%d-%H").split("-")

    log("Nurls All:", len(df))
    urlspast = url_load_previousfetched(cfg, y=y, m=m)
    df = df[ -df['url'].isin(urlspast)]
    log("Nurls News:", len(df))

    return df 


@diskcache_decorator
def url_load_previousfetched(cfg=None,y=None,m=None):
    """
         dirdata
         cfg = "config/dev/cfg_dev.yaml"
         dfold = url_load_previousfetched(cfg)

    """
    global dirdata   
    cfg0     = config_load(cfg) if len(str(cfg)) > 4  else {}   
    dirdata  = cfg0.get('data', {}).get('dirdata',  dirdata)

    if y is None :
       y,m,d,h = date_now(fmt="%Y-%m-%d-%H").split("-")

    dirin1 = dirdata + "/news_text/year={y}/month={m}/**/*.parquet"
    dirin1 = dirin1.format(y=y,m=m,)

    # flist = glob_glob_s3(dirin1)
    # flist = np_remove_dup(flist)
    # if len(flist)<1:
    #    log("No previous files to match")
    #    return set()
    dfold = pd_read_file_s3(dirin1,  npool=4)
    dfold = dfold.drop_duplicates('url')
    urls2 = dfold['url'].values
    urls2 = [ x for x in urls2 if x.startswith("http")]
    urls2 = set(urls2)    
    log("N_Prev-fetched: ", len(urls2))
    return urls2



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



@diskcache_decorator
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
    for jj,url in enumerate(urls):
        dt = time.time() - t0
        try:
            article = g.extract(url=url)
            title = article.title 
            text  = article.cleaned_text

            # goose3 return exception message as article.title rather than rising an exception
            if title in ERRORS  or   not text_is_valid_v1(text) :
                miss.append( (url, title, text) )  
                log(jj, url, title)
            else:
                dd = { 'url' :  str(url),
                      'title':  str(article.title),
                      'date':   str(article.publish_date),
                      'text':   str(text)
                }
                oks.append( dd )
                ii = ii +1

        except Exception as e :
             log(ii, url,  e)
             miss.append( (url, str(e) ) )              
    g.close()
 
    dt = time.time()-t0 
    log( f"Fetched {ii} / {n_urls}", dt )
    return oks, miss



def text_is_valid_v1(txt):
    ll =["please enable cookies",
         "unfortunately the page that you",
         "why have i been blocked",
         "performance & security by",
         "waiting for www.",
         "this page appears",
         "this site https://",
         "about this page our systems have detected",
         "experiencing technical difficulty",
         "you can register for free by",
         "error with your",
    ]

    if len(txt) < 100: 
        return False

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



def test_goose():
    urls = [ "http://www.example.com" ]
    oks, miss = url_extract_text_goose(urls) 

    df = pd.DataFrame(oks )
    dt0 = date_now(fmt="%Y/%m/%d %H:%M:%S")

    miss_url = [x[0] for x in miss ]
    log(oks)
    log(miss)



def url_getfinal_url(url):

   try :
      ### Only the header without body
      response = requests.head(url, allow_redirects=True, verify=False, timeout=5)
      return  response.url
   except Exception as e:
      log(e)
      try:
         url = response.connection.url
         return url
      except Exception as e2 :
         log(e2)  

   return url


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








def url_gnews_decode(source_url):

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
            decoded_str = decoded_str[2:length+1]
        else:
            decoded_str = decoded_str[1:length+1]

        return decoded_str
    else:
        return source_url

def test3():
    source_url = 'https://news.google.com/rss/articles/CBMiLmh0dHBzOi8vd3d3LmJiYy5jb20vbmV3cy9hcnRpY2xlcy9jampqbnhkdjE4OG_SATJodHRwczovL3d3dy5iYmMuY29tL25ld3MvYXJ0aWNsZXMvY2pqam54ZHYxODhvLmFtcA?oc=5'
    print(url_decode_google_news_url(source_url))






#######################################################################################
####### Extract content from other ####################################################
def run_newsapi():
    """ 

        from newsapi import NewsApiClient

        # /v2/top-headlines/sources
        sources = newsapi.get_sources()

        dfs = pd.DataFrame(sources["sources"] )
        dfs = dfs[dfs.language == "en" ]
        dfs['name'].values 

        sstr = ",".join(dfs['id'].values )


    """
    from newsapi import NewsApiClient
    newspaper_apikey = os.environ.get( "newspaper_apikey", "987dc435fc99427bbd2afebe2dc4757e")
    newsapi = NewsApiClient(api_key= newspaper_apikey)
    ssource ='abc-news,abc-news-au,al-jazeera-english,ars-technica,associated-press,australian-financial-review,axios,bbc-news,bbc-sport,bleacher-report,bloomberg,breitbart-news,business-insider,business-insider-uk,buzzfeed,cbc-news,cbs-news,cnn,crypto-coins-news,engadget,entertainment-weekly,espn,espn-cric-info,financial-post,football-italia,fortune,four-four-two,fox-news,fox-sports,google-news,google-news-au,google-news-ca,google-news-in,google-news-uk,hacker-news,ign,independent,mashable,medical-news-today,msnbc,mtv-news,mtv-news-uk,national-geographic,national-review,nbc-news,news24,new-scientist,news-com-au,newsweek,new-york-magazine,next-big-future,nfl-news,nhl-news,politico,polygon,recode,reddit-r-all,reuters,rte,talksport,techcrunch,techradar,the-american-conservative,the-globe-and-mail,the-hill,the-hindu,the-huffington-post,the-irish-times,the-jerusalem-post,the-lad-bible,the-next-web,the-sport-bible,the-times-of-india,the-verge,the-wall-street-journal,the-washington-post,the-washington-times,time,usa-today,vice-news,wired'

    y,m,d,h = date_now(fmt="%Y-%m-%d-%H").split("-")
    dirout2 = dirdata +"/news_text_v2/year={y}/month={m}/day={d}"
    dirout2 = dirout2.format(y=y, m=m,d=d )

    t1 = date_now(fmt="%Y-%m-%d", add_days=0 )
    t0 = date_now(fmt="%Y-%m-%d", add_days=-5)


    wlist = ['partnership', 'acquisition']
    
    dfall = pd.DataFrame()
    for word in wlist:
        for pi in range(1, 6):
            log("page:",word,  pi)
            dd = newsapi.get_everything(q= f' {word} ',
                                      sources= ssource,
                                      # category='business',
                                      #searchIn='title',
                                      #domains='bbc.co.uk,techcrunch.com',
                                      from_param=t0,
                                      to=t1,
                                      language='en',
                                      sort_by='relevancy',
                                      #pageSize=100,
                                  
                                      page=pi)
        

            if dd['totalResults'] < 1: 
                break

            df1 = dd['articles']
            df1 = pd.DataFrame(df1)
            df1['keywords'] = word 
            df1['origin']   = "newspaper"
            dfall = pd.concat((dfall, df1))


    dfall = dfall.drop_duplicates("content")
    dirout3 = dirout2 + f"/df_{len(dfall)}.parquet"
    pd_to_file(dfall, dirout3, show=1)
















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


def urls_extract(base_url ):
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



