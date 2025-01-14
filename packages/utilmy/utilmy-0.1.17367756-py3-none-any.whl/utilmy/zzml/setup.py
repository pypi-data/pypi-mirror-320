# pylint: disable=C0321,C0103,C0301,E1305,E1121,C0302,C0330,C0111,W0613,W0611,R1705
# -*- coding: utf-8 -*-
"""


"""
import io
import os
import subprocess
import sys

from setuptools import find_packages, setup




######################################################################################
root = os.path.abspath(os.path.dirname(__file__))


##### check if GPU available  #########################################################
"""
try :
  p = subprocess.Popen(["command -v nvidia-smi"], stdout=subprocess.PIPE, shell=True)
  out = p.communicate()[0].decode("utf8")
  gpu_available = len(out) > 0
except : pass
"""

##### Version  #######################################################################
version ='0.35.2'
cmdclass= None



#### Issues When Building on Colab
#import versioneer
#version = versioneer.get_version()
#cmdclass=versioneer.get_cmdclass()

print("version", version)





######################################################################################
with open('install/requirements.txt') as fp:
    install_requires = fp.read()



######################################################################################
#with open("README.md", "r") as fh:
#    long_description = fh.read()


long_description =  """

```


This repository is the ***Model ZOO for Pytorch, Tensorflow, Keras, Gluon, LightGBM, Keras, Sklearn models etc*** with Lightweight Functional interface to wrap access to Recent and State of Art Deep Learning, ML models and Hyper-Parameter Search, cross platforms that follows the logic of sklearn, such as fit, predict, transform, metrics, save, load etc. 
Now, more than **60 recent models** (> 2018) are available in those domains : 
* Time Series, 
* Text classification, 
* Vision, 
* Image Generation,Text generation, 
* Gradient Boosting, Automatic Machine Learning tuning, 
* Hyper-parameter search.

With the goal to transform Script/Research code into re-usable batch/code with minimal code change, we used functional interface instead of pure OOP. This is because functional reduces the amount of code needed which is good to scientific computing. Thus, we can focus on the computing part than design. Also, it is easy to maintain for medium size project. 




##### Include models :

https://github.com/arita37/mlmodels/blob/dev/README.md



```
"""




"""

import os

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


from pathlib import Path
import inspect
root_path = Path("mlmodels/")
extra_files = package_files( root_path )

print(root_path)


print( __pkgname__ )


"""


### Packages  ########################################################
packages = ["mlmodels"] + ["mlmodels." + p for p in find_packages("mlmodels")]

print(packages)

### CLI Scripts  ####################################################
"""
scripts = [ "mlmodels/models.py",
            "mlmodels/optim.py",
            "mlmodels/",     
            ]


"""
scripts = [ "mlmodels/distri_torch_mpirun.sh",     
            ]



### CLI Scripts  ###################################################   
entry_points={ 'console_scripts': [
                'ml_models      = mlmodels.models:main'
               ,'ml_optim       = mlmodels.optim:main'
               ,'ml_test        = mlmodels.ztest:main'
               ,'ml_benchmark   = mlmodels.benchmark:main'
               ,'ml_distributed = mlmodels.distributed:main'   ### Not functionnal
              ] }






##################################################################   
setup(
    name="mlmodels",
    description="Generic model API, Model Zoo in Tensorflow, Keras, Pytorch, Gluon and Hyperparamter search",
    keywords='Machine Learning Interface library',
    
    author="Kevin Noel, MLMODELS Team",
    author_email="brookm291@gmail.com",
    url="https://github.com/arita37/mlmodels",
    
    install_requires=install_requires,
    python_requires='>=3.6.5',
    
    packages=packages,

    include_package_data=True,
    #    package_data= {'': extra_files},

    package_data={
       '': ['*','*/*','*/*/*','*/*/*/*']
    },

   
    ### Versioning
    version=version,
    #cmdclass=cmdclass,


    #### CLI
    scripts = scripts,
  
    ### CLI pyton
    entry_points= entry_points,



    long_description=long_description,
    long_description_content_type="text/markdown",


    classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          'Topic :: Scientific/Engineering',
          'Topic :: Scientific/Engineering :: ' +
          'Artificial Intelligence',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: ' +
          'Python Modules',
          'Topic :: Scientific/Engineering :: Information Analysis',
          'Environment :: Console',
          'Environment :: Web Environment',
          'Operating System :: POSIX',
          'Operating System :: MacOS :: MacOS X',
      ]
)





################################################################################
################################################################################
"""


https://packaging.python.org/tutorials/packaging-projects/


import io
import os
import subprocess
import sys

from setuptools import setup, find_packages

root = os.path.abspath(os.path.dirname(__file__))


# required packages for NLP Architect
with open('install/requirements.txt') as fp:
    install_requirements = fp.readlines()

# check if GPU available
p = subprocess.Popen(['command -v nvidia-smi'], stdout=subprocess.PIPE, shell=True)
out = p.communicate()[0].decode('utf8')
gpu_available = len(out) > 0

# Tensorflow version (make sure CPU/MKL/GPU versions exist before changing)
for r in install_requirements:
    if r.startswith('tensorflow=='):
        tf_version = r.split('==')[1]

# default TF is CPU
chosen_tf = 'tensorflow=={}'.format(tf_version)
# check system is linux for MKL/GPU backends
if 'linux' in sys.platform:
    system_type = 'linux'
    tf_be = os.getenv('NLP_ARCHITECT_BE', False)
    if tf_be and 'mkl' == tf_be.lower():
        chosen_tf = 'intel-tensorflow=={}'.format(tf_version)
    elif tf_be and 'gpu' == tf_be.lower() and gpu_available:
        chosen_tf = 'tensorflow-gpu=={}'.format(tf_version)

for r in install_requirements:
    if r.startswith('tensorflow=='):
        install_requirements[install_requirements.index(r)] = chosen_tf

with open('README.md', encoding='utf8') as fp:
    long_desc = fp.read()

with io.open(os.path.join(root, 'nlp_architect', 'version.py'), encoding='utf8') as f:
    version_f = {}
    exec(f.read(), version_f)
    version = version_f['NLP_ARCHITECT_VERSION']

setup(name='nlp-architect',
      version=version,
      description='Intel AI Lab\'s open-source NLP and NLU research library',
      long_description=long_desc,
      long_description_content_type='text/markdown',
      keywords='NLP NLU deep learning natural language processing tensorflow keras dynet',
      author='Intel AI Lab',
      packages=find_packages(exclude=['tests.*', 'tests', '*.tests', '*.tests.*',
                                      'examples.*', 'examples', '*.examples', '*.examples.*']),
      install_requires=install_requirements,
      scripts=['nlp_architect/nlp_architect'],
      include_package_data=True,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          'Topic :: Scientific/Engineering',
          'Topic :: Scientific/Engineering :: ' +
          'Artificial Intelligence',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: ' +
          'Python Modules',
          'Topic :: Scientific/Engineering :: Information Analysis',
          'Environment :: Console',
          'Environment :: Web Environment',
          'Operating System :: POSIX',
          'Operating System :: MacOS :: MacOS X',
      ]
      )



import os
from io import open

from setuptools import find_packages, setup

packages = ['elfi'] + ['elfi.' + p for p in find_packages('elfi')]

# include C++ examples
package_data = {'elfi.examples': ['cpp/Makefile', 'cpp/*.txt', 'cpp/*.cpp']}

with open('install/requirements.txt', 'r') as f:
    requirements = f.read().splitlines()

optionals = {'doc': ['Sphinx'], 'graphviz': ['graphviz>=0.7.1']}

# read version number
__version__ = open('elfi/__init__.py').readlines()[-1].split(' ')[-1].strip().strip("'\"")

setup(
    name='elfi',
    keywords='abc likelihood-free statistics',
    packages=packages,
    package_data=package_data,
    version=__version__,
    author='ELFI authors',
    author_email='elfi-support@hiit.fi',
    url='http://elfi.readthedocs.io',
    install_requires=requirements,
    extras_require=optionals,
    description='ELFI - Engine for Likelihood-free Inference',
    long_description=(open('docs/description.rst').read()),
    license='BSD',
    classifiers=[
        'Programming Language :: Python :: 3.5', 'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Mathematics', 'Operating System :: OS Independent',
        'Development Status :: 4 - Beta', 'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License'
    ],
    zip_safe=False)



"""



