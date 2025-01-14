#!/bin/bash

# Keeps Python from generating .pyc files in the container
export PYTHONDONTWRITEBYTECODE=1   

# Turns off buffering for easier container logging
export PYTHONUNBUFFERED=1          

#### Remove Assert and Docstring , remove creates some issue
# export PYTHONOPTIMIZE=2 


