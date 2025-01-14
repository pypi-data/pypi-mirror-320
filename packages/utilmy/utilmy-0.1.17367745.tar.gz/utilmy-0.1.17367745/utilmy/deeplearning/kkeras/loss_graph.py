# -*- coding: utf-8 -*-
"""nsl_graph_losses.ipynb
Original file is located at
    https://colab.research.google.com/drive/11BWemRJoxYmz3YpvX4MBxRomOu2IJQa6
#!pip install neural_structured_learning

"""
from numpy import ndarray
from typing import Tuple
import numpy as np, tensorflow as tf

try :
    import neural_structured_learning as nsl
    from neural_structured_learning.keras import layers as nsl_layers
    import neural_structured_learning.configs as nsl_configs
except Exception as e :
    print(e)
    print("pip install neural_structured_learning ") ; 1/0


######################################################################################
from utilmy import log, log2

def help():
    from utilmy import help_create
    print(help_create(__file__) )



######################################################################################
def test_graph_loss() -> None:
    """
    Summary: Calculates the graph loss
    """

    # Prepare data.
    max_neighbors = 2
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
    x_train, x_test = x_train / 255.0, x_test / 255.0

    # Create fake neighbors
    neighbors_train, neighbor_train_weights = create_fake_neighbor(x_train, max_neighbors)
    neighbors_test, neighbor_test_weights   = create_fake_neighbor(x_test, max_neighbors)

    ### Train
    train_ds = tf.data.Dataset.from_tensor_slices((x_train, y_train, neighbors_train, neighbor_train_weights))
    train_ds = train_ds.shuffle(buffer_size=x_train.shape[0])
    train_ds = train_ds.batch(32)
    train_ds = train_ds.map(map_func, num_parallel_calls=2)
    train_ds = train_ds.prefetch(1)

    ### Test
    test_ds = tf.data.Dataset.from_tensor_slices((x_train, y_train, neighbors_train, neighbor_train_weights))
    test_ds = test_ds.shuffle(buffer_size=x_train.shape[0])
    test_ds = test_ds.batch(32)
    test_ds = test_ds.map(map_func, num_parallel_calls=2)
    test_ds = test_ds.prefetch(1)


    base_model = tf.keras.Sequential([
        tf.keras.Input((28, 28), name='feature'),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(128, activation=tf.nn.relu),
        tf.keras.layers.Dense(10, activation=tf.nn.softmax)
    ])


    ##### Compute     
    nbr_features_layer, regularizer  = create_graph_loss(max_neighbors=2)
    
    cross_entropy = tf.keras.losses.SparseCategoricalCrossentropy()
    optimizer     = tf.keras.optimizers.Adam(1e-3)

    ##### Train Loop 
    for epoch in range(1):
        #### Train Loop #######################
        for i, (images, labels) in enumerate(train_ds):
            outputs, total_loss, labeled_loss, graph_loss = train_step(images, labels, base_model, cross_entropy, optimizer,
                                                                       nbr_features_layer, regularizer
                                                                      )
            y_pred   = np.argmax(outputs.numpy(), 1)
            accuracy = (y_pred == labels.numpy()).mean()
        print('[Epoch {:03d} iter {:04d}] Loss: {:.4f} - Labeled loss: {:.4f} - Graph loss: {:.4f} - Accuracy: {:.4f}'.format(
                epoch+1, i+1, total_loss.numpy(), labeled_loss.numpy(), graph_loss.numpy(), accuracy)
        )

        
        #### Test Loop   ##########################################
        test_loss = []
        correct_cnt = 0
        total = 0
        for i, (images, labels) in enumerate(test_ds):
            outputs, total_loss, labeled_loss, graph_loss = test_step(images, labels, base_model, cross_entropy,
                                                                      nbr_features_layer, regularizer
                                                                     )
            correct_cnt += int((np.argmax(outputs.numpy(), 1) == labels.numpy()).sum())
            total += len(outputs)
            test_loss.append(total_loss.numpy())

        test_accuracy = (correct_cnt / total) if total > 0 else 0
        print('[Epoch {:03d}] Test Loss: {:.4f} Test Accuracy: {:.4f}\n'.format(
            epoch+1, np.mean(test_loss), test_accuracy
        ))



def test_adversarial() -> None:
    """
    Summary: Adversarial Regularization """
    # Prepare data.
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
    x_train, x_test = x_train / 255.0, x_test / 255.0

    train_ds = tf.data.Dataset.from_tensor_slices((x_train, y_train))
    train_ds = train_ds.shuffle(buffer_size=x_train.shape[0])
    train_ds = train_ds.batch(32)
    train_ds = train_ds.prefetch(1)

    test_ds = tf.data.Dataset.from_tensor_slices((x_test, y_test))
    test_ds = test_ds.shuffle(buffer_size=x_test.shape[0])
    test_ds = test_ds.batch(32)
    test_ds = test_ds.prefetch(1)

    base_model = tf.keras.Sequential([
        tf.keras.Input((28, 28), name='feature'),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(128, activation=tf.nn.relu),
        tf.keras.layers.Dense(10, activation=tf.nn.softmax)
    ])

    cross_entropy = tf.keras.losses.SparseCategoricalCrossentropy()
    optimizer = tf.keras.optimizers.Adam(1e-3)    
    
    
    # Wrap the model with adversarial regularization.
    # adv_config = nsl.configs.make_adv_reg_config(multiplier=0.2, adv_step_size=0.05)
    # adv_model = nsl.keras.AdversarialRegularization(base_model, label_keys=['label'], adv_config=adv_config)

    # adv_model.compile(optimizer='adam', loss='sparse_categorical_crossentropy',
    #                    metrics=['acc'])


    for epoch in range(10):
        for i, (images, labels) in enumerate(train_ds):
            outputs, total_loss, labeled_loss, adv_loss = train_step(images, labels, base_model, cross_entropy, optimizer)
            y_pred = np.argmax(outputs.numpy(), 1)
            accuracy = (y_pred == labels.numpy()).mean()
        print('[Epoch {:03d} iter {:04d}] Loss: {:.4f} - Accuracy: {:.4f}'.format(
                epoch+1, i+1, total_loss.numpy(), accuracy)
        )

        test_loss = []
        correct_cnt = 0
        total = 0
        for i, (images, labels) in enumerate(test_ds):
            outputs, total_loss, labeled_loss, adv_loss = test_step(images, labels, base_model, cross_entropy)
            correct_cnt += int((np.argmax(outputs.numpy(), 1) == labels.numpy()).sum())
            total += len(outputs)
            test_loss.append(total_loss.numpy())

        test_accuracy = (correct_cnt / total) if total > 0 else 0
        print('[Epoch {:03d}] Test Loss: {:.4f} Test Accuracy: {:.4f}\n'.format(
            epoch+1, np.mean(test_loss), test_accuracy
        ))

        
        
#################################################################################################################
"""# Graph regularization"""
def create_fake_neighbor(x: ndarray, max_neighbors: int) -> Tuple[ndarray, ndarray]:
    """
    Summary: Graph regularization

    Parameter:
    x (np.array):
    max_neighbors (integer):

    Returns:
    np.array: containing neighbors
    np.array: containing neighbor_weights
    """

    n                = x.shape[0]
    neighbors        = []
    neighbor_weights = []
    for i in range(n):
        neighbors.append(x[np.random.choice(n, max_neighbors)])
        neighbor_weights.append(np.ones((max_neighbors,)))

    return np.array(neighbors), np.array(neighbor_weights)


def map_func(x_batch, y_batch, neighbors, neighbor_weights):
    """
    Summary: Maps x_batch features

    Parameter:
    x_batch (np.array):
    y_batch (np.array):
    neighbors (data_type):
    neighbor_weights (data_type):

    Returns:
    features_dict (dictionary): containing mapped features of x_batch
    y_batch (np.array):
    """

    feature_name = 'feature'
    # for x_batch, y_batch, neighbors, neighbor_weights in ds:
    # x_batch, y_batch, neighbors, neighbor_weights = samples
    features_dict = {feature_name: x_batch}

    n_neighbors = neighbors.shape[1]
    for i in range(n_neighbors):
        neighbor_feat_name = f'NL_nbr_{i}_{feature_name}'
        neighbor_weight_name = f'NL_nbr_{i}_weight'
        features_dict[neighbor_feat_name] = neighbors[:, i, ...]
        features_dict[neighbor_weight_name] = neighbor_weights[:, i:i+1]
    return features_dict, y_batch


def create_graph_loss(max_neighbors=2):
    """
    Summary: Creates Graph loss

    Parameter:
    max_neighbors (integer):

    Returns:
    nbr_features_layer (data_type):
    regularizer (data_type):
    """

    graph_reg_config = nsl.configs.make_graph_reg_config(
        max_neighbors          = max_neighbors,
        neighbor_prefix        = 'NL_nbr_',
        neighbor_weight_suffix = '_weight',
    )

    nbr_features_layer = nsl_layers.NeighborFeatures(graph_reg_config.neighbor_config)
    regularizer        = nsl_layers.PairwiseDistance(graph_reg_config.distance_config, name='graph_loss')

    #cross_entropy = tf.keras.losses.SparseCategoricalCrossentropy()
    #optimizer     = tf.keras.optimizers.Adam(1e-3)
    return nbr_features_layer, regularizer

    
@tf.function
def train_step(x, y, model, loss_fn, optimizer, 
               nbr_features_layer=None,  ### Graph
               regularizer=None,   ## Graph
              ):   #changed file
    """
    Summary: Function defining train steps

    Parameter:
    x (np.array):
    y (np.array):
    model (data_type):
    loss_fn (data_type):
    optimizer (data_type):
    nbr_features_layer (data_type):
    regularizer (data_type):
    
    Returns:
    base_output (data_type):
    total_loss (data_type):
    labeled_loss (data_type):
    scaled_graph_loss (data_type):
    """

    #### Add Graph OPtimization to actual loss
    
    with tf.GradientTape() as tape_w:

        # A separate GradientTape is needed for watching the input.
        with tf.GradientTape() as tape_x:
            tape_x.watch(x)
            # Regular forward pass.
            if nbr_features_layer is not None :
                sample_features, nbr_features, nbr_weights = nbr_features_layer.call(x)
                base_output  = model(sample_features, training=True)
            else :
                base_output  = model(x, training=True)
            labeled_loss = loss_fn(y, base_output)

        has_nbr_inputs = nbr_weights is not None and nbr_features
        if (has_nbr_inputs and graph_reg_config.multiplier > 0):
            # Use logits for regularization.
            sample_logits = base_output
            nbr_logits    = model(nbr_features, training=True)
            graph_loss    = regularizer(sources=sample_logits, targets=nbr_logits, weights=nbr_weights)
        else:
            graph_loss = tf.constant(0, dtype=tf.float32)

        scaled_graph_loss = graph_reg_config.multiplier * graph_loss

        
        ##### Combines both losses. This could also be a weighted combination.
        total_loss = labeled_loss + scaled_graph_loss

    # Regular backward pass.
    gradients = tape_w.gradient(total_loss,  model.trainable_variables)
    optimizer.apply_gradients(zip(gradients, model.trainable_variables))
    return base_output, total_loss, labeled_loss, scaled_graph_loss



@tf.function
def test_step(x, y, model, loss_fn,
               nbr_features_layer=None,  ### Graph
               regularizer=None,        #### Graph             
             ):  
    """
    Summary: Function defining test steps

    Parameter:
    x (np.array):
    y (np.array):
    model (data_type):
    loss_fn (data_type):
    nbr_features_layer (data_type):
    regularizer (data_type):
    
    Returns:
    base_output (data_type):
    total_loss (data_type):
    labeled_loss (data_type):
    scaled_graph_loss (data_type):
    """

    # Regular forward pass.
    sample_features, nbr_features, nbr_weights = nbr_features_layer.call(x)
    base_output  = model(sample_features, training=False)
    labeled_loss = loss_fn(y, base_output)

    has_nbr_inputs = nbr_weights is not None and nbr_features
    if (has_nbr_inputs and graph_reg_config.multiplier > 0):
        # Use logits for regularization.
        sample_logits = base_output
        nbr_logits    = model(nbr_features, training=False)
        graph_loss    = regularizer(sources=sample_logits, targets=nbr_logits, weights=nbr_weights)
    else:
        graph_loss = tf.constant(0, dtype=tf.float32)

    scaled_graph_loss = graph_reg_config.multiplier * graph_loss

    # Combines both losses. This could also be a weighted combination.
    total_loss = labeled_loss + scaled_graph_loss
    return base_output, total_loss, labeled_loss, scaled_graph_loss

    
    




        
        
        
        
        
        
        
        
#############################################################################################        
#############################################################################################    

        
        
        
        
        
