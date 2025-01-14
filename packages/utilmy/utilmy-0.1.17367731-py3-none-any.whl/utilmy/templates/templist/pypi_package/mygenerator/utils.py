# -*- coding: utf-8 -*-
import glob
import json
import os
import pathlib
import shutil
import sys
import tarfile
import zipfile
from typing import Optional, Union

import wget
import yaml
from loguru import logger


##########################################################################################
################### Logs Wrapper #########################################################
def log(*s):
    """function log.
    Doc::
            
            Args:
                *s:   
            Returns:
                
    """
    logger.info(",".join([str(t) for t in s]))


def log2(*s):
    """function log2.
    Doc::
            
            Args:
                *s:   
            Returns:
                
    """
    logger.debug(",".join([str(t) for t in s]))


def logw(*s):
    """function logw.
    Doc::
            
            Args:
                *s:   
            Returns:
                
    """
    logger.warning(",".join([str(t) for t in s]))


def loge(*s):
    """function loge.
    Doc::
            
            Args:
                *s:   
            Returns:
                
    """
    logger.error(",".join([str(t) for t in s]))


def logger_setup():
    """function logger_setup.
    Doc::
            
            Args:
            Returns:
                
    """
    config = {
        "handlers": [
            {
                "sink": sys.stdout,
                "format": "<level>{level: <8}</level>| <level>{message}</level>",
            }
        ]
    }
    logger.configure(**config)


logger_setup()


##########################################################################################
################### donwload  ############################################################
def config_load(config_path: Optional[Union[str, pathlib.Path]] = None):
    """Load Config file into a dict.
    Doc::
            
            1) load config_path
            2) If not, load in HOME USER
            3) If not, create default one
            Args:
                config_path: path of config or 'default' tag value
            Returns: dict config
    """
    path_default = pathlib.Path.home() / ".mygenerator"
    config_path_default = path_default / "config.yaml"

    if config_path is None or config_path == "default":
        logw(f"Using config: {config_path_default}")
        config_path = config_path_default

    try:
        log2("loading config", config_path)
        return yaml.load(config_path.read_text(), Loader=yaml.Loader)

    except Exception as e:
        logw(f"Cannot read yaml file {config_path}", e)

    logw("#### Using default configuration")
    config_default = {
        "current_dataset": "mnist",
        "datasets": {
            "mnist": {
                "url": "https://github.com/arita37/mnist_png/raw/master/mnist_png.tar.gz",
                "path": str(path_default / "mnist_png" / "training"),
            }
        },
    }
    log2(config_default)

    log(f"Creating config file in {config_path_default}")
    os.makedirs(path_default, exist_ok=True)
    with open(config_path_default, mode="w") as fp:
        yaml.dump(config_default, fp)
    return config_default


##########################################################################################
################### donwload  ############################################################
def dataset_donwload(url, path_target):
    """Donwload on disk the tar.gz file.
    Doc::
            
            Args:
                url:
                path_target:
            Returns:
        
    """
    log(f"Donwloading mnist dataset in {path_target}")
    os.makedirs(path_target, exist_ok=True)
    wget.download(url, path_target)
    tar_name = url.split("/")[-1]
    os_extract_archive(path_target + "/" + tar_name, path_target)
    log2(path_target)
    return path_target + tar_name


def dataset_get_path(cfg: dict):
    """function dataset_get_path.
    Doc::
            
            Args:
                cfg (  dict ) :   
            Returns:
                
    """
    #### Donaload dataset
    # cfg = config_load()
    name = cfg.get("current_dataset", "mnist")
    cfgd = cfg["datasets"].get(name, {})
    url = cfgd.get("url", None)
    path = cfgd.get("path", None)
    path_default = os.path.expanduser("~").replace("\\", "/") + f"/.mygenerator/dataset/{name}/"

    if path is None or path == "default":
        path_target = path_default
    else:
        path_target = path

    #### Customize by Dataset   #################################
    if name == "mnist":
        ### TODO hardcoded per dataset source
        path_data = path_target + "/mnist_png/training/"
        fcheck = glob.glob(path_data + "/*/*")
        log2("n_file: ", len(fcheck))
        if len(fcheck) < 1:
            dataset_donwload(url, path_target)

        return path_data

    else:
        raise Exception("No dataset available")


def os_extract_archive(file_path, path=".", archive_format="auto"):
    """Extracts an archive if it matches tar, tar.gz, tar.bz, or zip formats..
    Doc::
            
            Args:
                file_path: path to the archive file
                path: path to extract the archive file
                archive_format: Archive format to try for extracting the file.
                    Options are 'auto', 'tar', 'zip', and None.
                    'tar' includes tar, tar.gz, and tar.bz files.
                    The default 'auto' is ['tar', 'zip'].
                    None or an empty list will return no matches found.
            Returns:
                True if a match was found and an archive extraction was completed,
                False otherwise.
    """
    if archive_format is None:
        return False
    if archive_format == "auto":
        archive_format = ["tar", "zip"]
    if isinstance(archive_format, str):
        archive_format = [archive_format]

    file_path = os.path.abspath(file_path)
    path = os.path.abspath(path)

    for archive_type in archive_format:
        if archive_type == "tar":
            open_fn = tarfile.open
            is_match_fn = tarfile.is_tarfile
        if archive_type == "zip":
            open_fn = zipfile.ZipFile
            is_match_fn = zipfile.is_zipfile

        if is_match_fn(file_path):
            with open_fn(file_path) as archive:
                try:
                    archive.extractall(path)
                except (tarfile.TarError, RuntimeError, KeyboardInterrupt):
                    if os.path.exists(path):
                        if os.path.isfile(path):
                            os.remove(path)
                        else:
                            shutil.rmtree(path)
                    raise
            return True
    return False


def to_file(s, filep):
    """function to_file.
    Doc::
            
            Args:
                s:   
                filep:   
            Returns:
                
    """
    with open(filep, mode="a") as fp:
        fp.write(str(s) + "\n")
