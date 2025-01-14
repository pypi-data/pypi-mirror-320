""" LLM tooling

    #### Init
        cd webapi/asearch/
        export PYTHONPATH="$(pwd)"


    ### Usage:
        alias pyllm="python rag/llm.py       "

        # Prompt Optimization
            pyllm prompt_find_best --dirout ztmp/exp/

        # Generating synthetic queries
            pyllm generate_question  --dirdata ztmp/bench --dataset ag_news --nfile 10 --nquery 5 --prompt_id "20240505-514"


   Instread thw whole text to LLM
      we can chunk the text in sentence and only triplet on the sentences,
          much smaller size --> more precise extraction.


    Prompt + good chunking --> ++ results
       Provide the list of relation in the prompt.
         Normalized relation in the prompt.
          Provide 

       List of relation (previously extracted)
          "capital of"

          Submit inside the prompt.
          Pseudo context Limitation.

   Context the : RAG-like.

   RAG on the news :  another dataset.
      Qdrant release some tooling: Sparse + neo4J 


   export OPENAI_API_KEY="sk-UYj8"

   os.environ['OPENAI_KEY'] = "sk-proj-5dxaa_WWY-JPe7AUP3EMtavCmIrEJeOxk39omg6wCT7A8AaKPY-6Csj6gVipcA"


"""
from typing import Type, get_origin, get_args, List, Literal
from typing import Union
try:
    from types import UnionType
except ImportError:
    UnionType = Union


import asyncio, concurrent, json, time, traceback, random
from concurrent.futures import ThreadPoolExecutor
import os, copy, random, fire, re, pandas as pd
from box import Box
from pydantic import BaseModel

##############
from openai import OpenAI


###############
from utilmy import (pd_read_file, pd_to_file, os_makedirs, glob_glob, date_now,
                    json_load, json_save, config_load)
from utilmy import log, log2, log_error

#### Local Import
# from utils.util_exp import (exp_config_override)

# from utilmy import json_save

def date_get(ymd=None, add_days=0):
    y,m,d,h = date_now(ymd, fmt="%Y-%m-%d-%H", add_days= add_days).split("-")
    ts      = date_now(ymd, fmt="%Y%m%d_%H%M%S")
    return y,m,d,h,ts


#########################################################################
####### LLM Swiss-knife Class to call quickly ###########################
def test_all_llm():
    os.environ["LLM_ROTATE_KEY"] ="1"
    test_llm_without_schema()
    test_llm_without_schema_bulk()
    test_llm_get_with_schema()
    test_llm_get_with_schema_bulk()


def test_single_request():
    dirout = "ztmp/gpt_out/"
    llm1 = LLM('openai', 'gpt-4o-mini')
    llm1.get_save_sync("What is capital of Germany?", dirout=dirout)  ### No blocker calll


def test_bulk():
    dirout = "ztmp/gpt_out/"
    llm1 = LLM('openai', 'gpt-3.5-turbo')
    llm1.get_batch(["What is capital of Germany?",
                        "What is capital of France?",
                        "What is capital of Spain?",
                        "What is capital of India?",
                        ], dirout=dirout)


def test_llm_without_schema():
    prompt = "Tell me about Nelson Mandela"
    llm1 = LLM('openai', 'gpt-3.5-turbo')
    result = llm1.get_save_sync(prompt=prompt, output_schema=None, dirout=None)
    try:
        answer = result["choices"][0]["message"]["content"]
    except Exception as err:
        answer = ""
    assert len(answer) > 0


def test_llm_without_schema_bulk():
    prompts = ["Tell me about Nelson Mandela", "What is the Capital of Argentina?", "Where is Canada?"]
    # TODO: put all parameters even default
    llm1 = LLM(service='openai', model='gpt-3.5-turbo')
    results = llm1.get_batch(prompts=prompts, output_schema=None, dirout=None)
    try:
        answers = [result["choices"][0]["message"]["content"] for result in results]
    except Exception as err:
        answers = [""]
    assert all([len(answer) > 0 for answer in answers])


def test_llm_get_with_schema():
    class PlayerFormat(BaseModel):
        first_name: str
        last_name: str
        year_of_birth: int
        num_seasons_in_nba: int

    class AbstractDetailsFormat(BaseModel):
        problem: str
        approach: str
        evaluation: str

    test_data = [
        ("Tell me about Stephen Curry", PlayerFormat),
        ("Tell me about Michael Jordan", PlayerFormat),
        (
            "Provide details about following abstract:\n```Abstract: The dominant sequence transduction models are based on complex recurrent or convolutional neural networks in an encoder-decoder configuration. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train. Our model achieves 28.4 BLEU on the WMT 2014 English-to-German translation task, improving over the existing best results, including ensembles by over 2 BLEU. On the WMT 2014 English-to-French translation task, our model establishes a new single-model state-of-the-art BLEU score of 41.8 after training for 3.5 days on eight GPUs, a small fraction of the training costs of the best models from the literature. We show that the Transformer generalizes well to other tasks by applying it successfully to English constituency parsing both with large and limited training data.```",
            AbstractDetailsFormat),
    ]
    for prompt, answer_format in test_data:
        llm1 = LLM('openai', 'gpt-3.5-turbo')
        result = llm1.get_save_sync(prompt=prompt, output_schema=answer_format, dirout=None)
        try:
            answer = result["choices"][0]["message"]["content"]
            answer = llm_cleanup_gpt_jsonformat(answer)
            answer = json.loads(answer)
            # answer = result["response"]
        except Exception as err:
            print(traceback.format_exc())
            answer = {}

        assert set(answer_format.model_fields.keys()).difference(set(answer.keys())) == set()


def test_llm_get_with_schema_bulk():
    class AnswerFormat(BaseModel):
        first_name: str
        last_name: str
        year_of_birth: int
        num_seasons_in_nba: int

    prompts = ["Tell me about Stephen Curry", "Provide details about Michael Jordan", "Who was Nelson Mandela?"]
    llm1 = LLM('openai', 'gpt-3.5-turbo')
    results = llm1.get_batch(prompts=prompts, output_schema=AnswerFormat, dirout=None)
    try:
        # log(results)
        answers = [result["choices"][0]["message"]["content"] for result in results]
        answers = [llm_cleanup_gpt_jsonformat(answer) for answer in answers]
        answers = [json.loads(answer) for answer in answers]
        # log(answers)
    except Exception as err:
        print(traceback.format_exc())
        answers = [{}]
    assert all([set(AnswerFormat.model_fields.keys()).difference(set(answer.keys())) == set() for answer in answers])


def test_df_parallel(nrows:int=30, npool:int=10):
    llm1 = LLM('openai', 'gpt-3.5-turbo')
    df = pd_read_file("ztmp/bench/norm/ag_news/test/df_0.parquet")
    df = df[["text_id", "title", "text"]][:nrows]
    # print(df[:2])
    prompt_template = """Generate title for text below:                    
                     ```
                     <prompt_text>
                     ```
                     """
    prompt_map_dict = {"<prompt_text>": "text"}
    s_time = time.time()
    df = llm1.get_batch_df(df, prompt_template, prompt_map_dict, dirout="ztmp/gpt_out/", npool=npool )
    log(f"nrows: {nrows}, npool: {npool}, df process time: {time.time() - s_time}")
    assert df.shape == (nrows, 6)


###############################################################################















################################################################################
def llm_get_client(service: str = "openai", api_key: str = None, api_url: str = None):

    from openai import OpenAI
    if service == 'groq':

        from groq import Groq
        if str(os.environ.get("LLM_ROTATE_KEY", "1" )) in {"1"} :
            api_key = random.choice(GKEYS)
            
        else:        
            api_key = api_key or  random.choice(GKEYS) 
        # api_base = api_url or "https://api.groq.com/openai/v1"
        # client = OpenAI(api_key=api_key, base_url=api_base)
        # log2(api_key)

        # os.environ['GROQ_KEY'] = api_key 
        client = Groq(api_key=api_key)


    elif service == 'azure':
        from openai import AzureOpenAI
        # https://{your-resource-name}.openai.azure.com/
        endpoint = os.environ.get['AZURE_OPENAI_url']
        client = AzureOpenAI(api_key=api_key, api_version="2023-12-01-preview",
                             azure_endpoint=endpoint)

    elif service == 'claude':
        api_key = api_key or os.environ.get('CLAUDE_KEY', os.environ.get('CLAUDE_API_KEY',None))
        api_base = api_url or "https://api.anthropic.com/v1"
        client = OpenAI(api_key=api_key, base_url=api_base)


    elif service == 'gemini':
        api_key = api_key or os.environ.get('GEMINI_API_KEY', os.environ.get('GEMINI_API_KEY',None))
        api_base = api_url or "https://generativelanguage.googleapis.com/v1beta/openai/"
        client = OpenAI(api_key=api_key, base_url=api_base)


    else:
        api_key = api_key or os.environ.get('OPENAI_KEY', os.environ.get('OPENAI_API_KEY', None  ))
        if api_key is None:    
            log('No OPENAI_KEY, OPENAI_API_KEY, un-available ')
            return None

        api_base = api_url or "https://api.openai.com/v1"
        client = OpenAI(api_key=api_key, base_url=api_base)
        # self.modelid = model

    #log2(client)
    return client



class LLM(object):
    def __init__(self, service='openai', model="gpt-3.5-turbo",
                 dirout="ztmp/gpt_answer/",
                 api_key="", api_url=None,
                 temperature=0,
                 max_tokens=5000,
                 cfg = None,
                 cfg_name = None,
                 **kw):
        """ Various util functions for quick LLM : One Liner method
            Portable class to any project.

             ll1 = LLM(service='groq', mdoel='llama3-70b', )
             ll1.get_save(prompt+'mypromt, dirout='ztmp/dirout/")
             GROQ
             Llama3-8b-8192
             self = Box({})
             

             service='openai'; model="llama3_8b_8192";
             dirout="ztmp/gpt_answer/";
             api_key=None; api_url=None;
             temperature=0;
             max_tokens=2000;

             api_key      = os.environ['GROQ_KEY']
             self.modelid = "llama3-8b-8192"


        """
        if isinstance(cfg, str):
            from utilmy import config_load
            cfg0 = config_load(cfg)
            cfgd = cfg0.get(cfg_name, {}) if cfg_name is not None else cfg0

            self.error_callback = None
            self.dirout  = cfgd.get('dirout', dirout)
            self.service = cfgd.get('service', service)
            self.modelid = str(cfgd.get('model', model))
            # self.api_key = cfgd.get('api_key', api_key)

            ### Output Control
            self.temperature = cfgd.get('temperature', temperature)
            self.max_tokens  = cfgd.get('max_tokens',  max_tokens)


        else:

            self.error_callback = None
            self.dirout  = dirout
            self.service = service
            self.modelid = str(model)
            # self.api_key = api_key

            ### Output Control
            self.temperature = temperature
            self.max_tokens = max_tokens

        if  'true' in str(self.modelid).lower() :
            log('Error modelid is empty')
            1/0
            

        self.client = llm_get_client(service=service, api_url=api_url)
        log(service, self.modelid, self.client)


    def test(self, prompt: str = "Capital of france ?"):
        """ 
                 llm1.test() ### test the API KEY

        """
        ddict = self.client.chat.completions.create(model=self.modelid,
                                                    messages=[{"role": "user", "content": prompt}],
                                                    # logprobs=     dd.logprobs,
                                                    # top_logprobs= dd.topk,
                                                    temperature=self.temperature,
                                                    max_tokens=self.max_tokens,
                                                    )
        print(ddict)
        return ddict

    def prompt_validate(self, prompti:str, prompt_map:dict):
          """  VALIDATE prompt with schema
             prompti = PROMPTS["question_create_v3"]
          """
          import re
          matches = re.findall(r'<(.*?)>', prompti)

          for xi in matches:
              if  "<"+xi+">" not in prompt_map:
                 log("missing var in Map_dict:", xi )
                 return False

          log("prompt vars exist in map")       
          return True



    def generate(self, user_message: str, system_message: str) -> str:
        result = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_message},
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
            model=self.modelid,
            temperature=self.temperature,
            top_p=1,
            stop=None,
            stream=False,
        )
        return result.choices[0].message.content


    def get_save_sync(self, prompt: str, dirout: str = None, output_schema: object = None):
        """
            result.get() - Blocks until the result is ready
            result.wait() - Waits for the result without blocking
            result.ready() - Checks if the result is available
        """
        prompt_request = promptRequest(prompt=prompt, max_tokens=self.max_tokens, service=self.service, modelid=self.modelid,
                                       json_schema=output_schema)

        # synchronous call. parallelization responsibility on caller.
        result = llm_get_sync(prompt_request=prompt_request)

        if dirout is not None:
            self.json_save(dd=result, dirout=dirout)

        return result


    def json_save(self, dd: dict, dirout=None, ):
        dirout1 = self.dirout if dirout is None else dirout
        ts, tag = date_now(fmt="%y%m%d_%H%M%S"), str(random.randint(10000, 99999))
        fname = f"{dirout1}/jsllm_{ts}_{tag}.json"
        json_save(dd, fname)


    def get_json(self, prompt_req: object = None, prompt: str = None, dirout: str = None, output_schema: object = None):

        try:

            if prompt_req is not None:
                dd = prompt_req
            else:
                dd = promptRequest(prompt=prompt, service=self.service, modelid=self.modelid,
                                   json_schema=output_schema)

            if 'gpt' in self.modelid:
                res = self.client.chat.completions.create(model=self.modelid,
                                                          messages=[{"role": "user", "content": prompt}],
                                                          #logprobs= dd.logprobs,
                                                          #top_logprobs=dd.topk,
                                                          temperature=dd.temperature,
                                                          max_tokens=dd.max_tokens,
                                                          )
            else:  ### GROQ and other
                res = self.client.chat.completions.create(model=self.modelid,
                                                          messages=[{"role": "user", "content": prompt}],
                                                          # logprobs=     dd.logprobs,
                                                          # top_logprobs= dd.topk,
                                                          temperature=dd.temperature,
                                                        #   max_tokens=dd.max_tokens,
                                                          )


            dd = res.to_dict()
            dd['prompt'] = prompt
            return dd
        except Exception as e:
            log(traceback.format_exc())
            log(e)


    def get_batch(self, prompts: list, dirout: str = None, output_schema: object = None, max_workers=None):

        """ multiple request
        saves output in a jsonl file
        """

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # If max_workers is None or not given, it will default to the number of processors on the machine,
            # multiplied by 5 assuming it"s being used for IO intensive tasks
            # Start the load operations and mark each future with its prompt
            func_to_be_used = llm_get_sync #if not output_schema else llm_get_with_schema
            future_to_prompt = {
                executor.submit(func_to_be_used, prompt_request=promptRequest(prompt=prompt, service=self.service,
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


    def get_batch_df(self, df, prompt_template: str, prompt_map_dict: dict, dirout: str = None, dirname: str = None,
                     output_schema: object = None, keeponly_msg=1, 
                     npool=1):
        """ Variables in template are consistent with columns in df
            ### prompt:
                Extract people name from text below
                     <prompt_ttile>

                     <prompt_text>
                        
            { "<prompt_text>":  "text_df_column",
              "<prompt_ttile>": "title_df_column",
              
            }
        """

        log('Check:\n', df[ [ x for x in prompt_map_dict.values()] ].shape) 
        def prompt_create(row):
            pp = copy.deepcopy(prompt_template)
            for key_str, coldf_name in prompt_map_dict.items():
                if key_str in prompt_template:
                    pp = pp.replace(key_str, row[coldf_name])
            return pp

        df['llm_prompt'] = df.apply(lambda x: prompt_create(x), axis=1)


        #### Run LLM call #############################################
        t0 = time.time()
        pr = promptRequest(modelid   =  self.modelid,
                           service   =  self.service,
                           json_schema=  output_schema,
                           max_tokens =  self.max_tokens
                           )

        if npool == 1:
            df["llm_json"] = df.apply(lambda x: llm_get_sync(x, prompt_request=pr), axis=1)
        else:
            df = pd_parallel_apply_thread(df, llm_get_sync, n_threads=npool,
                                          colout="llm_json",    prompt_request=pr )


        if output_schema is not None:
            df['llm_msg'] = df['llm_json'].apply(lambda x: llm_cleanup_gpt_jsonformat(x))
        else:
            df['llm_msg'] = df['llm_json'].apply(lambda x: self.get_msg(x))


        log("dt_fetch: ", time.time() - t0 )
        #### Extract
        # log('dt fetch', time.time()-t0 )
        
        if keeponly_msg == 1:
            del df['llm_prompt']
            del df['llm_json']
            cols = [ 'llm_msg' ]
        else:    
            cols = [ 'llm_prompt', 'llm_json', 'llm_msg' ]

        log("Added cols: ", cols)
        if dirout is not None:
            ts = date_now(fmt="%y%m%d_%H%M%S")
            # pd_to_file(df, dirout + f"/df_{ts}.csv")
            pd_to_file(df, dirout + f"/df_{ts}.parquet" )

        return df

    def get_batch_df_block(self, df, prompt_template: str, prompt_map_dict: dict, dirout: str = None, dirname: str = None,
                     output_schema: object = None, keeponly_msg=1, nmax=10000000,
                     kbatch=10,tag="",
                     npool=1):

        df = df.iloc[:nmax]
        mbatch = len(df) // kbatch
        for kk in range(0, mbatch+1):
            dfk = df.iloc[kk*kbatch: (kk+1)*kbatch, : ]
            if len(dfk)< 1: break
            log(kk, dfk.shape)

            df1 = self.get_batch_df(dfk, prompt_template, prompt_map_dict,
                                  dirout=dirout, npool=npool ,
                                  keeponly_msg = keeponly_msg,
                                  output_schema= output_schema ) ### custom parser in LLM class

            y,m,d,h,ts = date_get()
            pd_to_file(df1, dirout + f"/{tag}/df_{ts}_{len(df1)}.parquet")


    def get_msg_df(self, df, coljson='llm_json', colmsg='llm_msg'):
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




#########################################################################
class promptRequest(BaseModel):
    """
    class to store prompt request. To simplify argument passing while parellizing
    """
    prompt: str = ""
    service: str = "openai"
    modelid: str = "gpt-3.5-turbo"
    temperature: float = 0
    max_tokens: int = 1000
    dirout: str = "ztmp/gpt_out"
    json_schema: object = None
    #api_key: str = None
    dirout: str = None
    topk: int = 5
    logprobs: bool = False



def llm_get_sync(row=None, prompt_request: promptRequest = None):
    """
            prompt: str used as prompt when applied on dataframes
            prompt_request: promptRequest

            separate llm call logic. Easy to parellize.
            1. create llm client here
            2. call llm
            example output object:
            {
            "id": "chatcmpl-9k9MR8TtV301n6xAzfbxWM2liX2dV",
            "choices": [
                {
                    "finish_reason": "length",
                    "index": 0,
                    "logprobs": [{"content": {}}],
                    "message": {
                        "content": "Sachin Tendulkar is a former Indian cricketer who is widely regarded as one of the greatest batsmen in the history of the",
                        "role": "assistant"}
                }
            ],
            "created": 1720786099,
            "model": "gpt-3.5-turbo-0125",
            "object": "chat.completion",
            "system_fingerprint": None,
            "usage": {
                "completion_tokens": 30,
                "prompt_tokens": 16,
                "total_tokens": 46,
                "prompt": "Tell me about Sachin Tendulkar"
            }
        }
    """
    try:
        client = llm_get_client(service=prompt_request.service)
        # takes prompt when explicity set. Usually in case of pandas apply
        llm_prompt = row["llm_prompt"] if row is not None else prompt_request.prompt

        if prompt_request.json_schema is not None:
            schema_json = prompt_fun_addprefix_jsonformat(prompt_request.json_schema)
            llm_prompt = f"{llm_prompt}\nRespond with the following JSON schema: \n{schema_json}"

        if 'gpt' in prompt_request.modelid:
            response = client.chat.completions.create(model=prompt_request.modelid,
                                                      messages=[{"role": "user", "content": llm_prompt}],
                                                      #logprobs=prompt_request.logprobs,
                                                      #top_logprobs=prompt_request.topk,
                                                      temperature=prompt_request.temperature,
                                                      max_tokens=prompt_request.max_tokens,
                                                      )
        else:  ### GROQ and other
            response = client.chat.completions.create(model=prompt_request.modelid,
                                                      messages=[{"role": "user", "content": llm_prompt}],
                                                      # logprobs=     dd.logprobs,
                                                      # top_logprobs= dd.topk,
                                                      temperature=prompt_request.temperature,
                                                      #   max_tokens=dd.max_tokens,
                                                      )
        dd = response.to_dict()
        dd['prompt'] = llm_prompt
        log(time.time())
        return dd

    except Exception as e:
        log(traceback.format_exc())
        e1 = str(e).lower()
        log(e1)
        if 'rate' in e1:
            log('Sleeping 120sec')
            time.sleep(120)





############################################################################
######## Enforce JSON Formatting ###########################################
def prompt_fun_addprefix_jsonformat(model: Type[BaseModel]):
    """
    Converts the pydantic schema into a text representation that can be embedded
    into the prompt payload.

    function copied from https://github.com/piercefreeman/gpt-json/blob/2297c5c403511747b906f5af97ee262434016337/gpt_json/prompts.py#L7
    """
    payload = []
    for key, value in model.model_fields.items():
        field_annotation = value.annotation
        annotation_origin = get_origin(field_annotation)
        annotation_arguments = get_args(field_annotation)

        if field_annotation is None:
            continue
        elif annotation_origin in {list, List}:
            if issubclass(annotation_arguments[0], BaseModel):
                payload.append(
                    f'"{key}": {prompt_fun_addprefix_jsonformat(annotation_arguments[0])}[]'
                )
            else:
                payload.append(f'"{key}": {annotation_arguments[0].__name__}[]')
        elif annotation_origin == UnionType:
            payload.append(
                f'"{key}": {" | ".join([arg.__name__.lower() for arg in annotation_arguments])}'
            )
        elif annotation_origin == Literal:
            allowed_values = [f'"{arg}"' for arg in annotation_arguments]
            payload.append(f'"{key}": {" | ".join(allowed_values)}')
        elif issubclass(field_annotation, BaseModel):
            payload.append(f'"{key}": {prompt_fun_addprefix_jsonformat(field_annotation)}')
        else:
            payload.append(f'"{key}": {field_annotation.__name__.lower()}')
        if value.description:
            payload[-1] += f" // {value.description}"
    # All brackets are double defined so they will passthrough a call to `.format()` where we
    # pass custom variables
    return "{{\n" + ",\n".join(payload) + "\n}}"




def llm_cleanup_gpt_jsonformat(msg: str, return_dict=1):
    if not msg.startswith('{'):
        # strip till first open bracket
        msg = msg[msg.index('{'):]

    if not msg.endswith('}'):
        # strip till last close bracket
        msg = msg[:msg.rindex('}') + 1]

    if return_dict == 0 :
        return msg
 
    #### return dict formatted as string
    try:
        dd  = json.loads(msg)
        dd2 = {}
        for key,val in dd.items():
            if isinstance(val, list):
                dd2[key] = [ str(x) for x in val]

            elif isinstance(val, dict):
                dd2[key] = { str(key2): str(val2) for key2,val2 in val.items() }

            else:
                dd2[key] = str(val)
        return dd2
    except Exception as e:
        log(e)
        return None





################################################################################
class MODELS_OPENAI: ### Auto-completion
    gpt35t          = "gpt-3.5-turbo"
    gpt4omini       = "gpt-4o-mini"         #### very slow
    gpt4o           = "gpt-4o"         #### very slow


class MODELS_GROQ: ### Auto-completion
    llama3_70b_8192 = "llama3-70b-8192"
    llama3_8b_8192  = "llama3-8b-8192"
    llama31_8b_instant = 'llama-3.1-8b-instant'
    gemma_7b_it     = 'gemma-7b-it'
    gemma2_9b_it    = 'gemma2-9b-it'
    llama31_70b     = "llama-3.1-70b-versatile"



class MODELS_GEMINI:
    gemini_2_flash=  'gemini-2.0-flash-exp'



################################################################################
GKEYS = [
   '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',
   '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',
   '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',
   "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",
   "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",
   "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"

]
os.environ['GROQ_KEY']= random.choice(GKEYS)


llpairs = [
  # ('groq', MODELALIAS.llama3_8b_8192),
  # ('groq', MODELALIAS.llama_31_8b_instant),  
  # ('groq', MODELALIAS.gemma_7b_it),
  # ('groq', MODELALIAS.gemma2_9b_it),  
  ('openai', MODELS_OPENAI.gpt4omini )

]



###### task ##########################################################
ppair = random.choice(llpairs)

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









########################################################################################
def pd_parallel_apply(df, myfunc, colout="llm_json", npool=4, ptype="process", **kwargs):
    """Apply a function to each row of a DataFrame using multithreading.
            Parameters:
            - df (pandas.DataFrame): The DataFrame on which to apply the function.
            - func (function): The function to apply to each row.
            - colout (str): The name of the column in which to store the results.
            - n_threads (int): Number of threads to use for parallel execution.

            Returns:
            - pandas.DataFrame: DataFrame with the results of the applied function as a new column.
    """
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")

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
         log('Using threads:', npool)
         from concurrent.futures import ThreadPoolExecutor as mp
         with mp(max_workers=npool) as executor:
                # Submit all the tasks to the executor
                futures = [executor.submit(worker, row, **kwargs) for _, row in df.iterrows()]

    # Collect the results as they become available
    for future in futures:
        results.append(future.result())

    df[colout] = results
    return df




def pd_parallel_apply_thread(df, func, colout="llm_json", n_threads=4, **kwargs):
    """
    Apply a function to each row of a DataFrame using multithreading.

    Parameters:
    - df (pandas.DataFrame): The DataFrame on which to apply the function.
    - func (function): The function to apply to each row.
    - colout (str): The name of the column in which to store the results.
    - n_threads (int): Number of threads to use for parallel execution.

    Returns:
    - pandas.DataFrame: DataFrame with the results of the applied function as a new column.
    """
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")

    # Define a wrapper function to handle thread-safe operations
    def worker(row, **kwargs):
        return func(row, **kwargs)

    results = []

    with ThreadPoolExecutor(max_workers=n_threads) as executor:
        # Submit all the tasks to the executor
        futures = [executor.submit(worker, row, **kwargs) for _, row in df.iterrows()]

        # Collect the results as they become available
        for future in futures:
            results.append(future.result())

    df[colout] = results
    return df
















#######################################################################################
### Prompt storage  ###################################################################
def test_prompt_storage():
    #### Using Prompt 
    template = "You are a writer. Reply to the question : <question>"
    # make random dirtmp
    tmp_storage = f"ztmp/prompt_store_{random.randint(100, 999)}.csv"
    prompt_store = PromptStorage(dirstorage=tmp_storage)
    prompt_args = {"args": {
        "<question>": ("str", "this is  document from which you want to generate queries")
    }}
    #
    prompt_store.append(prompt_template=template, model_id="gpt-3.5-turbo",
                          task_name="synthetic_query_generation",
                          prompt_args=prompt_args)
    prompt_store.save()
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
            self.dirstorage = os.environ.get("prompt_storage", "ztmp/prompt_hist.csv")

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
        dfnew["model_id"]        = model_id
        dfnew["prompt_args"]     = prompt_args
        dfnew["dt"]              = date_now(fmt="%Y-%m-%d %H:%M:%S")

        if isinstance(prompt_examples, list):
            prompt_examples = self.sep_prompt.join(prompt_examples)

        dfnew["prompt_examples"] = prompt_examples
        dfnew["task_name"]       = task_name
        dfnew["info_json"]       = info_json
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













##########################################################################################
if __name__ == '__main__':
    fire.Fire()










