
import argparse
import time
from tests.sub_dir.subsub_dir.helper import  goodnight
import pandas

df = pandas.DataFrame([[3,4,5]*100, [5,2,1]*100])
df.apply(lambda x: x**3)
def sleep_one_seconds():
    """function sleep_one_seconds.
    Doc::
            
            Args:
            Returns:
                
    """
    time.sleep(1)

def sleep_two_seconds():
    """function sleep_two_seconds.
    Doc::
            
            Args:
            Returns:
                
    """
    time.sleep(2)

goodnight()

for i in range(10):
    foo()
bar()

def foo():
    """function foo.
    Doc::
            
            Args:
            Returns:
                
    """
    time.sleep(2)

foo()

parser = argparse.ArgumentParser(description='Testing.')
parser.add_argument('-w', action='store_true')
args = parser.parse_args()
print(args.w)