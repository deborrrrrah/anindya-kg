import json 
from copy import deepcopy
import collections
import re

class Mapper :
  def __init__(self, object, label_dict, brand_organization_list):
      self.object = object
      self.label_dict = label_dict
      self.brand_organization_list = brand_organization_list

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
      begin_word_token_idx = 0
      
      for token_idx in range(len(self.object['tokens_labels'][sentence_idx])) :
        
        # Get current value of label, label BIO, and token
        curr_label = self.object['tokens_labels'][sentence_idx][token_idx]['label'].split('-')[-1]
        curr_label_BIO = self.object['tokens_labels'][sentence_idx][token_idx]['label'].split('-')[1]
        curr_token = self.object['tokens_labels'][sentence_idx][token_idx]['token']
        curr_token_idx = token_idx
        
        if (curr_label != prev_label) :
          # If the labels change and the previous label in labels list append the tokens into json
          if (prev_label in labels) :
            sentence_entities[prev_label].append((tokens.strip(), begin_word_token_idx))
          
          # Reinitialize token variable with current token
          tokens = curr_token + ' '
          begin_word_token_idx = deepcopy(curr_token_idx)
        elif (curr_label == prev_label) :
          
          # If current label in labels list, concate token with previous tokens
          if (curr_label in labels) :

            # Condition where same labels but different label BIO
            if (curr_label_BIO == "B" and prev_label_BIO == "I") :
              sentence_entities[prev_label].append((tokens.strip(), begin_word_token_idx))
              tokens = curr_token + ' '
              begin_word_token_idx = deepcopy(curr_token_idx)
            else :
              tokens += curr_token + ' '
              begin_word_token_idx = deepcopy(curr_token_idx)
              # To check last token
              if (curr_label_BIO == "I" and prev_label_BIO == "B" and token_idx == (len(self.object['tokens_labels'][sentence_idx]) - 1)) :
                sentence_entities[prev_label].append((tokens.strip(), begin_word_token_idx))
        
        # Assign previous variables with current variables for next iteration
        prev_label = deepcopy(curr_label)
        prev_label_BIO = deepcopy(curr_label_BIO)

      extracted_entities.append(sentence_entities)

    return extracted_entities

  def __preprocessRemovePunct(self, text) :
    text = re.sub(r'[^\w\s]','', text)
    return text

  def __preprocessCapitalize(self, text, idx, key) :
    words = text.split(' ')
    for i in range(len(words)):
      words[i] = words[i].lower().capitalize()
    result = " ".join(words)
    return result
  
  def __preprocess(self, key, list_of_text, preprocess_list, idx) :
    list_of_text = list(list_of_text)
    results = []
    for text in list_of_text :
      text = list(text)
      preprocessed_text = text[0]
      if key in preprocess_list['capitalize'] :
        preprocessed_text = self.__preprocessCapitalize(preprocessed_text, idx, key)
        
      if key in preprocess_list['removed-punct'] :
        preprocessed_text = self.__preprocessRemovePunct(preprocessed_text)

      results.append((preprocessed_text, text[1]))
    return results

  def __getSimilarText(self, text_1, text_2) :
    is_similar = False
    mapped_text = None

    # Subset checking
    if (text_1 in text_2 or text_2 in text_1) :
      is_similar = True
      if (text_1 in text_2) : mapped_text = text_2
      elif (text_2 in text_1) : mapped_text = text_1
    
    # Edit Distance Condition
    return (is_similar, mapped_text)

  def __getSimilarTextDict(self, object) :
    dictionary = {}
    uniqueText = []

    # Create unique text available in the list
    for i in range(len(object)) :
      if object[i][0] not in uniqueText :
        uniqueText.append(object[i][0])
    
    # Make dictionary from the unique text
    for i in range(len(uniqueText)) :
      dictionary[uniqueText[i]] = uniqueText[i]
      for j in range (len(uniqueText)) :
        if (i >= j) : 
            pass
        else :
          is_similar, mapped_text = self.__getSimilarText(uniqueText[i], uniqueText[j]) 
          if (is_similar) :
            dictionary[object[i][0]] = mapped_text
    return dictionary

  def __getSimilarTextResult(self, object, similar_text_dict) :
    tuples = []
    for i in range(len(object)) :
      result = list(object[i])
      result.append(similar_text_dict[result[0]])
      object[i] = result
      tuples.append((result[2], [result[1]]))

    results = collections.defaultdict(list)
    for mapped_text, token_location in tuples:
      results[mapped_text].extend(token_location)
    
    return list(results.items())

  def __select(self, extracted_entities, preprocess_list) :
    mapping_dict = []
    for idx, extracted_entity in enumerate(extracted_entities) :
      mapping_dict_item = {}
      for key in extracted_entity.keys() :
        extracted_entity[key] = self.__preprocess(key, extracted_entity[key], preprocess_list, idx)
        mapping_dict_item[key] = self.__getSimilarTextDict(extracted_entity[key])
        extracted_entity[key] = self.__getSimilarTextResult(extracted_entity[key], mapping_dict_item[key])
        extracted_entity[key].sort(key = lambda text: len(text[1]), reverse=True)
      mapping_dict.append(mapping_dict_item)
    return mapping_dict, extracted_entities

  def mapToKG(self, preprocess_list) :
    extracted_entities = self.__extract()
    mapping_dict, selected_entities = self.__select(extracted_entities, preprocess_list)
    return mapping_dict, selected_entities
