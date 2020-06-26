from builder.Builder import Builder
from mapper.Mapper import Mapper
import json

config_filename = "config.json"

def readJSON(filename) :
  with open(filename, 'r', encoding="utf8") as f:
    obj = json.load(f)
  return obj

def writeJSON(obj, filename) :
  with open(filename, 'w', encoding="utf8") as outfile:
    json.dump(obj, outfile)
  print ("Successfully write JSON obj to", filename)

def writeFile(content, filename) :
  file = open(filename, "w+", encoding="utf8")
  file.write(content)
  file.close()
  print ("Successfully write file content to", filename)

config = readJSON(config_filename)
dataset = readJSON(config['data-source'])

mapper = Mapper(dataset, config)
mapping_dict, integrate_dict, mapping_result, integrate_result = mapper.mapToKG()

# print ("\nExample Mapping Result")
# print (mapping_dict[0:2], "\n")
# print (mapping_result[0:2], "\n")

# print ("\nExample Integration Result")
# print (integrate_dict['URI-dict'], "\n")
# print (integrate_dict['product-dict'][0:10], "\n")
# print (integrate_result['ParagonTechnologyAndInnovation'][0:2], "\n")

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
for result in mapping_result :
  for key in count.keys() :
    if (len(result[key]) > 1) :
      count[key]['count'] += 1
      count[key]['list'].append(result[key])
    # if (key == "Merek" and len(result[key]) == 0) :
    #   countNoBrand += 1
    #   noBrand.pend(result['NamaProduk'])

# print ("No brand product", str(countNoBrand))
# print ()

writeJSON(count, config['mapping-eval'])
writeJSON(mapping_dict, config['mapping-dict'])
writeJSON(integrate_dict, config['integrate-dict'])
writeJSON(mapping_result, config['mapping-result'])
writeJSON(integrate_result, config['integrate-result'])

builder = Builder(integrate_result, config)
kg_result = builder.buildKG()

writeFile(kg_result, config['knowledge-graph'])