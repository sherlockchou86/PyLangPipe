
import threading
import json
from ollama import generate
from .lpnode import LPNode, LPNodeType


class LPClassifier(LPNode):
    """
    task classification using LLM based on Ollama.
    access `lpdata['global_vars']['cls_label']` to get the classification label.
    """
    
    def __init__(self, name, labels_desc:dict[str,str], model='minicpm-v:8b') -> None:
        super().__init__(name, LPNodeType.LLM, model)
        self.__labels_desc = labels_desc
        self.__cls_label_id = -1
        self.__cls_label = None
        self.__cls_prompt_template = """
        你是一个强大的文本分类助手，能够根据用户定义的分类标签对任何文本进行精准分类。
        用户提供的分类标签及其描述如下（JSON 格式）：
        {0}

        请按照以下要求进行文本分类：
        1. 认真阅读待分类的文本，并理解其主要内容。
        2. 根据用户提供的标签及描述，选出最符合该文本内容的分类标签。
        3. 仅返回一个最合适的分类标签，不要输出多余内容。 
        4. 如果文本内容不属于任何分类，直接返回None。

        待分类文本：
        "{1}"

        请直接返回最符合该文本的分类标签（不要用引号包裹标签）：
        """
    
    def _handle(self, lpdata) -> None:
        query = lpdata['query']
        prompt = self.__cls_prompt_template.format(json.dumps(self.__labels_desc, indent=4, ensure_ascii=False), query)

        response = generate(model=self.model, 
                            prompt=prompt,
                            options={
                                'top_k': 1,
                                'temperature': 0.5
                            })
        self.__cls_label = response['response']
        if self.__cls_label in self.__labels_desc:
            self.__cls_label_id = list(self.__labels_desc.keys()).index(self.__cls_label)
        
        # update record
        messages = lpdata['records'][-1]['messages']
        message = {}
        message['role'] = 'user'
        message['content'] = prompt
        messages.append(message)

        message = {}
        message['role'] = 'assistant'
        message['content'] = response['response']
        messages.append(message)
    
    def _after_handle(self, lpdata) -> None:
        super()._after_handle(lpdata)

        # insert local variables
        record = lpdata['records'][-1]
        record['local_vars']['__labels_desc'] = json.dumps(self.__labels_desc, indent=4, ensure_ascii=False)
        record['local_vars']['cls_label_id'] = self.__cls_label_id
        record['local_vars']['cls_label'] = self.__cls_label

        # update global variables
        lpdata['final_out'] = self.__cls_label
        lpdata['global_vars']['cls_label'] = self.__cls_label
    
    def _dispatch(self, lpdata) -> None:
        """
        dispatch lpdata according to the label id.
        """

        # classification fails, disptach lpdata to the last one only if it is end node
        if self.__cls_label_id == -1 and len(self.next_nodes) > 0:
            node = self.next_nodes[-1]
            if node.type == LPNodeType.End:
                if lpdata['sync']:
                    node.run(lpdata)
                else:
                    threading.Thread(target=lambda d: node.run(d), args=(lpdata,)).start()
        
        for i, node in enumerate(self.next_nodes):
            if i == self.__cls_label_id:
                if lpdata['sync']:
                    node.run(lpdata)
                else:
                    threading.Thread(target=lambda d: node.run(d), args=(lpdata,)).start()
                break