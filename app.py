from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

def get_path(store_name):
    conn = sqlite3.connect('stores.db')
    c = conn.cursor()
    c.execute("SELECT path FROM stores WHERE name = ?", (store_name,))
    result = c.fetchone()
    conn.close()
    return result[0] + ' > ' + store_name if result else "Магазин не найден"

@app.route('/', methods=['GET', 'POST'])
def index():
    path = None
    if request.method == 'POST':
        store_name = request.form['store_name']
        path = get_path(store_name)
    return render_template('index.html', path=path)

if __name__ == '__main__':
    app.run(debug=True)