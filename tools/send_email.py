# encoding = utf-8

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
import random
import datetime
from main_settings import directory, EMAIL, EMAIL_PASSWORD, SMTP_ADDRESS


def send_email(receiver, name):
    username = name
    email = receiver
    sender = EMAIL
    password = EMAIL_PASSWORD
    smtp_address = SMTP_ADDRESS
    port = 465
    email_content = open(directory+"tools/email.html", 'r', encoding='utf-8').read()
    verification = ""
    for i in range(6):
        verification += str(random.randint(0, 6))
    template = Template(email_content)
    template = template.render(name=name, Verification=verification, date=datetime.datetime.today().strftime("%Y年%m月%d日"))
    message = MIMEText(template, 'html', 'utf-8')
    multi_msg = MIMEMultipart()
    multi_msg.attach(message)
    multi_msg['Subject'] = '[FuSite] 验证码'
    multi_msg['From'] = sender
    multi_msg['To'] = receiver
    content = multi_msg.as_string()
    server = smtplib.SMTP_SSL(smtp_address, port)
    server.login(sender, password)
    server.sendmail(sender, receiver, content)
    server.quit()
    now = datetime.datetime.now() + datetime.timedelta(minutes=20)
    return [username, email, verification, (now.year, now.month, now.day, now.hour, now.minute, now.second)]
