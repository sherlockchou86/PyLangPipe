import sqlite3
from langpipe import LPBaseInvoker

class LPDBSearch(LPBaseInvoker):
    """
    search from database based on sqlite.
    access `lpdata['global_vars']['db_searched_result']` for the searched result from sqlite.
    """
    def __init__(self, name, db_name) -> None:
        super().__init__(name)
        self.__db_name = db_name
        self.__sql_query = None
        self.__db_searched_result = None
    
    def _invoke(self, lpdata) -> None:
        self.__sql_query = lpdata.get('global_vars', {}).get('created_sql', None)
        if self.__sql_query is not None:
            self.__db_searched_result = self.__db_search()
    
    def _after_handle(self, lpdata) -> None:
        super()._after_handle(lpdata)

        # update local variables
        record = lpdata['records'][-1]
        record['local_vars']['__db_name'] = self.__db_name
        record['local_vars']['__sql_query'] = self.__sql_query

        # update global variables
        if self.__db_searched_result is not None:
            lpdata['final_out'] = self.__db_searched_result
            lpdata['global_vars']['db_searched_result'] = self.__db_searched_result

    
    def __db_search(self) -> str:
        try:
            conn = sqlite3.connect(self.__db_name)
            cursor = conn.cursor()
            cursor.execute(self.__sql_query)

            rows = cursor.fetchall()
            return str(rows)
        except Exception as e:
            print(e)
            return None
        