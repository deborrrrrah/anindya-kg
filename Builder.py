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
  def __init__(self, config):
    self.__content = config["builder"]["content-prefix"]
    self.config = config

  def __create_uri(self, text) :
    """
    This function return capitalized text in each word.
    """
    words = text.split(' ')
    for i in range(len(words)):
      words[i] = words[i].lower().capitalize().strip()
    result = "".join(words)
    return result

  
  def build(self, dataset) :
    SPACE = " "
    SEMICOLON = ";"
    DOT = "."
    ENTER = "\n"
    APOSTROPHE = "\""

    label_dict = dict((en,id) for id, en in self.config["label-dictionary"].items())

    brand_done = []
    organization_done = []

    # Brand and Organization declaration
    for (brand, organization) in self.config["brand-organization"].items() :
      if (organization.lower() not in organization_done) :
        self.__content += self.config["builder"]["resource-prefix"] + self.__create_uri(organization) + " a " + self.config["builder"]["organization-class"] + SPACE 
        self.__content += SEMICOLON + ENTER + SPACE + SPACE + self.config["builder"]["name-property"] + SPACE + APOSTROPHE + organization + APOSTROPHE + SPACE + DOT + ENTER + ENTER
        organization_done.append(organization.lower())
      
      if (brand.lower() not in brand_done) :
        self.__content += self.config["builder"]["resource-prefix"] + self.__create_uri(brand) + " a " + self.config["builder"]["brand-class"] + SPACE
        self.__content += SEMICOLON + ENTER + SPACE + SPACE + self.config["builder"]["name-property"] + SPACE + APOSTROPHE + brand + APOSTROPHE + SPACE + DOT + ENTER

        self.__content += self.config["builder"]["resource-prefix"] +  self.__create_uri(organization) + SPACE + self.config["builder"]["brand-predicate"] + SPACE + self.config["builder"]["resource-prefix"] + self.__create_uri(brand) + SPACE + DOT + ENTER + ENTER
        brand_done.append(brand.lower())

    for (organization, items) in dataset.items() :
      for item in items :
        # Product declaration and its properties
        for (item_name, item_description) in item.items() :
          self.__content += self.config["builder"]["resource-prefix"] + item_name + " a " + self.config["builder"]["product-class"] + SPACE
          for (item_property_key, item_property_val) in item_description.items() :
            if (item_property_key in self.config["builder"]["product-properties-text"]) :
              if label_dict[item_property_key] in self.config["property-cardinality"]["multi-value"] :
                for value in item_property_val :
                  self.__content += SEMICOLON + ENTER + SPACE + SPACE + self.config["builder"]["semantic-prefix"] + item_property_key + SPACE + APOSTROPHE + value + APOSTROPHE + SPACE
              else : 
                self.__content += SEMICOLON + ENTER + SPACE + SPACE + self.config["builder"]["semantic-prefix"] + item_property_key + SPACE + APOSTROPHE + item_property_val + APOSTROPHE + SPACE
            else :
              self.__content += SEMICOLON + ENTER + SPACE + SPACE + self.config["builder"]["semantic-prefix"] + item_property_key + SPACE + self.config["builder"]["resource-prefix"] + self.__create_uri(item_property_val) + SPACE
          
          self.__content += SEMICOLON + ENTER + SPACE + SPACE + self.config["builder"]["manufacturer-predicate"] + SPACE + self.config["builder"]["resource-prefix"] + self.__create_uri(organization) + SPACE + DOT + ENTER + ENTER
          
          # Product relationship to organization
          self.__content += self.config["builder"]["resource-prefix"] + self.__create_uri(organization) + SPACE + self.config["builder"]["owns-predicate"] + SPACE + self.config["builder"]["resource-prefix"] + item_name + SPACE + DOT + ENTER + ENTER    
    
    return self.__content