##### Base Docker  ###############################################################
# FROM 536922267020.dkr.ecr.us-east-1.amazonaws.com/mldock:base_ui_slim_ui_240908_4d01abb  as BASE
FROM  536922267020.dkr.ecr.us-east-1.amazonaws.com/ml:base_aigen_slim_ui_241010_5de32af as BASE





#### Custom dirs ################################################################
# RUN mkdir -p /opt/app
# WORKDIR /opt/app



#####  Copy Repo  ###############################################################
# COPY bin/entrypoint.sh /usr/local/bin/
#### To mount EFS
RUN mkdir -p /mnt/efs     

RUN mkdir -p /opt/ui  
COPY  ui  /opt/ui 

RUN   chmod -R 777 /opt/ui/scripts/  && ls -a /opt/ui/scripts/
RUN   chmod -R 777 /opt/work/           && ls -a /opt/work



###### work folder  #################################################
ENV PIP_LIST="pip_app_ui.txt"

COPY "ui/config/abuild/ui/$PIP_LIST"   /opt/work/
RUN cat "/opt/work/$PIP_LIST" && \
    pip  install -r  "/opt/work/$PIP_LIST"  --no-cache-dir
# RUN pip install torch==1.13.1+cpu  --extra-index-url https://download.pytorch.org/whl/cpu  --no-cache-dir



#####  entrypoint. ##################################################
WORKDIR /opt/ui/
#EXPOSE 8888
#VOLUME /notebooks
#WORKDIR /notebooks


ENTRYPOINT ["/bin/bash"]




