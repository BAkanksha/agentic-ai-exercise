
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
from dotenv import load_dotenv

load_dotenv(override=True)


def send_email(subject: str, text_body: str, html_body: str) -> None:
    email_from = os.getenv("EMAIL_FROM")
    app_password = os.getenv("EMAIL_APP_PASSWORD")
    email_to = os.getenv("EMAIL_TO")

    if not (email_from and app_password and email_to):
        print("[DRY RUN] Email settings not found in .env, printing instead of sending.")
        print(f"Subject: {subject}\n\n{text_body}\n")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = email_from
    msg["To"] = "akanksha78si@gmail.com"
    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(email_from, app_password)
        server.sendmail(email_from, [email_to], msg.as_string())
    print("Email sent.")


def push(message: str) -> None:
    user = os.getenv("PUSHOVER_USER")
    token = os.getenv("PUSHOVER_TOKEN")

    if not (user and token):
        print(f"[DRY RUN] Pushover keys not found, printing instead:\n{message}\n")
        return

    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={"user": user, "token": token, "message": message},
        timeout=30,
    )