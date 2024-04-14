import time
from data_loader import *
from prompt_util import *
from datetime import datetime
import copy

def model_inference(jsonitem,model,strategies,datatype,dataindex,mind_map):
    save_item = {}
    save_item['mid_out'] = []
    if strategies == 'Vallina' or strategies == 'CoT':
        prompt_ex = load_prompt(strategies, datatype, dataindex, mind_map)
        model_input = get_model_input(jsonitem, prompt_ex, strategies, datatype, mind_map)
        resp = model.generator(model_input, 256)

    else:
        for j in range(dataindex):
            prompt_ex = load_prompt('SI-Selection', datatype, dataindex, mind_map)
            model_input = get_model_input(jsonitem, prompt_ex, 'SI-Selection', datatype, mind_map)
            resp = model.generator(model_input, 256)
            selection_fact = truncate_string(resp)

            jsonitem['selected_evidence'] = selection_fact
            prompt_ex = load_prompt('SI-Inference', datatype, dataindex, mind_map)
            model_input = get_model_input(jsonitem, prompt_ex, 'SI-Inference', datatype, mind_map)
            resp = model.generator(model_input, 128)
            newfact = truncate_line(resp)
            save_item['mid_out'].append(newfact)
            if mind_map:
                chainnum = findAnswerChain(selection_fact)
                jsonitem['subject_chain'] = inserttoStr(jsonitem['subject_chain'], 'chain-' + str(chainnum), newfact)
            else:
                jsonitem['linelist'].append(newfact)
        prompt_ex = load_prompt('CoT', datatype, dataindex, mind_map)
        model_input = get_model_input(jsonitem, prompt_ex, 'CoT', datatype, mind_map)
        resp = model.generator(model_input)
    final_resp = truncate_string(resp)
    save_item['mid_out'].append(newfact)
    save_item['final_resp'] = final_resp
    last_ans = findanswer(final_resp, datatype)
    save_item['answer'] = last_ans
    save_item['question'] = jsonitem['question']
    save_item['ground_truth'] = jsonitem['answer']
    return save_item

def operate_Predict(model,strategies,datatype,dataindex,mind_map,unknow_data):
    start_time = time.time()
    answer_list = []
    if datatype == 'bAbI':
        num_data = -1
    elif datatype == 'pW' or datatype == 'hotpotqa' or datatype == 'wmh' or datatype == 'stgq':
        num_data = 999
    o = 0
    jsondoc = load_data(datatype,dataindex)
    for k in range(len(jsondoc)):
        jsonitem = jsondoc[k]
        if datatype == 'bAbI':
            save_item = model_inference(jsonitem, model, strategies, datatype, dataindex, mind_map)
            answer_list.append(copy.deepcopy(save_item))
            o+= 1
        elif datatype == 'proofWriter':
            for l in range(len(jsonitem['questions'])):
                if not unknow_data:
                    if jsonitem['answers'][l] == 'Unknown':
                        continue
                jsonitem['question'] = jsonitem['questions'][l]
                jsonitem['answer'] = jsonitem['answers'][l]
                save_item = model_inference(jsonitem, model, strategies, datatype, dataindex, mind_map)
                answer_list.append(copy.deepcopy(save_item))
                o += 1
        if o > num_data and num_data != -1:
            break
    end_time = time.time()
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    run_time = end_time - start_time
    hours = int(run_time // 3600)
    minutes = int((run_time % 3600) // 60)
    seconds = int(run_time % 60)
    save_obj = {'datatype': datatype + str(dataindex),
                'nowTime': formatted_time, 'run_time': f"{hours:02}:{minutes:02}:{seconds:02}", 'answer': answer_list}
    with open('result/' + datatype + '_' + str(dataindex) + '_' + strategies + 'mindmap' if mind_map else '' + '_' + str(num_data) + '_' + 'unknow_data' if unknow_data else '' + '.json', "w") as f:
        json.dump(save_obj, f)