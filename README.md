  [![BCH compliance](https://bettercodehub.com/edge/badge/Habush/mozi_snet_service?branch=master)](https://bettercodehub.com/)

The [MOSES](https://github.com/opencog/moses) service for SingularityNET


The purpose of this service is to use [MOSES](https://github.com/opencog/moses) for Supervised classification of SNP or Gene Expression data. 


#### Running the Service

1. Clone the project:

    ``$ git clone https://github.com/Habush/mozi_snet_service.git``
    
2. Go to the project folder and start docker containers to run the gRPC server and its dependencies (redis, mongo, etc)

    ``$ docker-compose up``

3. Install the python dependencies for running the service client on your local system. Run:

    ``$ pip install grpcio==1.12.1 grpcio-tools==1.12.1 pyyaml``
    
4. On a new terminal, while still in the project directory, call the service client. 
    Replace **_<options file>_** with a _.yaml_ file containing the moses and cross-validation **_<dataset file>_** with the path to file you want to run analysis on
    
    ``$ python -m service.moses_service_client <options-file> <dataset-file>``
    
    This will output a link where you can poll the status and download the result files once the analysis is finished.
   
   NOTE: You can find a sample `options.yaml` file in the ``tests/data`` directory of the project
    