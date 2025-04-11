import json
from ollama import generate
from .lpnode import LPNode, LPNodeType

class LPAggregator(LPNode):
    """
    data aggregation using LLM base on Ollama.
    access `lpdata['global_vars']['aggregated_data']` for the aggregated data.
    """
    def __init__(self, name, aggregate_desc=None, model='minicpm-v:8b') -> None:
        super().__init__(name, LPNodeType.LLM, model)
        self.__aggregate_desc = aggregate_desc
        self.__aggregated_data = None
        self.__aggregate_prompt_template = """
        你是一个智能信息聚合器（Aggregator），负责整合多个来源的信息，并基于所有可用数据生成高质量、清晰且有逻辑性的最终回答。
        以下是所有可用的信息：
        ---
        {0}
        ---

        以下是待回答的问题：
        ---
        {1}
        ---

        任务要求：
        1. **信息整合**：充分利用所有来源的数据，确保信息完整，不遗漏任何重要内容。
        2. **语义流畅**：避免直接罗列数据，而是用自然语言组织，使回答清晰易懂。

        请给出最终整合后的完整回答：
        """

    def _handle(self, lpdata) -> None:
        query = lpdata['query'] if self.__aggregate_desc is None else self.__aggregate_desc
        prompt = self.__aggregate_prompt_template.format(json.dumps(lpdata['global_vars'], indent=4, ensure_ascii=False), query)

        response = generate(model=self.model, 
                            prompt=prompt,
                            options={
                                'top_k': 1,
                                'temperature': 0.5
                            })
        self.__aggregated_data = response['response']

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

        # update local vars
        record = lpdata['records'][-1]
        record['local_vars']['__aggregate_desc'] = self.__aggregate_desc

        # update global variables
        lpdata['final_out'] = self.__aggregated_data
        lpdata['global_vars']['aggregated_data'] = self.__aggregated_data
