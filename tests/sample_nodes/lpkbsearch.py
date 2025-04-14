import sqlite3
import faiss
import numpy as np
from ollama import embed # just used for embedding of query text
from langpipe import LPBaseInvoker

class LPKBSearch(LPBaseInvoker):
    """
    search from knowledge base based on faiss which used to save embeddings & sqlite which used to save meta data.
    access `lpdata['global_vars']['kb_searched_result']` for the searched result from knowledge base.
    """
    def __init__(self, name, index_name, db_name) -> None:
        super().__init__(name)

        self.__index_name = index_name
        self.__db_name = db_name
        self.__topk = 10
        self.__embedding_model = 'granite-embedding:278m'
        self.__query = None
        self.__kb_searched_result = None
    
    def _invoke(self, lpdata) -> None:
        self.__query = lpdata['query']
        self.__kb_searched_result = self.__kb_search()
    
    def _after_handle(self, lpdata) -> None:
        super()._after_handle(lpdata)

        # update local variables
        record = lpdata['records'][-1]
        record['local_vars']['__db_name'] = self.__db_name
        record['local_vars']['__index_name'] = self.__index_name
        record['local_vars']['__topk'] = self.__topk
        record['local_vars']['__embedding_model'] = self.__embedding_model
        record['local_vars']['__query'] = self.__query
        
        # update global variables
        if self.__kb_searched_result is not None:
            lpdata['final_out'] = self.__kb_searched_result
            lpdata['global_vars']['kb_searched_result'] = self.__kb_searched_result
    
    def __kb_search(self) -> str:
        index = faiss.read_index(self.__index_name)
        conn = sqlite3.connect(self.__db_name)

        query_vec = embed(model=self.__embedding_model, input=[self.__query])['embeddings']
        D, I = index.search(np.array(query_vec), self.__topk)

        cur = conn.cursor()
        placeholders = ",".join("?" for _ in I[0])
        cur.execute(f"SELECT chunk_text, source_file FROM faiss_meta WHERE id IN ({placeholders})", tuple(map(int, I[0])))
        rows = cur.fetchall()

        search_result = ""
        count = 1
        for idx, row in enumerate(rows, start=1):
            search_result += (
                f"[[引用：{idx}]]\n"
                f"出自：{row[1]}\n"
                f"原文：{row[0]}\n"
                f"相关性：{D[0][idx-1]}\n\n"
                )
        cur.close()
        conn.close()
        return search_result
