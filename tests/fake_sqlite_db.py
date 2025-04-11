import sqlite3
import random
from datetime import datetime
from faker import Faker

"""
模拟生成一个shop.db sqlite数据库，数据库包含5张数据表，shop.db文件供 11-sql_rag.py 脚本使用。
"""

# 初始化
fake = Faker("zh_CN")
conn = sqlite3.connect("shop.db")
cursor = conn.cursor()

# 建表
cursor.executescript("""
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
""")

# 清空旧数据（按依赖顺序删除）
cursor.executescript("""
PRAGMA foreign_keys = OFF;
DELETE FROM refunds;
DELETE FROM order_items;
DELETE FROM orders;
DELETE FROM products;
DELETE FROM users;
PRAGMA foreign_keys = ON;
""")

# 插入 10 个用户
users = [
    ("张三", "zhangsan01@163.com", fake.sha256()),
    ("李四", "lisi_88@163.com", fake.sha256()),
    ("王五", "wangwu2023@163.com", fake.sha256()),
    ("赵六", "zhaoliu@163.com", fake.sha256()),
    ("钱七", "qianqi@163.com", fake.sha256()),
    ("孙八", "sunba_001@163.com", fake.sha256()),
    ("周九", "zhoujiu@163.com", fake.sha256()),
    ("吴十", "wushi666@163.com", fake.sha256()),
    ("郑强", "zhengqiang@163.com", fake.sha256()),
    ("冯刚", "fenggang@163.com", fake.sha256())
]
cursor.executemany("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)", users)
cursor.execute("SELECT id FROM users")
user_ids = [row[0] for row in cursor.fetchall()]

# 插入 30 个商品
products = [
    ("可口可乐", "经典口味碳酸饮料，畅爽解渴", 3.50, random.randint(0, 100)),
    ("百事可乐", "清爽可乐饮品，口感独特", 3.20, random.randint(0, 100)),
    ("雪碧", "柠檬味碳酸饮料，清新提神", 3.00, random.randint(0, 100)),
    ("农夫山泉", "天然矿泉水，饮用安全健康", 2.00, random.randint(0, 100)),
    ("康师傅绿茶", "绿茶口味，清凉解渴", 3.80, random.randint(0, 100)),
    ("脉动", "维生素饮料，运动后补水佳品", 4.50, random.randint(0, 100)),
    ("乐事薯片", "原味薯片，酥脆可口", 5.50, random.randint(0, 100)),
    ("奥利奥", "巧克力夹心饼干，甜蜜美味", 6.00, random.randint(0, 100)),
    ("卫龙辣条", "经典辣条，香辣十足", 2.50, random.randint(0, 100)),
    ("小米手机", "性价比高的智能手机", 1999.00, random.randint(0, 100)),
    ("华为手机", "高性能安卓手机", 3499.00, random.randint(0, 100)),
    ("iPhone手机", "苹果品牌智能手机", 5999.00, random.randint(0, 100)),
    ("电动牙刷", "声波震动清洁牙齿", 129.99, random.randint(0, 100)),
    ("剃须刀", "男士专用电动剃须刀", 89.50, random.randint(0, 100)),
    ("洗发水", "去屑清爽型洗发水", 29.90, random.randint(0, 100)),
    ("沐浴露", "滋润保湿型沐浴露", 35.00, random.randint(0, 100)),
    ("洗面奶", "控油清洁型洗面奶", 22.80, random.randint(0, 100)),
    ("护肤霜", "保湿滋润型护肤霜", 45.60, random.randint(0, 100)),
    ("润唇膏", "防干裂润唇膏", 15.00, random.randint(0, 100)),
    ("蓝牙耳机", "无线蓝牙耳机，降噪功能", 199.00, random.randint(0, 100)),
    ("充电宝", "移动电源，快充大容量", 89.90, random.randint(0, 100)),
    ("鼠标", "无线鼠标，人体工学设计", 49.90, random.randint(0, 100)),
    ("键盘", "机械键盘，手感极佳", 159.00, random.randint(0, 100)),
    ("U盘", "64GB金属U盘，数据存储", 39.99, random.randint(0, 100)),
    ("移动硬盘", "1TB移动硬盘，快速传输", 359.00, random.randint(0, 100)),
    ("显示器", "24英寸高清显示器", 699.00, random.randint(0, 100)),
    ("路由器", "双频无线路由器", 129.00, random.randint(0, 100)),
    ("电饭煲", "智能电饭煲，多种烹饪模式", 259.00, random.randint(0, 100)),
    ("电磁炉", "家用电磁炉，节能高效", 199.00, random.randint(0, 100)),
    ("吸尘器", "无线手持吸尘器", 499.00, random.randint(0, 100))
]
cursor.executemany("INSERT INTO products (name, description, price, stock) VALUES (?, ?, ?, ?)", products)
cursor.execute("SELECT id, price FROM products")
product_list = cursor.fetchall()

# 插入 50 个订单
statuses = ['pending', 'paid', 'shipped', 'completed', 'cancelled']
orders = []
for _ in range(50):
    uid = random.choice(user_ids)
    status = random.choice(statuses)
    order_date = fake.date_time_between(start_date="-30d", end_date="now")
    total = round(random.uniform(50, 2000), 2)
    orders.append((uid, status, total, order_date))
cursor.executemany("INSERT INTO orders (user_id, status, total_amount, created_at) VALUES (?, ?, ?, ?)", orders)
cursor.execute("SELECT id FROM orders")
order_ids = [row[0] for row in cursor.fetchall()]

# 插入 200 个订单项
order_items = []
for _ in range(200):
    order_id = random.choice(order_ids)
    product_id, price = random.choice(product_list)
    quantity = random.randint(1, 5)
    order_items.append((order_id, product_id, quantity, price))
cursor.executemany("INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)", order_items)

# 插入 20 条退款记录
refunds = []
reasons = ['价格太贵', '快递太慢', '商品不符合广告宣传', '商品破损、质量问题', '买错了']
for _ in range(20):
    order_id = random.choice(order_ids)
    amount = round(random.uniform(10, 500), 2)
    reason = random.choice(reasons)
    date = fake.date_time_between(start_date='-7d', end_date='now')
    refunds.append((order_id, amount, reason, date))
cursor.executemany("INSERT INTO refunds (order_id, refund_amount, reason, refund_date) VALUES (?, ?, ?, ?)", refunds)

# 提交保存
conn.commit()
print("✅ 已插入模拟数据完成")

# 输出5张表的数据记录
tables=["users", "products", "orders", "order_items", "refunds"]
for table in tables:
    cursor.execute(f"SELECT * FROM {table}")
    rows = cursor.fetchall()
    print(f"\n数据表：{table}")
    for row in rows:
        print(row)
    print("------")

cursor.close()
conn.close()