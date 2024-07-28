import sqlite3
# 创建数据库链接

def initialize_db():
    conn = sqlite3.connect('userInfo.db')
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS userInfo')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS userInfo (
        userid INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        username VARCHAR,
        verificate_code VARCHAR,
        input_verificate_code VARCHAR,
        verificate_code_created TIMESTAMP,
        password TEXT
    )
    ''')

    conn.commit()
    conn.close()
 

if __name__ == '__main__':
    initialize_db()