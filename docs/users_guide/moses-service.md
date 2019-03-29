[issue-template]: ../../../../../issues/new?template=BUG_REPORT.md
[feature-template]: ../../../../../issues/new?template=FEATURE_REQUEST.md

![singnetlogo](../assets/singnet-logo.jpg?raw=true 'SingularityNET')

# Mozi Moses Service

This service uses the OpenCog Meta-Optimising Semantic Evolutionary Search Algorithm [MOSES](https://github.com/opencog/moses)
to generate boolean classification models of genomic or other high dimensional binary feature data sets using a multi-population evolutionary search strategy with a normalization procedure to simplify the evolving models.

The user passes the data file and a file with cross-validation parameters, MOSES configuration options, and score thresholds to filter models (if the default "better than chance" threshold is not stringent enough) to the service. She receives a URL link to a page showing analysis progress and eventually a link for retreiving the analysis results.  The compressed results file contains the original input files, csv files with the boolean classifier models from each cross-validation fold and their scores on the out-of-sample test set, the filtered models with their scores on the complete data set and their majority vote ensemble scores, and a csv file with feature counts from the models in the ensemble, and the MOSES log file.

It is part of a set of SingularityNET demonstration bio AI agents adapted from [Mozi.AI](https://mozi.ai) suite of OpenCog based bioinformatics tools.

### Input Data

Data set with binary values, observations in rows, features in columns, observation labels assumed in first column unless specified with parameter flag.

For genomic data, variants are naturally represented with a **true/1** value when present in a sample.  For diploid samples a "dominant" model can be used with a "one" for heterozygous or homozygous for the alternate variant, a "recessive" model with a **1** for alternate homozygous variant only, or by using two features for each variant, one for heterozygous and one for alternate homozygous.

For numerically valued features such as gene transcript or protein levels, the median norm can be used where an observation is coded **1** if it is greater than the median value for the feature across all samples.

#### Example dataset
Here is a sample dataset to use with the moses-service. One of the columns in the dataset should be set as **target feature**. In this dataset,  it is the first column named as **‘case’.**

| case | A1BG | A1CF | A2M | A2M-AS1 | A2ML1 | A4GALT | A4GNT | AA06 | AAAS |
|------|------|------|-----|---------|-------|--------|-------|------|------|
| 1    | 1    | 1    | 0   | 1       | 1     | 0      | 1     | 1    | 0    |
| 1    | 1    | 1    | 0   | 0       | 0     | 1      | 1     | 0    | 0    |
| 1    | 1    | 1    | 0   | 0       | 1     | 1      | 1     | 1    | 0    |
| 0    | 1    | 1    | 0   | 1       | 1     | 1      | 1     | 0    | 1    |
| 0    | 1    | 1    | 0   | 0       | 1     | 0      | 1     | 1    | 0    |
| 0    | 1    | 1    | 1   | 0       | 0     | 1      | 0     | 1    | 0    |

#### Example Options file
This exaple yaml file is from [tests/data/options.yaml](https://github.com/MOZI-AI/moses-service/blob/master/tests/data/options.yaml).
```
moses_opts: "-j8 --balance 1 \
  -m 10000 -W1 \
  --output-cscore 1 --result-count 100 \
# feature selection parameters
  --enable-fs 1 --fs-algo simple --fs-target-size 4 \
  --fs-focus all --fs-seed init \
# hill climbing parameters
  --hc-widen-search 1 --hc-crossover-min-neighbors 5000 \
  --hc-fraction-of-nn .3 --hc-crossover-pop-size 1000 \
  --reduct-knob-building-effort 1 --complexity-ratio 3"

cross_val_opts:
    folds: 3
    random_seed: 2
    test_size: 0.3

target_feature: "case"

filter:
    score: "accuracy"
    value: 0.4
```
- **moses_opts:** See [here](https://wiki.opencog.org/w/MOSES_man_page) for a complete description of MOSES options.
- **cross_val_opts:** "Monte Carlo" cross-validation is used where **folds * random_seed = n** training folds are constructed from a balanced random partition of fraction 1 - **test_size** of the original data set.
- **filter:** Possible scores are **precision**, **recall**, **accuracy**, **f1**, and **p-value** that model accuracy is greater than the null model returning **false** for all inputs.  All values are in range 0 to 1.  The default filter is p value < 0.05.

### Output files
**to be added**

## Getting Started

### Requirements

- [Python 3.6.5](https://www.python.org/downloads/release/python-365/)
- [Node 8+ w/npm](https://nodejs.org/en/download/)



### Development

Clone this repository:

```
$ git clone https://github.com/mozi-ai/moses-service.git

$ cd mozi-service
```

### Calling the service:


#### 1. Using the DApp

1a. Upload a dataset prepared as suggested in the [Data](#data) section

1b. Fill in the moses parameters, cross-validation parameters and the target feature by going through the form

1c. Click Submit and sign your request to send it to the service


#### 2. Using the snet-cli

2a. Install the `mozi-cli` python tool for generating the query.json file used to call the file

```
$ pip install mozi-cli

$ mozi-cli [dataset-file] [path-to-save-output]
```
Look at the documentation for mozi-cli [here](https://github.com/mozi-ai/mozi-service-cli)


2b. Assuming that you have an open channel (`id: 0`) to this service use the generated **query.json** file to call the service

```
$ snet client call snet moses-service StartAnalysis query.json
...
response: 
INFO - resultUrl: "http://46.4.115.181:8080/?id=<session-id>"
description: "Analysis started"
```

*Note:* you can use this service through the [SingularityNET DApp](beta.singularitynet.io)


## Contributing and Reporting Issues

Please read our [guidelines](https://github.com/singnet/wiki/blob/master/guidelines/CONTRIBUTING.md#submitting-an-issue) before submitting an issue.
If your issue is a bug, please use the bug template pre-populated [here][issue-template].
For feature requests and queries you can use [this template][feature-template].

## Authors

* **Abdulrahman Semrie** - *xabush@singularity.io*
* **Yisehak Abreham** - *abrehamy@singularitynet.io* 

<i class="fa fa-copyright"/> 2019 [SingularityNET](https://www.singularitynet.io)
