import langpipe
import json

# parameters description
params_desc = """
{
  "时间": "时间、日期等",
  "地点": "位置信息",
  "事件": "发生的事件类型，描述"
}
"""

query = """
【新华社2025年3月22日讯】今日上午10时30分，位于江苏省南通市的一家化工厂发生严重爆炸事故，目前已确认造成5人死亡，12人受伤，其中3人伤势严重，仍在抢救中。事故现场浓烟滚滚，消防救援人员已紧急赶赴现场进行灭火和搜救。
"""

# create nodes
begin = langpipe.LPBegin('begin_node')
extractor = langpipe.LPExtractor('extractor', json.loads(params_desc), 'qwen2.5:7b')
end = langpipe.LPEnd('end_node', debug=False, print_final_out=False)

# link together
begin.link(extractor)
extractor.link(end)

# visualize the pipeline with data flow
print('-----board for debug purpose-----')
renderer = langpipe.LPBoardRender(node_size=100)
renderer.render(begin, False)  # no block

# input with sync mode
begin.input(query)

# print the output
print(end.final_out)