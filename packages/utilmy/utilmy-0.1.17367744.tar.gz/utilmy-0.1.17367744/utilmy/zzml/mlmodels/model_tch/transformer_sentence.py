# -*- coding: utf-8 -*-
"""
https://pypi.org/project/sentence-transformers/

from sentence_transformers import SentenceTransformer
model = SentenceTransformer('bert-base-nli-mean-tokens')


sentences = ['This framework generates embeddings for each input sentence',
    'Sentences are passed as a list of string.', 
    'The quick brown fox jumps over the lazy dog.']
sentence_embeddings = model.encode(sentences)


bert-base-nli-cls-token.zip                        14-Aug-2019 12:53           405237015
bert-base-nli-max-tokens.zip                       14-Aug-2019 12:53           405231770
bert-base-nli-mean-tokens.zip                      14-Aug-2019 09:03           405234788
bert-base-nli-stsb-mean-tokens.zip                 14-Aug-2019 12:52           405233603
bert-base-wikipedia-sections-mean-tokens.zip       14-Aug-2019 12:53           405227291
bert-large-nli-cls-token.zip                       14-Aug-2019 12:57          1243516284
bert-large-nli-max-tokens.zip                      14-Aug-2019 12:54          1243506292
bert-large-nli-mean-tokens.zip                     14-Aug-2019 12:55          1243511182
bert-large-nli-stsb-mean-tokens.zip                14-Aug-2019 12:57          1243516997
distilbert-base-nli-mean-tokens.zip                06-Dec-2019 11:09           244584363
distilbert-base-nli-stsb-mean-tokens.zip           06-Dec-2019 13:51           244582843
distiluse-base-multilingual-cased.zip              23-Jan-2020 09:51           504125638
readme.txt                                         14-Aug-2019 09:04                  82
roberta-base-nli-mean-tokens.zip                   05-Dec-2019 12:44           458913367
roberta-base-nli-stsb-mean-tokens.zip              05-Dec-2019 13:21           459100025
roberta-large-nli-mean-tokens.zip                  05-Dec-2019 12:49          1312045841
roberta-large-nli-stsb-mean-tokens.zip             05-Dec-2019 13:43          1312308420



bert-base-nli-mean-tokens: BERT-base model with mean-tokens pooling. Performance: STSbenchmark: 77.12
bert-base-nli-max-tokens: BERT-base with max-tokens pooling. Performance: STSbenchmark: 77.18
bert-base-nli-cls-token: BERT-base with cls token pooling. Performance: STSbenchmark: 76.30
bert-large-nli-mean-tokens: BERT-large with mean-tokens pooling. Performance: STSbenchmark: 79.19
bert-large-nli-max-tokens: BERT-large with max-tokens pooling. Performance: STSbenchmark: 78.32
bert-large-nli-cls-token: BERT-large with CLS token pooling. Performance: STSbenchmark: 78.29
roberta-base-nli-mean-tokens: RoBERTa-base with mean-tokens pooling. Performance: STSbenchmark: 77.42
roberta-large-nli-mean-tokens: RoBERTa-base with mean-tokens pooling. Performance: STSbenchmark: 78.58
distilbert-base-nli-mean-tokens: DistilBERT-base with mean-tokens pooling. Performance: STSbenchmark: 76.97
Trained on STS data

These models were first fine-tuned on the AllNLI datasent, then on train set of STS benchmark. They are specifically well suited for semantic textual similarity. For more details, see: sts-models.md.

bert-base-nli-stsb-mean-tokens: Performance: STSbenchmark: 85.14
bert-large-nli-stsb-mean-tokens: Performance: STSbenchmark: 85.29
roberta-base-nli-stsb-mean-tokens: Performance: STSbenchmark: 85.40
roberta-large-nli-stsb-mean-tokens: Performance: STSbenchmark: 86.31
distilbert-base-nli-stsb-mean-tokens: Performance: STSbenchmark: 84.38





"""
import glob
import inspect
from jsoncomment import JsonComment ; json = JsonComment()
import logging
import math
import os
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm_notebook, trange




from scipy.stats import pearsonr
from sklearn.metrics import (confusion_matrix, matthews_corrcoef,   mean_squared_error)


import torch
from torch.utils.data import (DataLoader, RandomSampler, SequentialSampler, TensorDataset)
from torch.utils.data.distributed import DistributedSampler


from sentence_transformers import (LoggingHandler, SentencesDataset,
                                   SentenceTransformer, losses, models,
                                   readers)
from sentence_transformers.evaluation import EmbeddingSimilarityEvaluator
from sentence_transformers.readers import *
import sentence_transformers as K
from sentence_transformers import models


####################################################################################################
from mlmodels.util import  log, path_norm, get_model_uri, path_norm_dict

VERBOSE = False
MODEL_URI = get_model_uri(__file__)






####################################################################################################
class Model:
  def __init__(self, model_pars=None, data_pars=None, compute_pars=None, **kwargs):
    """ Model:__init__.
    Doc::
            
            Args:
                model_pars:     
                data_pars:     
                compute_pars:     
                **kwargs:     
            Returns:
               
    """
    self.model_pars = model_pars
    self.model_pars = compute_pars
    self.data_pars = data_pars

    if model_pars is None :
        self.model = None

    else :
    ### Model Structure        ################################
        self.EmbeddingModel       = getattr(models, model_pars["embedding_model"])
        self.word_embedding_model = self.EmbeddingModel( model_pars["embedding_model_name"])
        self.pooling_model        = models.Pooling(self.word_embedding_model.get_word_embedding_dimension(),
            pooling_mode_mean_tokens = model_pars.get("pooling_mode_mean_tokens"  ,True),
            pooling_mode_cls_token   = model_pars.get("pooling_mode_cls_token" ,False),
            pooling_mode_max_tokens  = model_pars.get("pooling_mode_max_tokens",False))

        self.model       = SentenceTransformer( modules=[self.word_embedding_model, self.pooling_model] )

        self.fit_metrics = {"train": {}, "test": {}}    #### metrics during training


def fit(model, data_pars=None, model_pars=None, compute_pars=None, out_pars=None, *args, **kw):
    """.
    Doc::
            
    """

    log("############ Dataloader setup  #############################")
    data_readers, interal_states = get_dataset(data_pars)
    train_reader, val_reader = data_readers

    train_data       = SentencesDataset(train_reader.get_examples('train.gz'),  model=model.model)
    train_dataloader = DataLoader(train_data, shuffle=True, batch_size=compute_pars["batch_size"])

    val_data         = SentencesDataset(val_reader.get_examples('val/sts-dev.csv'), model=model.model)
    val_dataloader   = DataLoader(val_data, shuffle=True, batch_size=compute_pars["batch_size"])


    log("############ Fit setup  ##################################")
    emb_dim          = model.model.get_sentence_embedding_dimension()
    train_num_labels = train_reader.get_num_labels()

    train_loss = getattr(losses, compute_pars["loss"])(
        model                        = model.model,
        sentence_embedding_dimension = emb_dim,
        num_labels                   = train_num_labels
    )
    train_loss.float()
    evaluator = EmbeddingSimilarityEvaluator(val_dataloader)
    model.model.float()

    model.fit_metrics = model.model.fit(train_objectives=[(train_dataloader, train_loss)],
                        evaluator        = evaluator,
                        epochs           = compute_pars["num_epochs"],
                        evaluation_steps = compute_pars["evaluation_steps"],
                        warmup_steps     = compute_pars["warmup_steps"],
                        output_path      = out_pars["model_path"]
                        )
    return model, None





def evaluate(model, session=None, data_pars=None, compute_pars=None, out_pars=None, **kw):
    """.
    Doc::
            
               Return metrics of the model when fitted.
    """
    ddict = model.fit_metrics    
    return ddict


def predict(model, session=None, data_pars=None, out_pars=None, compute_pars=None, **kw):
    """function predict.
    Doc::
            
            Args:
                model:   
                session:   
                data_pars:   
                out_pars:   
                compute_pars:   
                **kw:   
            Returns:
                
    """

    reader      = get_dataset(data_pars)
    train_fname = 'train.gz' if data_pars["train_type"].lower() == 'nli' else 'sts-train.csv'
    examples    = [ex.texts for ex in reader.get_examples(train_fname)]
    Xpred       = sum(examples, [])

    #### Do prediction
    ypred = model.model.encode(Xpred)

    ### Save Results

    ### Return val
    # if compute_pars.get("return_pred_not") is not None :
    return ypred


  
def reset_model():
    """function reset_model.
    Doc::
            
            Args:
            Returns:
                
    """
    pass


def save(model, session=None, save_pars=None):
    """function save.
    Doc::
            
            Args:
                model:   
                session:   
                save_pars:   
            Returns:
                
    """
    return torch.save(model.modl, save_pars['path'])


def load(load_pars=None):
    """function load.
    Doc::
            
            Args:
                load_pars:   
            Returns:
                
    """
    model = Model(skip_create=True)
    model.model = torch.load(load_pars['path'])
    return model   



####################################################################################################
def get_dataset(data_pars=None, **kw):
    """.
    Doc::
            
            JSON data_pars to get dataset
            "data_pars":    { "data_path": "dataset/GOOG-year.csv", "data_type": "pandas",
            "size": [0, 0, 6], "output_size": [0, 6] },
    """
    from mlmodels.dataloader import DataLoader
    loader = DataLoader(data_pars)
    loader.compute()
    return loader.get_data()



############# Refactor ###########################################################################
def fit2(model, data_pars=None, model_pars=None, compute_pars=None, out_pars=None, *args, **kw):
    """.
    Doc::
            
    """
    log("############ Dataloader setup  ###########################")
    data_pars['is_train'] = 1
    train_dataloader, val_dataloader, pars = get_dataset2(data_pars, model=model)


    log("############ Fit setup  ##################################")
    emb_dim          = model.model.get_sentence_embedding_dimension()
    train_num_labels = pars["train_num_labels"]
    # train_num_labels = train_reader.get_num_labels()

    train_loss = getattr(losses, compute_pars["loss"])(
        model                        = model.model,
        sentence_embedding_dimension = emb_dim,
        num_labels                   = train_num_labels
    )
    train_loss.float()

    evaluator = EmbeddingSimilarityEvaluator(val_dataloader)
    model.model.float()

    model.fit_metrics = model.model.fit(train_objectives=[(train_dataloader, train_loss)],
                        evaluator        = evaluator,
                        epochs           = compute_pars["num_epochs"],
                        evaluation_steps = compute_pars["evaluation_steps"],
                        warmup_steps     = compute_pars["warmup_steps"],
                        output_path      = out_pars["model_path"]
                        )
    return model, None


def predict2(model, session=None, data_pars=None, out_pars=None, compute_pars=None, **kw):
    """function predict2.
    Doc::
            
            Args:
                model:   
                session:   
                data_pars:   
                out_pars:   
                compute_pars:   
                **kw:   
            Returns:
                
    """
    data_pars['is_train'] = 1
    reader, pars      = get_dataset2(data_pars, model=model)

    train_fname = pars['train_fname']
    examples    = [ex.texts for ex in reader.get_examples(train_fname)]
    Xpred       = sum(examples, [])

    #### Do prediction
    ypred = model.model.encode(Xpred)

    ### Save Results

    ### Return val
    # if compute_pars.get("return_pred_not") is not None :
    return ypred



def get_dataset2(data_pars=None, model=None, **kw):
    """.
    Doc::
            
            JSON data_pars to get dataset
            "data_pars":    { "data_path": "dataset/GOOG-year.csv", "data_type": "pandas",
            "size": [0, 0, 6], "output_size": [0, 6] },
    """
    # data_path = path_norm(data_pars["data_path"])

    istrain   = data_pars.get("is_train", 0)
    mode      = "train" if istrain else "test"
    data_type = data_pars[f"{mode}_type"].lower() 
   
    def get_reader(data_type, path) :
        if data_type == 'nli':     Reader = readers.NLIDataReader
        elif data_type == 'sts':   Reader = readers.STSDataReader
        else :
            Reader = "MyCustomReader()"

        path = os.path.join(path)
        reader = Reader(path)
        return reader


    def get_filename(data_type, mode='test') :
        if mode == 'train' :
            fname   = 'train.gz' if data_pars["train_type"].lower() == 'nli'else 'sts-train.csv'              
        
        if mode == 'test' :
            fname   = 'dev.gz' if data_pars["test_type"].lower() == 'nli'  else 'sts-dev.csv'
      
        return fname


    log("############ Dataloader setup  #############################")
    train_dataloader = None
    if istrain :
        train_pars              = data_pars.copy()
        train_pars.update(train=1)
        train_fname             = get_filename( data_pars, mode='train'  )  # 'train.gz' if data_pars["train_type"].lower() == 'nli'else 'sts-train.csv'
        train_reader            = get_reader(data_type, data_pars['train_path'])    
        train_data       = SentencesDataset(train_reader.get_examples(train_fname),  model=model.model)
        train_dataloader = DataLoader(train_data, shuffle=True, batch_size=data_pars["batch_size"])

        val_pars                = data_pars.copy()
        val_pars.update(train=0)
        val_fname               = get_filename( data_pars, mode='test'  )  #'dev.gz' if data_pars["test_type"].lower() == 'nli'  else 'sts-dev.csv'
        val_reader            = get_reader(data_type, data_pars['test_path'])    
        val_data         = SentencesDataset(val_reader.get_examples(val_fname), model=model.model)
        val_dataloader   = DataLoader(val_data, shuffle=True, batch_size=data_pars["batch_size"])

        pars = { "train_num_labels" :  train_reader.get_num_labels() }
        return train_dataloader, val_dataloader, pars


    else :
        #### Inference part
        val_pars                = data_pars.copy()
        val_pars.update(train=0)
        val_fname               = get_filename( data_pars, mode='test'  )  #'dev.gz' if data_pars["test_type"].lower() == 'nli'  else 'sts-dev.csv'
        val_reader            = get_reader(data_type, data_pars['test_path'])    

        pars = {"train_fname" : 'train.gz' if data_pars["train_type"].lower() == 'nli' else 'sts-train.csv'}

        return val_reader , pars 
      







def get_params(param_pars, **kw):
    """function get_params.
    Doc::
            
            Args:
                param_pars:   
                **kw:   
            Returns:
                
    """
    choice      = param_pars['choice']
    config_mode = param_pars['config_mode']
    data_path   = param_pars['data_path']

    if choice == "json":
       data_path = path_norm(data_path)
       cf        = json.load(open(data_path, mode='r'))
       cf        = cf[config_mode]
       cf        = path_norm_dict(cf)
       return cf['model_pars'], cf['data_pars'], cf['compute_pars'], cf['out_pars']


    if choice == "test01":
        """
        log("#### Path params   ##########################################")
        data_path  = path_norm("dataset/text/")
        out_path   = path_norm("ztest/model_tch/transformer_sentence/" )
        model_path = os.path.join(out_path, "model")

        data_pars = {
            "data_path" : data_path,
            "train_path": "AllNLI",
            # one of: STS, NLI
            "train_type": "NLI",
            "test_path": "stsbenchmark",
            # one of: STS, NLI
            "test_type": "sts",
            "train": 1
        }

        model_pars = {
            "embedding_model": "BERT",  "embedding_model_name": "bert-base-uncased",
        }

        compute_pars = {
            "loss": "SoftmaxLoss",
            "batch_size": 32,
            "num_epochs": 1,
            "evaluation_steps": 10,
            "warmup_steps": 100,
        }

        out_pars = {
            "model_path": model_path,
            "path": out_path
        }
        return model_pars, data_pars, compute_pars, out_pars
        """


##################################################################################################
def test(data_path="dataset/", pars_choice="test01", config_mode="test"):
    """function test.
    Doc::
            
            Args:
                data_path:   
                pars_choice:   
                config_mode:   
            Returns:
                
    """
    ### Local test
    from mlmodels.util import path_norm
    data_path = path_norm(data_path)

    log("#### Loading params   ##############################################") 
    param_pars = { "choice": pars_choice, "data_path": data_path, "config_mode" : config_mode }
    model_pars, data_pars, compute_pars, out_pars = get_params(param_pars)


    log("#### Loading dataset   #############################################")
    Xtuple = get_dataset(data_pars)


    log("#### Model init, fit   #############################################")
    model = Model(model_pars, compute_pars)
    model, session = fit(model, data_pars, model_pars, compute_pars, out_pars)


    log("#### Predict   #####################################################")
    ypred = predict(model, session, data_pars, compute_pars, out_pars)


    log("#### metrics   #####################################################")
    metrics_val = evaluate(model, ypred, data_pars, compute_pars, out_pars)
    print(metrics_val)


    log("#### Plot   ########################################################")


    log("#### Save   ###################################################")
    save_pars = {"path": out_pars['path']}
    save(model, session, save_pars=save_pars)


    log("#### Load #####################################################")
    model2, session2 = load(save_pars)
    print(model2, session2)


    log("#### Predict   ################################################")
    ypred = predict(model2, session2, data_pars, compute_pars, out_pars)
    print(ypred)




if __name__ == '__main__':
    VERBOSE = True
    test_path = os.getcwd() + "/mytest/"


    #### Very Slow !!!!!!!!!!!!!!!!!!!!
    ### Local fixed params
    # test(pars_choice="json")
    test(pars_choice="json", data_path="model_tch/transformer_sentence.json", config_mode="test")
    # test(pars_choice="test01", data_path= "model_tch/transformer_sentence.json", config_mode="test")


    # test(pars_choice="test01", data_path= "model_tch/transformer_sentence_new.json", config_mode="test")



    ### Local json file
    # test(pars_choice="json")

    ####    test_module(model_uri="model_xxxx/yyyy.py", param_pars=None)
    # from mlmodels.models import test_module
    # param_pars = {'choice': "test01", 'config_mode': 'test', 'data_path': '/dataset/'}
    # test_module(module_uri=MODEL_URI, param_pars=param_pars)

    ##### get of get_params
    # choice      = pp['choice']
    # config_mode = pp['config_mode']
    # data_path   = pp['data_path']


    ####    test_api(model_uri="model_xxxx/yyyy.py", param_pars=None)
    # from mlmodels.models import test_api
    # param_pars = {'choice': "test01", 'config_mode': 'test', 'data_path': '/dataset/'}
    # test_api(module_uri=MODEL_URI, param_pars=param_pars)




