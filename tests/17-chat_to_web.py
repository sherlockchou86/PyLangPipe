import langpipe
import sample_nodes

# create nodes
begin = langpipe.LPBegin('begin_node')
bocha_search = sample_nodes.LPBoChaSearch('bocha_search', 'sk-***') # replace with your own api key
aggregator = langpipe.LPAggregator('aggregator', None, 'qwen2.5:7b')
end = langpipe.LPEnd('end_node', callback=(lambda x: 
                                           print(f'query : {x['query']}\n'
                                                 f'answer: {x['final_out']}\n'
                                                 )), 
                                           debug=False, print_final_out=False)

# link together
begin.link(bocha_search)
bocha_search.link(aggregator)
aggregator.link(end)


"""
chat to web, sample question (online):
1. 腾讯今日的股价行情?
2. 小米汽车高速撞车重大事故的详细经过是怎样的？
3. 当前美国对华征收关税为多少？对中美贸易有何影响
4. 如何学习开飞机？
5. 韩国2025年发生了哪些重大事件？

sample input & output:
>>>韩国2025年发生了哪些重大事件？
query : 韩国2025年发生了哪些重大事件？
answer: 2025年对于韩国来说是充满挑战的一年。年初以来，一系列重大事件接连发生，不仅影响了国内政治和社会稳定，也对国际关系产生了深远的影响。
首先，在政治领域，韩国总统尹锡悦因涉嫌滥用职权、非法戒严及“引诱朝鲜攻击”计划等罪名被逮捕，成为宪政史上首位在任期内被捕的总统。这一事件引发了广泛的争议和讨论，不仅导致了国内政局的动荡，还使得经济增速预测从1.9%下调至1.6%，加剧了社会不安。
其次，在司法领域，三星电子会长李在镕因2015年的会计造假、操纵股价等行为被二审法院维持无罪判决。这一结果引发了公众对财阀特权的质疑，并进一步削弱了公众对司法公正的信任。
此外，娱乐圈也出现了重大丑闻，影帝刘亚仁因涉毒和非法出售豪宅等问题受到广泛关注。这些事件不仅暴露了娱乐圈与财阀资本之间的复杂关系，还引发了社会对于洗钱等犯罪行为的关注。
与此同时，韩国政坛的另一重要人物——共同民主党党首李在明，在涉及违反《公职选举法》案中被判无罪，这为他未来的政治生涯带来了新的希望。然而，如果检方继续上诉至最高法院并最终确定刑期，李在明仍可能面临参选障碍。
国际关系方面，美国将韩国列入“敏感国家名单”，这一决定反映了美韩同盟关系中的复杂动态。尽管近年来两国合作加深，但此次事件凸显了双方在安全和战略问题上的分歧。
此外，韩国还面临着严重的山火危机。自3月起，多处林区发生火灾，造成26人死亡、大量山林被毁，并对文化遗产构成了威胁。这一自然灾害不仅考验着政府的应急响应能力，也引发了关于森林管理和环境保护政策的广泛讨论。
综上所述，2025年的韩国经历了政治动荡、司法争议、娱乐圈丑闻以及国际关系紧张等多重挑战，这些事件共同塑造了这一年复杂而多变的政治和社会图景。
"""
while True:
    input_txt = input('>>>')
    if input_txt == 'exit':
        break

    # input what you want to
    begin.input(input_txt)