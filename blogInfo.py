import mysql.connector

# 创建数据库链接
connection = mysql.connector.connect(
    user='your_username',
    password='your_password',
    host='localhost',
    database='blogInfo'
)


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
    input_verificate_code VARCHAR(255),
    verificate_code_created TIMESTAMP,
    password VARCHAR(255)
)
''')

# 创建posts表
cursor.execute('''
CREATE TABLE posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL
)
''')

# 插入示例数据到posts表
cursor.execute("INSERT INTO posts (title, content) VALUES (%s, %s)",
               ('学习Flask1', 'flask教程第一部分'))
cursor.execute("INSERT INTO posts (title, content) VALUES (%s, %s)",
               ('学习Flask2', 'flask教程第二部分'))

# 提交数据
connection.commit()

# 关闭游标和连接
cursor.close()
connection.close()
