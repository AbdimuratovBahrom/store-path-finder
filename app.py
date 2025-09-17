from flask import Flask, render_template, request, jsonify
import sqlite3
import re

app = Flask(__name__)

def extract_row(path):
    match = re.search(r'Ряд\s+([A-Za-zА-Яа-я0-9]+)', path)
    return match.group(1) if match else ''

def sort_rows(rows):
    # Сортировка рядов: числовые (Ряд 1, Ряд 2) по числу, буквенные (Ряд L, Ряд Q) по алфавиту
    def key(row):
        match = re.match(r'Ряд (\d+)', row)
        return (0, int(match.group(1))) if match else (1, row)
    return sorted(rows, key=key)

def sort_stores(stores):
    # Сортировка магазинов: числовые (Маг-1, Маг-1А) по числу, остальные по алфавиту
    def key(store):
        match = re.match(r'Маг-(\d+)([А-Яа-я]?)', store)
        if match:
            num = int(match.group(1))
            suffix = match.group(2) or ''
            return (0, num, suffix)
        return (1, store)
    return sorted(stores, key=key)

@app.route('/')
def index():
    conn = sqlite3.connect('shops.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT block FROM shops')
    blocks = sorted([row[0] for row in cursor.fetchall()])  # Сортировка блоков по алфавиту
    conn.close()
    return render_template('index.html', blocks=blocks)

@app.route('/get_rows')
def get_rows():
    block = request.args.get('block')
    if not block:
        return jsonify({'rows': []})
    
    conn = sqlite3.connect('shops.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT path FROM shops WHERE block = ?', (block,))
    paths = [row[0] for row in cursor.fetchall()]
    rows = sort_rows(sorted(set([extract_row(path) for path in paths if extract_row(path)])))
    conn.close()
    return jsonify({'rows': rows})

@app.route('/get_stores')
def get_stores():
    block = request.args.get('block')
    row = request.args.get('row')
    if not block or not row:
        return jsonify({'stores': []})
    
    conn = sqlite3.connect('shops.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT shop_number FROM shops WHERE block = ? AND path LIKE ?', (block, f'%Ряд {row}%'))
    stores = sort_stores([row[0] for row in cursor.fetchall()])
    conn.close()
    return jsonify({'stores': stores})

@app.route('/get_path')
def get_path():
    block = request.args.get('block')
    row = request.args.get('row')
    store = request.args.get('store')
    if not block or not row or not store:
        return jsonify({'path': ''})
    
    conn = sqlite3.connect('shops.db')
    cursor = conn.cursor()
    cursor.execute('SELECT path FROM shops WHERE block = ? AND shop_number = ? AND path LIKE ?', 
                  (block, store, f'%Ряд {row}%'))
    result = cursor.fetchone()
    conn.close()
    path = result[0] if result else ''
    if path:
        path = f"{path} > {store}"  # Добавляем конечный магазин к пути
    return jsonify({'path': path})



if __name__ == '__main__':
    app.run(debug=True)