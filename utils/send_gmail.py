import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from django.conf import settings

from decouple import config

GMAIL_APP_PASSWORD = config("GMAIL_APP_PASSWORD")
GMAIL_HOST_USER = config("GMAIL_HOST_USER")


class EmailThread(threading.Thread):
    """
    Threaded Email Sender
    """
    def __init__(self, msg):
        self.msg = msg
        threading.Thread.__init__(self)

    def run(self):
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(GMAIL_HOST_USER, GMAIL_APP_PASSWORD)
            server.sendmail(
                self.msg["From"],
                self.msg["To"].split(","),    # handles multiple emails
                self.msg.as_string()
            )
            server.quit()
        except Exception as e:
            print("Email sending error:", e)


def send_mail(
    subject,
    body,
    recipient_list,
    html=None,
    attachments=None,
    from_email=None
):
    """
    Unified email sending helper
    """

    from_email = from_email or GMAIL_HOST_USER

    # Multipart alternative for HTML + Text
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = ",".join(recipient_list)

    # Plain text fallback
    msg.attach(MIMEText(body, "plain"))

    # HTML part
    if html:
        msg.attach(MIMEText(html, "html"))

    # Attachments (list of file paths)
    if attachments:
        for file_path in attachments:
            try:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(open(file_path, "rb").read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={file_path.split('/')[-1]}"
                )
                msg.attach(part)
            except Exception as e:
                print("Attachment error:", e)

    # send email in a thread
    EmailThread(msg).start()
