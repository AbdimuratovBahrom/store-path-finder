import sqlite3
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Импорт данных с проверкой переменных или функций
def get_data(module_name, data_name, func_name):
    try:
        module = __import__(module_name)
        if hasattr(module, func_name):
            logger.debug(f"Using function {func_name} from {module_name}")
            return getattr(module, func_name)()
        elif hasattr(module, data_name):
            logger.debug(f"Using variable {data_name} from {module_name}")
            return getattr(module, data_name)
        else:
            raise ImportError(f"Neither {data_name} nor {func_name} found in {module_name}")
    except ImportError as e:
        logger.error(f"Import error for {module_name}: {e}")
        raise

def init_db():
    logger.debug("Initializing database...")
    conn = sqlite3.connect('shops.db')
    cursor = conn.cursor()
    
    # Создание таблицы
    cursor.execute('''CREATE TABLE IF NOT EXISTS shops (
        block TEXT,
        shop_number TEXT,
        path TEXT
    )''')
    logger.debug("Table 'shops' created or already exists")
    
    # Очистка таблицы
    cursor.execute('DELETE FROM shops')
    logger.debug("Table 'shops' cleared")
    
    # Вставка данных
    for block, module_name in [
        ('1-блок', 'block1_data'),
        ('2-блок', 'block2_data'),
        ('3-блок', 'block3_data'),
        ('38-склад', 'block38_data')
    ]:
        try:
            data = get_data(module_name, f"{module_name}", f"get_{module_name}")
            logger.debug(f"Data for block {block}: {data[:5]}")  # Логируем первые 5 записей
            for entry in data:
                path = entry['path']
                for shop_number in entry['shops']:
                    cursor.execute(
                        'INSERT INTO shops (block, shop_number, path) VALUES (?, ?, ?)',
                        (block, shop_number, path)
                    )
            logger.debug(f"Inserted data for block: {block}")
        except Exception as e:
            logger.error(f"Error inserting data for block {block}: {e}")

    conn.commit()
    logger.debug("Database changes committed")
    conn.close()
    logger.debug("Database connection closed")

    import re


if __name__ == '__main__':
    init_db()