import sqlite3

conn = sqlite3.connect('stores.db')
c = conn.cursor()
c.execute("SELECT name, block, row, path FROM stores WHERE name = 'Маг-1'")
results = c.fetchall()
for result in results:
    print(f"Name: {result[0]}, Block: {result[1]}, Row: {result[2]}, Path: {result[3]}")
conn.close()