import sqlite3
import re

paths_text = open('test.txt', encoding='utf-8').read()

def parse_stores(store_str):
    stores = []
    parts = store_str.split(',')
    for part in parts:
        part = part.strip()
        if '...' in part:
            ranges = part.split('...')
            if len(ranges) != 2:
                continue
            start, end = ranges
            try:
                if start.isdigit() and end.isdigit():
                    stores.extend([str(i) for i in range(int(start), int(end)+1)])
                elif start.endswith('g') and end.endswith('g'):
                    start_num = int(start[:-1])
                    end_num = int(end[:-1])
                    stores.extend([f"{i}g" for i in range(start_num, end_num+1)])
                elif 'a' in start and 'a' in end:
                    prefix = ''.join(c for c in start if not c.isdigit())
                    start_num = int(''.join(c for c in start if c.isdigit()))
                    end_num = int(''.join(c for c in end if c.isdigit()))
                    stores.extend([f"{prefix}{i}" for i in range(start_num, end_num+1)])
                else:
                    stores.append(part)
            except ValueError:
                continue
        else:
            stores.append(part)
    prefixed = []
    for s in stores:
        if (s[0].isdigit() or (s[0].isalpha() and len(s) == 1)) and 'a' not in s.lower()[1:]:
            prefixed.append(f"Маг-{s}")
        elif s.startswith('5a') or s.endswith('g'):
            prefixed.append(f"Маг-{s}")
        else:
            prefixed.append(s)
    return prefixed

paths = [p.strip() for p in paths_text.split(';') if p.strip()]
store_paths = {}
for path in paths:
    if '>' not in path:
        continue
    components = [c.strip() for c in path.split('>')]
    full_path = ' > '.join(components[:-1])
    store_part = components[-1].strip().replace('Маг-', '')
    if any(spec in store_part.lower() for spec in ['освещение', 'кабинет', 'тунель', 'пирошкихона', 'шит', 'пост']):
        store_name = store_part
        store_paths[store_name] = full_path
    else:
        stores = parse_stores(store_part)
        for store in stores:
            store_paths[store] = full_path

conn = sqlite3.connect('stores.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS stores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    path TEXT
)''')
for name, path in store_paths.items():
    c.execute("INSERT OR REPLACE INTO stores (name, path) VALUES (?, ?)", (name, path))
conn.commit()
conn.close()