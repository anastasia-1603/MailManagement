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

    def send_email(self, recipient, subject, body):
        pass
