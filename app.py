import re
from flask import Flask, render_template, jsonify, request, session
from flask_babel import Babel
import sqlite3

app = Flask(__name__)
app.config['BABEL_DEFAULT_LOCALE'] = 'ru'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
app.secret_key = 'your-secret-key'
babel = Babel(app)


@babel.localeselector
def get_locale():
    return session.get('lang', app.config['BABEL_DEFAULT_LOCALE'])

@app.route('/')
def index():
    conn = sqlite3.connect('shops.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT block FROM shops')
    blocks = [row[0] for row in cursor.fetchall()]
    conn.close()
    locale = get_locale()  # Получаем текущий язык
    return render_template('index.html', blocks=blocks, locale=locale)

@app.route('/get_rows/<block>')
def get_rows(block):
    conn = sqlite3.connect('shops.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT path FROM shops WHERE block = ?', (block,))
    paths = [r[0] for r in cursor.fetchall()]
    rows = set()
    for path in paths:
        match = re.search(r'Ряд\s+([A-Za-zА-Яа-я0-9\-]+)', path)
        if match:
            rows.add(match.group(1))  # Только номер/буква ряда
    # Для 3-блока сортируем как числа, для остальных — как строки
    if block == "3-блок":
        def row_key(x):
            try:
                return int(x)
            except ValueError:
                return float('inf')
        rows = sorted(rows, key=row_key)
    else:
        rows = sorted(rows)
    conn.close()
    app.logger.debug(f"Fetched rows for block {block}: {rows}")
    return jsonify(rows)

@app.route('/get_stores/<block>/<row>')
def get_stores(block, row):
    conn = sqlite3.connect('shops.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT DISTINCT shop_number FROM shops WHERE block = ? AND path LIKE ?",
        (block, f"%Ряд {row}%")
    )
    stores = []
    for (shop,) in cursor.fetchall():
        # Если в shop есть хотя бы две буквы подряд — убираем "Маг-" в начале
        if re.match(r'^Маг-[A-Za-zА-Яа-я]{2,}', shop):
            stores.append(shop[4:])  # убираем "Маг-"
        else:
            stores.append(shop)
    conn.close()
    app.logger.debug(f"Fetched stores for block {block}, row {row}: {stores}")
    return jsonify(stores)

@app.route('/get_path/<block>/<row>/<shop_number>')
def get_path(block, row, shop_number):
    conn = sqlite3.connect('shops.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT path, shop_number FROM shops WHERE block = ? AND path LIKE ? AND shop_number = ?",
        (block, f"%Ряд {row}%", shop_number)
    )
    row_db = cursor.fetchone()
    conn.close()
    if row_db:
        # Если магазин начинается с Маг- и далее две буквы — не добавлять Маг-
        if re.match(r'^Маг-[A-Za-zА-Яа-я]{2,}', row_db[1]):
            full_path = f"{row_db[0]} > {row_db[1][4:]}"
        else:
            full_path = f"{row_db[0]} > {row_db[1]}"
        return jsonify({'path': full_path})
    else:
        return jsonify({'path': None})

@app.route('/set_language/<lang>')
def set_language(lang):
    session['lang'] = lang
    app.logger.debug(f"Language switched to: {lang}")
    return jsonify({'status': 'success', 'language': lang})

if __name__ == '__main__':
    app.run(debug=True)