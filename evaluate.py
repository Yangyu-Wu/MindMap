import stanza
import json
import re
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

nlp = stanza.Pipeline('en', processors='tokenize', download_method=None)

def is_list_contained(full_list, sublist):
    return set(sublist).issubset(set(full_list))

def draw_heat_map(wswa, wsra,rswa, rsra):
    data = [[wswa, wsra], [rswa, rsra]]
    print(data)
    sns.heatmap(data, annot=True, fmt='d', cmap='Blues')
    plt.title('bAbI-task3')
    plt.ylabel('Selection Label')
    plt.xlabel('Answer Label')
    plt.show()
    plt.savefig('bAbI-3_SA.png')

def count_token_num(text):
    tokens = nlp(text)
    total_tokens = 0
    for sentence in tokens.sentences:
        total_tokens += len(sentence.tokens)
    return total_tokens


def has_at_least_two_common_words(str1, str2):
    str1 = str1.replace(',', ' ').replace('.', ' ')
    str2 = str2.replace(',', ' ').replace('.', ' ')
    split_by_comma = str1.split(',')
    words1 = [item.split(' ') for item in split_by_comma]
    split_by_comma = str2.split(',')
    words2 = [item.split(' ') for item in split_by_comma]

    word_set1 = set([element for sublist in words1 for element in sublist])
    word_set2 = set([element for sublist in words2 for element in sublist])
    word_set1 = {word for word in word_set1 if len(word) > 3}
    word_set2 = {word for word in word_set2 if len(word) > 3}

    common_words = word_set1.intersection(word_set2)
    return len(common_words) >= 2

def analyse_Evidence_Chain_Construction(result_path):
    with open(result_path, "r") as f:
        json_data = json.load(f)
    compnum = 0
    total = 0
    for j in range(len(json_data)):
        group = json_data[j]['main_chain']
        suplist = json_data[j]['support_list']
        complit_flag = False
        chain_num = 0
        for gitem,chainlist in group.items():
            if is_list_contained(chainlist,suplist):
                complit_flag = True
                json_data[j]['rightchain'] = {'num':chain_num,'key':gitem,'chlist':chainlist}
                break
            chain_num += 1
        if complit_flag:
            compnum += 1
        total += 1
    print(compnum)
    print(total)
    print(compnum/total)
    print(json_data[4])

def analyse_Evidence_Chain_Summarization_tokens(result_path):
    with open(result_path, "r") as f:
        json_data = json.load(f)
    orign_token = 0
    sum_token = 0
    for j in range(len(json_data)):
        doc_item = json_data[j]
        text = " ".join(doc_item['linelist'])
        orign_token += count_token_num(text)
        sum_token += count_token_num(doc_item['subject_chain'])
    print(orign_token)
    print(sum_token)
    print((orign_token - sum_token) / orign_token)

def analyse_Evidence_Chain_Summarization_correctness(result_path):
    with open(result_path, "r") as f:
        json_data = json.load(f)
    countRight = 0
    countall = 0
    for j in range(len(json_data)):
        doc_item = json_data[j]
        if 'subject_chain' not in doc_item:
            continue
        strtext = doc_item["subject_chain"]
        strlist = strtext.split("\n")
        linelist = doc_item["linelist"]
        oindex = 0
        for key, valuelist in doc_item['main_chain'].items():
            sumtext = strlist[oindex]
            chainlist = []
            if key in sumtext:
                count = 0
                for vi in valuelist:
                    time_info = re.findall(r't=(\d+)', linelist[vi])
                    # text_without_time = re.sub(r'\(t=\d+\)', '', sumtext)
                    text_without_time = re.sub(r"\[.*?\]|\(.*?\)", "", sumtext)
                    text_without_time = text_without_time[8:]
                    # if 't='+time_info[0] in sumtext:
                    if has_at_least_two_common_words(text_without_time, linelist[vi]):
                        count += 1
                    else:
                        break
                if count == len(valuelist):
                    countRight += 1
            countall += 1
            oindex += 1
    print(countRight)
    print(countall)

def analyse_chain_to_answer(baseline_result_path,result_path):
    with open(result_path, "r") as f:
        json_data = json.load(f)
    with open(baseline_result_path, "r") as f:
        sumresult_data = json.load(f)
    sumresult_data = sumresult_data['answer']
    wswa = 0
    wsra = 0
    rsra = 0
    rswa = 0
    for j in range(len(json_data)):
        rchain = json_data[j]['rightchain']
        fresp = sumresult_data[j]['final_resp']
        if 'chain-' + str(rchain['num']) in fresp and rchain['key'] in fresp:
            if sumresult_data[j]['answer'] == sumresult_data[j]['true_label']:
                rsra += 1
            else:
                rswa += 1
        else:
            if sumresult_data[j]['answer'] == sumresult_data[j]['true_label']:
                wsra += 1
            else:
                wswa += 1
    print("Wrong Selection Wrong Answer:", wswa)
    print("Wrong Selection Right Answer:", wsra)
    print("Right Selection Right Answer:", rsra)
    print("Right Selection Wrong Answer:", rswa)
    draw_heat_map(wswa, wsra, rswa, rsra)
def calculate_accuracy(result_path):
    with open(result_path, "r") as f:
        json_data = json.load(f)
    acc = 0
    total = 0
    for i in range(len(json_data)):
        jitem = json_data[i]
        if jitem['answer']:
            if jitem['answer'].lower() == jitem['true_label'].lower():
                    acc+=1
        total += 1
    print("Accuracy: ",acc/total)

if __name__ == '__main__':
    # Please fill in the path of the result file
    result_path = ''
    calculate_accuracy(result_path)
    # analyse_Evidence_Chain_Construction(result_path)
    # analyse_Evidence_Chain_Summarization_tokens(result_path)
    # analyse_Evidence_Chain_Summarization_correctness(result_path)
    # analyse_chain_to_answer(baseline_result_path, result_path)