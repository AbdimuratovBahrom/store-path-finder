import sqlite3
import re
from block1_data import get_block1_data
from block2_data import block2_data
from block3_data import get_block3_data
from block38_data import get_block38_data

def parse_store_range(store_str, block_name):
    stores = []
    parts = store_str.replace(' ', '').split(',')
    
    # Список названий, к которым не добавляется префикс "Маг-"
    no_prefix_shops = [
        '35-постГамбургербутка',
        '35-постохрана',
        '9-постГамбургербутка',
        '9-постохрана',
        '1-пост(5-арка-дизельлиния:шлакбаун)',
        '1-пост(5-арка)'
    ]
    
    # Для 3-блок числа 1–11 без префикса "Маг-"
    no_prefix_numbers = [str(i) for i in range(1, 12)]  # '1', '2', ..., '11'
    
    for part in parts:
        if '...' in part:
            try:
                start, end = part.split('...')
                start_match = re.match(r'(\D*)(\d+)(.*)', start)
                end_match = re.match(r'(\D*)(\d+)(.*)', end)
                if start_match and end_match:
                    prefix = start_match.group(1) or ''
                    start_num = int(start_match.group(2))
                    end_num = int(end_match.group(2))
                    suffix = start_match.group(3) or ''
                    for i in range(start_num, end_num + 1):
                        store_name = f"{prefix}{i}{suffix}"
                        # Для 38-склад не добавляем префикс "Маг-"
                        if block_name == '38-склад':
                            stores.append(store_name)
                        # Для других блоков проверяем исключения
                        elif store_name in no_prefix_shops or (block_name == '3-блок' and store_name in no_prefix_numbers):
                            stores.append(store_name)
                        else:
                            stores.append(f"Маг-{store_name}" if store_name[0].isdigit() else store_name)
                else:
                    stores.append(part)
            except (ValueError, AttributeError):
                stores.append(part)
        else:
            # Для 38-склад не добавляем префикс "Маг-"
            if block_name == '38-склад':
                stores.append(part)
            # Для других блоков проверяем исключения
            elif part in no_prefix_shops or (block_name == '3-блок' and part in no_prefix_numbers):
                stores.append(part)
            else:
                if part and not (part[0].isdigit() or part.startswith('1-') or part.startswith('9-') or part.startswith('35-')):
                    stores.append(part)
                else:
                    stores.append(f"Маг-{part}" if part else part)
    
    # Сортировка для 38-склад: магазины, начинающиеся с "38", идут первыми
    if block_name == '38-склад':
        stores.sort(key=lambda x: (not x.startswith('38'), x))
    # Сортировка для 3-блок: по числовому значению или строке
    elif block_name == '3-блок':
        def sort_key(x):
            match = re.search(r'\d+', x)
            if match:
                return (0, int(match.group()))
            return (1, x)
        stores.sort(key=sort_key)
    
    return stores

def add_shops_to_db(data, block_name, cursor):
    for entry in data:
        path = entry['path']
        shops = entry['shops']
        # Обрабатываем каждый магазин отдельно
        for shop in shops:
            parsed_shops = parse_store_range(shop, block_name)
            for parsed_shop in parsed_shops:
                cursor.execute('''
                    INSERT OR REPLACE INTO shops (block, shop_number, path)
                    VALUES (?, ?, ?)
                ''', (block_name, parsed_shop, path))
                # Отладочный вывод
                print(f"Добавлено: block={block_name}, shop={parsed_shop}, path={path}")

def init_db():
    conn = sqlite3.connect('shops.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            block TEXT,
            shop_number TEXT,
            path TEXT
        )
    ''')
    
    add_shops_to_db(get_block1_data(), '1-блок', cursor)
    add_shops_to_db(block2_data, '2-блок', cursor)
    add_shops_to_db(get_block3_data(), '3-блок', cursor)
    add_shops_to_db(get_block38_data(), '38-склад', cursor)
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()