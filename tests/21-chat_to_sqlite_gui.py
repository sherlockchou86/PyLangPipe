from flask import Flask, jsonify, render_template_string, request
from flask_socketio import SocketIO, emit
import json
import langpipe
import sample_nodes

"""
run fake_sqlite_db.py first to generate shop.db.
"""

ddl_desc = """
##下面是sqlite数据库的DDL结构##
-- ----------------------------
-- 用户表：users
-- 存储注册用户的基本信息
-- ----------------------------
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,              -- 用户唯一ID，自增主键
    username TEXT NOT NULL UNIQUE,                     -- 用户名，必须唯一且非空
    email TEXT NOT NULL UNIQUE,                        -- 用户邮箱，必须唯一且非空
    password_hash TEXT NOT NULL,                       -- 密码哈希值，用于存储加密后的密码
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP     -- 注册时间，默认为当前时间
);

-- ----------------------------
-- 商品表：products
-- 存储上架商品的详细信息
-- ----------------------------
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,              -- 商品唯一ID，自增主键
    name TEXT NOT NULL,                                -- 商品名称，非空
    description TEXT,                                  -- 商品描述，可选
    price REAL NOT NULL,                               -- 商品单价，使用REAL表示小数
    stock INTEGER DEFAULT 0,                           -- 商品库存数量，默认0
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP     -- 上架时间，默认为当前时间
);

-- ----------------------------
-- 订单表：orders
-- 记录用户提交的订单信息
-- ----------------------------
/*
订单状态（status）字段说明：
- 'pending'    等待付款
- 'paid'       已付款
- 'shipped'    已发货
- 'completed'  已完成
- 'cancelled'  已取消
*/
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,              -- 订单唯一ID，自增主键
    user_id INTEGER NOT NULL,                          -- 下单用户的ID，关联 users(id)
    status TEXT DEFAULT 'pending',                     -- 订单状态，默认为 pending
    total_amount REAL NOT NULL,                        -- 订单总金额
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,    -- 订单创建时间
    FOREIGN KEY (user_id) REFERENCES users(id)         -- 外键：用户ID
);

-- ----------------------------
-- 订单项表：order_items
-- 记录每个订单中包含哪些商品及数量
-- ----------------------------
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,              -- 订单项唯一ID，自增主键
    order_id INTEGER NOT NULL,                         -- 所属订单ID，关联 orders(id)
    product_id INTEGER NOT NULL,                       -- 商品ID，关联 products(id)
    quantity INTEGER NOT NULL,                         -- 购买数量
    unit_price REAL NOT NULL,                          -- 下单时的商品单价
    FOREIGN KEY (order_id) REFERENCES orders(id),      -- 外键：订单ID
    FOREIGN KEY (product_id) REFERENCES products(id)   -- 外键：商品ID
);

-- ----------------------------
-- 退款表：refunds
-- 记录订单退款的请求和处理信息
-- ----------------------------
CREATE TABLE IF NOT EXISTS refunds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,              -- 退款记录ID，自增主键
    order_id INTEGER NOT NULL,                         -- 关联的订单ID
    refund_amount REAL NOT NULL,                       -- 退款金额
    reason TEXT,                                       -- 退款原因，可选
    refund_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,   -- 退款时间，默认为当前时间
    FOREIGN KEY (order_id) REFERENCES orders(id)       -- 外键：订单ID
);
"""


lpdata = None
def handle_output(x):
    global lpdata
    lpdata = x

# create nodes
begin = langpipe.LPBegin('begin_node')
sqlcreator = langpipe.LPSQLCreator('sql_creator', ddl_desc, 'qwen2.5:32b')
dbsearch = sample_nodes.LPDBSearch('db_search', 'shop.db')
aggregator = langpipe.LPAggregator('aggregator', None, 'qwen2.5:32b')
end = langpipe.LPEnd('end_node', callback=handle_output)

# link together
begin.link(sqlcreator)
sqlcreator.link(dbsearch)
dbsearch.link(aggregator)
aggregator.link(end)


# web html
HTML_TEMPLATE = """
<!doctype html>
<html lang=\"zh\">
<head>
  <meta charset=\"UTF-8\">
  <title>Chat To Sqlite Using LangPipe</title>
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
<h1>Chat To Sqlite Using LangPipe</h1>
<div id=\"inputArea\">
  <input type=\"text\" id=\"user_input\" value=\"谁的退货次数最多？需要对该用户进行特别关注，以防恶意刷单\" required>
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
    return lpdata['final_out'], lpdata.get('global_vars', {}).get('created_sql', '')

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    msg = data.get('message', '')
    res, sql = get_bot_response(msg)
    return jsonify({'response': res + '<br/>SQL: ' + sql})

if __name__ == '__main__':
    # visit 127.0.0.1:5000
    app.run(debug=True, port=5000)
