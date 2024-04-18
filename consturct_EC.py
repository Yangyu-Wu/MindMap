import stanza
from tqdm import tqdm
from data_loader import *
import copy

def extract_subject(datatype,dataindex):
    doc_data = load_data(datatype,dataindex,'origin_data')
    nlp = stanza.Pipeline('en',download_method=None)
    chain_doc = []
    for j in tqdm(range(len(doc_data))):
        if j > 10 :
            break
        paperitem = doc_data[j]
        text = paperitem['text']
        if datatype == 'bAbI':
            line_list = paperitem['linelist']
        else:
            line_list = paperitem['fact_list']
        main_list = []
        object_list = []
        main_chain = {}
        object_chain = {}
        for i in range(len(line_list)):
            sp = nlp(line_list[i])
            for item in sp.sentences:
                for token in item.tokens:
                    if token.to_dict()[0]['deprel'] == "nsubj":
                        name = token.to_dict()[0]['text']
                        if 't=' in name:
                            continue
                        if name in main_chain:
                            if i not in main_chain[name]:
                                main_chain[name].append(i)
                        else:
                            main_chain[name] = [i]
                    elif token.to_dict()[0]['upos'] == "NOUN":
                        name = token.to_dict()[0]['text']
                        if 't=' in name:
                            continue
                        if name in object_chain and i not in object_chain[name]:
                            if i not in object_chain[name]:
                                object_chain[name].append(i)
                        else:
                            object_chain[name] = [i]
        for k,v in main_chain.items():
            main_list.append(v)
        for k, v in object_chain.items():
            object_list.append(v)
        sequential_array = list(range(0, len(line_list), 1))
        main_chain["others"] = [x for x in sequential_array if all(x not in sublist for sublist in main_list)]
        object_chain["others"] = [x for x in sequential_array if all(x not in sublist for sublist in object_list)]
        paperitem["main_chain"] = main_chain
        paperitem["object_chain"] = object_chain
        chain_doc.append(copy.deepcopy(paperitem))
    if datatype == 'bAbI':
        output_path = './data/consturct_data/bAbI/bAbI-task'+ str(dataindex) + '.json'
    else:
        output_path = './data/consturct_data/proofWriter/depth-' + str(dataindex) + '.json'
    with open(output_path, "w") as f:
        json.dump(chain_doc, f)

if __name__ == '__main__':
    babi_num = [3, 2, 1]
    pw_num = [5, 3, 2, 1, 0]
    for num in babi_num:
        extract_subject('bAbI', num)
    for num in pw_num:
        extract_subject('proofWriter', num)