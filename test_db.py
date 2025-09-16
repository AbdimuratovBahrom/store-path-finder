import sqlite3

def test_db():
    conn = sqlite3.connect('shops.db')
    c = conn.cursor()
    c.execute("SELECT block, shop_number, path FROM shops WHERE shop_number = 'Маг-1'")
    result = c.fetchall()
    print("Результат запроса для Маг-1:", result)
    conn.close()

if __name__ == '__main__':
    test_db()