
import threading
from enum import Enum
from datetime import datetime

class LPNodeState(Enum):
    """
    node state in LangPipe.
    """
    Pending = -1
    Runing = 0
    Completed = 1


class LPNodeType(Enum):
    """
    node type in LangPipe.

    - Begin: begin point in pipeline.
    - LLM: node which works based on LLM.
    - Invoke: node which need call external tools or 3rd service to get more data. 
    - End: end point in pipeline.
    """
    Begin = 1
    LLM = 2
    Invoke = 3
    End = 4

class LPNode:
    """
    base class for all nodes in LangPipe.
    """
    
    def __init__(self, name, type, model) -> None:
        self.name = name
        self.type = type
        self.model = model
        self.state = LPNodeState.Pending
        self.cost_time = 0
        self.next_nodes = []
    
    def __str__(self):
        return self._str_helper(is_root=True)

    def _str_helper(self, prefix='', is_last=True, is_root=False):
        title = f"{self.name}[type:{str(self.type.name)}]"
        lines = []
        if is_root:
            lines.append(title)
        else:
            connector = '└── ' if is_last else '├── '
            lines.append(prefix + connector + title)

        new_prefix = prefix + ('    ' if is_last else '│   ')
        child_count = len(self.next_nodes)
        for i, child in enumerate(self.next_nodes):
            is_last_child = (i == child_count - 1)
            lines.append(child._str_helper(new_prefix, is_last_child))
        return '\n'.join(lines)

    def run(self, lpdata) -> None:
        """
        execute main logic in node.
        """
        self._before_handle(lpdata)
        self._handle(lpdata)
        self._after_handle(lpdata)
        self._dispatch(lpdata)

    def link(self, next_nodes) -> int:
        """
        link node to next nodes and return total size of next nodes.
        """
        if isinstance(next_nodes, list):
            self.next_nodes.extend(next_nodes)
        else:
            self.next_nodes.append(next_nodes)
        return len(self.next_nodes)

    def _before_handle(self, lpdata) -> None:
        """
        add a new record in lpdata.
        """
        record = {}
        record['begin_t'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record['end_t'] = None
        record['node_name'] = self.name
        record['node_type'] = str(self.type)
        record['model'] = self.model
        record['local_vars'] = {}
        record['messages'] = []
        
        lpdata['records'].append(record)

        # enter running state
        self.state = LPNodeState.Runing

    def _handle(self, lpdata) -> None:
        """
        main logic for handling lpdata and update key/values in lpdata if nessessary.
        """
        pass

    def _after_handle(self, lpdata) -> None:
        """
        update record in lpdata.
        """
        record = lpdata['records'][-1]
        record['end_t'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.cost_time = int((datetime.strptime(record['end_t'], "%Y-%m-%d %H:%M:%S") 
                          - datetime.strptime(record['begin_t'], "%Y-%m-%d %H:%M:%S")).total_seconds())
        # enter completed state
        self.state = LPNodeState.Completed

    def _dispatch(self, lpdata) -> None:
        """
        dispatch data to next nodes in sync or async mode.

        Depth-First Search(DFS) for the pipeline in sync mode.
        """
        for node in self.next_nodes:
            if lpdata['sync']:
                node.run(lpdata)
            else:
                threading.Thread(target=lambda d: node.run(d), args=(lpdata,)).start()