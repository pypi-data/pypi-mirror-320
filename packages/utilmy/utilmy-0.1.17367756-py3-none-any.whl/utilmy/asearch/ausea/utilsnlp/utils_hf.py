"""  
## Install

    ### Diskcache Enable
    export CACHE_ENABLE="1"   




"""
if "import":
    import os, sys, json, pandas as pd,numpy as np, gc, time
    import copy, random
    from copy import deepcopy
    from typing import Optional, Union
    from box import Box
    from tqdm import tqdm
    from functools import partial
    from dataclasses import dataclass


    from datasets import load_dataset, DatasetDict, Dataset
    from sklearn.metrics import classification_report

    from transformers import (AutoTokenizer, AutoModelForSequenceClassification,    
       TrainingArguments, Trainer, pipeline, DataCollatorWithPadding,
       BertModel, EarlyStoppingCallback
    )

    # from sentence_transformers import SentenceTransformer
    import torch, evaluate
    import torch.nn as nn

   # from src.engine.usea.utilsr.util_exp import (exp_create_exp_folder,
   #                                              exp_config_override, exp_get_filelist, json_save, log_pd,
   #                                              torch_device)

    from src.utils.utilmy_base import diskcache_decorator, log_pd
    from utilmy import (pd_read_file, os_makedirs, pd_to_file, date_now, glob_glob, config_load,
                       json_save, json_load, log, log2, loge,)






def torch_init():

    try:
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




@dataclass
class HFtask:
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




def test_ds_token():
    ## Multi-label working dataloader for debugging Purpose
    from datasets import load_dataset
        
    dataset = load_dataset('knowledgator/events_classification_biotech') 
        
    classes = [class_ for class_ in dataset['train'].features['label 1'].names if class_]
    class2id = {class_:id for id, class_ in enumerate(classes)}
    id2class = {id:class_ for class_, id in class2id.items()}


    from transformers import AutoTokenizer
    model_path = "microsoft/deberta-v3-base"
    tokenizer = AutoTokenizer.from_pretrained(model_path)

    def preprocess_function(example):
       text = f"{example['title']}.\n{example['content']}"
       all_labels = example['all_labels'] # .split(', ')
       labels = [0. for i in range(len(classes))]
       for label in all_labels:
           label_id = class2id[label]
           labels[label_id] = 1.
      
       example = tokenizer(text, truncation=True)
       example['labels'] = labels

       #dd2 = {k:v for k,v in example.items() if k in ll }     
       return example

    tokenized_dataset = dataset.map(preprocess_function)
    log(tokenized_dataset)
    n_labels = len(classes)
    return tokenized_dataset, tokenizer, n_labels 





from transformers import TrainerCallback
class CallbackCSaveCheckpoint(TrainerCallback):
    def __init__(self, cc=None, thisfile=None):
        self.cc       = cc  # Store cc as an instance variable
        self.thisfile = thisfile  if thisfile is None else __file__

    def on_save(self, args, state, control, **kwargs):
        """ When doing Checkpoint /saving
        
        """
        if state.is_world_process_zero:
            # Get the checkpoint folder path
            try:
               import os, json
               from utilmy import json_save
               dircheck = args.output_dir + f"/checkpoint-{state.global_step}" 
               os_makedirs(dircheck) 

               ### Train file
               os_copy_current_file(dircheck +"/train.py", self.thisfile)

               ### Metrics history
               json_save(state.log_history, dircheck +"/meta_metrics.json"  )            
                
               ### Meta data 
               json_save(self.cc.to_dict(), dircheck +"/meta.json"  )            
               print(f"Saved custom info to {dircheck}")

            except Exception as e:
               log(e)   
        
        return control




##############################################################################################
def hf_save_dataset(dataset: Dataset, path: str):
    dataset.save_to_disk(path)


def hf_save_model_with_checkpoint(trainer, dirout):

    trainer.save_pretrained(dirout)
    trainer.save_state()


def hf_model_get_mapping(model='mymodel'):
    from transformers import AutoConfig

    config = AutoConfig.from_pretrained(model)

    log(config)

    label2id   = config.label2id
    id2label   = config.id2label
    max_length = config.max_position_embeddings
    log('mdoel: ', str(label2id)[:100] )    
    log('model: max_length ', max_length)
    return label2id, id2label, max_length


def hf_model_load_checkpoint(dir_checkpoint):
    from transformers import AutoModelForSequenceClassification

    model = AutoModelForSequenceClassification.from_pretrained(dir_checkpoint, num_labels=2)
    checkpoint = torch.load( dir_checkpoint )
    model.load_state_dict(checkpoint, strict=False)
    return model 


def hf_tokenized_data_clean(tk_ds, cols_remove1=None):
    ll = [ 'input_ids', 'token_type_ids', 'attention_mask', 'labels' ]

    if 'train' in tk_ds:
        cols_remove = [  ci   for ci in tk_ds['train'].column_names if ci not in ll  ]

    tk_ds       = tk_ds.remove_columns(cols_remove)
    log(tk_ds)
    log('labels: ', tk_ds['train']['labels'][0] )
    return tk_ds


def tokenize_singlerow(rows, tokenizer, num_labels, label2key):
    """
      # tokenize2 = partial(tokenize_singlerow, num_labels=cc.num_labels, label2key=cc.label2key)
      # tk_ds = dataset.map(partial( tokenize2)) # , batched=False)

    """
    out = tokenizer( rows["text"], truncation=True, max_length=2048, )
             # padding=True, 
             # max_length=2048, 
    xval = rows['label']
    if isinstance(xval, str):
         xval = xval.split(',')
    elif isinstance(xval, list):
         pass 
    else :
         xval = [xval]    
   
    if isinstance(xval, list):            
        ones = [0. for i in range(num_labels)]
        for label_idx in xval :
           ones[label_idx] = 1.

    out['labels'] = ones
    #     # ones = torch.tensor(ones, dtype=torch.float)
    return out







def hf_predict_format(df, colpred, colout, label2id, cc  ):
    ### 2Dim: each prediction --> (label_id, score)

    c = "-" +colout ### suffix
    # from src.utilsnlp.utils_hf import np_sort, np_argmax
    predictions = df[colpred ].values

    preds_2d   = [ np_sort([(label2id[ x["label"] ], x["score"])  for x in  pred_row ], col_id=1)  for pred_row in predictions]


    ### Best Top1 prediction
    cc.key2label = { int(key): val  for key,val in cc.key2label.items()    }

    pred_labels_top1 = [  np_argmax(x,1)[0]  for x in preds_2d   ] ## Argmax on Score
    df['pred_idx'+c]   = pred_labels_top1
    df['pred'+c]       = df['pred_idx'+c].apply( lambda x : cc.key2label.get(x, "NA") )
    log(df[[ 'pred'+c  ]]) 


    #### 2Dim : NBatch x N_labels
    df['pred_2d_idx'+c]  = [ [ str(x[0]), str(x[1]) ] for x in  preds_2d ]
    df['pred_2d_label'+c]= [ np_sort([( cc.key2label.get( label2id[ x["label"] ], ""), str(x["score"]) )   for x in row ], col_id= 1)  for row in predictions]


    log(df[[ xi + c for xi in [ 'pred_idx', 'pred', 'pred_2d_idx', 'pred_2d_idx'  ]        ] ])
    return df










############################################################################################
######### Metrics ##########################################################################
f1_metric       = evaluate.load("f1")
accuracy_metric = evaluate.load("accuracy")
clf_metric      = evaluate.combine(["accuracy", "f1", "precision", "recall"])


######## Multi ####################################################
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
    f1_per_class = f1_metric.compute(predictions=pred_labels, references=ref_labels, average=None)['f1']
    
    # Create a dictionary with class names (adjust based on your number of classes)
    class_names       = [f"class_{i}" for i in range(len(f1_per_class))]
    f1_per_class_dict = {f"f1_{name}": score for name, score in zip(class_names, f1_per_class)}

    return {  "accuracy":     acc["accuracy"],
              "f1_micro":     f1_micro,
              "f1_per_class": f1_per_class_dict 
            }



def compute_multi_accuracy_hamming(eval_pred):
    from sklearn.metrics import hamming_loss
    preds_score, labels = eval_pred


    pred_labels = [ [ pi>0.5 for pi in pred ] for pred in preds_score ] # np.argmax(predictions, axis=1)
    ham_list    = []
    for pred, label in zip(preds_score, labels):
        ham_values = 1 - hamming_loss(labels, preds_score)
        ham_list.append( ham_values)

    return {
        "accuracy_hamming": float( np.sum(ham_list) )
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



######## Single ##################################################
def compute_single_(eval_pred, accuracy_fn):
   predictions, labels = eval_pred
   predictions = np.argmax(predictions, axis=1)
   return accuracy_fn.compute(predictions=predictions, references=labels)


def compute_single_accuracy_f1(eval_pred):
    pred_2D, labels = eval_pred
    pred_1D = pred_2D.argmax(axis=-1)
    
    accuracy = accuracy_metric.compute(predictions=pred_1D, references=labels)["accuracy"]
    f1       = f1_metric.compute(predictions=pred_1D, references=labels, average="macro")["f1"]
    return {   "accuracy": accuracy,  "f1": f1, }
    
    
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
    
    return {   "accuracy": accuracy,
               "f1": f1,
               **f1_per_class_dict
            }
    


##################################################################
def classification_report_v2(y_true, y_pred, labels=None, target_names=None, digits=4):

    from sklearn.metrics import confusion_matrix

    report = classification_report(y_true, y_pred, labels=labels, target_names=target_names, output_dict=True, digits=digits)
    cm     = confusion_matrix(y_true, y_pred, labels=labels)
    per_class_accuracy = cm.diagonal() / cm.sum(axis=1)
    
    for i, label in enumerate(labels or range(len(per_class_accuracy))):
        report[str(label)]['accuracy'] = per_class_accuracy[i]
    
    return report


def check1():
    """ 
      MoritzLaurer/deberta-v3-large-zeroshot-v2.0





    """






################################################################################
################################################################################
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
    json_save(cc, f'{output_dir}/meta.json', show=0)  ### Required when reloading for   

    log('Moving trainer state to model dir')
    state_files = ['optimizer.pt', 'scheduler.pt', 'trainer_state.json', 'rng_state.pth']
    for file in state_files:
        src = os.path.join(trainer.args.output_dir, file)
        dst = os.path.join(output_dir, file)
        if os.path.exists(src):
            shutil.move(src, dst)


def dataset_reduce(dataset, ntrain: int = 10, ntest: int = 5) :

    ntrain = min(len(dataset), ntrain)
    ntest  = min(len(dataset), ntest)

    if  isinstance(dataset, DatasetDict) :  
        return DatasetDict({
            'train':  dataset['train'].select(range(ntrain)),
            'test':   dataset['test'].select(range(ntest))
        })
    else:
        return dataset.select(range(ntrain))
    

def accelerator_init(device="cpu", model=None):
    from accelerate import Accelerator
    try: 
       accelerator = Accelerator(cpu=True if device == "cpu" else False)
       return accelerator
    except Exception as e:
       log(e) 


def np_argmax(tuple_list, col_idx=1):
    idx= np.argmax([t[col_idx] for t in tuple_list])
    return tuple_list[ idx] 


def np_sort(tuples, col_id=0, desc=1):
    return sorted(tuples, key=lambda x: float(x[col_id]), reverse=True if desc == 1 else False)


def cc_save(cc, dirout):
    flist = [ f'{dirout}/meta.json',  f'{dirout}/train/meta.json',
              f'{dirout}/model/meta.json'  ]
    for fi in flist :
        log(fi)
        json_save(cc, fi)

    os_copy_current_file( f"{dirout}/train/train.py")    


def os_copy_current_file(dirout, thisfile=None):
    import os, shutil
    try:
       thisfile = __file__ if thisfile is None else thisfile 
       current_file = os.path.abspath(thisfile)
       shutil.copy2(current_file, dirout)
    except Exception as e:
       log(e)
       

    
def argmax_score(scores):
    return max(range(len(scores)), key=scores.__getitem__)







#########################################################################################
######## Torch  #########################################################################
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


def accelerator_init(device="cpu"):
    from accelerate import Accelerator
    try: 
       accelerator = Accelerator(cpu=True if device == "cpu" else False)
    except Exception as e:
       log(e) 






##############################################################################################
def hf_head_task():

    ### Increase the head task
    model.classifier = nn.Sequential(
        nn.Linear(model.config.hidden_size, 512),
        nn.ReLU(),
        nn.Linear(512, num_labels)
    )



   
      
###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()












