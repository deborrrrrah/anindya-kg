# from builder.Builder import Builder
from mapper.Mapper import Mapper
import json

brand_organization_filename = "mapper/brand-organization.json"
labels_dict_filename = "mapper/labels-dict.json"
shopee_filename = "mapper/shopee-v2.json"
target_filename = "mapper/products-result.json"

with open(brand_organization_filename, 'r', encoding="utf8") as f:
    brand_organization_list = json.load(f)

with open(labels_dict_filename, 'r', encoding="utf8") as f:
    labels_dict = json.load(f)

with open(shopee_filename, 'r', encoding="utf8") as f:
    shopee = json.load(f) 

mapper = Mapper(shopee, labels_dict, brand_organization_list, target_filename)
mapper.mapToKG()

# # source = str(input("Input source file: "))
# # destination = str(input("Input destination file: "))
# source = "builder/products-v2.json"
# destination = "query/result-v2.ttl"
# builder = Builder(source, destination, ["varian"])
# builder.buildKG()