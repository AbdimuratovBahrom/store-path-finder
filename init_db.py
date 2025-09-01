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
store_paths = []
for path in paths:
    if '>' not in path:
        continue
    components = [c.strip() for c in path.split('>')]
    full_path = ' > '.join(components[:-1])
    store_part = components[-1].strip().replace('Маг-', '')
    block = None
    row = None
    for i, comp in enumerate(components):
        if 'блок' in comp.lower():
            block = comp
        if 'Ряд' in comp:
            row = comp
    if any(spec in store_part.lower() for spec in ['освещение', 'кабинет', 'тунель', 'пирошкихона', 'шит', 'пост']):
        store_paths.append((store_part, full_path, block, row))
    else:
        stores = parse_stores(store_part)
        for store in stores:
            store_paths.append((store, full_path, block, row))

conn = sqlite3.connect('stores.db')
c = conn.cursor()
c.execute('''DROP TABLE IF EXISTS stores''')
c.execute('''CREATE TABLE stores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    path TEXT,
    block TEXT,
    row TEXT
)''')
for name, path, block, row in store_paths:
    c.execute("INSERT INTO stores (name, path, block, row) VALUES (?, ?, ?, ?)", (name, path, block, row))
conn.commit()
conn.close()