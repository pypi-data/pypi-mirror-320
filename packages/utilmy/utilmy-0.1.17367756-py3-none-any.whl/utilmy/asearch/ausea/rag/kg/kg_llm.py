"""" LLM triplet extractor
        pip install fire utilmy
        git clone
        cd myutil 

        pip install -e .
        export PYTHONPATH+"$(pwd)"    ###needed

        #### ztmp/data is in gitignore, you can put your data there
        mkdir -p ztmp/data


    python rag/kg_llm.py    run_extract_kg --dirin ztmp/data/input/news.parquet    --dirout ztmp/out/mykg.parquet

"""
import os

from pydantic import BaseModel
from typing import List, Dict, Union, Tuple
from abc import ABC, abstractmethod
import json, re, ast, pandas as pd, hashlib
from rich import print as rprint
from box import Box

from utilmy import log, pd_read_file, pd_to_file

#### cd myutil     pip install -e .
from rag.llm import LLM,MODELS_GROQ, MODELS_OPENAI




################################################################################################################
def run_extract_kg(cfg=None, cfg_name="test1", dirin="./ztmp/news.parquet", dirout= "ztmp/data/out/", nmax=4, npool=1, keeponly_msg=0,
                   llm_service='groq', llm_model='gemma9b', llm_key=None, entities=None ):
    """ LLM Extractor
    
        python rag/kg_llm.py run_extract_kg   --dirin  "./ztmp/data/news.parquet"
        print( os.environ['GROQ_KEY'] )  # by LLM class



    """
    log("##### Load config #######################################################")
    from utilmy import config_load
    cfg0 = config_load(cfg)
    cfgd = cfg0.get(cfg_name, {})



    log("##### Params ##########################################################")
    cc = Box({})

    entities = cfgd.get('entities', ["COMPANY", "PERSON", "PRODUCT", "EVENT", "JOB_TITLE"] ) if entities is None else entities
    # edges    = cfgd.get('edges',    ["PARTNER","ACQUIRE","INVEST","PRODUCE","ORGANIZE","FUND","HAS_JOB_TITLE","WORK_FOR"] ) if edges is None else edges

    cc.max_triplets           = cfg.get('max_triplets', 10)
    cc.allowed_entity_types   = entities
    cc.allowed_relation_types = None
    cc.facts_count            = cfg.get('facts_counts', 15)

    cc.llm_service = cfg.get('llm_service', ) if llm_service is None else llm_service
    cc.llm_model   = cfg.get('llm_model', )   if llm_model is None else llm_model


    log("##### Load data #######################################################")
    df = pd_read_file(dirin)
    df = df.iloc[:nmax, :]
    log( df[["title", "text"]] )


    log("##### LLM init  #######################################################")
    llm = LLM(service = cc.llm_service ,
              api_key = llm_key , ### print( os.environ['GROQ_KEY'] )
              model   = cc.llm_model ) # "llama-3.1-70b-versatile" )


    log("##### LLM Extract Fact ###############################################")
    ### pseudo function coded as english language
    PROMPT_FACTS = """
        You are a knowldge graph worker your goal is to read the text, understand its main takeaways and synthesise {facts_count} important short factual tasks from the text.
        The facts must be short (up to 20clean words)   
        dont include Facts that are vague or could not relate to real actors or objects (mentioned in the text)   
        Respond ONLY with the facts extrcated           
        ```
            <prompt_text>
        ```
        {facts_count} FACTS:

    """

    ### Static
    PROMPT_FACTS = PROMPT_FACTS.format( facts_count= cc.facts_count )

    ### map <. Placeholder  >. with dataframe column "text'"
    prompt_map_dict = {"<prompt_text>": "text"}

    df = llm.get_batch_df(df, PROMPT_FACTS, prompt_map_dict, dirout=None, npool=npool ,keeponly_msg = keeponly_msg )

    ### Rename columns
    cols_llm = [ 'llm_prompt', 'llm_json', 'llm_msg' ] 
    df       = pd_col_rename(df, cols_llm, suffix="_facts", prefix=None)


    log("##### LLM Extract Triplet ########################################")
    prompt_triplet= """
            Extract up to <max_triplets> knowledge triplets from the given text. 
            Each triplet should be in the form of (head, relation, tail) with their respective types.
            ---------------------
            ALLOWED entity types:
            Entity Types: <allowed_entity_types>


            ONLY extract triplets with this entitiy types.

            GUIDELINES:
            - Output in JSON format: [{{'head': '', 'head_type': '', 'relation': '', 'tail': '', 'tail_type': ''}}]
            - Use the most complete form for entities (e.g., 'United States of America' instead of 'USA')
            - Keep entities concise (3-5 words max)
            - ONLY entities with (3-5 words max) are valid
            - Break down complex phrases into multiple triplets
            - if you find a triplet make sure the types are correct if not ommit the triplet
            - Ensure the knowledge graph is coherent and easily understandable
            - Ensure that entities are real things not ABSTRCATIONS
            Do not add any other comment before or after the json. Respond ONLY with a well formed json that can be directly read by a program.

            TEXT : 
            <prompt_text>
            RESPONSE : 
    """

    #### Static:
    prompt_triplet = prompt_triplet.replace("<max_triplets>",        str(cc.max_triplets))
    prompt_triplet = prompt_triplet.replace("<allowed_entity_types>",str(cc.allowed_entity_types))
    
    #### Dynamic:  map <. Placeholder  >. with dataframe column "text'"
    prompt_map_dict = {"<prompt_text>": "llm_msg_facts"}

    df = llm.get_batch_df(df, prompt_triplet, 
                          prompt_map_dict, dirout=None, npool=npool ,keeponly_msg = keeponly_msg )

    ###### Normalized columns
    cols_llm = [ 'llm_prompt', 'llm_json', 'llm_msg' ] 
    df       = pd_col_rename(df, cols_llm, suffix="_triplets", prefix=None)


    log("########## parse triplet json  #######################################")
    df["llm_msg_triplets_json"] =  df["llm_msg_triplets"].apply(parse_triplets)

    log(df[["llm_msg_triplets","llm_msg_facts","llm_msg_triplets_json"]])

    if isinstance(dirout, str):
       from utilmy import date_now 
       ts = date_now(fmt="%y%m%d_%H%M%S") 
       pd_to_file(df, dirout + f"/df_triplet_extract_{ts}_{len(df)}.parquet")

    return df





################################################################################################################
def run_extract_kg_with_edge(cfg= "rag/kg/cfg_kg_llm.yaml", cfg_name='test1', entities = None, edges = None,
        dirin="./ztmp/news.parquet", dirout= "ztmp/data/out/", nmax=4, npool=1, keeponly_msg=0,
        llm_service = "groq",llm_model="gemma-7b-it"):
    """ LLM Extractor

        export cfg=""rag/kg/cfg_kg_llm.yaml"
        python rag/kg_llm.py run_extract_kg_with_edge --cfg $cfg --cfg_name test25   --dirin  "./ztmp/data/news.parquet"
        print( os.environ['GROQ_KEY'] )  # by LLM class



    """
    log("##### Load config ###################################################")
    from utilmy import config_load
    cfg0 = config_load(cfg)
    cfgd = cfg0.get(cfg_name, {})
    log(cfgd)




    log("##### Params #######################################################")
    cc = Box({})

    entities = cfgd.get('entities', ["COMPANY", "PERSON", "PRODUCT", "EVENT", "JOB_TITLE"] ) if entities is None else entities
    edges    = cfgd.get('edges',    ["PARTNER","ACQUIRE","INVEST","PRODUCE","ORGANIZE","FUND","HAS_JOB_TITLE","WORK_FOR"] ) if edges is None else edges

    cc.allowed_entity_types   = entities
    cc.allowed_relation_types = edges
    cc.max_triplets           = cfgd.get('max_triplets', 10)
    cc.facts_count            = cfgd.get('facts_counts', 15)


    log("##### Load data #######################################################")
    df = pd_read_file(dirin)
    df = df.iloc[:nmax, :]
    log( df[["title", "text"]] )



    log("##### LLM Load #######################################################")
    llm = LLM(service = llm_service,
              api_key = None, ### print( os.environ['GROQ_KEY'] ) No needee
              model   = llm_model) # "llama-3.1-70b-versatile" )



    log("##### LLM Extract Fact ############################################")
    PROMPT_FACTS = """
        You are a knowldge graph worker your goal is to read the text, understand its main takeaways 
        and synthesize up to {facts_count} important short factual tasks from the text.
        The facts must be short (up to 20 clean words)   
        dont include Facts that are vague or could not relate to real actors or objects (mentioned in the text)   
        Respond ONLY with the facts extrcated           
        ```
            <prompt_text>
        ```
        FACTS:

    """

    ### Static
    PROMPT_FACTS = PROMPT_FACTS.format( facts_count= cc.facts_count )

    ### map <. Placeholder  >. with dataframe column "text'"
    prompt_map_dict = {"<prompt_text>": "text"}
    df = llm.get_batch_df(df, PROMPT_FACTS, prompt_map_dict, dirout=None, npool=npool ,keeponly_msg = keeponly_msg )

    ### Rename columns
    cols_llm = [ 'llm_prompt', 'llm_json', 'llm_msg' ] 
    df       = pd_col_rename(df, cols_llm, suffix="_facts", prefix=None)


    log("##### LLM Extract Triplet ########################################")
    ## prompt == pseudo function in english words < hardcoded function

    prompt_triplet= """
            Extract up to <max_triplets> knowledge triplets from the given text. 
            Each triplet should be in the form of (head, relation, tail) with their respective types.
            ---------------------
            ALLOWED entity types:
            Entity Types: <allowed_entity_types>
            ALLOWED relation types:
            Relations Types: <allowed_relation_types>

            ONLY extract triplets with this entitiy and relations types.

            GUIDELINES:
            - Output in JSON format: [{{'head': '', 'head_type': '', 'relation': '', 'tail': '', 'tail_type': ''}}]
            - Use the most complete form for entities (e.g., 'United States of America' instead of 'USA')
            - Keep entities concise (3-5 words max)
            - ONLY entities with (3-5 words max) are valid
            - Break down complex phrases into multiple triplets
            - if you find a triplet make sure the types are correct if not ommit the triplet
            - Ensure the knowledge graph is coherent and easily understandable
            - Ensure that entities are real things not ABSTRCATIONS
            Do not add any other comment before or after the json. Respond ONLY with a well formed json that can be directly read by a program.

            TEXT : 
            <prompt_text>
            RESPONSE : 
    """

    #### Static:
    prompt_triplet = prompt_triplet.replace("<max_triplets>",        str(cc.max_triplets))
    prompt_triplet = prompt_triplet.replace("<allowed_entity_types>",str(cc.allowed_entity_types))
    prompt_triplet = prompt_triplet.replace("<allowed_relation_types>",str(cc.allowed_relation_types))
    
    #### Dynamic:  map <. Placeholder  >. with dataframe column "text'"
    prompt_map_dict = {"<prompt_text>": "llm_msg_facts"}

    df = llm.get_batch_df(df, prompt_triplet, 
                          prompt_map_dict, dirout=None, npool=npool ,keeponly_msg = keeponly_msg )
    log(df.columns)

    ###### Normalized columns
    cols_llm = [ 'llm_prompt', 'llm_json', 'llm_msg' ] 
    df       = pd_col_rename(df, cols_llm, suffix="_triplets", prefix=None)


    log("########## parse triplet json  ################")
    df["llm_msg_triplets_json"]      = df["llm_msg_triplets"].apply(parse_triplets)
    df["llm_msg_triplets_json_norm"] = df["llm_msg_triplets"].apply(lambda triplet: parse_triplets_normalized(triplet,edges))
    log(df[["llm_msg_triplets","llm_msg_facts","llm_msg_triplets_json","llm_msg_triplets_json_norm"]])
    # log(df[["llm_msg_triplets_normalized_json"]].values)


    if isinstance(dirout, str):
       from utilmy import date_now 
       ts = date_now(fmt="%y%m%d_%H%M%S") 
       pd_to_file(df, dirout + f"/df_triplet_extract_{ts}_{len(df)}.parquet")

    return df
















####################################################################################
def llm_create_new_relation(cfg=None, cfg_name='test1', rel_str='buy',  dirout=None):
    """ Experiments: different prompts or tricks.


       python rag/kg/kg_llm.py llm_create_new_relation --cfg "rag/kg/cfg_llm.yaml"



    """

    log("##### LLM init  #######################################################")
    llm = LLM(cfg=cfg, cfg_name= cfg_name)


    PROMPT_ENRICH_RELATION = """
     Your goal is to enrich the graph schema.
     You are given a relation name and need to output a list of synonmyms, inverson of the given relation.
     You must output the list in this format : ["rel_1","rel_2","rel_3", ...] with no additional text !
     Relation: {rel_str}
     OUTPUT:   
    """

    rel_enrichements = llm.generate("You are a knowldge graph worker",
                                    PROMPT_ENRICH_RELATION.format(rel_str=rel_str))

    # print(" rel enrich : ", rel_str,rel_enrichements)
    try:
        rels  = [rel_str] + ast.literal_eval(rel_enrichements)
    except:
        rels =  [rel_str]

    dd = { rel_str: rels }


    if dirout is not None:
        from utilmy import json_save, json_load, date_now
        ts = date_now("%Y%m%d-%H%M%d")
        json_save(dd, dirout + f"/new_kg_relation_{ts}.json")


    return dd






############################################################################################
####### Previous version ###################################################################
def run_extract_kg_v1(dirin="./ztmp/news.parquet",dirout= "ztmp/data/input/news_enriched.parquet", nmax=10):
    """
    
        python src/rag/kg_llm.py run_extract_kg    

        python src/rag/kg_llm.py run_extract_kg   --dirin  "./ztmp/data/news.parquet"

    """
    llm = LLM(service="groq",api_key = None , model = "mixtral-8x7b-32768")
    allowed_entity_types = ["COMPANY", "PERSON", "PRODUCT", "EVENT", "JOB_TITLE"]
    triplet_extractor = TripletExtractor(allowed_entity_types,llm)
    df = pd_read_file(dirin)

    df = df.iloc[:nmax,:]
    log(df, df.columns)

    # load texts as list (to controle rate limit) 
    # uing a simple loop (3-4s per request) 
    df_out = triplet_extractor.from_df(df,"text",rows_limit = 2)
    print(df_out.shape)
    print(df_out.head())
    return df_out 






#############################################################################################################
def llm_finetune(dirin="mydata.json"):
    import openai

    openai.api_key = os.environ["OPEN_KEY"]

    # Prepare training data
    training_data = [
        {"prompt": "Input text", "completion": "Output text"},
        # Add more examples
    ]

    from utilmy import json_save, json_load

    training_data = json_load(dirin)


    # Fine-tune the model
    response = openai.FineTune.create(
        model="gpt-4-mini",
        training_file=openai.File.create(
            file=open("training_data.jsonl", "rb"),
            purpose='fine-tune'
        ).id
    )



    # Use the fine-tuned model
    completion = openai.Completion.create(
        model=response.fine_tuned_model,
        prompt="Your prompt here"
    )
    print(completion.choices[0].text)




#############################################################################################################
class Edge(BaseModel):
    head: str
    head_type: str
    relation: str
    tail: str
    tail_type: str


class TripletExtractor:

    def __init__(
        self,
        allowed_entity_types: List[str],
        llm_client: LLM,
    ):
        self.allowed_entity_types = allowed_entity_types
        self._llm_client = llm_client
        self._max_knowledge_triplets = 50
        self._task_count = 10

    def user_message(self, text: str) -> str:
        return f"input text: ```\n{text}\n```"

    # def system_message(self) -> str:
    #     return (
    #         "You are an expert at creating Knowledge Graphs. "
    #         "Consider the following ontology. \n"
    #         f"{self._ontology} \n"
    #         "The user will provide you with an input text delimited by ```. "
    #         "Extract all the entities and relationships from the user-provided text as per the given ontology. Do not use any previous knowledge about the context."
    #         "Remember there can be multiple direct (explicit) or implied relationships between the same pair of nodes. "
    #         "Be consistent with the given ontology. Use ONLY the labels and relationships mentioned in the ontology. "
    #         "Format your output as a json with the following schema. \n"
    #         "[\n"
    #         "   {\n"
    #         '       node_1: Required, an entity object with attributes: {"label": "as per the ontology", "name": "Name of the entity"},\n'
    #         '       node_2: Required, an entity object with attributes: {"label": "as per the ontology", "name": "Name of the entity"},\n'
    #         "       relationship: Describe the relationship between node_1 and node_2 as per the context, in a few sentences.\n"
    #         "   },\n"
    #         "]\n"
    #         "Do not add any other comment before or after the json. Respond ONLY with a well formed json that can be directly read by a program."
    #     )
    def triplets_system_message(self) -> str:
        return (
            f"Extract up to {self._max_knowledge_triplets} knowledge triplets from the given text. "
            "Each triplet should be in the form of (head, relation, tail) with their respective types.\n"
            "---------------------\n"
            "ALLOWED entity types:\n"
            f"Entity Types: {self.allowed_entity_types}\n"
            # "Relation Types: {allowed_relation_types}\n"
            "\n"
            "ONLY extract triplets with this entitiy types.\n"
            "\n"
            "GUIDELINES:\n"
            "- Output in JSON format: [{{'head': '', 'head_type': '', 'relation': '', 'tail': '', 'tail_type': ''}}]\n"
            "- Use the most complete form for entities (e.g., 'United States of America' instead of 'USA')\n"
            "- Keep entities concise (3-5 words max)\n"
            "- ONLY entities with (3-5 words max) are valid\n"
            "- Break down complex phrases into multiple triplets\n"
            # "- if you find a triplet make sure the types are correct if not ommit the triplet\n"
            "- Ensure the knowledge graph is coherent and easily understandable\n"
            "- Ensure that entities are real things not ABSTRCATIONS\n"
            # "---------------------\n"
            # "EXAMPLE:\n"
            # "Text: Tim Cook, CEO of Apple Inc., announced the new Apple Watch that monitors heart health. "
            # "UC Berkeley researchers studied the benefits of apples.\n"
            # "Output:\n"
            # "[\n"
            # "   {\n"
            # '       head: Required, an entity object with attributes: {"label": "as per the ontology", "name": "Name of the entity"},\n'
            # '       node_2: Required, an entity object with attributes: {"label": "as per the ontology", "name": "Name of the entity"},\n'
            # "       relationship: Describe the relationship between node_1 and node_2 as per the context, in a few sentences.\n"
            # "   },\n"
            # "]\n"
            # "---------------------\n"
            # "Text: {text}\n"
            # "Output:\n"
            "Do not add any other comment before or after the json. Respond ONLY with a well formed json that can be directly read by a program."

        )

    def facts_system_message(self) -> str:

        return (
            f"You are a knowldge graph worker your goal is to read the text, understand its main takeaways and synthesise up to {self._task_count} important  short factual tasks from the text"
            "The facts must be short (up to 9-10 words)"
            "dont include Facts that are vague or could not relate to real actors or objects (mentioned in the text)"
            "Respond ONLY with the facts extrcated"

        )

    def generate(self, text: str) -> str:
        # rprint(self.facts_system_message())
        facts_text = self._llm_client.generate(user_message=self.user_message(text),
                                               system_message=self.facts_system_message())
        # rprint(facts_text)
        response = self._llm_client.generate(
            user_message=self.user_message(facts_text),
            system_message=self.triplets_system_message(),
        )
        return {"triplets_raw":response,
                "facts_raw":facts_text}

    def parse_json(self, text: str):
        try:
            parsed_json = json.loads(text)
            return parsed_json
        except json.JSONDecodeError as e:
            # rprint(f"JSON Parsing failed with error: { e.msg}")
            # rprint(f"FAULTY JSON: {text}")
            return None

    def manually_parse_json(self, text: str):
        pattern = r"\}\s*,\s*\{"
        stripped_text = text.strip("\n[{]}` ")
        splits = re.split(pattern, stripped_text,
                          flags=re.MULTILINE | re.DOTALL)
        obj_string_list = list(map(lambda x: "{" + x + "}", splits))
        edge_list = []
        for string in obj_string_list:
            try:
                edge = json.loads(ast.literal_eval(json.dumps(string)))
                edge_list.append(edge)
            except json.JSONDecodeError as e:
                # rprint(
                #     f"Failed to Parse the Edge: {string}\n{e.msg}")
                # rprint(f"FAULTY EDGE: {string}")
                continue
        return edge_list

    def json_to_edge(self, edge_dict):
        try:
            edge = Edge(**edge_dict)
        except:
            edge = None
        finally:
            return edge

    def from_text(self, text):
        llm_resp = self.generate(text)
        response = llm_resp["triplets_raw"].replace("'", '"')
        if False:
            rprint(f"LLM Response:\n{response}")

        json_data = self.parse_json(response)
        if not json_data:
            json_data = self.manually_parse_json(response)
        # print("json data ", json_data)
        edges = [self.json_to_edge(edg) for edg in json_data]
        edges = list(filter(None, edges))

        return {
            "triplets":edges,
            "triplets_llm_raw":response,
            "facts_llm_raw": llm_resp["facts_raw"]
        }
    def from_df(self,df,column ="text", rows_limit = 5):
        failed_texts = []
        triplets_formated = []
        for text_idx,text in enumerate(df[column].values[:rows_limit]):
            try : 
                # text hash (as text_id)
                text_id = hashlib.sha256(text.encode("utf-8")).hexdigest()
                ans = self.from_text(text)
                # extract llm outs (for debug purpose)
                facts_raw = ans["facts_llm_raw"]
                triplets_raw = ans["triplets_llm_raw"]
                
                # extract triplets 
                triplets = ans["triplets"]
                triplets_f = [
                    (edge.head,edge.head_type,edge.tail,edge.tail_type,edge.relation)
                    for edge in triplets
                ]
                triplets_formated.append({
                    "text_id":text_id,
                    "triplets_formated" : triplets_f,
                    "triplets_llm_raw":triplets_raw,
                    "facts_llm_raw":facts_raw
                })
                print(f"text_id = ({text_idx}) / triplets extrcated = ({len(triplets)})")
            except Exception as e : 
                print(e)
                failed_texts.append(text_idx)
        # to pandas
        df_out = pd.DataFrame(triplets_formated)
        return df_out




#############################################################################################################
def pd_col_rename(df, cols, suffix=None, prefix=None):

    suffix = "" if suffix is None else suffix 
    prefix = "" if prefix is None else prefix
    # cols_llm = [ 'llm_prompt', 'llm_json', 'llm_msg' ] 
    for ci in cols :
        if ci not in df.columns : continue
        cinew = f"{prefix}{ci}{suffix}"
        df[cinew ] = df[ci]
        log(ci, cinew)
        del df[ci]
    return df 

def parse_json(text: str):
    try:
        parsed_json = json.loads(text)
        return parsed_json
    except json.JSONDecodeError as e:
        # rprint(f"JSON Parsing failed with error: { e.msg}")
        # rprint(f"FAULTY JSON: {text}")
        return None


def manually_parse_json(text: str):
    pattern = r"\}\s*,\s*\{"
    stripped_text = text.strip("\n[{]}` ")
    splits = re.split(pattern, stripped_text,
                        flags=re.MULTILINE | re.DOTALL)
    obj_string_list = list(map(lambda x: "{" + x + "}", splits))
    edge_list = []
    for string in obj_string_list:
        try:
            edge = json.loads(ast.literal_eval(json.dumps(string)))
            edge_list.append(edge)
        except json.JSONDecodeError as e:
            # rprint(
            #     f"Failed to Parse the Edge: {string}\n{e.msg}")
            # rprint(f"FAULTY EDGE: {string}")
            continue
    return edge_list


def json_to_edge(edge_dict):
    try:
        edge = Edge(**edge_dict)
    except:
        edge = None
    finally:
        return edge


def parse_triplets(triplets_str):
        response = triplets_str.replace("'", '"')
        try : 
            json_data = parse_json(response)
            if not json_data:
                json_data = manually_parse_json(response)
            # print("json data ", json_data)
            edges = [json_to_edge(edg) for edg in json_data]
            edges = list(filter(None, edges))

            return [
                (edge.head,edge.head_type,edge.tail,edge.tail_type,edge.relation)
                for edge in edges
            ]
        except : 
            return []

def parse_triplets_normalized(triplets_str,rel_mapper):
        response = triplets_str.replace("'", '"')
        try : 
            json_data = parse_json(response)
            if not json_data:
                json_data = manually_parse_json(response)
            # print("json data ", json_data)
            edges = [json_to_edge(edg) for edg in json_data]
            edges = list(filter(None, edges))

            return [
                (edge.head,edge.head_type,edge.tail,edge.tail_type,rel_mapper.get(edge.relation,None))
                for edge in edges
            ]
        except : 
            return []


def run_banchmark():
    # run benchmark 
    for model_key in ["llama3-70b-8192","llama-guard-3-8b","mixtral-8x7b-32768","gemma-7b-it","gemma2-9b-it"]:
        model_sig = {
            "service":"groq",
            "model_key":model_key
        }
        print("--------------",model_key,"--------------------")
        run_extract_kg(dirin="/workspaces/myutil/zmtp/data/df_news_100.parquet", 
                       dirout= f"/workspaces/myutil/zmtp/data/df_news_100_enriched_model_groq_{model_key}.parquet", 
                       nmax=40, npool=1, keeponly_msg=0,
                       default_model = model_sig)
def run_clean_benchmark(df_paths,path_out:str):
    # concat benchmarks 
    dfs = []
    for i, path in enumerate(df_paths):
        df = pd.read_parquet(path)
        # Select the desired columns
        df = df[["url", "llm_msg_triplets_json"]]
        new_col_name = path.split("/")[-1].replace(".parquet", "")
        df = df.rename(columns={"llm_msg_triplets_json": new_col_name})
        dfs.append(df)

    df_final = reduce(lambda x, y: pd.merge(x, y, on='url'), dfs)

    # format triplets
    trip_cols = [col for col in df_final.columns if "triplet" in col]


    def format_triplets(triplets):
        trpls_str = ""

        for triplet in triplets:
            trpls_str += f"{triplet[1]}:{triplet[0]};{triplet[3]}:{triplet[2]};REL:{triplet[4]}*"
        return trpls_str
    def count_triplets(triplets):
        return len(triplets)

    for col in trip_cols : 
        df_final[f"{col}_formated"] = df_final[col].apply(
            lambda x: format_triplets(x))  
        df_final[f"{col}_count"] = df_final[col].apply(
            lambda x: count_triplets(x))  
    for col in trip_cols:
        del df_final[col]
    # save
    df_final.to_csv(path_out, index=False)



##################################################################################
if __name__ == "__main__":
    import fire 
    fire.Fire()
    # import time
    # start = time.time()
    # os.environ["LLM_ROTATE_KEY"] = "0"
    # os.environ['GROQ_KEY'] = "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"
    # run_extract_kg_controlled(dirin ="/workspaces/myutil/utilmy/asearch/ztmp/news.parquet",dirout="/workspaces/myutil/utilmy/asearch/ztmp/news_enriched.parquet",nmax=20, npool=1)
    # print("time elapsed = ", round(time.time()-start,3) , "s")














# ###################################################################################################
# if __name__ == "__main__":
#     import fire
#     fire.Fire()

