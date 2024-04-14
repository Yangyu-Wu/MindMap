import json
import logging

logging.basicConfig(filename='modelrun.log', level=logging.DEBUG)

from transformers import AutoTokenizer, AutoModelForCausalLM, LlamaForCausalLM
import torch
from tqdm import tqdm
import ray
from model_inference import *
from prompt_util import time_change

from llama_cpp import Llama, LlamaCache
import time

class Vicuna():
    @torch.inference_mode()
    def __init__(self):
        model_path = 'vicuna-7b'
        tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=False)
        model = AutoModelForCausalLM.from_pretrained(
            model_path, low_cpu_mem_usage=False, torch_dtype=torch.float16
        ).cuda()
        self.model = model
        self.tokenizer =tokenizer

    def generator(self,text,max_token=512,temperature = 0.1):
        text = text.strip()
        input_ids = self.tokenizer([text]).input_ids
        output_ids = self.model.generate(
            torch.as_tensor(input_ids).cuda(),
            do_sample=True,
            temperature=temperature,
            max_new_tokens=max_token,
        )
        output_ids = output_ids[0][len(input_ids[0]):]
        outputs = self.tokenizer.decode(output_ids, skip_special_tokens=True).strip()
        return outputs

class AlpacaModel:
    def __init__(self):
        self.initialized = False

    @classmethod
    def from_pretrained(self, path):
        result = self()

        cache_capacity = 0

        params = {
            'model_path': str(path),
            'n_ctx': 4096,
            'seed': 0
        }
        self.model = Llama(**params)
        return result, result

    def encode(self, string):
        if type(string) is str:
            string = string.encode()
        return self.model.tokenize(string)

    def generator(self, context="", max_token=512, temperature=0.1, top_p=1, top_k=50, repetition_penalty=1, mirostat_mode=0, mirostat_tau=5, mirostat_eta=0.1, callback=None):
        context = context.strip()
        context = context if type(context) is str else context.decode()
        completion_chunks = self.model.create_completion(
            prompt=context,
            max_tokens=max_token,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            repeat_penalty=repetition_penalty,
            mirostat_mode=int(mirostat_mode),
            mirostat_tau=mirostat_tau,
            mirostat_eta=mirostat_eta,
            stream=True
        )
        output = ""
        for completion_chunk in completion_chunks:
            text = completion_chunk['choices'][0]['text']
            output += text
            if callback:
                callback(text)
        return output


if __name__ == '__main__':
    datatype = 'bAbI'
    dataindex = 3
    stratage = 'CoT'
    model_type = 'vicuna'
    mind_map = False
    unknow_data = True
    babi_num = [3,2,1]
    pw_num = [5,3,2,1,0]
    start_time = time.time()
    logging.info('************************************')
    if model_type == 'alpaca':
        logging.info('loading Alpaca......')
        model_path = 'alpaca-13b/ggml-alpaca-7b-q4.bin'
        model,tokenizer = AlpacaModel().from_pretrained(model_path)
        logging.info('Alpaca complete!!!')
    elif model_type == 'vicuna':
        logging.info('loading Vicuna......')
        model = Vicuna()
        logging.info('Vicuna complete!!!')
    logging.info('loading dataset......')
    logging.info('Evaluation begining.....')
    end_time = time.time()
    chargetime = time_change(end_time - start_time)
    logging.info(model_type + "model charging time：")
    logging.info(chargetime)
    start_time = time.time()
    if datatype == 'bAbI':
        for num in babi_num:
            if not mind_map:
                operate_Predict(model, 'Vallina', datatype, dataindex, mind_map, unknow_data)
            operate_Predict(model, 'CoT', datatype, dataindex, mind_map, unknow_data)
            operate_Predict(model, 'SI', datatype, dataindex, mind_map, unknow_data)
    elif datatype == 'pW':
        for num in pw_num:
            if not mind_map:
                operate_Predict(model, 'Vallina', datatype, dataindex, mind_map, unknow_data)
            operate_Predict(model, 'CoT', datatype, dataindex, mind_map, unknow_data)
            operate_Predict(model, 'SI', datatype, dataindex, mind_map, unknow_data)
    end_time = time.time()
    runtime = time_change(end_time - start_time)
    logging.info(model_type + "model in '"+stratage+"' stratage running time：")
    logging.info(runtime)