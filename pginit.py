import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']

if __name__ == '__main__':
    conn = psycopg2.connect(DATABASE_URL,sslmode='prefer')
    cur = conn.cursor()
    with open('schema.sql','r') as f:
        cur.execute(f.read())
        conn.commit()
    try:
        with open('insertdata.sql','r') as f:
            cur.execute(f.read())
            conn.commit()
    except Exception as e:
        print(e)

