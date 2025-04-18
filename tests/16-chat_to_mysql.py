import langpipe

# define DDL description for mysql
mysql_ddl_desc = """
-- ----------------------------
-- 用户表：users
-- 存储注册用户的基本信息
-- ----------------------------
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户唯一ID，自增主键',
    username VARCHAR(255) NOT NULL UNIQUE COMMENT '用户名，必须唯一且非空',
    email VARCHAR(255) NOT NULL UNIQUE COMMENT '用户邮箱，必须唯一且非空',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希值，用于存储加密后的密码',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间，默认为当前时间'
) COMMENT = '存储注册用户的基本信息';

-- ----------------------------
-- 商品表：products
-- 存储上架商品的详细信息
-- ----------------------------
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '商品唯一ID，自增主键',
    name VARCHAR(255) NOT NULL COMMENT '商品名称，非空',
    description TEXT COMMENT '商品描述，可选',
    price DECIMAL(10, 2) NOT NULL COMMENT '商品单价，使用DECIMAL表示小数',
    stock INT DEFAULT 0 COMMENT '商品库存数量，默认0',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '上架时间，默认为当前时间'
) COMMENT = '存储上架商品的详细信息';

-- ----------------------------
-- 订单表：orders
-- 记录用户提交的订单信息
-- ----------------------------
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '订单唯一ID，自增主键',
    user_id INT NOT NULL COMMENT '下单用户的ID，关联 users(id)',
    status ENUM('pending', 'paid', 'shipped', 'completed', 'cancelled') DEFAULT 'pending' COMMENT '订单状态',
    total_amount DECIMAL(10, 2) NOT NULL COMMENT '订单总金额',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '订单创建时间',
    FOREIGN KEY (user_id) REFERENCES users(id)
) COMMENT = '记录用户提交的订单信息';

-- ----------------------------
-- 订单项表：order_items
-- 记录每个订单中包含哪些商品及数量
-- ----------------------------
CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '订单项唯一ID，自增主键',
    order_id INT NOT NULL COMMENT '所属订单ID，关联 orders(id)',
    product_id INT NOT NULL COMMENT '商品ID，关联 products(id)',
    quantity INT NOT NULL COMMENT '购买数量',
    unit_price DECIMAL(10, 2) NOT NULL COMMENT '下单时的商品单价',
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
) COMMENT = '记录每个订单中包含哪些商品及数量';

-- ----------------------------
-- 退款表：refunds
-- 记录订单退款的请求和处理信息
-- ----------------------------
CREATE TABLE IF NOT EXISTS refunds (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '退款记录ID，自增主键',
    order_id INT NOT NULL COMMENT '关联的订单ID',
    refund_amount DECIMAL(10, 2) NOT NULL COMMENT '退款金额',
    reason TEXT COMMENT '退款原因，可选',
    refund_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '退款时间，默认为当前时间',
    FOREIGN KEY (order_id) REFERENCES orders(id)
) COMMENT = '记录订单退款的请求和处理信息';
"""

# create nodes
begin = langpipe.LPBegin('begin_node')
sqlcreator = langpipe.LPSQLCreator('sql_creator', mysql_ddl_desc, 'qwen2.5:7b')
end = langpipe.LPEnd('end_node', callback=(lambda x: 
                                           print(f'txt: {x['query']}\n'
                                                 f'sql: {x['final_out']}\n'
                                                 )), 
                                           debug=False, print_final_out=False)

# link together
begin.link(sqlcreator)
sqlcreator.link(end)

"""
chat to mysql, sample question (from mysql):
1. 哪些人买过可口可乐？都是什么时候买的，分别买了多少瓶
2. 本月各类商品的销售额是多少？
3. 谁最爱买华为手机？一共买了多少部？是不是代表他爱国？
4. 谁的退货次数最多？需要对该用户进行特别关注，以防恶意刷单
5. 当前每种订单状态下各有多少个订单？
6. 最近一周最主要的退款原因是什么？
7. 购买力前5的用户有哪些，各消费了多少？我需要他们详细资料
8. 谁最爱吃奥利奥？爱到什么程度

sample input & output:
>>>谁最爱吃奥利奥？爱到什么程度
txt: 谁最爱吃奥利奥？爱到什么程度
sql: SELECT u.username, COUNT(oi.quantity) AS love_level FROM users u JOIN order_items oi ON u.id = oi.user_id WHERE oi.product_id = (SELECT id FROM products WHERE name = '奥利奥') GROUP BY u.username ORDER BY love_level DESC;
"""
while True:
    input_txt = input('>>>')
    if input_txt == 'exit':
        break

    # input what you want to
    begin.input(input_txt)