# app/db/connection.py

from mysql.connector import connect, Error
from dotenv import load_dotenv
import os

load_dotenv()

def get_connection():
    try:
        return connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            autocommit=True
        )
    except Error as e:
        raise RuntimeError(f"Database connection failed: {e}")
