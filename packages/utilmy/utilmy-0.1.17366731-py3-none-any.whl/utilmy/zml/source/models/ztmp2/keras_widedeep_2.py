# pylint: disable=C0321,C0103,C0301,E1305,E1121,C0302,C0330,C0111,W0613,W0611,R1705
# -*- coding: utf-8 -*-
"""
ipython source/models/keras_widedeep.py  test  --pdb


python keras_widedeep.py  test

pip install Keras==2.4.3


"""
import os, pandas as pd, numpy as np, sklearn, copy
from sklearn.model_selection import train_test_split

import tensorflow
try :
  import keras
  from keras.callbacks import EarlyStopping, ModelCheckpoint
  from keras import layers
except :
  from tensorflow import keras
  from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
  from tensorflow.keras import layers

####################################################################################################
verbosity =2

def log(*s):
    """function log.
    Doc::
            
            Args:
                *s:   
            Returns:
                
    """
    print(*s, flush=True)

def log2(*s):
    """function log2.
    Doc::
            
            Args:
                *s:   
            Returns:
                
    """
    if verbosity >= 2 :
      print(*s, flush=True)


####################################################################################################
global model, session

def init(*kw, **kwargs):
    """function init.
    Doc::
            
            Args:
                *kw:   
                **kwargs:   
            Returns:
                
    """
    global model, session
    model = Model(*kw, **kwargs)
    session = None


cols_ref_formodel = ['cols_cross_input', 'cols_deep_input', 'cols_deep_input']

def Modelcustom(n_wide_cross, n_wide,n_deep, n_feat=8, m_EMBEDDING=10, loss='mse', metric = 'mean_squared_error'):
        """function Modelcustom.
        Doc::
                
                    Args:
                        n_wide_cross:   
                        n_wide:   
                        n_deep:   
                        n_feat:   
                        m_EMBEDDING:   
                        loss:   
                        metric :   
                    Returns:
                        
        """

        #### Wide model with the functional API
        col_wide_cross          = layers.Input(shape=(n_wide_cross,))
        col_wide                = layers.Input(shape=(n_wide,))
        merged_layer            = layers.concatenate([col_wide_cross, col_wide])
        merged_layer            = layers.Dense(15, activation='relu')(merged_layer)
        predictions             = layers.Dense(1)(merged_layer)
        wide_model              = keras.Model(inputs=[col_wide_cross, col_wide], outputs=predictions)

        wide_model.compile(loss = 'mse', optimizer='adam', metrics=[ metric ])
        log2(wide_model.summary())

        #### Deep model with the Functional API
        deep_inputs             = layers.Input(shape=(n_deep,))
        embedding               = layers.Embedding(n_feat, m_EMBEDDING, input_length= n_deep)(deep_inputs)
        embedding               = layers.Flatten()(embedding)

        merged_layer            = layers.Dense(15, activation='relu')(embedding)

        embed_out               = layers.Dense(1)(merged_layer)
        deep_model              = keras.Model(inputs=deep_inputs, outputs=embed_out)
        deep_model.compile(loss='mse',   optimizer='adam',  metrics=[ metric ])
        log2(deep_model.summary())


        #### Combine wide and deep into one model
        merged_out = layers.concatenate([wide_model.output, deep_model.output])
        merged_out = layers.Dense(1)(merged_out)
        model      = keras.Model( wide_model.input + [deep_model.input], merged_out)
        model.compile(loss=loss,   optimizer='adam',  metrics=[ metric ])
        log2(model.summary())

        return model


def get_dataset_tuple(Xtrain, cols_type_received, cols_ref):
    """  Split into Tuples to feed  Xyuple = (df1, df2, df3).
    Doc::
            
            Xtrain:
            cols_type_received:
            cols_ref:
            :return:
    """
    if len(cols_ref) < 1 :
        return Xtrain

    Xtuple_train = []
    for cols_groupname in cols_ref :
        assert cols_groupname in cols_type_received, "Error missing colgroup in config data_pars[cols_model_type] "
        cols_i = cols_type_received[cols_groupname]
        Xtuple_train.append( Xtrain[cols_i] )

    if len(cols_ref) == 1 :
        return Xtuple_train[0]  ### No tuple
    else :
        return Xtuple_train


def get_dataset(data_pars=None, task_type="train", **kw):
    """.
    Doc::
            
              return tuple of dataframes
    """
    # log(data_pars)
    data_type = data_pars.get('type', 'ram')
    cols_ref  = cols_ref_formodel

    if data_type == "ram":
        # cols_ref_formodel = ['cols_cross_input', 'cols_deep_input', 'cols_deep_input' ]
        ### dict  colgroup ---> list of colname
        cols_type_received     = data_pars.get('cols_model_type2', {} )  ##3 Sparse, Continuous

        if task_type == "predict":
            d = data_pars[task_type]
            Xtrain       = d["X"]
            Xtuple_train = get_dataset_tuple(Xtrain, cols_type_received, cols_ref)
            return Xtuple_train

        if task_type == "eval":
            d = data_pars[task_type]
            Xtrain, ytrain  = d["X"], d["y"]
            Xtuple_train    = get_dataset_tuple(Xtrain, cols_type_received, cols_ref)
            return Xtuple_train, ytrain

        if task_type == "train":
            d = data_pars[task_type]
            Xtrain, ytrain, Xtest, ytest  = d["Xtrain"], d["ytrain"], d["Xtest"], d["ytest"]

            ### dict  colgroup ---> list of df
            Xtuple_train = get_dataset_tuple(Xtrain, cols_type_received, cols_ref)
            Xtuple_test  = get_dataset_tuple(Xtest, cols_type_received, cols_ref)


            log2("Xtuple_train", Xtuple_train)

            return Xtuple_train, ytrain, Xtuple_test, ytest


    elif data_type == "file":
        raise Exception(f' {data_type} data_type Not implemented ')

    raise Exception(f' Requires  Xtrain", "Xtest", "ytrain", "ytest" ')


########################################################################################################
########################### Using Sparse Tensor  #######################################################
def ModelCustom2():
    """function ModelCustom2.
    Doc::
            
            Args:
            Returns:
                
    """
    # Build a wide-and-deep model.
    def wide_and_deep_classifier(inputs, linear_feature_columns, dnn_feature_columns, dnn_hidden_units):
        deep = tf.keras.layers.DenseFeatures(dnn_feature_columns, name='deep_inputs')(inputs)
        layers = [int(x) for x in dnn_hidden_units.split(',')]
        for layerno, numnodes in enumerate(layers):
            deep = tf.keras.layers.Dense(numnodes, activation='relu', name='dnn_{}'.format(layerno+1))(deep)
        wide = tf.keras.layers.DenseFeatures(linear_feature_columns, name='wide_inputs')(inputs)
        both = tf.keras.layers.concatenate([deep, wide], name='both')
        output = tf.keras.layers.Dense(1, activation='sigmoid', name='pred')(both)
        model = tf.keras.Model(inputs, output)
        model.compile(optimizer='adam',
                      loss='binary_crossentropy',
                      metrics=['accuracy'])
        return model

    sparse, real =  input_template_feed_keras(cols_type_received, cols_ref)

    DNN_HIDDEN_UNITS = 10
    model = wide_and_deep_classifier(
        inputs,
        linear_feature_columns = sparse.values(),
        dnn_feature_columns = real.values(),
        dnn_hidden_units = DNN_HIDDEN_UNITS)
    #tf.keras.utils.plot_model(model, 'flights_model.png', show_shapes=False, rankdir='LR')
    return model


def input_template_feed_keras(Xtrain, cols_type_received, cols_ref, **kw):
    """.
    Doc::
            
               Create sparse data struccture in KERAS  To plug with MODEL:
               No data, just virtual data
            https://github.com/GoogleCloudPlatform/data-science-on-gcp/blob/master/09_cloudml/flights_model_tf2.ipynb
        
            :return:
    """
    from tensorflow.feature_column import (categorical_column_with_hash_bucket,
        numeric_column, embedding_column, bucketized_column, crossed_column, indicator_column)

    if len(cols_ref) <= 1 :
        return Xtrain

    dict_sparse, dict_dense = {}, {}
    for cols_groupname in cols_ref :
        assert cols_groupname in cols_type_received, "Error missing colgroup in config data_pars[cols_model_type] "

        if cols_groupname == "cols_sparse" :
           col_list = cols_type_received[cols_groupname]
           for coli in col_list :
               m_bucket = min(500, int( Xtrain[coli].nunique()) )
               dict_sparse[coli] = categorical_column_with_hash_bucket(coli, hash_bucket_size= m_bucket)

        if cols_groupname == "cols_dense" :
           col_list = cols_type_received[cols_groupname]
           for coli in col_list :
               dict_dense[coli] = numeric_column(coli)

        if cols_groupname == "cols_cross" :
           col_list = cols_type_received[cols_groupname]
           for coli in col_list :
               m_bucketi = min(500, int( Xtrain[coli[0]].nunique()) )
               m_bucketj = min(500, int( Xtrain[coli[1]].nunique()) )
               dict_sparse[coli[0]+"-"+coli[1]] = crossed_column(coli[0], coli[1], m_bucketi * m_bucketj)

        if cols_groupname == "cols_discretize" :
           col_list = cols_type_received[cols_groupname]
           for coli in col_list :
               bucket_list = np.linspace(min, max, 100).tolist()
               dict_sparse[coli +"_bin"] = bucketized_column(numeric_column(coli), bucket_list)


    #### one-hot encode the sparse columns
    dict_sparse = { colname : indicator_column(col)  for colname, col in dict_sparse.items()}

    ### Embed
    dict_embed  = { 'em_{}'.format(colname) : embedding_column(col, 10) for colname, col in dict_sparse.items()}

    dict_dnn    = {**dict_embed,  **dict_dense}
    dict_linear = {**dict_sparse, **dict_dense}

    return (dict_linear, dict_dnn )



def get_dataset_tuple_keras(pattern, batch_size, mode=tf.estimator.ModeKeys.TRAIN, truncate=None):
    """  ACTUAL Data reading :.
    Doc::
            
                   Dataframe ---> TF Dataset  --> feed Keras model
        
    """
    import os, json, math, shutil
    import tensorflow as tf

    DATA_BUCKET = "gs://{}/flights/chapter8/output/".format(BUCKET)
    TRAIN_DATA_PATTERN = DATA_BUCKET + "train*"
    EVAL_DATA_PATTERN = DATA_BUCKET + "test*"

    CSV_COLUMNS  = ('ontime,dep_delay,taxiout,distance,avg_dep_delay,avg_arr_delay' + \
                    ',carrier,dep_lat,dep_lon,arr_lat,arr_lon,origin,dest').split(',')
    LABEL_COLUMN = 'ontime'
    DEFAULTS     = [[0.0],[0.0],[0.0],[0.0],[0.0],[0.0],\
                    ['na'],[0.0],[0.0],[0.0],[0.0],['na'],['na']]

    def pandas_to_dataset(training_df, coly):
        # tf.enable_eager_execution()
        # features = ['feature1', 'feature2', 'feature3']
        print(training_df)
        training_dataset = (
            tf.data.Dataset.from_tensor_slices(
                (
                    tf.cast(training_df[features].values, tf.float32),
                    tf.cast(training_df[coly].values, tf.int32)
                )
            )
        )

        for features_tensor, target_tensor in training_dataset:
            print(f'features:{features_tensor} target:{target_tensor}')
        return training_dataset

    def load_dataset(pattern, batch_size=1):
      return tf.data.experimental.make_csv_dataset(pattern, batch_size, CSV_COLUMNS, DEFAULTS)

    def features_and_labels(features):
      label = features.pop('ontime') # this is what we will train for
      return features, label

    dataset = load_dataset(pattern, batch_size)
    dataset = dataset.map(features_and_labels)

    if mode == tf.estimator.ModeKeys.TRAIN:
        dataset = dataset.shuffle(batch_size*10)
        dataset = dataset.repeat()
        dataset = dataset.prefetch(1)
    if truncate is not None:
        dataset = dataset.take(truncate)
    return dataset


def get_dataset2(data_pars=None, task_type="train", **kw):
    """.
    Doc::
            
              return tuple of Tensoflow
    """
    # log(data_pars)
    data_type = data_pars.get('type', 'ram')
    cols_ref  = cols_ref_formodel

    if data_type == "ram":
        # cols_ref_formodel = ['cols_cross_input', 'cols_deep_input', 'cols_deep_input' ]
        ### dict  colgroup ---> list of colname
        cols_type_received     = data_pars.get('cols_model_type2', {} )  ##3 Sparse, Continuous

        if task_type == "predict":
            d = data_pars[task_type]
            Xtrain       = d["X"]
            Xtuple_train = get_dataset_tuple_keras(Xtrain, cols_type_received, cols_ref)
            return Xytuple_train

        if task_type == "eval":
            d = data_pars[task_type]
            Xtrain, ytrain  = d["X"], d["y"]
            Xtuple_train    = get_dataset_tuple_keras(Xtrain, cols_type_received, cols_ref)
            return Xytuple_train

        if task_type == "train":
            d = data_pars[task_type]
            Xtrain, ytrain, Xtest, ytest  = d["Xtrain"], d["ytrain"], d["Xtest"], d["ytest"]

            ### dict  colgroup ---> list of df
            Xytuple_train = get_dataset_tuple_keras(Xtrain, ytrain, cols_type_received, cols_ref)
            Xytuple_test  = get_dataset_tuple_keras(Xtest, ytest, cols_type_received, cols_ref)

            log2("Xtuple_train", Xytuple_train)

            return Xytuple_train, Xytuple_test


    elif data_type == "file":
        raise Exception(f' {data_type} data_type Not implemented ')

    raise Exception(f' Requires  Xtrain", "Xtest", "ytrain", "ytest" ')



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
        self.history = None
        if model_pars is None:
            self.model = None
        else:
            log2("data_pars", data_pars)

            model_class = model_pars['model_class']  #

            ### Dynamic shape of input
            model_pars['model_pars']['n_wide_cross'] = len(data_pars['cols_model_type2']['cols_cross_input'])
            model_pars['model_pars']['n_wide']       = len(data_pars['cols_model_type2']['cols_deep_input'])
            model_pars['model_pars']['n_deep']       = len(data_pars['cols_model_type2']['cols_deep_input'])

            model_pars['model_pars']['n_feat']       = model_pars['model_pars']['n_deep']

            mdict = model_pars['model_pars']

            self.model  = Modelcustom(**mdict)
            log2(model_class, self.model)
            self.model.summary()


def fit(data_pars=None, compute_pars=None, out_pars=None, **kw):
    """.
    Doc::
            
    """
    global model, session
    session = None  # Session type for compute

    Xtrain_tuple, ytrain, Xtest_tuple, ytest = get_dataset(data_pars, task_type="train")
    cpars          = copy.deepcopy( compute_pars.get("compute_pars", {}))   ## issue with pickle
    early_stopping = EarlyStopping(monitor='loss', patience=3)
    model_ckpt     = ModelCheckpoint(filepath = compute_pars.get('path_checkpoint', 'ztmp_checkpoint/model_.pth'),
                                     save_best_only=True, monitor='loss')
    cpars['callbacks'] =  [early_stopping, model_ckpt]

    assert 'epochs' in cpars, 'epoch missing'
    hist = model.model.fit( Xtrain_tuple, ytrain,  **cpars)
    model.history = hist



def predict(Xpred=None, data_pars=None, compute_pars={}, out_pars={}, **kw):
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
    if Xpred is None:
        Xpred_tuple = get_dataset(data_pars, task_type="predict")
    else :
        cols_type   = data_pars.get('cols_model_type2', {})  ##
        Xpred_tuple = get_dataset_tuple(Xpred, cols_type, cols_ref_formodel)

    log2(Xpred_tuple)
    ypred = model.model.predict(Xpred_tuple )

    ypred_proba = None  ### No proba
    if compute_pars.get("probability", False):
         ypred_proba = model.model.predict_proba(Xpred)
    return ypred, ypred_proba


def reset():
    """function reset.
    Doc::
            
            Args:
            Returns:
                
    """
    global model, session
    model, session = None, None


def save(path=None, info=None):
    """function save.
    Doc::
            
            Args:
                path:   
                info:   
            Returns:
                
    """
    import dill as pickle, copy
    global model, session
    os.makedirs(path, exist_ok=True)

    ### Keras
    model.model.save(f"{path}/model_keras.h5")

    ### Wrapper
    modelx = Model()  # Empty model  Issue with pickle
    modelx.model_pars   = model.model_pars
    modelx.data_pars    = model.data_pars
    modelx.compute_pars = model.compute_pars

    pickle.dump(modelx, open(f"{path}/model.pkl", mode='wb'))  #
    pickle.dump(info,   open(f"{path}/info.pkl", mode='wb'))  #


def load_model(path=""):
    """function load_model.
    Doc::
            
            Args:
                path:   
            Returns:
                
    """
    global model, session
    import dill as pickle

    model_keras = keras.models.load_model(path + '/model_keras.h5' )
    model0      = pickle.load(open(f"{path}/model.pkl", mode='rb'))

    model = Model()  # Empty model
    model.model = model_keras
    model.model_pars = model0.model_pars
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


####################################################################################################
############ Do not change #########################################################################
def test(config=''):
    """.
    Doc::
            
                Group of columns for the input model
                   cols_input_group = [ ]
                  for cols in cols_input_group,
        
            config:
            :return:
    """

    X = pd.DataFrame( np.random.rand(100,30), columns= [ 'col_' +str(i) for i in range(30)] )
    y = pd.DataFrame( np.random.binomial(n=1, p=0.5, size=[100]), columns = ['coly'] )
    X_train_full, X_test, y_train_full, y_test = train_test_split(X, y, random_state=2021, stratify=y)
    X_train, X_valid, y_train, y_valid         = train_test_split(X_train_full, y_train_full, random_state=2021, stratify=y_train_full)

    log(X_train.shape, )
    ##############################################################
    ##### Generate column actual names from
    colnum = [ 'col_0', 'col_11', 'col_8']
    colcat = [ 'col_13', 'col_17', 'col_13', 'col_9']

    cols_input_type_1 = {
        'colnum' : colnum,
        'colcat' : colcat
    }

    ###### Keras has 1 tuple input    ###########################
    colg_input = {
      'cols_cross_input':  ['colnum', 'colcat' ],
      'cols_deep_input':   ['colnum', 'colcat' ],
    }

    cols_model_type2= {}
    for colg, colist in colg_input.items() :
        cols_model_type2[colg] = []
        for colg_i in colist :
          cols_model_type2[colg].extend( cols_input_type_1[colg_i] )


    ##################################################################################
    model_pars = {'model_class': 'WideAndDeep',
                  'model_pars': {},
                }
    
    n_sample = 100
    data_pars = {'n_sample': n_sample,
                  'cols_input_type': cols_input_type_1,

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
    data_pars['eval'] =  {'X': X_test,
                          'y': y_test}
    data_pars['predict'] = {'X': X_test}

    compute_pars = { 'compute_pars' : { 'epochs': 2,
                   } }

    ######## Run ###########################################
    test_helper(model_pars, data_pars, compute_pars)


def test_helper(model_pars, data_pars, compute_pars):
    """function test_helper.
    Doc::
            
            Args:
                model_pars:   
                data_pars:   
                compute_pars:   
            Returns:
                
    """
    global model, session
    root  = "ztmp/"
    model = Model(model_pars=model_pars, data_pars=data_pars, compute_pars=compute_pars)

    log('\n\nTraining the model..')
    fit(data_pars=data_pars, compute_pars=compute_pars, out_pars=None)

    log('Predict data..')
    ypred, ypred_proba = predict(Xpred=None, data_pars=data_pars, compute_pars=compute_pars)
    log(f'Top 5 y_pred: {np.squeeze(ypred)[:5]}')

    log('Evaluating the model..')
    log(eval(data_pars=data_pars, compute_pars=compute_pars))
    #
    log('Saving model..')
    save(path= root + '/model_dir/')

    log('Load model..')
    model, session = load_model(path= root + "/model_dir/")
    log('Model successfully loaded!\n\n')

    log('Model architecture:')
    log(model.summary())


#######################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire(test)
























def Modelsparse2():
    """.
    Doc::
            
            https://github.com/GoogleCloudPlatform/data-science-on-gcp/blob/master/09_cloudml/flights_model_tf2.ipynb
        
            :return:
    """
    import tensorflow as tf
    NBUCKETS = 10

    real = {
        colname : tf.feature_column.numeric_column(colname)
              for colname in
                ('dep_delay,taxiout,distance,avg_dep_delay,avg_arr_delay' +
                 ',dep_lat,dep_lon,arr_lat,arr_lon').split(',')
    }
    inputs = {
        colname : tf.keras.layers.Input(name=colname, shape=(), dtype='float32')
              for colname in real.keys()
    }

    sparse = {
          'carrier': tf.feature_column.categorical_column_with_vocabulary_list('carrier',
                      vocabulary_list='AS,VX,F9,UA,US,WN,HA,EV,MQ,DL,OO,B6,NK,AA'.split(',')),
          'origin' : tf.feature_column.categorical_column_with_hash_bucket('origin', hash_bucket_size=1000),
          'dest'   : tf.feature_column.categorical_column_with_hash_bucket('dest', hash_bucket_size=1000)
    }
    inputs.update({
        colname : tf.keras.layers.Input(name=colname, shape=(), dtype='string')
              for colname in sparse.keys()
    })



    latbuckets = np.linspace(20.0, 50.0, NBUCKETS).tolist()  # USA
    lonbuckets = np.linspace(-120.0, -70.0, NBUCKETS).tolist() # USA
    disc = {}
    disc.update({
           'd_{}'.format(key) : tf.feature_column.bucketized_column(real[key], latbuckets)
              for key in ['dep_lat', 'arr_lat']
    })
    disc.update({
           'd_{}'.format(key) : tf.feature_column.bucketized_column(real[key], lonbuckets)
              for key in ['dep_lon', 'arr_lon']
    })

    # cross columns that make sense in combination
    sparse['dep_loc'] = tf.feature_column.crossed_column([disc['d_dep_lat'], disc['d_dep_lon']], NBUCKETS*NBUCKETS)
    sparse['arr_loc'] = tf.feature_column.crossed_column([disc['d_arr_lat'], disc['d_arr_lon']], NBUCKETS*NBUCKETS)
    sparse['dep_arr'] = tf.feature_column.crossed_column([sparse['dep_loc'], sparse['arr_loc']], NBUCKETS ** 4)
    #sparse['ori_dest'] = tf.feature_column.crossed_column(['origin', 'dest'], hash_bucket_size=1000)

    # embed all the sparse columns
    embed = {
           'embed_{}'.format(colname) : tf.feature_column.embedding_column(col, 10)
              for colname, col in sparse.items()
    }
    real.update(embed)

    # one-hot encode the sparse columns
    sparse = {
        colname : tf.feature_column.indicator_column(col)
              for colname, col in sparse.items()
    }


    print(sparse.keys())
    print(real.keys())


    # Build a wide-and-deep model.
    def wide_and_deep_classifier(inputs, linear_feature_columns, dnn_feature_columns, dnn_hidden_units):
        deep = tf.keras.layers.DenseFeatures(dnn_feature_columns, name='deep_inputs')(inputs)
        layers = [int(x) for x in dnn_hidden_units.split(',')]
        for layerno, numnodes in enumerate(layers):
            deep = tf.keras.layers.Dense(numnodes, activation='relu', name='dnn_{}'.format(layerno+1))(deep)
        wide = tf.keras.layers.DenseFeatures(linear_feature_columns, name='wide_inputs')(inputs)
        both = tf.keras.layers.concatenate([deep, wide], name='both')
        output = tf.keras.layers.Dense(1, activation='sigmoid', name='pred')(both)
        model = tf.keras.Model(inputs, output)
        model.compile(optimizer='adam',
                      loss='binary_crossentropy',
                      metrics=['accuracy'])
        return model


    DNN_HIDDEN_UNITS = 10
    model = wide_and_deep_classifier(
        inputs,
        linear_feature_columns = sparse.values(),
        dnn_feature_columns = real.values(),
        dnn_hidden_units = DNN_HIDDEN_UNITS)
    tf.keras.utils.plot_model(model, 'flights_model.png', show_shapes=False, rankdir='LR')



