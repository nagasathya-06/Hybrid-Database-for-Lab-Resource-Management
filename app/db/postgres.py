# app/db/postgres.py
import psycopg2
import psycopg2.extras
from config import Config

def get_connection():
    """Returns a fresh PostgreSQL connection."""
    return psycopg2.connect(
        host     = Config.DB_HOST,
        port     = Config.DB_PORT,
        dbname   = Config.DB_NAME,
        user     = Config.DB_USER,
        password = Config.DB_PASSWORD
    )

def query(sql, params=None, fetchone=False):
    """Run a SELECT query and return results as dicts."""
    conn = get_connection()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(sql, params)
    result = cur.fetchone() if fetchone else cur.fetchall()
    cur.close()
    conn.close()
    return result