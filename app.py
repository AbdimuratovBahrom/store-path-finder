
from flask import Flask, render_template, request, jsonify
import sqlite3
import re

app = Flask(__name__)

def sort_rows(rows):
    """Сортировка рядов: числовые (Ряд 1, Ряд 2) по числу, буквенные (Ряд L, Ряд Q) по алфавиту."""
    def row_key(row):
        match = re.match(r'Ряд (\d+)', row)
        if match:
            return (0, int(match.group(1)))  # Числовые ряды сортируются по числу
        return (1, row)  # Буквенные ряды сортируются по алфавиту
    return sorted(rows, key=row_key)

def sort_stores(stores):
    """Сортировка магазинов: числовые (Маг-1, Маг-1А) по числу, остальные по алфавиту."""
    def store_key(store):
        match = re.match(r'Маг-(\d+)([А-Яа-я]?)', store)
        if match:
            num = int(match.group(1))
            suffix = match.group(2) or ''
            return (0, num, suffix)  # Числовые магазины сортируются по числу и суффиксу
        return (1, store)  # Остальные сортируются по алфавиту
    return sorted(stores, key=store_key)

@app.route('/')
def index():
    print("Rendering index.html")  # Логирование
    conn = sqlite3.connect('stores.db')
    c = conn.cursor()
    c.execute('SELECT DISTINCT block FROM stores')
    blocks = sorted([row[0] for row in c.fetchall()])  # Сортировка блоков по алфавиту
    conn.close()
    print(f"Blocks fetched: {blocks}")  # Логирование
    return render_template('index.html', blocks=blocks)

@app.route('/get_rows', methods=['GET'])
def get_rows():
    block = request.args.get('block')
    print(f"Fetching rows for block: {block}")  # Логирование
    conn = sqlite3.connect('stores.db')
    c = conn.cursor()
    c.execute('SELECT DISTINCT row FROM stores WHERE block = ? AND row IS NOT NULL', (block,))
    rows = sort_rows([row[0] for row in c.fetchall()])  # Сортировка рядов
    conn.close()
    print(f"Rows found: {rows}")  # Логирование
    return jsonify(rows)

@app.route('/get_stores', methods=['GET'])
def get_stores():
    block = request.args.get('block')
    row = request.args.get('row')
    print(f"Fetching stores for block: {block}, row: {row}")  # Логирование
    conn = sqlite3.connect('stores.db')
    c = conn.cursor()
    c.execute('SELECT DISTINCT name FROM stores WHERE block = ? AND (row = ? OR row IS NULL)', (block, row))
    stores = sort_stores([row[0] for row in c.fetchall()])  # Сортировка магазинов
    conn.close()
    print(f"Stores found: {stores}")  # Логирование
    return jsonify(stores)

@app.route('/get_path', methods=['POST'])
def get_path():
    try:
        block = request.form.get('block')
        row = request.form.get('row')
        store = request.form.get('store')
        print(f"Fetching path for block: {block}, row: {row}, store: {store}")  # Логирование

        if not store:
            print("Error: 'store' parameter is missing in the request")
            return jsonify({'error': 'Параметр store отсутствует'}), 400

        conn = sqlite3.connect('stores.db')
        c = conn.cursor()
        query = 'SELECT path FROM stores WHERE block = ? AND (row = ? OR row IS NULL) AND name = ?'
        c.execute(query, (block, row, store))
        path = c.fetchone()
        conn.close()

        if path:
            # Добавляем имя магазина к пути, если оно еще не включено
            final_path = path[0]
            if not final_path.endswith(store):
                final_path = f"{final_path} > {store}"
            print(f"Path found: {final_path}")  # Логирование
            return jsonify({'path': final_path})
        else:
            print(f"No path found for block: {block}, row: {row}, store: {store}")  # Логирование
            return jsonify({'error': 'Путь не найден'}), 404
    except Exception as e:
        print(f"Error in get_path: {str(e)}")  # Логирование
        return jsonify({'error': f'Ошибка сервера: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
