import langpipe
import base64

# collect query images as base64 strings
query_imgs = []
with open('files/1.jpg', 'rb') as f:
    img_base64 = base64.b64encode(f.read()).decode()
    query_imgs.append(img_base64)
with open('files/2.png', 'rb') as f:
    img_base64 = base64.b64encode(f.read()).decode()
    query_imgs.append(img_base64)

query = """
这是两张什么图片？
"""

# define output handler hooked at end node
def output_handler(lpdata):
    print('output from handler:')
    print(lpdata['final_out'])

# create nodes
begin = langpipe.LPBegin('begin_node')
generator = langpipe.LPGenerator('generator')
end = langpipe.LPEnd('end_node', callback=output_handler, print_final_out=False, debug=False)

# link together
begin.link(generator)
generator.link(end)

# input query & query images with sync mode
begin.input(query, query_imgs)