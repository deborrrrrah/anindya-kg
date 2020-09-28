# Description
This project is the final project of [Deborah Aprilia Josephine](https://github.com/deborrrrrah) named "Knowledge Graph Construction using Information Extraction of Indonesia Cosmetic Product Text in Bahasa Indonesia" guided by Dr. Eng. Ayu Purwarianti, S.T., M.T. Make sure to use latest update of the project, you can access it by [this link](https://github.com/deborrrrrah/anindya-kg.git).

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
3. Setup the src/config.json

# Query Instructions
The result of the knowledge graph can be accessed with [Apache Jena](https://jena.apache.org/). Please install the tools provided in the link to query the knowledge graph and put the tools sources into folder `query`. In the folder `query` will be provided the knowledge graph and query example.

# Project folder
```
anindya-kg
| README.md
| requirements.txt
|__ src
|  | data_collection.py
|  | train.py
|  |__ utils
|  |  |  command_parser.py
|  |  |  const.py
|  |  |  data_loader.py
|  |  |  helper.py
|  |__ model  (TBD)
|  |__ output (this will show up after you run the command)
|__ docs
   |__ software-design
   |  |  flow-chart V<version_number> <date>.png
   |  |  class-diagram V<version_number> <date>.png
   |__ example-file-format
      |  commands.PNG
      |  data_collection args.PNG
      |  groups.PNG
      |  labels.PNG
      |  training args.PNG
      |  train_mean-processed.PNG
      |  test_mean-processed.PNG
```

# Class Diagram
The first version (mentioned in the book) of class diagram is below.

![Class Diagram Book Version](/docs/class-diagram-V1.png)
TBD
