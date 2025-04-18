import langpipe
import sample_nodes

# create nodes
begin = langpipe.LPBegin('begin_node')
kbsearch = sample_nodes.LPKBSearch('kbsearch', 'faiss.index', 'faiss.db') # knowledge base file (vector & meta)
aggregator = langpipe.LPAggregator('aggregator', None, 'qwen2.5:7b')
end = langpipe.LPEnd('end_node', callback=(lambda x: 
                                           print(f'query : {x['query']}\n'
                                                 f'answer: {x['final_out']}\n'
                                                 )), 
                                           debug=False, print_final_out=False)

# link together
begin.link(kbsearch)
kbsearch.link(aggregator)
aggregator.link(end)

"""
chat to knowledge base, sample question (from knowledge base):
1. VideoPipe的主要功能是什么？
2. 车辆车型颜色识别算法哪些场景下精度会下降？
3. 车牌识别技术一般可以应用于哪些场合
4. VideoPipe中Node类型有哪几种？分别是什么

sample input & output:
>>>车辆车型颜色识别算法哪些场景下精度会下降？
query : 车辆车型颜色识别算法哪些场景下精度会下降？
answer: 车辆车型颜色识别算法在以下几种场景下的精度可能会有所下降：
1. **光线条件不佳的情况**：如凌晨或晚上无光线或光线较暗的环境。
2. **车辆严重遮挡**：当车辆存在严重的遮挡，导致关键特征被消除时。
3. **极端天气条件**：例如大雾、大雪等恶劣天气条件下。
这些因素都会对算法识别车辆的颜色和车型造成一定的影响。因此，在实际应用中需要综合考虑环境因素，以提高识别的准确率。
"""
while True:
    input_txt = input('>>>')
    if input_txt == 'exit':
        break

    # input what you want to
    begin.input(input_txt)