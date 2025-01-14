"""




python src/fetcher_auto.py test1


"""
import re, time, requests, asyncio
import pandas as pd

from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from utilmy import pd_to_file, pd_read_file, date_now, log


from src.engine.api.base import url0
from src.utils.utilmy_base import (diskcache_decorator )
from src.envs.vars import *


dirdata="./ztmp/data"


##########################################################################################
def test1():
    urls_list     = ["https://3dprint.com/109310/airbus-autodesk-dividing-wall/amp/"]
    df2, df2_miss = run_fetch(urls_list)
    assert df2[[ "url", "art2_title", "art2_text",       ]].shape
    


##########################################################################################
def url_getfinal_url(url):

   try :
      ### Only the header without body
      response = requests.head(url, allow_redirects=True, verify=False, timeout=5)
      return  response.url
   except Exception as e:
      log(e)
      try :
         response = requests.get(url, stream=True, timeout=5)
         url2 = response.url
         response.close()
         return url2 
      except Exception as e:
         log(e)  

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



##########################################################################################
def clean(xstr):
    return re.sub('\n+', '', re.sub('\s+', ' ', xstr)).strip()


def remove_misc(text):
    MISC_WORDS = ["Articles", "News", "Share", "LinkedIn", "Twitter", "Facebook", "WhatsApp", "Email"]
    for misc in MISC_WORDS :
        text = text.replace(misc, "")

    return text


def url_extract_words(url) :

    # trims last char if it is "/"
    if url.endswith("/") :
        url = url[:-1]

    # get the longest string which is potentially the url title
    word_list = url.split("/")[-1]

    # many urls will have potential keywords list in second last part of it
    if len(url.split("/")[-1]) <  len(url.split("/")[-2]) :
        word_list = url.split("/")[-2]

    # remove words with length less than 5
    word_list = list(filter(lambda ele: len(ele) >= 5, word_list.split("-")))

    return word_list, url


def get_best_content(txt_all, txt_specific, txt_all_sel, txt_sel_specific):
    if (len(txt_all) > 0 and len(txt_specific) > 0) and (len(txt_all) > len(txt_specific)):

        # if there is slight difference (upto 20%) in the text lengths, then it is highly possible that specific tags have got precise core content
        if float(len(txt_specific))/float(len(txt_all)) < 0.2:
            txt, txt_sel = txt_specific, txt_sel_specific
        else:
            txt, txt_sel = txt_all, txt_all_sel

    elif txt_specific != "":
        txt, txt_sel = txt_specific, txt_sel_specific

    else :
        txt, txt_sel = txt_all, txt_all_sel

    return txt, txt_sel


def find_best(text, text_sel, title, title_sel, txt, txt_sel, ttl, ttl_sel, txt_len, ttl_len, word):
    if txt_len < len(text) :
        txt, txt_sel, txt_len = text, text_sel, len(text)

    if title.lower().startswith(word.lower()):
        # this is the title even if anything else has longer length
        ttl, ttl_sel, ttl_len = title, title_sel, 200

    if ttl_len < len(title):
        ttl, ttl_sel, ttl_len = title, title_sel, len(title)

    return txt, txt_sel, txt_len, ttl, ttl_sel, ttl_len



def playw_extract_tag_text(page, elts, word, source):
    max_len, text, text_sel = 0, "", ""

    try :
        for elt in elts:
            # checking if the elt is html elt or not if not isinstance(elt, page._elt_handle_factory.create_js_handle('HTMLelt')._impl), so if goes to except, means elt is not html elt and we should move to next elt in loop
            try :
                elt_text = elt.inner_text()

            except :
                continue

            # skip texts exceeding char len of 230 for potential titles
            if source == "Title" and len(elt_text) > 230:
                continue

            else :
                elt_text = remove_misc(elt_text)

            # check if given word is present in the element text
            if word.lower() in elt_text.lower():
                elt_tag = elt.get_property('tagName').json_value().lower()

                # skip "script" tags
                if elt_tag == "script" :
                    continue

                # check if element is having class attribute present
                elt_classes = None

                if elt.get_attribute("class") :
                    elt_classes = ".".join(elt.get_attribute("class").split())

                elt_sel = f"{elt_tag}.{elt_classes}" if elt_classes else elt_tag

                # prioritize elements with tag=h1, for potential titles over other elements
                if source.strip() == "Title" and elt_tag == "h1":
                    return elt_text, elt_sel

                if max_len < len(elt_text) :
                    text, text_sel, txt_len = elt_text, elt_sel, len(elt_text)

    except Exception as e:
        pass

    return text, text_sel



def playw_cookies(page):
    try:
        # list of possible "accept all cookies" button selectors
        cookie_btn_sel = 'button[title="Accept all"], button[id="onetrust-accept-btn-handler"], a[id="btnSelectAllCheckboxes"], button[aria-label="Accept cookies"], button[id*="cookie"], button[class*="cookie"]'
        if page.is_visible(cookie_btn_sel):
            page.click(cookie_btn_sel)

    except:
        pass


def playw_find_sel_by_text(page, txt):

    playw_cookies(page)

    # find all elts, potential title and potential content elements
    all_elts   = page.query_selector_all("body *")
    title_elts = page.query_selector_all('h1, h2, [class*="heading"], [class*="header"], [class*="title"]')
    txt_elts   = page.query_selector_all('[class*="entry-content"], [class*="articleBody"], [class*="post-content"], [class*="content-body"], [class*="article-body"], [class*="the-content"], [class*="article-content"]')

    # get best title and core text found for the given word from all potential elements
    title, title_sel = playw_extract_tag_text(page, title_elts, txt, "Title")
    txt_specific, txt_sel_specific = playw_extract_tag_text(page, txt_elts, txt, "Core")
    txt_all, txt_all_sel = playw_extract_tag_text(page, all_elts, txt, "Core")

    # choose one core text from "potential selectors" and "all selectors"
    txt, txt_sel = get_best_content(txt_all, txt_specific, txt_all_sel, txt_sel_specific)

    return txt_sel, txt, title_sel, title


@diskcache_decorator
def run_fetch(urls_list, dirout="./ztmp", cols_extract=None):
    """

    """
    cols_extract = [ "url", "art2_date", "art2_title", "art2_text", "info"  ]
    
    dirout = dirdata +'/news_tmp/playw_run_fetch/'
    #fout        = open( dirout + "/extract_all.tsv", "w")
    #fout_miss   = open( dirout + "/extract_miss.tsv", "w")

    fout = []
    fout_miss = []

    # write headers in output files
    # fout.write("\t".join([ "url", "text_sel", "text", "title_sel", "title" ])+"\n")
    # fout_miss.write("\t".join([ "url", "error"]))

    # open browser with playwright
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page    = browser.new_page()

        # parse urls in list, one by one to get the core text and title
        for ii, url1 in enumerate(urls_list) :
            log("fetching:", ii )
            try :
                page.goto(url1)

                word_list, url1 = url_extract_words(url1)

                txt_len, txt, txt_sel = 0, "", ""
                ttl_len, ttl, ttl_sel = 0, "", ""

                for word in word_list:
                    text_sel, text, title_sel, title = playw_find_sel_by_text(page, word)

                    # compare the potential text and title we got for this word, with texts and titles from previous words and update the texts, selectors, max lengths of texts
                    txt, txt_sel, txt_len, ttl, ttl_sel, ttl_len = find_best(text, text_sel, title, title_sel, txt, txt_sel, ttl, ttl_sel, txt_len, ttl_len, word_list[0])
                            
                # write output for every url,
                # fout.write("\t".join([clean(url1), clean(txt_sel), clean(txt), clean(ttl_sel), clean(ttl)])+"\n")
                fout.append([clean(url1), clean(txt_sel), clean(txt), clean(ttl_sel), clean(ttl)] )

            except Exception as e:
                # fout_miss.write(url1+"\t"+clean(str(e))+"\n")
                log(e)
                fout_miss.append( [url1, clean(str(e)) ] )

        browser.close()


    #### Fetched
    fout = pd.DataFrame(fout, 
                        columns = [ "url", "text_sel", "art2_text", "title_sel", "art2_title" ] )

    fout['info'] = fout.apply(lambda x: f"'text-sel':{x['text_sel']};'title_sel':{x['title_sel']}", axis=1)
    fout["art2_date"] = date_now(fmt="%Y/%m/%d")

    fout = fout[ cols_extract ]
    log("\nFetched:\n", fout)
    YMD = date_now(fmt="%y%m%d")
    if len(fout) > 0:
       pd_to_file(fout,      dirout + f'/text/df_text_{YMD}.parquet', show=0)  


    #### Missed 
    fout_miss = pd.DataFrame(fout_miss, columns= [ "url", "err_msg" ] )
    log("\n\nMissed: ", fout_miss)
    if len(fout_miss) > 0:      
       pd_to_file(fout_miss, dirout + f'/miss/df_miss_{YMD}.parquet', show=0)  

    return fout, fout_miss








###################################################################
##### Global params  ##############################################
#@diskcache_decorator
def run_fetch_v3(urls_list, dirout=None, cols_extract=None,npool=4, mode='level1'):
    """
      
         urls_list = miss_urls
      


    """
    from utilmy.parallel import multithread_run, multiproc_tochunk
    from utilmy import os_makedirs
    
    log('Mode:', mode)

    if isinstance(dirout, str):
        os_makedirs(dirout)
        input_fixed = {"dirout": dirout, "mode": mode}  # input_fixed={'const': 50, 'const2': i}
    else:
        input_fixed = {"mode": mode}  

    
    if not isinstance(urls_list, list):
        urls_list = list(urls_list)
            

    input_list_list = multiproc_tochunk(urls_list, npool= npool )
    npool           = min( len(urls_list), npool)
    res = multithread_run(fetch_and_save, input_list_list, 
                        n_pool=npool, input_fixed=input_fixed)


    cols0 = [ 'art2_text', 'art2_title', 'art2_date', 'html_dict' ]  
    if len(res) < 1:
        df= pd.DataFrame([], columns= cols0 )
        return df

    try:
        ##### Wrapping results ##############################################
        res2 = []
        for resi in res:
            res2 = res2 +resi   ### Flatten list of list
        df = pd.DataFrame(res2)
        log(df.shape, list(df.columns))
        log(df)

        ##### Details
        df['html_dict']  = df['html'].apply(lambda x : html_parse_goose(x) )
        df['art2_date']  = df['html_dict'].apply(lambda x: x['publish_date'] )
        df['art2_title'] = df['html_dict'].apply(lambda x: x['title'] )
        df['art2_text']  = df['html_dict'].apply(lambda x: x['cleaned_text'] )

    except Exception as e: 
        log(e)
        df= pd.DataFrame([], columns= cols0 )
        return df

    assert df[[ 'art2_text', 'art2_title', 'art2_date' ]].shape
    return df 


 
def fetch_and_save(urls, dirout=None, mode='level1'):
    """ urls = 

       fetch_and_save(urls, dirout="./ztmp/data/urls_fetch/", mode='level1')
    """
    global url0, params1, params2
    from copy import deepcopy
    import time, random, json, requests

    params0 = params2 if mode == 'level2' else params1
    
    if isinstance(urls, str):
        urls = [urls]
    
    if isinstance(urls, list):  ### for parallel compute
        if isinstance(urls[0], list):
          urls = urls[0]
          
    res = []      
    for url in urls:
        try:        
            if 'google.com' in url:
               pp = deepcopy(params1b)
            else:
               pp = deepcopy(params0)

            pp['url'] = url
            response  = requests.get( url=url0, params=pp, )    
            html      = response.text
            url_final = response.url
            dd   = { "url": url,  "html": html, 'info' : "" }

            if dirout is not None :
                ts, tag  = int(time.time()),random.randint(10000, 99999)
                filename = f"{dirout}/urlfetch_{ts}_{tag}.json"            
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(dd, f, ensure_ascii=False, indent=2)
            
            res.append(dd)
            
        except Exception as e:
            log('Error: ', url,e)            
    return res


def fetch_parallel(dirin:str  ="./ztmp/data/urls/url_all.csv",
                   dirout:str ="./ztmp/data/urls_fetch/latest/", 
                   npool=3, max_url=1000000, istart=0,):
    
    from utilmy.parallel import multithread_run,multiproc_tochunk
    from utilmy import os_makedirs
    import tempfile
    
    os_makedirs(dirout)

    urls = url_load_filter(dirin, istart=istart, max_url=max_url)
    input_list_list  = multiproc_tochunk(urls[:max_url], npool=npool )
    input_fixed = {"dirout": dirout}  # input_fixed={'const': 50, 'const2': i}
    time.sleep(2)

    res = multithread_run(fetch_and_save, input_list_list, 
                        n_pool=npool, input_fixed=input_fixed)


def url_load_filter(dirin, istart=0, max_url=1000000):
    urls = pd_read_file(dirin, sep="\t")
    urls = urls.iloc[istart:istart+max_url,:]
    log('N_urls : ', len(urls))

    from src.fetchers import url_load_previousfetched
    urls_done = url_load_previousfetched()
    urls = urls[ -urls.url.str.contains("edge") ]  
    urls = urls[ -urls.url.isin(urls_done) ]    
    urls = urls.drop_duplicates('url')

    log('N_urls to fetch: ', len(urls))
    return list(urls['url'].values)




##################################################################################
##################################################################################
def url_merge_json(dirin="./ztmp/data/urls_fetch/", dirout="./ztmp/data/urls_text/", istest=False):

    from utilmy import glob_glob, json_load
    import json
    from src.utils.utilmy_base import hash_int64     
    flist = glob_glob(f"{dirin}/*.json",)    
        
    df = []
    for ii,fi in enumerate(flist): 
        if ii % 20 == 0 : log(ii)
        try:
            djson = json_load(fi)
            dd = html_parse_goose(djson['html'])
            ri ={
                'url'      : djson['url'], ### original url
                'date'     : str_to_date(dd['publish_date']),
                'title'    : dd['title'],
                'text'     : dd['cleaned_text'],
                'info_json': json.dumps(dd)
            }        
            df.append(ri)
        except Exception as e:
            log('error:', ii, e )
        if istest: break 
               
    df = pd.DataFrame(df)
    for ci in ['date', 'text', 'url' ]:
       df[ci] = df[ci].astype("str")
      
    #ymd = date_now(fmt="%y%m%d")
    #tag = hash_int64(str(df['url'].values))
    #diroutk = f"{dirout}/{ymd}/url_text_{tag}.parquet"  
    #pd_to_file(df, diroutk, show=1)
    return df 



def html_parse_goose(html):
    from goose3 import Goose
    if html.endswith('.html'):
       with open('./ztmp/data/urls/page1.html', 'r') as f:
           html_content = f.read()
    else: 
       html_content = html       

    g = Goose()
    article = g.extract(raw_html=html_content)
    dd = {
        'title'           : article.title,
        'cleaned_text'    : article.cleaned_text,
        'meta_description': article.meta_description,
        'meta_keywords'   : article.meta_keywords,
        'canonical_link'  : article.canonical_link,
        'domain'          : article.domain,
        'top_image'       : str(article.top_image.src) if article.top_image else None,
        'movies'          : [v.src for v in article.movies],
        'publish_date'    : str(article.publish_date),
        'authors'         : article.authors,
        'tags'            : article.tags,
        'links'           : article.links,
        'final_url'       : article.final_url,
        'meta_lang'       : article.meta_lang,
        'meta_favicon'    : article.meta_favicon
    }
    return dd



def str_to_date(x):
    """
        str_to_date(1684171328 )
        str_to_date( ['2023-03-01 17:33:10', '2023-03-01T12:03:10+00:00'] )
        
    """
    import dateparser
    from utilmy import date_now
    if isinstance(x, list):
           if len(x)> 0 :
              x = x[0]
           else : return ""    
               
    x1 = str(x)
    try:
        x2 =float(x1)
        return date_now(x2, fmt="%Y-%m-%d")
    except :
        pass        

    try:                  
        x2 = str(x1).split("T")[0]
        d1 = dateparser.parse(x2)
        d1 = date_now(d1, fmt="%Y-%m-%d")
        return d1 
    except Exception as e:
        return str(x)




def url_redirect():
   """
from apify_client import ApifyClient

# Initialize the ApifyClient with your Apify API token
client = ApifyClient("<YOUR_API_TOKEN>")

# Prepare the Actor input
run_input = {}

# Run the Actor and wait for it to finish
run = client.actor("manishrc/url-redirect").call(run_input=run_input)

# Fetch and print Actor results from the run's dataset (if there are any)
print("💾 Check your data here: https://console.apify.com/storage/datasets/" + run["defaultDatasetId"])
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(item)

# 📚 Want to learn more 📖? Go to → https://docs.apify.com/api/client/python/docs/quick-start

   """





###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()


