import json
def load_prompt(strategies,datatype,dataindex,mindmap):
    if mindmap:
        file_path = "prompt/evidenceChain/" + datatype
    else:
        file_path = "prompt/baseline/" + datatype
    if datatype == 'bAbI':
        file_path += "/bAbI-task"+str(dataindex)+"-"+strategies+".txt"
    else:
        file_path += "/proofWriter" + "-" + strategies + ".txt"
    with open(file_path, "r") as file:
        file_content = file.read()
    return file_content


def load_data(datatype,dataindex):
    file_path = "data/processed_data/" + datatype
    if datatype == 'bAbI':
        file_path += "/bAbI-task" + str(dataindex) + ".json"
    else:
        file_path += "/depth-" + str(dataindex) + ".json"
    with open(file_path, "r") as f:
        json_data = json.load(f)
    return json_data

def get_model_input(jsonitem,example_prompt,strategies,datatype,mindmap):
    instruction = "Example-5: Answer the question based on the following evidence chain:\n"
    if mindmap:
        context = jsonitem['subject_chain']
        question = jsonitem['question']
        if strategies == "CoT" or strategies == "SI-Selection":
            prompt = example_prompt + instruction
            if datatype == 'bAbI':
                prompt += 'Context: ' +  context
                prompt += "Question:" + question+"\nAnswer: "
            elif datatype == 'proofWriter':
                rule_text = "Rules: "
                rule_list = jsonitem['rule_list']
                for rule in rule_list:
                    rule_text += rule + " "
                if strategies == "CoT":
                    prompt += context + rule_text + "Does it imply that the statement \"" + question \
                              + "\" is True or False or Unknow?\nReason: The question is \"" + question \
                              + "\". The chain containing "
                elif strategies == "SI-Selection":
                    prompt += context + rule_text + "Does it imply that the statement \"" + question \
                              + "\" is True or False or Unknow?\nReason: "
        elif strategies == "SI-Inference":
            prompt = example_prompt + jsonitem['selected_evidence'] + "Therefore,"
    else:
        question = jsonitem['question']
        context = ''
        for line in jsonitem['linelist']:
            context += line + "\n"
        prompt = example_prompt
        if strategies == "Vallina":
            if datatype == 'bAbI':
                prompt += 'Context: ' + context + 'Question: ' + question
                chooselist = '\nChoice: garden\nChoice: bathroom\nChoice: office\nChoice: kitchen\nChoice: bedroom\nChoice: hallway\n'
                prompt += chooselist + "Answer: "
            elif datatype == 'proofWriter':
                prompt += context + "Does it imply that the statement \"" + question \
                          + "\" is True or False or Unknow?\nAnswer: "
        if strategies == "CoT" or strategies == "SI-Selection":
            prompt = example_prompt
            if datatype == 'bAbI':
                prompt += 'Context: ' + context + 'Question: ' + question
                prompt += "\nReason: "
                prompt += "Question:" + question+"\nAnswer: "
            elif datatype == 'proofWriter':
                prompt += context + "Does it imply that the statement \""+question+"\" is True or False or Unknow? Reason: "
        elif strategies == "SI-Inference":
            prompt = example_prompt + jsonitem['selected_evidence'] + "Therefore,"
    return prompt