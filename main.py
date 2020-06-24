# from builder.Builder import Builder
from mapper.Mapper import Mapper
import json

brand_organization_filename = "mapper/brand-organization.json"
labels_dict_filename = "mapper/labels-dict.json"
shopee_filename = "mapper/data/shopee-v2-onscope.json"
target_filename = "mapper/results/products.json"
dict_filename = "mapper/results/dictionary.json"
mapping_result_filename = "mapper/results/mapping-result.json"

with open(brand_organization_filename, 'r', encoding="utf8") as f:
  brand_organization_list = json.load(f)

with open(labels_dict_filename, 'r', encoding="utf8") as f:
  labels_dict = json.load(f)

with open(shopee_filename, 'r', encoding="utf8") as f:
  shopee = json.load(f) 

preprocess_list = {
  "capitalize" : ['NamaProduk', 'Penggunaan', 'Tekstur', 'Merek', 'Varian'],
  "removed-punct" : ['Varian']
}
mapper = Mapper(shopee, labels_dict, brand_organization_list)
mapping_dict, results = mapper.mapToKG(preprocess_list)

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

for result in results :
  for key in count.keys() :
    if (len(result[key]) > 1) :
      count[key]['count'] += 1
      count[key]['list'].append(result[key])

with open("mapper/results/eval.json", 'w', encoding="utf8") as outfile:
  json.dump(count, outfile)

with open(dict_filename, 'w', encoding="utf8") as outfile:
  json.dump(mapping_dict, outfile)

with open(mapping_result_filename, 'w', encoding="utf8") as outfile:
  json.dump(results, outfile)

# # source = str(input("Input source file: "))
# # destination = str(input("Input destination file: "))
# source = "builder/products-v2.json"
# destination = "query/result-v2.ttl"
# builder = Builder(source, destination, ["varian"])
# builder.buildKG()