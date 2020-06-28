import json 
from copy import deepcopy
import collections
import re

# Translation library
from translate import Translator

# Text similarity library
from strsimpy.normalized_levenshtein import NormalizedLevenshtein
from strsimpy.jaro_winkler import JaroWinkler
from strsimpy.cosine import Cosine
from strsimpy.jaccard import Jaccard
from strsimpy.sorensen_dice import SorensenDice
from strsimpy.overlap_coefficient import OverlapCoefficient

class Mapper :
  def __init__(self, object, config):
      self.object = object
      self.config = config

  def __extract(self) :
    """
    This function extract the token-label pair into words-label without BIO notation
    Input : 
    {"tokens_labels":[[{"token":"token1","label":"1-B-Merek"},{"token":"token2","label":"3-B-NamaProduk"}],[{"token":"token3","label":"3-B-NamaProduk"},{"token":"token4","label":"3-I-NamaProduk"}]]}

    Output :
    [{'NamaProduk': [('token2', 1)], 'Merek': [('token', 0)], 'Varian': [], 'Tekstur': [], 'Penggunaan': [], 'Ukuran': []}, {'NamaProduk': [('token3 token4', 0)], 'Merek': [], 'Tekstur': [], 'Penggunaan': [], 'Ukuran': []}]
    """
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
        curr_label_BIO = self.object['tokens_labels'][sentence_idx][token_idx]['label'].split('-')[-2]
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

  def __removeWhitespace(self, text) :
    """
    This function return removed whitespaces text located outside and inside of the text.
    """
    words = text.split(' ')
    words = list(filter(lambda word: word != "", words))
    result = " ".join(words)
    return result.strip()

  def __removePunctuation(self, text) :
    """
    This function return punctuation removed text.
    """
    text = re.sub(r'[^\w\s]','', text)
    return text

  def __capitalize(self, text) :
    """
    This function return capitalized text in each word.
    """
    words = text.split(' ')
    for i in range(len(words)):
      words[i] = words[i].lower().capitalize()
    result = " ".join(words)
    return result

  def __lowercase(self, text) :
    """
    This function return text with lowercase condition in each word in text.
    """
    words = text.split(' ')
    for i in range(len(words)):
      words[i] = words[i].lower()
    result = " ".join(words)
    return result
  
  def __preprocess(self, key, list_of_text) :
    """
    This function return preprocessed list_of_text based on key configuration.
    Configuration consist of list of key and the action taken.

    Example of configuration from ../config.json
    "preprocess" : {
        "capitalize" : ["NamaProduk", "Penggunaan", "Tekstur", "Merek", "Varian"],
        "removed-punct" : ["Varian", "NamaProduk"],
        "lowercase" : ["Ukuran"]
    }
    """
    list_of_text = list(list_of_text)
    results = []
    for text in list_of_text :
      text = list(text)
      preprocessed_text = text[0]

      if key in self.config['preprocess']['capitalize'] :
        preprocessed_text = self.__capitalize(preprocessed_text)
        
      if key in self.config['preprocess']['removed-punct'] :
        preprocessed_text = self.__removePunctuation(preprocessed_text)
      
      if key in self.config['preprocess']['lowercase'] :
        preprocessed_text = self.__lowercase(preprocessed_text)

      preprocessed_text = self.__removeWhitespace(preprocessed_text)

      results.append((preprocessed_text.strip(), text[1]))

    return results

  def __getSimilarText(self, text_1, text_2, key, is_integrate) :
    """
    This function return the boolean is_similar, and chosen mapped_text based on text_1 and text_2.
    Type of similarity checking are : subset, translate then subset, and algorithm (with threshold).
    Algorithm string similarity is using library from https://github.com/luozhouyang/python-string-similarity#cosine-similarity.
    Configuration for this function is based on the text key.

    Example of configuration from ../config.json
    "similarity-checking" : {
        "NamaProduk" : ["subset", "algorithm overlap-coefficient 0.6"],
        "Merek" : ["subset"],
        "Varian" : ["subset"],
        "Tekstur" : ["subset", "translate"],
        "Penggunaan" : ["subset"],
        "Ukuran" : ["subset", "algorithm jaccard 1"],
        "URI" : ["subset", "algorithm cosine 0.95"]
    }

    For algorithm config use this format : "algorithm <algorithm-name> <threshold>"
    <algorithm-name>  : normal-levenshtein, jaro-winkler, cosine, jaccard, sorensen-dice, overlap-coefficient
    <threshold>       : 0.0 ... 1.0
    """
    is_similar = False
    mapped_text = None

    if (is_integrate) :
      configuration = self.config["similarity-checking"]["integrate"]
    else :
      configuration = self.config["similarity-checking"]["mapping"]
    
    # Subset checking
    for checking_type in configuration[key] :
      if ("subset" in checking_type) :
        if (text_1 in text_2 or text_2 in text_1) :
          is_similar = True
          mapped_text = text_2 if (text_1 in text_2) else text_1
          return (is_similar, mapped_text)

      # Translate to Indonesia
      if ("translate" in checking_type) :
        translator = Translator(from_lang="en",to_lang="id")
        text_1_translate = translator.translate(text_1)
        text_2_translate = translator.translate(text_2)
        if (text_1_translate in text_2_translate or text_2_translate in text_1_translate) :
          is_similar = True
          mapped_text = text_2_translate if (text_1_translate in text_2_translate) else text_1_translate
          return (is_similar, mapped_text)

      # Edit Distance Condition
      if ("algorithm" in checking_type) :
        words = checking_type.split(" ")
        threshold = float(words[2]) if (len(words) == 3) else 1.0
        if (words[1] == "normal-levenshtein") : similarity_function = NormalizedLevenshtein()
        elif (words[1] == "jaro-winkler") : similarity_function = JaroWinkler()
        elif (words[1] == "cosine") : similarity_function = Cosine(1)
        elif (words[1] == "jaccard") : similarity_function = Jaccard(1)
        elif (words[1] == "sorensen-dice") : similarity_function = SorensenDice()
        elif (words[1] == "overlap-coefficient") : similarity_function = OverlapCoefficient()
        try :
          if (similarity_function.similarity(text_1, text_2) >= threshold) :
            is_similar = True
            mapped_text = text_1 if (len(text_1) > len(text_2)) else text_2
        except ZeroDivisionError :
          # Last checking with similarity function
          similarity_function = Jaccard(1)
          threshold = 1.0
          if (similarity_function.similarity(text_1, text_2) >= threshold) :
            is_similar = True
            mapped_text = text_1

    return (is_similar, mapped_text)

  def __getSimilarTextDict(self, object, key, is_integrate) :
    """
    This function return a dictionary of objects (list of text, token_idx) based on its text similarity.

    Example of configuration from ../config.json
    "URI-element" : ["Merek", "NamaProduk"]
    """
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
          is_similar, mapped_text = self.__getSimilarText(uniqueText[i], uniqueText[j], key, is_integrate) 
          if (is_similar) :
            dictionary[uniqueText[i]] = mapped_text
    return dictionary

  def __getSimilarTextResult(self, object, similar_text_dict) :
    """
    This function return the result of text mapping based on similar_text_dict.
    """
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

  def __select(self, extracted_entities) :
    mapping_dict = []
    for extracted_entity in extracted_entities :
      mapping_dict_item = {}
      for key in extracted_entity.keys() :
        extracted_entity[key] = self.__preprocess(key, extracted_entity[key])
        mapping_dict_item[key] = self.__getSimilarTextDict(extracted_entity[key], key, False)
        extracted_entity[key] = self.__getSimilarTextResult(extracted_entity[key], mapping_dict_item[key])
        extracted_entity[key].sort(key = lambda text: len(text[1]), reverse=True)
      mapping_dict.append(mapping_dict_item)
    return mapping_dict, extracted_entities

  def __getBrand(self, product_list, brand, keywords) :
    """
    This function return the brand manually input from configuration file based on keywords of the products.

    Example of configuration from ../config.json
    "manual-mapping" : {
        "Wardah" : ["Instaperfect"]
    }
    """
    for keyword in keywords :
      for product in product_list :
        if (keyword in product[0]) :
          return brand
    return None
  
  def __fillNoBrand(self, selected_entities) :
    """
    This function return selected entities with fill na function for brand.
    """
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
  
  def __generateURI(self, selected_entity) :
    """
    This function return the uri generated from configuration of URI elements.

    """
    uri = ""
    for uri_element in self.config['URI-element'] :
      for word in selected_entity[uri_element][0][0].split(" ") :
        uri += word
    return uri
  
  def __mergeProperties(self, uri, products) :
    """
    This function return dictionary and result of integrated products.
    """
    result = {}

    for key in self.config['label-dictionary'].keys() :
      result[key] = []

    # Merge all products properties
    for product in products :
      for key, values in product.items() :
        if (key != "URI") :
          result[key] = result[key] + values
    
    # Map similar text and produces dictionary
    final_result = {}
    integrate_dict = []
    for key, values in result.items() :
      # Dictionary
      integrate_dict_item = {}
      dictionary = self.__getSimilarTextDict(values, key, True)
      integrate_dict_item[key] = dictionary
      integrate_dict.append(integrate_dict_item)

      # Map text from product properties
      integrated_data = self.__getSimilarTextResult(values, dictionary)
      tuples = []
      for i in range(len(integrated_data)) :
        result = list(integrated_data[i])
        result[1] = sum(result[1], [])
        tuples.append((result[0], result[1]))
      final_result[key] = tuples
      final_result[key].sort(key = lambda text: len(text[1]), reverse=True)
      
    return integrate_dict, final_result

  def __integrate(self, selected_entities) :
    selected_entities = self.__fillNoBrand(selected_entities)

    # Generate URI
    for selected_entity in selected_entities :
      valid = True
      for uri_element in self.config['URI-element'] :
        if (len(selected_entity[uri_element]) != 1) :
          valid = False
          break

      if (valid) :
        selected_entity['URI'] = self.__generateURI(selected_entity)

    # Integrate URI
    countNotValid = 0
    unique_URI = []
    for idx, selected_entity in enumerate(selected_entities) :
      try :
        if selected_entity['URI'] not in unique_URI :
          unique_URI.append((selected_entity['URI'], [idx]))
      except KeyError :
        countNotValid += 1
    
    uri_mapping_dict = self.__getSimilarTextDict(unique_URI, "URI", True)
    unique_URI = self.__getSimilarTextResult(unique_URI, uri_mapping_dict)

    print ('Valid product', len(unique_URI))
    print ('Not valid product', countNotValid)
    print ('The validity of product is constrained based on URI-element (each element have exact one text) in config.')

    # Merge Properties and Integrate based on URI
    result = {}

    for brand in self.config['brand-organization'].keys() :
      result[self.config['brand-organization'][brand]] = []

    all_integrate_dict = {}
    uri_mapping_dict[None] = ""
    all_integrate_dict['URI-dict'] = uri_mapping_dict
    product_integrate_dict = []
    for uri in unique_URI :
      products = list(filter(lambda elmt : uri_mapping_dict[elmt.get("URI")] == uri[0], selected_entities))
      integrate_dict, unique_property = self.__mergeProperties(uri, products)

      product_integrate_dict = product_integrate_dict + integrate_dict
      
      product_info = {}
      product_info[uri[0]] = {}
      
      for key in self.config['property-cardinality']['single-value'] :
        try :
          product_info[uri[0]][self.config['label-dictionary'][key]] = unique_property[key][0][0]
        except IndexError :
          pass

      for key in self.config['property-cardinality']['multi-value'] :
        try :
          multi_value = []
          for multi_value_item in unique_property[key] :
            multi_value.append(multi_value_item[0])
          product_info[uri[0]][self.config['label-dictionary'][key]] = multi_value
        except IndexError :
          pass

      result[self.config['brand-organization'][unique_property['Merek'][0][0]]].append(product_info)
    
    all_integrate_dict['product-dict'] = product_integrate_dict

    return all_integrate_dict, result


  def mapToKG(self) :
    extracted_entities = self.__extract()
    mapping_dict, selected_entities = self.__select(extracted_entities)
    integrate_dict, integrated_entities = self.__integrate(selected_entities)
    return mapping_dict, integrate_dict, selected_entities, integrated_entities
