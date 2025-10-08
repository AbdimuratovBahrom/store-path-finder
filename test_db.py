import sqlite3
import os

DB_FILE = "shops.db"

def connect_db():
    if not os.path.exists(DB_FILE):
        print(f"❌ База {DB_FILE} не найдена. Сначала запусти init_db.py")
        exit(1)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def print_blocks():
    conn = connect_db()
    cursor = conn.cursor()

    print("\n=== 📦 Список блоков ===")
    blocks = cursor.execute("SELECT DISTINCT block FROM shops ORDER BY block").fetchall()
    for b in blocks:
        print(f"🔹 {b['block']}")

    print("\n=== 📂 Ряды по блокам ===")
    for b in blocks:
        rows = cursor.execute("SELECT DISTINCT row FROM shops WHERE block = ? ORDER BY row", (b["block"],)).fetchall()
        print(f"\n🔹 Блок: {b['block']}")
        for r in rows:
            print(f"   ➡️ Ряд: {r['row']}")

    conn.close()

def test_query(keyword):
    conn = connect_db()
    cursor = conn.cursor()

    print(f"\n============================================================")
    print(f"🔎 Testing query for '{keyword}'")

    results = cursor.execute("""
        SELECT * FROM shops
        WHERE shop LIKE ? OR block LIKE ? OR row LIKE ? OR path LIKE ?
    """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")).fetchall()

    if not results:
        print("❌ Ничего не найдено")
    else:
        for r in results:
            print(f"Block: {r['block']} | Row: {r['row']} | Shop: {r['shop']} | Path: {r['path']}")

    conn.close()

if __name__ == "__main__":
    # Проверка структуры
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='shops'")
    table = cursor.fetchone()
    if not table:
        print("❌ Таблица 'shops' не найдена. Сначала запусти init_db.py")
        exit(1)

    # Вывод блоков и рядов
    print_blocks()

    # Тестовые запросы
    test_query("Офис")
    test_query("освещение")
    test_query("туалет")