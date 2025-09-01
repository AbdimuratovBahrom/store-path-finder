from flask import Flask, render_template, request, jsonify
import sqlite3
import re

app = Flask(__name__)

def get_blocks():
    conn = sqlite3.connect('stores.db')
    c = conn.cursor()
    c.execute("SELECT DISTINCT block FROM stores WHERE block IS NOT NULL")
    blocks = [row[0] for row in c.fetchall()]
    conn.close()
    return sorted(blocks)

def get_rows(block):
    conn = sqlite3.connect('stores.db')
    c = conn.cursor()
    c.execute("SELECT DISTINCT row FROM stores WHERE block = ? AND row IS NOT NULL", (block,))
    rows = [row[0] for row in c.fetchall()]
    conn.close()
    return sorted(rows)

def sort_stores(stores):
    def get_sort_key(store):
        # Удаляем префикс "Маг-" для обработки
        name = store.replace('Маг-', '')
        # Проверяем, является ли имя числом (например, "1", "68")
        if name.isdigit():
            return (1, int(name), '')
        # Проверяем формат "5a1", "5a13"
        if name.startswith('5a'):
            num = int(name[2:]) if name[2:].isdigit() else 0
            return (2, num, name)
        # Проверяем формат "1g", "46g"
        if name.endswith('g'):
            num = int(name[:-1]) if name[:-1].isdigit() else 0
            return (3, num, name)
        # Буквенные обозначения (А, Б, Ж)
        return (4, 0, name)
    
    return sorted(stores, key=get_sort_key)

def get_stores(block, row):
    conn = sqlite3.connect('stores.db')
    c = conn.cursor()
    c.execute("SELECT DISTINCT name FROM stores WHERE block = ? AND row = ?", (block, row))
    stores = [row[0] for row in c.fetchall()]
    conn.close()
    return sort_stores(stores)

def get_path(block, row, store_name):
    conn = sqlite3.connect('stores.db')
    c = conn.cursor()
    c.execute("SELECT path FROM stores WHERE block = ? AND row = ? AND name = ?", (block, row, store_name))
    result = c.fetchone()
    conn.close()
    return result[0] + ' > ' + store_name if result else "Магазин не найден"

@app.route('/', methods=['GET', 'POST'])
def index():
    blocks = get_blocks()
    rows = []
    stores = []
    path = None
    selected_block = None
    selected_row = None
    selected_store = None

    if request.method == 'POST':
        selected_block = request.form.get('block')
        selected_row = request.form.get('row')
        selected_store = request.form.get('store_name')
        
        if selected_block:
            rows = get_rows(selected_block)
        if selected_block and selected_row:
            stores = get_stores(selected_block, selected_row)
        if selected_block and selected_row and selected_store:
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