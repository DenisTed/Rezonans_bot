import sqlite3
from datetime import datetime

DB_NAME = "theatre.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        first_name TEXT,
        username TEXT,
        registered_at TEXT,
        is_active INTEGER DEFAULT 1
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ticket_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER,
        customer_name TEXT,
        phone TEXT,
        show_name TEXT,
        ticket_count INTEGER,
        comment TEXT,
        created_at TEXT,
        status TEXT DEFAULT 'new'
    )
    """)

    conn.commit()
    conn.close()


def add_user(telegram_id, first_name, username):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO users (telegram_id, first_name, username, registered_at)
    VALUES (?, ?, ?, ?)
    """, (telegram_id, first_name, username, datetime.now().isoformat()))

    conn.commit()
    conn.close()


def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT telegram_id, first_name, username, registered_at
    FROM users
    ORDER BY id DESC
    """)

    users = cursor.fetchall()
    conn.close()
    return users


def add_ticket_order(telegram_id, customer_name, phone, show_name, ticket_count, comment):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO ticket_orders (
        telegram_id, customer_name, phone, show_name,
        ticket_count, comment, created_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        telegram_id,
        customer_name,
        phone,
        show_name,
        ticket_count,
        comment,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


def get_last_orders(limit=20):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT telegram_id, customer_name, phone, show_name,
           ticket_count, comment, created_at, status
    FROM ticket_orders
    ORDER BY id DESC
    LIMIT ?
    """, (limit,))

    orders = cursor.fetchall()
    conn.close()
    return orders