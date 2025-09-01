from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('stores.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_blocks():
    return ['Блок 1', 'Блок 2', 'Блок 3']

def get_rows(block):
    block_id = block.split(' ')[1]  # Извлекаем номер блока, например, "3" из "Блок 3"
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT DISTINCT SUBSTR(path, INSTR(path, 'Ряд ')+4, INSTR(SUBSTR(path, INSTR(path, 'Ряд ')+4), ' >')-1) AS row FROM stores WHERE path LIKE ?", (f'%{block_id}-блок%',))
    rows = [row['row'] for row in c.fetchall()]
    conn.close()
    return sorted(rows)

def sort_stores(stores):
    def get_sort_key(store):
        name = store.replace('Маг-', '')
        if name.isdigit():
            return (1, int(name), '')
        if name.startswith('5a'):
            num = int(name[2:]) if name[2:].isdigit() else 0
            return (2, num, name)
        if name.endswith('g'):
            num = int(name[:-1]) if name[:-1].isdigit() else 0
            return (3, num, name)
        return (4, 0, name)
    return sorted(stores, key=get_sort_key)

def get_stores(block, row):
    block_id = block.split(' ')[1]  # Извлекаем номер блока, например, "3" из "Блок 3"
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT name FROM stores WHERE path LIKE ? AND path LIKE ?", (f'%{block_id}-блок%', f'%Ряд {row}%'))
    stores = [row['name'] for row in c.fetchall()]
    conn.close()
    return sort_stores(stores)

def get_path(block, row, store_name):
    block_id = block.split(' ')[1]
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT path FROM stores WHERE name = ? AND path LIKE ? AND path LIKE ?", (store_name, f'%{block_id}-блок%', f'%Ряд {row}%'))
    result = c.fetchone()
    conn.close()
    return result['path'] + ' > ' + store_name if result else "Магазин не найден"

@app.route('/', methods=['GET', 'POST'])
def index():
    blocks = get_blocks()
    rows = []
    stores = []
    path = None
    selected_block = request.form.get('block', '')
    selected_row = request.form.get('row', '')
    selected_store = request.form.get('store_name', '')

    if selected_block:
        rows = get_rows(selected_block)
    if selected_block and selected_row:
        stores = get_stores(selected_block, selected_row)
    if request.method == 'POST' and selected_store:
        path = get_path(selected_block, selected_row, selected_store)

    return render_template('index.html', blocks=blocks, rows=rows, stores=stores, 
                           selected_block=selected_block, selected_row=selected_row, 
                           selected_store=selected_store, path=path)

@app.route('/get_rows')
def get_rows_route():
    block = request.args.get('block')
    rows = get_rows(block) if block else []
    return jsonify(rows)

@app.route('/get_stores')
def get_stores_route():
    block = request.args.get('block')
    row = request.args.get('row')
    stores = get_stores(block, row) if block and row else []
    return jsonify(stores)

if __name__ == '__main__':
    app.run(debug=True)