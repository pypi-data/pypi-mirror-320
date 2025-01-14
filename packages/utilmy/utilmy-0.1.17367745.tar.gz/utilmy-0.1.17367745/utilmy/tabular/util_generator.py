# -*- coding: utf-8 -*-
"""Genreate New train_data  using advanced Auto-Encoder, GAN
Docs::
    Install :
       pip install sdv ctgan==0.5.1  scikit-learn   imlearn  utilmy
    -------------------------------------------------------------------------------------
    import utilmy.tabular.util_generator as ug
    from utilmy import log
    root  = "ztmp/"
    -------------------------------------------------------------------------------------
    n_sample = 100
    from sdv.demo import load_timeseries_demo
    from sdv.constraints import Unique
    data = load_timeseries_demo()
    entity_columns  = ['Symbol']
    context_columns = ['MarketCap', 'Sector', 'Industry']
    data_col  = {'cols':list(data.columns)}
    data_pars = { 'n_sample':          n_sample,
                  'cols_model_type2' : data_col
                }
    data_pars['gen_samp'] =   {'Xtrain': data}
    data_pars['eval']     =   {'X': data, 'y': None}
    -------------------------------------------------------------------------------------
    models = {
        'PAR': {'model_class': 'PAR',
                  'model_pars': {
                     ## PAR
                     'epochs': 1,
                     'entity_columns': entity_columns,
                     'context_columns': context_columns,
                     'sequence_index': 'Date'
                                },
               } }
    compute_pars = { 'compute_pars' : {},
                     'metrics_pars' : {'metrics' :['CSTest', 'KSTest'], 'aggregate':False},
                     'n_sample_generation' : 10
                   }
    -------------------------------------------------------------------------------------
    model = ug.Model(model_pars=models['PAR'], data_pars=None, compute_pars=None)
    log('Training the model')
    ug.fit(data_pars=data_pars, compute_pars=compute_pars, out_pars=None,task_type='gen_samp')
    print()
    log('Predict data..')
    Xnew = ug.transform(Xpred=None, data_pars=data_pars, compute_pars=compute_pars)
    log(f'Xnew', Xnew)
    log('Evaluating model..')
    log( ug.evaluate(data_pars=data_pars, compute_pars=compute_pars))
    log('Savinf model..')
    ug.save(path= root + '/model_dir/')
    log('Load model..')
    ug.model, session = load_model(path= root + "/model_dir/")
    log(model)
    ----------------------------------------------------------------------------------
      Transformation for ALL Columns :   Increase samples, Reduce Samples.
      WARNING :
      Main isssue is the number of rows change  !!!!
        cannot merge with others
        --> store as train data
        train data ---> new train data
        Transformation with less rows !
"""
import os, sys,copy, pathlib, pprint, json, pandas as pd, numpy as np, scipy as sci, sklearn
from box import Box
####################################################################################################
from utilmy import pd_read_file, pd_to_file
from utilmy import log, log2, log3
verbosity= 5


######## Custom Model ################################################################################
sys.path.append( os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/")


### SDV
try:
    #from sdv.demo import load_tabular_demo
    import sdv
    from sdv.tabular import TVAE, CTGAN
    from sdv.timeseries import PAR
    from sdv.evaluation import evaluate
    import ctgan
    
    if ctgan.__version__ != '0.5.1':
        raise Exception('ctgan outdated', ctgan.__version__ != '0.5.1')
except:
    print("pip install sdv ctgan==0.5.1  scikit-learn ")


### IMBLEARN
import six
sys.modules['sklearn.externals.six'] = six
try:
    from imblearn.over_sampling import SMOTE
    from imblearn.combine import SMOTEENN, SMOTETomek
    from imblearn.under_sampling import NearMiss
except:
    print("pip install imlearn scikit-learn ")



####################################################################################################
global model, session
def init(*kw, **kwargs):
    """function init.
    Doc::
    """
    global model, session
    model = Model(*kw, **kwargs)
    session = None

def reset():
    """function reset.
    Doc::
    """
    global model, session
    model, session = None, None




####################################################################################################
try :
    # CONSTANTS
    SDV_MODELS      = ['TVAE', 'CTGAN', 'PAR'] # The Synthetic Data Vault Models
    IMBLEARN_MODELS = ['SMOTE', 'SMOTEENN', 'SMOTETomek', 'NearMiss']
    MODEL_LIST      = {'TVAE'           : TVAE,
                        'CTGAN'         : CTGAN,
                        'PAR'           : PAR,
                        'SMOTE'         : SMOTE,
                        'SMOTEENN'      : SMOTEENN,
                        'SMOTETomek'    : SMOTETomek,
                        'NearMiss'      : NearMiss
                        }


except : pass

#################################################################################################
###################### test #####################################################################
def test():
    """function test.      
    """
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split

    X, y = make_classification(n_features=10, n_redundant=0, n_informative=2,
                               random_state=1, n_clusters_per_class=1)
    X = pd.DataFrame( X, columns = [ 'col_' +str(i) for i in range(X.shape[1])] )
    y = pd.DataFrame( y, columns = ['coly'] )

    X['colid'] = np.arange(0, len(X))
    X_train, X_test, y_train, y_test    = train_test_split(X, y)
    X_train, X_valid, y_train, y_valid  = train_test_split(X_train, y_train, random_state=2021, stratify=y_train)

    #####
    colid  = 'colid'
    colnum = [ 'col_0', 'col_3', 'col_4', 'coly']
    colcat = [ 'col_1', 'col_7', 'col_8', 'col_9']

    cols_input_type_1 = {
        'colnum' : colnum,
        'colcat' : colcat
    }

    colg_input = {
      'cols_wide_input':   ['colnum', 'colcat' ],
      'cols_deep_input':   ['colnum', 'colcat' ],
    }

    cols_model_type2= {}
    for colg, colist in colg_input.items() :
        cols_model_type2[colg] = []
        for colg_i in colist :
          cols_model_type2[colg].extend( [i for i in cols_input_type_1[colg_i] if i not in y.columns ]   )
    
    ###############################################################################
    n_sample = 100
    data_pars = {'n_sample': n_sample,
                  'cols_input_type' : cols_input_type_1,

                  'cols_model_group': ['colnum',
                                       'colcat',
                                       # 'colcross_pair'
                                       ],

                  'cols_model_type2' : cols_model_type2


        ### Filter data rows   #######################3############################
        , 'filter_pars': {'ymax': 2, 'ymin': -1}
                  }

    data_pars['train'] ={'Xtrain': X_train,  'ytrain': y_train,
                         'Xtest': X_test,  'ytest': y_test}
    data_pars['eval'] =  {'X': X_valid,
                          'y': y_valid}
    data_pars['predict'] = {'X': X_valid}

    compute_pars = { 'compute_pars' : { 
                   } }

    #####################################################################
    models = {
        'CTGAN': {'model_class': 'CTGAN',
                  'model_pars': {
                      ## CTGAN
                     'primary_key': colid,
                     'epochs': 1,
                     'batch_size' :100,
                     'generator_dim' : (256, 256, 256),
                     'discriminator_dim' : (256, 256, 256)
                },
                },
        'TVAE': {'model_class': 'TVAE',
                  'model_pars': { 
                      ## TVAE
                     'primary_key': colid,
                     'epochs': 1,
                     'batch_size' :100,
                },
                },
        'PAR': {'model_class': 'PAR',
                  'model_pars': {
                     ## PAR
                     'epochs': 1,
                     'entity_columns': [colid],
                     'context_columns': None,
                     'sequence_index': None
                },
                },
        'SMOTE': {'model_class': 'SMOTE',
                  'model_pars': {
                     ## SMOTE
                },
                }
    }

    log("######## running Models test ##################")
    for model_name, model_pars in models.items():
        log(f"test --> {model_name}")
        test_helper(model_pars, data_pars, compute_pars)


def test2(n_sample = 1000):
    """function test2.
    """
    #df, colnum, colcat, coly = test_dataset_classi_fake(nrows= n_sample)
    #X,y, X_train, X_valid, y_train, y_valid, X_test,  y_test, num_classes  = train_test_split2(df, coly)

    import utilmy.adatasets as ad
    df, d = ad.test_data_classifier_fake(n_sample)
    colnum, colcat, coly = d['colnum'], d['colcat'], d['coly']
    X,y, X_train, X_valid, y_train, y_valid, X_test,  y_test, num_classes  = ad.pd_train_test_split2(df, coly)

    #### Matching Big dict  ##################################################
    def post_process_fun(y): return int(y)
    def pre_process_fun(y):  return int(y)

    m = {'model_pars': {
        'model_class':  "model_sampler.py::XXXXXX"
        ,'model_pars' : {}
        , 'post_process_fun' : post_process_fun   ### After prediction  ##########################################
        , 'pre_process_pars' : {'y_norm_fun' :  pre_process_fun ,  ### Before training  ##########################

        ### Pipeline for data processing ##############################
        'pipe_list': [  #### coly target prorcessing
            {'uri': 'source/prepro.py::pd_coly',                 'pars': {}, 'cols_family': 'coly',       'cols_out': 'coly',           'type': 'coly'         },
            {'uri': 'source/prepro.py::pd_colnum_bin',           'pars': {}, 'cols_family': 'colnum',     'cols_out': 'colnum_bin',     'type': ''             },
            {'uri': 'source/prepro.py::pd_colcat_bin',           'pars': {}, 'cols_family': 'colcat',     'cols_out': 'colcat_bin',     'type': ''             },
        ],
        }
        },

    'compute_pars': { 'metric_list': ['accuracy_score','average_precision_score'],
                      'compute_pars' : {'epochs': 1 },
                    },

    'data_pars': { 'n_sample' : n_sample,
        'download_pars' : None,
        'cols_input_type' : {
            'colcat' : colcat,
            'colnum' : colnum,
            'coly'  :  coly,
        },
        ### family of columns for MODEL  #########################################################
        'cols_model_group': [ 'colnum_bin',   'colcat_bin',  ],

        ### Added continuous & sparse features groups ###
        'cols_model_type2': {
            'colcontinuous':   colnum ,
            'colsparse' :      colcat,
        }

        ### Filter data rows   ##################################################################
        ,'filter_pars': { 'ymax' : 2 ,'ymin' : -1 }


        ##### Data Flow ##############################################
        ,'train':   {'Xtrain': X_train,  'ytrain': y_train, 'Xtest':  X_valid,  'ytest':  y_valid}
        ,'eval':    {'X': X_valid,  'y': y_valid}
        ,'predict': {}

        ,'task_type' : 'train', 'data_type': 'ram'

        }
    }

    ###  Tester #########################################################
    test_helper(m['model_pars'], m['data_pars'], m['compute_pars'])


def test4(n_sample = 1000):
    """function test4.
    """
    global model, session
    root  = "ztmp/"
    from sdv.demo import load_tabular_demo
    from sdv.constraints import Unique

    data = load_tabular_demo('student_placements')
    #####################################################################
    colid = 'student_id'

    unique_employee_student_id_constraint = Unique(column_names=['student_id'])

    constraints = [unique_employee_student_id_constraint]
    models = {
        'CTGAN': {'model_class': 'CTGAN',
                  'model_pars': {
                      ## CTGAN
                     'primary_key': colid,
                     'epochs': 1,
                     'anonymize_fields': {},
                     'batch_size' :100,
                     'generator_dim' : (256, 256, 256),
                     'discriminator_dim' : (256, 256, 256),
                     'constraints':constraints
                },
                },
        'TVAE': {'model_class': 'TVAE',
                  'model_pars': { 
                      ## TVAE
                     'primary_key': colid,
                     'epochs': 1,
                     'batch_size' :100,
                },
                },
              }

    ###############################################################################

    n_sample = 100
    data_col = {'cols':list(data.columns)}
    data_pars = {'n_sample': n_sample,
                'cols_model_type2' : data_col
                }
    compute_pars = { 'compute_pars' : {},
                     'metrics_pars' : {'metrics' :['CSTest', 'KSTest'], 'aggregate':False}
                   }

    data_pars['gen_samp'] =   {'Xtrain': data}
    data_pars['eval']     =   {'X': data, 'y': None}

    test_helper(models['CTGAN'], data_pars, compute_pars, task_type = "gen_samp")




def test5(n_sample = 1000):
    """function test5.
    """
    global model, session
    root  = "ztmp/"
    from sdv.metrics.demos import load_timeseries_demo

    #####################################################################

    data, _ , metadata = load_timeseries_demo()
    entity_columns = ['store_id']
    context_columns = ['region']
    sequence_index  = 'date'

    n_sample = 1
    data_col = {'cols':list(data.columns)}
    data_pars = {'n_sample': n_sample,
                'cols_model_type2' : data_col }
    data_pars['gen_samp'] =   {'Xtrain': data}

    data_pars['eval']     =   {'X': data, 'y': None}

    #####################################################################
    models = {
        'PAR': {'model_class': 'PAR',
                  'model_pars': {
                     ## PAR
                     'epochs': 1,
                     'entity_columns':  entity_columns,
                     'context_columns': context_columns,
                     'sequence_index':  sequence_index
                                },
                }
              }

    ###############################################################################
    compute_pars = { 'compute_pars' : {},
                     'metadata'     :  metadata,
                     'target'       :  'region',
                     'metrics_pars' : {'metrics' :['TSFClassifierEfficacy','LSTMClassifierEfficacy']},
                     'metric_type'  : 'timeseries',
                     'n_sample_generation' : n_sample
                   }


    #####################################################################
    test_helper(models['PAR'], data_pars, compute_pars, task_type = "gen_samp")

def test6():
    """function test6.
    """
    import sdv

    #####################################################################
    root   = "ztmp/"
    dirout = "ztmp/"

    data  = sdv.demo.load_tabular_demo('student_placements')
    colid = 'student_id'

    rule_unique_employee_student_id = sdv.constraints.Unique(column_names=['student_id'])
    constraints = [rule_unique_employee_student_id]


    model_pars = {'model_class': 'CTGAN',
                'model_pars': {
                      ## CTGAN
                     'primary_key': colid,
                     'epochs': 1,
                     'anonymize_fields': {},
                     'batch_size' :100,
                     'generator_dim' : (256, 256, 256),
                     'discriminator_dim' : (256, 256, 256),
                     'constraints':constraints
                                 },
                }

    compute_pars = { 'compute_pars' : {},
                     'metrics_pars' : {'metrics' :['CSTest', 'KSTest'], 'aggregate':False}
                   }

    generator_train_save(dirin_or_df= data, dirout=root, model_pars=model_pars, compute_pars=compute_pars)
    generator_load_generate(dirmodel=root, compute_pars= compute_pars, dirout=dirout)


def test7():
    """function test7
    Doc:: Generating synthetic samples of tabular Custom DataSet
    """

    #####################################################################
    root   = "ztmp/"
    dirout = "ztmp/"

    import wget
    import csv

    fname = os.path.join(root,"mlb_players.csv")

    if os.path.exists(fname) == False:
       ###Downloading tabular dataset
       wget.download("https://people.sc.fsu.edu/~jburkardt/data/csv/mlb_players.csv",out = root+"mlb_players.csv")
    
    assert(os.path.exists(fname) == True)
    data = pd_read_file(fname, quoting=csv.QUOTE_NONE, encoding='utf-8')
    #####################################################################
    colid = '"Name"'   #Column Name 

    model_pars = {'model_class': 'CTGAN',
                'model_pars': {
                      ## CTGAN
                     'primary_key': colid,
                     'epochs': 1,
                     'anonymize_fields': {},
                     'batch_size' :100,
                     'generator_dim' : (256, 256, 256),
                     'discriminator_dim' : (256, 256, 256),
                                 },
                }

    compute_pars = { 'compute_pars' : {},
                     'metrics_pars' : {'metrics' :['CSTest', 'KSTest'], 'aggregate':False}
                   }

    generator_train_save(dirin_or_df= data, dirout=root, model_pars=model_pars, compute_pars=compute_pars)
    generator_load_generate(dirmodel=root, compute_pars= compute_pars, dirout=dirout)


def test8():
    """function test8
    Doc:: Generating synthetic samples of tabular OpneBadit DataSet 
    """

    #####################################################################
    root   = "ztmp/"

    dataset_url = "https://research.zozo.com/data_release/open_bandit_dataset.zip"
    fname = "open_bandit_dataset/bts/men/men.csv"

    if os.path.exists(fname) == False:
       ###Downloading tabular dataset
       from utilmy.deeplearning.ttorch import  util_torch as ut
       dataset_path = ut.dataset_download(dataset_url, dirout='./')


    assert(os.path.exists(fname) == True)
    df      = pd.read_csv(fname)
    data    = df.loc[0:5000]

    #####################################################################
    colid = 'Unnamed: 0'   #Column Name 

    model_pars = {'model_class': 'CTGAN',
                'model_pars': {
                      ## CTGAN
                     'primary_key': colid,
                     'epochs': 1,
                     'anonymize_fields': {},
                     'batch_size' :100,
                     'generator_dim' : (256, 256, 256),
                     'discriminator_dim' : (256, 256, 256),
                                 },
                }

    compute_pars = { 'compute_pars' : {},
                     'metrics_pars' : {'metrics' :['CSTest', 'KSTest'], 'aggregate':False}
                   }

    generator_train_save(dirin_or_df= data, dirout=root, model_pars=model_pars, compute_pars=compute_pars)
    Xnew = generator_load_generate(dirmodel=root, compute_pars= compute_pars, dirout=None)
    log(evaluate(Xnew=Xnew, Xtrue=data, compute_pars=compute_pars))    


def test_helper(model_pars:dict, data_pars:dict, compute_pars:dict, task_type = "train"):
    """function RUN the model test_helper.
    Doc::                
    """
    global model, session
    root  = "ztmp/"
    model = Model(model_pars=model_pars, data_pars=data_pars, compute_pars=compute_pars)

    log('Training the model')
    fit(data_pars=data_pars, compute_pars=compute_pars, out_pars=None, task_type = task_type)

    log('Predict data..')
    Xnew = transform(Xpred=None, data_pars=data_pars, compute_pars=compute_pars)
    Xval, yval         = get_dataset(data_pars, task_type="eval")
    log(f'Xnew', Xnew)

    log('Evaluating the model..')
    log(evaluate(Xnew=Xnew, Xtrue=Xval, compute_pars=compute_pars))

    log('Saving model..')
    save(path= root + '/model_dir/')

    log('Load model..')
    model, session = load_model(path= root + "/model_dir/")
    log(model)


###############################################################################################
############### Wrapper #######################################################################
def generator_train_save(dirin_or_df="", dirout="",

                         model_pars:dict=None,  model_class = 'CTGAN',  model_class_pars = None,
                         compute_pars:dict=None,
                         metrics_pars =None,

                         n_sample=1000,
                         cols = None,
                         ):
    """ Data Generator Wrapper to train/save
    Docs::
        root   = "ztmp/"
        dirout = "ztmp/"
        data  = sdv.demo.load_tabular_demo('student_placements')
        colid = 'student_id'
        rule_unique_employee_student_id = sdv.constraints.Unique(column_names=['student_id'])
        constraints = [rule_unique_employee_student_id]
        model_pars = {'model_class': 'CTGAN',
                    'model_pars': {
                          ## CTGAN
                         'primary_key': colid,
                         'epochs': 1,
                         'anonymize_fields': {},
                         'batch_size' :100,
                         'generator_dim' : (256, 256, 256),
                         'discriminator_dim' : (256, 256, 256),
                         'constraints':constraints
                                     },
                    }
        compute_pars = { 'compute_pars' : {},
                         'metrics_pars' : {'metrics' :['CSTest', 'KSTest'], 'aggregate':False}
                       }
        generator_train_save(dirin_or_df= data, dirout=root, model_pars=model_pars, compute_pars=compute_pars)
    """
    global model, session


    df = pd_read_file(dirin_or_df)


    if model_pars  is None :
        model_pars = {'model_class': model_class,
                      'model_pars':  model_class_pars  }

    if compute_pars  is None :
        compute_pars = { 'compute_pars' : {}, 'metrics_pars' : metrics_pars   }


    data_pars    =   {}
    data_pars['cols_model_type2'] = {'cols':list(df.columns) if cols is None else cols }
    data_pars['gen_samp']         = {'Xtrain': df}
    data_pars['eval']             = {'X': df, 'y': None}
    data_pars['n_sample']         =  n_sample




    model = Model(model_pars=model_pars, data_pars=data_pars, compute_pars=compute_pars)

    log('Train model')
    fit(data_pars=data_pars, compute_pars=compute_pars, out_pars=None, task_type='gen_samp')

    log('Predict data..')
    Xnew = transform(Xpred=None, data_pars=data_pars, compute_pars=compute_pars)
    Xval, yval         = get_dataset(data_pars, task_type="eval")
    log(f'Xnew', Xnew)

    log('Evaluating the model..')
    log(evaluate(Xnew=Xnew, Xtrue=Xval, compute_pars=compute_pars))

    log('Save model..')
    save(path= dirout)


def generator_load_generate(dirmodel="", compute_pars:dict=None, dirout:str=None):
    """ Data genrator to load/generate
    Docs::
        root   = "ztmp/"
        dirout = "ztmp/"
        compute_pars = { 'compute_pars' : {},
                         'metrics_pars' : {'metrics' :['CSTest', 'KSTest'], 'aggregate':False}
                       }
        generator_load_generate(dirmodel=root, compute_pars= compute_pars, dirout=dirout)
    """
    global model, session



    log('Load model..')
    model, session = load_model(path= dirmodel)
    log(model)

    Xnew = transform(Xpred=None, compute_pars=compute_pars)

    if dirout is not None :
        pd_to_file(Xnew, dirout, show=1)
    else :
        return Xnew

############### Model #########################################################################
class Model(object):
    def __init__(self, model_pars=None, data_pars=None, compute_pars=None):
        """ Model:__init__.
        Doc::
                
                    Args:
                        model_pars:     
                        data_pars:     
                        compute_pars:      
                    Returns:
                       
        """
        self.model_pars, self.compute_pars, self.data_pars = model_pars, compute_pars, data_pars

        if model_pars is None:
            self.model = None
        else:
            try:
                model_class = MODEL_LIST[model_pars['model_class']]
            except Exception as e:
                raise KeyError("Please add model_class to MODEL_LIST")
            self.model  = model_class(**model_pars['model_pars'])
            log2(model_class, self.model)


def fit(data_pars: dict=None, compute_pars: dict=None, task_type = "train",**kw):
    """            
    """
    global model, session
    session = None  # Session type for compute
    Xtrain_tuple, ytrain, Xtest_tuple, ytest = get_dataset(data_pars, task_type=task_type)

    cpars = copy.deepcopy(compute_pars.get("compute_pars", {}))
    log('cpars', cpars)

    if ytrain is not None and model.model_pars['model_class'] not in SDV_MODELS :  ###with label
       model.model.fit(Xtrain_tuple, ytrain, **cpars)
    else :
       model.model.fit(Xtrain_tuple, **cpars)


def evaluate(Xnew = None, Xtrue = None, compute_pars:dict=None, metrics=None, metric_type=None):
    """ Return metrics of the model when fitted.
    Docs::
        Single Table Metrics
        https://github.com/sdv-dev/SDMetrics/tree/master/sdmetrics/single_table
        from sdmetrics.single_table import SingleTableMetric
        SingleTableMetric.get_subclasses()
        {'BNLogLikelihood'                 : sdmetrics.single_table.bayesian_network.BNLogLikelihood,
        'LogisticDetection'                : sdmetrics.single_table.detection.sklearn.LogisticDetection,
        'SVCDetection'                     : sdmetrics.single_table.detection.sklearn.SVCDetection,
        'BinaryDecisionTreeClassifier'     : sdmetrics.single_table.efficacy.binary.BinaryDecisionTreeClassifier,
        'BinaryAdaBoostClassifier'         : sdmetrics.single_table.efficacy.binary.BinaryAdaBoostClassifier,
        'BinaryLogisticRegression'         : sdmetrics.single_table.efficacy.binary.BinaryLogisticRegression,
        'BinaryMLPClassifier'              : sdmetrics.single_table.efficacy.binary.BinaryMLPClassifier,
        'MulticlassDecisionTreeClassifier' : sdmetrics.single_table.efficacy.multiclass.MulticlassDecisionTreeClassifier,
        'MulticlassMLPClassifier'          : sdmetrics.single_table.efficacy.multiclass.MulticlassMLPClassifier,
        'LinearRegression'                 : sdmetrics.single_table.efficacy.regression.LinearRegression,
        'MLPRegressor'                     : sdmetrics.single_table.efficacy.regression.MLPRegressor,
        'GMLogLikelihood'                  : sdmetrics.single_table.gaussian_mixture.GMLogLikelihood,
        'CSTest'                           : sdmetrics.single_table.multi_single_column.CSTest,
        'KSComplement'                     : sdmetrics.single_table.multi_single_column.KSComplement,
        'ContinuousKLDivergence'           : sdmetrics.single_table.multi_column_pairs.ContinuousKLDivergence,
        'DiscreteKLDivergence'             : sdmetrics.single_table.multi_column_pairs.DiscreteKLDivergence,
        'CategoricalCAP'                   : sdmetrics.single_table.privacy.cap,
        'CategoricalGeneralizedCAP'        : sdmetrics.single_table.privacy.cap,
        'CategoricalZeroCAP'               : sdmetrics.single_table.privacy.cap,
        'CategoricalKNN'                   : sdmetrics.single_table.privacy.cap,
        'CategoricalNB'                    : sdmetrics.single_table.privacy.cap,
        'CategoricalRF'                    : sdmetrics.single_table.privacy.cap,
        'CategoricalEnsemble'              : sdmetrics.single_table.privacy.ensemble,
        'NumericalLR'                      : sdmetrics.single_table.privacy.numerical_sklearn,
        'NumericalMLP'                     : sdmetrics.single_table.privacy.numerical_sklearn,
        'NumericalSVR'                     : sdmetrics.single_table.privacy.numerical_sklearn,
        'NumericalRadiusNearestNeighbor'   : sdmetrics.single_table.privacy.radius_nearest_neighbor}
        -------------------------------------------------------------------------------------
        https://github.com/sdv-dev/SDMetrics/tree/master/sdmetrics/timeseries
        from sdmetrics.timeseries import TimeSeriesMetric
        TimeSeriesMetric.get_subclasses()
        {'LSTMDetection': sdmetrics.timeseries.detection.LSTMDetection}
        -------------------------------------------------------------------------------------
        In [13]: sdv.evaluation.evaluate(synthetic_data, real_data, metrics=['CSTest'], aggregate=False)
        Out[13]:
           metric         name  raw_score  normalized_score  min_value  max_value      goal error
        0  CSTest  Chi-Squared   0.948027          0.948027        0.0        1.0  MAXIMIZE  None
    """
    compute_pars = {} if compute_pars is None else compute_pars

    mpars            = compute_pars.get("metrics_pars", {'aggregate': False, 'metrics': [ 'CSTest' ]  })
    mpars['metrics'] = metrics if metrics is not None else mpars['metrics']
    metric_type      = compute_pars.get("metric_type", 'tabular') if metric_type is None else metric_type
    metadata         = compute_pars.get('metadata', {})


    if  metric_type == 'timeseries':
        target = compute_pars.get("target", None)
        evals = evaluate_timeseries(Xnew, Xtrue, metadata = metadata, target=target, **mpars, )

    else :
        ###
        evals = sdv.evaluation.evaluate(Xnew, Xtrue, **mpars)

    return evals



def evaluate_timeseries(synthetic_data, real_data=None, metadata=None, metrics=None, target="y", **kw):
    """ Return metrics of the model for Time series data.
    """
    from sdv.metrics.timeseries import TSFClassifierEfficacy, LSTMClassifierEfficacy
    ML_EFF_METRICS = { 'TSFClassifierEfficacy'   :TSFClassifierEfficacy,
                       'LSTMClassifierEfficacy'  :LSTMClassifierEfficacy
                     }
    evals = []
    for m in metrics:
        metric = ML_EFF_METRICS[m]
        evals.append(metric.compute(real_data, synthetic_data, metadata=metadata, target=target))
    
    df = pd.DataFrame(columns=['metrics','scores'])
    df['metrics'] = metrics
    df['scores']  = evals
    return df


def transform(Xpred=None, data_pars: dict=None, compute_pars: dict=None, out_pars: dict=None, **kw):
    """ Geenrate Xtrain  ----> Xtrain_new.
    Doc::
            
            Xpred:
                Xpred ==> None            if you want to get generated samples by by SDV models
                      ==> tuple of (x, y) if you want to resample dataset with IMBLEARN models
                      ==> dataframe       if you want to transorm by sklearn models like TruncatedSVD
            data_pars:
            compute_pars:
            out_pars:
            kw:
    """
    global model, session
    name = model.model_pars['model_class']

    #######
    if name in IMBLEARN_MODELS:
        if Xpred is None:
            Xpred_tuple, y = get_dataset(data_pars, task_type="eval")
        else :
            cols_type         = data_pars['cols_model_type2']
            cols_ref_formodel = cols_type  ### Always match with feeded cols_type
            split             = kw.get("split", False)
            if isinstance(Xpred, tuple) and len(Xpred) == 2:
                x, y = Xpred
                Xpred_tuple = get_dataset_tuple(x, cols_type, cols_ref_formodel, split)
            else:
                raise  Exception(f"IMBLEARN MODELS need to pass x, y to resample,you have to pass them as tuple => Xpred = (x, y)")

        Xnew = model.model.fit_resample( Xpred_tuple, y, **compute_pars.get('compute_pars', {}) )
        log3("generated data", Xnew)
        return Xnew


    if name in SDV_MODELS :
        Xnew = model.model.sample(compute_pars.get('n_sample_generation', 100) )
        log3("generated data", Xnew)
        return Xnew


    else :
       if Xpred is None:
            Xpred_tuple, y = get_dataset(data_pars, task_type="eval")
       else :
            cols_type         = data_pars['cols_model_type2']
            cols_ref_formodel = cols_type  ### Always match with feeded cols_type
            split             = kw.get("split", False)
            Xpred_tuple       = get_dataset_tuple(Xpred, cols_type, cols_ref_formodel, split)

       Xnew = model.model.transform( Xpred_tuple, **compute_pars.get('compute_pars', {}) )
       log3("generated data", Xnew)
       return Xnew


def predict(Xpred=None, data_pars: dict=None, compute_pars: dict=None, out_pars: dict=None, **kw):
    """function predict.
    Doc::
            
            Args:
                Xpred:   
                data_pars:   
                compute_pars:   
                out_pars:   
                **kw:   
            Returns:
                
    """
    global model, session
    pass
    ### No need


#################### util #############################################################
def save(path=None, info=None):
    """function save.
    Doc::
            Args:
                path:
                info:
            Returns:
                
    """
    global model, session
    import cloudpickle as pickle
    os.makedirs(path, exist_ok=True)

    filename = "model.pkl"
    pickle.dump(model, open(f"{path}/{filename}", mode='wb'))  # , protocol=pickle.HIGHEST_PROTOCOL )

    filename = "info.pkl"
    pickle.dump(info, open(f"{path}/{filename}", mode='wb'))   # ,protocol=pickle.HIGHEST_PROTOCOL )


def load_model(path=""):
    """function load_model.
    Doc::
            
            Args:
                path:   
            Returns:
                
    """
    global model, session
    import cloudpickle as pickle
    model0 = pickle.load(open(f"{path}/model.pkl", mode='rb'))

    model = Model()  # Empty model
    model.model        = model0.model
    model.model_pars   = model0.model_pars
    model.compute_pars = model0.compute_pars
    session = None
    return model, session


def load_info(path=""):
    """function load_info.
    Doc::
            
            Args:
                path:   
            Returns:
                
    """
    import cloudpickle as pickle, glob
    dd = {}
    for fp in glob.glob(f"{path}/*.pkl"):
        if not "model.pkl" in fp:
            obj = pickle.load(open(fp, mode='rb'))
            key = fp.split("/")[-1]
            dd[key] = obj
    return dd


############# Dataset ##############################################################################
def get_dataset_load(df_or_path):
   """ Load the data into dataframe
   """
   if isinstance(df_or_path, pd.DataFrame):
      return df_or_path

   elif isinstance(df_or_path, str):
      from utilmy import pd_read_file
      df = pd_read_file(df_or_path)
      return df


def get_dataset_tuple(Xtrain, cols_type_received, cols_ref, split=False):
    """  Split into Tuples = (df1, df2, df3) to feed model, (ie Keras).
    Doc::
            
            Xtrain:
            cols_type_received:
            cols_ref:
            split: 
                True :  split data to list of dataframe 
                False:  return same input of data
            :return:
    """
    if len(cols_ref) <= 1  or not split :
        return Xtrain
        
    Xtuple_train = []
    for cols_groupname in cols_ref :
        assert cols_groupname in cols_type_received, "Error missing colgroup in config data_pars[cols_model_type] "
        cols_i = cols_type_received[cols_groupname]
        Xtuple_train.append( Xtrain[cols_i] )

    return Xtuple_train


def get_dataset(data_pars=None, task_type="train", **kw):
    """.
    Doc::
            
              return tuple of dataframes OR single dataframe
    """
    #### log(data_pars)
    data_type = data_pars.get('type', 'ram')

    ### Sparse columns, Dense Columns
    cols_type_received     = data_pars.get('cols_model_type2', {} )
    cols_ref  = list( cols_type_received.keys())
    split = kw.get('split', False)

    if data_type == "ram":
        # cols_ref_formodel = ['cols_cross_input', 'cols_deep_input', 'cols_deep_input' ]
        ### dict  colgroup ---> list of colname
        cols_type_received     = data_pars.get('cols_model_type2', {} )

        if task_type == "predict":
            d = data_pars[task_type]
            Xtrain       = get_dataset_load( d["X"] )
            Xtuple_train = get_dataset_tuple(Xtrain, cols_type_received, cols_ref, split)
            return Xtuple_train

        if task_type == "eval":
            d = data_pars[task_type]
            Xtrain, ytrain  = get_dataset_load( d["X"]), None if d['y'] is None else get_dataset_load( d["y"] )
            Xtuple_train    = get_dataset_tuple(Xtrain, cols_type_received, cols_ref, split)
            return Xtuple_train, ytrain

        if task_type == "train":
            d = data_pars[task_type]
            Xtrain, ytrain, Xtest, ytest  = get_dataset_load( d["Xtrain"]), get_dataset_load( d["ytrain"]),  get_dataset_load( d["Xtest"]), get_dataset_load( d["ytest"] )

            ### dict  colgroup ---> list of df
            Xtuple_train = get_dataset_tuple(Xtrain, cols_type_received, cols_ref, split )
            Xtuple_test  = get_dataset_tuple(Xtest,  cols_type_received, cols_ref, split )
            log2("Xtuple_train", Xtuple_train)

            return Xtuple_train, ytrain, Xtuple_test, ytest

        if task_type == "gen_samp":
            d = data_pars[task_type]
            Xtrain = get_dataset_load( d["Xtrain"])

            ### dict  colgroup ---> list of df
            Xtuple_train = get_dataset_tuple(Xtrain, cols_type_received, cols_ref, split )
            log2("Xtuple_train", Xtuple_train)

            return Xtuple_train, None, None, None

    elif data_type == "file":
        raise Exception(f' {data_type} data_type Not implemented ')

    raise Exception(f' Requires  Xtrain", "Xtest", "ytrain", "ytest" ')




if __name__ == "__main__":
    #from pyinstrument import Profiler;  profiler = Profiler() ; profiler.start()
    import fire
    fire.Fire()
    #profiler.stop() ; print(profiler.output_text(unicode=True, color=True))
    test4()
    test5()
    test6()
    test7()
    test8()
    
#test9()  -- error at evaluation phase
##Exception has occurred: ValueError  
##all input arrays must have the same shape
###***STEPS****
# 1. Downloaded the open-bandit dataclass
# 2. Created the metadata information(manually)
# 3. With PAR, facing runtime issue(Shape error)  

##Note: there is no partiular information about context columns, tried different columns as
# context column but faced the same issue


# def test9():
#     """function test9
#     Doc:: Generating synthetic samples of tabular OpneBadit DataSet 
#     """

#     #####################################################################
#     root   = "ztmp/"

#     dataset_url = "https://research.zozo.com/data_release/open_bandit_dataset.zip"
#     fname = "open_bandit_dataset/bts/men/men.csv"

#     if os.path.exists(fname) == False:
#        ###Downloading tabular dataset
#        from utilmy.deeplearning.ttorch import  util_torch as ut
#        dataset_path = ut.dataset_download(dataset_url, dirout='./')


#     assert(os.path.exists(fname) == True)
#     df      = pd.read_csv(fname)
#     n_sample = 1
#     data    = df.loc[0:100]



#     #####################################################################

#     metadata = {'fields': {
#         'position': {'type': 'categorical'},
#         'item_id': {'type': 'numerical', 'subtype': 'integer'},
#         'click': {'type': 'numerical', 'subtype': 'integer'},
#         'timestamp': {'type': 'datetime'},
#         'user_feature_0' : {'type': 'categorical'},
#         'propensity_score': {'type': 'numerical', 'subtype': 'float'},
#         },
#         'entity_columns': ['item_id'], 
#         'sequence_index': 'timestamp',
#         # 'context_columns': ['position']
#         }

#     entity_columns = ['item_id']
#     # context_columns = ['position']
#     sequence_index  = 'timestamp'

#     data  = data[list(metadata['fields'].keys())[0:6]]
#     data_col = {'cols':list(metadata['fields'].keys())[0:6]}
#     data_pars = {'cols_model_type2' : data_col }
#     data_pars['gen_samp'] =   {'Xtrain': data}
#     data_pars['eval']     =   {'X': data, 'y': None}

#     models = {
#         'PAR': {'model_class': 'PAR',
#                   'model_pars': {
#                      ## PAR
#                      'epochs': 1,
#                      'entity_columns':  entity_columns,
#                     #  'context_columns': context_columns,
#                     #  'sequence_index':  sequence_index
#                                 },
#                 }
#               }

#     compute_pars = { 'compute_pars' : {},
#                      'metadata'     :  metadata,
#                      'target'       :  'user_feature_0',
#                      'metrics_pars' : {'metrics' :['TSFClassifierEfficacy','LSTMClassifierEfficacy']},
#                      'metric_type'  : 'timeseries',
#                      'n_sample_generation' : n_sample
#                    }

#     #####################################################################
#     test_helper(models['PAR'], data_pars, compute_pars, task_type = "gen_samp")











"""
def test_dataset_classi_fake(nrows=500):
    from sklearn import datasets as sklearn_datasets
    ndim=11
    coly   = 'y'
    colnum = ["colnum_" +str(i) for i in range(0, ndim) ]
    colcat = ['colcat_1']
    X, y    = sklearn_datasets.make_classification(
              n_samples=10000, n_features=ndim, n_classes=1, n_redundant = 0, n_informative=ndim )
    df = pd.DataFrame(X,  columns= colnum)
    for ci in colcat :
      df[ci] = np.random.randint(0,1, len(df))
    df[coly]   = y.reshape(-1, 1)
    # log(df)
    return df, colnum, colcat, coly
def train_test_split2(df, coly):
    from sklearn.model_selection import train_test_split
    log3(df.dtypes)
    y = df[coly] ### If clonassificati
    X = df.drop(coly,  axis=1)
    log3('y', np.sum(y[y==1]) , X.head(3))
    ######### Split the df into train/test subsets
    X_train_full, X_test, y_train_full, y_test = train_test_split(X, y, test_size=0.05, random_state=2021)
    X_train, X_valid, y_train, y_valid         = train_test_split(X_train_full, y_train_full, random_state=2021)
    #####
    # y = y.astype('uint8')
    num_classes                                = len(set(y_train_full.values.ravel()))
    return X,y, X_train, X_valid, y_train, y_valid, X_test,  y_test, num_classes
"""








#########################  Second Part ###############################
######################### Useful Funciton ###############################
def zz_pd_sample_imblearn(df=None, col=None, pars=None):
    """.
    Doc::
            
                Over-sample
    """
    params_check(pars, ['model_name', 'pars_resample', 'coly']) # , 'dfy'
    prefix = '_sample_imblearn'

    ######################################################################################
    from imblearn.over_sampling import SMOTE
    from imblearn.combine import SMOTEENN, SMOTETomek
    from imblearn.under_sampling import NearMiss

    # model_resample = { 'SMOTE' : SMOTE, 'SMOTEENN': SMOTEENN }[  pars.get("model_name", 'SMOTEENN') ]
    model_resample = locals()[  pars.get("model_name", 'SMOTEENN')  ]
    pars_resample  = pars.get('pars_resample',
                             {'sampling_strategy' : 'auto', 'random_state':0}) # , 'n_jobs': 2

    if 'path_pipeline' in pars :   #### Inference time
        return df, {'col_new': col }

    else :     ### Training time
        colX    = col # [col_ for col_ in col if col_ not in coly]
        coly    = pars['coly']
        train_y = pars['dfy']  ## df[coly] #
        train_X = df[colX].fillna(method='ffill')
        gp      = model_resample( **pars_resample)
        X_resample, y_resample = gp.fit_resample(train_X, train_y)

        col_new   = [ t + f"_{prefix}" for t in col ]
        df2       = pd.DataFrame(X_resample, columns = col_new) # , index=train_X.index
        df2[coly] = y_resample

    ###################################################################################
    if 'path_features_store' in pars and 'path_pipeline_export' in pars:
       save_features(df2, prefix.replace("col_", "df_"), pars['path_features_store'])
       save(gp,             pars['path_pipeline_export'] + f"/{prefix}_model.pkl" )
       save(col,            pars['path_pipeline_export'] + f"/{prefix}.pkl" )
       save(pars_resample,  pars['path_pipeline_export'] + f"/{prefix}_pars.pkl" )


    col_pars = {'prefix' : prefix , 'path' :   pars.get('path_pipeline_export', pars.get('path_pipeline', None)) }
    col_pars['cols_new'] = {
       prefix :  col_new  ###  for training input data
    }
    return df2, col_pars


def zz_pd_augmentation_sdv(df, col=None, pars={})  :
    '''.
    Doc::
            
            Using SDV Variation Autoencoders, the function augments more data into the dataset
            params:
                    df          : (pandas dataframe) original dataframe
                    col : column name for data enancement
                    pars        : (dict - optional) contains:
                        n_samples     : (int - optional) number of samples you would like to add, defaul is 10%
                        primary_key   : (String - optional) the primary key of dataframe
                        aggregate  : (boolean - optional) if False, prints SVD metrics, else it averages them
                        path_model_save: saving location if save_model is set to True
                        path_model_load: saved model location to skip training
                        path_data_new  : new data where saved
            returns:
                    df_new      : (pandas dataframe) df with more augmented data
                    col         : (list of strings) same columns
    '''
    n_samples       = pars.get('n_samples', max(1, int(len(df) * 0.10) ) )   ## Add 10% or 1 sample by default value
    primary_key     = pars.get('colid', None)  ### Custom can be created on the fly
    metrics_type    = pars.get('aggregate', False)
    path_model_save = pars.get('path_model_save', 'data/output/ztmp/')
    model_name      = pars.get('model_name', "TVAE")

    # model fitting
    if 'path_model_load' in pars:
            model = load(pars['path_model_load'])
    else:
            log('##### Training Started #####')

            model = {'TVAE' : TVAE, 'CTGAN' : CTGAN, 'PAR' : PAR}[model_name]
            if model_name == 'PAR':
                model = model(entity_columns = pars['entity_columns'],
                              context_columns = pars['context_columns'],
                              sequence_index = pars['sequence_index'])
            else:
                model = model(primary_key=primary_key)
            model.fit(df)
            log('##### Training Finshed #####')
            try:
                 save(model, path_model_save )
                 log('model saved at: ', path_model_save  )
            except:
                 log('saving model failed: ', path_model_save)

    log('##### Generating Samples #############')
    new_data = model.sample(n_samples)
    log_pd( new_data, n=7)


    log('######### Evaluation Results #########')
    if metrics_type == True:
      evals = evaluate(new_data, df, aggregate= True )
      log(evals)
    else:
      evals = evaluate(new_data, df, aggregate= False )
      log_pd(evals, n=7)

    # appending new data
    df_new = df.append(new_data)
    log(str(len(df_new) - len(df)) + ' new data added')

    if 'path_newdata' in pars :
        new_data.to_parquet( pars['path_newdata'] + '/features.parquet' )
        log('###### df augmentation save on disk', pars['path_newdata'] )

    log('###### augmentation complete ######')
    return df_new, col

    


####################################################################################################
####################################################################################################

from util_feature import load_function_uri, load, save_features, params_check

def zz_pd_covariate_shift_adjustment():
    """.
    Doc::
            
            https://towardsdatascience.com/understanding-dataset-shift-f2a5a262a766
             Covariate shift has been extensively studied in the literature, and a number of proposals to work under it have been published. Some of the most important ones include:
                Weighting the log-likelihood function (Shimodaira, 2000)
                Importance weighted cross-validation (Sugiyama et al, 2007 JMLR)
                Integrated optimization problem. Discriminative learning. (Bickel et al, 2009 JMRL)
                Kernel mean matching (Gretton et al., 2009)
                Adversarial search (Globerson et al, 2009)
                Frank-Wolfe algorithm (Wen et al., 2015)
    """
    import numpy as np
    from scipy import sparse
    import pylab as plt

    # .. to generate a synthetic dataset ..
    from sklearn import datasets
    n_samples, n_features = 1000, 10000
    A, b = datasets.make_regression(n_samples, n_features)
    def FW(alpha, max_iter=200, tol=1e-8):
        # .. initial estimate, could be any feasible point ..
        x_t = sparse.dok_matrix((n_features, 1))
        trace = []  # to keep track of the gap
        # .. some quantities can be precomputed ..
        Atb = A.T.dot(b)
        for it in range(max_iter):
            # .. compute gradient. Slightly more involved than usual because ..
            # .. of the use of sparse matrices ..
            Ax = x_t.T.dot(A.T).ravel()
            grad = (A.T.dot(Ax) - Atb)
            # .. the LMO results in a vector that is zero everywhere except for ..
            # .. a single index. Of this vector we only store its index and magnitude ..
            idx_oracle = np.argmax(np.abs(grad))
            mag_oracle = alpha * np.sign(-grad[idx_oracle])
            g_t = x_t.T.dot(grad).ravel() - grad[idx_oracle] * mag_oracle
            trace.append(g_t)
            if g_t <= tol:
                break
            q_t = A[:, idx_oracle] * mag_oracle - Ax
            step_size = min(q_t.dot(b - Ax) / q_t.dot(q_t), 1.)
            x_t = (1. - step_size) * x_t
            x_t[idx_oracle] = x_t[idx_oracle] + step_size * mag_oracle
        return x_t, np.array(trace)

    # .. plot evolution of FW gap ..
    sol, trace = FW(.5 * n_features)
    plt.plot(trace)
    plt.yscale('log')
    plt.xlabel('Number of iterations')
    plt.ylabel('FW gap')
    plt.title('FW on a Lasso problem')
    plt.grid()
    plt.show()
    sparsity = np.mean(sol.toarray().ravel() != 0)
    print('Sparsity of solution: %s%%' % (sparsity * 100))


########################################################################################
########################################################################################
def zz_test():
    """function zz_test.
    Doc::
            
            Args:
            Returns:
                
    """
    from util_feature import test_get_classification_data
    dfX, dfy = test_get_classification_data()
    cols     = list(dfX.columsn)
    ll       = [ ('pd_sample_imblearn', {}  )


               ]

    for fname, pars in ll :
        myfun = globals()[fname]
        res   = myfun(dfX, cols, pars)
    
    
"""
def pd_generic_transform(df, col=None, pars={}, model=None)  :
 
     Transform or Samples using  model.fit()   model.sample()  or model.transform()
    params:
            df    : (pandas dataframe) original dataframe
            col   : column name for data enancement
            pars  : (dict - optional) contains:                                          
                path_model_save: saving location if save_model is set to True
                path_model_load: saved model location to skip training
                path_data_new  : new data where saved 
    returns:
            model, df_new, col, pars
   
    path_model_save = pars.get('path_model_save', 'data/output/ztmp/')
    pars_model      = pars.get('pars_model', {} )
    model_method    = pars.get('method', 'transform')
    
    # model fitting 
    if 'path_model_load' in pars:
            model = load(pars['path_model_load'])
    else:
            log('##### Training Started #####')
            model = model( **pars_model)
            model.fit(df)
            log('##### Training Finshed #####')
            try:
                 save(model, path_model_save )
                 log('model saved at: ' + path_model_save  )
            except:
                 log('saving model failed: ', path_model_save)
    log('##### Generating Samples/transform #############')    
    if model_method == 'sample' :
        n_samples =pars.get('n_samples', max(1, 0.10 * len(df) ) )
        new_data  = model.sample(n_samples)
        
    elif model_method == 'transform' :
        new_data = model.transform(df.values)
    else :
        raise Exception("Unknown", model_method)
        
    log_pd( new_data, n=7)    
    if 'path_newdata' in pars :
        new_data.to_parquet( pars['path_newdata'] + '/features.parquet' ) 
        log('###### df transform save on disk', pars['path_newdata'] )    
    
    return model, df_new, col, pars
"""