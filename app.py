import sqlite3
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_babel import Babel, gettext as _, get_locale

app = Flask(__name__)
app.secret_key = "supersecretkey"

# === Flask-Babel ===
babel = Babel(app)

LANGUAGES = {
    'ru': 'Русский',
    'uz_Latn': 'O‘zbekcha (Lotin)',
    'uz_Cyrl': 'Ўзбекча (Кирилл)'
}

@babel.localeselector
def select_locale():
    return session.get("lang", "ru")

@app.context_processor
def inject_conf_var():
    return dict(get_locale=lambda: str(get_locale()))


# === DB helper ===
def get_db_connection():
    conn = sqlite3.connect("shops.db")
    conn.row_factory = sqlite3.Row
    return conn

# === Routes ===
@app.route("/")
def index():
    conn = get_db_connection()
    blocks = conn.execute("SELECT DISTINCT block FROM shops").fetchall()
    conn.close()
    return render_template("index.html", blocks=[b["block"] for b in blocks])

@app.route("/set_language/<lang>")
def set_language(lang):
    if lang in LANGUAGES:
        session["lang"] = lang
    return redirect(url_for("index"))

@app.route("/get_rows/<block>")
def get_rows(block):
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT DISTINCT row FROM shops WHERE block = ? AND row IS NOT NULL",
        (block,)
    ).fetchall()
    conn.close()

    if rows:
        return jsonify({"type": "rows", "items": [r["row"] for r in rows]})
    else:
        # гипермаркет → сразу магазины
        conn = get_db_connection()
        shops = conn.execute(
            "SELECT DISTINCT shop_number FROM shops WHERE block = ?",
            (block,)
        ).fetchall()
        conn.close()
        return jsonify({"type": "shops", "items": [s["shop_number"] for s in shops]})

@app.route("/get_stores/<block>/<row>")
def get_stores(block, row):
    conn = get_db_connection()
    stores = conn.execute(
        "SELECT DISTINCT shop_number FROM shops WHERE block = ? AND row = ?",
        (block, row)
    ).fetchall()
    conn.close()
    return jsonify({"type": "shops", "items": [s["shop_number"] for s in stores]})

@app.route("/get_path/<block>/<row>/<shop>")
def get_path(block, row, shop):
    conn = get_db_connection()
    results = conn.execute(
        "SELECT * FROM shops WHERE block = ? AND (row = ? OR row IS NULL) AND shop_number = ?",
        (block, None if row == "None" else row, shop)
    ).fetchall()
    conn.close()

    if not results:
        return jsonify({"error": "⚠️ Магазин не найден"})

    formatted = []
    for r in results:
        formatted.append(f"{r['path']} > Магазин {r['shop_number']}")
    return jsonify({"path": "<br>".join(formatted)})

@app.route("/search")
def search():
    keyword = request.args.get("keyword", "").strip()
    conn = get_db_connection()
    results = conn.execute(
        "SELECT * FROM shops WHERE shop_number LIKE ? OR block LIKE ? OR row LIKE ?",
        (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
    ).fetchall()
    conn.close()
    formatted = [
        f"Block: {r['block']} | Row: {r['row']} | Shop: {r['shop_number']} | Path: {r['path']}"
        for r in results
    ]
    return jsonify(formatted)

@app.context_processor
def inject_translations():
    return dict(
        translations={
            "hide": _("Скрыть блоки"),
            "show": _("Показать блоки")
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
