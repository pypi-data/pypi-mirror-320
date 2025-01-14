from concurrent.futures import ThreadPoolExecutor

import keras
import numpy as np

from keras_dataloader.dataset import Dataset


def default_collate_fn(samples):
    """function default_collate_fn
    Args:
        samples:   
    Returns:
        
    """
    X = np.array([sample[0] for sample in samples])
    Y = np.array([sample[1] for sample in samples])

    return X, Y


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
        """ DataGenerator:__getitem__
        Args:
            index:     
        Returns:
           
        """
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
        """ DataGenerator:on_epoch_end
        Args:
        Returns:
           
        """
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
        """ DataGenerator:__len__
        Args:
        Returns:
           
        """
        return int(np.floor(len(self.dataset) / self.batch_size))
