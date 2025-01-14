from jsoncomment import JsonComment ; json = JsonComment()
import os
import copy

import numpy as np
import pandas as pd
import torch
from torch import optim
from torch.nn import functional as F

####################################################################################################
from mlmodels.util import  os_package_root_path, log, path_norm, get_model_uri

VERBOSE = False
MODEL_URI = get_model_uri(__file__)




####################################################################################################
from mlmodels.model_tch.raw.nbeats.model import NBeatsNet





# Model
class Model:
    def __init__(self, model_pars=None, data_pars=None, compute_pars=None):
        """ Model:__init__.
        Doc::
                
                    Args:
                        model_pars:     
                        data_pars:     
                        compute_pars:     
                    Returns:
                       
        """
        self.model_pars = model_pars    

        if model_pars is None : 
            self.model = None
            return None


        #### Remove Params
        if model_pars.get("model_uri") :
            del model_pars["model_uri"]
        self.model = NBeatsNet(**model_pars)




####################################################################################################
def get_data(data_pars):
  """function get_data.
  Doc::
          
        Args:
            data_pars:   
        Returns:
            
  """
  d = data_pars

  pred_length = d["prediction_length"]
  features    = d["col_Xinput"]
  target      = d["col_ytarget"]
  feat_len    = len(features)


  if d.get("test_data_path"):
    test = pd.read_csv(path_norm(data_pars["test_data_path"]))
    x_test = test[features]
    del test
    x_test = x_test.values.reshape(-1, pred_length, feat_len)
    y_test = test[target].fillna(0)
    y_test = y_test.values.reshape(-1, pred_length, 1)        
    
    if d["predict_only"]:        
        return x_test, y_test
    
    train = pd.read_csv(path_norm( data_pars["train_data_path"]))
    x_train = train[features]
    del train
    x_train = x_train.values.reshape(-1, pred_length, feat_len)
    y_train = train[features].shift().fillna(0)
    y_train = y_train.values.reshape(-1, pred_length, 1)

    return x_train, y_train, x_test, y_test






def get_dataset(**kw):
    """function get_dataset.
    Doc::
            
            Args:
                **kw:   
            Returns:
                
    """
    data_path = path_norm( kw['train_data_path'] )
    train_split_ratio = kw.get("train_split_ratio", 0.8)

    df = pd.read_csv(data_path,  parse_dates=True)

    #### Filter by columns 
    df = df[ kw['col_Xinput'] ]
    df = df.fillna(method="pad")

    if kw.get("test_data_path"):
        test = pd.read_csv( path_norm(kw["test_data_path"]),  parse_dates=True)
        test = test[ kw['col_Xinput'] ]        
        test = test.fillna(method="pad")

        df = df.append(test)
        train_split_ratio = kw["forecast_length"] / df.shape[0]
    

    if VERBOSE: print(df.head(5))

    #### Preprocess

    df = df.values  # just keep np array here for simplicity.
    norm_constant = np.max(df)
    df = df / norm_constant  # small leak to the test set here.
    print(df)

    x_train_batch, y = [], []
    backcast_length  = kw['backcast_length']
    forecast_length  = kw['forecast_length']
    for i in range(backcast_length, len(df) - forecast_length):
        x_train_batch.append(df[i - backcast_length:i])
        y.append(df[i:i + forecast_length])

    x_train_batch = np.array(x_train_batch)[..., 0]
    y = np.array(y)[..., 0]

    #### Split   ###############################################
    c                = int(len(x_train_batch) * train_split_ratio)
    x_train, y_train = x_train_batch[:c], y[:c]
    x_test, y_test   = x_train_batch[c:], y[c:]
    return x_train, y_train, x_test, y_test, norm_constant



def data_generator(x_full, y_full, bs):
    """function data_generator.
    Doc::
            
            Args:
                x_full:   
                y_full:   
                bs:   
            Returns:
                
    """
    def split(arr, size):
        arrays = []
        while len(arr) > size:
            slice_ = arr[:size]
            arrays.append(slice_)
            arr = arr[size:]
        arrays.append(arr)
        return arrays

    while True:
        for rr in split((x_full, y_full), bs):
            yield rr


######################################################################################################
# Model fit
def fit(model, data_pars=None, compute_pars=None, out_pars=None, **kw):
    """function fit.
    Doc::
            
            Args:
                model:   
                data_pars:   
                compute_pars:   
                out_pars:   
                **kw:   
            Returns:
                
    """
    device = torch.device('cpu')
    forecast_length = data_pars["forecast_length"]
    backcast_length = data_pars["backcast_length"]
    batch_size = compute_pars["batch_size"]  # greater than 4 for viz
    disable_plot = compute_pars["disable_plot"]


    # model0 = model.model
    model0 = model.model

    ### Get Data
    x_train, y_train, x_test, y_test, _ = get_dataset(**data_pars)
    data_gen = data_generator(x_train, y_train, batch_size)

    ### Setup session
    # print("[DEBUG] from fir of nbeats parameter {}\n",format(model.parameters()))
    optimiser = optim.Adam(model0.parameters())

    ### fit model
    net, optimiser = fit_simple(model0, optimiser, data_gen, plot_model, device, data_pars, out_pars)

    model.model = net
    return model, optimiser


def fit_simple(net, optimiser, data_generator, on_save_callback, device, data_pars, out_pars, max_grad_steps=500):
    """function fit_simple.
    Doc::
            
            Args:
                net:   
                optimiser:   
                data_generator:   
                on_save_callback:   
                device:   
                data_pars:   
                out_pars:   
                max_grad_steps:   
            Returns:
                
    """
    print('--- fiting ---')
    initial_grad_step = load_checkpoint(net, optimiser)

    for grad_step, (x, target) in enumerate(data_generator):
        grad_step += initial_grad_step
        optimiser.zero_grad()
        net.train()
        backcast, forecast = net(torch.tensor(x, dtype=torch.float).to(device))
        loss = F.mse_loss(forecast, torch.tensor(target, dtype=torch.float).to(device))
        loss.backward()
        optimiser.step()

        print(f'grad_step = {str(grad_step).zfill(6)}, loss = {loss.item():.6f}')
        if grad_step % 100 == 0 or (grad_step < 100 and grad_step % 100 == 0):
            with torch.no_grad():
                save_checkpoint(net, optimiser, grad_step)
                if on_save_callback is not None:
                    on_save_callback(net, x, target, grad_step, data_pars)

        if grad_step > max_grad_steps:
            print('Finished.')
            break
    return net, optimiser



def predict(model, data_pars=None, compute_pars=None, out_pars=None, **kw):
    """function predict.
    Doc::
            
            Args:
                model:   
                data_pars:   
                compute_pars:   
                out_pars:   
                **kw:   
            Returns:
                
    """
    model0 = model.model
    _, _, x_test, y_test, _ = get_dataset(**data_pars)

   
    test_losses = []
    model0.eval()
    _, f = model0(torch.tensor(x_test, dtype=torch.float))
    test_losses.append(F.mse_loss(f, torch.tensor(y_test, dtype=torch.float)).item())
    y_pred = f.detach().numpy()
    return y_pred, y_test



###############################################################################################################
def plot(net, x, target, backcast_length, forecast_length, grad_step, out_path="./"):
    """function plot.
    Doc::
            
            Args:
                net:   
                x:   
                target:   
                backcast_length:   
                forecast_length:   
                grad_step:   
                out_path:   
            Returns:
                
    """
    import matplotlib.pyplot as plt
    net.eval()
    _, f = net(torch.tensor(x, dtype=torch.float))
    subplots = [221, 222, 223, 224]

    plt.figure(1)
    plt.subplots_adjust(top=0.88)
    for i in range(4):
        ff, xx, yy = f.cpu().numpy()[i], x[i], target[i]
        plt.subplot(subplots[i])
        plt.plot(range(0, backcast_length), xx, color='b')
        plt.plot(range(backcast_length, backcast_length + forecast_length), yy, color='g')
        plt.plot(range(backcast_length, backcast_length + forecast_length), ff, color='r')
        # plt.title(f'step #{grad_step} ({i})')

    output = f'{out_path}/n_beats_{grad_step}.png'
    # plt.savefig(output)
    plt.clf()
    print('Saved image to {}.'.format(output))


def plot_model(net, x, target, grad_step, data_pars, disable_plot=False):
    """function plot_model.
    Doc::
            
            Args:
                net:   
                x:   
                target:   
                grad_step:   
                data_pars:   
                disable_plot:   
            Returns:
                
    """
    forecast_length = data_pars["forecast_length"]
    backcast_length = data_pars["backcast_length"]

    # batch_size = compute_pars["batch_size"]  # greater than 4 for viz
    # disable_plot = compute_pars.get("disable_plot", False)

    if not disable_plot:
        print('plot()')
        plot(net, x, target, backcast_length, forecast_length, grad_step)


def plot_predict(x_test, y_test, p, data_pars, compute_pars, out_pars):
    """function plot_predict.
    Doc::
            
            Args:
                x_test:   
                y_test:   
                p:   
                data_pars:   
                compute_pars:   
                out_pars:   
            Returns:
                
    """
    import matplotlib.pyplot as plt
    forecast_length = data_pars["forecast_length"]
    backcast_length = data_pars["backcast_length"]
    norm_constant = compute_pars["norm_contsant"]
    out_path = out_pars['out_path']
    if not os.path.exists(out_path): os.makedirs(out_path, exist_ok=True)
    output = f'{out_path}/n_beats_test.png'

    subplots = [221, 222, 223, 224]
    plt.figure(1)
    plt.subplots_adjust(top=0.88)
    for plot_id, i in enumerate(np.random.choice(range(len(p)), size=4, replace=False)):
        ff, xx, yy = p[i] * norm_constant, x_test[i] * norm_constant, y_test[i] * norm_constant
        plt.subplot(subplots[plot_id])
        plt.grid()
        plt.plot(range(0, backcast_length), xx, color='b')
        plt.plot(range(backcast_length, backcast_length + forecast_length), yy, color='g')
        plt.plot(range(backcast_length, backcast_length + forecast_length), ff, color='r')
    # plt.savefig(output)
    plt.clf()
    print('Saved image to {}.'.format(output))


###############################################################################################################
# save and load model helper function

def save_checkpoint(model, optimiser, grad_step, CHECKPOINT_NAME="mycheckpoint"):
    """function save_checkpoint.
    Doc::
            
            Args:
                model:   
                optimiser:   
                grad_step:   
                CHECKPOINT_NAME:   
            Returns:
                
    """
    torch.save({
        'grad_step': grad_step,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimiser.state_dict(),
    }, CHECKPOINT_NAME)


def load_checkpoint(model, optimiser, CHECKPOINT_NAME='nbeats-fiting-checkpoint.th'):
    """function load_checkpoint.
    Doc::
            
            Args:
                model:   
                optimiser:   
                CHECKPOINT_NAME:   
            Returns:
                
    """
    if os.path.exists(CHECKPOINT_NAME):
        checkpoint = torch.load(CHECKPOINT_NAME)
        model.load_state_dict(checkpoint['model_state_dict'])
        optimiser.load_state_dict(checkpoint['optimizer_state_dict'])
        grad_step = checkpoint['grad_step']
        print(f'Restored checkpoint from {CHECKPOINT_NAME}.')
        return grad_step
    return 0




def save(model, session, save_pars):
    """function save.
    Doc::
            
            Args:
                model:   
                session:   
                save_pars:   
            Returns:
                
    """
    model0          = model.model
    optimiser       = session
    grad_step       = save_pars['grad_step']
    CHECKPOINT_NAME = save_pars['checkpoint_name']
    torch.save({
        'grad_step': grad_step,
        'model_state_dict': model0.state_dict(),
        'optimizer_state_dict': optimiser.state_dict(),
    }, CHECKPOINT_NAME)


def load(load_pars):
    """function load.
    Doc::
            
            Args:
                load_pars:   
            Returns:
                
    """
    model   = None
    session = None




#############################################################################################################
def get_params(param_pars, **kw):
    """function get_params.
    Doc::
            
            Args:
                param_pars:   
                **kw:   
            Returns:
                
    """
    from jsoncomment import JsonComment ; json = JsonComment()
    pp = param_pars
    choice = pp['choice']
    config_mode = pp['config_mode']
    data_path = pp['data_path']


    if choice == "json":
        data_path = path_norm(data_path)
        cf = json.load(open(data_path, mode='r'))
        cf = cf[config_mode]

        cf['model_pars']["stack_types"]  =  [NBeatsNet.GENERIC_BLOCK, NBeatsNet.GENERIC_BLOCK]

        return cf['model_pars'], cf['data_pars'], cf['compute_pars'], cf['out_pars']



    if choice == "test01":
        log("#### Path params   ########################################################")
        data_path  = path_norm( "dataset/timeseries/milk.csv"  )   
        out_path   = path_norm( "ztest/model_tch/nbeats/" )   
        model_path = os.path.join(out_path , "model")
        print(data_path, out_path)  

        data_pars = {"data_path": data_path, "forecast_length": 5, "backcast_length": 10}

        device = torch.device('cpu')

        model_pars = {"stack_types": [NBeatsNet.GENERIC_BLOCK, NBeatsNet.GENERIC_BLOCK],
                      "device": device,
                      "nb_blocks_per_stack": 3, "forecast_length": 5, "backcast_length": 10,
                      "thetas_dims": [7, 8], "share_weights_in_stack": False, "hidden_layer_units": 256}

        compute_pars = {"batch_size": 100, "disable_plot": False,
                        "norm_contsant": 1.0,
                        "result_path": out_path + '/n_beats_test{}.png',
                        "model_path": "mycheckpoint"}

        out_pars = {"out_path": out_path + "/", 
                    "model_checkpoint" : out_path +"/model_checkpoint/"}

        return model_pars, data_pars, compute_pars, out_pars





#############################################################################################################

def test(choice="json", data_path="nbeats.json", config_mode="test"):
    """function test.
    Doc::
            
            Args:
                choice:   
                data_path:   
                config_mode:   
            Returns:
                
    """
    ###loading the command line arguments

    log("#### Loading params   #######################################")
    param_pars = { "choice" : choice, "data_path" : data_path, "config_mode" : config_mode }
    model_pars, data_pars, compute_pars, out_pars = get_params(param_pars)


    log("#### Loading dataset  #######################################")
    x_train, y_train, x_test, y_test, norm_const = get_dataset(**data_pars)


    log("#### Model setup   ##########################################")
    model = Model(model_pars, data_pars, compute_pars)

    log("#### Model fit   ############################################")
    model, optimiser = fit(model, data_pars, compute_pars, out_pars)

    log("#### Predict    #############################################")
    ypred, _ = predict(model, data_pars, compute_pars, out_pars)
    print(ypred)

    log("#### Plot     ###############################################")
    plot_predict(x_test, y_test, ypred, data_pars, compute_pars, out_pars)


if __name__ == '__main__':
    VERBOSE = True
    test(choice="json", data_path="model_tch/nbeats.json")

    # test()



