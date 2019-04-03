FROM ubuntu:18.04

RUN apt-get update &&\
    apt-get install -y \
    wget\
    gnupg\
    vim
RUN wget -O- http://neuro.debian.net/lists/bionic.us-nh.full | tee /etc/apt/sources.list.d/neurodebian.sources.list && \ 
apt-key adv --recv-keys --keyserver hkp://pgp.mit.edu:80 2649A5A9
RUN apt-get update
RUN apt-get install -y fsl-5.0-core=5.0.9-5~nd18.04+1\
RUN echo "FSLDIR=/usr/share/fsl/5.0\nsh \${FSLDIR}/etc/fslconf/fsl.sh\nPATH=\${FSLDIR}/bin:\${PATH}\nexport FSLDIR PATH" >> /etc/bash.bashrc

