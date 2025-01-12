# pylint: disable=C0321,C0103,E1221,C0301,E1305,E1121,C0302,C0330
# -*- coding: utf-8 -*-
"""
### Usage:
  python example/test_keras_vaemdn.py  train_sampler    --config  config_sampler
  python example/test_keras_vaemdn.py  transform        --config  config_sampler

"""
import warnings, copy, os, sys
warnings.filterwarnings("ignore")

###### Path ########################################################################
root_repo      =  os.path.abspath(os.getcwd()).replace("\\", "/") + "/"     ; print(root_repo)
THIS_FILEPATH  =  os.path.abspath(__file__)

sys.path.append(root_repo)
from source.util_feature import save,os_get_function_name

def global_pars_update(model_dict,  data_name, config_name):
    """function global_pars_update.
    Doc::
            
            Args:
                model_dict:   
                data_name:   
                config_name:   
            Returns:
                
    """
    print("config_name", config_name)
    dir_data  = root_repo + "/data/"  ; print("dir_data", dir_data)

    m                      = {}
    m["config_path"]       = THIS_FILEPATH
    m["config_name"]       = config_name
    m["model_file"]        = "model_sampler"

    #### peoprocess input path
    m["path_data_preprocess"] = dir_data + f"/input/{data_name}/train/"

    #### train input path
    dir_data_url              = "https://github.com/arita37/dsa2_data/tree/master/"  #### Remote Data directory
    m["path_data_train"]      = dir_data_url + f"/input/{data_name}/train/"
    m["path_data_test"]       = dir_data_url + f"/input/{data_name}/test/"
    #m["path_data_val"]       = dir_data + f"/input/{data_name}/test/"

    #### train output path
    m["path_train_output"]    = dir_data + f"/output/{data_name}/{config_name}/"
    m["path_train_model"]     = dir_data + f"/output/{data_name}/{config_name}/model/"
    m["path_features_store"]  = dir_data + f"/output/{data_name}/{config_name}/features_store/"
    m["path_pipeline"]        = dir_data + f"/output/{data_name}/{config_name}/pipeline/"


    #### predict  input path
    m["path_pred_data"]       = dir_data + f"/input/{data_name}/test/"
    m["path_pred_pipeline"]   = dir_data + f"/output/{data_name}/{config_name}/pipeline/"
    m["path_pred_model"]      = dir_data + f"/output/{data_name}/{config_name}/model/"

    #### predict  output path
    m["path_pred_output"]     = dir_data + f"/output/{data_name}/pred_{config_name}/"

    #####  Generic
    m["n_sample"]             = model_dict["data_pars"].get("n_sample", 5000)

    model_dict[ "global_pars"] = m
    return model_dict


####################################################################################
##### Params########################################################################
config_default   = "config_sampler"    ### name of function which contains data configuration


cols_input_type_1 = {
     "coly"   :   "Survived"
    ,"colid"  :   "PassengerId"
    ,"colcat" :   ["Sex", "Embarked" ]
    ,"colnum" :   ["Pclass", "Age","SibSp", "Parch","Fare"]
    ,"coltext" :  []
    ,"coldate" :  []
    ,"colcross" : [ "Name", "Sex", "Ticket","Embarked","Pclass", "Age", "SibSp", ]
}

coly   =   "Survived"
colid  =   "PassengerId"
colcat =   ["Sex", "Embarked", "Pclass", ]
colnum =   [ "Age","SibSp", "Parch","Fare"]


####################################################################################
def config_sampler() :
    """function config_sampler.
    Doc::
            
            Args:
            Returns:
                
    """
    data_name    = "titanic"         ### in data/input/
    model_class  = "source/models/model_vaemdn.py::VAEMDN"   ### ACTUAL Class name
    n_sample     = 1000

    def post_process_fun(y):   ### After prediction is done
        return  y

    def pre_process_fun(y):    ### Before the prediction is done
        return  y


    model_dict = {
      "model_pars": {
         "model_class": model_class
        ,"model_pars" : {
            'original_dim':       len( colcat + colnum),
            'class_num':             2,
            'intermediate_dim':     64,
            'intermediate_dim_2':   16,
            'latent_dim' :           3,
            'Lambda1'    :           1,
            'batch_size' :         256,
            'Lambda2'    :         200,
            'Alpha'      :         0.075
                        }

        , "post_process_fun" : post_process_fun   ### After prediction
        , "pre_process_pars" : {
              "y_norm_fun" :  pre_process_fun ,  ### Before training
              ### Pipeline for data processing ##############################
              "pipe_list": [
                  #### coly target prorcessing
                  {"uri": "source/prepro.py::pd_coly",                 "pars": {}, "cols_family": "coly",       "cols_out": "coly",           "type": "coly"         },

                  # {"uri": "source/prepro.py::pd_colnum_bin",           "pars": {}, "cols_family": "colnum",     "cols_out": "colnum_bin",     "type": ""             },
                  # {"uri": "source/prepro.py::pd_colnum_binto_onehot",  "pars": {}, "cols_family": "colnum_bin", "cols_out": "colnum_onehot",  "type": ""             },

                  #### catcol INTO integer,   colcat into OneHot
                  {"uri": "source/prepro.py::pd_colcat_bin",           "pars": {}, "cols_family": "colcat",     "cols_out": "colcat_bin",     "type": ""             },
                  #{"uri": "source/prepro.py::pd_colcat_to_onehot",     "pars": {}, "cols_family": "colcat_bin", "cols_out": "colcat_onehot",  "type": ""             },

              ],
        }
      },

      "compute_pars": { "metric_list": ["accuracy_score","average_precision_score"],
                        # ,"mlflow_pars" : {}   ### Not empty --> use mlflow
                        'compute_pars' : {}
      },

      "data_pars": {
          "n_sample" : n_sample,
          "download_pars" : None,
          ### Filter data rows   ##################################################################
          # "filter_pars": { "ymax" : 2 ,"ymin" : -1 },

          ### Raw data:  column input ##############################################################
          "cols_input_type" :  {
            'colid'  : colid,
            'colcat' : colcat,
            'colnum' : colnum,
            'coly'  :  coly,
          },


          ### Model Input :  Merge family of columns   #############################################
          "cols_model_group": [ "colnum",
                                "colcat",
                              ]

          #### Model Input : Separate Category Sparse from Continuous : Aribitrary name is OK (!)
        ,'cols_model_type': {
            'colcontinuous':   colnum ,
            'colsparse' :      colcat,
        }
      }
    }

    ##### Filling Global parameters    ############################################################
    model_dict        = global_pars_update(model_dict, data_name, config_name=os_get_function_name() )
    return model_dict




###################################################################################
########## Preprocess #############################################################
### def preprocess(config="", nsample=1000):
from core_run import preprocess




##################################################################################
########## Train #################################################################
# train_sampler(config=None, nsample=None):
from core_run import train_sampler



####################################################################################
####### Inference ##################################################################
# transform(config='', nsample=None):
from core_run import transform



if __name__ == "__main__":
    from pyinstrument import Profiler;  profiler = Profiler() ; profiler.start()
    import fire
    fire.Fire()
    profiler.stop() ; print(profiler.output_text(unicode=True, color=True))




