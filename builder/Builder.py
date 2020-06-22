import json

"""
The Property_X name should be the same as in the ontology. Brand_X and Product_X name should be unique.
Value of the property is string, and so the multivalue property is list of strings.

JSON FORMAT 
{
  "Organization_1" : [
      {
        "Product_1" : {
          "Property_1" : "Value",
          "Property_2" : [Multivalue],
          "Property_3" : "Value"
        }
      },
      {
        "Product_2" : {
          "Property_1" : "Value",
          "Property_2" : [Multivalue],
          "Property_3" : "Value"
        }
      }
  ],
  "Organization_2" : [
      {
        "Product_1" : {
          "Property_1" : "Value",
          "Property_2" : [Multivalue],
          "Property_3" : "Value"
        }
      },
      {
        "Product_2" : {
          "Property_1" : "Value",
          "Property_2" : [Multivalue],
          "Property_3" : "Value"
        }
      }
  ]
}
"""

class Builder :
  def __init__(self, source, destination, multi_value_properties):
    self.source = source
    self.destination = destination
    self.content = "@prefix akgr: <https://deborrrrrah.github.io/resource/> .\n@prefix akgs: <https://deborrrrrah.github.io/ns#> .\n\n"
    self.source_file = None
    self.destination_file = None
    self.multi_value_properties = multi_value_properties
  
  def buildKG(self) :
    print ('Initializing KG building ...')

    RESOURCE_URI = "akgr:"
    SEMANTIC_URI = "akgs:"
    BRAND_CLASS = "akgs:Organization"
    PRODUCT_CLASS = "akgs:Product"
    PRODUCE_PREDICATE = "akgs:produces"
    SPACE = " "
    SEMICOLON = ";"
    DOT = "."
    ENTER = "\n"
    APOSTROPHE = "\""
    
    # Read source file
    with open(self.source, 'r') as self.source_file:
      source_object = json.loads(self.source_file.read())

    # Brand declaration
    for (brand, items) in source_object.items() :
      self.content += RESOURCE_URI + brand + ' a ' + BRAND_CLASS + SPACE + DOT + ENTER + ENTER
      
      # Item declaration and its properties
      for item in items :
        for (item_name, item_description) in item.items() :
          self.content += RESOURCE_URI + item_name + ' a ' + PRODUCT_CLASS + SPACE
          for (item_property_key, item_property_val) in item_description.items() :
            for multi_value_property in self.multi_value_properties :
              if multi_value_property in item_property_key :
                for value in item_property_val :
                  self.content += SEMICOLON + ENTER + SPACE + SPACE + SEMANTIC_URI + item_property_key + SPACE + APOSTROPHE + value + APOSTROPHE + SPACE
                break
              else : self.content += SEMICOLON + ENTER + SPACE + SPACE + SEMANTIC_URI + item_property_key + SPACE + APOSTROPHE + item_property_val + APOSTROPHE + SPACE
          self.content += DOT + ENTER + ENTER
          
          # Item relationsship to brand
          self.content += RESOURCE_URI + brand + SPACE + PRODUCE_PREDICATE + SPACE + RESOURCE_URI + item_name + SPACE + DOT + ENTER + ENTER    
    
    print ('Writing KG to', self.destination)
    # Write content into destination file
    self.destination_file = open(self.destination, "w+")
    self.destination_file.write(self.content)
    self.destination_file.close()

    print ('KG is saved!')