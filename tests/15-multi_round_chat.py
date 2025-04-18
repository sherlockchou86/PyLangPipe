import langpipe
import json

# chat pipeline wrapper
class ChatPipeline:
    """
    hold chat status such as history messages outside langpipe.
    """
    def __init__(self, max_his_num=10) -> None:
        self.__max_his_num = max_his_num
        self.__his_messages = []
        self.__out_txt = ''

        # create nodes
        self.__begin = langpipe.LPBegin('begin_node')
        classifier = langpipe.LPClassifier('classifier', {'正常问题':'非敏感问题，都归属于正常问题', '非正常问题':'一切涉及政治、色情、歧视、暴恐等违法内容的问题'}, 'qwen2.5:7b')
        chatter = langpipe.LPChatter('chatter', 'qwen2.5:7b')
        end_legal = langpipe.LPEnd('end_legal', callback=self.__output_handler, debug=False, print_final_out=False, remove_thinking_txt=False)
        end_illegal = langpipe.LPEnd('end_illegal', callback=self.__output_handler, debug=False, print_final_out=False, remove_thinking_txt=False)
        end_failed = langpipe.LPEnd('end_failed', callback=self.__output_handler, debug=False, print_final_out=False, remove_thinking_txt=False)

        # link together
        self.__begin.link(classifier)
        classifier.link([chatter, end_illegal, end_failed])
        chatter.link(end_legal)

        # print pipeline
        print(self.__begin)
        """
        begin_node[type:Begin]
            └── classifier[type:LLM]
                ├── chatter[type:LLM]
                │   └── end_legal[type:End]
                ├── end_illegal[type:End]
                └── end_failed[type:End]
        """

    def __call__(self, input:str) -> str:
        return self.__chat(input)

    def __output_handler(self, lpdata):
        self.__out_txt = lpdata['final_out']
        self.__his_messages.append({'role': 'assistant', 
                                    'content': self.__out_txt})

    def __chat(self, input:str) -> str:
        if len(self.__his_messages) >= self.__max_his_num:
            self.__his_messages.clear()
        
        message = {
            "role": "user",
            "content": input
        }
        self.__his_messages.append(message)
        self.__begin.input(json.dumps(self.__his_messages, indent=4, ensure_ascii=False))
        return self.__out_txt

# create wrapper
chat_pipline = ChatPipeline()

# get user input and run pipline
while True:
    input_txt = input('>>>')
    if input_txt == 'exit':
        break

    res = chat_pipline(input_txt)
    print('<<<' + res)