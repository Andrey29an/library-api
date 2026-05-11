import os
import pytest
import psycopg2
from app import create_app

TEST_DB_CONFIG = {
    "host": os.environ.get("POSTGRES_HOST", "localhost"),
    "port": int(os.environ.get("POSTGRES_PORT", "5432")),
    "dbname": os.environ.get("POSTGRES_DB", "library_test_db"),
    "user": os.environ.get("POSTGRES_USER", "postgres"),
    "password": os.environ.get("POSTGRES_PASSWORD", "secret"),
}

@pytest.fixture(scope="session")
def app():
    return create_app(TEST_DB_CONFIG)

@pytest.fixture(scope="function")
def client(app):
    conn = psycopg2.connect(**TEST_DB_CONFIG)
    cur = conn.cursor()
    cur.execute("TRUNCATE books, authors RESTART IDENTITY CASCADE;")
    conn.commit()
    cur.close()
    conn.close()
    return app.test_client()
