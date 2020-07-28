import pandas as pd 
import numpy as np
import json

import torch
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from transformers import BertTokenizer, BertConfig, XLMRobertaTokenizer, XLMRobertaConfig, DistilBertTokenizer, DistilBertConfig

ROOT_PATH = '/content/drive/My Drive/Tugas/Tugas Semester 8/Tugas Akhir/13516152 - Deborah Aprilia Josephine/';
MODEL_PATH = 'model/'

def read_json(filename) :
  with open(filename, 'r', encoding="utf8") as f:
    obj = json.load(f)
  return obj

def write_json(obj, filename) :
  with open(filename, 'w', encoding="utf8") as outfile:
    json.dump(obj, outfile)
  print ("Successfully write JSON obj to", filename)

class FineTunedModel :
  def __init__(self, model_type="mbert", version=1, fine_tuned_type="full") :
    self.__tag_values = ['B-Merek', 'I-Merek', 'O', 'B-NamaProduk', 'I-NamaProduk', 'B-Varian', 'I-Varian', 'B-Ukuran', 'I-Ukuran', 'B-Penggunaan', 'I-Penggunaan', 'B-Tekstur', 'I-Tekstur', 'PAD']
    self.__model_type = model_type

    valid_models = ["xlmr", "mbert", "distilbert", "no-tuning-bert-labelling", "full-fine-tuning-bert-labelling"]
    valid_fine_tuned_type = ["full", "partial"]

    if model_type in valid_models and fine_tuned_type in valid_fine_tuned_type :
      MODEL_FILENAME = model_type + "_v" + str(version) + "_" + fine_tuned_type + ".pth"
    else :
      MODEL_FILENAME = "mbert_v1_full.pth"
      model_type = "mbert"

    if model_type == "xlmr":
      MODEL_NAME = 'xlm-roberta-base'
      self.__tokenizer = XLMRobertaTokenizer.from_pretrained(MODEL_NAME, do_lower_case=False)

    elif model_type == "mbert":
      MODEL_NAME = 'bert-base-multilingual-cased'
      self.__tokenizer = BertTokenizer.from_pretrained(MODEL_NAME, do_lower_case=False)

    elif model_type == "distilbert" :
      MODEL_NAME = 'distilbert-base-multilingual-cased'
      self.__tokenizer = DistilBertTokenizer.from_pretrained(MODEL_NAME, do_lower_case=False)

    else :
      MODEL_NAME = 'bert-base-multilingual-cased'
      self.__tokenizer = BertTokenizer.from_pretrained(MODEL_NAME, do_lower_case=False)
      if model_type == "no-tuning-bert-labelling" :
        MODEL_FILENAME = "model-mbert-labelling-no-tuning.pth"
      elif model_type == "full-fine-tuning-bert-labelling" :
        MODEL_FILENAME = "model-mbert-labelling-full-fine-tuning.pth"
    
    self.__model = torch.load(ROOT_PATH + MODEL_PATH + MODEL_FILENAME).cuda()

  def predict_text(self, text) :
    self.__model.eval()
    result = []
    tokenized_sentence = self.__tokenizer.encode(text)
    if (len(tokenized_sentence) > 512) :
      return None
    input_ids = torch.tensor([tokenized_sentence]).cuda()
    with torch.no_grad():
      output = self.__model(input_ids)
    label_indices = np.argmax(output[0].to('cpu').numpy(), axis=2)

    # Join Split Token
    tokens = self.__tokenizer.convert_ids_to_tokens(input_ids.to('cpu').numpy()[0])
    new_tokens, new_labels = [], []
    
    # Initialize Variables for XLM-R Join Token
    result_token = ""
    result_label = None
    
    for token, label_idx in zip(tokens, label_indices[0]):
      if "xlmr" in self.__model_type :
        if token.startswith("▁"):
          if result_token != "" :
            new_labels.append(result_label)
            new_tokens.append(result_token)
          result_token = token[1:]
          result_label = self.__tag_values[label_idx -1]
        else:
          result_token += token
      elif "bert" in self.__model_type :
        if token.startswith("##"):
          new_tokens[-1] = new_tokens[-1] + token[2:]
        else:
          new_labels.append(self.__tag_values[label_idx - 1])
          new_tokens.append(token)
    for token, label in zip(new_tokens, new_labels):
      elmt = {}
      elmt['token'] = token
      elmt['label'] = label
      result.append(elmt)
    # Remove [CLS] for mbert and distilbert, and <s> for xlmr
    del result[0]

    # Remove [SEP] for mbert and distilbert
    if "bert" in self.__model_type : 
      del result[-1]
    return result

  def predict(self, texts) :
    result = {}
    tokens_labels = []
    count = 0
    for idx, text in enumerate(texts) :
      result = predict_text(self,text)
      if result != None :
        tokens_labels.append(predict_text(self,text))
      else :
        count += 1
    result['tokens_labels'] = tokens_labels
    print ('Skipped text', count)
    return result