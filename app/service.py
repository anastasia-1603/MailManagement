import imaplib
import email
from email.header import decode_header
import base64

import dateparser
from bs4 import BeautifulSoup
import re
import chardet
from dateparser.search import search_dates
from imap_tools import MailBox
from imap_tools import MailMessage
from imap_tools import MailboxLoginError
from imap_tools import AND, OR, NOT, A, H, U


def get_host(service):
    hosts = {"cs.vsu.ru": "info.vsu.ru"}
    # "Mail.ru": "imap.mail.ru",
    # "Gmail": "imap.gmail.com",
    # "Outlook": "outlook.office365.com"
    return hosts[service]


def preprocess_date(msg: MailMessage):
    headers = msg.headers
    text = str(msg.text)
    date = str(msg.date)
    if 'x-original-date' in headers:
        date = headers['x-original-date'][0]

    if 'Sent:' in text:
        date = re.search(r'Sent: (.*?)\n', text).group(1)

    dp = dateparser.parse(date)
    if dp is not None:
        date = dp.strftime("%d.%m.%Y %H:%M:%S")
    else:
        date = search_dates(date)[0][1].strftime("%d.%m.%Y %H:%M:%S")
    return date


def preprocess_from(msg: MailMessage):
    headers = msg.headers
    text = msg.text
    x_from = msg.from_
    if 'x-original-from' in headers:
        x_from = headers['x-original-from'][0]
    elif 'From:' in text:
        x_from = re.search(r'From: (.*?)\n', text).group(1)

    if len(decode_header(x_from)) == 2:
        encoding = decode_header(x_from)[0][1]
        name = decode_header(x_from)[0][0]
        if encoding is not None:
            name = name.decode(encoding)

        address = decode_header(x_from)[1][0].decode()
        x_from = name + ' ' + address

    return x_from


def preprocess_subject(msg: MailMessage):
    subject = msg.subject
    if subject is not None and subject != '':
        subject = subject.removeprefix("FWD:").removeprefix("Fwd:")
    else:
        subject = 'Нет темы'
    return subject


def preprocess_attachments(msg: MailMessage):
    att_str = 'Нет вложений'
    if msg.attachments is not None and len(msg.attachments) != 0:
        att_str = ",".join(str(att.filename) for att in msg.attachments)
    return att_str


class Mail:
    def __init__(self, msg: MailMessage):
        self.msg = msg
        self.uid = msg.uid
        self.body: str = msg.text
        self.subject: str = preprocess_subject(msg)
        self.sender: str = preprocess_from(msg)
        attachment_filename = preprocess_attachments(msg)
        attachment_content_type = ",".join(str(att.content_type) for att in msg.attachments)
        self.attachment_name: str = attachment_filename
        self.attachment_type: str = attachment_content_type
        self.date = preprocess_date(msg)

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

    def to_str(self):
        return f"Тема: {self.subject}\nВложения: {self.attachment_name}\n{self.body}"


def auth(username, password, host):
    mailbox = MailBox(host)
    res = mailbox.login(username=username, password=password)
    return res, mailbox


class MailService:
    def __init__(self, service, username, password):
        self.host = get_host(service)
        self.username = username
        self.password = password
        self.mailbox = None
        # res, self.imap = auth(password=password, username=username, host=host)

    def auth(self):
        mailbox = MailBox(self.host)
        try:
            self.mailbox = mailbox.login(username=self.username, password=self.password)
            res = self.mailbox.login_result
        except MailboxLoginError as e:
            res = e.command_result
        return res

    def send_email(self, recipient, subject, body):
        pass

    def get_folders_list(self):
        folders = []
        for i in self.mailbox.folder.list('INBOX'):
            k = i.name.split('/')
            folders.append(k[1])
        return folders

    def get_mail(self, mail_id):
        msg = self.mailbox.fetch(AND(uid=mail_id), mark_seen=False)
        return Mail(msg)

    def get_latest_mail(self):
        mails = self.mailbox.fetch(limit=1, reverse=True, mark_seen=False)
        msgs = []
        for m in mails:
            msgs.append(m)
        msg = msgs[0]
        return Mail(msg)

    def get_all_emails(self):
        # columns = ['id', 'subject', 'from', 'text', 'date', 'attachment_filename', 'attachment_content_type']
        mails_list = [Mail]
        mails = self.mailbox.fetch(mark_seen=False)
        for msg in mails:
            mail = Mail(msg)
            mails_list.append(mail)
        return mails_list

    def copy_to_folder(self, mail, folder_str):
        f = 'INBOX/'+folder_str
        exist = self.mailbox.folder.exists(f)
        res = ''
        if exist:
            res = self.mailbox.copy(mail.uid, f)
        else:
            res_create = self.mailbox.folder.create(f)
            print(res_create)
            if 'OK' in res_create:
                res = self.mailbox.copy(mail.uid, f)
        return res


