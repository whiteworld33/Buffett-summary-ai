import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(summary):
    sender_email = "buffettsummary.bot"
    receiver_email = "whiteworld33@gmail.com"
    password = "buffettsumm@ryb0t"

    message = MIMEMultipart("alternative")
    message["Subject"] = "Latest Summary"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = f"Here is the latest summary:\n\n{summary}"
    part = MIMEText(text, "plain")
    message.attach(part)

    with smtplib.SMTP_SSL("smtp.example.com", 465) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

# 요약된 내용을 파일에서 읽어와서 이메일로 전송
with open("api/latest.js", "r", encoding="utf-8") as f:
    summary = f.read()
    send_email(summary)
