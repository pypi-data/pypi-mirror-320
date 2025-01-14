""" Re-usable helper functions to simplify training with HF library

     pip install utilmy fire python-box

 


"""
if "import":
    import os, sys, json, pandas as pd,numpy as np, gc, time, copy, random
    from copy import deepcopy
    from typing import Any, Callable, Dict, List, Optional, Sequence, Union
    from functools import partial
    from collections import Counter
    from dataclasses import dataclass
    from box import (Box, BoxList,  )
    from tqdm import tqdm


    from datasets import load_dataset, DatasetDict, Dataset

    from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support


    from transformers import (AutoTokenizer, AutoModelForSequenceClassification,    
       TrainingArguments, Trainer, pipeline, DataCollatorWithPadding,
       BertModel, EarlyStoppingCallback, PreTrainedTokenizerBase,  TrainerCallback
    )
    from transformers.utils import PaddingStrategy

    # from sentence_transformers import SentenceTransformer
    import torch, evaluate
    import torch.nn as nn

    from utilmy import (pd_read_file, os_makedirs, pd_to_file, date_now, glob_glob, config_load,
                       json_save, json_load, log, log2, loge, diskcache_decorator )


    import warnings
    warnings.filterwarnings("ignore")
    import os, pathlib, uuid, time, traceback, copy, json


    import pandas as pd, numpy as np, torch
    import mmh3, xxhash

    from datasets import Dataset, DatasetDict, load_dataset

    from utilmy import (pd_read_file, os_makedirs, pd_to_file, date_now, glob_glob,
           json_load, json_save)
    from utilmy import log, log2



###########################################################################################
def test_setup(epoch):
    # Load model and tokenizer
    model = AutoModelForSequenceClassification.from_pretrained("microsoft/deberta-v3-small", num_labels=2)
    tokenizer = AutoTokenizer.from_pretrained("microsoft/deberta-v3-small")

    # Load and preprocess dataset
    dataset = load_dataset("imdb")
    dataset["train"] = dataset["train"].select(range(20))
    dataset["test"] = dataset["test"].select(range(20))
    del dataset["unsupervised"]

    def tokenize_function(examples):
        return tokenizer(examples["text"], padding="max_length", truncation=True)
    tokenized_datasets = dataset.map(tokenize_function, batched=True)

    # Define metrics function
    def compute_metrics(pred):
        labels = pred.label_ids
        preds = pred.predictions.argmax(-1)
        precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='binary')
        acc = accuracy_score(labels, preds)
        return {"accuracy": acc, "f1": f1, "precision": precision, "recall": recall}

    # Define callback
    class PrintCallback:
        def on_log(self, args, state, control, logs=None, **kwargs):
            print(f"Step: {state.global_step}, Loss: {logs['loss']:.4f}")

    # Set up training arguments
    training_args = TrainingArguments(
        output_dir="./ztmp/results",
        num_train_epochs=epoch,
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=10,
    )

    return model, training_args, tokenized_datasets, compute_metrics, PrintCallback





#####################################################################################################
################# Shorcurts #########################################################################
@dataclass
class HFtask:  ##auto completion
    text_classification     : str = "text-classification"
    token_classification    : str = "token-classification"
    question_answering      : str = "question-answering"
    summarization           : str = "summarization"
    translation             : str = "translation"
    text_generation         : str = "text-generation"
    fill_mask               : str = "fill-mask"
    zero_shot_classification: str = "zero-shot-classification"
    sentence_similarity     : str = "sentence-similarity"
    feature_extraction      : str = "feature-extraction"
    text2text_generation    : str = "text2text-generation"
    conversational          : str = "conversational"
    table_question_answering: str = "table-question-answering"


@dataclass
class HFproblemtype:
    CAUSAL_LM                  : str = "causal_lm"
    MASKED_LM                  : str = "masked_lm"
    SEQ_2_SEQ_LM               : str = "seq2seq_lm"
    SEQUENCE_CLASSIFICATION    : str = "sequence_classification"
    QUESTION_ANSWERING         : str = "question_answering"
    TOKEN_CLASSIFICATION       : str = "token_classification"
    MULTIPLE_CHOICE            : str = "multiple_choice"
    SEMANTIC_SEGMENTATION      : str = "semantic_segmentation"
    MULTI_LABEL_CLASSIFICATION : str = "multi_label_classification"
    MASK_GENERATION            : str = "mask_generation"
    SINGLE_LABEL_CLASSIFICATION: str = "single_label_classification"



###################################################################################################
######## Init ######################################################################################
def torch_device(device=None) :
    """ ENV variable set
    """
    import torch
    if device is None or len(str(device)) == 0:
        device= os.environ.get("torch_device", "cpu")
        
    log('cuda available:', torch.cuda.is_available()  )    
    log('mps available:',  torch.backends.mps.is_available()  )        
    log("set torch_device=", device)
    return device


def torch_init():
    ### Reset cache
    try:
        ### Macos
        print( torch.mps.current_allocated_memory() )
        torch.mps.empty_cache()
    except Exception as e :
       log(e)    

    try:
        #### Most effectit to clean cuda cache 
        from numba import cuda
        device = cuda.get_current_device()
        device.reset()
    except Exception as e :
       log(e)    


def accelerator_init(device="cpu", model=None):
    from accelerate import Accelerator
    try: 
       accelerator = Accelerator(cpu=True if device == "cpu" else False)
       return accelerator
    except Exception as e:
       log(e) 


################################
####################################################################
############ Config helper ########################################################################

def cc_to_dict(cc):
    """ Convert nested cc to dict
    """
    if hasattr(cc, "to_dict") and callable(cc.to_dict):
        cc = cc.to_dict()
    for key in cc: # Nested values can be TrainingArguments objects so we need to convert them to dict
        if hasattr(cc[key], "to_dict") and callable(cc[key].to_dict):
            cc[key] = cc_to_dict(cc[key])
    return cc




####################################################################################################
############ Dataset helper ########################################################################
def test1():
    """
    Tests the `dataset_reduce` function
    """
    # DatasetDict
    dataset = load_dataset("imdb")
    reduced_dataset = dataset_reduce(dataset, ntrain=23, ntest=11)
    assert len(reduced_dataset['train']) == 23
    assert len(reduced_dataset['test']) == 11
    # Dataset
    reduced_dataset = dataset_reduce(dataset['train'], ntrain=17)
    assert len(reduced_dataset) == 17


def dataset_reduce(dataset, ntrain: int = 10, ntest: int = 5) :
    ### Reduce dataset size 
    if isinstance(dataset, DatasetDict):
        ntrain = min(len(dataset['train']), ntrain)
        ntest  = min(len(dataset['test']), ntest)

        return DatasetDict({
            'train':  dataset['train'].select(range(ntrain)),
            'test':   dataset['test'].select(range(ntest))
        })
    else:
        ntrain = min(len(dataset), ntrain)
        return dataset.select(range(ntrain))



def dataset_remove_columns(ds, cols):

    def ds_del(ds, cols1):
        cols2 = []
        for ci in cols1:
            if ci in ds:
                cols2.append(ci)

        ds = ds.remove_columns(cols2)
        return ds

    if isinstance(ds, DatasetDict):
        dsdict2 = DatasetDict({})
        for key in ds.keys():
            dsdict2[key] =    ds_del(ds[key], cols)
        return dsdict2

    else:
        return ds_del(ds, cols)


def test23(name="Small size data HF name "):
    """test function

    python util_hf.py  test1 --name "Small size data"


    """
    dirtmp = "./ztmp/tests/"

    ds = datasets.load_dataset(name)
    ds_to_file(ds, dirout=dirtmp, )
    for split in ["train", "test"]:
        assert os.path.exists(f"{dirtmp}/{name}_{split}.parquet")

    ### Simple tests


#######################################################################################
def ds_to_file(ds: DatasetDict, dirout: str, fmt="parquet", show: int = 0) -> None:
    """Writes  datasets to files in  specified directory after creating subdirectories for each key in  dataset.

    Args:
        ds (dict): A dictionary containing  dataset.
        dirout (str):  output directory path.
        show (int): Flag to indicate whe r to show additional information. Defaults to 0.

    Returns:
        None
    """
    for key in ds.keys():  ### "train", "test"
        dirout1 = f"{dirout}/{key}/"
        os_makedirs(dirout1)
        log(dirout1)
        ### Meta Data in JSON
        ds[key].info.write_to_directory(f"{dirout1}/", )

        if fmt == "parquet":
            ds[key].to_parquet(f"{dirout1}/df.{fmt}", )


def ds_read_file(dirin: str, fmt="parquet") -> DatasetDict:
    """Reads files from a specified directory,returns a DatasetDict.
    dsdict = ds_read_file(dirout +"/ztest")

    Args:
        dirin (str):  input directory path.
        format (str):  file format to read. Defaults to "parquet".

    Returns:
        DatasetDict: A dictionary containing datasets processed from  input files.
    """

    dirin = dirin[:-1] if dirin[-1] == "/" else dirin
    dirin = dirin.replace("//", "/") if ":" not in dirin else dirin

    dsdict = DatasetDict()

    from utilmy import glob_glob
    fpaths = glob_glob(f"{dirin}/*")

    for fp in fpaths:
        key = fp.split("/")[-1]
        if "." in key: continue  #### Path of a file

        flist = glob_glob(fp + f"/*.{fmt}")
        if flist is None or len(flist) < 1:
            continue
        log(flist[-1], len(flist))
        dsdict[key] = Dataset.from_parquet(flist)

    return dsdict



#######################################################################################
def dataset_direct_to_disk(name="ag_news", subset=None, dirout="./ztmp/hf_online/", splits=None,
                  cols_mapping=None, fmt="csv", ds_type="raw", show=1):
    """ Save a Hugging Face dataset to disk (Parquet format by default).
        # hf_ds_to_disk('tner/fin', subset=None, dirout='../data_temp', show=1)
        # hf_ds_to_disk('imvladikon/english_news_weak_ner', 'articles', '../data_temp', fmt='parquet', show=1)


    Args:
        name (str): Name of dataset.
        subset (str): Subset of dataset to load. Defaults to None.
        dirout (str): Output directory.
        splits (list): List of dataset splits to save. Defaults to None (saves all splits).
        cols_mapping (dict): Mapping of column names. Defaults to None.
        fmt (str): Format to save dataset ('parquet' or 'csv'). Defaults to 'parquet'.
        ds_type (str): Dataset type for path structure. Defaults to 'raw'.
        show (int): If set to 1, print path of saved files. Defaults to 1.

        load_dataset
            path             : str,
            name             : Optional[str] = None,
            data_dir         : Optional[str] = None,
            data_files       : Optional[Union[str, Sequence[str], Mapping[str, Union[str, Sequence[str]]]]] = None,
            split            : Optional[Union[str, Split]] = None,
            cache_dir        : Optional[str] = None,
            features         : Optional[Features] = None,
            download_config  : Optional[DownloadConfig] = None,
            download_mode    : Optional[Union[DownloadMode, str]] = None,
            verification_mode: Optional[Union[VerificationMode, str]] = None,
            ignore_verifications           = "deprecated",
            keep_in_memory : Optional[bool]                = None,
            save_infos     : bool                          = False,
            revision       : Optional[Union[str, Version]] = None,
            token          : Optional[Union[bool, str]]    = None,
                            use_auth_token                 = "deprecated",
                            task                           = "deprecated",
            streaming      : bool                          = False,
            num_proc       : Optional[int]                 = None,
            storage_options: Optional[Dict]                = None,
            **config_kwargs,

    """
    if subset:
        dataset = load_dataset(name, subset)
        subset2 = subset
    else:
        dataset = load_dataset(name)
        subset2 = ""

    name2 = name.split('/')[1].replace("-", "_")
    # name2 = name2 if subset is None else f"{name2}/{subset2}"

    if splits is None:
        splits = dataset.keys()

    for key in splits:
        df = pd.DataFrame(dataset[key])
        print(f"Processing split '{key}' with shape: {df.shape}")
        if cols_mapping is not None:
            df = df.rename(columns=cols_mapping)
        # dirfile = f"{dirout}/{name2}/{ds_type}/{key}/df.{fmt}"
        dirfile = f"{dirout}/{name2}/{key}.{fmt}"

        if subset:
            dirfile = f"{dirout}/{subset2}/{key}.{fmt}"
        else:
            dirfile = f"{dirout}/{key}.{fmt}"
        pd_to_file(df, dirfile, show=show)


def hf_ds_meta(dataset: DatasetDict = None, meta=None, dirout: str = None):
    """Generates metadata for a dataset based on  input dataset, metadata, and output directory.
    Args:
        dataset (Dataset, optional):  input dataset. Defaults to None.
        meta (dict):  metadata to be updated. If not provided, a new one with an empty "split" key is created. Defaults to None.
        dirout (str):  output directory to save  metadata JSON file. Defaults to None.

    Returns:
        dict:  updated metadata with information about each split and a list of splits.

    """
    meta = {"split": []} if meta is None else meta
    for split in dataset.keys():  ### Train
        meta[split] = dict(dataset[split].info)
        meta["split"].append(split)

    if isinstance(dirout, str):
        json_save(meta, dirout + "/meta.json")

    return meta


def hf_ds_meta_todict_v2(dataset=None, metadata=None):
    metadata = {"split": []}
    for split in dataset.keys():  ### Train
        ##### Convert metadata to dictionary
        mdict = {key: value for key, value in dataset[split].info.__dict__.items()}
        metadata[split] = mdict
        metadata["split"].append(split)

    return metadata


def hf_dataset_search(catname="text-classification", lang="en"):
    """A function to search for datasets based on   specified category and language.

          python utils/util_hf.py  hf_dataset_search --catname "text-classification"

    Args:
        catname (str):  Category name for dataset filtering. Default is "text-classification".
        lang (str):     Language for dataset filtering. Default is "en".

    """
    from huggingface_hub import HfApi, DatasetFilter
    api = HfApi()

    catname: list = catname if isinstance(catname, list) else catname.split(",")
    lang: list = lang if isinstance(lang, list) else lang.split(",")

    # Create a filter for English text classification datasets
    filter = DatasetFilter(
        task_categories=catname,
        languages=lang
    )

    # List datasets based on  filter
    datasets = api.list_datasets(filter=filter)
    print(datasets)







#####################################################################################################
######## Checkpoint helper ##########################################################################
def test2():
    """
            Test hf_model_load_checkpoint function
            
            Output logs:
            ```
            Some weights of DebertaV2ForSequenceClassification were not initialized from the model checkpoint at microsoft/deberta-v3-small and are newly initialized: ['classifier.bias', 'classifier.weight', 'pooler.dense.bias', 'pooler.dense.weight']
            You should probably TRAIN this model on a down-stream task to be able to use it for predictions and inference.
            /home/kryo/miniconda3/envs/py38/lib/python3.8/site-packages/transformers/convert_slow_tokenizer.py:562: UserWarning: The sentencepiece tokenizer that you are converting to a fast tokenizer uses the byte fallback option which is not implemented in the fast tokenizers. In practice this means that the fast version of the tokenizer can produce unknown tokens whereas the sentencepiece version would have converted these unknown tokens into a sequence of byte tokens matching the original piece of text.
            warnings.warn(
            {'loss': 0.7873, 'grad_norm': 11.288691520690918, 'learning_rate': 1.0000000000000002e-06, 'epoch': 0.5}                                                        
            {'loss': 0.7013, 'grad_norm': 10.004307746887207, 'learning_rate': 2.0000000000000003e-06, 'epoch': 1.0}                                                        
            {'train_runtime': 35.2049, 'train_samples_per_second': 0.568, 'train_steps_per_second': 0.568, 'train_loss': 0.7442865610122681, 'epoch': 1.0}                  
            100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 20/20 [00:35<00:00,  1.76s/it]
            ./ztmp/hf_save_checkpoint_result/meta.json
            ```
    """
    epoch = 1
    model, training_args, tokenized_ds, compute_metrics, PrintCallback = test_setup(epoch=epoch)

    cc = Box({})
    cc.vals = training_args

    # Initialize Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_ds["train"],
        eval_dataset=tokenized_ds["test"],
        compute_metrics=compute_metrics,
        # callbacks=[CallbackCSaveheckpoint(cc)]
    )

    # Train the model
    trainer.train()

    output_dir = "./ztmp/hf_save_checkpoint_result"
    hf_save_checkpoint(trainer, output_dir, cc)

    loaded_model = hf_model_load_checkpoint(output_dir)
    # compare state_dicts of model and loaded_model
    assert model.state_dict().__str__() == loaded_model.state_dict().__str__(), "Model state dicts are not equal"


def test3():
    """
            Tests the `hf_model_get_mapping` function
            
            Output logs:
            ```
            DebertaV2Config {
            "_name_or_path": "microsoft/deberta-v3-small",
            "attention_probs_dropout_prob": 0.1,
            "hidden_act": "gelu",
            "hidden_dropout_prob": 0.1,
            "hidden_size": 768,
            "initializer_range": 0.02,
            "intermediate_size": 3072,
            "layer_norm_eps": 1e-07,
            "max_position_embeddings": 512,
            "max_relative_positions": -1,
            "model_type": "deberta-v2",
            "norm_rel_ebd": "layer_norm",
            "num_attention_heads": 12,
            "num_hidden_layers": 6,
            "pad_token_id": 0,
            "pooler_dropout": 0,
            "pooler_hidden_act": "gelu",
            "pooler_hidden_size": 768,
            "pos_att_type": [
                "p2c",
                "c2p"
            ],
            "position_biased_input": false,
            "position_buckets": 256,
            "relative_attention": true,
            "share_att_key": true,
            "transformers_version": "4.43.3",
            "type_vocab_size": 0,
            "vocab_size": 128100
            }

            model:  {'LABEL_0': 0, 'LABEL_1': 1}
            model: max_length  512
            {'LABEL_0': 0, 'LABEL_1': 1} {0: 'LABEL_0', 1: 'LABEL_1'} 512
            ```
    """
    label2id, id2label, max_length = hf_model_get_mapping(model='microsoft/deberta-v3-small')
    print(label2id, id2label, max_length)


def test4():
    """
    Tests the `hf_save_checkpoint` which save checkpoint from trainer.
    """
    epoch = 1
    model, training_args, tokenized_ds, compute_metrics, PrintCallback = test_setup(epoch=epoch)

    cc = Box({})
    cc.vals = training_args

    # Initialize Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_ds["train"],
        eval_dataset=tokenized_ds["test"],
        compute_metrics=compute_metrics,
        # callbacks=[CallbackCSaveheckpoint(cc)]
    )

    # Train the model
    trainer.train()

    output_dir = "./ztmp/hf_save_checkpoint_result"
    hf_save_checkpoint(trainer, output_dir, cc)
    assert os.path.exists(output_dir), "Output dir is missing"
    for fname in ['meta.json', 'optimizer.pt', 'scheduler.pt', 'trainer_state.json', 'rng_state.pth']:
        assert os.path.exists(f'{output_dir}/{fname}'), f"{fname} is missing"


def test5():
    """
    Trains a model, saves checkpoints, and verifies the existence of checkpoint files.
    """
    epoch = 3
    model, training_args, tokenized_ds, compute_metrics, PrintCallback = test_setup(epoch=epoch)

    cc = Box({})
    cc.vals = training_args

    # Initialize Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_ds["train"],
        eval_dataset=tokenized_ds["test"],
        compute_metrics=compute_metrics,
        callbacks=[CallbackCSaveheckpoint(cc)]
    )

    # Train the model
    trainer.train()

    assert os.path.exists(training_args.output_dir)
    checkpoint_dir = f"{training_args.output_dir}/checkpoint-{epoch*len(tokenized_ds['train'])}"
    assert os.path.exists(checkpoint_dir), "Checkpoint dir is missing"
    # Save checkpoint
    assert os.path.exists(f"{checkpoint_dir}/model.safetensors"),   "model.safetensors is missing"
    assert os.path.exists(f"{checkpoint_dir}/optimizer.pt"),        "optimizer.pt is missing"
    assert os.path.exists(f"{checkpoint_dir}/rng_state.pth"),       "rng_state.pth is missing"
    assert os.path.exists(f"{checkpoint_dir}/scheduler.pt"),        "scheduler.pt is missing"
    assert os.path.exists(f"{checkpoint_dir}/trainer_state.json"),  "trainer_state.json is missing"
    assert os.path.exists(f"{checkpoint_dir}/training_args.bin"),   "training_args.bin is missing"
    # CallbackCSaveheckpoint
    assert os.path.exists(f"{checkpoint_dir}/meta.json"),           "meta.json is missing"
    assert os.path.exists(f"{checkpoint_dir}/meta_metrics.json"),   "meta_metrics.json is missing"
    assert os.path.exists(f"{checkpoint_dir}/train.py"),            "train.py is missing"




class CallbackCSaveheckpoint(TrainerCallback):
    def __init__(self, cc=None):
        self.cc = cc  # Store cc as an instance variable

    def on_save(self, args, state, control, **kwargs):
        """ When doing Checkpoint /saving:
             Need to save more extra information INSIDE the checkpoint Folder.
               --> current training train.py
               --> meta.json

             --> checkpoint contains ALL the needed information to re-train...

              do you see why ?

              cc = box(cc) --> contains ALL params + mapping + all; into JSON.
              cc.XXYYUEEE.  

              cc Dictionnary of all params --> must be save inside the checkpoint too.

             The checkpoint becomes Self-Indepneant : All we need is inside the checkpoint folder...
                easy to re-start,  send to somebody else
                Very useful 

              utils_huggingface.py
                 with many utils functions/class to simplify the training management.
                
              json_save(cc, )

        
        """
        if state.is_world_process_zero:
            # Get the checkpoint folder path
            try:
                import os, json
                from utilmy import json_save
                dircheck = args.output_dir + f"/checkpoint-{state.global_step}" 
                os_makedirs(dircheck) 

                ### Train file
                os_copy_current_file(dircheck +"/train.py", sys.argv[0])

                ### Metrics history
                from utilmy import json_save, json_load
                json_save(state.log_history, dircheck +"/meta_metrics.json"  )            

                ### Meta data 
                cc_dict = cc_to_dict(self.cc)
                json_save(cc_dict, dircheck +"/meta.json")            

                print(f"Saved custom info to {dircheck}")
            except Exception as e:
                log(e)   

        return control



def hf_save_checkpoint(trainer, output_dir, cc ):
    import os, shutil

    # Save the model
    trainer.save_model(output_dir)
    
    #if save_model_every_epoch:
    #    epoch = trainer.state.epoch
    #    checkpoint_dir = f"{output_dir}/checkpoint-{epoch}"
    #    trainer.save_model(checkpoint_dir)
    
    #### Save the trainer state in the same directory
    trainer.save_state()
    
    #### Move state files to the model directory
    cc = cc_to_dict(cc)
    json_save(cc, f'{output_dir}/meta.json', show=0)  ### Required when reloading for   

    # log('Moving trainer state to model dir')
    # state_files = ['optimizer.pt', 'scheduler.pt', 'trainer_state.json', 'rng_state.pth']
    # for file in state_files:
    #     src = os.path.join(trainer.args.output_dir, file)
    #     dst = os.path.join(output_dir, file)
    #     if os.path.exists(src):
    #         shutil.move(src, dst)
    # 
    # Trainer save checkpoint in trainer.output_dir/checkpoint-{global_step}, not in trainer.output_dir
    # Instead of moving the checkpoint, we save it again in the model directory
    trainer._save_rng_state(output_dir)
    trainer.state.save_to_json(os.path.join(output_dir, 'trainer_state.json'))
    trainer._save_optimizer_and_scheduler(output_dir)



def hf_model_load_checkpoint(dir_checkpoint):
    from transformers import AutoModelForSequenceClassification

    model = AutoModelForSequenceClassification.from_pretrained(dir_checkpoint, num_labels=2) # Load {dir_checkpoint}/model.safetensors
    # checkpoint = torch.load( dir_checkpoint )
    # model.load_state_dict(checkpoint, strict=False)
    return model 


def hf_model_get_mapping(model='mymodel'):
    from transformers import AutoConfig

    config = AutoConfig.from_pretrained(model)

    log(config)

    label2id   = config.label2id
    id2label   = config.id2label
    max_length = config.max_position_embeddings
    log('model: ', str(label2id)[:100] )    
    log('model: max_length ', max_length)
    return label2id, id2label, max_length


def os_copy_current_file(dirout, thisfile=None):
    import os, shutil
    try:
       thisfile = __file__ if thisfile is None else thisfile 
       current_file = os.path.abspath(thisfile)
       shutil.copy2(current_file, dirout)
    except Exception as e:
       log(e)
   





#####################################################################################################
######## Trainer helper  ############################################################################
def test21():
    """
    Tests the `TrainerWeighted` class
    """
    model, training_args, tokenized_ds, compute_metrics, PrintCallback = test_setup(epoch=3)
    
    # Need to add sample_weights to the dataset['train'] ONLY
    # tokenized_ds['train'] = tokenized_ds['train'].map(lambda x: {'sample_weights': np.random.rand(1)[0]})
    tokenized_ds['train'].sample_weights = [np.random.rand(1)[0] for i in range(len(tokenized_ds['train']))]
    
    # Usage
    trainer = TrainerWeighted(
        model=model,
        args=training_args,
        train_dataset=tokenized_ds['train'],
        eval_dataset=tokenized_ds['test'],
    )
    trainer.train()


class TrainerWeighted(Trainer):
    def get_train_dataloader(self):
        if self.train_dataset is None:
            raise ValueError("Trainer: training requires a train_dataset.")
        
        data_collator = self.data_collator
        train_dataset = self.train_dataset
        
        sampler = torch.utils.data.WeightedRandomSampler(
            weights=train_dataset.sample_weights,
            num_samples=len(train_dataset),
            replacement=True
        )
        
        return torch.utils.data.DataLoader(
            train_dataset,
            batch_size=self.args.train_batch_size,
            sampler=sampler,
            collate_fn=data_collator,
            drop_last=self.args.dataloader_drop_last,
            num_workers=self.args.dataloader_num_workers,
            pin_memory=self.args.dataloader_pin_memory,
        )




############################################################################################
######### Metrics ##########################################################################
f1_metric       = evaluate.load("f1")
accuracy_metric = evaluate.load("accuracy")
clf_metric      = evaluate.combine(["accuracy", "f1", "precision", "recall"])




#################################################################################
######## Metrics Multi Labels ####################################################
def test7():
    """
    Tests the `compute_multi_accuracy` function
    """
    preds_score_2D = np.array([[0.1, 0.9], [0.2, 0.8], [0.3, 0.7], [0.6, 0.4]])
    labels_2D_onehot = np.array([[0, 1], [0, 1], [1, 0], [1, 0]])
    eval_pred = (preds_score_2D, labels_2D_onehot)
    res = compute_multi_accuracy(eval_pred)

    assert res == {'accuracy': 0.75}


def test8():
    """
    Tests the `compute_multi_accuracy_f1` function
    """
    preds_score_2D = np.array([[0.1, 0.9], [0.2, 0.8], [0.3, 0.7], [0.6, 0.4]])
    labels_2D_onehot = np.array([[0, 1], [0, 1], [1, 0], [1, 0]])
    eval_pred = (preds_score_2D, labels_2D_onehot)
    res = compute_multi_accuracy_f1(eval_pred)

    assert res['accuracy'] == 0.75
    assert res['f1_micro'] == 0.75
    assert res['f1_per_class']['f1_class_0'] == 0.6666666666666666
    assert res['f1_per_class']['f1_class_1'] == 0.8


def test9():
    """
    Tests the `compute_multi_accuracy_hamming` function
    
    Output logs:
    ```
    {'accuracy_hamming': [0.5, 1.0, 0.0, 1.0]}
    ```
    
    FIXME: It return array of hamming loss values. Does it meet the requirements?
    """
    preds_score_2D = np.array([[0.9, 0.9], [0.2, 0.8], [0.3, 0.7], [0.6, 0.4]])
    labels_2D_onehot = np.array([[0, 1], [0, 1], [1, 0], [1, 0]])
    eval_pred = (preds_score_2D, labels_2D_onehot)
    res = compute_multi_accuracy_hamming(eval_pred)

    print(res)


def test10():
    """
    Test the `metrics_multi` function
    
    Output logs:
    ```
    {'accuracy': 0.5, 'f1': 0.6666666666666666, 'precision': 0.5, 'recall': 1.0}
    ```
    """
    preds_score_2D = np.array([[0.9, 0.9], [0.2, 0.8], [0.3, 0.7], [0.6, 0.4]])
    labels_2D_onehot = np.array([[0, 1], [0, 1], [1, 0], [1, 0]])
    eval_pred = (preds_score_2D, labels_2D_onehot)
    res = metrics_multi(eval_pred)
    print(res)



def compute_multi_accuracy(eval_pred):
    """  list of OneHot_vector !!! 2D vector
    """
    preds_score_2D, labels_2D_onehot = eval_pred        ### 2D vector
    pred_labels_idx = np.argmax(preds_score_2D, axis=1) ### need reduction
    labels_idx      = np.argmax(labels_2D_onehot,      axis=1)
    
    acc = accuracy_metric.compute(predictions=pred_labels_idx, references= labels_idx)
    return {  "accuracy": acc["accuracy"], }


def compute_multi_accuracy_f1(eval_pred):
    """  list of OneHot_vector !!! 2D vector

    """
    preds_score_2D, labels_2D_onehot = eval_pred        ### 2D vector
    pred_labels_idx = np.argmax(preds_score_2D, axis=1) ### need reduction
    labels_idx      = np.argmax(labels_2D_onehot,      axis=1)
    
    acc      = accuracy_metric.compute(predictions=pred_labels_idx, references= labels_idx)
    f1_micro = f1_metric.compute(predictions=pred_labels_idx,       references= labels_idx, average='micro')["f1"]

    # Compute F1 per class
    f1_per_class = f1_metric.compute(predictions=pred_labels_idx, references=labels_idx, average=None)['f1']

    # Create a dictionary with class names (adjust based on your number of classes)
    class_names       = [f"class_{i}" for i in range(len(f1_per_class))]
    f1_per_class_dict = {f"f1_{name}": score for name, score in zip(class_names, f1_per_class)}

    return {  
        "accuracy":     acc["accuracy"],
        "f1_micro":     f1_micro,
        "f1_per_class": f1_per_class_dict 
    }


def compute_multi_accuracy_hamming(eval_pred):
    """ Partial F1 score
    
    
    """
    from sklearn.metrics import hamming_loss
    preds_score, labels = eval_pred

    pred_labels = [ [ pi>0.5 for pi in pred ] for pred in preds_score ] # np.argmax(predictions, axis=1)

    ham_list    = []
    for pred, label in zip(pred_labels, labels):
        ham_values = 1 - hamming_loss(label, pred)
        ham_list.append(ham_values)

    return {
        "accuracy_hamming": ham_list
    }


def metrics_multi(eval_pred):

   def sigmoid(x):
       return 1/(1 + np.exp(-x))

   preds_score, labels = eval_pred
   preds_proba = sigmoid(preds_score)
   preds  = (preds_proba > 0.5).astype(int).reshape(-1)
   labels = labels.astype(int).reshape(-1)
   dd =  clf_metric.compute(predictions=preds, references=labels)
   return dd






#################################################################################
######## Metrics Single labels ##################################################
def test11():
    """
    Tests the `compute_single_accuracy_f1` function
    
    Output logs:
    ```
    {'accuracy': 0.75, 'f1': 0.7333333333333334}
    ```
    """
    preds_score_2D = np.array([[0.1, 0.9], [0.2, 0.8], [0.3, 0.7], [0.6, 0.4]])
    labels = np.array([1, 1, 0, 0])
    eval_pred = (preds_score_2D, labels)
    res = compute_single_accuracy_f1(eval_pred)
    print(res)
    assert res['accuracy'] == 0.75


def test12():
    """
    Tests the `compute_single_metrics_f1_acc_perclass` function
    
    Output logs:
    ```
    {'accuracy': 0.75, 'f1': 0.7333333333333334, 'f1_class_0': 0.6666666666666666, 'f1_class_1': 0.8}
    ```
    """
    preds_score_2D = np.array([[0.1, 0.9], [0.2, 0.8], [0.3, 0.7], [0.6, 0.4]])
    labels = np.array([1, 1, 0, 0])
    eval_pred = (preds_score_2D, labels)
    res = compute_single_metrics_f1_acc_perclass(eval_pred)
    print(res)


def compute_single_(eval_pred, accuracy_fn):
   predictions, labels = eval_pred
   predictions = np.argmax(predictions, axis=1)
   return accuracy_fn.compute(predictions=predictions, references=labels)


def compute_single_accuracy_f1(eval_pred):
    pred_2D, labels = eval_pred
    pred_1D = pred_2D.argmax(axis=-1)
    
    accuracy = accuracy_metric.compute(predictions=pred_1D, references=labels)["accuracy"]
    f1       = f1_metric.compute(predictions=pred_1D, references=labels, average="macro")["f1"]
    return { "accuracy": accuracy, "f1": f1 }


def compute_single_metrics_f1_acc_perclass(eval_pred):
    predictions, labels = eval_pred
    predictions = predictions.argmax(axis=-1)
    
    accuracy = accuracy_metric.compute(predictions=predictions, references=labels)["accuracy"]
    f1       = f1_metric.compute(predictions=predictions, references=labels, average="macro")["f1"]
    
    # Compute F1 per class
    f1_per_class = f1_metric.compute(predictions=predictions, references=labels, average=None)['f1']
    
    # Create a dictionary with class names (adjust based on your number of classes)
    class_names       = [f"class_{i}" for i in range(len(f1_per_class))]
    f1_per_class_dict = {f"f1_{name}": score for name, score in zip(class_names, f1_per_class)}
    
    return {   
        "accuracy": accuracy,
        "f1": f1,
        **f1_per_class_dict
    }


def np_argmax(tuple_list, col_idx=1):
    idx= np.argmax([t[col_idx] for t in tuple_list])
    return tuple_list[ idx] 


def np_sort(tuples, col_id=0, desc=1):
    return sorted(tuples, key=lambda x: float(x[col_id]), reverse=True if desc == 1 else False)


def argmax_score(scores):
    return max(range(len(scores)), key=scores.__getitem__)



################################################################################
################ Metrics Report #################################################
def test13():
    """
    Tests the `classification_report_v2` function
    
    Output logs:
    ```
    {'0': {'precision': 1.0, 'recall': 0.5, 'f1-score': 0.6666666666666666, 'support': 2.0, 'accuracy': 0.5}, '1': {'precision': 0.6666666666666666, 'recall': 1.0, 'f1-score': 0.8, 'support': 2.0, 'accuracy': 1.0}, 'accuracy': 0.75, 'macro avg': {'precision': 0.8333333333333333, 'recall': 0.75, 'f1-score': 0.7333333333333334, 'support': 4.0}, 'weighted avg': {'precision': 0.8333333333333333, 'recall': 0.75, 'f1-score': 0.7333333333333334, 'support': 4.0}}
    ```
    """
    preds_score_2D = np.array([[0.1, 0.9], [0.2, 0.8], [0.3, 0.7], [0.6, 0.4]])
    labels = np.array([1, 1, 0, 0])
    y_pred = np.argmax(preds_score_2D, axis=1)

    report = classification_report_v2(labels, y_pred)
    print(report)
    assert str(report) == "{'0': {'precision': 1.0, 'recall': 0.5, 'f1-score': 0.6666666666666666, 'support': 2.0, 'accuracy': 0.5}, '1': {'precision': 0.6666666666666666, 'recall': 1.0, 'f1-score': 0.8, 'support': 2.0, 'accuracy': 1.0}, 'accuracy': 0.75, 'macro avg': {'precision': 0.8333333333333333, 'recall': 0.75, 'f1-score': 0.7333333333333334, 'support': 4.0}, 'weighted avg': {'precision': 0.8333333333333333, 'recall': 0.75, 'f1-score': 0.7333333333333334, 'support': 4.0}}"


def classification_report_v2(y_true, y_pred, labels=None, target_names=None, digits=4):

    from sklearn.metrics import confusion_matrix

    report = classification_report(y_true, y_pred, labels=labels, target_names=target_names, output_dict=True, digits=digits)
    cm     = confusion_matrix(y_true, y_pred, labels=labels)
    per_class_accuracy = cm.diagonal() / cm.sum(axis=1)
    
    for i, label in enumerate(labels or range(len(per_class_accuracy))):
        report[str(label)]['accuracy'] = per_class_accuracy[i]
    
    return report




################################################################################
################ Eval ##########################################################
def test6():
    """
    Tests the `eval_text_classification_get_label_names` function
    
    Output logs:
    ```
    Map: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████| 10/10 [00:00<00:00, 43.12 examples/s]

    ################### Start Label Mapping ###########################
    label_idx  label_idx
    0          1          1
    1          0          0
    2          0          0
    3          1          1
    4          1          1
    5          0          0
    6          1          1
    7          1          1
    8          1          1
    9          1          1
    label  pred
    0      1     1
    1      0     0
    2      0     1
    3      1     1
    4      1     0
    5      0     0
    6      1     1
    7      1     0
    8      1     0
    9      1     1
    ./ztmp/hf_eval_text_classification_get_label_names/df_pred_10.parquet
                                                    text  ...                                      pred_2d_label
    0  If you consider yourself a horror movie fan, c...  ...  [(1, '0.6153630857579557'), (0, '0.02791722460...
    1  **Maybe spoilers** **hard to spoil this thing ...  ...  [(0, '0.8680428982231944'), (0, '0.45516851023...
    2  It is real easy to toast, roast, flay, and oth...  ...  [(1, '0.10457742492554267'), (0, '0.0456275986...
    3  A year after the release of the average "House...  ...  [(1, '0.19881294841836006'), (0, '0.1506101840...
    4  One of the most famous of all movie serials! S...  ...  [(0, '0.36334959170229275'), (1, '0.1316912803...
    5  John Candy was very much a hit-or-miss comic a...  ...  [(0, '0.8663493798481298'), (0, '0.23621877372...
    6  Footprints is a very interesting movie that is...  ...  [(1, '0.5426991739373082'), (1, '0.53605537819...
    7  I had to call my mother (a WASP) to ask her ab...  ...  [(0, '0.9257195158265408'), (0, '0.02066223393...
    8  Don't quite know why some people complain abou...  ...  [(0, '0.9474810513341109'), (1, '0.50724754808...
    9  Nurse Betty is really an interesting movie. I ...  ...  [(1, '0.508337755943324'), (1, '0.424952560718...

    [10 rows x 8 columns]
    ./ztmp/hf_eval_text_classification_get_label_names/df_pred_sample.csv

    ################### Start Metrics ##########################
                precision    recall  f1-score   support

            a     0.4000    0.6667    0.5000         3
            b     0.8000    0.5714    0.6667         7

        accuracy                         0.6000        10
    macro avg     0.6000    0.6190    0.5833        10
    weighted avg     0.6800    0.6000    0.6167        10


    Accuracy: 0.6, 
    F1 Score: 0.6
    ./ztmp/hf_eval_text_classification_get_label_names/meta.json
    ```
    """
    dataset = load_dataset("imdb", split="test")
    dataset = dataset.select([random.randint(0, len(dataset)) for i in range(10)])
    dataset = dataset.map(lambda x: {'info': 'info'}) # add column 'info' to dataset
    
    _predictions = dataset.to_dict()['label']
    predictions = []
    for lb in range(len(_predictions)):
        prediction = []
        for i in range(2):
            prediction.append({"label": random.randint(0, 1), "score": random.random()})
        predictions.append(prediction)
    
    cc = Box({})
    cc.task = HFtask.text_classification
    cc.label2id = { 0: 0, 1: 1}
    cc.key2label = { 0: 0, 1: 1}
    cc.classes = ['a', 'b']
    cc.classes_idx = [0, 1]
    cc.dirout = "./ztmp/hf_eval_text_classification_get_label_names"
    
    eval_text_classification_get_label_names(predictions, cc, dataset)


def eval_text_classification_get_label_names(predictions, cc, dataset):
    #### predictions = pipe(dataset["text"][i:i+ibatch], batch_size= batch_size)
    log("\n################### Start Label Mapping ###########################")
    if cc.task == HFtask.text_classification :
        ### 2Dim: each prediction --> (label_id, score)
        preds_2d   = [ np_sort([(cc.label2id[ x["label"] ], x["score"])  for x in  pred_row ], col_id=1)  for pred_row in predictions]

        ### Best Top1 prediction
        pred_labels_top1 = [  np_argmax(x,1)[0]  for x in preds_2d   ] ## Argmax on Score
        dfp = pd.DataFrame({ 'text'      : dataset['text'], 
                                'info'      : dataset['info'], # ERROR: column not found
                                'label_idx' : dataset['label'], 
                                'pred_idx'  : pred_labels_top1 } )

        dfp['label'] = dfp['label_idx'].apply(lambda x : cc.key2label.get(x, "NA") )
        dfp['pred']  = dfp['pred_idx'].apply( lambda x : cc.key2label.get(x, "NA") )
        log(dfp[[ 'label_idx', 'label_idx'  ]]) 
        log(dfp[[ 'label', 'pred'  ]]) 


        #### 2Dim : NBatch x N_labels
        dfp['pred_2d_idx'] = [ [ str(x[0]), str(x[1]) ] for x in  preds_2d ]

        preds_2d_label       = [ np_sort([( cc.key2label.get( cc.label2id[ x["label"] ], ""), str(x["score"]) )   for x in  pred_row ], col_id= 1)  for pred_row in predictions]
        dfp['pred_2d_label'] = preds_2d_label


        #### For metrics
        dfp[[ 'text', 'info', 'label_idx', 'pred_idx', 'pred', 'label', 'pred_2d_idx', 'pred_2d_label' ]].shape
        dfp['pred_2d_label'] = dfp['pred_2d_label'].astype(str) # Require to convert object to string

        pd_to_file(dfp, f"{cc.dirout}/df_pred_{len(dfp)}.parquet", show=1 )
        pd_to_file(dfp.sample(n=30, replace=True), f"{cc.dirout}/df_pred_sample.csv", show=0, sep="\t" )

    # TODO: Add other tasks

    log("\n################### Start Metrics ##########################")    
    if "metric":
        #from utilmy.webapi.asearch.utils.util_metrics import metrics_eval
        #metrics = metrics_eval(true_labels, pred_labels, metric_list=['accuracy', 'f1', 'precision', 'recall'])
        #print(metrics)        
        true_idx_1D = dfp['label_idx'].values 
        pred_idx_1D = dfp['pred_idx'].values

        accuracy = accuracy_metric.compute(references=true_idx_1D, predictions=pred_idx_1D)['accuracy']
        f1       = f1_metric.compute(references=true_idx_1D, predictions=pred_idx_1D, average='micro')['f1']

        from sklearn.metrics import classification_report
        txt = classification_report(true_idx_1D, pred_idx_1D, 
                                  target_names= cc.classes,
                                  labels      = cc.classes_idx,                                            
                                  digits=4)

        txt += f"\n\nAccuracy: {accuracy}, \nF1 Score: {f1}" 
        log(txt)
        cc.metrics = str(txt)
        with open(f"{cc.dirout}/metrics.txt", mode='w') as fp:
            fp.write(txt)

    json_save(cc, f"{cc.dirout}/meta.json")










############################################################################################
######## Muti-label Classifier Helper ######################################################
def test17():
    """
    Test the `pd_to_file` function
    
    Output logs:
    ```
    a,b,c
    ./ztmp/LABELdata/df.parquet
    col1 col2 col3 labels colnew
    0    a    b    c    1,2  a,b,c
    1    d    e    f    2,3  d,e,f
    2    g    h    i    1,3  g,h,i
    files loaded for labels:  ['./ztmp/LABELdata/df.parquet']
    utilmy/asearch/nlp/cats/utils_hf.py:1173: SettingWithCopyWarning: 
    A value is trying to be set on a copy of a slice from a DataFrame.
    Try using .loc[row_indexer,col_indexer] = value instead

    See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
    df[colabel] = df[colabel].apply(lambda xstr: [t.strip() for t in xstr.split(",")])
    class_0 : merge all_labels into_single_class
    class_1 : merge all_labels into_single_class
    ```
    """
    data = {'col1': ['a', 'd', 'g'], 'col2': ['b', 'e', 'h'], 'col3': ['c', 'f', 'i'], 'labels': ["1,2", "2,3", "1,3"]}
    df = pd.DataFrame(data)

    dlabel = LABELdata()
    df = dlabel.pd_labels_merge_into_singlecol(df, cols=['col1', 'col2', 'col3'], colabels="colnew")
    log(df["colnew"].values[0])
    pd_to_file(df, f"./ztmp/LABELdata/df.parquet", show=1)
    dlabel.create_metadict(dirdata=f"./ztmp/LABELdata/*.parquet")


def test15():
    """
    Tests the `data_tokenize_split` function
    
    Output logs:
    ```
    nlabel_total:  2
                                0
    text    This is a sample text.
    labels              [0.0, 1.0]
    Map: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 2/2 [00:00<00:00, 297.96 examples/s]
    Filter: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████| 2/2 [00:00<00:00, 1006.79 examples/s]
    Dataset({
        features: ['labels', 'input_ids', 'token_type_ids', 'attention_mask'],
        num_rows: 2
    })
    Dataset({
        features: ['labels', 'input_ids', 'token_type_ids', 'attention_mask'],
        num_rows: 2
    })
    ```
    """
    data = {
        'text': ['This is a sample text.', 'Another example text.'],
        'labels': ["pos", "neg"]
    }
    df = pd.DataFrame(data)

    labelEngine = LABELdata()
    labelEngine.NLABEL_TOTAL = 2

    cc = Box({})
    cc.data = Box({})
    cc.data.sequence_max_length = 128
    cc.data.nlabel_total = 2

    tokenizer = AutoTokenizer.from_pretrained("microsoft/deberta-v3-base")
    ds = data_tokenize_split(df, tokenizer, labelEngine, cc, filter_rows=True)
    print(ds)


class LABELdata:
    from utilmy import (date_now, pd_to_file, log, pd_read_file, os_makedirs,
                        glob_glob, json_save, json_load, config_load,
                        dict_merge_into)

    def __init__(self, dirdata=None, dirmeta=None):
        """ Label Data Storage and converter methods
            for multi-class, multi-label

            dlabel = LABELdata()
            dlabel.create_metadict(dirin="./ztmp/data/cats/arxiv/train/df_8000.parquet")
            print(dlabel.I2L, dlabel.L2I, dlabel.NLABEL_TOTAL)

        """
        self.dirdata = dirdata  ###  training data raw files
        self.dirmeta = dirmeta  ###  meta.json file

        self.I2L, self.L2I, self.meta_dict = {}, {}, {}
        self.I2CLASS, self.CLASS2I = {}, {}
        self.NLABEL_TOTAL = 0

    def save_metadict(self, dirmeta=None):
        """ Save json mapper to meta.json
        """
        dirout2 = dirmeta if dirmeta is not None else self.dirmeta
        dirout2 = dirout2 if ".json" in dirout2 else dirout2 + "/meta.json"
        json_save(self.meta_dict, dirout2)
        log(dirout2)

    def load_metadict(self, dirmeta: str = None):
        """Load mapper from a directory containing meta.json 
        Args: dirmeta (str, optional): directory containing meta.json
        Returns: dict containing all mapping.
        """

        dirmeta = dirmeta if dirmeta is not None else self.dirmeta
        flist = glob_glob(dirmeta)
        flist = [fi for fi in flist if ".json" in fi.split("/")[-1]]
        fi = flist[0]

        if "json" in fi.split("/")[-1].split(".")[-1]:
            with open(fi, 'r') as f:
                meta_dict = json.load(f)

            if "meta_dict" in meta_dict.get("data", {}):
                ### Extract meta_dict from config training
                meta_dict = meta_dict["data"]["meta_dict"]

            self.NLABEL_TOTAL = meta_dict["NLABEL_TOTAL"]
            self.I2L = {int(ii): label for ii, label in meta_dict["I2L"].items()}  ## Force encoding
            self.L2I = {label: int(ii) for label, ii in meta_dict["L2I"].items()}

            self.dirmeta = fi
            return self.I2L, self.L2I, self.NLABEL_TOTAL, meta_dict
        else:
            log(" need meta.json")

    def create_metadict(self, dirdata="./ztmp/data/cats/arxiv/*.parquet", cols_class=None, dirout=None,
                        merge_all_labels_into_single_class=1):
        """Create a mapper json file for labels from raw training data
            python nlp/cats/multilabel.py labels_load_create_metadict --dirin "./ztmp/data/cats/arxiv/train/*.parquet" --dirout "./ztmp/data/cats/arxiv/meta/meta.json"

        Doc::
            Args: dirin (str, optional):  df[["labels"]] as string joined by ","

            Returns: meta.json
                tuple: A tuple containing following mapper dictionaries:
                    - I2L (dict): dict mapping labels to their corresponding indices.
                    - L2I (dict): dict mapping indices to their corresponding labels.
                    - NLABEL_TOTAL (int): total number of labels.
                    - meta_dict (dict): dict containing additional metadata about labels.

        """
        flist = glob_glob(dirdata)
        log("files loaded for labels: ", flist)
        df = pd_read_file(flist)
        assert df[["labels"]].shape

        ##### Expand column lbael  into multiple columns
        df2, cols_class = self.pd_labels_split_into_cols(df, colabel="labels", cols_class=cols_class)
        # df2 = df2.drop_duplicates()


        #####  mapping Label --> Index : Be careful of duplicates
        I2L, L2I = {}, {}
        I2CLASS, CLASS2I = {}, {}
        dd = {"labels_n_unique": {}, "labels": {}}
        idx = -1
        for class_i in cols_class:
            vv = df2[class_i].drop_duplicates().values
            dd["labels_n_unique"][class_i] = len(vv)
            dd["labels"][class_i] = {"labels": list(vv),
                                     "freq": df2[class_i].value_counts().to_dict()}

            class_i2 = f"{class_i}"
            if int(merge_all_labels_into_single_class) == 1:
                log(f"{class_i} : merge all_labels into_single_class")
                class_i2 = "" ### Class Name default

            ### For each label of column, add indexesm add to class indexes. 
            if class_i2 not in CLASS2I:
               CLASS2I[class_i2] = []
               
            for label in vv:
                label = label.strip()
                label2 = f"{class_i2}-{label}" if class_i2 != "" else label  ### gender-male, gender-female
                # log("label:", label2)
                if label2 not in L2I:
                    idx += 1
                    L2I[label2] = idx  ### red --> 1, blue --> 2
                    I2L[idx]    = label2  ### 1 --> red, 2 --> blue

                    I2CLASS[idx] = class_i2  ####  red --> color, blue --> color
                    CLASS2I[class_i2].append(idx)  #### Color --> [red, blue]
                    # log(CLASS2I[class_i2])

        #### All classes
        dd["class_cols"]   = list(cols_class)  ### List of class columns
        dd["NCLASS_TOTAL"] = len(cols_class)

        #### Labels of each class
        ### colA --> OnehoA,  colB --> onehotB     bigHot = concat(onehotA, onehotB,...)      

        NLABEL_TOTAL = len(L2I) 
        
        #### +1 For NA/unknow values : not needed, only at Encoding
        # NLABEL_TOTAL = NLABEL_TOTAL + 1  ### + 1 for NA/Unknown Values   
             
        dd["NLABEL_TOTAL"] = NLABEL_TOTAL
        dd["I2L"] = I2L
        dd["L2I"] = L2I
        dd["I2CLASS"] = I2CLASS  ####  red --> color, blue --> color
        dd["CLASS2I"] = CLASS2I  ####  Color --> [red, blue]

        self.meta_dict = dd
        self.I2L = I2L
        self.L2I = L2I
        self.NLABEL_TOTAL = NLABEL_TOTAL


        if dirout is not None:
            self.save_metadict(dirout)

        return I2L, L2I, NLABEL_TOTAL, self.meta_dict

    def pd_labels_split_into_cols(self, df, colabel="labels", cols_class=None):
        df = df[[colabel]]
        if isinstance(df[colabel].values[0], str):
            df[colabel] = df[colabel].apply(lambda xstr: [t.strip() for t in xstr.split(",")])
        else:
            df[colabel] = df[colabel].apply(lambda xlist: [t.strip() for t in xlist])

        ncols = len(df[colabel].values[0])
        cols_class = [f"class_{i}" for i in range(ncols)] if cols_class is None else cols_class
        df2 = pd.DataFrame(df[colabel].tolist(), columns=cols_class)
        df2.index = df.index

        return df2, cols_class

    def pd_labels_merge_into_singlecol(self, df, cols=None, sep=",", colabels="labels"):
        if cols is None:
            cols = df.columns.tolist()
        df[colabels] = df[cols].astype(str).agg(sep.join, axis=1)
        return df


    def to_onehot(self, xstr: str):
        """ Converts a string of ","labels into a one-hot encoded list.
        """
        zero, one = 0.0, 1.0  ## HFace needs float !!
        labels_onehot = [float(zero)] * self.NLABEL_TOTAL
        
        if isinstance(xstr, str):
              xstr = xstr.split(",")
              
        for label in xstr:
            ### If mising, One Label INDEX for unknown
            label_id = self.L2I.get(label, self.NLABEL_TOTAL - 1)
            # log("label_id:",label,  label_id)
            labels_onehot[label_id] = one  #

        return labels_onehot

    def pd_validate_dataframe(df, cols=None, sep=",", colabels="labels", nrows=1000):

        assert df[["text", "labels"]].shape

        labels = df["labels"].values
        if isinstance(labels[0], str):
            labels= [ x.split(",") for x in  labels ]
            
        nclass = len(labels[0])
        for i in range(len(df)):
            if len(labels[i]) != nclass:
                    raise Exception(" Mismatch")

        log("dataframe text, labels  validated")
        return True


def data_tokenize_split(df, tokenizer, labelEngine, cc, filter_rows=True):
    """ 

        {'input_ids': [[1, 8382, 277, 39093, 25603, 31487, 840, 39093, 28368, 59543, 2, 2, 2, 2, 2, 2, 2, 2, 2], 
                      [1, 14046, 271, 5203, 473, 13173, 75204, 270, 6547, 40457, 267, 13946, 5648, 2, 2, 2, 2, 2, 2]],

        'token_type_ids': [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 

        'attention_mask': [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], 
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0]], 

        'labels': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 

    """
    cols = list(df.columns)
    max_length   = cc.data.sequence_max_length
    NLABEL_TOTAL = cc.data.nlabel_total
    log("nlabel_total: ", NLABEL_TOTAL)


    df["labels"] = df["labels"].apply(lambda x: labelEngine.to_onehot(x))
    # df["labels"] = df["labels"].apply(lambda x: to_onehot(x) )
    log(df[["text", "labels"]].head(1).T)


    def preprocess_func(row):
        #### Text tokenizer
        out = tokenizer(row["text"], truncation=True, padding=True, max_length=max_length,
                        return_offsets_mapping=False,
                        return_overflowing_tokens=False)

        out["labels"] = row["labels"]
        # log(out)    
        # output["input_ids"] = output.pop("input_ids")  # Add input_ids to  output
        return out

    #### Encode texts
    ds = Dataset.from_pandas(df[["text", "labels"]])
    ds = ds.map(preprocess_func, batched=True)


    #### Filter labels with only a single instance
    if filter_rows:
        label_counts = Counter([tuple(label) for label in ds["labels"]])
        valid_labels = [label for label, count in label_counts.items() if count > 1]
        ds = ds.filter(lambda row: tuple(row["labels"]) in valid_labels)

    #### Reduce columns in dataset
    ds = ds.remove_columns(['text'])

    #  ['text', 'labels', 'input_ids', 'token_type_ids', 'attention_mask']
    # ds           = ds.remove_columns( cols)
    # ds = ds.remove_columns(['overflow_to_sample_mapping', 'offset_mapping', ] + cols)
    log(ds)
    return ds







########################################################################################
##################### Tokenizer helper #################################################
def DataCollatorClassification(tokenizer=None):
    from transformers import DataCollatorWithPadding
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer, padding="longest")
    return data_collator


def test14():
    """
    Test the `tokenize_single_label_batch` function
    
    FIXME: The function is not complete.
    """
    dataset = load_dataset("imdb", split="test")
    dataset = dataset.select([random.randint(0, len(dataset)) for i in range(10)])
    tokenizer = AutoTokenizer.from_pretrained("microsoft/deberta-v3-base")

    out = tokenize_single_label_batch(dataset, 2, None, tokenizer)


def tokenize_single_label_batch(rows, num_labels, label2key, tokenizer, coltext='text', colabel='label'):
        """ Single Label: OneHot Label or Int Label. (HF has some small bugs...)
        """
        out = tokenizer( rows[coltext], truncation=True,  
            # padding=True, 
            # max_length= cc.max_length, 
        )

        # ##### Label_idx into Multi-Label OneHot encoding ######## 
        ll   = []
        sample_list = rows[colabel]
        for row in sample_list:
            ones = [0. for i in range(num_labels)]
            
            # if isinstance(row, str):
            #     row = row.split(",")
                
            if isinstance(row, int):
                ### 1 text ---> 1 Single Tags 
                ones[ row ] = 1.
                ll.append(ones)

            # elif isinstance(row, list):
            #     ### 1 text ---> Many Label Tags
            #     for vali in row:
            #         idx = label2key[vali] if isinstance(vali, str) else vali 
            #         ones[ vali ] = 1.   ### Float for Trainer
            #     ll.append(ones )                  
        out[colabel] = ll
        return out





######################################################################################
############Training helper ##########################################################
def run_train_single(istest=1, dirout="./ztmp/exp/L1_cat/v3deber/" ):
    """  multi_label_prediction ONLY

        alias pytr="python  src/train/cat_single.py  "

        pytr  run_train_single --istest 1  2>&1 | tee -a ztmp/exp/log_exp_L1_single.py  


        mkdir -p ztmp/exp/L0_type/
        pytr  run_train_single --istest 0  2>&1 | tee -a ztmp/exp/L0_type/log_exp_L0_type.py 


        python src/train/cat_single.py  run_eval --istest 0       

        #### Details
        export  PYTORCH_MPS_HIGH_WATERMARK_RATIO="0.0" 
      

    """
    checkpoint = None
    # checkpoint = "ztmp/exp/L2_cat/deberV3/train/checkpoint-17500-ok"
    # checkpoint = "ztmp/exp/L3_cat/deberV3large/train/checkpoint-10000ok"
    cc = json_load( f'{checkpoint}/meta.json') if checkpoint is not None else {}
    cc = Box(cc)

    if "#### News Type L0_type ":
        cc.task         = "L0_type"
        dirout          = f"./ztmp/exp/{cc.task}/deberV3/"
        cc.datafun_name = "data_newstype_train"
        cc.colabel      = 'newstype'
        cc.coltext      = 'text'
        cc.epochs       = 3
        cc.save_steps   = 500
        cc.eval_steps   = 200
        device          = 'mps'

    log("\n###### User default Params   ###################################")
    if "config":    
        cc.model_name ="MoritzLaurer/deberta-v3-base-zeroshot-v2.0"  ### level 2 
        cc.model_name = checkpoint if checkpoint is not None else  cc.model_name

        cc.device = torch_device(device)      
        cc.per_device_train_batch_size = 4
        cc.max_length = 1024  # 1024  #1024
 

        ### Need sample to get enough categories
        cc.n_train = 20   if istest == 1 else 1000000000
        cc.n_test  = 10   if istest == 1 else int(cc.n_train*0.1)


        if 'params':
            cc.checkpoint = checkpoint 
            cc.problem_type =  "single_label_classification" ### Hard-Coded
            cc.dirout            = dirout
            cc.dirout_checkpoint =  cc.dirout + '/train'
            cc.dirout_log        =  cc.dirout + '/log'
            cc.dirout_model      =  cc.dirout + '/model'
            
            #### Trainer Args ############################################
            aa = Box({})
            aa.output_dir    = cc.dirout_checkpoint
            aa.logging_dir   = cc.dirout_log
            aa.logging_steps = 10

            aa.per_device_train_batch_size = cc.per_device_train_batch_size 
            aa.per_device_eval_batch_size  = cc.per_device_train_batch_size

            aa.gradient_accumulation_steps = 1
            aa.optim                       = "adamw_hf"
            aa.learning_rate               = 2e-5
            aa.max_grad_norm               = 2
            aa.max_steps                   = -1
            aa.warmup_ratio                = 0.2 # 20%  total step warm-up
            # lr_schedulere_type='constant'
            aa.evaluation_strategy    = "steps"
            aa.save_strategy          = "steps"
            aa.load_best_model_at_end = False

            aa.num_train_epochs  = cc.epochs
            aa.logging_steps     = min(50,  cc.n_train-1)
            aa.eval_steps=   cc.eval_steps      
            aa.save_steps=   cc.save_steps

            cc.hf_args_train = copy.deepcopy(aa)

            os_makedirs(cc.dirout_log)
            os_makedirs(cc.dirout_checkpoint)
            os_makedirs(cc.dirout + "/model")        


    log("\n##### Data load  #########################################")

    df = pd_read_file("ztmp/data/cats/news/train_newstype/*.parquet")    
    df = df.sample(frac=1.0)
    log(df.columns, df.head(1).T, "\n\n")



    log("\n##### data encoding  #########################################")
    dataset, test_dataset, df, cc = dataload_fun(df, cc) 
    del df; gc.collect()

    cc.num_labels = len(cc.classes)
    log('N_labels used:', cc.num_labels, len(cc.label2key), len(cc.key2label) )


    log("\n###################load Tokenizer #############################")
    torch_init()
    tokenizer = AutoTokenizer.from_pretrained(cc.model_name)    

    def tokenize_batch_onehot(rows, num_labels, label2key, problem_type):
        out = tokenizer( rows["text"],truncation=True,  
                        # padding=True, 
                        # max_length= cc.max_length, 
                  )

        ##### Direct Integer encoding
        #if problem_type == 'single_label_classification':
        #    out['labels'] = rows['label'] ### No OneHot for Single Label
        #    return out

        # ##### Label_idx into Multi-Label OneHot encoding ######## 
        ll   = []
        sample_list = rows['label']
        for labeli in sample_list:
            ones = [0. for i in range(num_labels)]
                
            if isinstance(labeli, int):
                ### 1 text ---> 1 Single Tags 
                ones[ labeli ] = 1.0
                ll.append(ones)

            elif isinstance(labeli, str):
                ### 1 text ---> 1 Single Tags 
                idx = label2key[labeli]
                ones[ idx  ] = 1.0
                ll.append(ones)

            # elif isinstance(row, list):
            #     ### 1 text ---> Many Label Tags
            #     for vali in row:
            #         idx = label2key[vali] if isinstance(vali, str) else vali 
            #         ones[ vali ] = 1.   ### Float for Trainer
            #     ll.append(ones )                  
        out['labels'] = ll
        return out


    log(cc.problem_type) 
    tk_batch2 = partial(tokenize_batch_onehot, num_labels=cc.num_labels, label2key=cc.label2key, 
                        problem_type=cc.problem_type)
    tk_ds     = dataset.map(tk_batch2 , batched=True)

    log('##### \ntk_ds', tk_ds)
    log(tk_ds['test'][0]['labels'], "\n")

    ### need to remove for Single prediction)
    tk_ds       = tk_ds.remove_columns(['text'])
    tk_ds       = tk_ds.remove_columns(['__index_level_0__'])    
    log(tk_ds)
   

    from transformers import DataCollatorWithPadding
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer, 
                              max_length= cc.max_length, padding='max_length' )
    del dataset; gc.collect()     


    log("\n###################load model #############################")
    model = AutoModelForSequenceClassification.from_pretrained(cc.model_name, 
                      num_labels= cc.num_labels,
                      # id2label= cc.key2label, label2id= cc.label2key,
                      problem_type= cc.problem_type, ### Hard Coded, cannot Change
                      ignore_mismatched_sizes=True)

    model.config.max_position_embeddings = cc.max_length ### Force the max_length

    ##### Set up training
    args    = TrainingArguments(**cc.hf_args_train )
    trainer = Trainer( model=model, args=args, tokenizer=tokenizer,
        train_dataset   = tk_ds['train'],
        eval_dataset    = tk_ds['test'],
        # data_collator   = data_collator,
        compute_metrics = compute_single_accuracy_f1,
        # callbacks       = [EarlyStoppingCallback(early_stopping_patience= cc.early_stop )],
        callbacks       = [CallbackCSaveCheckpoint(TrainerCallback)],
        # optimizers=(optimizer, None)  # Pass optimizer, no scheduler
    )

    log("\n###################Train: start #############################")
    cc_save(cc, cc.dirout) 
    log("#### Checkpoint: ", cc.checkpoint)
    trainer_out = trainer.train(resume_from_checkpoint= cc.checkpoint)

    hf_save_checkpoint(trainer,  f"{cc.dirout}/model", cc )
    evals = trainer.evaluate()
    cc['trainer_eval']    = str(evals)
    cc['trainer_metrics'] = trainer_out.metrics
    cc_save(cc, cc.dirout)
    del trainer; del model; gc.collect()



def run_eval(cfg='config/train.yml', cfg_name='classifier_data', 
              dirout:  str = "./ztmp/exp",
              dirdata: str = './ztmp/data/cats/cat_name/train/',
              istest=1):
    """ 
    
       python  src/train/cat_single.py  run_eval --istest 0 

                 
    
    """
    istest=0
    log("\n###### User default Params   ###################################")

    dirdata = "ztmp/data/cats/news/train_gpt3/*.parquet"
    tag     = ""
  

    if "### L3 Eval":
        dirmodel = "ztmp/exp/L3_cat/deberV3large/train/checkpoint-5000"

        datafun_name = "data_eval_v1"    
        colabel ="L3_cat"
        tag = '-llama3_7b'
        nmax = 500000
        device = 'mps'


    log("\n################### Config Load  ##############################")
    cc = json_load(dirmodel +"/meta.json")
    if cc is None or len(cc) < 1 :
       cc = json_load(dirmodel +"/../../meta.json") #### Checkpoint
       #if cc is None : return

    ### pip install python-box fire  
    cc = Box(cc) ; log("cc.keys", cc.keys() )
    cc.dirmodel     =  dirmodel
    cc.colabel      =  colabel

    cc.n_train = 10 if istest == 1 else 10000000 
    cc.n_test  = 1  if istest == 1 else 100000 
    cc.batch_size = 8
    cc.device     = device


    device          = torch_device(device)
    cc.dirdata      = dirdata
    cc.datafun_name = datafun_name
    cc.task         = HFtask.text_classification
    cc.dirout       = cc.dirmodel + f'/eval{tag}/'


    #### Mapping with Real Label names
    cc.key2label = { int(key): label for key,label in cc.key2label.items() }
    log(len(cc.label2key), len(cc.key2label))
    classes_idx = [ cc.label2key[li] for li in cc.classes ]
    log('cc:',str(cc.classes)[:100])


    log("\n###################load dataset #############################")    
    df = pd_read_file(cc.dirdata)
    log(df.columns, df.head(1).T, "\n")

    dataset0 = Dataset.from_pandas(df[['text', 'label', 'info']])   


    log("\n################## Load model #############################")
    tokenizer = AutoTokenizer.from_pretrained(cc.model_name)
    pipe      = pipeline(cc.task, model=f"{cc.dirmodel}",tokenizer=tokenizer, device=device,
                         batch_size= cc.batch_size, return_all_scores=True,)

    #### Mapping with Internal Pytorch Mapping
    label2id, id2label, max_length= hf_model_get_mapping(model= f"{cc.dirmodel}" )


    log("\n################### Accelerate setup ##########################")
    accelerator = accelerator_init(device=device)
    pipe        = accelerator.prepare(pipe)
            

    log("\n################### Start inference ##########################")
    dataset = dataset_reduce(dataset0, nmax) #   ntrain= cc.ntrain)

    ibatch     = 512
    batch_size = 16
    t0 = time.time()
    predictions = [] ; 
    with torch.no_grad():
        for i in range(0, 1+len(dataset), ibatch):
            res = pipe(dataset["text"][i:i+ibatch], batch_size= batch_size)
            if len(res)< 1: break
            log(f"Block {i}. Pred:", str(res[0])[:80] )
            predictions = predictions + res     
    log('Npred:', len(predictions), time.time()-t0)


    log("\n################### Start Label Mapping ###########################")
    if cc.task == HFtask.text_classification :
            ### 2Dim: each prediction --> (label_id, score)
            preds_2d   = [ np_sort([(label2id[ x["label"] ], x["score"])  for x in  pred_row ], col_id=1)  for pred_row in predictions]

            ### Best Top1 prediction
            pred_labels_top1 = [  np_argmax(x,1)[0]  for x in preds_2d   ] ## Argmax on Score
            dfp = pd.DataFrame({ 'text'      : dataset['text'], 
                                  'info'     : dataset['info'],
                                 'label_idx' : dataset['label'], 
                                 'pred_idx'  : pred_labels_top1 } )

            dfp['label'] = dfp['label_idx'].apply(lambda x : cc.key2label.get(x, "NA") )
            dfp['pred']  = dfp['pred_idx'].apply( lambda x : cc.key2label.get(x, "NA") )
            log(dfp[[ 'label_idx', 'label_idx'  ]]) 
            log(dfp[[ 'label', 'pred'  ]]) 


            #### 2Dim : NBatch x N_labels
            dfp['pred_2d_idx'] = [ [ str(x[0]), str(x[1]) ] for x in  preds_2d ]

            preds_2d_label       = [ np_sort([( cc.key2label.get( label2id[ x["label"] ], ""), str(x["score"]) )   for x in  pred_row ], col_id= 1)  for pred_row in predictions]
            dfp['pred_2d_label'] = preds_2d_label


            #### For metrics
            dfp[[ 'text', 'info', 'label_idx', 'pred_idx', 'pred', 'label', 'pred_2d_idx', 'pred_2d_label' ]].shape


    elif cc.task == HFtask.zeroshot_classifier :
            true_labels = dataset["label"]
            pred_labels = [ x['labels'][ [ np.argmax(x['scores']) ] ] for x in predictions]

            dfp =[]
            for row in predictions :
               dfp.append( [row['labels'], row['scores'] ])
            dfp = pd.DataFrame( dfp, columns=['labels', 'scores'] )
            dfp['text']  = dataset['text']
            dfp['label'] = dataset['label']


    pd_to_file(dfp, f"{cc.dirout}/df_pred_{len(dfp)}.parquet", show=1 )
    pd_to_file(dfp.sample(n=30, replace=True), f"{cc.dirout}/df_pred_sample.csv", show=0, sep="\t" )


    log("\n################### Start Metrics ##########################")    
    if "metric":
        #from utilmy.webapi.asearch.utils.util_metrics import metrics_eval
        #metrics = metrics_eval(true_labels, pred_labels, metric_list=['accuracy', 'f1', 'precision', 'recall'])
        #print(metrics)        
        true_idx_1D = dfp['label_idx'].values 
        pred_idx_1D = dfp['pred_idx'].values

        accuracy = accuracy_metric.compute(references=true_idx_1D, predictions=pred_idx_1D)['accuracy']
        f1       = f1_metric.compute(references=true_idx_1D, predictions=pred_idx_1D, average='micro')['f1']

        from sklearn.metrics import classification_report
        txt = classification_report(true_idx_1D, pred_idx_1D, 
                                  target_names= cc.classes,
                                  labels      = classes_idx,                                            
                                  digits=4)

        txt += f"\n\nAccuracy: {accuracy}, \nF1 Score: {f1}" 
        log(txt)
        cc.metrics = str(txt)
        with open(f"{cc.dirout}/metrics.txt", mode='w') as fp:
            fp.write(txt)

    json_save(cc, f"{cc.dirout}/meta.json")



def cc_save(cc, dirout):
    flist = [ f'{dirout}/meta.json',  f'{dirout}/train/meta.json',
              f'{dirout}/model/meta.json'  ]
    for fi in flist :
        log(fi)
        json_save(cc, fi)

    os_copy_current_file( f"{dirout}/train/train.py")    




#######################################################################################
######### Manual multi softmax  #######################################################
def test16():
    """
    Tests the `MultiSoftmaxClassifier` class
    
    Output logs:
    ```
    Some weights of DebertaV2ForSequenceClassification were not initialized from the model checkpoint at microsoft/deberta-v3-base and are newly initialized: ['classifier.bias', 'classifier.weight', 'pooler.dense.bias', 'pooler.dense.weight']
    You should probably TRAIN this model on a down-stream task to be able to use it for predictions and inference.
    Asking to truncate to max_length but no maximum length is provided and the model has no predefined maximum length. Default to no truncation.
    Predicted probabilities: [[0.10758269 0.09973765 0.09275983 0.09038799 0.07966967 0.0963518
    0.07937793 0.07289842 0.10557437 0.08885682 0.08680277]] 
    ```
    """
    import torch
    from transformers import AutoTokenizer

    # Load model and tokenizer
    modelid = 'microsoft/deberta-v3-base'
    tokenizer = AutoTokenizer.from_pretrained(modelid)
    model = MultiSoftmaxClassifier.from_pretrained(modelid, num_labels=11)
    model.eval()  # Set model to evaluation mode

    # Function to perform inference
    def predict(texts):
        # Tokenize input text
        inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")

        # Move inputs to same device as model
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

        # Perform inference
        with torch.no_grad():
            outputs = model(**inputs)

        # Apply softmax to logits to get probabilities
        logits = outputs['logits']
        probabilities = torch.nn.functional.softmax(logits, dim=1)

        # Convert probabilities to numpy array
        probabilities = probabilities.cpu().numpy()

        return probabilities

    # Example usage
    texts = ["Sample text for classification."]
    predictions = predict(texts)
    print("Predicted probabilities:", predictions)


class MultiSoftmaxClassifier(AutoModelForSequenceClassification):
    def __init__(self, config):
        """
        3 softmax head : one per class group: 
            class A : A1-A5, 
            class B : B1-B4, 
            class C : C1-C2

        ### Usage code:
            # Load model and tokenizer
            modelid   = 'microsoft/deberta-v3-base'
            tokenizer = AutoTokenizer.from_pretrained( modelid)
            model     = MultiSoftmaxClassifier.from_pretrained(modelid, num_labels=11)
            model.eval()  # Set model to evaluation mode

            # Tokenize input text
            inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
            
            # Move inputs to same device as model
            inputs = {k: v.to(model.device) for k, v in inputs.items()}
            
            # Perform inference
            with torch.no_grad():
                outputs = model(**inputs)
            print( probabilities.cpu().numpy() )

        """
        super().__init__(config)
        self.classifier = torch.nn.Linear(config.hidden_size, config.num_labels)  # Total labels across all classes

    def forward(self, **inputs):
        outputs = super().forward(**inputs)
        # logits = outputs.logits
        logits = self.classifier(outputs.pooler_output)  # Use classifier on pooled output

        # Apply softmax per class group: A1-A5, B1-B4, C1-C2
        # 1 Class can only contain 1 label only,
        logits = torch.cat([
            torch.nn.functional.softmax(logits[:, :5], dim=1),
            torch.nn.functional.softmax(logits[:, 5:9], dim=1),
            torch.nn.functional.softmax(logits[:, 9:], dim=1)
        ], dim=1)
        return torch.nn.functional.softmax(logits, dim=1)







########################################################################################################
############# Hiearchical Softmax ######################################################################
import random
from transformers import DebertaV2PreTrainedModel, DebertaV2Model, TextClassificationPipeline
from transformers.modeling_outputs import SequenceClassifierOutput


from hierarchicalsoftmax import SoftmaxNode, HierarchicalSoftmaxLinear, HierarchicalSoftmaxLoss
from hierarchicalsoftmax.inference import leaf_probabilities
from hierarchicalsoftmax.metrics import (
        greedy_accuracy, 
        greedy_f1_score, 
        greedy_accuracy_depth_one, 
        greedy_accuracy_depth_two,
        greedy_accuracy_parent,
        greedy_precision,
        greedy_recall,)

def test_hiearsoftmax_get_dictalbel():
    """
            Tests the `generate_dictlabels` function
            
            Output logs:
            ```
            With name_recusive=True
            {'a': a, 'a,a': a,a, 'a,b': a,b, 'a,c': a,c, 'a,d': a,d, 'b': b, 'b,a': b,a, 'b,b': b,b, 'a,b,a': a,b,a, 'a,b,b': a,b,b, 'a,e': a,e, 'a,e,f': a,e,f}
            root
            ├── a
            │   ├── a,a
            │   ├── a,b
            │   │   ├── a,b,a
            │   │   └── a,b,b
            │   ├── a,c
            │   ├── a,d
            │   └── a,e
            │       └── a,e,f
            └── b
                ├── b,a
                └── b,b
            With name_recusive=False
            {'a': a, 'a,a': a, 'a,b': b, 'a,c': c, 'a,d': d, 'b': b, 'b,a': a, 'b,b': b, 'a,b,a': a, 'a,b,b': b, 'a,e': e, 'a,e,f': f}
            root
            ├── a
            │   ├── a
            │   ├── b
            │   │   ├── a
            │   │   └── b
            │   ├── c
            │   ├── d
            │   └── e
            │       └── f
            └── b
                ├── a
                └── b
            ```
    """
    label_list = ["a,a", "a,b", "a,c", "a,d", "b,a", "b,b", "a,b,a", "a,b,b", "a,e,f"]

    print("With name_recusive=True")
    root, dictlabels = hierarchicalsoftmax_get_dictlabels(label_list)
    print(dictlabels)
    assert root.render_equal("""
        root
        ├── a
        │   ├── a,a
        │   ├── a,b
        │   │   ├── a,b,a
        │   │   └── a,b,b
        │   ├── a,c
        │   ├── a,d
        │   └── a,e
        │       └── a,e,f
        └── b
            ├── b,a
            └── b,b 
        """,
        print=True,
    )
    assert list(dictlabels.keys()) == ['a', 'a,a', 'a,b', 'a,c', 'a,d', 'b', 'b,a', 'b,b', 'a,b,a', 'a,b,b', 'a,e', 'a,e,f']
    assert dictlabels["a,b,a"].name == "a,b,a"
    
    print("With name_recusive=False")
    root, dictlabels = hierarchicalsoftmax_get_dictlabels(label_list, name_recusive=False)
    print(dictlabels)
    assert root.render_equal("""
        root
        ├── a
        │   ├── a
        │   ├── b
        │   │   ├── a
        │   │   └── b
        │   ├── c
        │   ├── d
        │   └── e
        │       └── f
        └── b
            ├── a
            └── b
        """,
        print=True,
    )
    assert list(dictlabels.keys()) == ['a', 'a,a', 'a,b', 'a,c', 'a,d', 'b', 'b,a', 'b,b', 'a,b,a', 'a,b,b', 'a,e', 'a,e,f']
    assert dictlabels["a,b,a"].name == "a"



def test_hiearsoftmax_train():
    """
            # pip install hierarchicalsoftmax

            ### Hierachy Label
            # root = SoftmaxNode("root") # str or number
            # a = SoftmaxNode("a", parent=root)
            # aa = SoftmaxNode("aa", parent=a)
            # ab = SoftmaxNode("ab", parent=a)
            # b = SoftmaxNode("b", parent=root)
            # ba = SoftmaxNode("ba", parent=b)
            # bb = SoftmaxNode("bb", parent=b)

            # dictlabels ={
            #     'a' : SoftmaxNode("a", parent=root),
            #     'a,a' : SoftmaxNode("aa", parent=a),
            #     'a,b' : SoftmaxNode("ab", parent=a),
            #     'b' :  SoftmaxNode("b", parent=root),
            #     'b,a' : SoftmaxNode("ba", parent=b),
            #     'b,b' : SoftmaxNode("bb", parent=b)
            # }
            # ###############################################
                # hierarchical softmax tree Label output
                # root

                # ├── a           label 0 
                # │   ├── aa      label 2
                # │   └── ab      label 3
                # └── b           label 1
                #     ├── ba      label 4
                #     └── bb      label 5

                Output logs
                ```
            Some weights of DebertaV2ForSequenceClassificationHieraSoftmax were not initialized from the model checkpoint at microsoft/deberta-v3-small and are newly initialized: ['hidden_layer.bias', 'hidden_layer.weight', 'softmax.bias', 'softmax.weight']
            You should probably TRAIN this model on a down-stream task to be able to use it for predictions and inference.
            /home/kryo/miniconda3/envs/py38/lib/python3.8/site-packages/transformers/convert_slow_tokenizer.py:562: UserWarning: The sentencepiece tokenizer that you are converting to a fast tokenizer uses the byte fallback option which is not implemented in the fast tokenizers. In practice this means that the fast version of the tokenizer can produce unknown tokens whereas the sentencepiece version would have converted these unknown tokens into a sequence of byte tokens matching the original piece of text.
            warnings.warn(
            Map: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 200/200 [00:00<00:00, 15172.29 examples/s]
            Parameter 'function'=<function test20.<locals>.map_batch_mock_str_label_to_node_id at 0x7dca58fad4c0> of the transform datasets.arrow_dataset.Dataset._map_single couldn't be hashed properly, a random hash was used instead. Make sure your transforms and parameters are serializable with pickle or dill for the dataset fingerprinting and caching to work. If you reuse this transform, the caching mechanism will consider it to be different from the previous calls and recompute everything. This warning is only showed once. Subsequent hashing failures won't be showed.
            Map: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 200/200 [00:00<00:00, 71550.73 examples/s]
            Map:   0%|                                                                                                                                    | 0/1000 [00:00<?, ? examples/s]Asking to pad to max_length but no maximum length is provided and the model has no predefined maximum length. Default to no padding.
            Asking to truncate to max_length but no maximum length is provided and the model has no predefined maximum length. Default to no truncation.
            Map: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 200/200 [00:00<00:00, 5070.91 examples/s]
            {'loss': 1.0495, 'grad_norm': 7.613245487213135, 'learning_rate': 1.0000000000000002e-06, 'epoch': 0.01}                                                                      
            {'loss': 0.9376, 'grad_norm': 10.208002090454102, 'learning_rate': 2.0000000000000003e-06, 'epoch': 0.02}                                                                     
            {'loss': 1.1451, 'grad_norm': 12.561912536621094, 'learning_rate': 3e-06, 'epoch': 0.03}                                                                                      
                                                                        
            {'loss': 0.5719, 'grad_norm': 10.60204792022705, 'learning_rate': 2.3000000000000003e-05, 'epoch': 0.23}                                                                      
                                                                                
            {'loss': 0.3359, 'grad_norm': 0.06052033603191376, 'learning_rate': 6e-06, 'epoch': 0.94}                                                                                     
            {'loss': 0.4804, 'grad_norm': 5.339478969573975, 'learning_rate': 5e-06, 'epoch': 0.95}                                                                                                                                                          
            {'loss': 0.3288, 'grad_norm': 6.555310249328613, 'learning_rate': 1.0000000000000002e-06, 'epoch': 0.99}                                                                      
            {'loss': 1.164, 'grad_norm': 5.721235275268555, 'learning_rate': 0.0, 'epoch': 1.0}                                                                                           
            {'train_runtime': 166.9352, 'train_samples_per_second': 5.99, 'train_steps_per_second': 5.99, 'train_loss': 0.6256246494054795, 'epoch': 1.0}                                 
            100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1000/1000 [02:46<00:00,  5.99it/s]
            100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 200/200 [00:39<00:00,  5.01it/s]
            {'eval_loss': 0.5683719515800476, 'eval_accuracy': 0.3449999988079071, 'eval_f1': 0.17100371747211895, 'eval_runtime': 40.1048, 'eval_samples_per_second': 4.987, 'eval_steps_per_second': 4.987, 'epoch': 1.0}
            [b,b]
            tensor([[1.2572e-03, 9.9874e-01, 8.0601e-04, 4.5119e-04, 2.3171e-01, 7.6703e-01]],
                grad_fn=<CopySlices>)
                ```
    """

    label_list = ["a", "b", "a,a", "a,b", "b,a", "b,b"]
    root, dictlabels = hierarchicalsoftmax_get_dictlabels(label_list)
    pos_label_list = ["a", "a,a", "a,b"]
    neg_label_list = ["b", "b,a", "b,b"]

    ###### model
    model_name = "microsoft/deberta-v3-small"
    model = DebertaV2ForSequenceClassificationHieraSoftmax.from_pretrained(model_name, root=root, freeze_deberta=True)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # dataset
    dataset = load_dataset('imdb')
    dataset['train'] = dataset['train'].select([random.randint(0, len(dataset)) for i in range(1000)])
    dataset['test'] = dataset['test'].select([random.randint(0, len(dataset)) for i in range(200)])
    del dataset['unsupervised']

    ### Generate Mock Labels 'a', 'a,a', 'a,b', ...
    # Rename the original 'label' column because direct mapping 'label' to 'label' column has no effect
    dataset = dataset.rename_column('label', 'real_label') 
    def map_real_to_mock_str_label(x):
        """
        Map column 'real_label' (int) {0, 1} to 'mock_label' {'a', 'aa', ...} (str)

        Generate mock label is necessary to test training with hierarchical softmax. 
        Because x['label'] in imdb dataset is ONLY 1 or 0

        We generate mock labels as follows:
            - real_label = 0  ->  Randomly select from ['a', 'a,a', 'a,b']
            - real_label = 1  ->  Randomly select from ['b', 'b,a', 'b,b']
        """
        if x['real_label'] == 1:
            mock_str_label = random.choice(pos_label_list)
        else: # real_label == 0
            mock_str_label = random.choice(neg_label_list)
        x['mock_label'] = mock_str_label
        return x
    def map_batch_mock_str_label_to_node_id(batch):
        """
        Converts a list of string labels to integer IDs for corresponding softmax nodes.
        """
        label_object = [dictlabels.get(label) for label in batch['mock_label']]
        node_ids = root.get_node_ids(label_object)
        batch['label'] = node_ids
        return batch
    dataset = dataset.map(map_real_to_mock_str_label)
    dataset = dataset.map(map_batch_mock_str_label_to_node_id, batched=True) # Be aware that using map with batched=True can cause a stack overflow during debugging with vscode.

    def tokenize_function(examples):
        return tokenizer(examples['text'], padding='max_length', truncation=True)
    tokenized_ds = dataset.map(tokenize_function, batched=True, remove_columns=['text'])


    #### Data collator
    from transformers import DataCollatorWithPadding
    collator = DataCollatorWithPadding(tokenizer=tokenizer, padding="longest")

    ### metrics
    # Use metric from hierarchicalsoftmax library
    from hierarchicalsoftmax.metrics import (
        greedy_accuracy, 
        greedy_f1_score, 
        greedy_accuracy_depth_one, 
        greedy_accuracy_depth_two,
        greedy_accuracy_parent,
        greedy_precision,
        greedy_recall,
    )
    def compute_metrics(pred):
        labels = torch.from_numpy(pred.label_ids)
        preds = torch.from_numpy(pred.predictions)
        acc = greedy_accuracy(preds, labels, root=root)
        f1 = greedy_f1_score(preds, labels, root=root)
        return {"accuracy": acc, "f1": f1}

    # training
    training_args = TrainingArguments(
        output_dir="./ztmp/results",
        num_train_epochs=1,
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir='./ztmp/results/logs',
        logging_steps=10,
    )
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_ds["train"],
        eval_dataset=tokenized_ds["test"],
        compute_metrics=compute_metrics,
        data_collator=collator,
        tokenizer=tokenizer,
    )
    trainer.train()

    ### Evaluation
    print(trainer.evaluate())

    ### Inference
    # Convert prediction probality to node name, node probability, ...
    from hierarchicalsoftmax.inference import (
        greedy_predictions,
        node_probabilities, 
        leaf_probabilities,
        render_probabilities,
    )
    inputs = tokenizer(["How are you?"], padding=True, truncation=True, return_tensors="pt")
    predictions = model(**inputs)['logits']
    print(greedy_predictions(prediction_tensor=predictions, root=root, max_depth=2))
    print(node_probabilities(prediction_tensor=predictions, root=root))



class DebertaV2ForSequenceClassificationHieraSoftmax(DebertaV2PreTrainedModel):
    """
    This class extends the `DebertaV2PreTrainedModel` and incorporates hierarchical softmax for classification tasks 
    where labels are organized in a hierarchical structure.
    """
    def __init__(self, config, root, freeze_deberta=True):
        """
        Args:
            config (PretrainedConfig): The configuration object for the DeBERTaV2 model.
            root (SoftmaxNode): The root node of the hierarchical softmax structure.
            freeze_deberta (bool, optional): If True, the DeBERTa layers are frozen during training to only train the 
                classification head. Default is True.
        """
        super().__init__(config)
        self.root = root

        self.deberta = DebertaV2Model(config)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)

        # Define the hierarchical softmax layers
        self.hidden_layer = nn.Linear(config.hidden_size, config.hidden_size // 2)
        self.activation = nn.ReLU()

        self.softmax = HierarchicalSoftmaxLinear(
            in_features=config.hidden_size // 2, 
            root=self.root
        )

        # Freeze the Deberta layers if specified
        if freeze_deberta:
            for param in self.deberta.parameters():
                param.requires_grad = False

        self.init_weights()

    def forward(
        self,
        input_ids=None,
        attention_mask=None,
        token_type_ids=None,
        position_ids=None,
        inputs_embeds=None,
        labels=None, # new
        output_attentions=None,
        output_hidden_states=None,
        return_dict=None,
    ):
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict

        outputs = self.deberta(
            input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )

        pooled_output = outputs[0][:, 0, :]
        pooled_output = self.dropout(pooled_output)

        hidden_output = self.activation(self.hidden_layer(pooled_output))
        logits = self.softmax(hidden_output)

        loss = None
        if labels is not None:
            criterion = HierarchicalSoftmaxLoss(root=self.root)
            loss = criterion(logits, labels)

        if not return_dict:
            output = (logits,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output

        return SequenceClassifierOutput(
            loss=loss,
            logits=logits,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
        )



class HierarchicalSoftmaxTextClassificationPipeline(TextClassificationPipeline):
    """
    A custom text classification pipeline that integrates hierarchical softmax.
    
    The output of this pipeline is the probability distribution over the LEAF NODES of the hierarchy, 
    rather than over a flat set of labels.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.leaf_ids = self.model.root.leaf_indexes_in_softmax_layer.tolist()
        self.leaf_labels = [self.model.config.id2label[i] for i in self.leaf_ids]

    def postprocess(self, model_outputs, function_to_apply=None, top_k=1, _legacy=True):
        logrits = model_outputs['logits']
        leaf_scores = leaf_probabilities(prediction_tensor=logrits, root=self.model.root).float().numpy()

        if top_k == 1 and _legacy:
            return {"label": self.leaf_labels[leaf_scores.argmax().item()], "score": leaf_scores.max().item()}

        dict_scores = [
            {"label": self.leaf_labels[i], "score": score.item()} for i, score in enumerate(leaf_scores)
        ]
        if not _legacy:
            dict_scores.sort(key=lambda x: x["score"], reverse=True)
            if top_k is not None:
                dict_scores = dict_scores[:top_k]
        return dict_scores



def hierarchicalsoftmax_get_dictlabels(label_list, sep=",", name_recusive=True):
    """
    Generates a dictionary of SoftmaxNode objects with nested parent-child 
    relationships based on a list of labels.

    Args:
        label_list (list[str]): A list of comma-separated labels representing the hierarchy. 
                                Example: ["a,a", "a,b", "b,a", "b,b"]
        sep (str): The separator used in the labels. Default is ",".
        name_recusive (bool): A flag to determine how node names are generated.
                                - If True, the full recursive name (e.g., "a,b,a") will be used.
                                - If False, only the current part of the label (e.g., "a") will be used.

    Returns:
        root (SoftmaxNode): The root node of the hierarchy.
        dictlabels (dict[str, SoftmaxNode]): A dictionary where the keys are the labels from the input list,
                                                            and the values are the corresponding SoftmaxNode objects.
    """
    root = SoftmaxNode("root")
    node_dict = {"root": root}

    for label in label_list:
        parts = label.split(sep)
        parent_node = root
        current_parts = []
        for i, part in enumerate(parts):
            current_parts.append(part)
            current_label = sep.join(parts[:i+1])
            if current_label not in node_dict:
                if name_recusive:
                    node_dict[current_label] = SoftmaxNode(sep.join(current_parts), parent=parent_node)
                else:
                    node_dict[current_label] = SoftmaxNode(part, parent=parent_node)
            parent_node = node_dict[current_label]

        # dictlabels = node_dict without root
        dictlabels = {k: v for k, v in node_dict.items() if k != "root"}

    return root, dictlabels






################################################################################################
###### Run hierchical softmax ##################################################################
def run_train_hiear(istest=1, dirout="./ztmp/exp/L1_cat/v3deber/" ):
    """
    Tests finetune "MoritzLaurer/deberta-v3-large-zeroshot-v2.0" with df_news_100.parquet dataset 
            
            Output logs:
            ```
            Some weights of DebertaV2ForSequenceClassificationHieraSoftmax were not initialized from the model checkpoint at MoritzLaurer/deberta-v3-large-zeroshot-v2.0 and are newly initialized: ['hidden_layer.bias', 'hidden_layer.weight', 'softmax.bias', 'softmax.weight']
            You should probably TRAIN this model on a down-stream task to be able to use it for predictions and inference.
            Parameter 'function'=<function test23.<locals>.map_batch_mock_str_label_to_node_id at 0x7db5c657cd30> of the transform datasets.arrow_dataset.Dataset._map_single couldn't be hashed properly, a random hash was used instead. Make sure your transforms and parameters are serializable with pickle or dill for the dataset fingerprinting and caching to work. If you reuse this transform, the caching mechanism will consider it to be different from the previous calls and recompute everything. This warning is only showed once. Subsequent hashing failures won't be showed.
            Map: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████| 100/100 [00:00<00:00, 20055.97 examples/s]
            cuda available: False
            mps available: False
            set torch_device= cpu
            {'loss': 4.1912, 'grad_norm': 19.6280574798584, 'learning_rate': 4.9e-05, 'epoch': 0.1}                                                                         
            {'loss': 3.9375, 'grad_norm': 15.339924812316895, 'learning_rate': 4.8e-05, 'epoch': 0.2}                                                                       
            {'loss': 4.11, 'grad_norm': 19.279611587524414, 'learning_rate': 4.7e-05, 'epoch': 0.3}                                                                         
            {'loss': 4.5177, 'grad_norm': 19.70623779296875, 'learning_rate': 4.600000000000001e-05, 'epoch': 0.4}                                                                                                             
            {'loss': 3.5218, 'grad_norm': 20.66583251953125, 'learning_rate': 2.7000000000000002e-05, 'epoch': 2.3}                                                         
            {'loss': 3.8078, 'grad_norm': 23.79869270324707, 'learning_rate': 2.6000000000000002e-05, 'epoch': 2.4}                                                         
            {'loss': 3.5961, 'grad_norm': 18.601728439331055, 'learning_rate': 2.5e-05, 'epoch': 2.5}                                                                       
            50%|████████████████████████████████████████████████████████████▌                                                            | 250/500 [10:47<10:50,  2.60s/it]./ztmp/test23/train/checkpoint-250/meta_metrics.json
            ./ztmp/test23/train/checkpoint-250/meta.json
            Saved custom info to ./ztmp/test23/train/checkpoint-250
            {'loss': 3.2502, 'grad_norm': 15.718549728393555, 'learning_rate': 2.4e-05, 'epoch': 2.6}                                                                       
            {'loss': 3.8183, 'grad_norm': 16.629619598388672, 'learning_rate': 2.3000000000000003e-05, 'epoch': 2.7}                                                        
            {'loss': 3.545, 'grad_norm': 19.5266056060791, 'learning_rate': 2.2000000000000003e-05, 'epoch': 2.8}                                                           
                                                                
            {'loss': 3.5676, 'grad_norm': 17.472484588623047, 'learning_rate': 4.000000000000001e-06, 'epoch': 4.6}                                                         
            {'loss': 3.302, 'grad_norm': 24.410125732421875, 'learning_rate': 3e-06, 'epoch': 4.7}                                                                          
            {'loss': 3.6555, 'grad_norm': 17.18182373046875, 'learning_rate': 2.0000000000000003e-06, 'epoch': 4.8}                                                         
            {'loss': 3.6307, 'grad_norm': 18.987489700317383, 'learning_rate': 1.0000000000000002e-06, 'epoch': 4.9}                                                        
            {'loss': 3.2856, 'grad_norm': 15.010137557983398, 'learning_rate': 0.0, 'epoch': 5.0}                                                                           
            100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 500/500 [22:03<00:00,  2.68s/it]./ztmp/test23/train/checkpoint-500/meta_metrics.json
            ./ztmp/test23/train/checkpoint-500/meta.json
            Saved custom info to ./ztmp/test23/train/checkpoint-500
            {'train_runtime': 1336.5084, 'train_samples_per_second': 0.374, 'train_steps_per_second': 0.374, 'train_loss': 3.638541202545166, 'epoch': 5.0}                 
            100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 500/500 [22:16<00:00,  2.67s/it]
            ```
    """

    # config
    cc = Box({})


    if "cc params":
        #cc.checkpoint = dirout +'/train/checkpoint-500'     
        cc.checkpoint = None

        cc.dirout = "./ztmp/test23"
        cc.dirdata = "./ztmp/df_news_100.parquet"
        cc.epochs     = 5


        cc.model_name = "MoritzLaurer/deberta-v3-large-zeroshot-v2.0"
        #cc.model_name = model_name
        cc.problem_type = HFproblemtype.SEQUENCE_CLASSIFICATION
        cc.task    = HFtask.text_classification

        cc.device  = torch_device("cpu")

        cc.max_length = 1024

        cc.save_steps = 250
        cc.eval_steps = 0


        cc.dirout_checkpoint = cc.dirout + "/train"
        cc.dirout_log = cc.dirout + "/log"
        cc.dirout_model = cc.dirout + "/model"

        # Train Args
        cc.hf_args_train = Box({})
        cc.hf_args_train.output_dir = (cc.dirout_checkpoint,)
        cc.hf_args_train.num_train_epochs = (cc.epochs,)
        cc.hf_args_train.logging_dir = (cc.dirout_log,)
        cc.hf_args_train.save_steps = (cc.save_steps,)
        cc.hf_args_train.eval_steps = (cc.eval_steps,)

        # Model Args
        cc.hf_args_model = Box({})
        cc.hf_args_model.model_name = cc.model_name
        cc.hf_args_model.problem_type = cc.problem_type

        os_makedirs(cc.dirout_log)
        os_makedirs(cc.dirout_checkpoint)
        os_makedirs(cc.dirout_model)



    # dataset load + transform
    dataset = load_dataset("parquet", data_files=cc.dirdata )
    dataset = dataset.map(lambda x: {"label": f"{x['pred-L1_cat']} - {x['pred-L2_cat']} - {x['pred-L3_cat']}"})
    dataset = dataset.remove_columns(["__index_level_0__", "pred-L1_cat", "pred-L2_cat", "pred-L3_cat", "pred-L4_cat", "L0_catnews", "com_extract", 'text_com', 'text_summary', 'text_tags', 'title', 'url'])
    dataset = dataset['train'].train_test_split(test_size=0.2)

    # hierarchicalsoftmax label
    label_list = list(set(dataset['train']['label']) | set(dataset['test']['label'])) # Union of train and test labels here because num of samples is small
    root, dictlabels = hierarchicalsoftmax_get_dictlabels(label_list, sep=" - ", name_recusive=True)
    label2id = dict(zip(dictlabels.keys(), root.get_node_ids(dictlabels.values())))
    id2label = {y: x for x, y in label2id.items()}

    # Add some dataset related info into the cc config
    cc.n_train = len(dataset['train'])
    cc.n_val   = len(dataset['test'])
    cc.label2key = label2id
    cc.key2label = id2label

    log("\n###################load tokenizers #############################")
    tokenizer= AutoTokenizer.from_pretrained(cc.model_name)
    # dataset tokenize, map label
    def tokenize_function(examples):
        return tokenizer(examples["text"], padding="max_length", truncation=True)
    dataset = dataset.map(tokenize_function, batched=True)

    def map_batch_mock_str_label_to_node_id(batch):
        """
        Converts a list of string labels to integer IDs for corresponding softmax nodes.
        """
        label_object = [dictlabels.get(label) for label in batch['label']]
        node_ids = root.get_node_ids(label_object)
        batch['label'] = node_ids
        return batch
    dataset = dataset.map(map_batch_mock_str_label_to_node_id, batched=True) # Be aware that using map with batched=True can cause a stack overflow during debugging with vscode.


    #### Data collator
    from transformers import DataCollatorWithPadding
    collator = DataCollatorWithPadding(tokenizer=tokenizer, padding="longest")



    log("\n###################load model #############################")
    model    = DebertaV2ForSequenceClassificationHieraSoftmax.from_pretrained(
        cc.model_name, 
        root=root, 
        freeze_deberta=True,
        label2id=label2id,
        id2label=id2label,
    )
    model.config.max_position_embeddings = cc.max_length ### Force the max_length



    ### Metrics: Use metric from hierarchicalsoftmax library
    def compute_metrics(pred):
        labels = torch.from_numpy(pred.label_ids)
        preds  = torch.from_numpy(pred.predictions)
        acc    = greedy_accuracy(preds, labels, root=root)
        f1     = greedy_f1_score(preds, labels, root=root)
        return {"accuracy": acc, "f1": f1}


    # training
    ##### Set up training
    # args    = TrainingArguments(**cc.hf_args_train )

    args = TrainingArguments(
        output_dir=cc.dirout_checkpoint,
        num_train_epochs=cc.epochs,
        per_device_train_batch_size=1,
        logging_dir=cc.dirout_log,
        logging_steps=10,
        save_strategy="steps",
        save_steps=cc.save_steps,
        # evaluation_strategy="steps",
        # eval_steps=cc.eval_steps,
    )

    trainer = Trainer(
        model=model,
        args=args,
        tokenizer=tokenizer,
        train_dataset=dataset["train"],
        eval_dataset=dataset["test"],
        compute_metrics=compute_metrics,
        data_collator=collator,
        callbacks=[CallbackCSaveheckpoint(cc)]
    )
    # trainer.train()



    log("\n###################Train: start #############################")
    cc_save(cc, cc.dirout) 
    log("#### Checkpoint: ", cc.checkpoint)
    trainer_out = trainer.train(resume_from_checkpoint= cc.checkpoint)

    # hf_save_checkpoint(trainer,  f"{cc.dirout}/model", cc )
    evals = trainer.evaluate()
    cc['trainer_eval']    = str(evals)
    cc['trainer_metrics'] = trainer_out.metrics
    cc_save(cc, cc.dirout)
    del trainer; del model; gc.collect()






def run_infer_hiearchi():
    """
    hierarchicalsoftmax_sequence_classification evaluation
    
    Output logs:
    ```
    The model 'DebertaV2ForSequenceClassificationHieraSoftmax' is not supported for . Supported models are ['AlbertForSequenceClassification', 'BartForSequenceClassification', 'BertForSequenceClassification', 'BigBirdForSequenceClassification', 'BigBirdPegasusForSequenceClassification', 'BioGptForSequenceClassification', 'BloomForSequenceClassification', 'CamembertForSequenceClassification', 'CanineForSequenceClassification', 'LlamaForSequenceClassification', 'ConvBertForSequenceClassification', 'CTRLForSequenceClassification', 'Data2VecTextForSequenceClassification', 'DebertaForSequenceClassification', 'DebertaV2ForSequenceClassification', 'DistilBertForSequenceClassification', 'ElectraForSequenceClassification', 'ErnieForSequenceClassification', 'ErnieMForSequenceClassification', 'EsmForSequenceClassification', 'FalconForSequenceClassification', 'FlaubertForSequenceClassification', 'FNetForSequenceClassification', 'FunnelForSequenceClassification', 'GemmaForSequenceClassification', 'Gemma2ForSequenceClassification', 'GPT2ForSequenceClassification', 'GPT2ForSequenceClassification', 'GPTBigCodeForSequenceClassification', 'GPTNeoForSequenceClassification', 'GPTNeoXForSequenceClassification', 'GPTJForSequenceClassification', 'IBertForSequenceClassification', 'JambaForSequenceClassification', 'JetMoeForSequenceClassification', 'LayoutLMForSequenceClassification', 'LayoutLMv2ForSequenceClassification', 'LayoutLMv3ForSequenceClassification', 'LEDForSequenceClassification', 'LiltForSequenceClassification', 'LlamaForSequenceClassification', 'LongformerForSequenceClassification', 'LukeForSequenceClassification', 'MarkupLMForSequenceClassification', 'MBartForSequenceClassification', 'MegaForSequenceClassification', 'MegatronBertForSequenceClassification', 'MistralForSequenceClassification', 'MixtralForSequenceClassification', 'MobileBertForSequenceClassification', 'MPNetForSequenceClassification', 'MptForSequenceClassification', 'MraForSequenceClassification', 'MT5ForSequenceClassification', 'MvpForSequenceClassification', 'NezhaForSequenceClassification', 'NystromformerForSequenceClassification', 'OpenLlamaForSequenceClassification', 'OpenAIGPTForSequenceClassification', 'OPTForSequenceClassification', 'PerceiverForSequenceClassification', 'PersimmonForSequenceClassification', 'PhiForSequenceClassification', 'Phi3ForSequenceClassification', 'PLBartForSequenceClassification', 'QDQBertForSequenceClassification', 'Qwen2ForSequenceClassification', 'Qwen2MoeForSequenceClassification', 'ReformerForSequenceClassification', 'RemBertForSequenceClassification', 'RobertaForSequenceClassification', 'RobertaPreLayerNormForSequenceClassification', 'RoCBertForSequenceClassification', 'RoFormerForSequenceClassification', 'SqueezeBertForSequenceClassification', 'StableLmForSequenceClassification', 'Starcoder2ForSequenceClassification', 'T5ForSequenceClassification', 'TapasForSequenceClassification', 'TransfoXLForSequenceClassification', 'UMT5ForSequenceClassification', 'XLMForSequenceClassification', 'XLMRobertaForSequenceClassification', 'XLMRobertaXLForSequenceClassification', 'XLNetForSequenceClassification', 'XmodForSequenceClassification', 'YosoForSequenceClassification'].
    Token indices sequence length is longer than the specified maximum sequence length for this model (534 > 512). Running this sequence through the model will result in indexing errors
    Block 0. Pred: {'label': 'sales and marketing - sales tech - sales engagement platforms', 'scor
    Block 8. Pred: {'label': 'sales and marketing - martech - marketing automation', 'score': 0.092
    Npred: 16 50.32117056846619

    ################### Start Label Mapping ###########################
        label_idx  label_idx
    0          78         78
    1          60         60
    2          87         87
    3          82         82
    4          70         70
    5          83         83
    6          87         87
    7          57         57
    8          30         30
    9          78         78
    10         87         87
    11         70         70
    12         38         38
    13         77         77
    14         38         38
    15         56         56
                                                    label                                               pred
    0   information technology - computing - cloud opt...  sales and marketing - sales tech - sales engag...
    1        work - insurtech - insurtech: infrastructure  sales and marketing - martech - marketing auto...
    2   sales and marketing - sales tech - sales engag...  sales and marketing - martech - marketing auto...
    3   energy and climate change - computing - data i...  sales and marketing - martech - marketing auto...
    4   security - digital security - next-gen cyberse...  sales and marketing - martech - marketing auto...
    5   energy and climate change - specialty care - c...  sales and marketing - martech - marketing auto...
    6   sales and marketing - sales tech - sales engag...  sales and marketing - martech - marketing auto...
    7   work - virtual workplace - remote work infrast...  sales and marketing - martech - marketing auto...
    8   financial services - wealth tech - retail trad...  sales and marketing - martech - marketing auto...
    9   information technology - computing - cloud opt...  sales and marketing - martech - marketing auto...
    10  sales and marketing - sales tech - sales engag...  sales and marketing - martech - marketing auto...
    11  security - digital security - next-gen cyberse...  sales and marketing - martech - marketing auto...
    12  hospitality and travel - travel and tourism - ...  sales and marketing - martech - marketing auto...
    13  information technology - computing - machine l...  sales and marketing - martech - marketing auto...
    14  hospitality and travel - travel and tourism - ...  sales and marketing - martech - marketing auto...
    15  work - work automation - workflow automation p...  sales and marketing - martech - marketing auto...
    ./ztmp/test23/df_pred_16.parquet
                                                    text  label_idx  ...                                              label                                               pred
    0   Chicago, IL, August 01, 2024 --( PR.com )-- Cr...         78  ...  information technology - computing - cloud opt...  sales and marketing - sales tech - sales engag...
    1   Bloomberg Law recognized White & Case partner ...         60  ...       work - insurtech - insurtech: infrastructure  sales and marketing - martech - marketing auto...
    2   Microsoft is now a month into its fiscal 2025,...         87  ...  sales and marketing - sales tech - sales engag...  sales and marketing - martech - marketing auto...
    3   RICHMOND, VIRGINIA, UNITED STATES, July 29, 20...         82  ...  energy and climate change - computing - data i...  sales and marketing - martech - marketing auto...
    4   UK-based professional services firm PwC's Indi...         70  ...  security - digital security - next-gen cyberse...  sales and marketing - martech - marketing auto...
    5   FluxGen Sustainable Technologies, a provider o...         83  ...  energy and climate change - specialty care - c...  sales and marketing - martech - marketing auto...
    6   CallTower has partnered with Tollring on its A...         87  ...  sales and marketing - sales tech - sales engag...  sales and marketing - martech - marketing auto...
    7   Embee Software is proud to announce that it ha...         57  ...  work - virtual workplace - remote work infrast...  sales and marketing - martech - marketing auto...
    8   Typically, stocks trading below $5 per share a...         30  ...  financial services - wealth tech - retail trad...  sales and marketing - martech - marketing auto...
    9   Microsoft and Lumen Technologies have partnere...         78  ...  information technology - computing - cloud opt...  sales and marketing - martech - marketing auto...
    10  Microsoft is now a month into its fiscal 2025,...         87  ...  sales and marketing - sales tech - sales engag...  sales and marketing - martech - marketing auto...
    11  In a world where cyber threats are constantly ...         70  ...  security - digital security - next-gen cyberse...  sales and marketing - martech - marketing auto...
    12  With its massive traffic, incredible insights ...         38  ...  hospitality and travel - travel and tourism - ...  sales and marketing - martech - marketing auto...
    13  \n• The U.K.'s Competition and Markets Authori...         77  ...  information technology - computing - machine l...  sales and marketing - martech - marketing auto...
    14  With its massive traffic, incredible insights ...         38  ...  hospitality and travel - travel and tourism - ...  sales and marketing - martech - marketing auto...
    15  BONIFACIO GLOBAL CITY, PHILIPPINES, July 29, 2...         56  ...  work - work automation - workflow automation p...  sales and marketing - martech - marketing auto...

    [16 rows x 5 columns]
    ./ztmp/test23/df_pred_sample.csv

    ################### Start Metrics ##########################
    /home/kryo/miniconda3/envs/py38/lib/python3.8/site-packages/sklearn/metrics/_classification.py:1471: UndefinedMetricWarning: Precision and F-score are ill-defined and being set to 0.0 in labels with no predicted samples. Use `zero_division` parameter to control this behavior.
    _warn_prf(average, modifier, msg_start, len(result))
    /home/kryo/miniconda3/envs/py38/lib/python3.8/site-packages/sklearn/metrics/_classification.py:1471: UndefinedMetricWarning: Recall and F-score are ill-defined and being set to 0.0 in labels with no true samples. Use `zero_division` parameter to control this behavior.
    _warn_prf(average, modifier, msg_start, len(result))
    /home/kryo/miniconda3/envs/py38/lib/python3.8/site-packages/sklearn/metrics/_classification.py:1471: UndefinedMetricWarning: Precision and F-score are ill-defined and being set to 0.0 in labels with no predicted samples. Use `zero_division` parameter to control this behavior.
    _warn_prf(average, modifier, msg_start, len(result))
    /home/kryo/miniconda3/envs/py38/lib/python3.8/site-packages/sklearn/metrics/_classification.py:1471: UndefinedMetricWarning: Recall and F-score are ill-defined and being set to 0.0 in labels with no true samples. Use `zero_division` parameter to control this behavior.
    _warn_prf(average, modifier, msg_start, len(result))
    /home/kryo/miniconda3/envs/py38/lib/python3.8/site-packages/sklearn/metrics/_classification.py:1471: UndefinedMetricWarning: Precision and F-score are ill-defined and being set to 0.0 in labels with no predicted samples. Use `zero_division` parameter to control this behavior.
    _warn_prf(average, modifier, msg_start, len(result))
    /home/kryo/miniconda3/envs/py38/lib/python3.8/site-packages/sklearn/metrics/_classification.py:1471: UndefinedMetricWarning: Recall and F-score are ill-defined and being set to 0.0 in labels with no true samples. Use `zero_division` parameter to control this behavior.
    _warn_prf(average, modifier, msg_start, len(result))
                                                                                            precision    recall  f1-score   support

            transportation and logistics - distribution and logistics - truck industry tech     0.0000    0.0000    0.0000       0.0
                    transportation and logistics - distribution and logistics - edtech: k-12     0.0000    0.0000    0.0000       0.0
                    financial services - fintech banking and infra - fintech infrastructure     0.0000    0.0000    0.0000       0.0
                financial services - fintech banking and infra - business expense management     0.0000    0.0000    0.0000       0.0
                                    financial services - fintech banking and infra - neobanks     0.0000    0.0000    0.0000       0.0
                                    financial services - fintech payments - digital wallets     0.0000    0.0000    0.0000       0.0
                        financial services - fintech payments - business expense management     0.0000    0.0000    0.0000       0.0
                            financial services - fintech payments - fintech infrastructure     0.0000    0.0000    0.0000       0.0
                                financial services - fintech payments - biometric payments     0.0000    0.0000    0.0000       0.0
                                            financial services - primary care - travel tech     0.0000    0.0000    0.0000       0.0
                            financial services - wealth tech - retail trading infrastructure     0.0000    0.0000    0.0000       1.0
                                    financial services - wealth tech - capital markets tech     0.0000    0.0000    0.0000       0.0
                                                financial services - sales tech - neobanks     0.0000    0.0000    0.0000       0.0
                        financial services - digital retail - retail trading infrastructure     0.0000    0.0000    0.0000       0.0
                                financial services - martech - retail trading infrastructure     0.0000    0.0000    0.0000       0.0
                                    financial services - computing - cloud optimization tools     0.0000    0.0000    0.0000       0.0
                                    hospitality and travel - travel and tourism - travel tech     0.0000    0.0000    0.0000       2.0
                            hospitality and travel - food service tech - online food delivery     0.0000    0.0000    0.0000       0.0
                                    sports and entertainment - digital sports - sports tech     0.0000    0.0000    0.0000       0.0
                                        sports and entertainment - digital sports - esports     0.0000    0.0000    0.0000       0.0
                            sports and entertainment - computing - next-gen mobile networks     0.0000    0.0000    0.0000       0.0
                        sports and entertainment - digital entertainment - extended reality     0.0000    0.0000    0.0000       0.0
                                    sports and entertainment - work automation - sports tech     0.0000    0.0000    0.0000       0.0
                                        work - computing - machine learning infrastructure     0.0000    0.0000    0.0000       0.0
                                    work - work automation - workflow automation platforms     0.0000    0.0000    0.0000       1.0
                                        work - virtual workplace - remote work infrastructure     0.0000    0.0000    0.0000       1.0
                                    work - fintech banking and infra - fintech infrastructure     0.0000    0.0000    0.0000       0.0
                                            work - digital security - next-gen cybersecurity     0.0000    0.0000    0.0000       0.0
                                                work - insurtech - insurtech: infrastructure     0.0000    0.0000    0.0000       1.0
    education and public services - environmental services - waste recovery & management tech     0.0000    0.0000    0.0000       0.0
                        education and public services - environmental services - food waste     0.0000    0.0000    0.0000       0.0
                            education and public services - educational tech - higher edtech     0.0000    0.0000    0.0000       0.0
                education and public services - educational tech - edtech: corporate learning     0.0000    0.0000    0.0000       0.0
                                        security - digital security - next-gen cybersecurity     0.0000    0.0000    0.0000       2.0
                                                security - computing - next-gen cybersecurity     0.0000    0.0000    0.0000       0.0
                                        security - physical security - residential proptech     0.0000    0.0000    0.0000       0.0
                                        information technology - computing - edge computing     0.0000    0.0000    0.0000       0.0
                            information technology - computing - generative ai infrastructure     0.0000    0.0000    0.0000       0.0
                        information technology - computing - machine learning infrastructure     0.0000    0.0000    0.0000       1.0
                                information technology - computing - cloud optimization tools     0.0000    0.0000    0.0000       2.0
        information technology - blockchain based computing - enterprise blockchain solutions     0.0000    0.0000    0.0000       0.0
                    energy and climate change - computing - data infrastructure & analytics     0.0000    0.0000    0.0000       1.0
    energy and climate change - specialty care - carbon capture, utilization & storage (ccus)     0.0000    0.0000    0.0000       1.0
                                        sales and marketing - martech - marketing automation     0.0000    0.0000    0.0000       0.0
                                sales and marketing - sales tech - sales engagement platforms     0.0000    0.0000    0.0000       3.0
                                        manufacturing - digital retail - ecommerce platforms     0.0000    0.0000    0.0000       0.0
                                            manufacturing - martech - marketing automation     0.0000    0.0000    0.0000       0.0

                                                                                    micro avg     0.0000    0.0000    0.0000      16.0
                                                                                    macro avg     0.0000    0.0000    0.0000      16.0
                                                                                weighted avg     0.0000    0.0000    0.0000      16.0


    Accuracy: 0.0, 
    F1 Score: 0.0
    ./ztmp/test23/meta.json
    ```
    """
    # dataset load + transform
    dir_checkpoint = "ztmp/test23/train/checkpoint-250"
    dirdata        = "./ztmp/df_news_100.parquet"


    batch_size = 4


    dataset = load_dataset("parquet", data_files=dirdata)
    dataset = dataset.map(lambda x: {"label": f"{x['pred-L1_cat']} - {x['pred-L2_cat']} - {x['pred-L3_cat']}"})
    dataset = dataset_remove_columns(dataset, ["__index_level_0__", "pred-L1_cat", "pred-L2_cat", "pred-L3_cat", "pred-L4_cat", "L0_catnews", "com_extract", 'text_com', 'text_summary', 'text_tags', 'title', 'url'])
    dataset = dataset['train'].select(range(16))



    cc = Box(json_load( dir_checkpoint + "/meta.json"))
    label_list = list(cc.label2key.keys())
    label2id   = cc.label2key

    root, dictlabels = hierarchicalsoftmax_get_dictlabels(label_list, sep=" - ", name_recusive=True)

    log("\n################### Load checkpoint  ###############################")  
    tokenizer = AutoTokenizer.from_pretrained(cc.model_name)
    model = DebertaV2ForSequenceClassificationHieraSoftmax.from_pretrained(dir_checkpoint, # cc.model_name,
        root=root, 
        freeze_deberta=True,)
    pipe = HierarchicalSoftmaxTextClassificationPipeline(model=model, tokenizer=tokenizer)
    leaf_labels = pipe.leaf_labels
    leaf_ids    = pipe.leaf_ids


    log("\n################### Start Inference batch #########################")
    ibatch     = batch_size * 2
    t0 = time.time()
    predictions = []
    with torch.no_grad():
        for i in range(0, 1+len(dataset), ibatch):
            res = pipe(dataset["text"][i:i+ibatch], batch_size= batch_size)
            if len(res)< 1: break
            log(f"Block {i}. Pred:", str(res[0])[:80] )
            predictions = predictions + res     
    log('Npred:', len(predictions), time.time()-t0)


    log("\n################### Start Label Mapping ######################")
    if cc.task == HFtask.text_classification:
        pred_labels_top1 = [label2id[pred['label']] for pred in predictions]
        label_ids = [label2id[label] for label in dataset['label']]

        # FIXME: saved cc.key2label has format {'0': 'label', ...}
        cc.key2label = {int(k): v for k, v in cc.key2label.items()}

        dfp = pd.DataFrame({ 
            'text'      : dataset['text'], 
            'label_idx' : label_ids, 
            'pred_idx'  : pred_labels_top1
        })
        
        dfp['label'] = dfp['label_idx'].apply(lambda x : cc.key2label.get(x, "NA") )
        dfp['pred']  = dfp['pred_idx'].apply( lambda x : cc.key2label.get(x, "NA") )

        log(dfp[[ 'label_idx', 'label_idx'  ]]) 
        log(dfp[[ 'label', 'pred'  ]]) 

        pd_to_file(dfp, f"{cc.dirout}/df_pred_{len(dfp)}.parquet", show=1 )
        pd_to_file(dfp.sample(n=30, replace=True), f"{cc.dirout}/df_pred_sample.csv", show=0, sep="\t" )

    log("\n################### Start Metrics ##########################")    
    if "metric":
        true_idx_1D = dfp['label_idx'].values 
        pred_idx_1D = dfp['pred_idx'].values

        accuracy = accuracy_metric.compute(references=true_idx_1D, predictions=pred_idx_1D)['accuracy']
        f1       = f1_metric.compute(references=true_idx_1D, predictions=pred_idx_1D, average='micro')['f1']

        from sklearn.metrics import classification_report
        txt = classification_report(true_idx_1D, pred_idx_1D, 
                                  target_names= leaf_labels,
                                  labels      = leaf_ids,                                            
                                  digits=4)

        txt += f"\n\nAccuracy: {accuracy}, \nF1 Score: {f1}" 
        log(txt)
        cc.metrics = str(txt)
        with open(f"{cc.dirout}/metrics.txt", mode='w') as fp:
            fp.write(txt)

    json_save(cc, f"{cc.dirout}/meta.json")
















########################################################################################
############### NER Label helper #######################################################
class NERdata(object):
    def __init__(self, dirmeta=None, nertag_list=None, token_BOI=None):
        """ Utils to normalize NER data for pandas dataframe


            Args:
                nertag_list (list): list of tags. If not provided, default list of tags is used.
                token_BOI (list): list of token BOI values. If not provided, default list of token BOI values is used.
            Info:

                    - text (str): text.
                    - ner_list (list): List of named entity records. Each named entity record is dict with following keys:
                        - type (str)            : type of named entity.
                        - predictionstring (str): predicted string for named entity.
                        - start (int)           : start position of named entity.
                        - end (int)             : end position of named entity.
                        - text (str)            : text of named entity.
            Append dix;
                    - default list of tags is: ['location', 'city', 'country', 'location_type', 'location_type_exclude']
        """

        ##### dirmeta ###################################################
        self.dirmeta = dirmeta

        #### Class #####################################################################
        tags0 = ['location', 'city', 'country', 'location_type', 'location_type_exclude']
        if nertag_list is None:
            log(f"Using default nertag list inside NERdata.", tags0)
            self.nertag_list = tags0
        else:
            self.nertag_list = nertag_list

            # self.NCLASS       = len(self.tag) # Gpy40 make mistake here
        self.NCLASS = len(self.nertag_list)

        #############################################################################
        #### B-token am I-token, "other" as NA field
        #### We should make sure client provide exactly token_BOI with size 3.
        #### First for begin of words, second for inside and last for other-word.
        token_BOI = ["B", "I", "Other"] if token_BOI is None else token_BOI
        if len(token_BOI) != 3:
            log(f"Please use exactly name of token POI with size 3 for Begin, Inside and other word")
            self.token_BOI = ["B", "I", "Other"]

        self.token_BOI = token_BOI
        self.N_BOI = len(token_BOI) - 1

        #############################################################################
        ### Number of classes for model : B-token, I-token, O-End, + "Other" ####
        self.NCLASS_BOI = self.NCLASS * self.N_BOI + 1

        ### Number of Labels for model : B-token, I-token, O-End, + "Other"  ####
        self.NLABEL_TOTAL = self.NCLASS * 2 + 1  ## due to BOI notation

        ##### Dict mapping ##########################################################
        L2I, I2L, NCLASS = self.create_map_dict()

        self.L2I = L2I  ## Label to Index
        self.I2L = I2L  ## Index to Label
        self.NCLASS = NCLASS  ## NCLASS

        ##### NER record template for data validation ##############################
        self.ner_dataframe_cols = ['text', 'ner_list']
        self.ner_fields = ["start", "end", "class", "value"]

        ##### Meta dict load
        self.meta_dict = self.metadict_init()

    def metadict_save(self, dirmeta=None):
        """ Save json mapper to meta.json
        """
        dirout2 = dirmeta if dirmeta is not None else self.dirmeta
        dirout2 = dirout2 if ".json" in dirout2 else dirout2 + "/meta.json"
        json_save(self.meta_dict, dirout2)
        log(dirout2)
        log(self.meta_dict)

    def metadict_load(self, dirmeta: str = None):
        """Load mapper from directory containing meta.json
        Args: dirmeta (str, optional): directory containing meta.json
        Returns: dict containing all mapping.
        """
        from utilmy import glob_glob
        dirmeta = dirmeta if dirmeta is not None else self.dirmeta
        flist = glob_glob(dirmeta)
        flist = [fi for fi in flist if ".json" in fi.split("/")[-1]]
        fi = flist[0]

        if "json" in fi.split("/")[-1].split(".")[-1]:
            with open(fi, 'r') as f:
                meta_dict = json.load(f)

            meta_dict = Box(meta_dict)
            if "meta_dict" in meta_dict.get("data", {}):
                ### Extract meta_dict from config training
                meta_dict = meta_dict["data"]["meta_dict"]

            self.NLABEL_TOTAL = meta_dict["NLABEL_TOTAL"]
            self.I2L = {int(ii): label for ii, label in meta_dict["I2L"].items()}  ## Force encoding
            self.L2I = {label: int(ii) for label, ii in meta_dict["L2I"].items()}
            self.nertag_list = meta_dict['nertag_list']
            self.dirmeta = fi

            self.meta_dict = meta_dict
            return self.I2L, self.L2I, self.NLABEL_TOTAL, meta_dict
        else:
            log(" need meta.json")

    def metadict_init(self, ):
        dd = Box({})
        dd.nertag_list = self.nertag_list
        dd.NCLASS = self.NCLASS
        dd.NCLASS_BOI = self.NCLASS_BOI
        dd.NLABEL_TOTAL = self.NLABEL_TOTAL
        dd.token_BOI = self.token_BOI
        dd.L2I = self.L2I
        dd.I2L = self.I2L
        dd.ner_fields = self.ner_fields
        dd.ner_dataframe_cols = self.ner_dataframe_cols

        self.meta_dict = dd

    @staticmethod
    def from_meta_dict(meta_dict):
        ner_data_engine = NERdata()
        meta_dict = Box(meta_dict)
        if "meta_dict" in meta_dict.get("data", {}):
            ### Extract meta_dict from config training
            meta_dict = meta_dict["data"]["meta_dict"]

        ner_data_engine.NLABEL_TOTAL = meta_dict["NLABEL_TOTAL"]
        ner_data_engine.I2L = {int(ii): label for ii, label in meta_dict["I2L"].items()}  ## Force encoding
        ner_data_engine.L2I = {label: int(ii) for label, ii in meta_dict["L2I"].items()}
        ner_data_engine.nertag_list = meta_dict['nertag_list']
        ner_data_engine.meta_dict = meta_dict
        return ner_data_engine

    def create_metadict(self, ):

        mm = {

        }

        return mm

    def create_map_dict(self, ):
        NCLASS = self.NCLASS
        # log("token boi")
        # log(f'{self.token_BOI}')
        # log(f'{self.nertag_list}')
        begin_of_word = self.token_BOI[0]
        inside_of_word = self.token_BOI[1]
        other_word = self.token_BOI[2]
        ### Dict mapping: Label --> Index
        L2I = {}
        for index, c in enumerate(self.nertag_list):
            L2I[f'{begin_of_word}-{c}'] = index
            L2I[f'{inside_of_word}-{c}'] = index + NCLASS
        L2I[other_word] = NCLASS * 2
        L2I['Special'] = -100
        L2I

        ### Dict mapping: Index ---> Label
        I2L = {}
        for k, v in L2I.items():
            I2L[v] = k
        I2L[-100] = 'Special'

        I2L = dict(I2L)
        log(I2L)

        self.L2I = L2I
        self.I2L = I2L

        return L2I, I2L, NCLASS

    def get_class(self, class_idx: int):
        if class_idx == self.NCLASS_BOI - 1:
            return self.token_BOI[2]
        else:
            return self.I2L[class_idx].replace(self.token_BOI[0], "").replace(self.token_BOI[1], "").replace("-", "")

    def pred2span(self, pred_list, row_df, test=False):
        """ Converts list of predicted labels to spans and generates record format for each span.

        Args:
            pred_list (list or numpy.ndarray): list or numpy array of predicted labels.
            row_df (pandas.DataFrame)        : DataFrame containing text and offset_mapping columns.
            test (bool, optional)            : flag indicating whether it is in test mode. Defaults to False.

        Returns:
            dict: dict containing text and ner_list fields. ner_list field is list of dictionaries,
                  where each dict represents named entity and contains type, value, start, end, and text fields.
        """

        n_tokens = len(row_df['offset_mapping'][0])
        classes = []
        all_span = []
        log(row_df, pred_list, len(pred_list), n_tokens)
        # Gpt4o make mistake here: pred_list is list or numpy array
        pred_list = pred_list.tolist() if hasattr(pred_list, "tolist") else pred_list

        for i, c in enumerate(pred_list):
            if i == n_tokens:
                # If we go to end of sentence but for another reason maybe padding, etc so pred_list
                # often longger than n_tokens
                break
            if i == 0:
                cur_span = list(row_df['offset_mapping'][0][i])
                classes.append(self.get_class(c))
            elif i > 0 and (c - self.NCLASS == pred_list[i - 1] or c == pred_list[i - 1]):
                # We will go to next-token for current span: B-, I-, I-, I-
                # Note: index_of_inside_word - NCLASS ===  index_of_begin_word
                cur_span[1] = row_df['offset_mapping'][0][i][1]
            else:
                all_span.append(cur_span)
                cur_span = list(row_df['offset_mapping'][0][i])
                classes.append(self.get_class(c))
        all_span.append(cur_span)

        text = row_df["text"]

        # map token ids to word (whitespace) token ids
        predstrings = []
        for span in all_span:
            span_start = span[0]
            span_end = span[1]
            before = text[:span_start]
            token_start = len(before.split())
            if len(before) == 0:
                token_start = 0
            elif before[-1] != ' ':
                token_start -= 1

            num_tkns = len(text[span_start:span_end + 1].split())
            tkns = [str(x) for x in range(token_start, token_start + num_tkns)]
            predstring = ' '.join(tkns)
            predstrings.append(predstring)

        #### Generate Record format
        row = {"text": text, "ner_list": []}
        llist = []
        for ner_type, span, predstring in zip(classes, all_span, predstrings):
            if ner_type != self.token_BOI[2]:  # token_BOI[2] == 'Other word'
                e = {
                    "class": ner_type,
                    'value': text[span[0]:span[1]],
                    'start': span[0],
                    'end': span[1],
                }
                llist.append(e)
        row["ner_list"] = llist

        return row

    def pd_convert_ner_to_records(self, df_val: pd.DataFrame, offset_mapping: list,
                                  col_nerlist="pred_ner_list", col_text="text") -> pd.DataFrame:
        """Convert predicted classes into span records for NER.
        Args:
            df_val (pd.DataFrame): DataFrame containing input data. It should have following columns:
                - col_nerlist (str): Column name for predicted classes.
                - col_text (str): Column name for text.
            offset_mapping (list): List of offset mappings.

        Returns:
            list: List of span records for NER. Each span record is dict with following keys:
                - text (str): text.
                - ner_list (list): List of named entity records. Each named entity record is dict with following keys:
                    - type (str)            : type of named entity.
                    - predictionstring (str): predicted string for named entity.
                    - start (int)           : start position of named entity.
                    - end (int)             : end position of named entity.
                    - text (str)            : text of named entity.

        """
        #### Convert
        pred_class = df_val[col_nerlist].values
        valid = df_val[[col_text]]
        valid['offset_mapping'] = offset_mapping
        valid = valid.to_dict(orient="records")

        ### pred_class : tuple(start, end, string)
        predicts = [self.pred2span(pred_class[i], valid[i]) for i in range(len(valid))]

        # df_val["ner_list_records"] = [row['ner_list'] for row in predicts]

        return [row['ner_list'] for row in predicts]

    @staticmethod
    def nerdata_validate_dataframe(*dflist):

        for df in dflist:
            assert df[["text", "ner_list"]].shape
            rowset = set(df["ner_list"].values[0][0].keys())
            assert rowset.issuperset({"start", "end", "class", "value"}), f"error {rowset}"

    @staticmethod
    def nerdata_validate_row(x: Union[list, dict], cols_ref=None):
        """Check format of NER records.
        Args:
            x (Union[list, dict]):     NER records to be checked. list of dict or single dict.
            cols_ref (set, optional):  reference set of columns to check against.
        """

        cols_ref = {'start', 'value', "class"} if cols_ref is None else set(cols_ref)

        if isinstance(x, list):
            ner_records = set(x[0].keys())
            assert ner_records.issuperset(cols_ref), f" {ner_records} not in {cols_ref}"

        elif isinstance(x, dict):
            ner_records = set(x.keys())
            assert ner_records.issuperset(cols_ref), f" {ner_records} not in {cols_ref}"

        return True

    @staticmethod
    def nerdata_extract_nertag_from_df(df_or_path):
        df = pd_read_file(df_or_path)
        tag_list = []
        for index, row in df.iterrows():
            for tag in row['ner_list']:
                type_of_tag = tag["class"]
                if type_of_tag not in tag_list:
                    tag_list.append(type_of_tag)
        tag_list = sorted(tag_list)
        log("tag_list", tag_list)
        return tag_list


# TODO: test17　NERdata


##################### NER Tokenizer helper ##############################################
def test18():
    """
    Tests the `token_fix_beginnings` function

    Output logs:
    ```
    [0, 1, 2, 3, 0, 1, 2, 3]
    ```
    """
    labels = [0, 1, 2, 3, 4, 5, 6, 7]
    n_nerclass = 4
    labels_out = token_fix_beginnings(labels, n_nerclass)
    print(labels_out)
    assert labels_out == [0, 1, 2, 3, 0, 1, 2, 3]


def test19():
    """
    Tests the `DataCollatorForNER` class

    Output logs:
    ```
    You're using a DebertaV2TokenizerFast tokenizer. Please note that with a fast tokenizer, using the `__call__` method is faster than using a method to encode the text followed by a call to the `pad` method to get a padded encoding.
    {'input_ids': tensor([[   1, 5365,  261,  312,  601,  269,  918,  260,    2],
            [   1,  273,  685,  267,  485,  920,  260,    2,    0]]), 'attention_mask': tensor([[1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 0]]), 'labels': tensor([[   1,    0,    0,    0,    1,    0,    0],
            [   1,    0,    0,    1,    1, -100, -100]])}
    ```
    """
    tokenizer = AutoTokenizer.from_pretrained("microsoft/deberta-v3-base")
    data_collator = DataCollatorForNER(tokenizer)
    features = [
        {
            "input_ids": tokenizer.encode("Hello, my name is John.", add_special_tokens=True),
            "label": [1, 0, 0, 0, 1, 0, 0]
        },
        {
            "input_ids": tokenizer.encode("I live in New York.", add_special_tokens=True),
            "label": [1, 0, 0, 1, 1]
        }
    ]
    batch = data_collator(features)
    print(batch)


def token_fix_beginnings(labels, n_nerclass):
    """Fix   beginning of list of labels by adjusting   labels based on certain conditions.
    Args:
        labels (list): list of labels.
    # tokenize and add labels
    """
    for i in range(1, len(labels)):
        curr_lab = labels[i]
        prev_lab = labels[i - 1]
        if curr_lab in range(n_nerclass, n_nerclass * 2):
            if prev_lab != curr_lab and prev_lab != curr_lab - n_nerclass:
                labels[i] = curr_lab - n_nerclass
    return labels


def tokenize_and_align_labels(row: dict, tokenizer, L2I: dict, token_BOI: list):
    """Tokenizes  given examples and aligns  labels.
    Args:
        examples (dict): dict containing  examples to be tokenized and labeled.
            - "text" (str):  query string to be tokenized.
            - "ner_list" (list): list of dictionaries representing  entity tags.
                Each dict should have  following keys:
                - 'start' (int):  start position of  entity tag.
                - 'end' (int):  end position of  entity tag.
                - "class" (str):  type of  entity tag.

    Returns:
        dict: dict containing  tokenized and labeled examples.
            It has  following keys:
            - 'input_ids' (list): list of input ids.
            - 'attention_mask' (list): list of attention masks.
            - 'labels' (list): list of labels.
            - 'token_type_ids' (list, optional): list of token type ids. Only present if 'token_type_ids' is present in  input dict.
    """
    row['text'] = row['text'].replace("\n", "*")
    words = row['text'].split()
    # offset_mapping = [[]]
    # for word in words:

    o = tokenizer(row["text"],
                  return_offsets_mapping=True,
                  return_overflowing_tokens=True)
    offset_mapping = o["offset_mapping"]
    o["labels"] = []
    NCLASS = (len(L2I) - 1) // 2
    for i in range(len(offset_mapping)):
        labels = [L2I[token_BOI[2]] for i in range(len(o['input_ids'][i]))]
        for tag in row["ner_list"]:
            label_start = tag['start']
            label_end = tag['end']
            label = tag["class"]
            for j in range(len(labels)):
                token_start = offset_mapping[i][j][0]

                def fix_space(x, t):
                    while x < len(t) and t[x] == ' ':
                        x += 1
                    return x
                    # print(token_start)

                token_end = offset_mapping[i][j][1]

                if token_start == label_start or fix_space(token_start, row['text']) == label_start:
                    labels[j] = L2I[f'{token_BOI[0]}-{label}']
                if token_start > label_start and token_end <= label_end:
                    labels[j] = L2I[f'{token_BOI[1]}-{label}']
                # if token_start==89 or token_start==98:
                #     print(token_start, token_end, labels[j], label_start, label_end)

        for k, input_id in enumerate(o['input_ids'][i]):
            if input_id in [0, 1, 2]:
                labels[k] = -100
        # log(labels)
        labels = token_fix_beginnings(labels, NCLASS)
        # log(labels)
        o["labels"].append(labels)

    o['labels'] = o['labels'][0]
    o['input_ids'] = o['input_ids'][0]
    o['attention_mask'] = o['attention_mask'][0]
    if 'token_type_ids' in o: o['token_type_ids'] = o['token_type_ids'][0]
    return o


@dataclass
class DataCollatorForNER:
    tokenizer: PreTrainedTokenizerBase
    padding: Union[bool, str, PaddingStrategy] = True
    max_length: Optional[int] = None
    pad_to_multiple_of: Optional[int] = None

    def __call__(self, features):
        label_name = 'label' if 'label' in features[0].keys() else 'labels'
        labels = [feature.pop(label_name) for feature in features]
        max_length_labels = max([len(i) for i in labels])
        labels_pad = np.zeros((len(labels), max_length_labels,)) + -100
        for index in range(len(labels)):
            #             log(len(labels[index]), labels[index])
            labels_pad[index, : len(labels[index])] = labels[index]

        batch_size = len(features)
        flattened_features = features
        batch = self.tokenizer.pad(
            flattened_features,
            padding=self.padding,
            max_length=self.max_length,
            pad_to_multiple_of=self.pad_to_multiple_of,
            return_tensors='pt',
        )
        batch['labels'] = torch.from_numpy(labels_pad).long()

        return batch


###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()






























# def deberttav2_hierarchicalsoftmax_sequence_classification_checkpoint_load(dir_checkpoint):
#     """
#     Load DebertaV2ForSequenceClassificationHieraSoftmax for inference
#     """
#     cc = Box(json_load(os.path.join(dir_checkpoint, "meta.json")))

#     label_list = list(cc.label2key.keys())
#     root, dictlabels = hierarchicalsoftmax_get_dictlabels(label_list, sep=" - ", name_recusive=True)

#     tokenizer = AutoTokenizer.from_pretrained(cc.model_name)
#     model = DebertaV2ForSequenceClassificationHieraSoftmax.from_pretrained(
#         dir_checkpoint, # cc.model_name,
#         root=root, 
#         freeze_deberta=True,
#     )
#     pipe = HierarchicalSoftmaxTextClassificationPipeline(model=model, tokenizer=tokenizer)
#     return pipe




