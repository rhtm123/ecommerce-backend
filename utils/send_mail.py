import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from decouple import config

EMAIL_PASSWORD = config("EMAIL_HOST_PASSWORD")
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST = config("EMAIL_HOST")


class EmailThread(threading.Thread):
    """
    Threaded Email Sender
    """
    def __init__(self, msg):
        self.msg = msg
        threading.Thread.__init__(self)

    def run(self):
        try:
            server = smtplib.SMTP(EMAIL_HOST, 587)
            server.starttls()
            server.login(EMAIL_HOST_USER, EMAIL_PASSWORD)
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

    from_email = from_email or EMAIL_HOST_USER

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
