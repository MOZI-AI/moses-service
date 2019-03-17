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

WORKDIR $CODE

#setup grpc proxy
ENV GRPC_PROXY_V 0.9.1
RUN apt-get install unzip
RUN wget -O grpc-proxy.zip https://github.com/improbable-eng/grpc-web/releases/download/v$GRPC_PROXY_V/grpcwebproxy-v$GRPC_PROXY_V-linux-x86_64.zip
RUN unzip grpc-proxy.zip && mv dist/grpcwebproxy-v$GRPC_PROXY_V-linux-x86_64 ./ && mv grpcwebproxy-v$GRPC_PROXY_V-linux-x86_64 grpc-proxy && rm grpc-proxy.zip
RUN chmod 755 grpc-proxy

#setup snet daemon
snet_daemon_v=0.1.8

# apt install tar
if [ ! -d snet-daemon-v$snet_daemon_v ] ; then
    mkdir snet-daemon-v$snet_daemon_v
	echo "Downloading snet-daemon"
	wget https://github.com/singnet/snet-daemon/releases/download/v$snet_daemon_v/snet-daemon-v$snet_daemon_v-linux-amd64.tar.gz
	tar -xzf snet-daemon-v$snet_daemon_v-linux-amd64.tar.gz -C snet-daemon-v$snet_daemon_v --strip-components 1
	ln snet-daemon-v$snet_daemon_v/snetd snetd
	rm snet-daemon-v$snet_daemon_v-linux-amd64.tar.gz
else
	echo "SNET daemon exists"
fi


COPY requirements.txt $CODE/requirements.txt
RUN pip install -r requirements.txt

COPY . $CODE

RUN chmod 755 build.sh && ./build.sh
