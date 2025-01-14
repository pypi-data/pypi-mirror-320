from __future__ import absolute_import, division, print_function

import inspect
import os
import sys

import numpy as np
import tensorflow as tf
from numpy.testing import assert_allclose
from tensorflow.python.keras import backend as K
from tensorflow.python.keras.layers import Input, Masking
from tensorflow.python.keras.models import Model, load_model, save_model

from deepctr.inputs import SparseFeat, DenseFeat, VarLenSparseFeat,DEFAULT_GROUP_NAME
from deepctr.layers import custom_objects


SAMPLE_SIZE = 8
VOCABULARY_SIZE = 4


def get_xy_fd_din(hash_flag=False):


    feature_columns = [SparseFeat('user',3),SparseFeat(
        'gender', 2), SparseFeat('item', 3 + 1), SparseFeat('item_gender', 2 + 1),DenseFeat('score', 1)]
    feature_columns += [VarLenSparseFeat(SparseFeat('hist_item', vocabulary_size=3 + 1,embedding_dim=8,embedding_name='item'), maxlen=4),
                        VarLenSparseFeat(SparseFeat('hist_item_gender', 2 + 1,embedding_dim=4, embedding_name='item_gender'), maxlen=4)]

    behavior_feature_list = ["item", "item_gender"]
    uid = np.array([0, 1, 2])
    ugender = np.array([0, 1, 0])
    iid = np.array([1, 2, 3])  # 0 is mask value
    igender = np.array([1, 2, 1])  # 0 is mask value
    score = np.array([0.1, 0.2, 0.3])

    hist_iid = np.array([[1, 2, 3, 0], [1, 2, 3, 0], [1, 2, 0, 0]])
    hist_igender = np.array([[1, 1, 2, 0], [2, 1, 1, 0], [2, 1, 0, 0]])

    feature_dict = {'user': uid, 'gender': ugender, 'item': iid, 'item_gender': igender,
                    'hist_item': hist_iid, 'hist_item_gender': hist_igender, 'score': score}

    from deepctr.inputs import get_feature_names
    feature_names = get_feature_names(feature_columns)
    x = {name:feature_dict[name] for name in feature_names}
    y = [1, 0, 1]
    return x, y, feature_columns, behavior_feature_list

def get_xy_fd_dien(use_neg=False, hash_flag=False):

    feature_columns = [SparseFeat('user', 3,hash_flag),
                       SparseFeat('gender', 2,hash_flag),
                       SparseFeat('item', 3+1,hash_flag),
                       SparseFeat('item_gender', 2+1,hash_flag),
                       DenseFeat('score', 1)]

    feature_columns += [
        VarLenSparseFeat(SparseFeat('hist_item', vocabulary_size=3 + 1, embedding_dim=8, embedding_name='item'),
                         maxlen=4),
        VarLenSparseFeat(SparseFeat('hist_item_gender', 2 + 1, embedding_dim=4, embedding_name='item_gender'), maxlen=4)]

    behavior_feature_list = ["item","item_gender"]
    uid = np.array([0, 1, 2])
    ugender = np.array([0, 1, 0])
    iid = np.array([1, 2, 3])#0 is mask value
    igender = np.array([1, 2, 1])# 0 is mask value
    score = np.array([0.1, 0.2, 0.3])

    hist_iid = np.array([[ 1, 2, 3,0], [ 1, 2, 3,0], [ 1, 2, 0,0]])
    hist_igender = np.array([[1, 1, 2,0 ], [2, 1, 1, 0], [2, 1, 0, 0]])

    behavior_length = np.array([3,3,2])

    feature_dict = {'user': uid, 'gender': ugender, 'item': iid, 'item_gender': igender,
                    'hist_item': hist_iid, 'hist_item_gender': hist_igender,
                    'score': score}


    if use_neg:
        feature_dict['neg_hist_item'] = np.array([[1, 2, 3, 0], [1, 2, 3, 0], [1, 2, 0, 0]])
        feature_dict['neg_hist_item_gender'] = np.array([[1, 1, 2, 0], [2, 1, 1, 0], [2, 1, 0, 0]])
        feature_columns += [
            VarLenSparseFeat(SparseFeat('neg_hist_item', vocabulary_size=3 + 1, embedding_dim=8, embedding_name='item'),
                             maxlen=4),
            VarLenSparseFeat(SparseFeat('neg_hist_item_gender', 2 + 1, embedding_dim=4, embedding_name='item_gender'),
                             maxlen=4)]

    from deepctr.inputs import get_feature_names
    feature_names = get_feature_names(feature_columns)
    x = {name:feature_dict[name] for name in feature_names}
    x["seq_length"] = behavior_length
    y = [1, 0, 1]
    return x, y, feature_columns, behavior_feature_list

def get_xy_fd_dsin(hash_flag=False):
    feature_columns = [SparseFeat('user', 3, use_hash=hash_flag),
                       SparseFeat('gender', 2, use_hash=hash_flag),
                       SparseFeat('item', 3 + 1, use_hash=hash_flag),
                       SparseFeat('item_gender', 2 + 1, use_hash=hash_flag),
                       DenseFeat('score', 1)]
    feature_columns += [
        VarLenSparseFeat(SparseFeat('sess_0_item', 3 + 1, embedding_dim=4, use_hash=hash_flag, embedding_name='item'),
                         maxlen=4), VarLenSparseFeat(
            SparseFeat('sess_0_item_gender', 2 + 1, embedding_dim=4, use_hash=hash_flag, embedding_name='item_gender'),
            maxlen=4)]
    feature_columns += [
        VarLenSparseFeat(SparseFeat('sess_1_item', 3 + 1, embedding_dim=4, use_hash=hash_flag, embedding_name='item'),
                         maxlen=4), VarLenSparseFeat(
            SparseFeat('sess_1_item_gender', 2 + 1, embedding_dim=4, use_hash=hash_flag, embedding_name='item_gender'),
            maxlen=4)]

    behavior_feature_list = ["item", "item_gender"]
    uid = np.array([0, 1, 2])
    ugender = np.array([0, 1, 0])
    iid = np.array([1, 2, 3])  # 0 is mask value
    igender = np.array([1, 2, 1])  # 0 is mask value
    score = np.array([0.1, 0.2, 0.3])

    sess1_iid = np.array([[1, 2, 3, 0], [1, 2, 3, 0], [0, 0, 0, 0]])
    sess1_igender = np.array([[1, 1, 2, 0], [2, 1, 1, 0], [0, 0, 0, 0]])

    sess2_iid = np.array([[1, 2, 3, 0], [0, 0, 0, 0], [0, 0, 0, 0]])
    sess2_igender = np.array([[1, 1, 2, 0], [0, 0, 0, 0], [0, 0, 0, 0]])

    sess_number = np.array([2, 1, 0])

    feature_dict = {'user': uid, 'gender': ugender, 'item': iid, 'item_gender': igender,
                    'sess_0_item': sess1_iid, 'sess_0_item_gender': sess1_igender, 'score': score,
                    'sess_1_item': sess2_iid, 'sess_1_item_gender': sess2_igender, }

    from deepctr.inputs import get_feature_names
    x = {name: feature_dict[name] for name in get_feature_names(feature_columns)}
    x["sess_length"] = sess_number

    y = [1, 0, 1]
    return x, y, feature_columns, behavior_feature_list


def gen_sequence(dim, max_len, sample_size):
    return np.array([np.random.randint(0, dim, max_len) for _ in range(sample_size)]), np.random.randint(1, max_len + 1,
                                                                                                         sample_size)


def get_test_data(sample_size=1000, embedding_size=4, sparse_feature_num=1, dense_feature_num=1,
                  sequence_feature=None, classification=True, include_length=False,
                  hash_flag=False, prefix='', use_group=False):
    if not sequence_feature:
        sequence_feature = ['sum', 'mean', 'max', 'weight']
    feature_columns = []
    model_input = {}
    if 'weight' in sequence_feature:
        feature_columns.append(
            VarLenSparseFeat(SparseFeat(prefix + "weighted_seq", vocabulary_size=2, embedding_dim=embedding_size),
                             maxlen=3, length_name=prefix + "weighted_seq" + "_seq_length",
                             weight_name=prefix + "weight"))
        s_input, s_len_input = gen_sequence(
            2, 3, sample_size)

        model_input[prefix + "weighted_seq"] = s_input
        model_input[prefix + 'weight'] = np.random.randn(sample_size, 3, 1)
        model_input[prefix + "weighted_seq" + "_seq_length"] = s_len_input
        sequence_feature.pop(sequence_feature.index('weight'))

    for i in range(sparse_feature_num):
        if use_group:
            group_name = str(i%3)
        else:
            group_name = DEFAULT_GROUP_NAME
        dim = np.random.randint(1, 10)
        feature_columns.append(
            SparseFeat(prefix + 'sparse_feature_' + str(i), dim, embedding_size, use_hash=hash_flag, dtype=tf.int32,group_name=group_name))

    for i in range(dense_feature_num):
        feature_columns.append(DenseFeat(prefix + 'dense_feature_' + str(i), 1, dtype=tf.float32))
    for i, mode in enumerate(sequence_feature):
        dim = np.random.randint(1, 10)
        maxlen = np.random.randint(1, 10)
        feature_columns.append(
            VarLenSparseFeat(SparseFeat(prefix + 'sequence_' + mode, vocabulary_size=dim, embedding_dim=embedding_size),
                             maxlen=maxlen, combiner=mode))

    for fc in feature_columns:
        if isinstance(fc, SparseFeat):
            model_input[fc.name] = np.random.randint(0, fc.vocabulary_size, sample_size)
        elif isinstance(fc, DenseFeat):
            model_input[fc.name] = np.random.random(sample_size)
        else:
            s_input, s_len_input = gen_sequence(
                fc.vocabulary_size, fc.maxlen, sample_size)
            model_input[fc.name] = s_input
            if include_length:
                fc.length_name = prefix + "sequence_" + str(i) + '_seq_length'
                model_input[prefix + "sequence_" + str(i) + '_seq_length'] = s_len_input

    if classification:
        y = np.random.randint(0, 2, sample_size)
    else:
        y = np.random.random(sample_size)

    return model_input, y, feature_columns


def layer_test(layer_cls, kwargs={}, input_shape=None, input_dtype=None,

               input_data=None, expected_output=None,

               expected_output_dtype=None, fixed_batch_size=False, supports_masking=False):
    # generate input data

    if input_data is None:

        if not input_shape:
            raise AssertionError()

        if not input_dtype:
            input_dtype = K.floatx()

        input_data_shape = list(input_shape)

        for i, e in enumerate(input_data_shape):

            if e is None:
                input_data_shape[i] = np.random.randint(1, 4)
        input_mask = []
        if all(isinstance(e, tuple) for e in input_data_shape):
            input_data = []

            for e in input_data_shape:
                input_data.append(
                    (10 * np.random.random(e)).astype(input_dtype))
                if supports_masking:
                    a = np.full(e[:2], False)
                    a[:, :e[1] // 2] = True
                    input_mask.append(a)

        else:

            input_data = (10 * np.random.random(input_data_shape))

            input_data = input_data.astype(input_dtype)
            if supports_masking:
                a = np.full(input_data_shape[:2], False)
                a[:, :input_data_shape[1] // 2] = True

                print(a)
                print(a.shape)
                input_mask.append(a)

    else:

        if input_shape is None:
            input_shape = input_data.shape

        if input_dtype is None:
            input_dtype = input_data.dtype

    if expected_output_dtype is None:
        expected_output_dtype = input_dtype

    # instantiation

    layer = layer_cls(**kwargs)

    # test get_weights , set_weights at layer level

    weights = layer.get_weights()

    layer.set_weights(weights)

    try:
        expected_output_shape = layer.compute_output_shape(input_shape)
    except Exception:
        expected_output_shape = layer._compute_output_shape(input_shape)

    # test in functional API
    if isinstance(input_shape, list):
        if fixed_batch_size:

            x = [Input(batch_shape=e, dtype=input_dtype) for e in input_shape]
            if supports_masking:
                mask = [Input(batch_shape=e[0:2], dtype=bool)
                        for e in input_shape]

        else:

            x = [Input(shape=e[1:], dtype=input_dtype) for e in input_shape]
            if supports_masking:
                mask = [Input(shape=(e[1],), dtype=bool) for e in input_shape]

    else:
        if fixed_batch_size:

            x = Input(batch_shape=input_shape, dtype=input_dtype)
            if supports_masking:
                mask = Input(batch_shape=input_shape[0:2], dtype=bool)

        else:

            x = Input(shape=input_shape[1:], dtype=input_dtype)
            if supports_masking:
                mask = Input(shape=(input_shape[1],), dtype=bool)

    if supports_masking:

        y = layer(Masking()(x), mask=mask)
    else:
        y = layer(x)

    if not (K.dtype(y) == expected_output_dtype):
        raise AssertionError()

    # check with the functional API
    if supports_masking:
        model = Model([x, mask], y)

        actual_output = model.predict([input_data, input_mask[0]])
    else:
        model = Model(x, y)

        actual_output = model.predict(input_data)

    actual_output_shape = actual_output.shape
    for expected_dim, actual_dim in zip(expected_output_shape,

                                        actual_output_shape):

        if expected_dim is not None:

            if not (expected_dim == actual_dim):
                raise AssertionError("expected_shape", expected_output_shape, "actual_shape", actual_output_shape)

    if expected_output is not None:
        assert_allclose(actual_output, expected_output, rtol=1e-3)

    # test serialization, weight setting at model level

    model_config = model.get_config()

    recovered_model = model.__class__.from_config(model_config)

    if model.weights:
        weights = model.get_weights()

        recovered_model.set_weights(weights)

        _output = recovered_model.predict(input_data)

        assert_allclose(_output, actual_output, rtol=1e-3)

    # test training mode (e.g. useful when the layer has a

    # different behavior at training and testing time).

    if has_arg(layer.call, 'training'):
        model.compile('rmsprop', 'mse')

        model.train_on_batch(input_data, actual_output)

    # test instantiation from layer config

    layer_config = layer.get_config()

    layer_config['batch_input_shape'] = input_shape

    layer = layer.__class__.from_config(layer_config)

    # for further checks in the caller function

    return actual_output


def has_arg(fn, name, accept_all=False):
    """Checks if a callable accepts a given keyword argument.



    For Python 2, checks if there is an argument with the given name.



    For Python 3, checks if there is an argument with the given name, and

    also whether this argument can be called with a keyword (i.e. if it is

    not a positional-only argument).



    # Arguments

        fn: Callable to inspect.

        name: Check if `fn` can be called with `name` as a keyword argument.

        accept_all: What to return if there is no parameter called `name`

                    but the function accepts a `**kwargs` argument.



    # Returns

        bool, whether `fn` accepts a `name` keyword argument.

    """

    if sys.version_info < (3,):

        arg_spec = inspect.getargspec(fn)

        if accept_all and arg_spec.keywords is not None:
            return True

        return (name in arg_spec.args)

    elif sys.version_info < (3, 3):

        arg_spec = inspect.getfullargspec(fn)

        if accept_all and arg_spec.varkw is not None:
            return True

        return (name in arg_spec.args or

                name in arg_spec.kwonlyargs)

    else:

        signature = inspect.signature(fn)

        parameter = signature.parameters.get(name)

        if parameter is None:

            if accept_all:

                for param in signature.parameters.values():

                    if param.kind == inspect.Parameter.VAR_KEYWORD:
                        return True

            return False

        return (parameter.kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD,

                                   inspect.Parameter.KEYWORD_ONLY))


def check_model(model, model_name, x, y, check_model_io=True):
    """
    compile model,train and evaluate it,then save/load weight and model file.
    model:
    model_name:
    x:
    y:
    check_model_io: test save/load model file or not
    :return:
    """

    model.compile('adam', 'binary_crossentropy',
                  metrics=['binary_crossentropy'])
    model.fit(x, y, batch_size=100, epochs=1, validation_split=0.5)

    print(model_name + " test train valid pass!")
    model.save_weights(model_name + '_weights.h5')
    model.load_weights(model_name + '_weights.h5')
    os.remove(model_name + '_weights.h5')
    print(model_name + " test save load weight pass!")
    if check_model_io:
        save_model(model, model_name + '.h5')
        model = load_model(model_name + '.h5', custom_objects)
        os.remove(model_name + '.h5')
        print(model_name + " test save load model pass!")

    print(model_name + " test pass!")
