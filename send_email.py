import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googletrans import Translator

def translate_text(text, dest_language="ko"):
    translator = Translator()
    translated = translator.translate(text, dest=dest_language)
    return translated.text

def send_email(summary):
    sender_email = os.getenv("EMAIL")
    receiver_email = "receiver_email@example.com"
    password = os.getenv("PASSWORD")

    # 번역기 설정
    translated_summary = translate_text(summary)

    message = MIMEMultipart("alternative")
    message["Subject"] = "Latest Summary"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = f"Here is the latest summary:\n\n{translated_summary}"
    part = MIMEText(text, "plain")
    message.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

# 요약된 내용을 파일에서 읽어와서 이메일로 전송
with open("api/latest.js", "r", encoding="utf-8") as f:
    summary = f.read()
    send_email(summary)
