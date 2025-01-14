# -*- coding: utf-8 -*-
MNAME="utilmy.deeplearning.keras.util_dataloader_tab"
"""# 
Doc::




https://www.tensorflow.org/tutorials/structured_data/feature_columns


https://www.tensorflow.org/guide/migrate/migrating_feature_columns






"""
import os, numpy as np, glob, pandas as pd
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import keras
from keras_dataloader.dataset import Dataset

###################################################################################################################
from utilmy import log, log2

def help():
    from utilmy import help_create
    ss = help_create(MNAME)
    log(ss)





###################################################################################################################
def test2():  # using predefined df and model training using model.fit()
    """Tests model training process"""
    from PIL import Image
    from pathlib import Path
    from tensorflow import keras
    from tensorflow.keras import layers

    def get_model():
        model = keras.Sequential([
            keras.Input(shape=(28, 28, 3)),
            layers.Conv2D(32, kernel_size=(3, 3), activation="relu"),
            layers.MaxPooling2D(pool_size=(2, 2)),
            layers.Flatten(),
            layers.Dense(num_labels, activation="softmax"),
        ])
        model.compile(loss=tf.keras.losses.CategoricalCrossentropy(),
                      optimizer=tf.keras.optimizers.Adam(learning_rate=1e-7), metrics=["accuracy"])
        return model

    #####################################################

    df = test_randaom_ds( num_labels=num_labels,)

    input_layer = pd_to_tf_input_layer(df:pd.DataFrame, 

    cols_cat_dict:    dict, 
    cols_catstr_dict: dict, 

    cols_num_dict:dict,  
    is_sparse=True, **kw)

    

    log('############   without Transform')

    model = get_model()
    model.fit(dt_loader, epochs=1, )






def pd_to_tf_input_layer(df:pd.DataFrame, 

    cols_cat_dict:    dict, 
    cols_catstr_dict: dict, 

    cols_num_dict:dict,  
    is_sparse=True, **kw):

    """
        pandas --->  Keras Prepro Layers  , sparse format

        df: input dataframe
        cols_type:  colname --->  type('category, .....),
        cols_unique:  colname ---> ['red', 'blue'] Unique values (for category)


        With Keras preprocessing layers

        inputs = {
        'type': tf.keras.Input(shape=(), dtype='int64'),
        'size': tf.keras.Input(shape=(), dtype='string'),
        'weight': tf.keras.Input(shape=(), dtype='float32'),
        }
        # Convert index to one-hot; e.g. [2] -> [0,0,1].
        type_output = tf.keras.layers.CategoryEncoding(
            one_hot_dims, output_mode='one_hot')(inputs['type'])
        # Convert size strings to indices; e.g. ['small'] -> [1].
        size_output = tf.keras.layers.StringLookup(vocabulary=vocab)(inputs['size'])
        # Normalize the numeric inputs; e.g. [2.0] -> [0.0].
        weight_output = tf.keras.layers.Normalization(
            axis=None, mean=weight_mean, variance=weight_variance)(inputs['weight'])
        outputs = {
        'type': type_output,
        'size': size_output,
        'weight': weight_output,
        }
        preprocessing_model = tf.keras.Model(inputs, outputs)


    """
    inputs = Box({})
    outputs = Box({})


    #### Category
    for ci in cols_cat_dict['cols']: 
        inputs[ci] =  tf.keras.Input(shape=(), dtype='int64'),

        is not is_sparse :        
           outputs[ci] = tf.keras.layers.CategoryEncoding(cols_cat_dict['nunique'][ci], output_mode='one_hot', )(inputs[ci] )
        else
           outputs[ci] = ### Sparse

    for ci in cols_catstr_dict['cols']: 
        inputs[ci] =  tf.keras.Input(shape=(), dtype='string'),
        is not is_sparse :        
           outputs[ci] = tf.keras.layers.StringLookup(vocabulary= cols_catstr_dict['vocab'][ci])(inputs[ci] )
        else
           outputs[ci] = ### Sparse

    for ci in cols_num_dict['cols']:
       inputs[ci] = tf.keras.Input(shape=(), dtype='float32')

       outputs[ci] = tf.keras.layers.Normalization(axis=None, mean=cols_num_dict['mean'][ci], variance=cols_num_dict['variance'][ci])(inputs[ci])

    features_prepro_model = tf.keras.Model(inputs, outputs)
    return features_prepro_model






def pd_to_tf_features(Xtrain:pd.DataFrame, cols_type_received, cols_ref, **kw):
    """
       Create sparse data struccture in KERAS  To plug with MODEL:
       No data, just virtual data  https://github.com/GoogleCloudPlatform/data-science-on-gcp/blob/master/09_cloudml/flights_model_tf2.ipynb

        ## With feature columns
        ### Feature columns must be passed as a list to the estimator on creation, and will be called implicitly during training.

        categorical_col = tf1.feature_column.categorical_column_with_identity(
            'type', num_buckets=one_hot_dims)
        # Convert index to one-hot; e.g. [2] -> [0,0,1].
        indicator_col = tf1.feature_column.indicator_column(categorical_col)

        # Convert strings to indices; e.g. ['small'] -> [1].
        vocab_col = tf1.feature_column.categorical_column_with_vocabulary_list(
            'size', vocabulary_list=vocab, num_oov_buckets=1)
        # Embed the indices.
        embedding_col = tf1.feature_column.embedding_column(vocab_col, embedding_dims)

        normalizer_fn = lambda x: (x - weight_mean) / math.sqrt(weight_variance)
        # Normalize the numeric inputs; e.g. [2.0] -> [0.0].
        numeric_col = tf1.feature_column.numeric_column(
            'weight', normalizer_fn=normalizer_fn)

        estimator = tf1.estimator.DNNClassifier(
            feature_columns=[indicator_col, embedding_col, numeric_col],
            hidden_units=[1])

        def _input_fn():
        return tf1.data.Dataset.from_tensor_slices((features, labels)).batch(1)

        estimator.train(_input_fn)


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









import os
import sys
import numpy as np, pandas as pd
import gdown
from tempfile import gettempdir


def tf_dataset(dataset_pars):
    """
        dataset_pars ={ "dataset_id" : "mnist", "batch_size" : 5000, "n_train": 500, "n_test": 500, 
                            "out_path" : "dataset/vision/mnist2/" }
        tf_dataset(dataset_pars)
        
        
        https://www.tensorflow.org/datasets/api_docs/python/tfds
        import tensorflow_datasets as tfds
        import tensorflow as tf
        
        # Here we assume Eager mode is enabled (TF2), but tfds also works in Graph mode.
        print(tfds.list_builders())
        
        # Construct a tf.data.Dataset
        ds_train = tfds.load(name="mnist", split="train", shuffle_files=True)
        
        # Build your input pipeline
        ds_train = ds_train.shuffle(1000).batch(128).prefetch(10)
        for features in ds_train.take(1):
          image, label = features["image"], features["label"]
          
          
        NumPy Usage with tfds.as_numpy
        train_ds = tfds.load("mnist", split="train")
        train_ds = train_ds.shuffle(1024).batch(128).repeat(5).prefetch(10)
        
        for example in tfds.as_numpy(train_ds):
          numpy_images, numpy_labels = example["image"], example["label"]
        You can also use tfds.as_numpy in conjunction with batch_size=-1 to get the full dataset in NumPy arrays from the returned tf.Tensor object:
        
        train_ds = tfds.load("mnist", split=tfds.Split.TRAIN, batch_size=-1)
        numpy_ds = tfds.as_numpy(train_ds)
        numpy_images, numpy_labels = numpy_ds["image"], numpy_ds["label"]
        
        
        FeaturesDict({
    'identity_attack': tf.float32,
    'insult': tf.float32,
    'obscene': tf.float32,
    'severe_toxicity': tf.float32,
    'sexual_explicit': tf.float32,
    'text': Text(shape=(), dtype=tf.string),
    'threat': tf.float32,
    'toxicity': tf.float32,
})
            
            
    
    """
    import tensorflow_datasets as tfds

    d          = dataset_pars
    dataset_id = d['dataset_id']
    batch_size = d.get('batch_size', -1)  # -1 neans all the dataset
    n_train    = d.get("n_train", 500)
    n_test     = d.get("n_test", 500)
    out_path   = path_norm(d['out_path'] )
    name       = dataset_id.replace(".","-")    
    os.makedirs(out_path, exist_ok=True) 


    train_ds =  tfds.as_numpy( tfds.load(dataset_id, split= f"train[0:{n_train}]", batch_size=batch_size) )
    test_ds  = tfds.as_numpy( tfds.load(dataset_id, split= f"test[0:{n_test}]", batch_size=batch_size) )

    # test_ds  = tfds.as_numpy( tfds.load(dataset_id, split= f"test[0:{n_test}]", batch_size=batch_size) )


    
    print("train", train_ds.shape )
    print("test",  test_ds.shape )

    
    def get_keys(x):
       if "image" in x.keys() : xkey = "image"
       if "text" in x.keys() : xkey = "text"    
       return xkey
    
    
    for x in train_ds:
       #print(x)
       xkey =  get_keys(x)
       np.savez_compressed(out_path + f"{name}_train" , X = x[xkey] , y = x.get('label') )
        

    for x in test_ds:
       #print(x)
       np.savez_compressed(out_path + f"{name}_test", X = x[xkey] , y = x.get('label') )
        
    print(out_path, os.listdir( out_path ))
        
     

####################################################################################
def import_data_tch(name="", mode="train", node_id=0, data_folder_root=""):
    import torch.utils.data.distributed
    from torchvision import datasets, transforms

    if name == "mnist" :
        data_folder = os.path.join( data_folder_root,  "data-%d" % node_id)
        dataset = datasets.MNIST(
            data_folder,
            train=True if mode =="train" else False,
            download=True,
            transform=transforms.Compose(
                [transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))]
            ),
        )
        return dataset


    
"""

Dataset from pytorch Vision
https://pytorch.org/docs/master/torchvision/datasets.html#fashion-mnist



Dataset from Torch Text
https://pytorch.org/text/datasets.html



All dataset
https://en.wikipedia.org/wiki/List_of_datasets_for_machine-learning_research




Time series
https://gluon-ts.mxnet.io/api/gluonts/gluonts.dataset.repository.datasets.html


https://github.com/zalandoresearch/fashion-mnist





####LudWig

https://blog.dominodatalab.com/a-practitioners-guide-to-deep-learning-with-ludwig/






class CustomDatasetFromCSV(Dataset):
    def __init__(self, csv_path, height, width, transforms=None):
        
        Args:
            csv_path (string): path to csv file
            height (int): image height
            width (int): image width
            transform: pytorch transforms for transforms and tensor conversion
        
        self.data = pd.read_csv(csv_path)
        self.labels = np.asarray(self.data.iloc[:, 0])
        self.height = height
        self.width = width
        self.transforms = transform

    def __getitem__(self, index):
        single_image_label = self.labels[index]
        # Read each 784 pixels and reshape the 1D array ([784]) to 2D array ([28,28]) 
        img_as_np = np.asarray(self.data.iloc[index][1:]).reshape(28,28).astype('uint8')
  # Convert image from numpy array to PIL image, mode 'L' is for grayscale
        img_as_img = Image.fromarray(img_as_np)
        img_as_img = img_as_img.convert('L')
        # Transform image to tensor
        if self.transforms is not None:
            img_as_tensor = self.transforms(img_as_img)
        # Return image and the label
        return (img_as_tensor, single_image_label)

    def __len__(self):
        return len(self.data.index)
        

if __name__ == "__main__":
    transformations = transforms.Compose([transforms.ToTensor()])
    custom_mnist_from_csv = \
        CustomDatasetFromCSV('../data/mnist_in_csv.csv', 28, 28, transformations)        
"""














###################################################################################################################
def default_collate_fn(samples):
    X = np.array([sample[0] for sample in samples])
    Y = np.array([sample[1] for sample in samples])

    return X, Y


def tf_data_create_sparse(cols_type_received:dict= {'cols_sparse' : ['col1', 'col2'],
                                                     'cols_num'    : ['cola', 'colb']

                                                     },
                           cols_ref:list=  [ 'col_sparse', 'col_num'  ], Xtrain:pd.DataFrame=None,
                           **kw):
    """

       Create sparse data struccture in KERAS  To plug with MODEL:
       No data, just virtual data
    https://github.com/GoogleCloudPlatform/data-science-on-gcp/blob/master/09_cloudml/flights_model_tf2.ipynb

    :return:
    """
    import tensorflow
    from tensorflow.feature_column import (categorical_column_with_hash_bucket,
        numeric_column, embedding_column, bucketized_column, crossed_column, indicator_column)

    ### Unique values :
    col_unique = {}

    if Xtrain is not None :
        for coli in cols_type_received['col_sparse'] :
                col_unique[coli] = int( Xtrain[coli].nunique())

    dict_cat_sparse, dict_dense = {}, {}
    for cols_groupname in cols_ref :
        assert cols_groupname in cols_type_received, "Error missing colgroup in config data_pars[cols_model_type] "

        if cols_groupname == "cols_sparse" :
           col_list = cols_type_received[cols_groupname]
           for coli in col_list :
               m_bucket = min(500, col_unique.get(coli, 500) )
               dict_cat_sparse[coli] = categorical_column_with_hash_bucket(coli, hash_bucket_size= m_bucket)

        if cols_groupname == "cols_dense" :
           col_list = cols_type_received[cols_groupname]
           for coli in col_list :
               dict_dense[coli] = numeric_column(coli)

        if cols_groupname == "cols_cross" :
           col_list = cols_type_received[cols_groupname]
           for coli in col_list :
               m_bucketi = min(500, col_unique.get(coli, 500) )
               m_bucketj = min(500, col_unique.get(coli, 500) )
               dict_cat_sparse[coli[0]+"-"+coli[1]] = crossed_column(coli[0], coli[1], m_bucketi * m_bucketj)

        if cols_groupname == "cols_discretize" :
           col_list = cols_type_received[cols_groupname]
           for coli in col_list :
               bucket_list = np.linspace(min, max, 100).tolist()
               dict_cat_sparse[coli +"_bin"] = bucketized_column(numeric_column(coli), bucket_list)


    #### one-hot encode the sparse columns
    dict_cat_sparse = { colname : indicator_column(col)  for colname, col in dict_cat_sparse.items()}

    ### Embed
    dict_cat_embed  = { 'em_{}'.format(colname) : embedding_column(col, 10) for colname, col in dict_cat_sparse.items()}


    #### TO Customisze
    #dict_dnn    = {**dict_cat_embed,  **dict_dense}
    # dict_linear = {**dict_cat_sparse, **dict_dense}

    return  dict_cat_sparse, dict_cat_embed, dict_dense,


def tf_data_pandas_to_dataset(training_df: pd.DataFrame, colsX: str, coly: str):
    """
    Creates tf dataset from pandas dataframes
    Args:
        training_df: Dataframe
        colsX: X column name;
        coly: Y column name

    Returns:
        tf dataset object
    """
    # tf.enable_eager_execution()
    # features = ['feature1', 'feature2', 'feature3']
    import tensorflow as tf
    print(training_df)
    training_dataset = (
        tf.data.Dataset.from_tensor_slices(
            (
                tf.cast(training_df[colsX].values, tf.float32),
                tf.cast(training_df[coly].values, tf.int32)
            )
        )
    )

    for features_tensor, target_tensor in training_dataset:
        print(f'features:{features_tensor} target:{target_tensor}')
    return training_dataset



def tf_data_file_to_dataset(pattern, batch_size, mode=tf.estimator.ModeKeys.TRAIN, truncate=None):
    """  ACTUAL Data reading :
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



class DataGenerator(keras.utils.Sequence):

    def __init__(self,
                 dataset: Dataset,
                 collate_fn=default_collate_fn,
                 batch_size=32,
                 shuffle=True,
                 num_workers=0,
                 replacement: bool = False,
                 ):
        """
        dataset (Dataset): Data set to load
        batch_size (int): how many samples in one batch
        shuffle (bool, optional): set to ``True`` to have the data reshuffled
            at every epoch (default: ``True``).
        num_workers (int, optional): how many threads to use for data
            loading in one batch. 0 means that the data will be loaded in the main process.
            (default: ``0``)
        replacement (bool): samples are drawn with replacement if ``True``, default=False
        collate_fn (callable, optional):
        """
        self.dataset = dataset
        self.shuffle = shuffle
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.replacement = replacement
        self.indices = []
        self.collate_fn = collate_fn
        self.on_epoch_end()

    def __getitem__(self, index):
        indices = self.indices[index * self.batch_size: (index + 1) * self.batch_size]

        samples = []
        if self.num_workers == 0:
            for i in indices:
                data = self.dataset[i]
                samples.append(data)
        else:
            with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
                for sample in executor.map(lambda i: self.dataset[i], indices):
                    samples.append(sample)
        X, Y = self.collate_fn(samples)
        return X, Y

    def on_epoch_end(self):
        n = len(self.dataset)
        seq = np.arange(0, n)
        if self.shuffle:
            if self.replacement:
                self.indices = np.random.randint(low=0, high=n, size=(n,),
                                                 dtype=np.int64).tolist()
            else:
                np.random.shuffle(seq)
                self.indices = seq
        else:
            self.indices = seq

    def __len__(self):
        return int(np.floor(len(self.dataset) / self.batch_size))




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
    print(*s, flush=True)

def log2(*s):
    if verbosity >= 2 :
      print(*s, flush=True)


####################################################################################################
global model, session

def init(*kw, **kwargs):
    global model, session
    model = Model(*kw, **kwargs)
    session = None


cols_ref_formodel = ['cols_cross_input', 'cols_deep_input', 'cols_deep_input']

def Modelcustom(n_wide_cross, n_wide,n_deep, n_feat=8, m_EMBEDDING=10, loss='mse', metric = 'mean_squared_error'):

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
    """  Split into Tuples to feed  Xyuple = (df1, df2, df3)
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
    """
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
    """
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
    """  ACTUAL Data reading :
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
    """
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
    """
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
    global model, session
    model, session = None, None


def save(path=None, info=None):
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
    """
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








