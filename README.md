# :bulb: MindMap: Constructing Evidence Chains for Multi-Step Reasoning in Large Language Models
## :star: Abstract
Large language models (LLMs) have demonstrated remarkable performance across a range of natural language processing (NLP) tasks. 
However, they encounter significant challenges in automated reasoning, especially in multi-step reasoning scenarios.
In order to solve complex reasoning problems, LLMs need to perform faithful multi-step reasoning based on a given set of facts and rules. 
A lot of work has focused on guiding LLMs to think logically by generating reasoning paths, but ignores the relationship among available facts.
In this paper, we introduce MindMap, a straightforward yet powerful approach for constructing evidence chains to support reasoning in LLMs.
An evidence chain refers to a set of facts that are associated with the same subject.
In this way, we can organize related facts together to avoid missing relevant information. 
MindMap can seamlessly integrate with existing reasoning frameworks, such as Chain-of-Thought (CoT) and Selection-Inference (SI), by enabling the model to generate and select relevant evidence chains from independent facts. The experimental results on the bAbI and ProofWriterOWA datasets demonstrate the effectiveness of MindMap. 
Our approach can significantly enhance the performance of CoT and SI, particularly in multi-step reasoning tasks. 
## :bell: Overview
The main framework of the proposed MindMap approach.

![fig1](./img/paperpic1.pdf)

![fig2](./img/paperpic2.pdf)

The figure above the head illustrates the MindMap's workflow for answering a question from the bAbI dataset, comprising three modules: evidence chain construction, summarization, and utilization for reasoning. 
**Evidence chain construction**:To construct these chains, we deploy the Evidence Chain Construction module. This involves creating subjects using entity extraction and dependency parsing from the Stanford CoreNLP toolkit. We then form an evidence chain for each subject by collating facts that include the specific subject.
**Evidence chain summarization**: evidence chains vary in length. To achieve brevity, we introduce an evidence chain summarization module. It guides a Large Language Model to generate summaries focusing on key entities in each chain.
**Evidence chain utilization for reasoning**: During inference, we substitute individual facts with these summarized evidence chains for reasoning. This modification doesn't alter the underlying reasoning framework, demonstrating MindMap's compatibility with various reasoning approaches.
## :thumbsup: Paper and Citation
More technical details can be found in our [paper](https://ojs.aaai.org/index.php/AAAI/article/view/29896/31566).

If you find MindMap useful or relevant to your project and research, please kindly cite our paper:
```
@inproceedings{wu2024mindmap,
  title={MindMap: Constructing Evidence Chains for Multi-Step Reasoning in Large Language Models},
  author={Wu, Yangyu and Han, Xu and Song, Wei and Cheng, Miaomiao and Li, Fei},
  booktitle={Proceedings of the AAAI Conference on Artificial Intelligence},
  volume={38},
  number={17},
  pages={19270--19278},
  year={2024}
 }
```
