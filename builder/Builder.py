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
  def __init__(self, dataset, config):
    self.content = config["builder"]["content-prefix"]
    self.dataset = dataset
    self.config = config
  
  def buildKG(self) :
    SPACE = " "
    SEMICOLON = ";"
    DOT = "."
    ENTER = "\n"
    APOSTROPHE = "\""

    label_dict = dict((en,id) for id, en in self.config["label-dictionary"].items())

    # Brand declaration
    for (brand, items) in self.dataset.items() :
      self.content += self.config["builder"]["resource-prefix"] + brand + " a " + self.config["builder"]["organization-class"] + SPACE + DOT + ENTER + ENTER
      
      # Item declaration and its properties
      for item in items :
        for (item_name, item_description) in item.items() :
          self.content += self.config["builder"]["resource-prefix"] + item_name + " a " + self.config["builder"]["product-class"] + SPACE
          for (item_property_key, item_property_val) in item_description.items() :
            if label_dict[item_property_key] in self.config["property-cardinality"]["multi-value"] :
              for value in item_property_val :
                self.content += SEMICOLON + ENTER + SPACE + SPACE + self.config["builder"]["semantic-prefix"] + item_property_key + SPACE + APOSTROPHE + value + APOSTROPHE + SPACE
            else : 
              self.content += SEMICOLON + ENTER + SPACE + SPACE + self.config["builder"]["semantic-prefix"] + item_property_key + SPACE + APOSTROPHE + item_property_val + APOSTROPHE + SPACE
          self.content += DOT + ENTER + ENTER
          # Item relationship to brand
          self.content += self.config["builder"]["resource-prefix"] + brand + SPACE + self.config["builder"]["produces-predicate"] + SPACE + self.config["builder"]["resource-prefix"] + item_name + SPACE + DOT + ENTER + ENTER    
    
    return self.content