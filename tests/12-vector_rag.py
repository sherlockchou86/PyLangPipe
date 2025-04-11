import langpipe
import sample_nodes

"""
run fake_faiss_index.py first to generate faiss.index and faiss.db
"""

query = """
VideoPipe的主要功能是什么？
"""

query2 = """
车辆车型颜色识别算法哪些场景下精度会下降？
"""

query3 = """
车牌识别技术一般可以应用于哪些场合
"""

# create nodes
begin = langpipe.LPBegin('begin_node')
kbsearch = sample_nodes.LPKBSearch('kbsearch', 'faiss.index', 'faiss.db')
aggregator = langpipe.LPAggregator('aggregator', None, 'qwen2.5:7b')
end = langpipe.LPEnd('end_node')

# link together
begin.link(kbsearch)
kbsearch.link(aggregator)
aggregator.link(end)

# input what you want to
begin.input(query, None, False)

# visualize the pipeline with data flow
print('-----board for debug purpose-----')
renderer = langpipe.LPBoardRender(node_size=100)
renderer.render(begin)