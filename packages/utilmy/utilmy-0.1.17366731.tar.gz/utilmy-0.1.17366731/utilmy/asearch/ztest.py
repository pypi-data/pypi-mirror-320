"""



    print(get_completion("Hello"))

     python ztest.py phi1


"""


import json

from utilmy import log, json_load, json_save




def phi0():
    # from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from pystealth import PyStealth

    from selenium.webdriver.chrome.service import Service as ChromeService
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from seleniumwire import webdriver

    # from selenium.webdriver.common.proxy import Proxy, ProxyType

    import time

    proxy_host = "45.127.248.127"
    proxy_port = "5128"
    proxy_user = "vzsfvpcp"
    proxy_pass = "iednr47ngm37"

    proxy_options = {
        'proxy': {
            'http': f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}",
            'https': f"https://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}",
            'no_proxy': 'localhost.127.0.0.1'
        }
    }

    options = webdriver.ChromeOptions()

    options.add_argument("user-data-dir=C:\\Users\\The Saviour\\OneDrive\\Documents\\User Data");
    options.add_argument("profile-directory=Profile 8");

    # Initialize WebDriver with options
    driver = webdriver.Chrome(options=options, seleniumwire_options=proxy_options)

    driver.get("http://www.phind.com")
    time.sleep(50)

    # Perform actions or validations here

    # Close the browser
    # driver.quit()





def phi1(q="Capital of USA"):
    """



    :param q:
    :return:
    """
    from selenium import webdriver

    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')

    def get_completion(info):
        global driver
        driver = webdriver.Chrome(options=options)
        driver.get(f"https://www.phind.com/")
        script = """
            return fetch("https://www.phind.com/api/agent", {
                credentials: "include",
                headers: {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
                    "Accept": "*/*",
                    "Accept-Language": "q=0.8,en-US;q=0.5,en;q=0.3",
                    "Content-Type": "application/json",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-origin"
                },\n"""

        script += f'referrer: "https://www.phind.com/agent?q={info}&source=searchbox",\n'
        script += 'body: JSON.stringify({userInput: " ' +info +'", messages: [], shouldRunGPT4: false}),\n'
        script += """
                method: "POST",
                mode: "cors"
            })
            .then(response => response.text())
            .then(data => data)
            .catch(error => console.error(error));
        """

        result = driver.execute_script(script)
        result = result.replace("\n", "").split("data:")
        stroke = []

        driver.quit()

        if "<!DOCTYPE html>" in result[0]:
            print(result[0])
        return result

        # for i in range(len(result)):
        #     try:
        #         x = json.loads(result[i])["choices"][0]["delta"]["content"]
        #         if type(x) == str:
        #             stroke.append(x)
        #     except:
        #         pass
        # return ''.join(stroke)

    res = get_completion(info=q)
    log(res)
    dirout = "./ztmp/phind_res.json"
    json_save(res, dirout)




def phi3(q="Microsot partnerhips in August 2023"):
    """

       python ztest.py phi3

       working


    """
    from playwright.sync_api import sync_playwright
    from halo import Halo

    # Initialize vars
    url = "https://www.phind.com/search?q=" + q

    with sync_playwright() as p:
        # suppress logging and make the browser headless
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        try:
            # Start the spinner
            spinner = Halo("Getting Answer from Phind...\n\n\n\n\n \n", spinner="dots")
            spinner.start()

            # Get the page content
            page.goto(url)

            # wait until its all loaded
            page.wait_for_selector("body", timeout=50000)
            page.wait_for_timeout(15000)

            # Get the elements
            answer_elements = page.query_selector_all("main div.fs-5")

            # init the list
            paragraph_texts = []

            # get content
            for answer_element in answer_elements:
                paragraph_texts.append(answer_element.inner_text().strip())


            text = ""
            for text in paragraph_texts:
                # Stop spinner
                spinner.stop()
                all1 = text +"\n\n "


        finally:
            pass
            # Close the browser
            #browser.close()


def phi2(q="Capital of France"):
    """

       python ztest.py phi2

       working


    """
    import time
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
    from halo import Halo

    # Initialize vars
    url = "https://www.phind.com/search?q=" + q

    # suppress logging
    chrome_options = Options()
    chrome_options.add_argument("--log-level=3")
    # make the browser not open
    #chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    # init the webdriver
    #driver = webdriver.Firefox(options=chrome_options)
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Start the spinner
        spinner = Halo("Getting Answer from Phind...\n\n\n\n\n \n", spinner="dots")
        spinner.start()

        # Get the page content
        driver.get(url)

        # wait until its all loaded
        WebDriverWait(driver, timeout=50).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(15)

        # Get the elements
        answer_elements = driver.find_elements(By.CSS_SELECTOR, "main div.fs-5")

        # init the list
        paragraph_texts = []

        # get content
        for answer_element in answer_elements:
            paragraph_texts.append(answer_element.text.strip())

        # print it
        for text in paragraph_texts:
            # Stop spinner
            spinner.stop()
            print(text)

    finally:
        # Close the browser
        driver.quit()



def ppp():
    from fake_useragent import UserAgent
    import requests, json

    userAgent = UserAgent().chrome
    # Please get key form serper.dev
    serperDevKey = ""
    searchResFrom = "Google"

    # Google Search API From serper.dev
    def getSearchResultFromGoogle(question):
        url = "https://google.serper.dev/search"
        payload = json.dumps({
            "q": question,
            "num": 30
        })
        headers = {
            'X-API-KEY': serperDevKey,
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        searchRes = response.json()
        search_data = {
            "_type": "SearchResponse",
            "queryContext": {
                "originalQuery": searchRes['searchParameters']['q'],
            },
            "webPages": {
                "webSearchUrl": f"https://www.google.com/search?q={searchRes['searchParameters']['q']}",
                "totalEstimatedMatches": len(searchRes["organic"]),
                "value": []
            }
        }
        for resPageIdx in range(len(searchRes["organic"])):
            temp = {
                "id": f"https://api.bing.microsoft.com/api/v7/#WebPages.{resPageIdx}",
                "name": searchRes["organic"][resPageIdx]["title"],
                "url": searchRes["organic"][resPageIdx]["link"],
                # "isFamilyFriendly":true,
                "displayUrl": searchRes["organic"][resPageIdx]["link"],
                "snippet": searchRes["organic"][resPageIdx]["snippet"],
                # "dateLastCrawled":"2023-02-26T01:29:00.0000000Z",
                "deepLinks": [],
                "language": "zh_chs",
                "isNavigational": False
            }
            if "sitelinks" in searchRes["organic"][resPageIdx].keys():
                for deepLink in searchRes["organic"][resPageIdx]["sitelinks"]:
                    temp["deepLinks"].append(
                        {
                            "name": deepLink["title"],
                            "url": deepLink["link"]
                        }
                    )
            search_data["webPages"]["value"].append(temp)
        return search_data

    def getSearchResultFromPhind(session, question):
        search_api = "https://phind.com/api/search"
        search_data = {
            "freshness": "",
            "q": question,
            "userRankList": {
                "developer.mozilla.org": 1,
                "github.com": 1,
                "stackoverflow.com": 1,
                "www.reddit.com": 1,
                "en.wikipedia.org": 1,
                "www.amazon.com": -1,
                "www.quora.com": -2,
                "www.pinterest.com": -3,
                "rust-lang": 2,
                ".rs": 1
            }
        }
        search_api_res = session.post(search_api, json=search_data, headers={'User-Agent': userAgent})
        return search_api_res.json()["processedBingResults"]

    if __name__ == '__main__':
        question = "如何使用Python解决01背包问题？"

        index_url = "https://phind.com/search"
        api_url = "https://phind.com/api/tldr"
        session = requests.session()
        session.get(index_url, headers={'User-Agent': userAgent})
        api_data = {
            "bingResults": None,
            "question": question
        }
        if searchResFrom == "Google":
            api_data["bingResults"] = getSearchResultFromGoogle(question)
        elif searchResFrom == "Phind":
            api_data["bingResults"] = getSearchResultFromPhind(session, question)
        else:
            print("请选定至少一个搜索引擎！")
            exit(-1)

        final_res = session.post(api_url, json=api_data, headers={'User-Agent': userAgent})
        answerText = ""
        answerList = final_res.text.split("data: ")
        for answer in answerList:
            if '{' not in answer or '}' not in answer:
                continue
            else:
                answer = json.loads(answer.strip('\n').strip('\r').strip('\n'))
                if "sentence" in answer.keys():
                    answerText += answer["sentence"]
        print(answerText)




def fake1():
    from fake_useragent import UserAgent
    import requests, json

    userAgent = UserAgent().chrome
    # Please get key form serper.dev
    serperDevKey = ""
    searchResFrom = "Google"

    # Google Search API From serper.dev
    def getSearchResultFromGoogle(question):
        url = "https://google.serper.dev/search"
        payload = json.dumps({
            "q": question,
            "num": 30
        })
        headers = {
            'X-API-KEY': serperDevKey,
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        searchRes = response.json()
        search_data = {
            "_type": "SearchResponse",
            "queryContext": {
                "originalQuery": searchRes['searchParameters']['q'],
            },
            "webPages": {
                "webSearchUrl": f"https://www.google.com/search?q={searchRes['searchParameters']['q']}",
                "totalEstimatedMatches": len(searchRes["organic"]),
                "value": []
            }
        }
        for resPageIdx in range(len(searchRes["organic"])):
            temp = {
                "id": f"https://api.bing.microsoft.com/api/v7/#WebPages.{resPageIdx}",
                "name": searchRes["organic"][resPageIdx]["title"],
                "url": searchRes["organic"][resPageIdx]["link"],
                # "isFamilyFriendly":true,
                "displayUrl": searchRes["organic"][resPageIdx]["link"],
                "snippet": searchRes["organic"][resPageIdx]["snippet"],
                # "dateLastCrawled":"2023-02-26T01:29:00.0000000Z",
                "deepLinks": [],
                "language": "zh_chs",
                "isNavigational": False
            }
            if "sitelinks" in searchRes["organic"][resPageIdx].keys():
                for deepLink in searchRes["organic"][resPageIdx]["sitelinks"]:
                    temp["deepLinks"].append(
                        {
                            "name": deepLink["title"],
                            "url": deepLink["link"]
                        }
                    )
            search_data["webPages"]["value"].append(temp)
        return search_data

    def getSearchResultFromPhind(session, question):
        search_api = "https://phind.com/api/search"
        search_data = {
            "freshness": "",
            "q": question,
            "userRankList": {
                "developer.mozilla.org": 1,
                "github.com": 1,
                "stackoverflow.com": 1,
                "www.reddit.com": 1,
                "en.wikipedia.org": 1,
                "www.amazon.com": -1,
                "www.quora.com": -2,
                "www.pinterest.com": -3,
                "rust-lang": 2,
                ".rs": 1
            }
        }
        search_api_res = session.post(search_api, json=search_data, headers={'User-Agent': userAgent})
        return search_api_res.json()["processedBingResults"]



if __name__ == '__main__':
    import requests
    question = "如何使用Python解决01背包问题？"

    index_url = "https://phind.com/search"
    api_url = "https://phind.com/api/tldr"
    session = requests.session()
    session.get(index_url, headers={'User-Agent': userAgent})
    api_data = {
        "bingResults": None,
        "question": question
    }
    if searchResFrom == "Google":
        api_data["bingResults"] = getSearchResultFromGoogle(question)
    elif searchResFrom == "Phind":
        api_data["bingResults"] = getSearchResultFromPhind(session, question)
    else:
        print("请选定至少一个搜索引擎！")
        exit(-1)

    final_res = session.post(api_url, json=api_data, headers={'User-Agent': userAgent})
    answerText = ""
    answerList = final_res.text.split("data: ")
    for answer in answerList:
        if '{' not in answer or '}' not in answer:
            continue
        else:
            answer = json.loads(answer.strip('\n').strip('\r').strip('\n'))
            if "sentence" in answer.keys():
                answerText += answer["sentence"]
    print(answerText)



###################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()





"""


############ Phind API Reference
         
         ###### Overview
         
         Phind is an AI answer engine that provides users with the ability to interact with an AI model to get answers, assistance with queries, and engage in chat conversations. This API reference details the endpoints available for interacting with Phind's services.
        
         ### This is not finished and subject to change
         
         You might notice that this doc looks a little barebones - I'm working on properly reverse enginering their backend. For now, this is what you get (the old docs were out of date and a lot had changed!).
        
         
         ####### Authentication
         
         ### Get Session
         
             - **Endpoint:** `GET /api/auth/session`
             - **Description:** Retrieves the current session information for the user.
             - **Headers:**
               - `Accept`: `*/*`
               - `Accept-Encoding`: `gzip, deflate, br`
               - `Accept-Language`: Language preferences (e.g., `en-GB,en;q=0.9,en-US;q=0.8`)
             - **Query Parameters:**
               - None.
             - **Response:**
               - **Status Code:** `304 Not Modified` (if session is unchanged) or `200 OK` (if a new session is created).
               - **Content-Type:** `application/json`
               - **Body:** An empty JSON object `{}` or session details.
         
         ## Querying
         
         ### Make a Query
         
             - **Endpoint:** `POST https://https.api.phind.com/infer/`
             - **Description:** Submits a user's question to the AI model and receives an answer.
             - **Headers:**
               - `Content-Type`: `application/json;charset=UTF-8`
               - `Origin`: `https://www.phind.com`
             - **Payload:**
               - `question`: The user's query.
               - `options`: Various options for customizing the query (e.g., `date`, `language`, `detailed`, etc.).
               - `context`: Optional context for the question.
               - `challenge`: A numeric value included for anti-fraud or verification purposes.
             - **Response:**
               - **Status Code:** `200 OK`
               - **Content-Type:** `text/event-stream; charset=utf-8`
               - **Body:** A stream of events containing the AI's responses and follow-up prompts.
         
         ### Cache Query Result
         
             - **Endpoint:** `POST /api/db/cache`
             - **Description:** Stores the results of a query in cache.
             - **Headers:**
               - `Content-Type`: `application/json;charset=UTF-8`
               - `Origin`: `https://www.phind.com`
             - **Payload:**
               - `title`: The title of the query.
               - `value`: An array containing the query and its result.
               - `challenge`: A numeric value for verification.
             - **Response:**
               - **Status Code:** `200 OK`
               - **Content-Type:** `application/json; charset=utf-8`
               - **Body:** A JSON object containing a `request_id`.
         
         ## Chat
         
         ### Preflight Request
         
             - **Endpoint:** `OPTIONS https://https.api.phind.com/agent/`
             - **Description:** A preflight request for CORS that precedes the actual request to the chat endpoint.
             - **Headers:**
               - `Access-Control-Request-Headers`: `content-type`
               - `Access-Control-Request-Method`: `POST`
               - `Origin`: `https://www.phind.com`
             - **Response:**
               - **Status Code:** `200 OK`
               - **Content-Type:** `text/plain; charset=utf-8`
               - **Headers:** Appropriate CORS headers.
         
         ### Send Chat Message
         
         - **Endpoint:** `POST https://https.api.phind.com/agent/`
         - **Description:** Sends a message to the AI chat agent and receives a response.
         - **Headers:**
           - `Content-Type`: `application/json;charset=UTF-8`
           - `Origin`: `https://www.phind.com`
         - **Payload:**
           - `user_input`: The user's chat message.
           - `message_history`: An array of previous messages in the conversation.
           - `requested_model`: The AI model being used for the chat.
           - `anon_user_id`: An anonymous identifier for the user.
           - `challenge`: A numeric value for verification.
         - **Response:**
           - **Status Code:** `200 OK`
           - **Content-Type:** `text/event-stream; charset=utf-8`
           - **Body:** A stream of events containing the chat agent's responses.
         
         ### Store Chat Message
         
         - **Endpoint:** `POST /api/db/chat`
         - **Description:** Stores a chat message in the database.
         - **Headers:**
           - `Content-Type`: `application/json;charset=UTF-8`
           - `Origin`: `https://www.phind.com`
         - **Payload:**
           - `title`: The title or subject of the chat.
           - `messages`: An array of message objects with `role`, `content`, and `metadata`.
           - `challenge`: A numeric value for verification.
         - **Response:**
           - **Status Code:** `200 OK`
           - **Content-Type:** `application/json; charset=utf-8`
           - **Body:** A JSON object with details about the stored chat, including an `id`.
         
         ## Notes
         
         - All endpoints are served over HTTPS and require proper headers to be set for CORS and content type.
         - The `challenge` field in requests is used for security purposes and may be part of anti-fraud measures.
         - Responses, especially those involving AI interactions, are returned as streams of events and may require special handling to process.
         - The exact request content and responses will differ per user and context.
         - This API Reference is based on observed requests and responses and is unofficial.
        
        


"""