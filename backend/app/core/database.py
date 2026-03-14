"""
PostgreSQL / Supabase database layer using psycopg2.
"""
from contextlib import contextmanager
from typing import Generator, Optional
from app.core.config import settings
import psycopg2
import psycopg2.extras
import psycopg2.pool
import logging

logger = logging.getLogger("cargozen.db")

_pool: Optional[psycopg2.pool.SimpleConnectionPool] = None


def _get_pool() -> psycopg2.pool.SimpleConnectionPool:
    global _pool
    if _pool is None or _pool.closed:
        _pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=settings.DATABASE_URL,
        )
        logger.info("PostgreSQL connection pool created")
    return _pool


def get_connection():
    """Return a connection from the pool (for health-check compatibility)."""
    pool = _get_pool()
    conn = pool.getconn()
    pool.putconn(conn)
    return conn


@contextmanager
def get_cursor(schema: str = None) -> Generator:
    """Yield a RealDictCursor inside a transaction."""
    pool = _get_pool()
    conn = pool.getconn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)


def execute_query(sql: str, params: tuple = None, schema: str = None) -> list[dict]:
    with get_cursor(schema) as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
        return [dict(r) for r in rows]


def execute_one(sql: str, params: tuple = None, schema: str = None) -> Optional[dict]:
    with get_cursor(schema) as cur:
        cur.execute(sql, params)
        row = cur.fetchone()
        return dict(row) if row else None


def execute_write(sql: str, params: tuple = None, schema: str = None) -> int:
    with get_cursor(schema) as cur:
        cur.execute(sql, params)
        return cur.rowcount


def execute_insert_returning_id(sql: str, params: tuple = None, schema: str = None):
    with get_cursor(schema) as cur:
        cur.execute(sql, params)
        row = cur.fetchone()
        return list(dict(row).values())[0] if row else None
