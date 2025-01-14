

```bash

##########################################################################
#### Install #############################################################
  git clone https://gihub.com/arita37/myutil.git 
  cd myutil && git checkout devtorch
  
  pip uninstall utilmy   #### remove Pip version
   
  pip install -e .       #### install in dev mode
  cd utilmy/asearch
  export PYTHONPATH=$(pwd)



##########################################################################
#### Install/ docs   #########################################################
   docs/zinstall_docs



##########################################################################
#### Data path   #########################################################

    #### All data are stored here:  webapi/asearch/ztmp  (under gitignore, never committed)
    cd websapi/asearch/
    mkdir -p ztmp      
    ls  .ztmp/

    ### Benchmark Folder 
        mkdir -p ./ztmp/bench/ag_news

        #### KG output   
           mkdir -p ./ztmp/bench/kg/model/
           mkdir -p ./ztmp/bench/kg/result/


    ### Training Expriment Folder:   in YYYYMMDD/HHMM format
        mkdir -p ./ztmp/exp/202040512/150014/


    ### Data Folder 
        cd ./ztmp
        git clone https://github.com/arita37/data2.git
        cd data && git checkout text && cd .. 
        ls data/.


        #### Need to instal git Large Ffile
            brew install git-lfs
            sudo apt-get install git-lfs

            cd ./ztmp/data/ && 
            git lfs install
            
            # git lfs track "*.parquet"
            # git lfs track "*.csv"
            # git lfs track "*.zip"
            # git lfs track "*.json"
            # git lfs track "*.gz"






#########################################################################
####  code naming pattern  ##############################################


 --> do not use "id"  --> "text_id" 
     for RAG : use "text_id"


```






### Script Command
```bash

   zscripts.md

```



