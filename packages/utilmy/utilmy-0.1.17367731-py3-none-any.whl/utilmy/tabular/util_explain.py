# -*- coding: utf-8 -*-
MNAME = "utilmy.tabular.util_explain"
""" utils for model explanation
"""
import os, numpy as np, glob, pandas as pd, matplotlib.pyplot as plt
from box import Box


from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor, plot_tree, DecisionTreeClassifier
from sklearn import metrics


from imodels import SLIMRegressor, BayesianRuleListClassifier, RuleFitRegressor, GreedyRuleListClassifier
from imodels import SLIMClassifier, OneRClassifier, BoostedRulesClassifier
from imodels.util.convert import tree_to_code

#### Types


#############################################################################################
from utilmy import log, log2
from imodels.algebraic.slim import SLIMRegressor
from imodels.rule_set.rule_fit import RuleFitRegressor
from imodels.tree.figs import FIGSRegressor
from numpy import ndarray
from typing import List, Optional, Tuple, Union

def help():
    """function help
    Args:
    Returns:
        
    """
    from utilmy import help_create
    print( help_create(MNAME) )



#############################################################################################
def test_all() -> None:
    """function test_all
    Args:
    Returns:
        
    """
    log(MNAME)
    test1()
    test2()


def test1() -> None:
    """  imodels.FIGSRegressor
      Doc::

          HSTreeRegressorCV reg_param_list: List[float] = [0.1, 1, 10, 50, 100, 500], shrinkage_scheme_: str = 'node_based', cv: int = 3, scoring=None, *args, **kwargs)
          imodels.SLIMRegressor, RuleFitRegressor,
          GreedyRuleListClassifier,  BayesianRuleListClassifier,
          imodels.SLIMClassifier, OneRClassifier, BoostedRulesClassifier
    """
    d = Box({})
    d.X_train, d.X_test, d.y_train, d.y_test, d.feat_names = test_data_regression_boston()
    d.task_type = 'regressor'



    mlist = [ ('imodels.FIGSRegressor',      {'max_rules':10},  ), 
              # ('imodels.HSTreeRegressorCV',  { 'estimator' : None, 'reg_param_list':[0.1, 1, 10, 50, 100, 500],   'cv':3 , 'scoring': None},  ), 

              ('imodels.RuleFitRegressor',   {'max_rules':10},  ), 
              ('imodels.SLIMRegressor',      {'alpha': 0.01},  ) ## no Rules
                         
    ]

    for m in mlist :
        log(m[0])
        d.task_type = 'regressor' if 'Regressor' in m[0] else 'classifier'
        model = model_fit(name       = m[0] , 
                          model_pars = m[1], 
                          data_pars=d, do_eval=True )
        model_save(model, 'mymodel/')


        # reLoad model and check
        model2 = model_load('mymodel/')
        model_extract_rules(model2)



def test2() -> None:
    """  imodels.FIGSRegressor
      Doc::

          HSTreeRegressorCV reg_param_list: List[float] = [0.1, 1, 10, 50, 100, 500], shrinkage_scheme_: str = 'node_based', cv: int = 3, scoring=None, *args, **kwargs)
          imodels.SLIMRegressor, RuleFitRegressor,
          GreedyRuleListClassifier,  BayesianRuleListClassifier,
          imodels.SLIMClassifier, OneRClassifier, BoostedRulesClassifier
    """
    d = Box({})
    d.X_train, d.X_test, d.y_train, d.y_test, d.feat_names = test_data_classifier_diabetes()
    d.task_type = 'classifier'



    mlist = [ # ('imodels.FIGSClassifier',      {'max_rules':10},  ), 
              # ('imodels.HSTreeClassifierCV',  {'estimator': None, 'reg_param_list':[0.1, 1, 10, 50, 100, 500],   'cv':3 , 'scoring': None},  ), 
             
              #('imodels.RuleFitClassifier',   {'max_rules':10},  ), 
                         
    ]

    for m in mlist :
        log(m[0])
        d.task_type = 'regressor' if 'Regressor' in m[0] else 'classifier'
        model = model_fit(name       = m[0] , 
                          model_pars = m[1], 
                          data_pars=d, do_eval=True )
        model_save(model, 'mymodel/')


        # reLoad model and check
        model2 = model_load('mymodel/')
        model_extract_rules(model2)



def test_imodels():   
    """Copy of imodels_demo.ipynb
    Doc::

            https://colab.research.google.com/drive/18Y5odtkZ1dI9kAs1KMK8Z7u-DKspbP9p
    """

    #!pip install --upgrade mlxtend
    #!pip install imodels
    #!git clone https://github.com/csinva/imodels # clone the repo which has some of the data
    # note after these installs, need to click "Restart runtime"

    import os

    import matplotlib.pyplot as plt
    import numpy as np
    np.random.seed(13)
    from sklearn.datasets import load_boston
    from sklearn.model_selection import train_test_split
    from sklearn.tree import DecisionTreeRegressor, plot_tree, DecisionTreeClassifier
    from sklearn import metrics
    from scipy.io.arff import loadarff

    # installable with: `pip install imodels`
    from imodels import SLIMRegressor, BayesianRuleListClassifier, RuleFitRegressor, GreedyRuleListClassifier
    from imodels import SLIMClassifier, OneRClassifier, BoostedRulesClassifier
    from imodels.util.convert import tree_to_code

    # change working directory to project root
    if os.getcwd().split('/')[-1] != 'imodels':
        os.chdir('..')


    X_train_reg, X_test_reg, y_train_reg, y_test_reg, feat_names_reg = test_data_regression_boston()
    X_train, X_test, y_train, y_test, feat_names = test_data_classifier_diabetes()


    def viz_classification_preds(probs, y_test):
        '''look at prediction breakdown
        '''
        plt.subplot(121)
        plt.hist(probs[:, 1][y_test==0], label='Class 0')
        plt.hist(probs[:, 1][y_test==1], label='Class 1', alpha=0.8)
        plt.ylabel('Count')
        plt.xlabel('Predicted probability of class 1')
        plt.legend()
        
        plt.subplot(122)
        preds = np.argmax(probs, axis=1)
        plt.title('ROC curve')
        fpr, tpr, thresholds = metrics.roc_curve(y_test, preds)
        plt.xlabel('False positive rate')
        plt.ylabel('True positive rate')
        plt.plot(fpr, tpr)
        plt.tight_layout()
        plt.show()

    # load some data
    print('regression data', X_train_reg.shape, 'classification data', X_train.shape)

    """# rule sets
    Rule sets are models that create a set of (potentially overlapping) rules.
    ### rulefit
    """

    # fit a rulefit model
    rulefit = RuleFitRegressor(max_rules=10)
    rulefit.fit(X_train_reg, y_train_reg, feature_names=feat_names_reg)

    # get test performance
    preds = rulefit.predict(X_test_reg)
    print(f'test r2: {metrics.r2_score(y_test_reg, preds):0.2f}')


    # inspect and print the rules
    rules = rulefit.get_rules()
    rules = rules[rules.coef != 0].sort_values("support", ascending=False)

    # 'rule' is how the feature is constructed
    # 'coef' is its weight in the final linear model
    # 'support' is the fraction of points it applies to
    rules[['rule', 'coef', 'support']].style.background_gradient(cmap='viridis')

    """## boosted stumps"""

    # fit boosted stumps
    brc = BoostedRulesClassifier(n_estimators=10)
    brc.fit(X_train, y_train, feature_names=feat_names)

    print(brc)

    # look at performance
    probs = brc.predict_proba(X_test)
    viz_classification_preds(probs, y_test)

    """# rule lists
    ### greedy rule lists
    **like a decision tree that only ever splits going left**
    """

    # fit a greedy rule list
    m = GreedyRuleListClassifier()
    m.fit(X_train, y=y_train, feature_names=feat_names) # stores into m.rules_
    probs = m.predict_proba(X_test)

    # print the list
    print(m)

    # look at prediction breakdown
    viz_classification_preds(probs, y_test)

    """### oneR
    **fits a rule list restricted to use only one feature**
    """

    # fit a oneR model
    m = OneRClassifier()
    m.fit(X_train, y=y_train, feature_names=feat_names) # stores into m.rules_
    probs = m.predict_proba(X_test)

    # print the rule list
    print(m)

    # look at prediction breakdown
    viz_classification_preds(probs, y_test)

    """### scalable bayesian rule lists"""

    # train classifier (allow more iterations for better accuracy; use BigDataRuleListClassifier for large datasets)
    print('training...')
    m = BayesianRuleListClassifier(max_iter=3000, class1label="diabetes", verbose=False)
    m.fit(X_train, y_train)
    probs = m.predict_proba(X_test)
    print("learned model:\n", m)
    viz_classification_preds(probs, y_test)

    """# rule trees
    ### short decision tree
    """

    # specify a decision tree with a maximum depth
    dt = DecisionTreeClassifier(max_depth=3)
    dt.fit(X_train, y_train)

    # calculate mse on the training data
    probs = dt.predict_proba(X_test)
    # print(f'test mse: {np.mean(np.square(preds-y)):0.2f}')

    plot_tree(dt)
    # plt.savefig('tree.pdf')
    plt.show()

    viz_classification_preds(probs, y_test)

    """### optimal classification tree
    - docs [here](https://github.com/csinva/interpretability-workshop/tree/master/imodels/optimal_classification_tree)
    - note: this implementation is still somewhat unstable, and can be made faster by installing either `cplex` or `gurobi`
    """

    # sys.path.append('../imodels/optimal_classification_tree/pyoptree')
    # sys.path.append('../imodels/optimal_classification_tree/')

    # from optree import OptimalTreeModel
    # feature_names = np.array(["x1", "x2"])

    # X = np.array([[1, 2, 2, 2, 3], [1, 2, 1, 0, 1]]).T
    # y = np.array([1, 1, 0, 0, 0]).reshape(-1, 1)
    # X_test = np.array([[1, 1, 2, 2, 2, 3, 3], [1, 2, 2, 1, 0, 1, 0]]).T
    # y_test = np.array([1, 1, 1, 0, 0, 0, 0])

    # np.random.seed(13)
    # model = OptimalTreeModel(tree_depth=3, N_min=1, alpha=0.1) #, solver_name='baron'
    # model.fit(X_test, y_test) # this method is currently using the fast, but not optimal solver
    # preds = model.predict(X_test)

    # # fit on the bigger diabetes dset from above
    # # model.fit(Xtrain, ytrain) # this method is currently using the fast, but not optimal solver
    # # preds = model.predict(Xtest)

    # print('acc', np.mean(preds == y_test))

    # model.print_tree(feature_names)

    """# algebraic models
    ### integer linear models
    """

    np.random.seed(123)

    # generate X and y
    n, p = 500, 10
    X_sim = np.random.randn(n, p)
    y_sim = 1 * X_sim[:, 0] + 2 * X_sim[:, 1] - 1 * X_sim[:, 2] + np.random.randn(n)

    # fit linear models with different regularization parameters
    print('groundtruth weights should be 1, 2, -1...')
    model = SLIMRegressor()
    for lambda_reg in [1e-3, 1e-2, 5e-2, 1e-1, 1, 2, 5, 10]:
        model.fit(X_sim, y_sim, lambda_reg)
        mse = np.mean(np.square(y_sim - model.predict(X_sim)))
        print(f'lambda: {lambda_reg}\tmse: {mse: 0.2f}\tweights: {model.model_.coef_}')

    y_sim = 1 / (1 + np.exp(-y_sim))
    y_sim = np.round(y_sim)

    # fit linear models with different regularization parameters
    print('groundtruth weights should be 1, 2, -1...')
    model = SLIMClassifier()
    for lambda_reg in [1e-3, 1e-2, 5e-2, 1e-1, 1, 2, 5, 10]:
        model.fit(X_sim, y_sim, lambda_reg)
        mll = np.mean(metrics.log_loss(y_sim, model.predict(X_sim)))
        print(f'lambda: {lambda_reg}\tmlogloss: {mll: 0.2f}\tweights: {model.model_.coef_}')

#############################################################################################


"""

https://modal-python.readthedocs.io/en/latest/content/examples/Pytorch_integration.html

"""

#############################################################################################
#######iguana Rule generator ################################################################

def generate_rules_fromdata():
    """"  Helper for Rule Generators.
    Doc::

        from iguanas.rule_generation import RuleGeneratorDT
        from iguanas.rule_optimisation import BayesianOptimiser
        from iguanas.metrics.classification import FScore, Precision
        from iguanas.metrics.pairwise import JaccardSimilarity
        from iguanas.rules import Rules, ConvertProcessedConditionsToGeneral, ReturnMappings
        from iguanas.correlation_reduction import AgglomerativeClusteringReducer
        from iguanas.rule_selection import SimpleFilter, GreedyFilter, CorrelatedFilter
        from iguanas.rbs import RBSPipeline, RBSOptimiser

        import pandas as pd
        import numpy as np
        from sklearn.model_selection import train_test_split
        from category_encoders.one_hot import OneHotEncoder
        from sklearn.ensemble import RandomForestClassifier
        import pickle
        from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, classification_report
        import seaborn as sns

        RuleGeneratorDT: Generate rules by extracting the highest performing branches from a tree ensemble model.

        RuleGeneratorOpt: Generate rules by optimising the thresholds of single features and combining these one condition rules with AND conditions to create more complex rules.

            params = {
            'metric': f1.fit,
            'n_total_conditions': 4,
            'tree_ensemble': RandomForestClassifier(n_estimators=10, random_state=0),
            'target_feat_corr_types': 'Infer',
            'num_cores': 4,
            'verbose': 1
        }

     https://paypal.github.io/Iguanas/examples/complete/rbs_example.html
    """
    ss=""
    print(ss)






#############################################################################################
def model_fit(name:str='imodels.SLIMRegressor', model_pars:dict=None, data_pars:dict=None, do_eval: bool=True, **kw
) -> Union[RuleFitRegressor, FIGSRegressor, SLIMRegressor]:
    """ Fit Imodel.
    Doc::

      imodels.SLIMRegressor, BayesianRuleListClassifier, RuleFitRegressor, GreedyRuleListClassifier
      imodels.SLIMClassifier, OneRClassifier, BoostedRulesClassifier
    """
    from imodels.util.convert import tree_to_code
    from sklearn import metrics

    from utilmy.utils import load_function_uri
    d = Box(data_pars) if data_pars is not None else Box({})

    log("#### model load")    
    name = name.replace(".", ":")
    Model0 = load_function_uri(name)
    model  = Model0(**model_pars)

    log("#### model fit")    ###  brc = BoostedRulesClassifier(n_estimators=10)
    try :
       model.fit(d.X_train, d.y_train, feature_names=d.feat_names)
    except :
       model.fit(d.X_train, d.y_train, )
    log(model)

    ### d.get('task_type', 'classifier')
    if do_eval :
      model_evaluate(model, data_pars)

    return model


def model_evaluate(model: Union[RuleFitRegressor, FIGSRegressor, SLIMRegressor], data_pars:dict) -> None:
    """ Evaluate model
    """
    d = Box(data_pars) if data_pars is not None else Box({})
    task_type = d.get('task_type', 'classifier')
    if task_type == 'classifier' :
      probs = model.predict_proba(d.X_test)
      log(probs)
      model_viz_classification_preds(probs, d.y_test)
    else :
      # get test performance
      preds = model.predict(d.X_test)
      print(f'test r2: {metrics.r2_score(d.y_test, preds):0.2f}')


def model_predict(model, predict_pars:dict):
    """function model_predict
    Args:
        model:   
        predict_pars ( dict ) :   
    Returns:
        
    """
    pass


def model_save(model: Union[RuleFitRegressor, FIGSRegressor, SLIMRegressor], path: Optional[str]=None, info: None=None) -> None:
    """function model_save
    Args:
        model (  Union[RuleFitRegressor ) :   
        FIGSRegressor:   
        SLIMRegressor]:   
        path (  Optional[str] ) :   
        info (  None ) :   
    Returns:
        
    """
    import cloudpickle as pickle
    os.makedirs(path, exist_ok=True)
    filename = "model.pkl"
    pickle.dump(model, open(f"{path}/{filename}", mode='wb'))  # , protocol=pickle.HIGHEST_PROTOCOL )

    filename = "info.pkl"
    info = {} if info is None else info
    pickle.dump(info, open(f"{path}/{filename}", mode='wb'))   # ,protocol=pickle.HIGHEST_PROTOCOL )


def model_load(path: str="") -> Union[RuleFitRegressor, FIGSRegressor, SLIMRegressor]:
    """function model_load
    Args:
        path (  str ) :   
    Returns:
        
    """
    import cloudpickle as pickle
    model0 = pickle.load(open(f"{path}/model.pkl", mode='rb'))
    return model0


def model_info(path=""):
    """function model_info
    Args:
        path:   
    Returns:
        
    """
    import cloudpickle as pickle
    model0 = pickle.load(open(f"{path}/info.pkl", mode='rb'))
    return model0


def model_viz_classification_preds(probs:np.ndarray, y_test:list):
    '''look at prediction breakdown
    '''
    try :
        plt.subplot(121)
        plt.hist(probs[:, 1][y_test==0], label='Class 0')
        plt.hist(probs[:, 1][y_test==1], label='Class 1', alpha=0.8)
        plt.ylabel('Count')
        plt.xlabel('Predicted probability of class 1')
        plt.legend()
        
        plt.subplot(122)
        preds = np.argmax(probs, axis=1)
        plt.title('ROC curve')
        fpr, tpr, thresholds = metrics.roc_curve(y_test, preds)
        plt.xlabel('False positive rate')
        plt.ylabel('True positive rate')
        plt.plot(fpr, tpr)
        plt.tight_layout()
        plt.show()
    except Exception as e :
        log(e)


def model_extract_rules(model: Union[RuleFitRegressor, FIGSRegressor, SLIMRegressor]) -> None:
    """ From imodel extract rules
       # 'rule' is how the feature is constructed
       # 'coef' is its weight in the final linear model
       # 'support' is the fraction of points it applies to
    """ 
    try :
      rules =  model.get_rules()

      # inspect and print the rules
      rules = rules[rules.coef != 0].sort_values("support", ascending=False)

      display(rules[['rule', 'coef', 'support']].style.background_gradient(cmap='viridis'))
    except :
      print('No rules available')




#############################################################################################
def test_data_regression_boston() -> Tuple[ndarray, ndarray, ndarray, ndarray, ndarray]:
    '''load (regression) data on boston housing prices
    '''
    from sklearn.datasets import load_boston
    X_reg, y_reg = load_boston(return_X_y=True)
    feature_names = load_boston()['feature_names']
    X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(X_reg, y_reg, test_size=0.75) # split
    return X_train_reg, X_test_reg, y_train_reg, y_test_reg, feature_names


def test_data_classifier_diabetes() -> Tuple[ndarray, ndarray, ndarray, ndarray, List[str]]:
    '''load (classification) data on diabetes
    '''
    from sklearn.datasets import load_diabetes
    from sklearn.model_selection import train_test_split
    diabetes = load_diabetes()
    X, y     = diabetes.data, diabetes.target
    feature_names = load_diabetes()['feature_names']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.75) # split
    return X_train, X_test, y_train, y_test, feature_names
    

def load_function_uri(uri_name="path_norm"):
    """ Load dynamically function from URI
    Doc::

        ###### Pandas CSV case : Custom MLMODELS One
        #"dataset"        : "mlmodels.preprocess.generic:pandasDataset"
        ###### External File processor :
        #"dataset"        : "MyFolder/preprocess/myfile.py:pandasDataset"
    """
    import importlib, sys
    from pathlib import Path
    pkg = uri_name.split(":")

    assert len(pkg) > 1, "  Missing :   in  uri_name module_name:function_or_class "
    package, name = pkg[0], pkg[1]
    
    try:
        #### Import from package mlmodels sub-folder
        return  getattr(importlib.import_module(package), name)

    except Exception as e1:
        try:
            ### Add Folder to Path and Load absoluate path module
            path_parent = str(Path(package).parent.parent.absolute())
            sys.path.append(path_parent)
            #log(path_parent)

            #### import Absolute Path model_tf.1_lstm
            model_name   = Path(package).stem  # remove .py
            package_name = str(Path(package).parts[-2]) + "." + str(model_name)
            #log(package_name, model_name)
            return  getattr(importlib.import_module(package_name), name)

        except Exception as e2:
            raise NameError(f"Module {pkg} notfound, {e1}, {e2}")






###################################################################################################
if __name__ == "__main__":
    import fire

    fire.Fire()


