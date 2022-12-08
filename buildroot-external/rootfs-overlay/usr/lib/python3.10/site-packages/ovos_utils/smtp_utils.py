from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP_SSL

from ovos_config import Configuration


def send_smtp(user, pswd, sender,
              destinatary, subject, contents,
              host, port=465):
    with SMTP_SSL(host=host, port=port) as server:
        server.login(user, pswd)
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = destinatary
        msg['Subject'] = subject
        msg.attach(MIMEText(contents))
        server.sendmail(sender, destinatary, msg.as_string())


def send_email(subject, body, recipient=None):
    mail_config = Configuration.get("email") or {}
    if not mail_config:
        raise KeyError("email configuration not set")

    smtp_config = mail_config["smtp"]
    user = smtp_config["username"]
    pswd = smtp_config["password"]
    host = smtp_config["host"]
    port = smtp_config.get("port", 465)

    recipient = recipient or mail_config.get("recipient") or user

    send_smtp(user, pswd,
              user, recipient,
              subject, body,
              host, port)


if __name__ == "__main__":
    USER = "JarbasAI"
    YOUR_EMAIL_ADDRESS = "jarbasai@mailfence.com"
    DESTINATARY_ADDRESS = "casimiro@jarbasai.online"
    YOUR_PASSWORD = "a very very strong Password1!"
    HOST = "smtp.mailfence.com"
    PORT = 465

    subject = 'test again'
    body = 'this is a test bruh'

    send_email(USER, YOUR_PASSWORD,
               YOUR_EMAIL_ADDRESS, DESTINATARY_ADDRESS,
               subject, body,
               HOST, PORT)
