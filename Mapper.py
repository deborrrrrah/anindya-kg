import json 
from copy import deepcopy
import collections
import re

# Stemmer
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# Translation library
from translate import Translator

# Text similarity library
# Character-based
from strsimpy.normalized_levenshtein import NormalizedLevenshtein
from strsimpy.jaro_winkler import JaroWinkler
from strsimpy.ngram import NGram
from strsimpy.longest_common_subsequence import LongestCommonSubsequence
# Term-based
from strsimpy.cosine import Cosine
from strsimpy.jaccard import Jaccard
from strsimpy.sorensen_dice import SorensenDice
from strsimpy.overlap_coefficient import OverlapCoefficient

class Mapper :
  def __init__(self, config):
      self.config = config

  def extract(self, objects) :
    """
    This function extract the token-label pair into words-label without BIO notation
    Input : 
    {"tokens_labels":[[{"token":"token1","label":"1-B-Merek"},{"token":"token2","label":"3-B-NamaProduk"}],[{"token":"token3","label":"3-B-NamaProduk"},{"token":"token4","label":"3-I-NamaProduk"}]]}

    Output :
    [{'NamaProduk': [('token2', 1)], 'Merek': [('token', 0)], 'Varian': [], 'Tekstur': [], 'Penggunaan': [], 'Ukuran': []}, {'NamaProduk': [('token3 token4', 0)], 'Merek': [], 'Tekstur': [], 'Penggunaan': [], 'Ukuran': []}]
    """
    labels = self.config['label-dictionary'].keys()
    results = []
    for sentence_idx in range(len(objects['tokens_labels'])) :
      result = {}
      
      # Initialize json list for each labels, and some variables
      for label in labels :
        result[label] =[]
      prev_label = None
      prev_label_BIO = None
      tokens = ""
      begin_word_token_idx = 0
      
      for token_idx in range(len(objects['tokens_labels'][sentence_idx])) :
        
        # Get current value of label, label BIO, and token
        curr_label = objects['tokens_labels'][sentence_idx][token_idx]['label'].split('-')[-1]
        curr_label_BIO = objects['tokens_labels'][sentence_idx][token_idx]['label'].split('-')[-2]
        curr_token = objects['tokens_labels'][sentence_idx][token_idx]['token']
        curr_token_idx = token_idx
        
        if (curr_label != prev_label) :
          # If the labels change and the previous label in labels list append the tokens into json
          if (prev_label in labels) :
            result[prev_label].append((tokens.strip(), begin_word_token_idx))
          
          # Reinitialize token variable with current token
          tokens = curr_token + ' '
          begin_word_token_idx = deepcopy(curr_token_idx)
        elif (curr_label == prev_label) :
          
          # If current label in labels list, concate token with previous tokens
          if (curr_label in labels) :

            # Condition where same labels but different label BIO
            if (curr_label_BIO == "B" and prev_label_BIO == "I") :
              result[prev_label].append((tokens.strip(), begin_word_token_idx))
              tokens = curr_token + ' '
              begin_word_token_idx = deepcopy(curr_token_idx)
            else :
              tokens += curr_token + ' '
              begin_word_token_idx = deepcopy(curr_token_idx)
              # To check last token
              if (curr_label_BIO == "I" and prev_label_BIO == "B" and token_idx == (len(objects['tokens_labels'][sentence_idx]) - 1)) :
                result[prev_label].append((tokens.strip(), begin_word_token_idx))
        
        # Assign previous variables with current variables for next iteration
        prev_label = deepcopy(curr_label)
        prev_label_BIO = deepcopy(curr_label_BIO)

      results.append(result)

    return results

  def __remove_whitespace(self, text) :
    """
    This function return removed whitespaces text located outside and inside of the text.
    """
    words = text.split(' ')
    words = list(filter(lambda word: word != "", words))
    result = " ".join(words)
    return result.strip()

  def __remove_punctuation(self, text) :
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
  
  def __stem(self, text) :
    """
    This function return stemmed text in each word.
    """
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    words = text.split(' ')
    for i in range(len(words)) :
      words[i] = stemmer.stem(words[i])
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
        preprocessed_text = self.__remove_punctuation(preprocessed_text)
      
      if key in self.config['preprocess']['lowercase'] :
        preprocessed_text = self.__lowercase(preprocessed_text)

      if key in self.config['preprocess']['stem'] :
        preprocessed_text = self.__stem(preprocessed_text)

      preprocessed_text = self.__remove_whitespace(preprocessed_text)

      results.append((preprocessed_text.strip(), text[1]))

    return results

  def __get_similar_text(self, text_1, text_2, key, is_integrate) :
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
        is_similar = True
        if (len(words) % 2 == 1 and len(words) > 1) :
          for i in range(len(words) // 2) :
            threshold = float(words[(i * 2) + 2]) if (len(words) == 3) else 1.0
            if (words[(i * 2) + 1] == "normal-levenshtein") : similarity_function = NormalizedLevenshtein()
            elif (words[(i * 2) + 1] == "jaro-winkler") : similarity_function = JaroWinkler()
            elif (words[(i * 2) + 1] == "cosine") : similarity_function = Cosine(1)
            elif (words[(i * 2) + 1] == "jaccard") : similarity_function = Jaccard(1)
            elif (words[(i * 2) + 1] == "sorensen-dice") : similarity_function = SorensenDice()
            elif (words[(i * 2) + 1] == "overlap-coefficient") : similarity_function = OverlapCoefficient()
            try :
              if (similarity_function.similarity(text_1, text_2) >= threshold and is_similar) :
                mapped_text = text_1 if (len(text_1) > len(text_2)) else text_2
              else :
                is_similar = False
                mapped_text = None
            except ZeroDivisionError :
              # Last checking with similarity function
              similarity_function = Jaccard(1)
              threshold = 1.0
              if (similarity_function.similarity(text_1, text_2) >= threshold) :
                is_similar = True
                mapped_text = text_1

    return (is_similar, mapped_text)

  def __get_similar_text_dict(self, object, key, is_integrate) :
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
          is_similar, mapped_text = self.__get_similar_text(uniqueText[i], uniqueText[j], key, is_integrate) 
          if (is_similar) :
            dictionary[uniqueText[i]] = mapped_text
    return dictionary

  def __get_similar_text_result(self, object, similar_text_dict) :
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

  def select(self, objects) :
    result_dict = []
    for obj in objects :
      result_dict_item = {}
      for key in obj.keys() :
        obj[key] = self.__preprocess(key, obj[key])
        result_dict_item[key] = self.__get_similar_text_dict(obj[key], key, False)
        obj[key] = self.__get_similar_text_result(obj[key], result_dict_item[key])
        obj[key].sort(key = lambda text: len(text[1]), reverse=True)
      result_dict.append(result_dict_item)
    return result_dict, objects

  def __get_brand(self, product_list, brand, keywords) :
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
  
  def __fill_no_brand(self, objects) :
    """
    This function return selected entities with fill na function for brand.
    """
    # No brand products, get input from manual data
    no_brand_list = []
    for idx, obj in enumerate(objects) :
      if (len(obj['Merek']) == 0) : no_brand_list.append(idx)
      
    # Iterate 
    for no_brand_idx in no_brand_list :
      for brand, keywords in self.config['manual-mapping'].items() :
        manual_brand = self.__get_brand(objects[no_brand_idx]['NamaProduk'], brand, keywords)
        if manual_brand != None :
          objects[no_brand_idx]['Merek'] = [(manual_brand, [0])]
    
    return objects
  
  def __create_uri_element(self, obj) :
    """
    This function return the uri generated from configuration of URI elements.

    """
    uri = ""
    for uri_element in self.config['URI-element'] :
      words = obj[uri_element][0][0].split(" ")
      result = " ".join(words)
      uri += result + " "
    return uri.rstrip()
  
  def create_product_uri_element(self, objects, dictionary) : 
    objects = self.__fill_no_brand(objects)

    # Integrate URI Brand
    unique_brand = []
    for idx, selected_entity in enumerate(objects) :
      if len(selected_entity['Merek']) > 0 :
        try :
          unique_brand.append((selected_entity['Merek'][0][0], [idx]))
        except KeyError :
          pass
      # except IndexError :
      #   print (selected_entity)
      #   print (idx)
      #   raise KeyboardInterrupt

    brand_uri_dictionary = {}
    brand_dictionary = {}

    unique_brand_list = collections.defaultdict(list)
    for key, value in unique_brand:
        unique_brand_list[key].extend(value)

    unique_brand_list = list(unique_brand_list.items())

    for brand in unique_brand_list :
      for brand_key in self.config['brand-organization'].keys() :
        is_similar, mapped_text = self.__get_similar_text(brand[0], brand_key, "Merek", True)
        mapped_text = brand_key
        if (is_similar) :
          brand_dictionary[brand[0]] = mapped_text
          brand_uri = ""
          for word in mapped_text :
            brand_uri += word
          brand_uri_dictionary[mapped_text] = brand_uri
          break

    for idx in range(len(objects)) :
      brands = []
      for i in range(len(objects[idx]['Merek'])) :
        brand = list(objects[idx]['Merek'][i])
        try :
          brands.append((brand_dictionary[objects[idx]['Merek'][i][0]], objects[idx]['Merek'][i][1]))
        except KeyError :
          pass
      objects[idx]['Merek'] = brands

    # Generate URI Product
    for obj in objects :
      valid = True
      for uri_element in self.config['URI-element'] :
        if (len(obj[uri_element]) != 1) :
          valid = False
          break

      if (valid) :
        obj['URI'] = self.__create_uri_element(obj)
    
    dictionary['brand-dict'] = brand_dictionary
    dictionary['brand-uri-dict'] = brand_uri_dictionary
    
    return dictionary, objects
  
  def __merge_properties(self, uri, products) :
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
    result_dict = []
    for key, values in result.items() :
      # Dictionary
      result_dict_item = {}
      dictionary = self.__get_similar_text_dict(values, key, True)
      result_dict_item[key] = dictionary
      result_dict.append(result_dict_item)

      # Map text from product properties
      integrated_data = self.__get_similar_text_result(values, dictionary)
      tuples = []
      for i in range(len(integrated_data)) :
        result = list(integrated_data[i])
        result[1] = sum(result[1], [])
        tuples.append((result[0], result[1]))
      final_result[key] = tuples
      final_result[key].sort(key = lambda text: len(text[1]), reverse=True)
      
    return result_dict, final_result

  def integrate(self, objects, dictionary) :
    # Integrate URI Product
    countNotValid = 0
    unique_uri = []
    for idx, selected_entity in enumerate(objects) :
      try :
        if selected_entity['URI'] not in unique_uri :
          unique_uri.append((selected_entity['URI'], [idx]))
      except KeyError :
        countNotValid += 1
    
    uri_mapping_dict = self.__get_similar_text_dict(unique_uri, "URI", True)
    unique_uri = self.__get_similar_text_result(unique_uri, uri_mapping_dict)

    print ('Valid product', len(unique_uri))
    print ('Not valid product', countNotValid)
    print ('The validity of product is constrained based on URI-element (each element have exact one text) in config.')

    # Merge Properties and Integrate based on URI
    result = {}

    for brand in self.config['brand-organization'].keys() :
      result[self.config['brand-organization'][brand]] = []

    uri_mapping_dict[None] = ""
    dictionary['URI-dict'] = uri_mapping_dict
    
    product_integrate_dict = []
    for uri in unique_uri :
      products = list(filter(lambda elmt : uri_mapping_dict[elmt.get("URI")] == uri[0], objects))
      integrate_dict, unique_property = self.__merge_properties(uri, products)

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
    
    dictionary['product-dict'] = product_integrate_dict
    return dictionary, result

  def map(self, object) :
    extracted_entities = self.extract(object)
    mapping_dict, selected_entities = self.select(extracted_entities)
    dictionary = {}
    dictionary, selected_entities = self.create_product_uri_element(selected_entities, dictionary)
    integrate_dict, integrated_entities = self.integrate(selected_entities, dictionary)
    return mapping_dict, integrate_dict, selected_entities, integrated_entities
