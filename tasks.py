import smtplib
import ssl
from email.message import EmailMessage
from settings import settings


async def send_mail(payload):
    msg = EmailMessage()
    msg['From'] = settings.email_host_user
    msg['To'] = payload.get('recipient')
    msg['Subject'] = payload.get('subject')
    msg.set_content(payload.get('message'))
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(settings.smtp, settings.smtp_port, context=context) as smtp:
        smtp.login(user=settings.email_host_user, password=settings.email_host_password)
        smtp.sendmail(settings.email_host_user, payload.get('recipient'), msg.as_string())
        smtp.quit()
    return f"Mail sent to {payload.get('recipient')}"
