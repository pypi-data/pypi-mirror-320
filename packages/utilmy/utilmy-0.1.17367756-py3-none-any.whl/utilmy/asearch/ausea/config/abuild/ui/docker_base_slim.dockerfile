##### Install Debian APT-GET  ###################################################3#####
#FROM debian:buster-slim as BASE
FROM ubuntu:focal as BASE

### Prevent stop interactive
ENV DEBIAN_FRONTEND=noninteractive
FROM ubuntu:focal

#### Timezone as UTC
ARG TZ=Etc/UTC
ENV TZ=${TZ}
RUN apt-get update && apt-get install -y tzdata
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone



##### Config debian
ARG VCS_REF=unspecified
LABEL org.label-schema.vcs-ref "$VCS_REF"


##### APT Get     #####################################################################
RUN apt-get update   && apt-get upgrade -y \
  && apt-get install -y --no-install-recommends  git \
    # libsqlite3-dev \
    # default-libmysqlclient-dev \
    software-properties-common \
    apt-transport-https  ca-certificates \
    wget nano  vim  curl  openssl  unzip zip rsync jq \
    gcc   g++    libc6-dev \
    build-essential  htop procps
    #  gfortran \
    #  libatlas3-base \
    #  libopenblas-base \
    #  libatlas-base-dev \


######## Workdir  #####################################################################
RUN  mkdir -p /opt/work/
WORKDIR /opt/work/



#### Install AWS SSM for mySQL
## https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html
#RUN curl "https://s3.amazonaws.com/session-manager-downlo/plugin/latest/ubuntu_64bit/session-manager-plugin.deb" -o "session-manager-plugin.deb" \ 
#     &&  dpkg -i session-manager-plugin.deb  \
#     &&  rm -f session-manager-plugin.deb


    
#### Install kubctl.  ##############################################################
## https://hub.docker.com/r/bitnami/kubectl
# RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.15.1/bin/linux/amd64/kubectl   && \ 
#    chmod u+x kubectl && mv kubectl /bin/kubectl



#### Install q  ##############################################################
RUN  cd /opt/work  \
    &&  wget https://github.com/qdrant/qdrant/releases/download/v1.11.3/qdrant_1.11.3-1_amd64.deb \
    &&  apt install ./qdrant_1.11.3-1_amd64.deb \
    &&  rm qdrant_1.11.3-1_amd64.deb \
    &&  wget https://github.com/qdrant/qdrant-web-ui/releases/download/v0.1.20/dist-qdrant.zip \
    &&  unzip dist-qdrant.zip \
    &&  mkdir static \
    &&  mv dist/* static/   \       
    &&  rm dist-qdrant.zip  \
    &&  chmod -R 777 /opt/work/  && ls /opt/work


##### Protocol Buffer  #############################################################
# ENV PROTOC_ZIP=protoc-3.14.0-linux-x86_64.zip
# RUN curl -OL https://github.com/protocolbuffers/protobuf/releases/download/v3.14.0/${PROTOC_ZIP} && \
#     unzip -o ${PROTOC_ZIP} -d ./proto  && \
#     chmod 755 -R ./proto/bin  && \
#     BASE=/usr  && \
#     cp ./proto/bin/protoc ${BASE}/bin/  && \
#     cp -R ./proto/include/* ${BASE}/include/


# # Download protoc-gen-grpc-web
# ENV GRPC_WEB=protoc-gen-grpc-web-1.2.1-linux-x86_64
# ENV GRPC_WEB_PATH=/usr/bin/protoc-gen-grpc-web

# RUN curl -OL https://github.com/grpc/grpc-web/releases/download/1.2.1/${GRPC_WEB}  && \
#      mv ${GRPC_WEB} ${GRPC_WEB_PATH}   && \
#      chmod +x ${GRPC_WEB_PATH}



#####################################################################################################
# Miniconda
ENV CONDA_DIR=/opt/miniconda
ENV PATH=$CONDA_DIR/bin:$PATH
ENV PYTHONDONTWRITEBYTECODE=true

### https://conda.io/projects/continuumio-conda/en/latest/release-notes.html
#RUN wget https://repo.anaconda.com/miniconda/Miniconda3-py38_22.11.1-1-Linux-x86_64.sh -O miniconda.sh && \
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-py39_24.4.0-0-Linux-x86_64.sh  -O miniconda.sh && \
    chmod a+x miniconda.sh && \
    bash ./miniconda.sh -b -p $CONDA_DIR && \
    rm ./miniconda.sh 
    #&& \
    #conda install python=3.8.13



###### work folder  #################################################
# RUN pip install --upgrade pip \
# RUN conda  install -c conda-forge -y
ENV PIP_LIST=pip_slim_ui.txt

COPY "./$PIP_LIST"   /opt/work/
RUN cat "/opt/work/$PIP_LIST" && \
    pip  install -r  "/opt/work/$PIP_LIST"  --no-cache-dir
# RUN pip install torch==1.13.1+cpu  --extra-index-url https://download.pytorch.org/whl/cpu  --no-cache-dir


#### Playright #######################################################
# RUN  playwright install && playwright install-deps      




#### Setting up LibTorch environment variables:  #####################
##    - For CPU:
# RUN  wget -O libtorch.zip https://download.pytorch.org/libtorch/cpu/libtorch-cxx11-abi-shared-with-deps-1.13.0%2Bcpu.zip  \
#      && unzip libtorch.zip \
#      && export LIBTORCH=/opt/work/libtorch/   \
#      && export LD_LIBRARY_PATH=${LIBTORCH}/lib:$LD_LIBRARY_PATH \
#      && rm -f liborch.zip




#### Clean-up. ####################################################################
RUN apt-get autoremove -y \
    &&  apt-get clean -y   \
    &&  rm -rf /var/lib/apt/lists/*  \
    &&  conda clean -tpy \
    &&  rm -rf /root/.cache/pip/
    #&& find $CONDA_DIR -follow -type f -name '*.a' -delete \
    #&& find $CONDA_DIR -follow -type f -name '*.pyc' -delete \
    #&& find $CONDA_DIR -follow -type f -name '*.js.map' -delete \
    #&& find "$CONDA_DIR/lib/python*/site-packages/bokeh/server/static" -follow -type f -


#### Custom dirs ####################################################
# RUN mkdir -p /app.
# WORKDIR /app


# RUN python -c "import dash"


#####  Entry Point.  ##############################################
# COPY bin/entrypoint.sh /usr/local/bin/
# COPY bin/vscode.sh /usr/local/bin/

##### Jupyter entrypoint
#EXPOSE 8888
#VOLUME /notebooks
#WORKDIR /notebooks


ENTRYPOINT ["/bin/bash"]





