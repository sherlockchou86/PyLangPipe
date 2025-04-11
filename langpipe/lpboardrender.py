import cv2
import threading
import numpy as np
from datetime import datetime
from .lpnode import LPNodeState

class LPBoardRender:
    """
    pipeline visualization tools based on OpenCV library.
    """
    def __init__(self, node_size=50, h_spacing=100, v_spacing=80):
        self.__node_size = node_size
        self.__h_spacing = h_spacing
        self.__v_spacing = v_spacing
        self.__y_positions = {}
        self.__img = None
        self.__colors = {
            LPNodeState.Pending: (0, 0, 0),    # bgr is black
            LPNodeState.Runing: (0, 0, 255),   # bgr is red
            LPNodeState.Completed: (255, 0, 0) # bgr is blue
        }
        self.__runing = False
    
    def __del__(self):
        self.__runing = False

    def __get_tree_depth(self, root):
        if not root.next_nodes:
            return 1
        return 1 + max(self.__get_tree_depth(child) for child in root.next_nodes)

    def __get_layer_nodes(self, root, depth=0, layers=None):
        if layers is None:
            layers = {}
        if depth not in layers:
            layers[depth] = []
        layers[depth].append(root)
        for child in root.next_nodes:
            self.__get_layer_nodes(child, depth + 1, layers)
        return layers

    def __draw_node(self, node, x, y):
        cv2.rectangle(self.__img, (x, y), 
                      (x + self.__node_size, y + self.__node_size), 
                      self.__colors[node.state], 2)
        
        # name
        text_size = cv2.getTextSize(node.name, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
        text_x = x + (self.__node_size - text_size[0]) // 2
        text_y = y + (self.__node_size + text_size[1]) // 2
        cv2.putText(self.__img, node.name, (text_x, text_y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.__colors[node.state], 1)
        
        # type
        text_size = cv2.getTextSize('[' + node.type.name + ']', cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
        text_x = x + (self.__node_size - text_size[0]) // 2
        text_y = y + text_size[1] + 5
        cv2.putText(self.__img, '[' + node.type.name + ']', (text_x, text_y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.__colors[node.state], 1)

        # cost time
        if node.state == LPNodeState.Completed:
            text_size = cv2.getTextSize(str(node.cost_time) + 'sec', cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
            text_x = x + (self.__node_size - text_size[0]) // 2
            text_y = y + self.__node_size - 5
            cv2.putText(self.__img, str(node.cost_time) + 'sec', (text_x, text_y), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.__colors[node.state], 1)

        # child nodes
        child_x = x + self.__node_size + self.__h_spacing
        for child in node.next_nodes:
            child_y = self.__y_positions[child]
            cv2.line(self.__img, (x + self.__node_size, y + self.__node_size // 2), 
                     (child_x, child_y + self.__node_size // 2), self.__colors[child.state], 1, cv2.LINE_AA)
            cv2.circle(self.__img, (child_x, child_y + self.__node_size // 2), 
                       5, self.__colors[child.state], -1)
            self.__draw_node(child, child_x, child_y)
    
    def __draw_info(self):
        cv2.putText(self.__img, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
    def __draw_board(self, root):
        layers = self.__get_layer_nodes(root)
        max_depth = max(layers.keys())
        max_width = max(len(layers[d]) for d in layers)
        
        img_height = max(400, max_width * (self.__node_size + self.__v_spacing))
        img_width = (max_depth + 1) * (self.__node_size + self.__h_spacing)
        
        for depth, nodes in layers.items():
            layer_height = len(nodes) * (self.__node_size + self.__v_spacing)
            start_y = (img_height - layer_height + self.__v_spacing) // 2
            self.__y_positions.update({node: start_y + i * (self.__node_size + self.__v_spacing) for i, node in enumerate(nodes)})
                
        root_x = self.__h_spacing // 2
        root_y = self.__y_positions[root]

        while self.__runing:
            self.__img = np.ones((img_height, img_width, 3), dtype=np.uint8) * 255
            self.__draw_node(root, root_x, root_y)
            self.__draw_info()
            cv2.imshow("Tree", self.__img)
            if cv2.waitKey(100) & 0xFF == 27:
                break

    def render(self, root, block=True):
        self.__runing = True
        render_th = threading.Thread(target=self.__draw_board, args=(root,), daemon=True)
        render_th.start()

        if block:
            render_th.join()
