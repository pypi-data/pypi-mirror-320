


arg = data_pars['precprces']['arg']

xxx = data_info.get( “xxx”, arg.get(“xxxx”, -1))



def get_loader(fix_length, vocab_threshold, batch_size):
    train_dataset = SentimentDataset("data/train.csv", fix_length, vocab_threshold)

    vocab = train_dataset.vocab

    # valid_dataset = SentimentDataset("data/valid.csv", fix_length, vocab_threshold, vocab)

    test_dataset = SentimentDataset("data/test.csv", fix_length, vocab_threshold, vocab)

    train_dataloader = DataLoader(dataset=train_dataset,
                                  batch_size=batch_size,
                                  shuffle=True,
                                  num_workers=4)

    """
    valid_dataloader = DataLoader(dataset=valid_dataset,
                                  batch_size=batch_size,
                                  shuffle=False,
                                  num_workers=4)
    """

    test_dataloader = DataLoader(dataset=test_dataset,
                                 batch_size=batch_size,
                                 shuffle=False,
                                 num_workers=4)

    return train_dataloader, test_dataloader, vocab





#########################################################################################################
#########################################################################################################
from torchvision.datasets.vision import VisionDataset
class MNIST(VisionDataset):
    """`MNIST <http://yann.lecun.com/exdb/mnist/>`_ Dataset.
    Args:
        root (string): Root directory of dataset where ``MNIST/processed/training.pt``
            and  ``MNIST/processed/test.pt`` exist.
        train (bool, optional): If True, creates dataset from ``training.pt``,
            otherwise from ``test.pt``.
        download (bool, optional): If true, downloads the dataset from the internet and
            puts it in root directory. If dataset is already downloaded, it is not
            downloaded again.
        transform (callable, optional): A function/transform that  takes in an PIL image
            and returns a transformed version. E.g, ``transforms.RandomCrop``
        target_transform (callable, optional): A function/transform that takes in the
            target and transforms it.
    """

    from torchvision.datasets.vision import VisionDataset
    import warnings
    from PIL import Image
    import os
    import os.path
    import numpy as np
    import torch
    import codecs
    import string
    from torchvision.datasets.utils import download_url, download_and_extract_archive, extract_archive,  verify_str_arg


    resources = [
        ("http://yann.lecun.com/exdb/mnist/train-images-idx3-ubyte.gz", "f68b3c2dcbeaaa9fbdd348bbdeb94873"),
        ("http://yann.lecun.com/exdb/mnist/train-labels-idx1-ubyte.gz", "d53e105ee54ea40749a09fcbcd1e9432"),
        ("http://yann.lecun.com/exdb/mnist/t10k-images-idx3-ubyte.gz", "9fb629c4189551a2d022fa330f9573f3"),
        ("http://yann.lecun.com/exdb/mnist/t10k-labels-idx1-ubyte.gz", "ec29112dd5afa0611ce80d1b7f02629c")
    ]

    training_file = 'training.pt'
    test_file = 'test.pt'
    classes = ['0 - zero', '1 - one', '2 - two', '3 - three', '4 - four',
               '5 - five', '6 - six', '7 - seven', '8 - eight', '9 - nine']

    @property
    def train_labels(self):
        warnings.warn("train_labels has been renamed targets")
        return self.targets

    @property
    def test_labels(self):
        warnings.warn("test_labels has been renamed targets")
        return self.targets

    @property
    def train_data(self):
        warnings.warn("train_data has been renamed data")
        return self.data

    @property
    def test_data(self):
        warnings.warn("test_data has been renamed data")
        return self.data

    def __init__(self, root, train=True, transform=None, target_transform=None,
                 download=False):
        super(MNIST, self).__init__(root, transform=transform,
                                    target_transform=target_transform)
        self.train = train  # training set or test set

        if download:
            self.download()

        if not self._check_exists():
            raise RuntimeError('Dataset not found.' +
                               ' You can use download=True to download it')

        if self.train:
            data_file = self.training_file
        else:
            data_file = self.test_file
        self.data, self.targets = torch.load(os.path.join(self.processed_folder, data_file))

    def __getitem__(self, index):
        """
        Args:
            index (int): Index
        Returns:
            tuple: (image, target) where target is index of the target class.
        """
        img, target = self.data[index], int(self.targets[index])

        # doing this so that it is consistent with all other datasets
        # to return a PIL Image
        img = Image.fromarray(img.numpy(), mode='L')

        if self.transform is not None:
            img = self.transform(img)

        if self.target_transform is not None:
            target = self.target_transform(target)

        return img, target

    def __len__(self):
        return len(self.data)

    @property
    def raw_folder(self):
        return os.path.join(self.root, self.__class__.__name__, 'raw')

    @property
    def processed_folder(self):
        return os.path.join(self.root, self.__class__.__name__, 'processed')

    @property
    def class_to_idx(self):
        return {_class: i for i, _class in enumerate(self.classes)}

    def _check_exists(self):
        return (os.path.exists(os.path.join(self.processed_folder,
                                            self.training_file)) and
                os.path.exists(os.path.join(self.processed_folder,
                                            self.test_file)))

    def download(self):
        """Download the MNIST data if it doesn't exist in processed_folder already."""

        if self._check_exists():
            return

        os.makedirs(self.raw_folder, exist_ok=True)
        os.makedirs(self.processed_folder, exist_ok=True)

        # download files
        for url, md5 in self.resources:
            filename = url.rpartition('/')[2]
            download_and_extract_archive(url, download_root=self.raw_folder, filename=filename, md5=md5)

        # process and save as torch files
        print('Processing...')

        training_set = (
            read_image_file(os.path.join(self.raw_folder, 'train-images-idx3-ubyte')),
            read_label_file(os.path.join(self.raw_folder, 'train-labels-idx1-ubyte'))
        )
        test_set = (
            read_image_file(os.path.join(self.raw_folder, 't10k-images-idx3-ubyte')),
            read_label_file(os.path.join(self.raw_folder, 't10k-labels-idx1-ubyte'))
        )
        with open(os.path.join(self.processed_folder, self.training_file), 'wb') as f:
            torch.save(training_set, f)
        with open(os.path.join(self.processed_folder, self.test_file), 'wb') as f:
            torch.save(test_set, f)

        print('Done!')

    def extra_repr(self):
        return "Split: {}".format("Train" if self.train is True else "Test")






#########################################################################################################
#########################################################################################################
def pandas_dataset() :

    from typing import Union, Dict

    import pandas as pd
    from torchtext.data import (Field, Example, Iterator, BucketIterator, Dataset)
    from tqdm import tqdm


    class DataFrameExampleSet(Dataset):
        def __init__(self, data_pars):
            self.data_pars = data_pars
            d =data_pars
            self._df = pd.read_csv( d['load_path']  )

            fields = None
            self._fields = fields
            self._fields_dict = {field_name: (field_name, field)
                                 for field_name, field in fields.items()
                                 if field is not None}

        def __iter__(self):
            for item in tqdm(self._df.itertuples(), total=len(self)):
                example = Example.fromdict(item._asdict(), fields=self._fields_dict)
                yield example

        def __len__(self):
            return len(self._df)

        def shuffle(self, random_state=None):
            self._df = self._df.sample(frac=1.0, random_state=random_state)


    class DataFrameDataset(Dataset):
        def __init__(self, df: pd.DataFrame,
                     fields: Dict[str, Field], filter_pred=None):
            examples = DataFrameExampleSet(df, fields)
            super().__init__(examples, fields, filter_pred=filter_pred)


    class DataFrameIterator(Iterator):
        def data(self):
            if isinstance(self.dataset.examples, DataFrameExampleSet):
                if self.shuffle:
                    self.dataset.examples.shuffle()
                dataset = self.dataset
            else:
                dataset = super().data()
            return dataset


    class DataFrameBucketIterator(BucketIterator):
        def data(self):
            if isinstance(self.dataset.examples, DataFrameExampleSet):
                if self.shuffle:
                    self.dataset.examples.shuffle()
                dataset = self.dataset
            else:
                dataset = super().data()
            return dataset




def custom_dataset():
    import re
    import logging

    import numpy as np
    import pandas as pd
    import spacy
    import torch
    from torchtext import data

    NLP = spacy.load('en')
    MAX_CHARS = 20000
    VAL_RATIO = 0.2
    LOGGER = logging.getLogger("toxic_dataset")



    def get_dataset(fix_length=100, lower=False, vectors=None):
        if vectors is not None:
            # pretrain vectors only supports all lower cases
            lower = True


        comment = data.Field(
            sequential=True,
            fix_length=fix_length,
            tokenize=tokenizer,
            pad_first=True,
            tensor_type=torch.cuda.LongTensor,
            lower=lower
        )

        train, val = data.TabularDataset.splits(
            path='cache/', format='csv', skip_header=True,
            train='dataset_train.csv', validation='dataset_val.csv',
            fields=[
                ('id', None),
                ('comment_text', comment),
                ('toxic', data.Field(
                    use_vocab=False, sequential=False, tensor_type=torch.cuda.ByteTensor)),
                ('severe_toxic', data.Field(
                    use_vocab=False, sequential=False, tensor_type=torch.cuda.ByteTensor)),
                ('obscene', data.Field(
                    use_vocab=False, sequential=False, tensor_type=torch.cuda.ByteTensor)),
                ('threat', data.Field(
                    use_vocab=False, sequential=False, tensor_type=torch.cuda.ByteTensor)),
                ('insult', data.Field(
                    use_vocab=False, sequential=False, tensor_type=torch.cuda.ByteTensor)),
                ('identity_hate', data.Field(
                    use_vocab=False, sequential=False, tensor_type=torch.cuda.ByteTensor)),
            ])

        test = data.TabularDataset(
            path='cache/dataset_test.csv', format='csv', skip_header=True,
            fields=[
                ('id', None),
                ('comment_text', comment)
            ])
        LOGGER.debug("Building vocabulary...")
        comment.build_vocab(
            train, val, test,
            max_size=20000,
            min_freq=50,
            vectors=vectors
        )
        return train, val, test


    def get_iterator(dataset, batch_size, train=True, shuffle=True, repeat=False):
        dataset_iter = data.Iterator(
            dataset, batch_size=batch_size, device=0,
            train=train, shuffle=shuffle, repeat=repeat,
            sort=False
        )
        return dataset_iter




def text_dataloader():  
    import torchtext
    import torchtext.data as data
    import torchtext.vocab as vocab
    import os
    import spacy
    import pandas as pd
    import random
    import dill
    from tqdm import tqdm
    from torchtext.data import BucketIterator

    spacy = spacy.load("en_core_web_sm")
    SEED = 1024

    def spacy_tokenize(x):
        return [
            tok.text
            for tok in spacy.tokenizer(x)
            if not tok.is_punct | tok.is_space
        ]


    class NewsDataset(data.Dataset):
        def __init__(
            self, path, max_src_len=100, field=None, debug=False, **kwargs
        ):
            examples = []
            fields = [("src", field), ("tgt", field)]
            df = pd.read_csv(path, encoding="utf-8", usecols=["content", "title"])
            df = df[~(df["content"].isnull() | df["title"].isnull())]
            df = df[~(df["content"] == "[]")]
            for i in tqdm(range(df.shape[0])):
                examples.append(
                    data.Example.fromlist(
                        [df.iloc[i].content, df.iloc[i].title], fields
                    )
                )
                if debug and i == 100:
                    break
            super().__init__(
                examples, fields, filter_pred=lambda s: len(s.src) > 10, **kwargs
            )
            for example in self.examples:
                example.tgt = ["<sos>"] + example.tgt + ["<eos>"]


    class NewsDataLoader:
        def __init__(
            self,
            csv_path,
            use_save=False,
            embed_path=None,
            build_vocab=True,
            batch_size=64,
            val_size=0.2,
            max_src_len=100,
            save=True,
            shuffle=True,
            debug=False,
        ):
            random.seed(SEED)

            def trim_sentence(s):
                return s[:max_src_len]

            self.field = data.Field(
                tokenize=spacy_tokenize,
                batch_first=True,
                include_lengths=True,
                lower=True,
                preprocessing=trim_sentence,
            )

            if use_save:
                save = False
                build_vocab = False
                with open("data/dataset.pickle", "rb") as f:
                    self.field = dill.load(f)

            dataset = NewsDataset(
                csv_path, max_src_len, field=self.field, debug=debug
            )

            if build_vocab:
                # load custom word vectors
                if embed_path:
                    path, embed = os.path.split(embed_path)
                    vec = vocab.Vectors(embed, cache=path)
                    self.field.build_vocab(dataset, vectors=vec)
                else:
                    self.field.build_vocab(
                        dataset, vectors="glove.6B.300d", max_size=40000
                    )

            self.dataloader = BucketIterator(
                dataset,
                batch_size=batch_size,
                device=-1,
                sort_key=lambda x: len(x.src),
                sort_within_batch=True,
                repeat=False,
                shuffle=shuffle,
            )
            self.stoi = self.field.vocab.stoi
            self.itos = self.field.vocab.itos
            self.sos_id = self.stoi["<sos>"]
            self.eos_id = self.stoi["<eos>"]
            self.pad_id = self.stoi["<pad>"]
            self.n_examples = len(dataset)

            if save:
                with open("data/dataset.pickle", "wb") as f:
                    temp = self.field
                    dill.dump(temp, f)

        def __iter__(self):
            for batch in self.dataloader:
                x = batch.src
                y = batch.tgt
                yield (x[0], x[1], y[0], y[1])

        def __len__(self):
            return len(self.dataloader)


   
            dl = NewsDataLoader(csv_path="data/val.csv", debug=True, save=False)
            for x, len_x, y, len_y in dl:
            if (len_x == 0).any():
                import pdb

                pdb.set_trace()















#########################################################################
#### System utilities
import os
import sys
import inspect
from urllib.parse import urlparse
from jsoncomment import JsonComment ; json = JsonComment()
from importlib import import_module
import pandas as pd
import numpy as np
from collections.abc import MutableMapping


#possibly replace with keras.utils.get_file down the road?
#### It dowloads from HTTP from Dorpbox, ....  (not urgent)
from cli_code.cli_download import Downloader 

from sklearn.model_selection import train_test_split
import cloudpickle as pickle

#########################################################################
#### mlmodels-internal imports
from preprocessor import Preprocessor
from util import load_callable_from_dict



#########################################################################
#### Specific packages
import tensorflow as tf
import torch
import torchtext
import keras

import tensorflow.data





"""
Where are the input json samples ?
   I've uploaded that one to dataset/json/all/03_nbeats_dataloader.json.
   They used to temporarily be in dataset/json_, but that folder's been removed in the last merge with dev.

    I change to mlodels/ #possibly replace with keras.utils.get_file down the road?



Can you open the chat ?

"""
#Todo: stable layout for json, component separation, component development.

"""
Typical user workflow

def get_dataset(data_pars):
    loader = DataLoader(data_pars)
    loader.compute()
    data = loader.get_data()
    [print(x.shape) for x in data]
    return data



"""


def pickle_load(file):
    return pickle.load(open(f, " r"))


def image_dir_load(path):
    return ImageDataGenerator().flow_from_directory(path)


def batch_generator(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx : min(ndx + n, l)]


class DataLoader:

    default_loaders = {
        ".csv": {"uri": "pandas::read_csv"},
        ".npy": {"uri": "numpy::load"},
        ".npz": {"uri": "np:load", "arg": {"allow_pickle": True}},
        ".pkl": {"uri": "dataloader::pickle_load"},
        "image_dir": {"uri": "dataloader::image_dir_load"},
    }

    def __init__(self, data_pars):
        self.input_pars = data_pars['input_pars']
        
        self.intermediate_output = None
        self.intermediate_output_split = None
        self.final_output = None
        self.final_output_split = None

        self.loader = data_pars['loader']
        self.preprocessor = data_pars['preprocessor']
        self.output = data_pars['output']
        self.data_pars = data_pars.copy() #for getting with __get_item__/dict-like indexing.
        
               
    def compute(self):
        
        ### Generate self.names
        self._interpret_input_pars(self.input_pars)

        #if self._names or False :
        #  raise Exception("this is bad")

        loaded_data = self._load_data(self.loader) 
        
        '''
        if isinstance(preprocessor, Preprocessor):
            self.preprocessor = preprocessor
            processed_data = self.preprocessor.transform(loaded_data)
        else:
            self.preprocessor = Preprocessor(preprocessor)
            processed_data = self.preprocessor.fit_transform(loaded_data)

        ### Hello, can you open the chat ?    
        '''
        preprocessor_class, _ = load_callable_from_dict(self.preprocessor)
        self.preprocessor = preprocessor_class(self.data_pars)
        self.preprocessor.compute(loaded_data)

        if self._names is not None:
            self.intermediate_output = self._name_outputs(
                self.names, self.intermediate_output
            )
        if self._split_data():
            self.final_output_split = tuple(
                self._interpret_output(output, o)
                for o in self.intermediate_output_split[0:2]
            ) + tuple(self.intermediate_output_split[2])
        else:
            self.final_output = self._interpret_output(output, self.intermediate_output)


    def __getitem__(self, key):
        return self.data_pars[key]

    def _interpret_input_pars(self, input_pars):
        try:
            path = input_pars["path"]
        except KeyError:
            raise Exception('Missing path key in the dataloader.')

        path_type = input_pars.get("path_type", None)
        if path_type is None:
            if os.path.isfile(path):
                path_type = "file"
            if os.path.isdir(path):
                path_type = "dir"
            if urlparse(path).scheme != "":
                path_type = "url"
                download_path = input_pars.get("download_path", "./")
            if path_type == "dropbox":
                dropbox_download(path)
                path_type = "file"
            if path_type is None:
                raise Exception(f'Path type for {path} is undeterminable')

        elif path_type != "file" and path_type != "dir" and path_type != "url":
            raise Exception('Unknown location type')

        file_type = input_pars.get("file_type", None)
        if file_type is None:
            if path_type == "dir":
                file_type = "image_dir"
            elif path_type == "file":
                file_type = os.path.splitext(path)[1]
            else:
                if path[-1] == "/":
                    raise Exception('URL must target a single file.')
                file_type = os.path.splittext(path.split("/")[-1])[1]

        self.path = path
        self.path_type = path_type
        self.file_type = file_type
        self.test_size = input_pars.get("test_size", None)
        self.generator = input_pars.get("generator", False)
        if self.generator:
            try:
                self.batch_size = int(input_pars.get("batch_size", 1))
            except:
                raise Exception('Batch size must be an integer')
        self._names = input_pars.get("names", None) #None by default. (Possibly rename for clarity?)
        validation_split_function = [
            {"uri": "sklearn.model_selection::train_test_split", "args": {}},
            "test_size",
        ]
        self.validation_split_function = input_pars.get(
            "split_function", validation_split_function
        )
        self.split_outputs = input_pars.get("split_outputs", None)
        self.misc_outputs = input_pars.get("misc_outputs", None)

    def _load_data(self, loader):
        data_loader = loader.get("data_loader", None)
        if isinstance(data_loader, tuple):
            loader_function = data_loader[0]
            loader_args = data_loader[1]
        else:
            if data_loader is None or "uri" not in data_loader.keys():
                try:
                    if data_loader is not None and "arg" in data_loader.keys():
                        loader_args = data_loader["arg"]
                    else:
                        loader_args = {}
                    data_loader = self.default_loaders[self.file_type]
                except KeyError:
                    raise Exception('Loader function could not beautomataically determined.')
            try:
                loader_function, args = load_callable_from_dict(data_loader)
                if args is not None:
                    loader_args.update(args)
                assert callable(loader_function)
            except:
                raise Exception(f'Invalid loader function: {data_loader}')

        if self.path_type == "file":
            if self.generator:
                if self.file_type == "csv":
                    if loader_function == pd.read_csv:
                        loader_args["chunksize"] = loader.get(
                            "chunksize", self.batch_size
                        )
            loader_arg = self.path

        if self.path_type == "url":
            if self.file_type == "csv" and loader_function == pd.read_csv:
                data = loader_function(self.path, **loader_args)
            else:
                downloader = Downloader(url)
                downloader.download(out_path)
                filename = self.path.split("/")[-1]
                loader_arg = out_path + "/" + filename
        data = loader_function(loader_arg, **loader_args)
        if self.file_type == "npz" and loader_function == np.load:
            data = [data[f] for f in data.files]

        return data

    def _interpret_output(self, output, intermediate_output):
        if isinstance(intermediate_output, list) and len(output) == 1:
            intermediate_output = intermediate_output[0]
        # case 0: non-tuple, non-dict: single output from the preprocessor/loader.
        # case 1: tuple of non-dicts: multiple outputs from the preprocessor/loader.
        # case 2: tuple of dicts: multiple args from the preprocessor/loader.
        # case 3: dict of non-dicts: multiple named outputs from the preprocessor/loader.
        # case 4: dict of dicts: multiple named dictionary outputs from the preprocessor. (Special case)
        case = 0
        if isinstance(intermediate_output, tuple):
            if not isinstance(intermediate_output[0], dict):
                case = 1
            else:
                case = 2
        if isinstance(intermediate_output, dict):
            if not isinstance(tuple(intermediate_output.values())[0], dict):
                case = 3
            else:
                case = 4
        
        #max_len enforcement
        max_len = output.get("out_max_len", None)
        try:
            if case == 0:
                intermediate_output = intermediate_output[0:max_len]
            if case == 1:
                intermediate_output = [o[0:max_len] for o in intermediate_output]
            if case == 3:
                intermediate_output = {
                    k: v[0:max_len] for k, v in intermediate_output.items()
                }
        except:
            pass

        # shape check
        shape = output.get("shape", None)
        if shape is not None:
            if (
                case == 0
                and hasattr(intermediate_output, "shape")
                and tuple(shape) != intermediate_output.shape
            ):
                raise Exception(f'Expected shape {tuple(shape)} does not match shape data shape {intermediate_output.shape[1:]}')
            if case == 1:
                for s, o in zip(shape, intermediate_output):
                    if hasattr(o, "shape") and tuple(s) != o.shape[1:]:
                        raise Exception(f'Expected shape {tuple(shape)} does not match shape data shape {intermediate_output.shape[1:]}')
            if case == 3:
                for s, o in zip(shape, tuple(intermediate_output.values())):
                    if hasattr(o, "shape") and tuple(s) != o.shape[1:]:
                        raise Exception(f'Expected shape {tuple(shape)} does not match shape data shape {intermediate_output.shape[1:]}')
        self.output_shape = shape

        # saving the intermediate output
        '''
        path = output.get("path", None)
        if isinstance(path, str):
            if isinstance(intermediate_output, np.ndarray):
                np.save(path, intermediate_output)
            elif isinstance(intermediate_output, pd.core.frame.DataFrame):
                intermediate_output.to_csv(path)
            elif isinstance(intermediate_output, tuple) and all(
                [isinstance(x, np.ndarray) for x in intermediate_output]
            ):
                np.savez(path, *intermediate_output)
            elif isinstance(intermediate_output, dict) and all(
                [isinstance(x, np.ndarray) for x in tuple(intermediate_output.values())]
            ):
                np.savez(path, *(tuple(intermediate_output.values)))
            else:
                pickle.dump(intermediate_output, open(path, "wb"))
        elif isinstance(path, list):
            try:
                for p, f in zip(path, intermediate_output):
                    if isinstance(f, np.ndarray):
                        np.save(p, self.f)
                    elif isinstance(f, pd.core.frame.DataFrame):
                        f.to_csv(f)
                    elif isinstance(f, list) and all(
                        [isinstance(x, np.ndarray) for x in f]
                    ):
                        np.savez(p, *f)
                    else:
                        pickle.dump(f, open(p, "wb"))
            except:
                pass
        '''
        
        # Framework-specific output formatting.
        final_output = intermediate_output
        output_format = output.get("format", None)
        if output_format == "tfDataset":
            if case == 3:
                intermediate_output = tuple(
                    x for x in tuple(intermediate_output.values())
                )
            if case == 2 or case == 4:
                raise Exception(
                    "Input format not supported for the specified output format"
                )
            final_output = tf.data.Dataset.from_tensor_slices(intermediate_output)
        if output_format == "tchDataset":
            if case == 3:
                intermediate_output = tuple(
                    x for x in tuple(intermediate_output.values())
                )
            if case == 2 or case == 4:
                raise Exception(
                    "Input format not supported for the specified output format"
                )
            if case == 1:
                final_output = torch.utils.data.TensorDataset(intermediate_output)
            else:
                final_output = torch.utils.data.TensorDataset(*intermediate_output)
        if output_format == "generic_generator":
            if case == 0:
                final_output = batch_generator(intermediate_output, self.batch_size)
            if case == 1:
                final_output = batch_generator(
                    tuple(zip(*intermediate_output)), self.batch_size
                )
            if case == 3:
                final_output = batch_generator(
                    tuple(zip(*tuple(intermediate_output.values()))), self.batch_size
                )
            if case == 2 or case == 4:
                raise Exception(
                    "Input format not supported for the specified output format"
                )

        return final_output

    def get_data(self, intermediate=False):
        if intermediate or self.final_output is None:
            if self.intermediate_output_split is not None:
                return (
                    *self.intermediate_output_split[0],
                    *self.intermediate_output_split[1],
                    *self.intermediate_output_split[2],
                )
            if isinstance(self.intermediate_output, dict):
                return tuple(self.intermediate_output.values())
            return self.intermediate_output
        if self.final_output_split is not None:
            return (
                *self.final_output_split[0],
                *self.final_output_split[1],
                *self.final_output_split[2],
            )
        return self.final_output

    def _name_outputs(self, names, outputs):
        if hasattr(outputs, "__getitem__") and len(outputs) == len(names):
            data = dict(zip(names, outputs))
            self.data_pars.update(data)
            return data
        else:
            raise Exception("Outputs could not be named")

    def _split_data(self):
        if self.split_outputs is not None:
            if (
                self._names is not None or isinstance(self.intermediate_output, dict)
            ) or isinstance(self.intermediate_output, tuple):
                processed_data = tuple(
                    self.intermediate_output[n] for n in self.split_outputs
                )
        else:
            processed_data = self.intermediate_output
        func_dir = self.validation_split_function[0]
        split_size_arg_dict = {
            self.validation_split_function[1]: self.test_size,
            **func_dir.get("arg", {}),
        }
        if self.test_size > 0:
            func, arg = load_callable_from_dict(self.validation_split_function[0])
            if arg is None:
                arg = {}
            arg.update({self.validation_split_function[1]: self.test_size})
            l = len(processed_data)
            processed_data = func(*processed_data, **arg)
            processed_data_train = processed_data[0:l]
            processed_data_test = processed_data[l:]
            processed_data_misc = []

            if self._names is not None and isinstance(self.intermediate_output, dict):
                new_names = [x + "_train" for x in self.split_outputs]
                processed_data_train = dict(zip(new_names, processed_data_train))
                new_names = [x + "_test" for x in self.split_outputs]
                processed_data_test = dict(zip(new_names, processed_data_test))
                
            if self.misc_outputs is not None:
                if self._names is not None and isinstance(
                    self.intermediate_output, dict
                ):
                    processed_data_misc = {
                        misc: self.intermediate_output[misc]
                        for misc in self.misc_outputs
                    }
                else:
                    processed_data_misc = tuple(
                        self.intermediate_output[misc] for misc in self.misc_outputs
                    )
            self.intermediate_output_split = (
                processed_data_train,
                processed_data_test,
                processed_data_misc,
            )
            return True
        return False


if __name__ == "__main__":
    from models import test_module

    param_pars = {
        "choice": "json",
        "config_mode": "test",
        "data_path": "dataset/json/refractor/03_nbeats_dataloader.json",
    }
    test_module("model_tch/03_nbeats_dataloader.py", param_pars)
    # param_pars = {
    #   "choice": "json",
    #   "config_mode": "test",
    #   "data_path": f"dataset/json_/namentity_crm_bilstm_dataloader.json",
    # }
    #
    # test_module("model_keras/dataloader/namentity_crm_bilstm.py", param_pars)

    # param_pars = {
    #    "choice": "json",
    #    "config_mode": "test",
    #    "data_path": f"dataset/json_/textcnn_dataloader.json",
    # }
    # test_module("model_tch/textcnn.py", param_pars)
