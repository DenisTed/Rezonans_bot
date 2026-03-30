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
        phone TEXT,
        registered_at TEXT,
        is_active INTEGER DEFAULT 1
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS shows (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        show_date TEXT,
        show_time TEXT,
        description TEXT,
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


def update_user_phone(telegram_id, phone):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE users SET phone = ? WHERE telegram_id = ?
    """, (phone, telegram_id))

    conn.commit()
    conn.close()


def get_user(telegram_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT telegram_id, first_name, username, phone, registered_at
    FROM users
    WHERE telegram_id = ?
    """, (telegram_id,))

    user = cursor.fetchone()
    conn.close()
    return user


def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT telegram_id, first_name, username, phone, registered_at
    FROM users
    ORDER BY id DESC
    """)

    users = cursor.fetchall()
    conn.close()
    return users


def add_show(title, show_date, show_time, description=""):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO shows (title, show_date, show_time, description)
    VALUES (?, ?, ?, ?)
    """, (title, show_date, show_time, description))

    conn.commit()
    conn.close()


def get_active_shows():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, title, show_date, show_time, description
    FROM shows
    WHERE is_active = 1
    ORDER BY id DESC
    """)

    shows = cursor.fetchall()
    conn.close()
    return shows


def add_ticket_order(telegram_id, customer_name, phone, show_name, ticket_count, comment):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO ticket_orders (
        telegram_id, customer_name, phone, show_name,
        ticket_count, comment, created_at, status
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, 'new')
    """, (
        telegram_id,
        customer_name,
        phone,
        show_name,
        ticket_count,
        comment,
        datetime.now().isoformat()
    ))

    order_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return order_id


def get_last_orders(limit=20):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, telegram_id, customer_name, phone, show_name,
           ticket_count, comment, created_at, status
    FROM ticket_orders
    ORDER BY id DESC
    LIMIT ?
    """, (limit,))

    orders = cursor.fetchall()
    conn.close()
    return orders


def get_user_orders(telegram_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, show_name, ticket_count, comment, created_at, status
    FROM ticket_orders
    WHERE telegram_id = ?
    ORDER BY id DESC
    """, (telegram_id,))

    orders = cursor.fetchall()
    conn.close()
    return orders


def update_order_status(order_id, status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE ticket_orders
    SET status = ?
    WHERE id = ?
    """, (status, order_id))

    updated = cursor.rowcount
    conn.commit()
    conn.close()
    return updated > 0


def get_order_by_id(order_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, telegram_id, customer_name, phone, show_name,
           ticket_count, comment, created_at, status
    FROM ticket_orders
    WHERE id = ?
    """, (order_id,))

    order = cursor.fetchone()
    conn.close()
    return order