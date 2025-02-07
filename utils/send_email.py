import threading

from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage


def send_mail(subject, body, from_email, recipient_list, fail_silently=False,
              html=None, attach=None, file=None, *args, **kwargs):
    msg = EmailMultiAlternatives(
        subject, body, from_email, recipient_list
    )

    if html:
        msg.attach_alternative(html, "text/html")

    # Si adjunta un archivo
    if attach:
        msg_image = MIMEImage(file.read())
        msg_image.add_header('Content-ID', '<{}>'.format(
            "<" + file.name + ">")
                             )
        msg_image.add_header(
            "Content-Disposition", "inline",
            filename=file.name
        )
        msg.attach(msg_image)

    # msg.send(fail_silently)
    msg.send(fail_silently)



class EmailThread(threading.Thread):
    """
    Class para enviar un email con thread.
    """

    def __init__(self, subject, body, from_email, recipient_list,
                 fail_silently, html, attach, file):
        self.subject = subject
        self.body = body
        self.recipient_list = recipient_list
        self.from_email = from_email
        self.fail_silently = fail_silently
        self.html = html
        self.attach = attach
        self.file = file
        threading.Thread.__init__(self)

    def run(self):
        send_mail(self.subject, self.body, self.from_email, self.recipient_list, self.fail_silently,
                      self.html, self.attach, self.file)


def send_mail_thread(subject, body, from_email, recipient_list, fail_silently=False,
              html=None, attach=None, file=None, *args, **kwargs):
    """
    Send email
    """
    EmailThread(
        subject, body, from_email, recipient_list,
        fail_silently, html, attach, file
    ).start()