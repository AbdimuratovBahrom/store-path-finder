import sqlite3
from block1_data import get_block1_data
from block2_data import get_block2_data
from block3_data import get_block3_data
from block38_data import get_block38_data
from blockGiper_data import get_blockGiper_data

conn = sqlite3.connect("shops.db")
cursor = conn.cursor()

# Создаём таблицу
cursor.execute("""
CREATE TABLE IF NOT EXISTS shops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    block TEXT,
    row TEXT,
    shop_number TEXT,
    path TEXT
)
""")

# Очистим
cursor.execute("DELETE FROM shops")

def insert_block(block_name, data_func):
    """ Для блоков 1,2,3,38 — вставка с выделением ряда """
    for entry in data_func():
        path = entry["path"]
        shops = entry["shops"]

        # вытащим ряд (после слова 'Ряд ...')
        row_name = None
        parts = path.split(">")
        for part in parts:
            part = part.strip()
            if part.startswith("Ряд"):
                row_name = part.replace("Ряд", "").strip()
                break

        for shop in shops:
            cursor.execute(
                "INSERT INTO shops (block, row, shop_number, path) VALUES (?, ?, ?, ?)",
                (block_name, row_name, shop, path)
            )

# Заполняем блоки
insert_block("1-блок", get_block1_data)
insert_block("2-блок", get_block2_data)
insert_block("3-блок", get_block3_data)
insert_block("38-склад", get_block38_data)

# Гипермаркет — тут ряд не нужен
for entry in get_blockGiper_data():
    path = entry["path"]
    for shop in entry["shops"]:
        cursor.execute(
            "INSERT INTO shops (block, row, shop_number, path) VALUES (?, ?, ?, ?)",
            ("Гипермаркет", None, shop, path)
        )

conn.commit()
conn.close()
print("✅ Database initialized with all blocks and Гипермаркет.")
