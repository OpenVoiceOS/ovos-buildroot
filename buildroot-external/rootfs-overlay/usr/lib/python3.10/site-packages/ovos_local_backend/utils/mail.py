from ovos_local_backend.configuration import CONFIGURATION
from ovos_utils.smtp_utils import send_smtp


def send_email(subject, body, recipient=None):
    mail_config = CONFIGURATION["email"]

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
