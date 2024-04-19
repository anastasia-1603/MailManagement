import imaplib
import email
from email.header import decode_header
import base64
from bs4 import BeautifulSoup
import re


def get_host(service):
    dict = {"cs.vsu.ru": "info.vsu.ru",
            "Mail.ru": "imap.mail.ru",
            "Gmail": "imap.gmail.com",
            "Outlook": "outlook.office365.com"}
    return dict[service]


class Mail:
    def __init__(self):
        self.body: str = None
        self.subject: str = None
        self.sender: str = None
        self.attachment_name: str = None
        self.attachment_type: str = None

    def set_body(self, body):
        self.body = body

    def set_subject(self, subject):
        self.subject = subject

    def set_sender(self, sender):
        self.sender = sender

    def set_attachment_name(self, attachment_name):
        self.attachment_name = attachment_name

    def set_attachment_type(self, attachment_type):
        self.attachment_type = attachment_type

    def print_mail(self):
        print(f"Subject={self.subject}, \nbody={self.body}")


class MailService:
    def __init__(self, service, username, password):
        self.service = service
        self.host = get_host(service)
        self.username = username
        self.password = password
        self.imap = imaplib.IMAP4_SSL(self.host)

    def auth(self):
        res = self.imap.login(self.username, self.password)
        print(res)
        self.get_mail()

    def send_email(self, recipient, subject, body):
        pass

    def get_folders(self):
        for i in self.imap.list()[1]:
            k = i.decode().split(' "/" ')
            print(k[0] + " = " + k[1])
        return self.imap.list()[1]

    def get_mail(self):
        self.imap.list()
        self.imap.select("inbox")
        result, data = self.imap.search(None, "ALL")
        ids = data[0]
        id_list = ids.split()
        latest_email_id = id_list[-1]
        result, data = self.imap.fetch(latest_email_id, "(RFC822)")
        mail = Mail()
        for response in data:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # decode the email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    # if it's a bytes, decode to str
                    subject = subject.decode(encoding)
                    mail.subject = subject
                # decode email sender
                sender, encoding = decode_header(msg.get("From"))[0]
                if isinstance(sender, bytes):
                    sender = sender.decode(encoding)
                    mail.sender = sender
                # print("Subject:", subject)
                # print("From:", sender)
                # if the email message is multipart
                if msg.is_multipart():
                    # iterate over email parts
                    for part in msg.walk():
                        # extract content type of email
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            # get the email body
                            body = part.get_payload(decode=True).decode()

                        except:
                            pass
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            # print text/plain emails and skip attachments
                            mail.body = body
                        elif "attachment" in content_disposition:
                            content_type = part.get_content_type()
                            filename = decode_header(part.get_filename())[0][0].decode()
                            if filename:
                                mail.attachment_type = content_type
                                mail.attachment_name = filename
                                # print("Filename:", filename)
                                # print("type:", content_type)
                else:

                    content_type = msg.get_content_type()
                    # get the email body
                    body = msg.get_payload(decode=True).decode()
                    if content_type == "text/plain":
                        # print only text email parts
                        mail.body = body
        mail.print_mail()
