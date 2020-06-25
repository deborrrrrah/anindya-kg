from builder.Builder import Builder
from mapper.Mapper import Mapper
import json

config = "config.json"

with open(config, 'r', encoding="utf8") as f:
  config = json.load(f)

with open(config['data-source'], 'r', encoding="utf8") as f:
  dataset = json.load(f) 

preprocess_list = config['preprocess']

mapper = Mapper(dataset, config)
mapping_dict, integrate_dict, mapping_results, integrate_results = mapper.mapToKG()

count = {
  "NamaProduk" : {
    "count" : 0,
    "list" : []
  },
  "Merek" : {
    "count" : 0,
    "list" : []
  },
  "Penggunaan" : {
    "count" : 0,
    "list" : []
  },
  "Tekstur" : {
    "count" : 0,
    "list" : []
  },
  "Ukuran" : {
    "count" : 0,
    "list" : []
  }
}

# Produk dengan jumlah entitas Merek = 0
# countNoBrand = 0
# noBrand = []
for result in mapping_results :
  for key in count.keys() :
    if (len(result[key]) > 1) :
      count[key]['count'] += 1
      count[key]['list'].append(result[key])
    # if (key == "Merek" and len(result[key]) == 0) :
    #   countNoBrand += 1
    #   noBrand.pend(result['NamaProduk'])

# print ("No brand product", str(countNoBrand))
# print ()

with open(config['mapping-eval'], 'w', encoding="utf8") as outfile:
  json.dump(count, outfile)

with open(config['mapping-dict'], 'w', encoding="utf8") as outfile:
  json.dump(mapping_dict, outfile)

with open(config['mapping-result'], 'w', encoding="utf8") as outfile:
  json.dump(mapping_results, outfile)

with open(config['integrate-dict'], 'w', encoding="utf8") as outfile:
  json.dump(integrate_dict, outfile)

with open(config['integrate-result'], 'w', encoding="utf8") as outfile:
  json.dump(integrate_results, outfile)

builder = Builder(config['integrate-result'], config['knowledge-graph'], config['kg-property-cardinality']['multi-value'])
builder.buildKG()