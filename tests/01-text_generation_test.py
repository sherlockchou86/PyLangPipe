import langpipe

query = """
如何驾驶飞机？
"""

# create nodes
begin = langpipe.LPBegin('begin_node')
generator = langpipe.LPGenerator('generator', 'deepseek-r1:8b')
end = langpipe.LPEnd('end_node', print_final_out=False)

# link together
begin.link(generator)
generator.link(end)

# input with sync mode
begin.input(query)

# print result
print(end.final_out)