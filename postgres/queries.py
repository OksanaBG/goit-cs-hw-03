# queries.py
from pg_connect import create_connection

def q1_tasks_by_user(user_id:int):
    sql = "SELECT id, title, description FROM tasks WHERE user_id = %s ORDER BY id;"
    return run(sql, (user_id,))

def q2_tasks_by_status_name(status_name:str):
    sql = """
    SELECT t.id, t.title
    FROM tasks t
    WHERE t.status_id = (SELECT s.id FROM status s WHERE s.name = %s);
    """
    return run(sql, (status_name,))

def q3_update_task_status(task_id:int, new_status:str):
    sql = """
    UPDATE tasks
    SET status_id = (SELECT id FROM status WHERE name = %s)
    WHERE id = %s
    RETURNING id;
    """
    return run(sql, (new_status, task_id))

def q4_users_without_tasks():
    sql = """
    SELECT u.id, u.fullname, u.email
    FROM users u
    WHERE u.id NOT IN (SELECT DISTINCT user_id FROM tasks);
    """
    return run(sql)

def q5_insert_task_for_user(user_id:int, title:str, description:str, status_name:str="new"):
    sql = """
    INSERT INTO tasks(title, description, status_id, user_id)
    VALUES (%s, %s, (SELECT id FROM status WHERE name=%s), %s)
    RETURNING id;
    """
    return run(sql, (title, description, status_name, user_id))

def q6_not_completed_tasks():
    sql = """
    SELECT t.id, t.title, s.name AS status
    FROM tasks t JOIN status s ON s.id = t.status_id
    WHERE s.name <> 'completed';
    """
    return run(sql)

def q7_delete_task(task_id:int):
    sql = "DELETE FROM tasks WHERE id = %s RETURNING %s;"
    # returning the id as echo
    return run(sql, (task_id, task_id))

def q8_users_by_email_like(pattern:str):
    sql = "SELECT id, fullname, email FROM users WHERE email ILIKE %s;"
    return run(sql, (pattern,))

def q9_update_user_fullname(user_id:int, new_name:str):
    sql = "UPDATE users SET fullname=%s WHERE id=%s RETURNING id;"
    return run(sql, (new_name, user_id))

def q10_task_count_by_status():
    sql = """
    SELECT s.name AS status, COUNT(t.id) AS total
    FROM status s
    LEFT JOIN tasks t ON t.status_id = s.id
    GROUP BY s.name
    ORDER BY s.name;
    """
    return run(sql)

def q11_tasks_by_user_email_domain(domain:str):
    # domain like '%@example.com'
    sql = """
    SELECT t.id, t.title, u.email
    FROM tasks t
    JOIN users u ON u.id = t.user_id
    WHERE u.email ILIKE %s;
    """
    return run(sql, (domain,))

def q12_tasks_without_description():
    sql = "SELECT id, title FROM tasks WHERE description IS NULL OR description = '';"
    return run(sql)

def q13_users_with_inprogress_tasks():
    sql = """
    SELECT u.fullname, t.title
    FROM users u
    JOIN tasks t    ON t.user_id = u.id
    JOIN status s   ON s.id = t.status_id
    WHERE s.name = 'in progress'
    ORDER BY u.fullname;
    """
    return run(sql)

def q14_users_and_their_task_counts():
    sql = """
    SELECT u.id, u.fullname, COUNT(t.id) AS tasks_total
    FROM users u
    LEFT JOIN tasks t ON t.user_id = u.id
    GROUP BY u.id, u.fullname
    ORDER BY u.fullname;
    """
    return run(sql)

def run(sql:str, params:tuple|None=None):
    with create_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            try:
                return cur.fetchall()
            except Exception:
                return []
