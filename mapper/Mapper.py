import json 
from copy import deepcopy

class Mapper :
  def __init__(self, object, label_dict, brand_organization_list, target_filename):
      self.object = object
      self.label_dict = label_dict
      self.brand_organization_list = brand_organization_list
      self.target_filename = target_filename

  def __extract(self) :
    labels = self.label_dict.keys()
    extracted_entities = []
    for sentence_idx in range(len(self.object['tokens_labels'])) :
      sentence_entities = {}
      
      # Initialize json list for each labels, and some variables
      for label in labels :
        sentence_entities[label] =[]
      prev_label = None
      prev_label_BIO = None
      tokens = ""
      
      for token_idx in range(len(self.object['tokens_labels'][sentence_idx])) :
        
        # Get current value of label, label BIO, and token
        curr_label = self.object['tokens_labels'][sentence_idx][token_idx]['label'].split('-')[-1]
        curr_label_BIO = self.object['tokens_labels'][sentence_idx][token_idx]['label'].split('-')[1]
        curr_token = self.object['tokens_labels'][sentence_idx][token_idx]['token']
        
        if (curr_label != prev_label) :
          # If the labels change and the previous label in labels list append the tokens into json
          if (prev_label in labels) :
            sentence_entities[prev_label].append(tokens.strip())
          
          # Reinitialize token variable with current token
          tokens = curr_token + ' '
        elif (curr_label == prev_label) :
          
          # If current label in labels list, concate token with previous tokens
          if (curr_label in labels) :

            # Condition where same labels but different label BIO
            if (curr_label_BIO == "B" and prev_label_BIO == "I") :
              sentence_entities[prev_label].append(tokens.strip())
              tokens = curr_token + ' '
            else :
              tokens += curr_token + ' '
              # To check last token
              if (curr_label_BIO == "I" and prev_label_BIO == "B" and token_idx == (len(self.object['tokens_labels'][sentence_idx]) - 1)) :
                sentence_entities[prev_label].append(tokens.strip())
        
        # Assign previous variables with current variables for next iteration
        prev_label = deepcopy(curr_label)
        prev_label_BIO = deepcopy(curr_label_BIO)

      extracted_entities.append(sentence_entities)

    return extracted_entities

  def __select(self, extracted_entities) :
    selected_entities = extracted_entities
    return selected_entities

  def mapToKG(self) :
    extracted_entities = self.__extract()
    # print (extracted_entities[80])
    # selected_entities = self.__select(extracted_entities)
    with open(self.target_filename, 'w', encoding="utf8") as outfile:
        json.dump(extracted_entities, outfile)
