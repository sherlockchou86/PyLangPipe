
from ollama import generate
from .lpnode import LPNode, LPNodeType


class LPGenerator(LPNode):
    """
    text generation using LLM based on Ollama.
    access `lpdata['global_vars']['generated_txt']` to get generated text.
    """

    def __init__(self, name, model='minicpm-v:8b') -> None:
        super().__init__(name, LPNodeType.LLM, model)
        self.__generated_txt = None
    
    def _handle(self, lpdata) -> None:
        query = lpdata['query']
        query_imgs = lpdata['query_imgs']
        response = generate(model=self.model, 
                            prompt=query,
                            images=query_imgs,
                            options={
                                'top_k': 100,
                                'temperature': 0.8
                            })
        # take care <think>...</think> in some reason models
        self.__generated_txt = response['response']

        # update records
        messages = lpdata['records'][-1]['messages']
        message = {}
        message['role'] = 'user'
        message['content'] = query
        messages.append(message)

        message = {}
        message['role'] = 'assistant'
        message['content'] = response['response']
        messages.append(message)
    
    def _after_handle(self, lpdata) -> None:
        super()._after_handle(lpdata)
    
        # update global variables
        lpdata['final_out'] = self.__generated_txt
        lpdata['global_vars']['generated_txt'] = self.__generated_txt