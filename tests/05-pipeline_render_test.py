import langpipe

# create nodes
root_node = langpipe.LPNode("root", langpipe.LPNodeType.Begin, None)
child_node1 = langpipe.LPNode("child_node1", langpipe.LPNodeType.LLM, None)
child_node2 = langpipe.LPNode("child_node2", langpipe.LPNodeType.LLM, None)
child_node3 = langpipe.LPNode("child_node3", langpipe.LPNodeType.LLM, None)

grandchild_node11 = langpipe.LPNode("grandchild_node11", langpipe.LPNodeType.LLM, None)
grandchild_node12 = langpipe.LPNode("grandchild_node12", langpipe.LPNodeType.LLM, None)
grandchild_node21 = langpipe.LPNode("grandchild_node21", langpipe.LPNodeType.LLM, None)

end11 = langpipe.LPEnd('end11')
end12 = langpipe.LPEnd('end12')
end21 = langpipe.LPEnd('end21')
end3 = langpipe.LPEnd('end3')

# link together
root_node.link([child_node1, child_node2, child_node3])
child_node1.link([grandchild_node11, grandchild_node12])
child_node2.link([grandchild_node21])
grandchild_node11.link(end11)
grandchild_node12.link(end12)
grandchild_node21.link(end21)
child_node3.link(end3)

# print the pipeline
print(root_node)
"""
root[type:Begin]
    ├── child_node1[type:LLM]
    │   ├── grandchild_node11[type:LLM]
    │   │   └── end11[type:End]
    │   └── grandchild_node12[type:LLM]
    │       └── end12[type:End]
    ├── child_node2[type:LLM]
    │   └── grandchild_node21[type:LLM]
    │       └── end21[type:End]
    └── child_node3[type:LLM]
        └── end3[type:End]
"""

# render the pipeline
board = langpipe.LPBoardRender(node_size=100)
board.render(root_node) # block here