
from __future__ import print_function

import argparse
import glob
import os
import re
from importlib import import_module

import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torch.utils.data.distributed

from torchvision import datasets, transforms


def model_create(modelname="", params=None, modelonly=1):
    """.
    Doc::
            
              modelname:  model_tch.mlp.py
              model_tch/****
              
    """
    modelname = modelname.replace(".py", "")
    print(modelname)
    try :
      module = import_module("{a}".format(a=modelname))
    except Exception as e :
      raise NameError("Module {} notfound, {}".format(modelname, e))    

    model = module.Model(**params)
    return  model


def model_instance(name="net", params={}):
    """function model_instance.
    Doc::
            
            Args:
                name:   
                params:   
            Returns:
                
    """
    if name == "net":
        return Net()
    else  :
        return model_create(name, params)
         




####################################################################################################
class Net(nn.Module):
    def __init__(self):
        """ Net:__init__.
        Doc::
                
                    Args:
                    Returns:
                       
        """
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 10, kernel_size=5)
        self.conv2 = nn.Conv2d(10, 20, kernel_size=5)
        self.conv2_drop = nn.Dropout2d()
        self.fc1 = nn.Linear(320, 50)
        self.fc2 = nn.Linear(50, 10)

    def forward(self, x):
        """ Net:forward.
        Doc::
                
                    Args:
                        x:     
                    Returns:
                       
        """
        x = F.relu(F.max_pool2d(self.conv1(x), 2))
        x = F.relu(F.max_pool2d(self.conv2_drop(self.conv2(x)), 2))
        x = x.view(-1, 320)
        x = F.relu(self.fc1(x))
        x = F.dropout(x, training=self.training)
        x = self.fc2(x)
        return F.log_softmax(x)





# model = Net()
