
from abc import ABC, abstractmethod
from typing import final
from .lpnode import LPNode, LPNodeType

class LPBaseInvoker(ABC, LPNode):
    """
    base class for all invoker nodes, which invokes external services, access database, or call 3rd tools.
    """
    def __init__(self, name) -> None:
        super().__init__(name, LPNodeType.Invoke, None)
    
    @final
    def _handle(self, lpdata) -> None:
        # hidden _handle(...) in derived classes, using _invoke(...) instead
        self._invoke(lpdata)
    
    @abstractmethod
    def _invoke(self, lpdata) -> None:
        pass