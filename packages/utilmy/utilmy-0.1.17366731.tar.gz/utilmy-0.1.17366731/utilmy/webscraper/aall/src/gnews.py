"""
Docs :
           https://github.com/ultrafunkamsterdam/undetected-chromedriver

            https://gist.github.com/shtange/f0a16a7b5e8ec08804cbff61618d95ed

            https://gist.github.com/huksley/bc3cb046157a99cd9d1517b32f91a99e


            https://www.marketingscoop.com/tech/web-scraping/how-to-log-in-to-a-website-using-scrapingbee-with-nodejs/



Usage 
   pip install utilmy

   cd aall
   python gnews.py  url_getfinal_url   --dirin  dfurl.csv



"""




import time
import fire
from utilmy import pd_read_file
import pandas as pd

def pd_parallel_apply(df, myfunc, colout="url2", npool=4, ptype="thread", **kwargs):
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")

    def worker(row, **kwargs):
        return myfunc(row, **kwargs)
    
    results = []

    if ptype == "process":
        from concurrent.futures import ProcessPoolExecutor as mp
        with mp(max_workers=npool) as executor:
            futures = [executor.submit(myfunc, row, **kwargs) for _, row in df.iterrows()]

    else:
        from concurrent.futures import ThreadPoolExecutor as mp
        with mp(max_workers=npool) as executor:
            futures = [executor.submit(worker, row, **kwargs) for _, row in df.iterrows()]

    for future in futures:
        results.append(future.result())

    df[colout] = results
    return df 



def fetch_url(row):
    try:
        from playwright.sync_api import sync_playwright
        from playwright_stealth import stealth_sync
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            stealth_sync(page)
            page.goto(row['url'], wait_until="networkidle")
            # time.sleep(3)
            current_url = page.url
            browser.close()
            return current_url
    except Exception as e:
        print (e)
        # return row['url']


def url_getfinal_url(dirin: str):
    df = pd_read_file(dirin, sep="\t")
    log(df)
    first20_df = df[: 5]
    # print (first20_df)
    final_df = pd_parallel_apply(first20_df, fetch_url, npool=2)
    print (final_df['url2'])
    return final_df



if __name__ == '__main__':
    fire.Fire()
