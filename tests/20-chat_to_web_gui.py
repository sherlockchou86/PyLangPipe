from flask import Flask, jsonify, render_template_string, request
from flask_socketio import SocketIO, emit
import json
import langpipe
import sample_nodes

# create nodes
begin = langpipe.LPBegin('begin_node')
bocha_search = sample_nodes.LPBoChaSearch('bocha_search', 'sk-***') # replace with your own api key
aggregator = langpipe.LPSuperAggregator('aggregator', None, True, 'qwen2.5:7b')
end = langpipe.LPEnd('end_node', debug=True, print_final_out=False)

# link together
begin.link(bocha_search)
bocha_search.link(aggregator)
aggregator.link(end)

# web html
HTML_TEMPLATE = """
<!doctype html>
<html lang=\"zh\">
<head>
  <meta charset=\"UTF-8\">
  <title>Chat To Web Using LangPipe</title>
  <style>
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background-color: #f0f2f5;
      padding: 40px;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    h1 {
      color: #333;
      text-align: center;
    }
    #inputArea {
      margin-top: 20px;
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 10px;
      width: 100%;
      max-width: 800px;
    }
    input[type=text] {
      padding: 10px;
      width: 75%;
      font-size: 16px;
      border: 1px solid #ccc;
      border-radius: 5px;
      max-width: 600px;
    }
    button {
      padding: 10px 20px;
      font-size: 16px;
      background-color: #4CAF50;
      color: white;
      border: none;
      border-radius: 5px;
      cursor: pointer;
    }
    .chat-box {
      margin-top: 30px;
      background-color: white;
      padding: 20px;
      border-radius: 10px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      text-align: left;
      width: 100%;
      max-width: 800px;
    }
    .user, .bot {
      margin-bottom: 10px;
    }
    .user strong {
      color: #007bff;
    }
    .bot strong {
      color: #28a745;
    }
  </style>
</head>
<body>
<h1>Chat To Web Using LangPipe</h1>
<div id=\"inputArea\">
  <input type=\"text\" id=\"user_input\" required>
  <button onclick=\"sendMessage()\">发送</button>
</div>
<div class=\"chat-box\" id=\"chat_box\"></div>

<script>
  function sendMessage() {
    const input = document.getElementById('user_input');
    const msg = input.value;
    if (msg.trim()) {
      const chatBox = document.getElementById('chat_box');
      chatBox.innerHTML += `<div class='user'><strong>你：</strong> ${msg}</div>`;
      input.value = '';
      fetch('/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: msg })
      })
      .then(response => response.json())
      .then(data => {
        chatBox.innerHTML += `<div class='bot'><strong>LangPipe：</strong> ${data.response}</div>`;
      });
    }
  }
</script>
</body>
</html>
"""


app = Flask(__name__)

def get_bot_response(user_input):
    begin.input(user_input)
    return json.loads(end.final_out)['content']

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    msg = data.get('message', '')
    response = get_bot_response(msg)
    return jsonify({'response': response})

if __name__ == '__main__':
    # visit 127.0.0.1:5000
    app.run(debug=True, port=5000)

