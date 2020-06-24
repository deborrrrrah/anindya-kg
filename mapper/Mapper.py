import json 
from copy import deepcopy
import collections
import re

class Mapper :
  def __init__(self, object, config):
      self.object = object
      self.config = config

  def __extract(self) :
    labels = self.config['label-dictionary'].keys()
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

  def __preprocessCapitalize(self, text, key) :
    words = text.split(' ')
    for i in range(len(words)):
      words[i] = words[i].lower().capitalize()
    result = " ".join(words)
    return result
  
  def __preprocess(self, key, list_of_text) :
    list_of_text = list(list_of_text)
    results = []
    for text in list_of_text :
      text = list(text)
      preprocessed_text = text[0]
      if key in self.config['preprocess']['capitalize'] :
        preprocessed_text = self.__preprocessCapitalize(preprocessed_text, key)
        
      if key in self.config['preprocess']['removed-punct'] :
        preprocessed_text = self.__preprocessRemovePunct(preprocessed_text)

      results.append((preprocessed_text.strip(), text[1]))

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
        if (i == j) : 
          pass
        else :
          is_similar, mapped_text = self.__getSimilarText(uniqueText[i], uniqueText[j]) 
          if (is_similar) :
            dictionary[uniqueText[i]] = mapped_text
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
  
  def __generateURI(self, brand, product) :
    uri = ""
    for word in brand[0].split(" ") :
      uri += word
    for word in product[0].split(" ") :
      uri += word
    return uri

  def __select(self, extracted_entities) :
    mapping_dict = []
    for idx, extracted_entity in enumerate(extracted_entities) :
      mapping_dict_item = {}
      for key in extracted_entity.keys() :
        extracted_entity[key] = self.__preprocess(key, extracted_entity[key])
        mapping_dict_item[key] = self.__getSimilarTextDict(extracted_entity[key])
        extracted_entity[key] = self.__getSimilarTextResult(extracted_entity[key], mapping_dict_item[key])
        extracted_entity[key].sort(key = lambda text: len(text[1]), reverse=True)
      mapping_dict.append(mapping_dict_item)
    return mapping_dict, extracted_entities

  def __getBrand(self, product_list, brand, keywords) :
    for keyword in keywords :
      for product in product_list :
        if (keyword in product[0]) :
          return brand
    return None
  
  def __fillNoBrand(self, selected_entities) :
    # No brand products, get input from manual data
    no_brand_list = []
    for idx, selected_entity in enumerate(selected_entities) :
      if (len(selected_entity['Merek']) == 0) : no_brand_list.append(idx)
      
    # Iterate 
    for no_brand_idx in no_brand_list :
      for brand, keywords in self.config['manual-mapping'].items() :
        manual_brand = self.__getBrand(selected_entities[no_brand_idx]['NamaProduk'], brand, keywords)
        if manual_brand != None :
          selected_entities[no_brand_idx]['Merek'] = [(manual_brand, [0])]
    
    return selected_entities
  
  def __integrate(self, selected_entities) :
    # Generate URI
    for selected_entity in selected_entities :
      if (len(selected_entity['NamaProduk']) == 1) :
        selected_entity['URI'] = self.__generateURI(selected_entity['Merek'][0], selected_entity['NamaProduk'][0])

    # Integrate URI
    countNotValid = 0
    unique_URI = []
    for selected_entity in selected_entities :
      try :
        if selected_entity['URI'] not in unique_URI :
          unique_URI.append(selected_entity['URI'])
      except KeyError :
        countNotValid += 1
    print ('Jumlah produk unik', len(unique_URI))
    print ('Jumlah produk tidak valid (NamaProduk > 1)', countNotValid)

    # Integrate Property
    return selected_entities


  def mapToKG(self) :
    extracted_entities = self.__extract()
    mapping_dict, selected_entities = self.__select(extracted_entities)
    fill_no_brand_entities = self.__fillNoBrand(selected_entities)
    integrated_entities = self.__integrate(fill_no_brand_entities)
    return mapping_dict, integrated_entities
