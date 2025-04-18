import langpipe
import json

# labels description
labels_desc = """
{
  "科技": "涉及科技发展、人工智能、编程、工程等相关内容",
  "财经": "涉及金融、经济、市场趋势、投资等内容",
  "体育": "涉及各类体育赛事、运动员、比赛分析等",
  "娱乐": "涉及电影、音乐、明星、综艺等内容",
  "健康": "涉及医学、养生、健康饮食、心理健康等内容"
}
"""
json.loads(labels_desc)

# create nodes
begin = langpipe.LPBegin('begin')
classifier = langpipe.LPClassifier('classifier', json.loads(labels_desc))
end0 = langpipe.LPEnd('end0')     # 1st label
end1 = langpipe.LPEnd('end1')     # 2nd label
end2 = langpipe.LPEnd('end2')     # 3rd label
end3 = langpipe.LPEnd('end3')     # 4th label
end4 = langpipe.LPEnd('end4')     # 5th label
end10 = langpipe.LPEnd('end10')   # classification fails

# link together
begin.link([classifier])
classifier.link([end0, end1, end2, end3, end4])
classifier.link(end10)

# input what you want to, with async mode
begin.input("这次比赛，日本代表团获得了三金四银的好成绩", None, False)

# visualize the pipeline with data flow
print('-----board for debug purpose-----')
renderer = langpipe.LPBoardRender(node_size=80, v_spacing=50)
renderer.render(begin)
