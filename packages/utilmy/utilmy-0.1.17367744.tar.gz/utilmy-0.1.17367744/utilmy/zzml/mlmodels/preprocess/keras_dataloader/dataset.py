import bisect
import warnings


class Dataset(object):
    """An abstract class representing a Dataset.

    All other datasets should subclass it. All subclasses should override
    ``__len__``, that provides the size of the dataset, and ``__getitem__``,
    supporting integer indexing in range from 0 to len(self) exclusive.
    """

    def __init__(self, dtype='float32'):
        """ Dataset:__init__.
        Doc::
                
                    Args:
                        dtype:     
                    Returns:
                       
        """
        self.dtype = dtype

    def __getitem__(self, index):
        """ Dataset:__getitem__.
        Doc::
                
                    Args:
                        index:     
                    Returns:
                       
        """
        raise NotImplementedError

    def __len__(self):
        """ Dataset:__len__.
        Doc::
                
                    Args:
                    Returns:
                       
        """
        raise NotImplementedError

    def __add__(self, other):
        """ Dataset:__add__.
        Doc::
                
                    Args:
                        other:     
                    Returns:
                       
        """
        return ConcatDataset([self, other])


class ConcatDataset(Dataset):
    """
    Dataset to concatenate multiple datasets.
    Purpose: useful to assemble different existing datasets, possibly
    large-scale datasets as the concatenation operation is done in an
    on-the-fly manner.

    Arguments:
        datasets (sequence): List of datasets to be concatenated
    """

    @staticmethod
    def cumsum(sequence):
        """ ConcatDataset:cumsum.
        Doc::
                
                    Args:
                        sequence:     
                    Returns:
                       
        """
        r, s = [], 0
        for e in sequence:
            l = len(e)
            r.append(l + s)
            s += l
        return r

    def __init__(self, datasets):
        """ ConcatDataset:__init__.
        Doc::
                
                    Args:
                        datasets:     
                    Returns:
                       
        """
        super(ConcatDataset, self).__init__()
        assert len(datasets) > 0, 'datasets should not be an empty iterable'
        self.datasets = list(datasets)
        self.cumulative_sizes = self.cumsum(self.datasets)

    def __len__(self):
        """ ConcatDataset:__len__.
        Doc::
                
                    Args:
                    Returns:
                       
        """
        return self.cumulative_sizes[-1]

    def __getitem__(self, idx):
        """ ConcatDataset:__getitem__.
        Doc::
                
                    Args:
                        idx:     
                    Returns:
                       
        """
        dataset_idx = bisect.bisect_right(self.cumulative_sizes, idx)
        if dataset_idx == 0:
            sample_idx = idx
        else:
            sample_idx = idx - self.cumulative_sizes[dataset_idx - 1]
        return self.datasets[dataset_idx][sample_idx]

    @property
    def cummulative_sizes(self):
        """ ConcatDataset:cummulative_sizes.
        Doc::
                
                    Args:
                    Returns:
                       
        """
        warnings.warn("cummulative_sizes attribute is renamed to "
                      "cumulative_sizes", DeprecationWarning, stacklevel=2)
        return self.cumulative_sizes
