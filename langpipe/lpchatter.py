import json
from ollama import chat
from .lpnode import LPNode, LPNodeType

class LPChatter(LPNode):
    """
    chat with LLM based on Ollama, supporting chat histories which is different from text generation.
    access `lpdata['global_vars']['chatted_text']` to get the chat text.
    """
    def __init__(self, name, model='minicpm-v:8b') -> None:
        super().__init__(name, LPNodeType.LLM, model)
        self.__chatted_text = None

    def _handle(self, lpdata) -> None:
        # convert query to json object something like: [{'role': 'user', 'content': 'Hello, how are you?'}, {...}, {...}]
        messages_from_query = json.loads(lpdata['query'])
        response = chat(model=self.model, 
                        messages=messages_from_query,
                        options={
                            'top_k': 100,
                            'temperature': 0.8
                        })
        # take care <think>...</think> in some reason models
        self.__chatted_text = response['message']['content']

        # update records
        messages = lpdata['records'][-1]['messages']
        messages.extend(messages_from_query)

        message = {}
        message['role'] = 'assistant'
        message['content'] = response['message']['content']
        messages.append(message)
    
    def _after_handle(self, lpdata) -> None:
        super()._after_handle(lpdata)

        # update global variables
        lpdata['final_out'] = self.__chatted_text
        lpdata['global_vars']['chatted_text'] = self.__chatted_text