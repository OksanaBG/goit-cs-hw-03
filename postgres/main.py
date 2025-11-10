# main.py
from queries import *

if __name__ == "__main__":
    print("q10 counts:", q10_task_count_by_status())
    # приклади параметрів:
    print("q2 'new':", q2_tasks_by_status_name("new")[:5])
    print("insert:", q5_insert_task_for_user(1, "Write report", "Draft v1", "in progress"))
    print("domain '@gmail.com':", q11_tasks_by_user_email_domain("%@gmail.com")[:5])
