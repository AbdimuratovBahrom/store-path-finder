import sqlite3

DB_FILE = "shops.db"

def test_all_data():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Проверим, есть ли таблица
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='shops'")
    if not cursor.fetchone():
        print("❌ Таблица 'shops' не найдена.")
        conn.close()
        return

    # Количество строк
    cursor.execute("SELECT COUNT(*) FROM shops")
    total = cursor.fetchone()[0]
    print(f"✅ Всего записей в shops: {total}")

    # Выведем первые 20 строк для проверки
    print("\n📋 Первые 20 записей:")
    cursor.execute("SELECT block, row, shop_number, path FROM shops LIMIT 20")
    for row in cursor.fetchall():
        print(row)

    conn.close()

def test_query(shop_number):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT block, row, shop_number, path FROM shops WHERE shop_number = ?",
        (shop_number,)
    )
    results = cursor.fetchall()
    conn.close()
    return results

if __name__ == "__main__":
    test_all_data()

    test_shops = ["22", "79", "1A", "140a", "38-автостансия"]
    for shop in test_shops:
        print(f"\n🔎 Testing query for {shop}:")
        results = test_query(shop)
        if results:
            for r in results:
                print(f"  Block: {r[0]} | Row: {r[1]} | Shop: {r[2]} | Path: {r[3]}")
        else:
            print("  ❌ Ничего не найдено")
