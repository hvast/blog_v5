import sqlite3
# 创建数据库链接
connection = sqlite3.connect('database.db')
# 执行数据库语句
with open('db.sql') as f:
    connection.executescript(f.read())

# 创建一个执行句柄，用来执行后面的语句
cur = connection.cursor()

# 插入两条文章，只需填写title和content，id和created会自动填写
cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
            ('学习Flask1', 'flask教程第一部分')
            )

cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
            ('学习Flask2', 'flask教程第一部分')
            )

#提交数据
connection.commit()
connection.close()