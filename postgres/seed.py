# seed.py
from pg_connect import create_connection
from faker import Faker
from random import randint, choice

STATUSES = [("new",), ("in progress",), ("completed",)]

def seed_statuses(conn):
    with conn.cursor() as cur:
        cur.executemany("INSERT INTO status(name) VALUES (%s) ON CONFLICT (name) DO NOTHING;", STATUSES)

def seed_users(conn, n=20):
    fake = Faker()
    rows = [(fake.name(), fake.unique.email()) for _ in range(n)]
    with conn.cursor() as cur:
        cur.executemany("INSERT INTO users(fullname, email) VALUES (%s, %s) ON CONFLICT (email) DO NOTHING;", rows)

def seed_tasks(conn, n=60):
    fake = Faker()
    with conn.cursor() as cur:
        # fetch ids
        cur.execute("SELECT id FROM users;")
        user_ids = [r[0] for r in cur.fetchall()]
        cur.execute("SELECT id, name FROM status;")
        statuses = [r for r in cur.fetchall()]

        rows = []
        for _ in range(n):
            title = fake.sentence(nb_words=4).rstrip(".")
            description = fake.paragraph(nb_sentences=3)
            status_id = choice(statuses)[0]
            user_id   = choice(user_ids)
            rows.append((title, description, status_id, user_id))

        cur.executemany("""
            INSERT INTO tasks(title, description, status_id, user_id)
            VALUES (%s, %s, %s, %s);
        """, rows)

if __name__ == "__main__":
    with create_connection() as conn:
        seed_statuses(conn)
        seed_users(conn, n=25)
        seed_tasks(conn, n=120)
    print("Seed done.")
