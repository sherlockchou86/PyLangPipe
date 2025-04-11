import threading
from abc import ABC, abstractmethod
from typing import final
from .lpnode import LPNode, LPNodeType

class LPBaseRouter(ABC, LPNode):
    """
    base class for router node, which is used to route the data to different branches in pipeline.
    """
    def __init__(self, name) -> None:
        super().__init__(name, LPNodeType.Invoke, None)
    
    @abstractmethod
    def _condition_check(self, lpdata) -> int:
        """
        if/elif/.../else condition check, return int value to identity which branch to run.
        - 0 means first branch to run
        - 1 means second branch to run
        - ...
        """
        pass

    def _dispatch(self, lpdata) -> None:
        route_id = self._condition_check(lpdata)

        if route_id >= 0 and len(self.next_nodes) > route_id:
            node = self.next_nodes[route_id]
            if lpdata['sync']:
                node.run(lpdata)
            else:
                threading.Thread(target=lambda d: node.run(d), args=(lpdata,)).start()