import smtplib
import ssl
from email.message import EmailMessage
import config



def send_email(subject, body, email_receiver):
    try:
        subject = subject
        body = body

        em = EmailMessage()
        em["From"] = config.email_sender
        em["To"] = email_receiver
        em["Subject"] = subject
        em.set_content(body)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:

            smtp.login(config.email_sender, config.email_app_password)
            smtp.sendmail(config.email_sender, email_receiver, em.as_string())
    except Exception as ex:
        pass
