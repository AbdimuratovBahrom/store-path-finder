import sqlite3

def get_path(store_name):
    conn = sqlite3.connect('stores.db')
    c = conn.cursor()
    c.execute("SELECT path FROM stores WHERE name = ?", (store_name,))
    result = c.fetchone()
    conn.close()
    if result:
        return result[0] + ' > ' + store_name
    else:
        return "Магазин не найден"

# Пример использования
print(get_path("Маг-1"))
print(get_path("Маг-1g"))
print(get_path("освещение 3-блока"))