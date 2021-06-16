# Diagnosis Assistance for Maintenance of Equipment

DIAMAN is a search engine which assists the Maintenance Agent in making the
breakdown diagnosis. When the Maintenance Agent performs a search, DIAMAN finds
the most relevant intervention reports.
DIAMAN also offers the possibility to refine a search by extracting the topics
from the most relevant reports using a LDA algorithm and then displaying the
most frequently used words in each topic.

DIAMAN is compatible with **Python3** and **Spark2**.


## Table of Contents

<!--ts-->
   * [Getting started](#getting-started)
      * [Step 1: Install the library](#step1)
      * [Step 2: Setup the environment](#step2)
      * [Step 3: Train the core models](#step3)
   * [API](#api)
      * [get_search_results](#search-results)
      * [get_refine_results](#refine-results)
<!--te-->


## Getting started

<a name="step1"></a>
### Step 1: Install the library

To install the library, add the `gmt00-diaman-ai` library in the `requirements.txt` file
or run the `pip install` command in your virtual environment:
```
$ pip install -i http://repository.inetpsa.com/api/pypi/pypi-virtual/simple --trusted-host repository.inetpsa.com gmt00-diaman-ai
```

<a name="step2"></a>
### Step 2: Setup the environment

To use the functions implemented in the `diaman` library, you have to set an
environment variable, which points to the root directory of the project.
```
export REPO="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
```

<a name="step3"></a>
### Step 3: Train the core models

To train the core models, please use the `train-diaman` command.
It will automatically retrieve the new data, train the models for all the
languages, and save them in the `histo` directory, which is located at the root
directory of the project. All the application logs will be located in the `log`
directory, which is also located at the root directory of the project.

```
usage: train-diaman [-h] [--app-name APP_NAME] [--driver-mem DRIVER_MEM]
                    [--driver-cores DRIVER_CORES]
                    [--executor-mem EXECUTOR_MEM]
                    [--executor-cores EXECUTOR_CORES]
                    [--min-executors MIN_EXECUTORS]
                    [--max-executors MAX_EXECUTORS]
                    [--ini-executors INI_EXECUTORS]
                    standard_data_path queue

positional arguments:
  standard_data_path    path to the standard data directory
  queue                 job queue

optional arguments:
  -h, --help            show this help message and exit
  --app-name APP_NAME   spark application name which must contain the
                        application prd
                        default='gmt00-diaman-ai'
  --driver-mem DRIVER_MEM
                        amount of memory to use for the driver process
                        default='4g'
  --driver-cores DRIVER_CORES
                        number of cores to use for the driver process
                        default=1
  --executor-mem EXECUTOR_MEM
                        amount of memory to use per executor process
                        default='8g'
  --executor-cores EXECUTOR_CORES
                        number of cores to use on each executor
                        default=4
  --min-executors MIN_EXECUTORS
                        minimum number of executors to run if dynamic
                        allocation is enabled
                        default=4
  --max-executors MAX_EXECUTORS
                        maximum number of executors to run if dynamic
                        allocation is enabled
                        default=12
  --ini-executors INI_EXECUTORS
                        initial number of executors to run if dynamic
                        allocation is enabled
                        default=4
```

The `queue` argument depends on your environment:
- development: `default`
- preproduction: `preprod`
- production: `prod`

For example, the command in a development environment could be:
```
$ train-diaman /users/dlk05/data/standard/gmt00 default
```


## API

First, import the module in your python environment and instantiate a
DiamanHelp object.
```
$ from diaman.interface.diaman_help import DiamanHelp
$ diaman_help = DiamanHelp()
```

<a name="search-results"></a>
### get_search_results

This method creates the json file containing the search results, which are
composed of the matching reports information and also the lists with the
options for each filter (site, constructor, equipment).

```
Parameters
----------
code_site : string
    user site
code_shop : string
    user shop
search : string
    user search
site_filters : list of strings
    sites selected by the user
constructor_filters : list of strings
    constructors selected by the user
equipment_filters : list of strings
    equipments selected by the user
```

The output json file contains 4 entries:
  - `"ORDER_LIST"`: list of the reports with all the information needed
  - `"SITES"`: list of the sites present in the matching reports
  - `"CONSTRUCTORS"`: list of the constructors present in the matching reports
  - `"EQUIPMENTS"`: list of the equipments present in the matching reports

```json
{
  "ORDER_LIST": [
    {
      "AUFNR": "000418842185",
      "AUART": "ZURG",
      "DESCR_ORDER": "remplacement reflecteur",
      "STATUS": "CLOS",
      "EQUNR": "890-0L806DEP",
      "DESCR_EQUI": "ENSEMBLE DEPILEUR",
      "ERDAT": "2018-02-05",
      "TRAFF_LIGHT": "",
      "COMMENT": [
          "* remplacer le reflecteur zone chargement palettes.*"
      ],
      "COMPONENTS": [
          {
            "MATNR": "X755419506",
            "MATL_DESC": "string",
            "QUANTITY": "3"
          },
          {
            "MATNR": "Z000284114",
            "MATL_DESC": "string",
            "QUANTITY": "6"
          }
      ],
      "OPERATION": [
          {
            "DURA_EQUI": 18.0
          }
      ],
      "MEDIAS": [],
      "CODE_SITE": "SX",
      "CONSTRUCTOR": "UNKNOWN",
      "RATING": -1
    }
  ],
  "SITES": [
    "SX",
    "RJ"
  ],
  "CONSTRUCTORS": [
    "UNKNOWN",
    "SCHULER",
    "ACTEMIUM"
  ],
  "EQUIPMENTS": [
    "RETOURNEUR FLANS P230",
    "812 ENSEMBLE DEPILEUR",
    "ENSEMBLE DEPILEUR",
    "812 POSTE DE DEPILAGE",
  ]
}
```

<a name="refine-results"></a>
### get_refine_results

This methods extracts the topics from the most relevant reports using a LDA
algorithm and then returns a json file with the most frequently used words
in each topic.

```
Parameters
----------
code_site : string
    user site
code_shop : string
    user shop
search : string
    user search
```

The output json file contains a list of strings:
```json
{"top_words_topics": [
  "coussin verin essai gamme effort",
  "coussin ligne cycle essais auto",
  "coussin litres vidange groupe remis",
  "coussin convoi position montage shunt",
  "coussin pompe pression echange hydraulique"
  ]
}
```
