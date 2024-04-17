import json
import logging
from prompt_util import *
from data_loader import *
import re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, LlamaForCausalLM
from llama_cpp import Llama, LlamaCache
insr3 = "Below are some places where people moved or items they carried. Please summarize based on the examples!\n"

class Vicuna():
    @torch.inference_mode()
    def __init__(self):
        model_path = '../wyy/vicuna-7b'
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

def summaries_ablation(model,datatype,dataindex):
    jsondoc = load_data(datatype, dataindex, 'origin_data')
    for i in range(len(jsondoc)):
        context = jsondoc[i]['text'] + "Request: Write a summary of each chain!\nSummary:"
        prompt = load_prompt('', datatype, dataindex, 'ablation') + context
        resp = model.generator(prompt, 512)
        smllm = truncate_string(resp)
        jsondoc[i]['ablation_summarized'] = smllm
    with open('data/ablation/bAbI-task' + str(dataindex) + '.json', "w") as f:
        json.dump(jsondoc, f)

def summerize_chain(model,datatype,dataindex):
    jsondoc = load_data(datatype,dataindex,'consturct_data')
    for i in range(len(jsondoc)):
        docitem = jsondoc[i]
        line_list = docitem['linelist']
        question = docitem['question']
        group = docitem['main_chain']
        objectchain = docitem['object_chain']
        cindex = 0
        fullchain = ''
        oi = 0
        for gitem, chainlist in group.items():
            if len(chainlist) > 0 and gitem != 'others':
                context = 'chain-' + str(cindex) + ':'
                orthercontext = 'Entity about '+ gitem + ':'
                for li in chainlist:
                    context += line_list[li] + '\n'
                    for gitem1, chainlist1 in objectchain.items():
                        if len(chainlist1) > 0 and gitem1 != 'others':
                            if li in chainlist1:
                                orthercontext += gitem1 + ','
                orthercontext = orthercontext[:len(orthercontext)-1]
                orthercontext += '\n'
                cindex += 1
                sum_context = insr3 + context + orthercontext + '\nSummary:'
                prompt = load_prompt('', datatype, dataindex, 'consturction') + sum_context
                resp = model.generator(prompt, 512)
                chain_sum = truncate_string(resp)
                fullchain += chain_sum + '\n'
                oi += 1
        jsondoc[i]['subject_chain'] = fullchain
    if datatype == 'bAbI':
        with open('data/summerized_data/bAbI/bAbI-task' + str(dataindex) + '.json', "w") as f:
            json.dump(jsondoc, f)
    else:
        with open('data/summerized_data/proofWriter/depth-' + str(dataindex) + '.json', "w") as f:
            json.dump(jsondoc, f)
if __name__ == '__main__':
    babi_num = [3, 2, 1]
    pw_num = [5, 3, 2, 1, 0]
    model = Vicuna()
    for num in babi_num:
        summerize_chain(model,'bAbI', num)
    for num in pw_num:
        summerize_chain(model,'proofWriter', num)