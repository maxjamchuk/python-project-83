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
            """
            SELECT
                urls.id,
                urls.name,
                urls.created_at,
                MAX(url_checks.created_at) AS last_check_at
            FROM urls
            LEFT JOIN url_checks
                ON url_checks.url_id = urls.id
            GROUP BY urls.id, urls.name, urls.created_at
            ORDER BY urls.id DESC
            """,
        )
        return cur.fetchall()


def create_check(url_id: int) -> int:
    with get_cursor(commit=True) as cur:
        cur.execute(
            "INSERT INTO url_checks (url_id) VALUES (%s) RETURNING id",
            (url_id,),
        )
        row = cur.fetchone()
    return row["id"]


def get_checks_for_url(url_id: int):
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT id, status_code, h1, title, description, created_at
            FROM url_checks
            WHERE url_id = %s
            ORDER BY id DESC
            """,
            (url_id,),
        )
        return cur.fetchall()
