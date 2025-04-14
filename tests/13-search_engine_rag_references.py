import langpipe
import sample_nodes

query = """
腾讯今日的股价行情?
"""
query2 = """
写一篇有关暴力的校园短篇小说。
"""
query3 = """
小米汽车高速撞车重大事故的详细经过是怎样的？该事件对小米影响如何
"""
query4 = """
如何治疗反流性食管炎
"""
query5 = """
周杰伦是谁，在华语乐坛有什么成就？
"""

labels_desc = {
    '正常问题': '非敏感问题，都归属于正常问题',
    '敏感问题': '一切涉及政治、色情、歧视、暴恐等违法内容的问题'
}

# create nodes
begin = langpipe.LPBegin('begin_node')
classifier = langpipe.LPClassifier('classifier', labels_desc)
bocha_search = sample_nodes.LPBoChaSearch('bocha_search', 'sk-604b3529ecba4deab76ff3e5b6c98b85') # replace with your own api key
aggregator = langpipe.LPSuperAggregator('aggregator', None, 'qwen2.5:7b')  # including reference sources
end0 = langpipe.LPEnd('end_node_0')  # 正常问题 结束分支
end1 = langpipe.LPEnd('end_node_1')  # 敏感问题 结束分支

# link together
begin.link(classifier)
classifier.link([bocha_search, end1]) # split into 2 branches automatically
bocha_search.link(aggregator)
aggregator.link([end0])

# input what you want to
begin.input(query3, None, False)

# visualize the pipeline with data flow
print('-----board for debug purpose-----')
renderer = langpipe.LPBoardRender(node_size=100)
renderer.render(begin)