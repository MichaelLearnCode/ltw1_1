import sqlite3
import os

DB_PATH = "database.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    if not os.path.exists(DB_PATH):
        conn = get_db()
        cursor = conn.cursor()

        # Bảng don_vi_cap_1
        cursor.execute(
            """
            CREATE TABLE don_vi_cap_1 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ten_don_vi TEXT NOT NULL,
                dia_diem TEXT, website TEXT, email TEXT,
                dien_thoai TEXT, mo_ta TEXT, image_url TEXT
            )
        """
        )

        # Bảng don_vi_cap_2
        cursor.execute(
            """
            CREATE TABLE don_vi_cap_2 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ten_don_vi TEXT NOT NULL,
                dia_diem TEXT, website TEXT, email TEXT,
                dien_thoai TEXT, mo_ta TEXT, image_url TEXT,
                don_vi_cap_1_id INTEGER NOT NULL,
                FOREIGN KEY (don_vi_cap_1_id) REFERENCES don_vi_cap_1(id)
            )
        """
        )

        # Bảng users
        cursor.execute(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                role TEXT DEFAULT 'collaborator'
            )
        """
        )
        conn.commit()
        conn.close()
