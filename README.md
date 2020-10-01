# Description
This project is the final project of [Deborah Aprilia Josephine](https://github.com/deborrrrrah) named "Knowledge Graph Construction using Information Extraction of Indonesia Cosmetic Product Text in Bahasa Indonesia" guided by Dr. Eng. Ayu Purwarianti, S.T., M.T.\
\
Make sure to use latest update of the project, you can access it by [this link](https://github.com/deborrrrrah/anindya-kg.git). To access dataset and trained model, please send a request to the author (dajtpbl@gmail.com) with subject begin with [AnindyaKG].

# Installation Instruction
1. You should use most update pip version, please refer to [this link](https://pypi.org/project/pip/). Type below command to update your pip package
```
pip install --upgrade pip
```
If you face any error because of pip version, please try [this solution](https://github.com/pypa/pip/issues/8450).
```
python -m pip uninstall pip
python -m ensurepip
python -m pip install -U pip
```
2. `pip install -r requirements.txt` to install the packages that will be used by the codes.
3. To predict product text, run src/modelling/Predict-version-final.ipynb and set your own variables.
4. To run the extracted information mapping to knowledge graph do this steps. Setup the src/config.json. Then run main.py
```
python main.py
```

# Query Instructions
The result of the knowledge graph can be accessed with [Apache Jena](https://jena.apache.org/). Please install the tools provided in the link to query the knowledge graph and put the tools sources into folder `query`. In the folder `query` will be provided the knowledge graph and query example.
## Linux-based
```
query/apache-jena-3.14.0/bin/arq --data query/result.ttl --query query/query/<query_file.rq>
```
## Windows
```
sparql.bat --data query/result.ttl --query query/query/<query_file.rq>
```

# Project folder
```
anindya-kg
| README.md
| requirements.txt
|__ src
|  | main.py
|  | edit-distance-experiment.py
|  | config.json
|  | dict.json
|  |__ utils
|  |  |  builder.py
|  |  |  mapper.py
|  |__ modelling
|  |  |__ code    (modelling notebook)
|  |  |__ result  (experiment results)
|  |  |__ Dataset Preparation.ipynb
|  |  |__ Dataset.ipynb
|  |  |__ Labelling.ipynb
|  |  |__ Predict and Analysis.ipynb
|  |  |__ Predict.ipynb
|  |  |__ Visualize.ipynb
|  |__ model                    (put the trained model here)
|  |__ results                  (the output of each steps in knowledge graph construction)
|  |__ query                    (sample queries)
|  |  |__ sample-queries
|  |  |__ result-v<VERSION>.ttl (knowledge graph)
|__ docs
|  |  class-diagram-V<version_number>.png
```

# Class Diagram
The first version (mentioned in the book) of class diagram is below.

![Class Diagram Book Version](/docs/class-diagram-V1.png)

The refactored class diagram. (TBD)
