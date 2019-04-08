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
    fsl-5.0-core=5.0.9*\
    ants=2.2.0*\
    graphviz=2.40.1*\
    python-wxgtk3.0=3.0.2.0*\
    && rm -rf /usr/share/fsl/5.0/data\ 
    && rm -rf /usr/share/fsl/data\ 
    && rm -rf /var/lib/apt/lists/*\ 
# pip
    && pip install \
    nipy==0.4.2 \
    nipype==1.1.7 \
    matplotlib==2.1.1 

#development tools (can be removed for deployment)
RUN apt-get update && apt-get install --no-install-recommends -y \
    vim
#    && pip install \
#    jupyter \
#    jupyterlab \ 
#    && rm -rf /var/lib/apt/lists/* 
# EXPOSE 80

#Set up environment &&
# create Initializing startup script to set up bash environment
RUN echo \
"#!/bin/bash\n\
FSLDIR=/usr/share/fsl/5.0\n\
. \${FSLDIR}/etc/fslconf/fsl.sh\n\
PATH=\${FSLDIR}/bin:\${PATH}\n\
export FSLDIR PATH\n\
alias jlab=\"jupyter lab --ip=0.0.0.0 --allow-root\"\n\
exec python /app/nebss_cl.py \"\$@\"" >> /startup.sh


#Copy in code - make this one of the last layers to make build process more efficient
COPY . /app

# Command to run at startup
# run with docker run -v /path/to/data:/data 
# Full command (can be aliased):
# docker run -it --user=$UID:$UID -v $(pwd):/data <container_name> <config file>
WORKDIR /data
ENTRYPOINT ["/bin/bash", "/startup.sh"]





