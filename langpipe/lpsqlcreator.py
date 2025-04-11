
import re
from ollama import generate
from .lpnode import LPNode, LPNodeType


class LPSQLCreator(LPNode):
    """
    SQL creator using LLM based on Ollama.
    access `lpdata['global_vars']['created_sql']` to get created SQL.
    """
    def __init__(self, name, ddl_desc:str=None, model='minicpm-v:8b') -> None:
        super().__init__(name, LPNodeType.LLM, model)
        self.__ddl_desc = ddl_desc
        self.__created_sql = None
        self.__sql_create_template_prompt = """
        你是一个强大的SQL语句生成助手，专门用于基于数据库的结构来生成SQL查询。
        以下是数据库结构（DDL语句）：
        ---
        {0}
        ---

        任务描述：
        1. 请根据用户输入的问题，生成正确的SQL查询语句。
        2. 你需要确保查询符合数据库的表结构。
        3. 使用SQL语法规范，避免SQL语法错误。
        4. 优先生成可读性高的SQL语句，并适当使用`JOIN`、`WHERE`、`ORDER BY`等。
        5. 如果查询需要聚合数据，请使用`GROUP BY`和适当的聚合函数（如 COUNT、SUM、AVG等）。
        6. 如果问题不明确，你可以假设合理的查询条件。
        7. 输出只包含SQL语句，SQL语句以分号结束，不要包含其他任何解释或注释。
        
        参考示例1：
        用户问题：“查询所有用户的姓名和电子邮件。”
        示例输出：SELECT name, email FROM users;

        参考示例2： 
        用户问题：“获取 2024 年 3 月订单总数。”
        示例输出：SELECT COUNT(*) FROM orders WHERE order_date BETWEEN '2024-03-01' AND '2024-03-31';

        请根据以下用户输入，返回对应的SQL查询：
        ---
        {1}
        ---
        """
    
    def _handle(self, lpdata) -> None:
        query = lpdata['query']
        prompt = self.__sql_create_template_prompt.format(self.__ddl_desc, query)

        response = generate(model=self.model, 
                            prompt=prompt,
                            options={
                                'top_k': 1,
                                'temperature': 0.5
                            })
        # in case <think>...</think> in some reason models
        self.__created_sql = re.sub(r"<think>.*?</think>", "", response['response'], flags=re.DOTALL)
        # no `\n` in sql
        self.__created_sql = self.__created_sql.replace('\n', ' ')

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
        record['local_vars']['__ddl_desc'] = self.__ddl_desc

        # update global variables
        lpdata['final_out'] = self.__created_sql
        lpdata['global_vars']['created_sql'] = self.__created_sql
    
