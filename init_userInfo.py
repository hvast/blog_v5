import sqlite3
# 创建数据库链接
#user_connection = sqlite3.connect('userInfo.db')
def initialize_db():
    user_info_connection = sqlite3.connect('userInfo.db')
    user_info_cursor = user_info_connection.cursor()

    user_info_cursor.execute('DROP TABLE IF EXISTS userInfo')
    user_info_cursor.execute('''
    CREATE TABLE userInfo (
        userid INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        username VARCHAR NOT NULL,
        verificate_code VARCHAR NOT NULL,
        input_verificate_code VARCHAR NOT NULL,
        verificate_code_created TIMESTAMP,
        password TEXT NOT NULL
    )
    ''')

    user_info_connection.commit()
    user_info_connection.close()

if __name__ == '__main__':
    initialize_db()