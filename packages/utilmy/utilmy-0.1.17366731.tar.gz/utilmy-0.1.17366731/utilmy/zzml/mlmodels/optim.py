# -*- coding: utf-8 -*-
"""
Lightweight Functional interface to wrap Hyper-parameter Optimization

###### Model param search test
python optim.py --do test

##### #for normal optimization search method
python optim.py --do search --ntrials 1  --config_file optim_config.json --optim_method normal


###### for pruning method
python optim.py --do search --ntrials 1  --config_file optim_config.json --optim_method prune


###### HyperParam standalone run
python optim.py --model_uri model_tf.1_lstm.py  --do test
python optim.py --model_uri model_tf.1_lstm.py  --do search



"""
import argparse
from jsoncomment import JsonComment ; json = JsonComment()
import os
import copy
# import pandas as pd


####################################################################################################
# from mlmodels import models
from mlmodels.models import model_create, module_load
from mlmodels.util import log, path_norm, tf_deprecation, path_norm_dict

####################################################################################################
tf_deprecation()

VERBOSE = False


####################################################################################################
def optim(model_uri="model_tf.1_lstm",
          hypermodel_pars={},
          model_pars={},
          data_pars={},
          compute_pars={},
          out_pars={}):
    """
    Generic optimizer for hyperparamters
    Parameters
    ----------
    Returns : None
    """
    if hypermodel_pars["engine_pars"]['engine'] == "optuna":
        return optim_optuna(model_uri, hypermodel_pars,
                            model_pars, data_pars, compute_pars,
                            out_pars)

    # if hypermodel_pars["engine_pars"]['engine'] == "skopt":
    #    return optim_skopt(model_uri, hypermodel_pars,
    #                       model_pars, data_pars, compute_pars,
    #                       out_pars)

    return None


def optim_optuna(model_uri="model_tf.1_lstm.py",
                 hypermodel_pars = {"engine_pars": {}},
                 model_pars      = {},
                 data_pars       = {},
                 compute_pars    = {},  # only Model pars
                 out_pars        = {}):
    """
    ### Distributed
    https://optuna.readthedocs.io/en/latest/tutorial/distributed.html
      { 'distributed' : 1,
       'study_name' : 'ok' , 
      'storage' : 'sqlite'
     }                                       
                                       
     ###### 1st engine is optuna
     https://optuna.readthedocs.io/en/stable/installation.html
    https://github.com/pfnet/optuna/blob/master/examples/tensorflow_estimator_simple.py
    https://github.com/pfnet/optuna/tree/master/examples 

    Interface layer to Optuna  for hyperparameter optimization
    optuna create-study --study-name "distributed-example" --storage "sqlite:///example.db"
    https://optuna.readthedocs.io/en/latest/tutorial/distributed.html

    study = optuna.load_study(study_name='distributed-example', storage='sqlite:///example.db')
    study.optimize(objective, n_trials=100)
    
    weight_decay = trial.suggest_loguniform('weight_decay', 1e-10, 1e-3)
    optimizer = trial.suggest_categorical('optimizer', ['MomentumSGD', 'Adam']) # Categorical parameter
    num_layers = trial.suggest_int('num_layers', 1, 3)      # Int parameter
    dropout_rate = trial.suggest_uniform('dropout_rate', 0.0, 1.0)      # Uniform parameter
    learning_rate = trial.suggest_loguniform('learning_rate', 1e-5, 1e-2)      # Loguniform parameter
    drop_path_rate = trial.suggest_discrete_uniform('drop_path_rate', 0.0, 1.0, 0.1) # Discrete-uniform parameter
    
    """
    import optuna
    # these parameters should be inside the key "engine_pars" which should be inside "hypermodel_pars" of the config json
    engine_pars   = hypermodel_pars['engine_pars']
    ntrials       = engine_pars['ntrials']
    # metric target should be a value that is available in the model.stats of the model we are optimizing it can simply be called "loss" or 
    # specific like "roc_auc_score" 
    metric_target = engine_pars["metric_target"]

    save_path     = out_pars['path']
    # log_path      = out_pars['log_path']
    os.makedirs(save_path, exist_ok=True)    

    model_name    = model_pars.get("model_name")  #### Only for sklearn model
    # model_type    = model_pars['model_type']
    log(model_pars, data_pars, compute_pars, hypermodel_pars)

    module = module_load(model_uri)
    log(module)

    def objective(trial):
        # log("check", module, data_pars)
        for t, p in hypermodel_pars.items():

            if t == 'engine_pars': continue  ##Skip
            # type, init, range[0,1]
            x = p['type']
            if x == 'log_uniform':
                pres = trial.suggest_loguniform(t, p['range'][0], p['range'][1])
            elif x == 'int':
                pres = trial.suggest_int(t, p['range'][0], p['range'][1])
            elif x == 'categorical':
                pres = trial.suggest_categorical(t, p['value'])
            elif x == 'discrete_uniform':
                pres = trial.suggest_discrete_uniform(t, p['init'], p['range'][0], p['range'][1])
            elif x == 'uniform':
                pres = trial.suggest_uniform(t, p['range'][0], p['range'][1])
            else:
                raise Exception(f'Not supported type {x}')
                pres = None

            model_pars[t] = pres

        module = model_create(module, model_pars, data_pars, compute_pars)  # module.Model(**param_dict)
        if VERBOSE: log(model)

        module.fit(data_pars=data_pars, compute_pars=compute_pars, out_pars=out_pars)
        metrics = module.evaluate(data_pars=data_pars, compute_pars=compute_pars, out_pars=out_pars)
        mtarget = metrics[metric_target]
        try:
            module.reset_model()  # Reset Graph for TF
        except Exception as e:
            log(e)

        return mtarget


    log("###### Hyper-optimization through study   ##################################")
    pruner = optuna.pruners.MedianPruner() if engine_pars["method"] == 'prune' else None

    if engine_pars.get("distributed") is not None:
        # study = optuna.load_study(study_name='distributed-example', storage='sqlite:///example.db')
        try:
            study = optuna.load_study(study_name=engine_pars['study_name'], storage=engine_pars['storage'])
        except:
            study = optuna.create_study(study_name=engine_pars['study_name'], storage=engine_pars['storage'],
                                        pruner=pruner)
    else:
        study = optuna.create_study(pruner=pruner)

    study.optimize(objective, n_trials=ntrials)  # Invoke optimization of the objective function.
    log("Optim, finished", n=35)
    param_dict_best = study.best_params
    # param_dict.update(module.config_get_pars(choice="test", )


    log("### Save Stats   ##########################################################")          
    study_trials = study.trials_dataframe()  
    study_trials.to_csv(f"{save_path}/{model_uri}_study.csv")
    param_dict_best["best_value"] = study.best_value
    json.dump(param_dict_best, open(f"{save_path}/{model_uri}_best-params.json", mode="w"))


    log("### Run Model with best   #################################################")
    model_pars_update = copy.deepcopy(model_pars)
    model_pars_update.update(param_dict_best)
    model_pars_update["model_name"] = model_name  ###SKLearn model

    module = model_create(module, model_pars_update, data_pars, compute_pars)
    module.fit(data_pars=data_pars, compute_pars=compute_pars, out_pars=out_pars)


    log("#### Saving     ###########################################################")
    model_uri = model_uri.replace(".", "-")
    save_pars = {'path': save_path, 'model_type': model_uri.split("-")[0], 'model_uri': model_uri}
    module.save(save_pars=save_pars)

    #log( os.stats(save_path))
    ## model_pars_update["model_name"] = model_name
    return model_pars_update



def post_process_best(model, module, model_uri, model_pars_update, data_pars, compute_pars, out_pars):
    """function post_process_best
    Args:
        model:   
        module:   
        model_uri:   
        model_pars_update:   
        data_pars:   
        compute_pars:   
        out_pars:   
    Returns:
        
    """
    log("### Run Model with best   #################################################")
    model = model_create(module, model_pars_update, data_pars, compute_pars)
    model, sess = module.fit(model, data_pars=data_pars, compute_pars=compute_pars, out_pars=out_pars)

    log("#### Saving     ###########################################################")
    model_uri = model_uri.replace(".", "-")
    save_path = out_pars['save_path']
    save_pars = {'path': save_path , 'model_type': model_uri.split("-")[0], 'model_uri': model_uri}
    module.save(model=model, session=sess, save_pars=save_pars)

    return model_pars_update

####################################################################################################
def test_json(path_json="", config_mode="test"):
    """function test_json
    Args:
        path_json:   
        config_mode:   
    Returns:
        
    """
    cf = json.load(open( path_norm(path_json), mode='r', encoding='utf-8'))
    cf = cf[config_mode]

    model_uri = cf['model_pars']['model_uri']  # 'model_tf.1_lstm'
    data_pars = path_norm_dict( cf['data_pars'] )
    out_pars  = path_norm_dict( cf['out_pars'] )

    res = optim(model_uri,
                hypermodel_pars = cf['hypermodel_pars'],
                model_pars      = cf['model_pars'],
                data_pars       = data_pars,
                compute_pars    = cf['compute_pars'],
                out_pars        = out_pars
                )
    return res



def test_all():
    """function test_all
    Args:
    Returns:
        
    """
    return 1



def optim_cli(arg):
    """function optim_cli
    Args:
        arg:   
    Returns:
        
    """
    # model_pars, data_pars, compute_pars = config_get_pars(arg)
    config_file = "template/optim_config.json" if arg.config_file is None else arg.config_file
    config_file =  path_norm( config_file )

    js = json.load(open(config_file, mode='r'))  # Config
    js = js[arg.config_mode]  # test /uat /prod
    data_pars = path_norm_dict( js['data_pars'] )
    out_pars  = path_norm_dict( js['out_pars'] )


    # log(model_pars, data_pars, compute_pars)
    log("############# OPTIMIZATION Start  ###############")
    res = optim(js["model_pars"]["model_uri"],
                hypermodel_pars = js["hypermodel_pars"],
                model_pars      = js["model_pars"],
                compute_pars    = js["compute_pars"],
                data_pars       = data_pars,
                out_pars        = out_pars )

    log("#############  OPTIMIZATION End ###############")
    log(res)


####################################################################################################
####################################################################################################
def cli():
    """
    add("--log_file", help="File to save the logging")
    add("--model_uri", default="model_tf.1_lstm.py",
        help="name of the model to be tuned this name will be used to save the model")
    add("--data_path", default="dataset/GOOG-year_small.csv", help="path of the training file")
    add('--optim_engine', default='optuna', help='Optimization engine')
    add('--optim_method', default='normal/prune', help='Optimization method')
    add('--save_path', default='ztest/search_save/', help='folder that will contain saved version of best model')
    """
    cli = argparse.ArgumentParser()
    subparsers = cli.add_subparsers(dest="subcommand")

    def argument(*names_or_flags, **kwargs):
        return names_or_flags, kwargs
    
    def subcommand(*subparser_args, parent=subparsers):
        def decorator(func):
            parser = parent.add_parser(func.__name__, description=func.__doc__)
            for args, kwargs in subparser_args:
                parser.add_argument(*args, **kwargs)
            parser.set_defaults(func=func)
        return decorator
    
    
    #########  Test  #########################################################
    @subcommand(
        argument("-ntrials", help="No. of trials", default=2),
        argument("model_uri", help="Model Name", default='model_tf.1_lstm')
    )
    def test(args):
        test_json( path_json="template/optim_config_prune.json", config_mode= args.config_mode )
        #    test_fast(ntrials=args.ntrials, model_uri=args.model_uri)
    


    @subcommand()
    def test_all(args):
        test_all()
    


    @subcommand(
        argument("--config_file", help="Path to config file", default=None),
        argument("--config_mode", help="test/ prod /uat", default="test")
    )
    def search(args):
        if args.config_file is None:
            args.config_file = path_norm("template/optim_config.json")
        js = json.load(open(args.config_file, mode='rb'))  # Config
        js = js[args.config_mode]  # test /uat /prod

        # log(model_pars, data_pars, compute_pars)
        log("############# OPTIMIZATION Start  ###############")
        res = optim(js["model_pars"]["model_uri"],
                    hypermodel_pars = js["hypermodel_pars"],
                    model_pars      = js["model_pars"],
                    compute_pars    = js["compute_pars"],
                    data_pars       = js["data_pars"],
                    out_pars        = js["out_pars"])

        log("#############  OPTIMIZATION End ###############")
        log(res)


"""
def main():
    cli()
"""


####################################################################################################
####################################################################################################
def cli_load_arguments(config_file=None):
    """
        Load CLI input, load config.toml , overwrite config.toml by CLI Input
    """
    p = argparse.ArgumentParser()
    def add(*k, **kw):
        p.add_argument(*k, **kw)

    add("--config_file" , default=None                     , help="Params File")
    add("--config_mode" , default="test"                   , help="test/ prod /uat")
    add("--log_file"    , help="File to save the logging")

    add("--do"          , default="test"                   , help="what to do test or search")

    ###### model_pars
    add("--model_uri", default="model_tf.1_lstm.py", help="name of the model for --do test")

    ###### data_pars
    # add("--data_path", default="dataset/GOOG-year_small.csv", help="path of the training file")


    ###### compute params
    add("--ntrials", default=1, help='number of trials during the hyperparameters tuning')
    # add('--optim_engine', default='optuna', help='Optimization engine')
    # add('--optim_method', default='normal/prune', help='Optimization method')


    ###### out params
    # add('--save_path', default='ztest/search_save/', help='folder that will contain saved version of best model')

    args = p.parse_args()
    # args = load_config(args, args.config_file, args.config_mode, verbose=0)
    return args



####################################################################################################
def main():
    arg = cli_load_arguments()

    if arg.do == "test":
        #test_fast(ntrials= arg.ntrials, model_uri= arg.model_uri)
        test_json( path_json="template/optim_config_prune.json", config_mode= arg.config_mode )

    if arg.do == "test_all":
        test_all()

    if arg.do == "search":
       optim_cli(arg)


####################################################################################################
if __name__ == "__main__":
    VERBOSE = True
    main()








"""
def test_fast(ntrials, model_uri):
    # path_curr = os.getcwd()
    data_path = path_norm('dataset/timeseries/GOOG-year_small.csv')
    log(data_path)

    #path_save = f"{path_curr}/ztest/optuna_1lstm/"
    #os.makedirs(path_save, exist_ok=True)
    # log("path_save", path_save, data_path)

    hypermodel_pars = {
        "engine_pars": {"engine": "optuna", "method": "normal", 'ntrials': 2, "metric_target": "loss"},

        "learning_rate": {"type": "log_uniform", "init": 0.01, "range": [0.001, 0.1]},
        "num_layers": {"type": "int", "init": 2, "range": [2, 4]},
        "size": {"type": "int", "init": 6, "range": [6, 6]},
        "output_size": {"type": "int", "init": 6, "range": [6, 6]},

        "size_layer": {"type": "categorical", "value": [128, 256]},
        "timestep": {"type": "categorical", "value": [5]},
        "epoch": {"type": "categorical", "value": [2]}
    }
    log("model details", model_uri, hypermodel_pars)

    model_pars   = {"model_uri": "model_tf.1_lstm",
                  "learning_rate": 0.001, "num_layers": 1, "size": None,
                  "size_layer": 128, "output_size": None, "timestep": 4, "epoch": 2, }

    data_pars    = {"data_path": data_path, "data_type": "pandas"}
    compute_pars = {}
    out_pars     = {"path": "ztest/optuna_1lstm/", "log_path": "ztest/optuna_1lstm/"}

    res = optim(model_uri,
                hypermodel_pars=hypermodel_pars,
                model_pars=model_pars,
                data_pars=data_pars,
                compute_pars=compute_pars,
                out_pars=out_pars
                )

    log("Finished OPTIMIZATION", n=30)
    log(res)
"""


