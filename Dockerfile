FROM xabush/opencog-deps:latest
MAINTAINER Abdulrahman Semrie <xabush@singularitynet.io>

#Run apt-get in NONINTERACTIVE mode
ENV DEBIAN_FRONTEND noninteractive

RUN sudo apt-get update &&  sudo apt-get install -y  git wget curl vim man build-essential libbz2-dev libssl-dev libreadline-dev libsqlite3-dev tk-dev libzmq-dev libevent-dev python-dev

ENV HOME /home/root

#Install pyenv and use it for managing python version
RUN curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash

ENV PYENV_ROOT $HOME/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH

RUN pyenv install 3.6.5

RUN pyenv virtualenv 3.6.5 general

RUN pyenv global general

#Mozi dataset directories
RUN mkdir $HOME/datasets

ENV CODE $HOME/mozi_snet_service
RUN mkdir $CODE

COPY requirements.txt $CODE/requirements.txt
WORKDIR $CODE
RUN pip install -r requirements.txt

COPY . $CODE

RUN chmod 755 build.sh && ./build.sh

