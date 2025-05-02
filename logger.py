import datetime

def log_visit():
    now = datetime.datetime.now()
    with open("visit_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{now.isoformat()}\n")
