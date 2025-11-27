import os
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    if DATABASE_URL is None:
        raise RuntimeError("DATABASE_URL is not set")
    return psycopg2.connect(DATABASE_URL)


@contextmanager
def get_cursor(commit: bool = False):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            yield cursor
            if commit:
                conn.commit()
    finally:
        conn.close()


def find_url_by_name(name: str):
    with get_cursor() as cur:
        cur.execute(
            "SELECT id, name, created_at FROM urls WHERE name = %s",
            (name,),
        )
        return cur.fetchone()


def insert_url(name: str) -> int:
    with get_cursor(commit=True) as cur:
        cur.execute(
            "INSERT INTO urls (name) VALUES (%s) RETURNING id",
            (name,),
        )
        row = cur.fetchone()
    return row["id"]


def get_url(id_: int):
    with get_cursor() as cur:
        cur.execute(
            "SELECT id, name, created_at FROM urls WHERE id = %s",
            (id_,),
        )
        return cur.fetchone()


def get_urls():
    with get_cursor() as cur:
        cur.execute(
            "SELECT id, name, created_at FROM urls ORDER BY id DESC",
        )
        return cur.fetchall()
