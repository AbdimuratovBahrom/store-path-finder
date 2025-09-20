# import sqlite3

# def test_db():
#     conn = sqlite3.connect('shops.db')
#     c = conn.cursor()
#     c.execute("SELECT block, shop_number, path FROM shops WHERE shop_number = 'Маг-1'")
#     result = c.fetchall()
#     print("Результат запроса для Маг-1:", result)
#     conn.close()

# if __name__ == '__main__':
#     test_db()


import sqlite3

def test_query(id):
    conn = sqlite3.connect('shops.db')
    cursor = conn.cursor()
    # ...existing code...
    cursor.execute('SELECT path FROM shops WHERE shop_number = ?', (shop,))
# ...existing code...
    result = cursor.fetchall()
    conn.close()
    return result

if __name__ == '__main__':
    test_shops = ['Маг-1', 'Склад-1', '42']  # Примеры ID магазинов
    for shop in test_shops:
        print(f"Testing query for {shop}:", test_query(shop))