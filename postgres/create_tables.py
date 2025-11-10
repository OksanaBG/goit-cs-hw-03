# create_tables.py
from pg_connect import create_connection

DDL = """
-- drop for clean runs (optional in dev)
DROP TABLE IF EXISTS tasks CASCADE;
DROP TABLE IF EXISTS status CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
    id        SERIAL PRIMARY KEY,
    fullname  VARCHAR(100) NOT NULL,
    email     VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE status (
    id    SERIAL PRIMARY KEY,
    name  VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE tasks (
    id          SERIAL PRIMARY KEY,
    title       VARCHAR(100) NOT NULL,
    description TEXT,
    status_id   INTEGER NOT NULL REFERENCES status(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    user_id     INTEGER NOT NULL REFERENCES users(id)  ON UPDATE CASCADE ON DELETE CASCADE
);
"""

if __name__ == "__main__":
    with create_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(DDL)
    print("Schema created.")