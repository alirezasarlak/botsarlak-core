import os
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor
import psycopg2
from app.config import Config
from app.utils.logger import logger

pool = SimpleConnectionPool(
    minconn=1, maxconn=12,
    dbname=Config.DB_NAME, user=Config.DB_USER, password=Config.DB_PASSWORD,
    host=Config.DB_HOST, port=Config.DB_PORT
)

def execute_query(query, params=None, fetch=None, commit=False):
    conn = pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            res = None
            if fetch == "one":
                res = cur.fetchone()
            elif fetch == "all":
                res = cur.fetchall()
            if commit:
                conn.commit()
            return res
    except Exception as e:
        if commit:
            conn.rollback()
        logger.exception("DB error")
        raise
    finally:
        pool.putconn(conn)

def run_migrations():
    import os
    mig_dir = "migrations"
    if not os.path.isdir(mig_dir): return
    for fn in sorted(os.listdir(mig_dir)):
        if not fn.endswith(".sql"): continue
        with open(os.path.join(mig_dir, fn), "r", encoding="utf-8") as f:
            sql = f.read()
        logger.info(f"Migration: {fn}")
        execute_query(sql, commit=True)
