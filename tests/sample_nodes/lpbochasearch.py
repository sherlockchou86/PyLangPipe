import json
import requests
from langpipe import LPBaseInvoker

class LPBoChaSearch(LPBaseInvoker):
    """
    web/ai search online using BoCha search service.
    access `lpdata['global_vars']['searched_result']` for the searched result.
    """
    def __init__(self, name, api_key, api_url='https://api.bochaai.com/v1/web-search', ai_search=False) -> None:
        super().__init__(name)
        self.__api_key = api_key
        self.__api_url = api_url
        self.__is_ai_search = ai_search

        self.__search_keywords = None
        self.__search_count = 10
        self.__search_result = None
    
    def _invoke(self, lpdata) -> None:
        self.__search_keywords = lpdata['query']

        if not self.__is_ai_search:
            ret, result = self.__web_search()
            if ret:
                self.__search_result = result
        else:
            ret, result = self.__ai_search()
            if ret:
                self.__search_result = result
    
    def _after_handle(self, lpdata) -> None:
        super()._after_handle(lpdata)

        # update local variables
        record = lpdata['records'][-1]
        record['local_vars']['__api_key'] = self.__api_key
        record['local_vars']['__api_url'] = self.__api_url
        record['local_vars']['__search_keywords'] = self.__search_keywords
        record['local_vars']['__search_count'] = self.__search_count
        record['local_vars']['__ai_search'] = self.__is_ai_search

        # update global variables
        if self.__search_result is not None:
            lpdata['final_out'] = self.__search_result
            lpdata['global_vars']['searched_result'] = self.__search_result
    
    def __web_search(self) -> tuple[int, str]:
        headers = {
            'Authorization': f'Bearer {self.__api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            "query": self.__search_keywords,
            "freshness": "noLimit",
            "summary": True,
            "count": self.__search_count
        }

        response = requests.post(self.__api_url, headers=headers, json=data)
        if response.status_code == 200:
            json_response = response.json()
            try:
                if json_response["code"] != 200 or not json_response["data"]:
                    return 0, f"搜索API请求失败，原因是: {response.msg or '未知错误'}"
                
                webpages = json_response["data"]["webPages"]["value"]
                if not webpages:
                    return 0, "未找到相关结果。"
                formatted_results = ""
                for idx, page in enumerate(webpages, start=1):
                    formatted_results += (
                        f"[[引用: {idx}]]\n"
                        f"标题: {page['name']}\n"
                        f"URL: {page['url']}\n"
                        f"摘要: {page['summary']}\n"
                        f"内容详细: {page['snippet']}\n"
                        f"网站名称: {page['siteName']}\n"
                        f"网站图标: {page['siteIcon']}\n"
                        f"发布时间: {page['dateLastCrawled']}\n\n"
                    )
                return 1, formatted_results.strip()
            except Exception as e:
                return 0, f"搜索API请求失败，原因是：搜索结果解析失败 {str(e)}"
        else:
            return 0, f"搜索API请求失败，状态码: {response.status_code}, 错误信息: {response.text}"
    

    def __ai_search(self) -> tuple[int, str]:
        pass