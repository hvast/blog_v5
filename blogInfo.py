import mysql.connector
from dotenv import load_dotenv
import os

# 加载 .env 文件中的环境变量
load_dotenv('/root/blog_v5/privacyInfo.env')

# 创建数据库链接
connection = mysql.connector.connect(
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
)

# 创建新的数据库
if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS blogInfo")
            cursor.execute("USE blogInfo")

# 创建一个执行句柄，用来执行后面的语句
cursor = connection.cursor()

# 删除表（如果存在），然后创建新的表
cursor.execute('DROP TABLE IF EXISTS userInfo')
cursor.execute('DROP TABLE IF EXISTS posts')

# 创建userInfo表
cursor.execute('''
CREATE TABLE userInfo (
    userid INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255),
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    username VARCHAR(255),    
    verificate_code VARCHAR(255),
    verificate_code_created TIMESTAMP,
    password VARCHAR(255)
)
''')

# 创建posts表
cursor.execute('''
CREATE TABLE posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    userid INT ,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL
)
''')

# 关闭游标和连接
cursor.close()
connection.close()
