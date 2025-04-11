import langpipe
import json
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

query = """
哪些人买过可口可乐？都是什么时候买的，分别买了多少瓶
"""
query2 = """
本月各类商品的销售额是多少？
"""
query3 = """
谁最爱买华为手机？一共买了多少部？是不是代表他爱国？
"""
query4 = """
谁的退货次数最多？需要对该用户进行特别关注，以防恶意刷单
"""
query5 = """
当前每种订单状态下各有多少个订单？
"""
query6 = """
最近一周最主要的退款原因是什么？
"""
query7 = """
购买力前5的用户有哪些，各消费了多少？我需要他们详细资料
"""
query8 = """
谁最爱吃奥利奥？爱到什么程度
"""

# create nodes
begin = langpipe.LPBegin('begin_node')
sqlcreator = langpipe.LPSQLCreator('sql_creator', ddl_desc, 'qwen2.5:32b')
dbsearch = sample_nodes.LPDBSearch('db_search', 'shop.db')
aggregator = langpipe.LPAggregator('aggregator', None, 'qwen2.5:32b')
end = langpipe.LPEnd('end_node')

# link together
begin.link(sqlcreator)
sqlcreator.link(dbsearch)
dbsearch.link(aggregator)
aggregator.link(end)

# input what you want to
begin.input(query8, None, False)

# visualize the pipeline with data flow
print('-----board for debug purpose-----')
renderer = langpipe.LPBoardRender(node_size=100)
renderer.render(begin)



