
import fire 



def run(dirin, dirout, coly='y', nmax=100000):
   """ 
      python src/data/util_data.py run --dirin "ztmp/dftrain.parquet" --dirout "ztmp/ztmp/"
   
   """
   from utilmy import (pd_read_file, os_makedirs)
   
   nmax = 5*10**4
   name = dirin.split("/")[-1].split(".")[0].replace("*", '')
   os_makedirs(dirout)

   df = pd_read_file(dirin)
   df = df.sample(n=nmax)
   
   
   import sweetviz
   my_report = sweetviz.analyze(df, target_feat=coly,
        pairwise_analysis= 'off'                                
   )
   my_report.show_html( dirout + f'/report_sweetviz_{name}.html')


  #  from ydata_profiling import ProfileReport
  #  profile = ProfileReport(df, title="Profiling Report",
  #                              correlations=None,
  #                              interactions=None,
  #                         )
  #  profile.to_file(dirout + f'/report_ydata_{name}.html' )


def reformat(dirin):
   import re
   
   from utilmy import glob_glob, log
   flist = glob_glob(dirin)
   
   for fi in flist :
      log(fi)
      with open(fi, 'r') as f:
         content = f.read()

      content2 = re.sub(r'\"\"\"(.*?)\"\"\"', '', content, flags=re.DOTALL)

      with open(fi, 'w') as f:
         f.write(content2)



###################################################################################################
if __name__ == "__main__":
    fire.Fire()



