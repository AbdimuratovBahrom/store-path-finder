import sqlite3
from block1_data import get_block1_data
from block2_data import block2_data
from block3_data import get_block3_data
from block38_data import get_block38_data

def extract_row(path, block):
    path_parts = path.split('>')
    # Ищем элемент, начинающийся с "Ряд "
    for part in path_parts:
        part = part.strip()
        if part.startswith('Ряд '):
            return part
    # Для 38-склада ряды не всегда явно указаны, возвращаем "Ряд 38"
    if block == '38-склад':
        return 'Ряд 38'
    # Если ряд не найден, возвращаем None
    return None

def create_database():
    conn = sqlite3.connect('shops.db')
    cursor = conn.cursor()
    
    # Удаление существующей таблицы
    cursor.execute('DROP TABLE IF EXISTS shops')
    
    # Создание таблицы
    cursor.execute('''
        CREATE TABLE shops (
            block TEXT,
            row TEXT,
            shop_id TEXT,
            path TEXT
        )
    ''')

    # Импорт данных
    for data_source, block_name in [
        (get_block1_data(), '1-блок'),
        (block2_data, '2-блок'),
        (get_block3_data(), '3-блок'),
        (get_block38_data(), '38-склад')
    ]:
        for entry in data_source:
            path = entry['path']
            shops = entry['shops']
            row = extract_row(path, block_name)
            if not row:
                print(f"Warning: No valid row found for path {path} in block {block_name}")
                continue
            for shop in shops:
                try:
                    cursor.execute(
                        'INSERT INTO shops (block, row, shop_id, path) VALUES (?, ?, ?, ?)',
                        (block_name, row, shop, path)
                    )
                except sqlite3.Error as e:
                    print(f"Error inserting data for shop {shop} in {path}: {e}")
    
    conn.commit()
    conn.close()
    print("Data imported successfully.")

if __name__ == '__main__':
    try:
        create_database()
    except sqlite3.Error as e:
        print(f"Database error: {e}")