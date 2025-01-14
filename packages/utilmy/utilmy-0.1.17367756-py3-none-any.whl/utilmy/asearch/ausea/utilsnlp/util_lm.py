"""
    
    

"""
import asyncio, concurrent, json, time, traceback, random  
import os, copy, random, fire, re, pandas as pd, numpy as np
from box import Box
from pydantic import BaseModel


from concurrent.futures import ThreadPoolExecutor
#from multiprocessing import Pool


##############
from openai import OpenAI


#import dspy
#global turbo  ### Debugging DSPy optinmization


###############
from utilmy import (pd_read_file, pd_to_file, os_makedirs, glob_glob, date_now,
                    json_load, json_save, config_load, log, log2, log_error)

#### Local Import
from src.utilsnlp.util_exp import (exp_config_override)



#########################################################################
####### Test #############################################################


################################################################################
class LLM(object):
    def __init__(self, service='openai', model="gpt-3.5-turbo",
                 dirout="ztmp/gpt_answer/",
                 api_key=None, api_url=None,
                 temperature=0,
                 nclient=1,
                 max_tokens=2000,
                 **kw):
        """ Various util functions for quick LLM : One Liner method
        """
        self.error_callback = None
        self.dirout = dirout
        self.service = service
        self.modelid = model
        if api_key is not None :
             self.api_key = api_key
        else:
             self.api_key = os.environ[ service.upper() + '_KEY']      
             
        ### Output Control
        self.temperature = temperature
        self.max_tokens = max_tokens

        
        self.client = llm_get_client(service= service, api_key= api_key, api_url= api_url)
        log(service, self.modelid, self.client)

        #from multiprocessing import Pool

    def test(self, prompt:str="Capital of france ?"):
        """ 
                 llm1.test() ### test the API KEY

        """        
        ddict = self.client.chat.completions.create(model= self.modelid,
                                                  messages=[{"role": "user", "content": prompt}],
                                                  #logprobs=     dd.logprobs,
                                                  #top_logprobs= dd.topk,
                                                  temperature=  self.temperature,
                                                  max_tokens=   self.max_tokens,
                                                  )
        print(ddict)
        return ddict


    def get_save_sync(self, prompt: str, dirout: str = None, output_schema: object = None):
        """
            result.get() - Blocks until the result is ready
            result.wait() - Waits for the result without blocking
            result.ready() - Checks if the result is available
        """
        prompt_request = promptRequest(prompt=prompt, service=self.service, modelid=self.modelid,
                                       json_schema=output_schema)

        # synchronous call. parallelization responsibility on caller.
        if not output_schema:
            result = llm_get_sync(prompt_request)
        else:
            prompt_request.api_key = self.api_key  ### wokaround for JSON
            result = llm_get_with_schema(prompt_request)

        if dirout is not None:
            self.json_save(dd= result, dirout= dirout)

        return result


    def json_save(self, dd: dict, dirout=None,):
            dirout1 = self.dirout if dirout is None else dirout
            ts, tag = date_now("%y%m%d_%H%M%S"), str(random.randint(10000, 99999))
            fname   = f"{dirout1}/jsllm_{ts}_{tag}.json"
            json_save(dd, fname)


    def get_json(self, prompt_req: object=None, prompt:str=None,  dirout: str = None, output_schema: object = None):

        try:

            if prompt_req is not None:
                dd = prompt_req 
            else:    
                dd = promptRequest(prompt=prompt, service=self.service, modelid=self.modelid,
                                   json_schema=output_schema, max_tokens= self.max_tokens)

            if 'gpt' in self.modelid :
                res = self.client.chat.completions.create(model= self.modelid,
                                                          messages=[{"role": "user", "content": prompt}],
                                                          # logprobs=     dd.logprobs,
                                                          # top_logprobs= dd.topk,
                                                          temperature=  dd.temperature,
                                                          max_tokens=   dd.max_tokens,
                                                          )
            else: ### GROQ and other
                res = self.client.chat.completions.create(model= self.modelid,
                                                          messages=[{"role": "user", "content": prompt}],
                                                          # logprobs=     dd.logprobs,
                                                          # top_logprobs= dd.topk,
                                                          temperature=  dd.temperature,
                                                          max_tokens=   dd.max_tokens,
                                                          )

            dd = res.to_dict()
            dd['prompt'] = prompt
            return dd
        except Exception as e:
            log(traceback.format_exc())
            log(e)
            if "connection error" in str(e).lower():
                log("Waiting 5mins to reconnrect")
                time.sleep(5*60)
                log("Re-starting reconnrect")



    def get_batch(self, prompts: list, dirout: str = None, output_schema: object = None, max_workers=None):

        """ multiple request
        saves output in a jsonl file
        """

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # If max_workers is None or not given, it will default to the number of processors on the machine,
            # multiplied by 5 assuming it"s being used for IO intensive tasks
            # Start the load operations and mark each future with its prompt
            func_to_be_used = llm_get_sync if not output_schema else llm_get_with_schema
            future_to_prompt = {executor.submit(func_to_be_used, promptRequest(prompt=prompt, service=self.service,
                                                    modelid=self.modelid,
                                                    json_schema=output_schema)): prompt for
                                prompt
                                in prompts}
            results = []
            for future in concurrent.futures.as_completed(future_to_prompt):
                url = future_to_prompt[future]
                try:
                    data = future.result()
                    # print(f"data: {data}")
                    results.append(data)
                except Exception as exc:
                    print('%r generated an exception: %s' % (url, exc))

        if dirout is not None:
            ###  1 json contans sub-json
            dirout1 = self.dirout if dirout is None else dirout
            ts, tag = int(time.time()), random.randint(10000, 99999)
            fname = f"{dirout1}/{ts}_{tag}.jsonl"

            with open(fname, 'w') as fp:
                for res in results:
                    fp.write(f"{res}" + '\n')  # json.dump(res)

        return results


    def get_batch_df(self, df, prompt_template: str ,prompt_map_dict: dict,  dirout: str = None, 
                     dirname:str=None,
                     output_schema: object = None, tag="", keeponly_msg=0,
                     npool=1):
        """ Variables in template are consistent with columns in df
            ### prompt:
                Clean the text below:
                     <prompt_ttile>
                     <prompt_text>
                        
            { "<prompt_text>": "text_df_column",
              "<prompt_ttile>": "title_df_column", }

        """
        def prompt_create(x):
           pp = copy.deepcopy(prompt_template) 
           for key_str, coldf_name in prompt_map_dict.items():
              if key_str in prompt_template: 
                  pp = pp.replace(key_str, x[coldf_name] )
           return pp      


        df['llm_prompt'] = df.apply(lambda x: prompt_create(x), axis=1)

        #### Run
        def prompt_run(x):
           try: 
              dd = self.get_json(prompt=x['llm_prompt'])
              return json.dumps(dd)
           except Exception as e:
              log(e)
              return ""   

        t0 = time.time()
        if npool == 1:  
            df['llm_json'+tag] = df.apply(lambda x: prompt_run(x), axis=1)

        else:   
            pr = promptRequest(api_key=self.api_key,
                                   modelid=self.modelid,
                                   service=self.service,
                                   json_schema=output_schema)

            df = pd_parallel_apply(df, llm_get_sync, npool=npool, colout="llm_json", ptype="thread",
                                    prompt_request=pr )

        #### Extract 
        df['llm_msg'+tag] = df['llm_json'].apply(lambda x : self.get_msg(x) )   
        log('dt fetch', time.time()-t0 )
        
        if keeponly_msg == 1:
            del df['llm_prompt']
            del df['llm_json']
            cols = [ 'llm_msg' ]

        else:    
            cols = [ 'llm_prompt', 'llm_json', 'llm_msg' ]


        if dirout is not None:
            ts = date_now("%y%m%d_%H%M%S")
            pd_to_file(df, dirout + f"/df_{ts}.parquet" )   
         

        log("Added cols: ", cols)   
        return df 
        

    def pd_get_msg(self, df, coljson='llm_json', colmsg='llm_msg'):
        df[colmsg] = df[coljson].apply(lambda x: self.get_msg(x))
        log('added ', colmsg)
        log(df['colmsg'].head(3))
        return df


    def get_msg(self, response_json):
        try:
            if isinstance(response_json, str):
                response_json = json.loads(response_json)

            return response_json['choices'][0]['message']['content']
        except Exception as e:
            log(e)
            return ""





def test1():
    """
         python src/utilsnlp/util_lm.py test1 

    """
    df = pd.DataFrame({
           "A" : [ str(i) for i in range(0, 6) ],
           "B" : [ str(i) for i in range(0, 6) ]
        })
    llm1 = LLM("openai", model="gpt-4o-mini", api_key=  os.environ['OPENAI_KEY'])
 
    prompt= """Add those 2 numbers : <A> , <B> """
    pdict = {"<A>" : "A", "<B>" : "B"}
     
    df = llm1.get_batch_df(df, prompt, pdict, npool= 4)  
    log(df)




def pd_parallel_apply(df, myfunc, colout="llm_json", npool=4, ptype="thread", timeout=1, **kwargs):
    """Apply a function to each row of a DataFrame using multithreading.
            Parameters:
            - df (pandas.DataFrame): The DataFrame on which to apply the function.
            - func (function): The function to apply to each row.
            - colout (str): The name of the column in which to store the results.
            - n_threads (int): Number of threads to use for parallel execution.

            submit is instant

            Returns:
            - pandas.DataFrame: DataFrame with the results of the applied function as a new column.
    """
    import concurrent.futures

    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")

    #if len(df) > npool * timeout : 
    #    raise ValueError(f"too big df: {len(df)}, Increase total timeout")
        
    # Define a wrapper function to handle thread-safe operations
    def worker(row, **kwargs):
        return myfunc(row, **kwargs)

    results = []

    if ptype =="process":
         log('Using processes:', npool)
         from concurrent.futures import ProcessPoolExecutor as mp
         with mp(max_workers=npool) as executor:
                # Submit all the tasks to the executor
                futures = [executor.submit( myfunc, row, **kwargs) for _, row in df.iterrows()]

    else:
         import copy
         log('Using threads:', npool)
         from concurrent.futures import ThreadPoolExecutor as mp
         rowlist = [ copy.deepcopy(row) for _,row in df.iterrows() ]

         t0 = time.time()
         with mp(max_workers=npool) as executor:
                # Submit all the tasks to the executor
                futures = []
                for row in  rowlist:
                   futures.append( executor.submit(worker, row, **kwargs)  )
                   #log(time.time() - t0 )

    # results, notdone = concurrent.futures.wait(futures, timeout= timeout) 
    # log(results)
    # log(notdone)

    # Collect the results as they become available
    for future in futures:
        results.append(future.result())

    df[colout] = results
    return df





def pd_parallel_apply_timeout(df, myfunc, colout="llm_json", npool=4, ptype="thread", timeout=1, **kwargs):
    """Apply a function to each row of a DataFrame using multithreading.
            Parameters:
            - df (pandas.DataFrame): The DataFrame on which to apply the function.
            - func (function): The function to apply to each row.
            - colout (str): The name of the column in which to store the results.
            - n_threads (int): Number of threads to use for parallel execution.

            Returns:
            - pandas.DataFrame: DataFrame with the results of the applied function as a new column.
    """
    import concurrent.futures

    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")

    #if len(df) > npool * timeout : 
    #    raise ValueError(f"too big df: {len(df)}, Increase total timeout")
        
    # Define a wrapper function to handle thread-safe operations
    def worker(row, **kwargs):
        return myfunc(row, **kwargs)

    results = []

    if ptype =="process":
         log('Using processes:', npool)
         from concurrent.futures import ProcessPoolExecutor as mp
         with mp(max_workers=npool) as executor:
                # Submit all the tasks to the executor
                futures = [executor.submit( myfunc, row, **kwargs) for _, row in df.iterrows()]

    else:
         import copy
         log('Using threads:', npool)
         from concurrent.futures import ThreadPoolExecutor as mp
         rowlist = [ copy.deepcopy(row) for _,row in df.iterrows() ]

         t0 = time.time()
         with mp(max_workers=npool) as executor:
                # Submit all the tasks to the executor
                futures = []
                for row in  rowlist:
                   futures.append( executor.submit(worker, row, **kwargs)  )
                   log(time.time() - t0 )

         log('fetching', time.time() - t0 )
         try:
            for future in concurrent.futures.as_completed(futures, timeout=1.0):
                log(time.time() - t0 )
                res = future.result()
                results.append(res)
                # 1/0
                # print(f"Task completed with result: {result}")
         except Exception as e:
            dt = time.time() -t0
            msg = f"Task timed out: {dt}," + str(e)
            print(msg)
            results = results + [msg] * (len(df) - len(results) )

    # results, notdone = concurrent.futures.wait(futures, timeout= timeout) 
    # log(results)
    # log(notdone)

    # Collect the results as they become available
    # for future in futures:
    #     results.append(future.result())

    df[colout] = results
    return df




########################################################################################
class promptRequest(BaseModel):
    """
    class to store prompt request. To simplify argument passing while parellizing
    """
    prompt: str  = ""
    service: str = "openai"
    modelid: str = "gpt-3.5-turbo"
    topk: int = 10
    logprobs: bool = False
    temperature: float = 0
    max_tokens: int = 500
    dirout: str = "ztmp/gpt_out"
    json_schema: object = None
    api_key: str = None
    dirout: str = None



def llm_get_sync(row=None,prompt_request: promptRequest=None):
    """
            {
            "choices": [
                {
                    "message": {
                        "content": "Sachin Tendulkar is a former Indian cricketer who is widely regarded as one of the greatest batsmen in the history of the",
                }
            ],
    """
    try:
        prompt1 = row["llm_prompt"] if row is not None else prompt_request.prompt

        client  = llm_get_client(service=prompt_request.service)
        response = client.chat.completions.create(model=prompt_request.modelid,
                                                    messages     = [{"role": "user", "content": prompt1 }],
                                                    # logprobs     = prompt_request.logprobs,
                                                    # top_logprobs = prompt_request.topk,
                                                    temperature  = prompt_request.temperature,
                                                    max_tokens   = prompt_request.max_tokens,
                                                 )

        dd = response.to_dict()
        # time.sleep(10.0)

        dd['prompt'] = prompt1
        return dd
    except Exception as e:
        log(traceback.format_exc())
        log('llm_get_sync:', e)


def llm_get_client(service: str="openai", api_key: str = None, api_url: str = None):

    from openai import OpenAI
    if service == 'groq':
        api_key  = api_key or os.environ['GROQ_KEY']
        api_base = api_url or "https://api.groq.com/openai/v1"
        client   = OpenAI(api_key=api_key, base_url=api_base)
        
    elif service == 'azure':
        from openai import AzureOpenAI
        # https://{your-resource-name}.openai.azure.com/
        endpoint = os.environ.get['AZURE_OPENAI_url']
        client   = AzureOpenAI(api_key=api_key, api_version="2023-12-01-preview",
                                  azure_endpoint=endpoint)
    elif service == 'claude':
        api_key  = api_key or os.environ.get['CLAUDE_KEY']
        api_base = api_url or "https://api.anthropic.com/v1"
        client   = OpenAI(api_key=api_key, base_url=api_base)

    else:
        api_key  = api_key or os.environ['OPENAI_KEY']
        api_base = api_url or "https://api.openai.com/v1"
        client   = OpenAI(api_key=api_key, base_url=api_base)
        # self.modelid = model

    return client



def llm_get_with_schema(prompt_request: promptRequest):
    """
    Async function to get an enforced schema based on the provided prompt and JSON schema.

    Note: GPT_JSON is a wrapper with lightweight dependencies: only OpenAI, pydantic, and backoff.
    It calls openai API on our behalf.



    Args:
        self: The object instance.
        prompt: The prompt to be used in the API call.
        json_schema: json schema to be enforced.
    sample output: {
      "response": {
        "first_name": "Sachin",
        "last_name": "Tendulkar",
        "year_of_birth": 1973,
        "num_seasons_in_nba": 0
      },
      "prompt": "Tell me about Sachin Tendulkar\nRespond with the following JSON schema: {json_schema}"
    }

       need 3.10
    """
    from gpt_json import GPTJSON, GPTMessage, GPTMessageRole
    API_KEY = prompt_request.api_key if prompt_request.api_key is not None else os.environ.get('OPENAI_KEY', '')


    gpt_json = GPTJSON[prompt_request.json_schema](API_KEY, prompt_request.modelid,
                                                   model_max_tokens=prompt_request.max_tokens)

    actual_prompt = f"{prompt_request.prompt}\nRespond with the following JSON schema: {{json_schema}}"
    payload = asyncio.run(gpt_json.run(
        messages=[
            GPTMessage(
                role=GPTMessageRole.USER,
                content=actual_prompt
            )
        ]
    ))
    # print(payload)
    # print(dict(payload))
    dd = {}
    dd["response"] = json.loads(payload.raw_response.content[0].text)
    dd["prompt"] = actual_prompt
    # print(json_response)
    return dd










#######################################################################################
### Prompt storage  ###################################################################
def test_prompt_storage():
    #### Using Prompt 
    template = "ok"
    # make random dirtmp
    tmp_storage = f"ztmp/{random.randint(100, 999)}.csv"
    prompt_storage = PromptStorage(dirstorage=tmp_storage)
    prompt_args = {"args": {
        "document": ("str", "this is  document from which you want to generate queries")
    }}
    #
    prompt_storage.append(prompt_template=template, model_id="gpt-3.5-turbo",
                          task_name="synthetic_query_generation",
                          prompt_args=prompt_args)
    prompt_storage.save()
    temp_df = pd_read_file(tmp_storage)
    assert len(temp_df) == 1
    os.remove(tmp_storage)
    # print(prompt_storage.df)


class PromptStorage:
    def __init__(self, dirstorage: str = None,
                 sep="あ",  ### Using unicode Japanese character....
                 sep_prompt="う"):  ### Using Unicode Japanese character....
        """Initializes a new instance of `PromptStorage` class.

        Args:
            dirstorage (str, optional): path to storage file. Defaults to None.
            sep (str, optional): separator character used in storage file. Defaults to "あ".
            sep_prompt (str, optional): separator character used in prompts. Defaults to "う".

        """
        self.df = None
        ### Fixes column names
        self.cols = ["prompt_id",  ### Unique ID for each prompt
                     "prompt_tags",  ### List of tags :  "questionNews, GPT4test" for easy search 
                     "prompt_template", "prompt_examples", "prompt_args",
                     "prompt_origin", "task_name",
                     "model_id", "dt", "api_endpoint", "info_json"]
        self.sep = sep  # note sep is expected to be single char by scv reader
        self.sep_prompt = sep_prompt

        if isinstance(dirstorage, str):
            self.dirstorage = dirstorage
        else:
            self.dirstorage = os.environ.get("prompt_dirstorage", "ztmp/prompt_hist.csv")

        self.load()

    def promptid_create(self):
        """Generate a unique prompt ID.
        Returns:
            str:  generated prompt ID in  format "YYYYMMDD-HMS-random_number".
        """
        ymd = date_now(fmt="%Y%m%d-%H%M%S")
        prompt_id = f"{ymd}-{random.randint(10, 99)}"
        return prompt_id

    def load(self):
        """Load from dirstorage
        """
        if not os.path.exists(self.dirstorage):
            self.df = pd.DataFrame(columns=self.cols)
            return
        self.df = pd_read_file(self.dirstorage, sep=self.sep, engine="python")
        assert self.df[self.cols].shape



    def append(self, prompt_template, model_id, prompt_args, prompt_examples="",
               task_name="", info_json=""):
        """Append a new prompt to  prompt storage.

        Args:
            prompt_template (str):  template for  prompt.
            model_id (str):  ID of  model.
            prompt_args (dict):  arguments for  prompt.
            prompt_examples (Optional[str]):  examples for  prompt.     : None.
            task_name (Optional[str]):  name of  task.     : None.
            info_json (Optional[str]): Additional information in JSON format.     : None.
        """
        dfnew = {ci: "" for ci in self.cols}

        ### Codeium  and Phind in VScode
        dfnew["prompt_id"] = self.promptid_create()
        dfnew["prompt_template"] = prompt_template
        dfnew["model_id"] = model_id
        dfnew["prompt_args"] = prompt_args
        dfnew["dt"] = date_now(fmt="%Y-%m-%d %H:%M:%S")

        if isinstance(prompt_examples, list):
            prompt_examples = self.sep_prompt.join(prompt_examples)

        dfnew["prompt_examples"] = prompt_examples
        dfnew["task_name"] = task_name
        dfnew["info_json"] = info_json
        dfnew = pd.DataFrame(dfnew)

        self.df = pd.concat([self.df, dfnew], ignore_index=True)
        self.save()
        return dfnew

    def save(self):
        """Save to dirstorage
        """
        pd_to_file(self.df, self.dirstorage, sep=self.sep, index=False)

    def get_prompt(self, prompt_id: str = None, prompt_tags: str = None) -> dict:
        """Retrieves a prompt from `PromptStorage` based on provided `prompt_id` or `prompt_tags`.

            Args:
                prompt_id (str, optional): ID of prompt to retrieve. Defaults to None.
                prompt_tags (str, optional): A comma-separated string of tags to filter prompts by. Defaults to None.

            Returns:
                dict: A dictionary containing retrieved prompt information. 

            Example:
                >>> prompt_storage = PromptStorage()
                >>> prompt_storage.get_prompt(prompt_id="123")
                {'prompt_id': '123', 'prompt_tags': ['tag1', 'tag2'], 'prompt_template': 'Template for Prompt 123'}

                >>> prompt_storage.get_prompt(prompt_tags="tag1,tag3")
                [{'prompt_id': '456', 'prompt_tags': ['tag1', 'tag3'], 'prompt_template': 'Template for Prompt 456'},
                    {'prompt_id': '789', 'prompt_tags': ['tag1', 'tag4'], 'prompt_template': 'Template for Prompt 789'}]
        """

        if isinstance(prompt_id, str):
            dfi = self.df[self.df["prompt_id"] == prompt_id]
            ddict = dfi.to_dict(orient="records")[0]
            return ddict

        elif prompt_tags is not None:
            prompt_tags = prompt_tags if isinstance(prompt_tags, list) else prompt_tags.split(",")
            dfiall = pd.DataFrame()
            for tag in prompt_tags:
                dfi = self.df[self.df["prompt_tags"].str.contains(tag)]
                dfiall = pd.concat((dfiall, dfi))

            log(dfiall[["prompt_id", "prompt_tags", "prompt_template"]])
            return dfiall.to_dict(orient="records")



#########################################################################################
###  Inference: query LLM  ##############################################################
def prompt_create_actual(prompt_template: str, prompt_values: dict):
    """Generate an actual prompt by replacing placeholders in  template with values from  prompt_values dictionary.
    Args:
        prompt_template (str):  template prompt containing placeholders.
        prompt_values (dict): A dictionary containing key-value pairs representing  values to replace  placeholders.

    Returns:
        str:  actual prompt with placeholders replaced by their corresponding values.
    """
    prompt_actual = copy.deepcopy(prompt_template)
    for key, val in prompt_values.items():
        prompt_actual = prompt_actual.replace(f"{{{key}}}", val)
    return prompt_actual


def llm_get_answer(prompt, model="gpt-3.5-turbo", max_tokens=1000):
    """
    """
    client = OpenAI()

    response = client.chat.completions.create(model=model,
                                              messages=[{"role": "user", "content": prompt}],
                                              max_tokens=max_tokens)
    return response.choices[0].message.content


##### prompt Tooling ################
def prompt_compress(text: str) -> str:
    """ Prompt Compression for long text

       ### Usage
         pip install git+https://github.com/microsoft/autogen.git@main  --no-cache
         pip install "llmlingua<0.3"   ### Long context

         python rag/query.py prompt_compress --text "write a long poem with many words."

       ### Infos
         https://github.com/microsoft/autogen.git

         https://microsoft.github.io/autogen/docs/topics/handling_long_contexts/compressing_text_w_llmligua

         https://github.com/microsoft/autogen
         import tempfile

         import fitz  # PyMuPDF
         import requests

         from autogen.agentchat.contrib.capabilities.text_compressors import LLMLingua
         from autogen.agentchat.contrib.capabilities.transforms import TextMessageCompressor

         AUTOGEN_PAPER = "https://arxiv.org/pdf/2308.08155"


         def extract_text_from_pdf():
             # Download PDF
             response = requests.get(AUTOGEN_PAPER)
             response.raise_for_status()  # Ensure download was successful

             text = ""
             # Save PDF to a temporary file
             with tempfile.TemporaryDirectory() as temp_dir:
                 with open(temp_dir + "temp.pdf", "wb") as f:
                     f.write(response.content)

                 # Open PDF
                 with fitz.open(temp_dir + "temp.pdf") as doc:
                     # Read and extract text from each page
                     for page in doc:
                         text += page.get_text()

             return text

         # Example usage
         pdf_text = extract_text_from_pdf()

         llm_lingua = LLMLingua()
         text_compressor = TextMessageCompressor(text_compressor=llm_lingua)
         compressed_text = text_compressor.apply_transform([{"content": pdf_text}])



    """
    from autogen.agentchat.contrib.capabilities.text_compressors import LLMLingua
    from autogen.agentchat.contrib.capabilities.transforms import TextMessageCompressor
    llm_lingua = LLMLingua()
    text_compressor = TextMessageCompressor(text_compressor=llm_lingua)
    ddict = text_compressor.apply_transform([{"content": text}])
    return ddict[0]["content"]


########################################################################################
########## Custom Examples for question generation by LLM  #############################
def zex_generate_question(dirdata: str = "./ztmp/data/cats/agnews/train/",
                          dirout: str = "ztmp/bench",
                          prompt_id: str = "",
                          nfile: int = 1, nquery: int = 1,
                          subsample=1):
    """Generate synthetic queries via LLM

      python query.py generate_question --dataset "ag_news" --nfile 1 --nquery 1
      
    """
    global turbo

    #### Export path of  synthetic queries
    dt = date_now(fmt="%Y%m%d_%H%M%S", returnval="str")
    dirout2 = f"{dirout}/df_synthetic_questions_{dt}.parquet"

    log("####### Load Reference answer data as Context for LLM  ")
    df_context = zex_generate_question_loadata(dirdata=dirdata, nfile=nfile, nrows=nquery, subsample=1)

    log("####### Load Custom Post-processor ")
    llm_output_cleaner_fun = zex_generate_question_llmcleaner

    #########################################################################################
    log("#######  Load prompt template from storage")
    prompt0 = PromptStorage()  ### using ENV variables prompt_dirstorage = "prompts/prompt_hist.csv"
    prompt_dict = prompt0.get_prompt(prompt_id=prompt_id)  ## user decide whihc om
    model_id = prompt_dict.get("model_id", "gpt-3.5-turbo")

    log("###### Generate Synthetic questions from answer ")
    queries = []
    for i, row in df_context.iterrows():
        prompt_values = {"document": row["body"]}
        # print(prompt_values)
        prompt_actual = prompt_create_actual(prompt_dict["prompt_template"], prompt_values)
        answer = llm_get_answer(prompt=prompt_actual, model=model_id)

        # answer =  llm_output_clean_custom_v1(answer)
        # queries = answer.split(sep="@@")
        query = llm_output_cleaner_fun(answer)
        queries.append(query)

    df_context["query"] = queries
    df_context = df_context[["id", "title", "body", "query"]]
    # explode df_query based on query list
    df_context = df_context.explode("query")

    pd_to_file(df_context, f"{dirout2}", show=1)



################################################################################
class MODELALIAS: ### Auto-completion
    gpt35t          = "gpt-3.5-turbo"
    gpt4omini       = "gpt-4o-mini"         #### very slow
    llama3_70b_8192 = "llama3-70b-8192"
    llama3_8b_8192  = "llama3-8b-8192"
    llama_31_8b_instant = 'llama-3.1-8b-instant'
    gemma_7b_it         = 'gemma-7b-it'
    gemma2_9b_it        = 'gemma2-9b-it'




################################################################################
os.environ['OPENAI_KEY']="sk-proj-2YsVF5nIOAUK9KdsrWU0T3BlbkFJNIU4GdtuYcWv1hN5ZHBj"

GKEYS = [
   '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',
   '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',
   "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"

]
os.environ['GROQ_KEY']= random.choice(GKEYS)


llpairs = [
  # ('groq', MODELALIAS.llama3_8b_8192),
  # ('groq', MODELALIAS.llama_31_8b_instant),  
  # ('groq', MODELALIAS.gemma_7b_it),
  # ('groq', MODELALIAS.gemma2_9b_it),  
  ('openai', MODELALIAS.gpt4omini )

]



ppair = random.choice(llpairs)


#########################################################
ptext = Box({
    "text": """Extract company names from:
         <art2_title>
    """,

    "map_dict" : {
         "<art2_title>" : "art2_title"
    }  ,

    'service':  ppair[0] ,
    'name'   :  ppair[1]
})


##########################################################
ptext_summary = Box({
    "text": """ Summarize this news article in 10 lines. 
    Keep relevant and factual information extracted from the news article.
    Discard all information about the writer and date. 
    Provide 15 detailed industry category tags related to this article.
    Extract the company names mentioned in this article. 

         <art2_text>
    """,

    "map_dict" : {
         "<art2_text>" : "art2_text"
    }  ,

    'service':  ppair[0] ,
    'name'   :  ppair[1]
})



ptext_summary_custom = Box({

  "partner": {

                "text": """ You are required to summarize the below article in 25 words or less. Provide the answer directly and rewrite in your own words. If the article is blank or does not have information about a partnership, please mention " error "
            Do not mention "Company X partnered with Company Y", "Company X and Company Y partner", or anything to repeat the fact that Company X partnered with Company Y. This is already mentioned in our platform and we do not need to say it again. Emphasize the benefits and rationale. Start with "To..."
            Further, please use the ISO 4217 format for any currency (USD, EUR, CAD, etc) if it is mentioned on the article.

            Output samples are as follows:
               "To develop an automated solution aimed at streamlining warehouse tasks and improving intra-logistics fulfillment. The solution will combine Siemens' SIMATIC Robot Pick AI, a computer vision software for robots, and Zivid's 3D camera, with Universal Robots' UR20, collaborative robot, to enable a wide range of tasks in fulfillment centers and the e-commerce industry."

               "To form a joint venture for last-mile delivery using gas stations to optimize operations, reduce costs, and improve efficiency in the delivery industry."
         
            Article:
               <art2_text>

                """

            ,"map_dict" : {
                    "<art2_text>" : "text_summary2"
              }  

            ,'service':  ppair[0] 
            ,'name'   :  ppair[1]

  }



  ,"merger": {

              'text': """You are a research analyst covering incumbent Merger and Acquisition (M&A) activities for an innovation research platform. You are required to summarize the below article in 25 words or less. Provide the answer directly.
          Do not mention ""Company X acquired/ merged with Company Y"", ""Company X and Company Y merged"", or anything to repeat the fact that Company X acquired or merged with Company Y. This is already mentioned in our platform and we do not need to say it again. Emphasize the benefits and rationale. Start with ""To...""
          The summary should focus on the M&A itself and the benefits/rationale of entering into the M&A. Be objective on the write up.please use the ISO 4217 format for any currency (USD, EUR, CAD, etc) if it is mentioned on the article""

          Output samples are as follows:
              "To provide enterprises and government agencies with advanced security features across messaging, voice calling, video calling, file sharing, and collaboration in compliance with privacy requirements."
              "To deepen IBM Consulting's ability to serve clients in the UK defence sector with additional highly specialist industry and technical domain skills across digital, cyber and defence cloud solutions."

          Article:
             <art2_text>

              """

              ,"map_dict" : {
                      "<art2_text>" : "text_summary2"
                }  

              ,'service':  ppair[0] 
              ,'name'   :  ppair[1]

  }


  ,"product": {

              'text': """ "You are a research analyst covering product updates for an innovation research platform. Can you please summarize the below article in 25 words or less focusing on the key details of the product update. Provide the answer directly.
                      Avoid marketing/promotion language and maintain a factual tone."

               Article:
                  <art2_text>

              """

              ,"map_dict" : {
                      "<art2_text>" : "text_summary2"
                }  

              ,'service':  ppair[0] 
              ,'name'   :  ppair[1]

  }


})


##########################################################
ptext_merger = Box({
    "text": """You are a market researcher. 
   Extract informations from this news text related to Merger and Acquisition
   and return under this JSON format:
    
          {   "company_buyer": 
              "company_acquired": 
              "amount":
              "currency":
              "date_acquisition":
         }

    Example:
    
         

    Discard all other information and make sure the information are inside the text.
    Think step by step.
    ### News text:
         <art2_title>

         <art2_text>


    """,

    "map_dict" : {
         "<art2_title>" : "art2_title",
         "<art2_text>" :  "art2_text"

    }  ,

    'service':  ppair[0] ,
    'name'   :  ppair[1]
})




####### Custom  #################################################################
def zex_generate_question_loadata(dirdata: str = "./ztmp/data/cats/agnews/train/",
                                  nfile=1, nrows=1000, subsample=1):
    log("###### Load Reference answer data  ")
    # diranswer = f"{dirdata}/agnews/train/df*.parquet"
    df = pd_read_file(dirdata, nfile=nfile)  ##  Real Dataset

    log("###### Data : Filter out rows with body length < 100 words")
    df["len"] = df["body"].apply(lambda x: len(x.split()))
    df = df[df["len"] > 100]
    log(df.shape)
    nquery = min(nrows, len(df))
    df_context = df.sample(nquery) if subsample > 0 else df
    log(df_context)

    return df_context


def zex_generate_question_llmcleaner(query: str, sep="@@"):
    """
    hacky way to clean queries. Ideally should be separated by separator only.
    """
    query = query.replace("\n", "")
    query_list = query.split("?")

    # remove sep
    query_list = [q.replace(sep, "") for q in query_list]

    # remove numbered prefix via regex
    query_list = [re.sub(r"^[0-9]*\.", "", q) for q in query_list]
    query_list = [q.strip() for q in query_list]
    query_list = [q for q in query_list if len(q) > 0]
    query_list = [f"{q}?" for q in query_list]

    return query_list
    # result = sep.join(query_list)
    # return result




##########################################################################################
if __name__ == '__main__':
    fire.Fire()










