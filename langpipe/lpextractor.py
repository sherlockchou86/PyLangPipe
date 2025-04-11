import json
import re
from ollama import generate
from .lpnode import LPNode, LPNodeType

class LPExtractor(LPNode):
    """
    parameters extraction using LLM based on Ollama.
    access `lpdata['global_vars']['extracted_params']` to get the values of extracted parameters.
    """
    
    def __init__(self, name, params_desc:dict[str,str], model='minicpm-v:8b') -> None:
        super().__init__(name, LPNodeType.LLM, model)
        self.__params_desc = params_desc
        self.__extracted_params = None
        self.__extract_prompt_template = """
        你是一个强大的参数提取助手，能够根据用户定义的参数名称和描述，从给定文本中提取相关参数值。  
        以下是用户定义的参数名称和描述：
        {0}

        任务要求：
        1. 请从用户提供的文本中，依据定义的参数名称和描述，提取出相应的参数值。
        2. 有些参数值可能无法直接获取，需要你从上下文中推断参数值。
        3. 若提取成功，请输出以JSON格式呈现，key为参数名，value为提取的参数值。
        4. 如果某个参数无法从文本中提取到，请将其值设为null。
        5. 输出JSON中的参数名称、顺序以及数量必须与用户给定的参数定义完全一致。
        6. 输出仅包含纯粹的JSON数据，不要包含任何额外字符、标点或说明文字。

        待提取参数值的文本为：
        "{1}"

        请输出提取到的结果（JSON格式）：
        """
    
    def _handle(self, lpdata) -> None:
        query = lpdata['query']
        prompt = self.__extract_prompt_template.format(json.dumps(self.__params_desc, indent=4, ensure_ascii=False), query)

        response = generate(model=self.model, 
                            prompt=prompt,
                            options={
                                'top_k': 1,
                                'temperature': 0.5
                            })
        # in case <think>...</think> in some reason models
        self.__extracted_params = re.sub(r"<think>.*?</think>", "", response['response'], flags=re.DOTALL)

        # update records
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
        
        # update local variables
        record = lpdata['records'][-1]
        record['local_vars']['__params_desc'] = json.dumps(self.__params_desc, indent=4, ensure_ascii=False)

        # update global variables
        lpdata['final_out'] = self.__extracted_params
        lpdata['global_vars']['extracted_params'] = json.loads(self.__extracted_params)
