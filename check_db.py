
import psycopg2
conn = psycopg2.connect(dbname='fieldcheck', user='postgres', password='password', host='localhost')
cur = conn.cursor()
cur.execute('SELECT id, token FROM contractors LIMIT 1;')
row = cur.fetchone()
if row:
    print('Contractor ID:', row[0])
    print('Token:', row[1])
else:
    print('No contractor')

