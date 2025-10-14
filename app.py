


import sqlite3
import re
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, make_response
from flask_babel import Babel, gettext as _, get_locale
from datetime import datetime


app = Flask(__name__)


app.secret_key = "super_secret_key"  # обязательно для session

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

# === Выбор языка ===
@babel.localeselector
def select_locale():
    # приоритет — язык из session
    lang = session.get("lang")
    if lang in LANGUAGES:
        return lang
    # если нет — смотрим Accept-Language заголовок браузера
    return request.accept_languages.best_match(LANGUAGES.keys()) or "ru"



@app.route("/set_language/<lang>")
def set_language(lang):
    if lang in LANGUAGES:
        session["lang"] = lang
    return redirect(url_for("index"))


@app.context_processor
def inject_helpers():
    """Добавляем текущий язык и список языков в шаблон."""
    try:
        locale_str = str(get_locale())
    except Exception:
        locale_str = session.get("lang", "ru")
    return dict(
        LANGUAGES=LANGUAGES,
        get_locale_str=locale_str,
        get_locale=lambda: locale_str
    )

# === База данных ===
def get_db_connection():
    conn = sqlite3.connect("shops.db")
    conn.row_factory = sqlite3.Row
    return conn


# === Служебные функции ===
def numeric_key_for_shop(name):
    if not name:
        return (10**9, "")
    m = re.search(r"(\d+)", str(name))
    return (int(m.group(1)), name) if m else (10**9, name.lower())


def row_sort_key(r):
    if not r:
        return (2, "")
    s = str(r).strip()
    if s.isdigit():
        return (0, int(s))
    m = re.search(r"(\d+)", s)
    if m:
        return (1, int(m.group(1)), s)
    return (2, s.lower())


def is_excluded_for_specific(shop_name):
    if not shop_name:
        return True
    s = re.sub(r"(?i)^маг[-\s]*", "", str(shop_name))
    if re.fullmatch(r"\d+", s) or re.fullmatch(r"\d+[a-zA-Zа-яёА-ЯЁ]+\d*", s) or s == "005":
        return True
    return False



@app.route("/get_rows/<block>")
def get_rows(block):
    conn = get_db_connection()
    if block == "Гипермаркет":
        # В гипермаркете нет рядов, сразу возвращаем магазины
        shops = conn.execute("SELECT DISTINCT shop FROM shops WHERE block=?", (block,)).fetchall()
        conn.close()
        return jsonify({
            "type": "shops",
            "items": sorted({s["shop"] for s in shops}, key=numeric_key_for_shop)
        })

    if block == "Специфические объекты":
        shops = conn.execute("SELECT DISTINCT shop FROM shops WHERE block=?", (block,)).fetchall()
        conn.close()
        items = sorted({s["shop"] for s in shops if not is_excluded_for_specific(s["shop"])}, key=str.lower)
        return jsonify({"type": "shops", "items": items})

    rows = conn.execute("SELECT DISTINCT row FROM shops WHERE block=?", (block,)).fetchall()
    conn.close()
    return jsonify({
        "type": "rows",
        "items": sorted({r["row"] for r in rows if r["row"]}, key=row_sort_key)
    })


@app.route("/get_stores/<block>/<row>")
def get_stores(block, row):
    conn = get_db_connection()
    if block == "Гипермаркет":
        shops = conn.execute("SELECT DISTINCT shop FROM shops WHERE block=?", (block,)).fetchall()
        conn.close()
        return jsonify({"items": sorted({s["shop"] for s in shops}, key=numeric_key_for_shop)})

    if block == "Специфические объекты":
        shops = conn.execute("SELECT DISTINCT shop FROM shops WHERE block=?", (block,)).fetchall()
        conn.close()
        items = sorted({s["shop"] for s in shops if not is_excluded_for_specific(s["shop"])}, key=str.lower)
        return jsonify({"items": items})

    shops = conn.execute("SELECT DISTINCT shop FROM shops WHERE block=? AND row=?", (block, row)).fetchall()
    conn.close()
    return jsonify({"items": sorted({s["shop"] for s in shops}, key=numeric_key_for_shop)})


@app.route("/get_path/<block>/<row>/<shop>")
def get_path(block, row, shop):
    conn = get_db_connection()
    if block == "Специфические объекты":
        res = conn.execute("SELECT DISTINCT path FROM shops WHERE shop=?", (shop,)).fetchall()
    elif block == "Гипермаркет":
        res = conn.execute("SELECT DISTINCT path FROM shops WHERE block=? AND shop=?", (block, shop)).fetchall()
    else:
        res = conn.execute("SELECT DISTINCT path FROM shops WHERE block=? AND row=? AND shop=?", (block, row, shop)).fetchall()
    conn.close()

    if not res:
        return jsonify({"error": _("Путь не найден")})

    # Добавляем финальную точку (последнее слово пути или shop)
    paths = []
    for r in res:
        p = r["path"].strip()
        if not p.endswith(shop):
            p += f" > {shop}"
        paths.append(p)

    return jsonify({"path": " | ".join(paths)})




if __name__ == "__main__":
    app.run(debug=True)


