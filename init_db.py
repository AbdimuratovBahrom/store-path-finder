import sqlite3
import re

# Попытка импортировать блок-данные, если у тебя они есть
try:
    from block1_data import get_block1_data
except Exception:
    get_block1_data = lambda: []

try:
    from block2_data import get_block2_data
except Exception:
    get_block2_data = lambda: []

try:
    from block3_data import get_block3_data
except Exception:
    get_block3_data = lambda: []

try:
    from block38_data import get_block38_data
except Exception:
    get_block38_data = lambda: []

try:
    from blockGiper_data import get_blockGiper_data
except Exception:
    get_blockGiper_data = lambda: []

# === Специфические объекты, которые ты прислал ===
SPECIFIC_OBJECTS = {
    "1-блок": [
        {
            'path': 'ТП-тинаник > Т1 > АВР > ЩР > 1-блок > Ряд O > ШР-сомсохона > ШО-1-ошхона > 1-ошхона(1-линия)',
            'shops': ['1-ошхона(1-линия)']
        },
        {
            'path': 'ТП-6699 > Т2 > ВРУ3 > ЩР3 > 1-блок > Ряд O > ШО-1-ошхона > 1-ошхона(2-линия)',
            'shops': ['1-ошхона(2-линия)']
        },
        {
            'path': 'ТП-6699 > Т1 > ВРУ3 > ЩР3 > 1-блок > Ряд Офис > Офис-дизель шит (1-линия) > Офис',
            'shops': ['Офис']
        },
        {
            'path': 'ТП-6699 > Т1 > ВРУ3 > ЩР3 > 1-блок > Ряд Офис > Офис-дизель шит (1-линия) > ШО-1-блок > 1-блок освищение',
            'shops': ['1-блок освищение']
        },
        {
            'path': 'ТП-6699 > Т1 > ВРУ3 > ЩР3 > 1-блок > Ряд Офис > Офис-дизель шит (1-линия) > ШО-режим > Режим хонаси',
            'shops': ['Режим хонаси']
        },
        {
            'path': 'ТП-6699 > Т1 > ВРУ5 > ЩР6 > 1-блок > Ряд F > Блогер хонаси',
            'shops': ['Блогер хонаси']
        },
        {
            'path': 'ТП-4768 > Т1 > АВР(ЩР18) > ЩР-Vip > 1-блок > Ряд L > Печенье цех-3-пост',
            'shops': ['Печенье цех-3-пост']
        },
        {
            'path': 'ТП-4768 > Т1 > АВР(ЩР5) > 1-блок > Ряд R > ШО-R3',
            'shops': ['освещение ряда Q и V']
        },
    ],
    "2-блок": [
        {
            'path': 'ТП-6699 > Т1 > 2-блок шитовой > Шит-2 > 2-блок > Ряд S > ШО-2 > ШО-4',
            'shops': ['1-пост(5-арка)']
        },
        {
            'path': 'ТП-6699 > Т1 > ВРУ3 > ЩР3 > 1-блок > Офис-дизель шит (1-линия) > ШО-7-пост > 2-блок > Ряд S > ШО-2',
            'shops': ['1-пост(5-арка-дизель линия:шлакбаун)']
        },
        {
            'path': 'ТП-6699 > Т1 > 2-блок шитовой > Шит-2 > 2-блок >  Ряд U ',
            'shops': ['9-пост Гамбургер бутка','9-пост охрана']
        },
        {
            'path': 'ТП-6699 > Т1 > 2-блок шитовой > Шит-6 > 2-блок >  Ряд U ',
            'shops': ['35-пост Гамбургер бутка','35-пост охрана']
        },
    ],
    "3-блок": [
        {
            'path': 'ТП-4768 > Т2 > АВР(ЩР8) > 3-блок > ЩР8 > Ряд 1 > ШО-7',
            'shops': ['3-блок туалет,сантехникхона,кател']
        },
        {
            'path': 'ТП-4768 > Т2 > АВР(ЩР10) > 3-блок > ЩР10',
            'shops': ['Пустой']
        },
        {
            'path': 'ТП-4768 > Т1 > АВР(ЩР6) > 3-блок > ШО-ZARIN',
            'shops': ['Маг-ZARIN']
        },
        {
            'path': 'ТП-4768 > Т2 > АВР(ЩР7) > 3-блок > Ряд 1 > ШО-29',
            'shops': ['13-пост', 'Пирошкихона1', 'Пирошкихона2']
        },
        {
            'path': 'ТП-4768 > Т1 > АВР(ЩР11) > 3-блок > ЩР11 > Ряд 3 > ШО-20',
            'shops': ['освещение 3-блока:(магазин 3-57)']
        },
        {
            'path': 'ТП-4768 > Т2 > АВР(ЩР17) > 3-блок > ЩР17 > Ряд 11 > ШО-освещение 11-ряда',
            'shops': ['ШО-освещение 11-ряда']
        },
        {
            'path': 'ТП-4768 > Т2 > АВР(ЩР17) > 3-блок > ЩР17 > Ряд 11 > Кабинет электриков',
            'shops': ['Кабинет электриков']
        },
        {
            'path': 'ТП-5353 > Т2 > АВР(ЩР16) > 3-блок > ЩР16 > Ряд 5 > ШО-28',
            'shops': ['13-пост', 'Paynet']
        },
    ]
}

# === Создание/заполнение БД ===
conn = sqlite3.connect("shops.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS shops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    block TEXT,
    row TEXT,
    shop TEXT,
    path TEXT
)
""")

# очистим старую таблицу
cursor.execute("DELETE FROM shops")
conn.commit()

# Вставим данные из блоков, если они есть (формат: list of dicts with keys 'path' and 'shops')
def insert_block_from_func(block_name, func):
    try:
        for entry in func():
            path = entry.get("path")
            shops = entry.get("shops", [])
            # попытаемся извлечь ряд из path
            row_name = None
            for part in path.split(">"):
                p = part.strip()
                if p.startswith("Ряд"):
                    row_name = p.replace("Ряд", "").strip()
                    break
            for s in shops:
                cursor.execute("INSERT INTO shops (block, row, shop, path) VALUES (?, ?, ?, ?)",
                               (block_name, row_name, s, path))
    except Exception:
        # если формат другой — просто пропускаем
        pass

insert_block_from_func("1-блок", get_block1_data)
insert_block_from_func("2-блок", get_block2_data)
insert_block_from_func("3-блок", get_block3_data)
insert_block_from_func("38-склад", get_block38_data)

# гипермаркет
try:
    for entry in get_blockGiper_data():
        path = entry.get("path")
        shops = entry.get("shops", [])
        for s in shops:
            cursor.execute("INSERT INTO shops (block, row, shop, path) VALUES (?, ?, ?, ?)",
                           ("Гипермаркет", None, s, path))
except Exception:
    pass

# Вставляем специфические объекты
for block, entries in SPECIFIC_OBJECTS.items():
    target_block = "Специфические объекты"
    for entry in entries:
        path = entry["path"]
        shops = entry.get("shops", [])
        # если в path есть "Ряд ..." — запомним ряд, иначе "Спец"
        row_name = None
        for part in path.split(">"):
            p = part.strip()
            if p.startswith("Ряд"):
                row_name = p.replace("Ряд", "").strip()
                break
        if row_name is None:
            row_name = "Спец"
        for s in shops:
            cursor.execute("INSERT INTO shops (block, row, shop, path) VALUES (?, ?, ?, ?)",
                           (target_block, row_name, s, path))

conn.commit()
conn.close()
print("✅ Database initialized. Если у тебя есть block*_data.py они добавлены; также добавлены SPECIFIC_OBJECTS.")
