import time
import json
import smtplib
import os
from email.mime.text import MIMEText

LOGFILE = "/var/log/app/app.log"
COOLDOWN = 60
last_alert_time = 0

def send_alert(line, retries=3):
    global last_alert_time
    msg = MIMEText(f"Error detected in application logs:\n\n{line}")
    msg["Subject"] = "App Error Detected"
    msg["From"] = os.environ["SMTP_USER"]
    msg["To"] = os.environ["ALERT_TO"]

    for attempt in range(retries):
        try:
            with smtplib.SMTP(os.environ["SMTP_HOST"], int(os.environ["SMTP_PORT"])) as s:
                s.starttls()
                s.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"])
                s.send_message(msg)
            print(f"[ALERT SENT] {line.strip()}")
            last_alert_time = time.time()
            return
        except Exception as e:
            print(f"[ATTEMPT {attempt+1} FAILED] {e}")
            time.sleep(2 ** attempt)
    print("[ALL RETRIES FAILED - giving up on this alert]")

def wait_for_file(path):
    while not os.path.exists(path):
        print("Waiting for log file to appear...")
        time.sleep(2)

def tail(f):
    f.seek(0, 2)
    while True:
        line = f.readline()
        if not line:
            time.sleep(1)
            continue
        yield line

wait_for_file(LOGFILE)
print("Log watcher started, monitoring:", LOGFILE)

with open(LOGFILE) as f:
    for line in tail(f):
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        if entry.get("level") == "ERROR":
            now = time.time()
            if now - last_alert_time > COOLDOWN:
                send_alert(line)
            else:
                print(f"[SUPPRESSED - cooldown active] {line.strip()}")
