import sqlite3
import os
import logging
from datetime import datetime

# Path to database file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "smartpos.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")
LOG_PATH = os.path.join(BASE_DIR, "logs", "db.log")

# Setup logging
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = None
            cls._instance.connect()
        return cls._instance

    def connect(self):
        try:
            self.connection = sqlite3.connect(
                DB_PATH,
                check_same_thread=False
            )
            self.connection.row_factory = sqlite3.Row
            self.connection.execute("PRAGMA foreign_keys = ON")
            self.connection.execute("PRAGMA journal_mode = WAL")
            self.initialize_schema()
            logging.info("Database connected: " + DB_PATH)
        except Exception as e:
            logging.error("Database connection failed: " + str(e))
            raise

    def initialize_schema(self):
        try:
            with open(SCHEMA_PATH, "r") as f:
                schema = f.read()
            self.connection.executescript(schema)
            self.connection.commit()
            logging.info("Schema initialized successfully.")
        except Exception as e:
            logging.error("Schema initialization failed: " + str(e))
            raise

    def execute(self, query, params=()):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            return cursor
        except Exception as e:
            logging.error("Query failed: " + str(e) +
                         " | Query: " + query)
            raise

    def fetchall(self, query, params=()):
        cursor = self.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def fetchone(self, query, params=()):
        cursor = self.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_last_id(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT last_insert_rowid()")
        return cursor.fetchone()[0]

    def close(self):
        if self.connection:
            self.connection.close()
            logging.info("Database connection closed.")

# Global database instance
db = Database()