import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from langpipe import LPBegin, LPGenerator, LPEnd, LPAggregator
from sample_nodes import LPBoChaSearch
from flask import Flask, request, jsonify, render_template

def create_chat2llm_pipeline():
    """
    chat to LLMs using LangPipe.
    """
    # create nodes
    begin = LPBegin('begin')
    generator = LPGenerator('generator', 'qwen2.5:7b')
    end = LPEnd('end')

    # link together
    begin.link(generator)
    generator.link(end)

    # return the head&tail of pipeline
    return begin, end

def create_chat2web_pipeline():
    """
    chat to Web(online search) using LangPipe.
    """
    # create nodes
    begin = LPBegin('begin')
    bocha_search = LPBoChaSearch('bocha_search', 'sk-***') # replace with your own api key
    aggregator = LPAggregator('aggregator', None, 'qwen2.5:7b')
    end = LPEnd('end')

    # link together
    begin.link(bocha_search)
    bocha_search.link(aggregator)
    aggregator.link(end)

    # return the head&tail of pipeline
    return begin, end

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    online_search_enabled = request.json.get("online_search", False) 
    response = ""

    if online_search_enabled:
        head, tail = create_chat2web_pipeline()
        head.input(user_message)
        response = tail.final_out
    else:
        head, tail = create_chat2llm_pipeline()
        head.input(user_message)
        response = tail.final_out

    return jsonify({"reply": response, "online_search": online_search_enabled})

if __name__ == "__main__":
    app.run(debug=True)
