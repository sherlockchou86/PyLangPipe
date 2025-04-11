import json
import re
from datetime import datetime
from .lpnode import LPNode, LPNodeType

class LPEnd(LPNode):
    """
    end node in pipeline.
    """

    def __init__(self, 
                 name, 
                 callback=None, 
                 debug=True, 
                 print_final_out=True,
                 remove_thinking_txt=True) -> None:
        super().__init__(name, LPNodeType.End, None)
        self.__callback = callback
        self.__debug = debug
        self.__print_final_out = print_final_out
        self.__remove_thinking_txt = remove_thinking_txt
        self.final_out = None
    
    def _dispatch(self, lpdata) -> None:
        """
        override dispatch() since no lpdata flowing downstream.
        """
        pass

    def _handle(self, lpdata) -> None:
        """
        postprocess for final_out if nessessary
        """
        self.final_out = lpdata['final_out']

        # remove <think>...</think>
        if self.__remove_thinking_txt:
            self.final_out = re.sub(r"<think>.*?</think>", "", self.final_out, flags=re.DOTALL)
        
        if self.__print_final_out:
            print(f'>>>>>>>>>>>>>[output][final_out from {self.name}]>>>>>>>>>>>>>')
            print(self.final_out)
            print(f'<<<<<<<<<<<<<[output][final_out from {self.name}]<<<<<<<<<<<<<')
    
    def _after_handle(self, lpdata) -> None:
        """
        override _after_handle() since we need callback/print/update when all works done.
        """
        super()._after_handle(lpdata)

        # update local vars
        record = lpdata['records'][-1]
        record['local_vars']['__callback'] = self.__callback if self.__callback is None else self.__callback.__name__
        record['local_vars']['__debug'] = self.__debug
        record['local_vars']['__print_final_out'] = self.__print_final_out
        record['local_vars']['__remove_thinking_txt'] = self.__remove_thinking_txt

        # update global vars
        lpdata['end_t'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # print for debug purpose
        if self.__debug:
            print(f'>>>>>>>>>>>>>[debug][lpdata from {self.name}]>>>>>>>>>>>>>')
            print(json.dumps(lpdata, indent=4, ensure_ascii=False))
            print(f'<<<<<<<<<<<<<[debug][lpdata from {self.name}]<<<<<<<<<<<<<')
        
        # callback to notify external codes
        if self.__callback is not None:
            self.__callback(lpdata)
    
    def link(self, next_nodes) -> int:
        """
        override link() since linking not approved for end node.
        """
        return 0