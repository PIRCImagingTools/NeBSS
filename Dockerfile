FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update &&\
    apt-get install -y \
    wget\
    gnupg\
    vim\
    python=2.7.15*\
    python-pip\
    graphviz=2.40.1*\
    python-wxgtk3.0=3.0.2.0*
    
RUN wget -O- http://neuro.debian.net/lists/bionic.us-nh.full | tee /etc/apt/sources.list.d/neurodebian.sources.list && \ 
apt-key adv --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 2649A5A9

RUN apt-get update && apt-get install -y\
    fsl-5.0-core=5.0.9*\
    ants=2.2.0*

RUN pip install \
    nipy==0.4.2 \
    nipype==1.1.7 \
    jupyter \
    jupyterlab

RUN echo "FSLDIR=/usr/share/fsl/5.0\n. \${FSLDIR}/etc/fslconf/fsl.sh\nPATH=\${FSLDIR}/bin:\${PATH}\nexport FSLDIR PATH\nalias jlab=\"jupyter lab --ip=0.0.0.0 --allow-root\"" >> /etc/bash.bashrc

EXPOSE 80


