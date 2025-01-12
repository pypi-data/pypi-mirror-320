"""




"""




import time
import fire
from utilmy import pd_read_file
import pandas as pd

def pd_parallel_apply(df, myfunc, colout="llm_json", npool=4, ptype="process", **kwargs):
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



def fetch_url(url):
    try:
        from playwright.sync_api import sync_playwright
        from playwright_stealth import stealth_sync
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            stealth_sync(page)
            page.goto(url, wait_until="networkidle")
            current_url = page.url
            browser.close()
            return current_url
    except Exception as e:
        return url


def url_getfinal_url(file: str):
    df = pd_read_file(file)
    final_df = pd_parallel_apply(df, fetch_url)
    print (final_df)
    return final_df




if __name__ == '__main__':
    fire.Fire()





