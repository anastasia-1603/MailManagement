import imaplib
import email
from email.header import decode_header
import base64
from bs4 import BeautifulSoup
import re
import chardet
from imap_tools import MailBox


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


def auth(username, password, host):
    mailbox = MailBox(host)
    mailbox.login(username=username, password=password)
    return mailbox


class MailService:
    def __init__(self, service, username, password):
        self.service = service
        host = get_host(service)
        self.imap = auth(password=password, username=username, host=host)

    def send_email(self, recipient, subject, body):
        pass

    def get_folders_list(self):
        folders = []
        for i in self.imap.folder.list('INBOX'):
            k = i.decode().split(' "/" ')
            folders.append(k[1])
        return folders

    def get_mail(self, mail_id):
        self.imap.list()
        self.imap.select("inbox")
        result, data = self.imap.fetch(mail_id, "(RFC822)")
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
                            # body = part.get_payload(decode=True).decode()
                            payload = part.get_payload(decode=True)
                            if payload is None:
                                continue
                            body = payload.decode()

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
                    payload = part.get_payload(decode=True)
                    if payload is None:
                        continue
                    body = payload.decode()
                    if content_type == "text/plain":
                        # print only text email parts
                        mail.body = body
        mail.print_mail()

    def get_latest_mail(self):
        self.imap.select("inbox")
        result, data = self.imap.search(None, "ALL")
        id_list = data[0].split()
        latest_email_id = id_list[-1]
        self.get_mail(latest_email_id)

    def get_all_emails(self):
        self.imap.select("inbox")
        result, data = self.imap.search(None, "ALL")
        data = data[0].split()

        for i in data:

            status, data = self.imap.fetch(i, '(RFC822)')
            data = data[0][1]
            enc = chardet.detect(data)
            print(f"\n\n\nID сообщения: {i}\nКодировка: {enc}")

            msg = email.message_from_bytes(data)
            print("From: ", msg['From'])
            print("Date: ", msg['Date'])
            print("Subject: ", msg['Subject'])

            if msg.is_multipart():
                print("Multipart: Yes")
                for part in msg.walk():
                    payload = part.get_payload(decode=True)
                    if payload is None:
                        continue
                    payload = payload.decode()
                    # payload = part.get_payload(decode=True).decode('utf-8')

            else:
                print("Multipart: No")
                payload = msg.get_payload(None).decode('utf-8')

            print("Тип Payload: ", type(payload))
            print("Payload: ", payload)
        # self.imap.close()

    def new_way_get_mails(self):

        # get emails from INBOX folder
        with MailBox(self.host).login(self.username, self.password, 'INBOX') as mailbox:
            for msg in mailbox.fetch():
                print(msg.uid)  # str or None: '123'
                print(msg.subject)  # str: 'some subject 你 привет'
                print(msg.from_)  # str: 'sender@ya.ru'
                print(msg.to)  # tuple: ('iam@goo.ru', 'friend@ya.ru', )
                print(msg.cc)  # tuple: ('cc@mail.ru', )
                print(msg.bcc)  # tuple: ('bcc@mail.ru', )
                print(msg.reply_to)  # tuple: ('reply_to@mail.ru', )
                print(msg.date)  # datetime.datetime: 1900-1-1 for unparsed, may be naive or with tzinfo
                print(msg.date_str)  # str: original date - 'Tue, 03 Jan 2017 22:26:59 +0500'
                print(msg.text)  # str: 'Hello 你 Привет'
                print(msg.html)  # str: '<b>Hello 你 Привет</b>'
                print(msg.flags)  # tuple: ('SEEN', 'FLAGGED', 'ENCRYPTED')
                print(msg.headers)  # dict: {'Received': ('from 1.m.ru', 'from 2.m.ru'), 'AntiVirus': ('Clean',)}

                for att in msg.attachments:  # list: [Attachment]
                    print(att.filename)  # str: 'cat.jpg'
                    print(att.content_type)  # str: 'image/jpeg'
                    # print(att.payload)  # bytes: b'\xff\xd8\xff\xe0\'
