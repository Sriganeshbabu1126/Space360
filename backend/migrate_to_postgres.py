import os
import psycopg2

from app.models import Base
from sqlalchemy import create_engine

LOCAL_URL = 'postgresql://fieldcheck_user:fieldcheck123@localhost:5432/fieldcheck'
REMOTE_URL = os.environ.get('PG_URL')

def migrate_data():
    if not REMOTE_URL:
        print("PG_URL environment variable is not set.")
        return

    print("Connecting to local PostgreSQL...")
    local_conn = psycopg2.connect(LOCAL_URL)
    local_cursor = local_conn.cursor()

    print(f"Connecting to Cloud SQL at {REMOTE_URL.split('@')[-1]}...")
    remote_conn = psycopg2.connect(REMOTE_URL)
    remote_cursor = remote_conn.cursor()

    sorted_table_names = [t.name for t in Base.metadata.sorted_tables]
    
    # We must truncate all tables in remote to avoid conflicts, cascade handles foreign keys.
    print("Truncating remote tables...")
    for table in reversed(sorted_table_names):
        try:
            remote_cursor.execute(f"TRUNCATE TABLE {table} CASCADE;")
        except Exception as e:
            print(f"Error truncating {table}: {e}")
            remote_conn.rollback()
    remote_conn.commit()
    
    for table in sorted_table_names:
        print(f"Migrating table: {table}")
        local_cursor.execute(f"SELECT * FROM {table}")
        rows = local_cursor.fetchall()
        
        if not rows:
            print(f"  No data to migrate for {table}")
            continue
            
        # Get column names
        local_cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name='{table}' ORDER BY ordinal_position;")
        columns = [row[0] for row in local_cursor.fetchall()]
        col_names = ", ".join([f'"{c}"' for c in columns])
        placeholders = ", ".join(["%s"] * len(columns))
        
        insert_query = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"
        
        for row in rows:
            try:
                remote_cursor.execute(insert_query, row)
            except Exception as e:
                print(f"  Error inserting into {table}: {e}")
                print(f"  Row data: {row}")
                remote_conn.rollback()
                break
        else:
            remote_conn.commit()
            print(f"  Successfully migrated {len(rows)} rows for {table}")

    remote_conn.commit()
    
    remote_cursor.close()
    remote_conn.close()
    local_cursor.close()
    local_conn.close()
    print("Migration complete!")

if __name__ == '__main__':
    migrate_data()
