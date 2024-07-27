import sqlite3

def check_table_structure():
    conn = sqlite3.connect('userInfo.db')
    cursor = conn.cursor()
    cursor.execute('PRAGMA table_info(userInfo)')
    columns = cursor.fetchall()
    for column in columns:
        print(column)

    conn.close()

if __name__ == '__main__':
    check_table_structure()
