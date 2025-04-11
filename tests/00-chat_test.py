import langpipe

# message
query = """
[
{
  "role": "user",
  "content": "你好"
},
{
  "role": "assistant",
  "content": "你好，有什么我可以帮助你的吗？"
},
{
  "role": "user",
  "content": "如何使用语言模型？"
},
{
  "role": "user",
  "content": "如何面对恐惧？"
}
]
"""

# create nodes
begin = langpipe.LPBegin('begin_node')
chatter = langpipe.LPChatter('chatter', 'qwen2.5:7b')
end = langpipe.LPEnd('end_node', callback=lambda x: print(x['final_out']), debug=False, print_final_out=False, remove_thinking_txt=False)

# link together
begin.link(chatter)
chatter.link(end)

# input with sync mode
begin.input(query)