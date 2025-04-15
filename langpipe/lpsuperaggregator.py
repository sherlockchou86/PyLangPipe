import json
import re
from ollama import generate
from .lpnode import LPNode, LPNodeType

class LPSuperAggregator(LPNode):
    """
    data aggregation using LLM based on Ollama, which able to list reference sources from context.
    access `lpdata['global_vars']['aggregated_data']` for the aggregated data with json format.

    NOTE: this node is also able to convert aggregated data into html format with reference links clickable, which can be used to render the data into a web page directly.
    """
    def __init__(self, name, aggregate_desc=None, to_html=False, model='minicpm-v:8b') -> None:
        super().__init__(name, LPNodeType.LLM, model)
        self.__aggregate_desc = aggregate_desc
        self.__to_html = to_html
        self.__aggregated_data = None
        self.__aggregate_prompt_template = """
        你是一个强大的智能信息聚合助手（Aggregator），擅长根据上下文信息，结合自己的理解、生成有引用标注的回答。
        以下是可供参考的上下文：
        ---
        {0}
        ---

        以下是待回答的问题：
        ---
        {1}
        ---

        请注意以下任务要求：
        1. 回答正文中如有引用某些具体数据、事实、日期、标准、文档结论等内容，请在该信息后添加引用占位符（如 `[1]`、`[2]` 等）。
        2. 按顺序列出这些引用编号所对应的来源（可以是网址、文档路径、书名等），来源不可重复。引用编号顺序必须与正文中使用的一致。

        重点注意：
        1. **信息整合**：充分利用所有来源的数据，确保信息完整，不遗漏任何重要内容。
        2. **语义流畅**：避免直接罗列数据，而是用自然语言组织，使回答清晰易懂。
        
        注意最终要以JSON格式输出：
        {{
            "content": "回答正文，包含引用占位符[1][2][N]……",
            "references": [
                "对应的引用来源1",
                "对应的引用来源2",
                "对应的引用来源N"
            ]
        }}

        现在给出你的回答：
        """

    def _handle(self, lpdata) -> None:
        query = lpdata['query'] if self.__aggregate_desc is None else self.__aggregate_desc
        prompt = self.__aggregate_prompt_template.format(json.dumps(lpdata['global_vars'], indent=4, ensure_ascii=False), query)
        response = generate(model=self.model, 
                            prompt=prompt,
                            format='json',
                            options={
                                'top_k': 1,
                                'temperature': 0.5,
                                'num_ctx': 32768 # 32K
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
        record['local_vars']['__to_html'] = self.__to_html

        # update global variables
        if self.__to_html:
            self.__aggregated_data = self.__convert_html()   # convert to html with reference links clickable 
        lpdata['final_out'] = self.__aggregated_data
        lpdata['global_vars']['aggregated_data'] = json.loads(self.__aggregated_data)
    
    def __convert_html(self) -> str:
        data = json.loads(self.__aggregated_data)
        content = data["content"]
        links = data["references"]

        def replace(match):
            num = int(match.group(1))
            index = num - 1
            if 0 <= index < len(links):
                url = links[index]
                return f'<a href="{url}" target="_blank">[{num}]</a>'
            else:
                return match.group(0)

        html_content = re.sub(r'\[(\d+)\]', replace, content)
        data['content'] = html_content
        return json.dumps(data, indent=4, ensure_ascii=False)
