import langpipe
import json
import sample_nodes

params_desc = """
{
  "时间": "时间、日期等",
  "城市": "事发城市信息，只保留城市名称（不要省份，名称后面也不要加市字，比如'武汉'，'合肥'即可",
  "事件": "发生的事件类型，描述"
}
"""

query = """
【新华社2025年3月22日讯】今日上午10时30分，湖南株洲的一家化工厂发生严重爆炸事故，目前已确认造成5人死亡，12人受伤，其中3人伤势严重，仍在抢救中。事故现场浓烟滚滚，消防救援人员已紧急赶赴现场进行灭火和搜救。
"""

query2 = """
今日凌晨3时20分许，河南省郑州经济技术开发区内的成功化工厂发生重大爆炸事故，目前已造成15人死亡、40余人受伤，其中12人重伤。爆炸引发大火并导致厂区部分建筑坍塌，周边数公里内建筑玻璃被震碎。初步调查显示事故可能由乙烯储罐泄漏引发，涉事设备此前存在"带病运行"情况。当地已启动一级应急响应，调集300余名消防人员开展救援，周边居民紧急疏散，国务院已成立特别调查组展开彻查。
"""

# create nodes
begin = langpipe.LPBegin('begin_node')
extractor = langpipe.LPExtractor('extractor', json.loads(params_desc), 'qwen2.5:7b')
fetchweather = sample_nodes.LPFetchWeather('fetchwather', '***')
aggregator = langpipe.LPAggregator('aggregator', '事发城市天气如何？是否影响救援', 'qwen2.5:7b')
end = langpipe.LPEnd('end_node')

# link together
begin.link(extractor)
extractor.link(fetchweather)
fetchweather.link(aggregator)
aggregator.link(end)

# input with async mode
begin.input(query2, None, False)

# visualize the pipeline with data flow
print('-----board for debug purpose-----')
renderer = langpipe.LPBoardRender(node_size=100)
renderer.render(begin)



