import sqlite3
import re
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_babel import Babel, gettext as _, get_locale

app = Flask(__name__)
babel = Babel(app)

# === Языки ===
LANGUAGES = {
    "ru": "Русский",
    "uz_Latn": "O‘zbekcha (Lotin)",
    "uz_Cyrl": "Ўзбекча (Кирилл)"
}

@babel.localeselector
def select_locale():
    # Пример: выбираем локаль по Accept-Language заголовку
    from flask import g, request
    if hasattr(g, 'user') and g.user:
        return g.user.locale
    return request.accept_languages.best_match(['en', 'ru'])  # Резервный вариант
    
    

# Создаём Babel с locale_selector (совместимо с recent flask-babel).
# Если у тебя старая версия flask-babel, используй альтернативный способ (в прошлом у тебя уже работало).
babel.init_app(app)

# делаем get_locale и LANGUAGES доступными в шаблонах
@app.context_processor
def inject_helpers():
    """Добавляем локаль и список языков в шаблоны."""
    try:
        locale_str = str(get_locale())
    except Exception:
        locale_str = "ru"
    return dict(get_locale_str=locale_str, LANGUAGES=LANGUAGES, get_locale=lambda: locale_str)


# === Подключение к БД ===
def get_db_connection():
    conn = sqlite3.connect("shops.db")
    conn.row_factory = sqlite3.Row
    return conn


# === Утилиты сортировки и фильтрации ===
def numeric_key_for_shop(name):
    """Сортируем так: числа как числа, затем прочие строки (натуральный порядок)."""
    if name is None:
        return (10**9, "")
    s = str(name)
    # попробуем найти первое число
    m = re.search(r"(\d+)", s)
    if m:
        return (int(m.group(1)), s)
    return (10**9, s.lower())


def row_sort_key(r):
    """Сортировка рядов: числовые сначала по числу, затем буквы в алфавитном."""
    if r is None:
        return (2, "")
    s = str(r).strip()
    if re.fullmatch(r"\d+", s):
        return (0, int(s))
    # если вид "38-ЩР14" — попробуем извлечь число внутри
    m = re.search(r"(\d+)", s)
    if m:
        return (1, int(m.group(1)), s)
    return (2, s.lower())


def is_excluded_for_specific(shop_name):
    """
    В специфических объектах НЕ показываем простые числа и обозначения типа 1g, 5a1, 005 и т.п.
    Возвращаем True если нужно ИСКЛЮЧИТЬ.
    """
    if not shop_name:
        return True
    s = str(shop_name).strip()
    # если в начале есть "Маг-" или "Маг " — уберём приставку для проверки
    s_check = re.sub(r"(?i)^маг[-\s]*", "", s)
    # чистое число (1,2,3...)
    if re.fullmatch(r"\d+", s_check):
        return True
    # число с буквой e.g. 1g, 5a1, 5a, 10g и т.п.
    if re.fullmatch(r"\d+[a-zA-Zа-яёА-ЯЁ]+\d*", s_check):
        return True
    # специальное исключение '005'
    if s_check == "005":
        return True
    return False


# === Маршруты ===
@app.route("/")
def index():
    conn = get_db_connection()
    rows = conn.execute("SELECT DISTINCT block FROM shops").fetchall()
    blocks = [r["block"] for r in rows]
    conn.close()

    # добавляем блок Специфические объекты в список блоков (если ещё нет)
    if "Специфические объекты" not in blocks:
        blocks.append("Специфические объекты")

    # сортируем блокы: оставим естественный порядок, но удобно отсортировать алфавитно
    blocks = sorted(blocks)
    return render_template("index.html", blocks=blocks)


@app.route("/set_language/<lang>")
def set_language(lang):
    if lang in LANGUAGES:
        session["lang"] = lang
    return redirect(url_for("index"))


@app.route("/get_rows/<block>")
def get_rows(block):
    conn = get_db_connection()

    # Гипермаркет — сразу список магазинов (нет рядов)
    if block == "Гипермаркет":
        stores = conn.execute("SELECT DISTINCT shop FROM shops WHERE block = ?", (block,)).fetchall()
        conn.close()
        items = sorted({s["shop"] for s in stores}, key=numeric_key_for_shop)
        return jsonify({"type": "shops", "items": items})

    # Специфические объекты — вернуть НЕ ряды, а магазины-спецы
    if block == "Специфические объекты":
        # Берём записи, отмеченные как спец (row='Спец') или записанные в спец-блок
        stores = conn.execute(
            "SELECT DISTINCT shop FROM shops WHERE block = 'Специфические объекты' OR row = 'Спец' OR block IN ('1-блок','2-блок','3-блок')"
        ).fetchall()
        conn.close()
        # фильтруем нежелательные магазины и сортируем по строке
        items = sorted({s["shop"] for s in stores if s["shop"] and not is_excluded_for_specific(s["shop"])}, key=lambda x: (x.lower()))
        return jsonify({"type": "shops", "items": items})

    # Обычный блок — возвращаем набор рядов (без None)
    rows = conn.execute(
        "SELECT DISTINCT row FROM shops WHERE block = ? AND row IS NOT NULL", (block,)
    ).fetchall()
    conn.close()
    items = sorted({r["row"] for r in rows if r["row"] is not None}, key=row_sort_key)
    return jsonify({"type": "rows", "items": items})


@app.route("/get_stores/<block>/<row>")
def get_stores(block, row):
    conn = get_db_connection()

    # Специфические объекты — вернуть заранее отфильтрованные магазины
    if block == "Специфические объекты":
        stores = conn.execute(
            "SELECT DISTINCT shop FROM shops WHERE block = 'Специфические объекты' OR row = 'Спец' OR block IN ('1-блок','2-блок','3-блок')"
        ).fetchall()
        conn.close()
        items = sorted({s["shop"] for s in stores if s["shop"] and not is_excluded_for_specific(s["shop"])}, key=lambda x: (x.lower()))
        return jsonify({"items": items})

    # Гипермаркет — вернуть магазины
    if block == "Гипермаркет":
        stores = conn.execute("SELECT DISTINCT shop FROM shops WHERE block = ?", (block,)).fetchall()
        conn.close()
        items = sorted({s["shop"] for s in stores}, key=numeric_key_for_shop)
        return jsonify({"items": items})

    # Обычный блок + ряд
    if row in ("None", "", "None "):
        stores = conn.execute("SELECT DISTINCT shop FROM shops WHERE block = ? AND row IS NULL", (block,)).fetchall()
    else:
        stores = conn.execute("SELECT DISTINCT shop FROM shops WHERE block = ? AND row = ?", (block, row)).fetchall()
    conn.close()
    items = sorted({s["shop"] for s in stores if s["shop"] is not None}, key=numeric_key_for_shop)
    return jsonify({"items": items})


@app.route("/get_path/<block>/<row>/<shop>")
def get_path(block, row, shop):
    conn = get_db_connection()
    add_mag = not (block in ["Гипермаркет", "Специфические объекты"])

    if block == "Специфические объекты":
        results = conn.execute("SELECT DISTINCT path FROM shops WHERE shop = ?", (shop,)).fetchall()
    elif row in ("None", "", "None "):
        results = conn.execute("SELECT DISTINCT path FROM shops WHERE block = ? AND row IS NULL AND shop = ?", (block, shop)).fetchall()
    else:
        results = conn.execute("SELECT DISTINCT path FROM shops WHERE block = ? AND row = ? AND shop = ?", (block, row, shop)).fetchall()

    conn.close()
    if not results:
        return jsonify({"error": _("Путь не найден")})

    paths = []
    for r in results:
        p = r["path"]
        # если нужно добавить Маг-N (shop — только цифры) и в path ещё нет Маг-
        shop_str = shop.strip()
        if add_mag and re.fullmatch(r"\d+", shop_str) and "Маг-" not in p and not re.search(r"\bМаг\b", p):
            p = f"{p} > Маг-{shop_str}"
        # для блока 38-склад: убираем слово "Ряд" в отображении (требование)
        p = re.sub(r"\bРяд\s+([^\>]+)\b", r"\1", p)
        paths.append(p)
    # убираем дубликаты, сохраняем порядок
    seen = set()
    final = []
    for x in paths:
        if x not in seen:
            final.append(x)
            seen.add(x)
    return jsonify({"path": " | ".join(final)})


@app.route("/search")
def search():
    keyword = request.args.get("keyword", "").strip()
    conn = get_db_connection()
    results = conn.execute(
        "SELECT * FROM shops WHERE shop LIKE ? OR block LIKE ? OR row LIKE ? OR path LIKE ?",
        (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
    ).fetchall()
    conn.close()
    formatted = [
        f"Block: {r['block']} | Row: {r['row']} | Shop: {r['shop']} | Path: {r['path']}"
        for r in results
    ]
    # убрать дубли и вернуть
    formatted = list(dict.fromkeys(formatted))
    if not formatted:
        return jsonify({"error": _("Ничего не найдено")})
    return jsonify({"results": formatted})


if __name__ == "__main__":
    app.run(debug=True)
