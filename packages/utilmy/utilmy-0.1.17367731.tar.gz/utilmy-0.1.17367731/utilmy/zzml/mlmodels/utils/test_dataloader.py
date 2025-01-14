import os
from jsoncomment import JsonComment ; json = JsonComment()
import pandas as pd
import numpy as np
import math



from keras.preprocessing.text import Tokenizer
import keras


###########################################################################3
from mlmodels.dataloader import DataLoader
from mlmodels.util import load_callable_from_dict, path_norm, path_norm_dict
### path_norm : find the ABSOLUTE PATH of the repobby heuristic.



###########################################################################3
def pandas_split_xy(out,data_pars):
    """function pandas_split_xy.
    Doc::
            
            Args:
                out:   
                data_pars:   
            Returns:
                
    """
    X_c    = data_pars['input_pars'].get('col_Xinput',[])
    y_c    = data_pars['input_pars'].get('col_yinput',[])
    misc_c = data_pars['input_pars'].get('col_miscinput',[])
    X      = out[X_c]
    y      = out[y_c]
    if len(misc_c)>1:
        misc = out[misc_c]
        return X,y,misc
    return X,y


def pandas_load_train_test(path, test_path, **args):
    """function pandas_load_train_test.
    Doc::
            
            Args:
                path:   
                test_path:   
                **args:   
            Returns:
                
    """
    return pd.read_csv(path,**args), pd.read_csv(test_path,**args),


def rename_target_to_y(out,data_pars):
    """function rename_target_to_y.
    Doc::
            
            Args:
                out:   
                data_pars:   
            Returns:
                
    """
    X_c    = data_pars['input_pars'].get('col_Xinput',[])
    y_c    = data_pars['input_pars'].get('col_yinput',[])
    return tuple(df[X_c+y_c].rename(columns={y_c[0]:'y'}, inplace=True) for df in out)


def load_npz(path):
    """function load_npz.
    Doc::
            
            Args:
                path:   
            Returns:
                
    """
    npz = np.load(path, allow_pickle=True)
    return tuple(npz[x] for x in sorted(npz.files))


def split_xy_from_dict(out, **kwargs):
    """function split_xy_from_dict.
    Doc::
            
            Args:
                out:   
                **kwargs:   
            Returns:
                
    """
    X_c    = kwargs.get('col_Xinput',[])
    y_c    = kwargs.get('col_yinput',[])
    X      = [out[n] for n in X_c]
    y      = [out[n] for n in y_c]
    return (*X,*y)
    
def split_timeseries_df(out,data_pars,length,shift):
    """function split_timeseries_df.
    Doc::
            
            Args:
                out:   
                data_pars:   
                length:   
                shift:   
            Returns:
                
    """
    X_c    = data_pars['input_pars'].get('col_Xinput',[])
    y_c    = data_pars['input_pars'].get('col_yinput',[])
    end_ind = len(out.index) - (len(out.index)%length)
    X      = out[X_c].values[:end_ind].reshape(-1,length,len(X_c))
    y      = out[y_c].shift(shift).fillna(0).values[:end_ind].reshape(X.shape[0],X.shape[1],1)
    return X,y
    
def gluon_append_target_string(out,data_pars):
    """function gluon_append_target_string.
    Doc::
            
            Args:
                out:   
                data_pars:   
            Returns:
                
    """
    return out, data_pars['input_pars'].get('col_yinput')[0]

def identical_test_set_split(*args,test_size,**kwargs):
    """function identical_test_set_split.
    Doc::
            
            Args:
                *args:   
                test_size:   
                **kwargs:   
            Returns:
                
    """
    return (*args,*args)

def read_csvs_from_directory(path,files=None,**args):
    """function read_csvs_from_directory.
    Doc::
            
            Args:
                path:   
                files:   
                **args:   
            Returns:
                
    """
    f = [x for x in os.listdir(path) if '.csv' in x] if files is None else [path+'/'+x for x in files]
    return (pd.read_csv(x,**args) for x in f)

def tokenize_x(data,no_classes,max_words=None):
    """function tokenize_x.
    Doc::
            
            Args:
                data:   
                no_classes:   
                max_words:   
            Returns:
                
    """
    if max_words is None:
        max_words = data[0].size
    t = Tokenizer(num_words=max_words)
    return t.sequences_to_matrix(data[0], mode='binary'), keras.utils.to_categorical(data[1], no_classes)

def timeseries_split(*args,test_size=0.2):
    """function timeseries_split.
    Doc::
            
            Args:
                *args:   
                test_size:   
            Returns:
                
    """
    train = []
    test = []
    index = math.floor(len(args[0])*(1-test_size))
    for data in args:
        train.append(data[:index])
        test.append(data[index:])
    return (*train, *test)


class SingleFunctionPreprocessor:
    def __init__(self,func_dict):
        """ SingleFunctionPreprocessor:__init__.
        Doc::
                
                    Args:
                        func_dict:     
                    Returns:
                       
        """
        func, args = load_callable_from_dict(func_dict)
        self.func = func
        self.args = args
    def compute(self,data):
        """ SingleFunctionPreprocessor:compute.
        Doc::
                
                    Args:
                        data:     
                    Returns:
                       
        """
        self.data = self.func(data,**self.args)
    def get_data(self):
        """ SingleFunctionPreprocessor:get_data.
        Doc::
                
                    Args:
                    Returns:
                       
        """
        return self.data


if __name__ == '__main__':
    refactor_path = path_norm('dataset/json/refactor/' )
    data_pars_list = [(f,json.loads(open(refactor_path+f).read())['test']['data_pars']) for f in os.listdir(refactor_path)]
    


    for f, data_pars in data_pars_list:
        print(f)
        data_pars = path_norm_dict( data_pars)
        loader    = DataLoader(data_pars)
        loader.compute()
        print(loader.get_data())





