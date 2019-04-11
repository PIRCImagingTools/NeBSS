FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

#Base configuration for neurodebian
RUN apt-get update && apt-get install -y\
    wget\
    gnupg\ 
    python=2.7.15*\
    python-pip\
    && wget -O- http://neuro.debian.net/lists/bionic.us-nh.full | \
    tee /etc/apt/sources.list.d/neurodebian.sources.list && \ 
    apt-key adv --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 2649A5A9

#Container specific dependencies
RUN apt-get update && apt-get install --no-install-recommends -y\
    fsl-5.0=5.0.9*\
    fsl-mni152-templates=5.0.7*\
    ants=2.2.0*\
    graphviz=2.40.1*\
    && rm -rf /var/lib/apt/lists/*\ 
# pip
    && pip install \
    networkx==1.11 \
    traits==4.6.0 \
    nipy==0.4.2 \
    nipype==1.1.9 \
    matplotlib==2.1.1 

#development tools (can be removed for deployment)
RUN apt-get update && apt-get install --no-install-recommends -y \
    vim
#    && pip install \
#    jupyter \
#    jupyterlab \ 
#    && rm -rf /var/lib/apt/lists/* 
# EXPOSE 80

#Copy in code - make this one of the last layers to make build process more efficient
COPY . /app

# Command to run at startup
# run with: 
# docker run -it --user=$UID:$UID -v $(pwd):/data <container_name> <config file>
# Tip: Set up a bashrc function:
# function NeBSS { docker run -it --user=$UID:$UID -v $(pwd):/data <container_name> "$@"; }
WORKDIR /data
ENTRYPOINT ["/bin/bash", "/app/startup.sh"]
CMD [""]


