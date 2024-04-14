import logging

choice_list = ["hallway", "bathroom", "bedroom", "garden", "kitchen", "office"]
stop_token = '&'
midstop_token = '$'
import re
def inserttoStr(text,target,insert_text):
    index = text.find(target)
    if index != -1:
        newline_index = text.find('\n', index)
        if newline_index != -1:
            modified_text = text[:newline_index] + insert_text + text[newline_index:]
            return modified_text
        else:
            return insert_text + "\n" + text
    else:
        return insert_text + "\n" + text

def findAnswerChain(text):
    pattern = r'chain-(\d+)'
    match = re.search(pattern, text)
    if match:
        number = match.group(1)
        return number
    else:
        return 0
def time_change(run_time):
    hours = int(run_time / 3600)
    minutes = int((run_time % 3600) / 60)
    seconds = int(run_time % 60)

    time_format = "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)
    return time_format

def truncate_line(input_string):
    if stop_token in input_string:
        substrings = input_string.split(stop_token)
        return substrings[0]
    substrings = input_string.split("\n")
    if substrings:
        return substrings[0]
    else:
        return input_string
def truncate_string(input_string):
    if stop_token in input_string:
        substrings = input_string.split(stop_token)
        return substrings[0]
    substrings = input_string.split("\n\n")
    if substrings:
        return substrings[0]
    else:
        return input_string
def truncate_triple(input_string):
    if stop_token in input_string:
        substrings = input_string.split(stop_token)
        return substrings[0]
    substrings = input_string.split("\n\n\n")
    if substrings:
        return substrings[0]
    else:
        return input_string
def findstep(input_string, numstep):
    reasontext = ""
    sentences_list = input_string.split(midstop_token)
    # for i in range(numstep+1):
    #     reasontext += sentences_list[i] + midstop_token
    # reasontext = reasontext[:len(reasontext)-1]
    return sentences_list[0]
def find_value_score(string):
    # parts = string.split("Judgement: ")
    # if len(parts) == 2:
    #     judgetxt = parts[1]
    # else:
    #     judgetxt = ""
    parts = string.split(" ")
    judgetxt = parts[-1]
    choice_list = ["Impossible","Highly unlikely","Unlikely","Doubtful","Uncertain","Likely","Probable","Very likely","Almost certain","Absolutely certain"]
    last_tag = "Doubtful"
    score = 3
    for t in range(len(choice_list)):
        tag = choice_list[t]
        if tag.lower() == judgetxt.lower():
            last_tag = tag
            score = t
            break
    return last_tag,score
def get_last_sentence(text):
    # 通过正则表达式查找句子结尾的标点符号或换行符
    pattern = r'[.!?]+\s*$|\n\s*$'
    match = re.search(pattern, text[::-1])  # 反转字符串并匹配
    if match:
        last_sentence = match.group()[::-1].strip()  # 反转并去除首尾空白字符
        return last_sentence
    else:
        return None
def find_last_tag(string):
    choice_list = ["hallway", "bathroom", "bedroom", "garden", "kitchen", "office"]
    last_tag = None
    for tag in choice_list:
        if tag in string:
            if last_tag is None or string.rfind(tag) > string.rfind(last_tag):
                last_tag = tag
    return last_tag
def find_first_substring(str1, strlist):
    for substring in strlist:
        if substring in str1:
            return substring
    return None
def findcoAns(prosstext):
    # prosstext = get_last_sentence(prosstext)
    words = prosstext.split()
    result = None
    if "in" in words:
        index = words.index("in")  # 找到"in"所在的位置
        if index+2<len(words):
            if words[index+1] == "the":  # 判断下一个单词是否为"the"
                result = words[index+2]  # 如果是，返回它后面的单词
    if "at" in words:
        index = words.index("at")  # 找到"in"所在的位置
        if index + 2 < len(words):
            if words[index+1] == "the":  # 判断下一个单词是否为"the"
                result = words[index+2]  # 如果是，返回它后面的单词
    if result not in choice_list:
        result = find_first_substring(prosstext,choice_list)
    return result
def removeBefore(input_string):
    # 找到最后一个'before'后面的部分
    before_index = input_string.rfind('before')
    if before_index != -1:
        result_string = input_string[:before_index]
    else:
        result_string = input_string
    return result_string
def rmAfterTherefore(input_string):
    # 找到最后一个'before'后面的部分
    before_index = input_string.rfind('Therefore')
    if before_index != -1:
        result_string = input_string[before_index:]
    else:
        result_string = input_string
    return result_string
def findanswer(resp,datatype):
    resp = rmAfterTherefore(resp)
    if datatype=='bAbI':
        resp = removeBefore(resp)
        res = findcoAns(resp)
        if res:
            return res
        else:
            finalans = find_last_tag(resp)
            return finalans
    elif datatype=='stgq':
        res = findcoAns(resp)
        if res:
            return res
        else:
            finalans = find_last_tag(resp)
            return finalans
    else:
        answerlist = ['unknow','true','false']
        if answerlist[0] in resp.lower():
            return 'Unknown'
        elif answerlist[1] in resp.lower():
            return 'True'
        elif answerlist[2] in resp.lower():
            return 'False'
        else:
            return 'wrong type'
def chainReco(question_word,linelist,chaindep):
    sort_list = []
    for ind in range(len(chaindep)):
        show_num = 0
        all_num = 0
        chainlist = chaindep[ind]
        for cid in chainlist:
            all_num += len(linelist[cid])
            for qword in question_word:
                if qword in linelist[cid]:
                    show_num += 1
        score = show_num/all_num
        sort_list.append(score)
    sorted_indices = sorted(range(len(sort_list)), key=lambda k: sort_list[k], reverse=True)
    chaindep_list = [chaindep[i] for i in sorted_indices]
    return chaindep_list
def chaintocontext(linelist,chaindep):
    context = ""
    for ind in range(len(chaindep)):
        chainlist = chaindep[ind]
        context += "\nchain-"+str(ind)+":\n"
        for cid in chainlist:
            context += linelist[cid] + "\n"
    return context
def have_common_elements(arr1, arr2):
    set1 = set(arr1)
    set2 = set(arr2)
    common_elements = set1.intersection(set2)
    return common_elements