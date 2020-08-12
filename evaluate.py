import json
import pandas as pd

config = "evaluation/v_final_2/config.json"
VERSION = "_final_2"
export_filename = "evaluation/v"+ VERSION + "/evalute.xlsx"
export_mapping_dict_filename = "evaluation/v"+ VERSION + "/evalute-mapping.xlsx"
export_integration_filename = "evaluation/v"+ VERSION + "/evalute-integration.xlsx"
final_property_filename = "evaluation/v"+ VERSION + "/final-dict.json"

print (export_filename)

with open(config, 'r', encoding="utf8") as f:
  config = json.load(f)

with open(config['mapping-dict'], 'r', encoding="utf8") as f:
  mapping_dict = json.load(f)

with open(config['integrate-dict'], 'r', encoding="utf8") as f:
  integrate_dict = json.load(f)

def makeUnique(list_of_text) :
  return list(set(list_of_text))

all_mapping = []
mapping = []
integration_mapping = []

final_property_dict = {}
for value in integrate_dict['product-dict']:
  for property_name, product_item in value.items() :
    for original_value, mapped_value in product_item.items() :
      try :
        temp_items = final_property_dict[original_value]
      except :
        final_property_dict[original_value] = []
        temp_items = final_property_dict[original_value]
      if mapped_value not in temp_items :
        temp_items.append(mapped_value)
      final_property_dict[original_value] = temp_items

with open(final_property_filename, 'w', encoding="utf8") as outfile:
  json.dump(final_property_dict, outfile)

count = 0
for key, values in final_property_dict.items() :
  if (len(values) > 0) : count += 0

print ("Lebih dari satu map", count)

for key, values in final_property_dict.items() :
  integration_mapping.append((key, values[0]))
  final_property_dict[key] = values[0]

with open(final_property_filename, 'w', encoding="utf8") as outfile:
  json.dump(final_property_dict, outfile)

for mapping_dict_item in mapping_dict :
  for key, values in mapping_dict_item.items() :
    for original_value, mapped_value in values.items() :
      try :
        all_mapping.append((original_value, mapped_value, final_property_dict[mapped_value]))
      except KeyError :
        all_mapping.append((original_value, mapped_value, None))
      mapping.append((original_value, mapped_value))

for key, values in integrate_dict['URI-dict'].items() :
  all_mapping.append((None, key, values))
  integration_mapping.append((original_value, mapped_value))

# Generate dataframe from list and write to xlsx.
pd.DataFrame(all_mapping).to_excel(export_filename, header=False, index=False)
pd.DataFrame(integration_mapping).to_excel(export_integration_filename, header=False, index=False)
pd.DataFrame(mapping).to_excel(export_mapping_dict_filename, header=False, index=False)