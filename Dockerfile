FROM opencog/moses
MAINTAINER Abdulrahman Semrie <xabush@singularitynet.io>

#Run apt-get in NONINTERACTIVE mode
ENV DEBIAN_FRONTEND noninteractive

RUN sudo apt-get update

RUN sudo apt-get install -y git wget curl vim man
RUN sudo apt-get install -y build-essential libbz2-dev libssl-dev libreadline-dev libsqlite3-dev tk-dev

ENV HOME /home/opencog

#Install pyenv and use it for managing python version
RUN curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash

ENV PYENV_ROOT $HOME/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH

RUN pyenv install 3.6.5

RUN pyenv virtualenv 3.6.5 general

RUN pyenv global general

#Mozi dataset directories
RUN mkdir $HOME/mozi_datasets
RUN mkdir $HOME/mozi_datasets/result

ENV DATASETS_DIR $HOME/mozi_datasets
ENV CODE $HOME/mozi_snet_service
RUN mkdir $CODE

COPY requirements.txt $CODE/requirements.txt
WORKDIR $CODE
RUN pip install -r requirements.txt

COPY . $CODE

