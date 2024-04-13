import imaplib
import email
from email.header import decode_header
import base64
from bs4 import BeautifulSoup
import re

mail_pass = "7PP4ZDXqnv"
username = "lazutkina@cs.vsu.ru"
imap_server = "info.vsu.ru"
imap = imaplib.IMAP4_SSL(imap_server)
imap.login(username, mail_pass)

imap.search(None, 'ALL')

letter_date = email.utils.parsedate_tz(msg["Date"]) # дата получения, приходит в виде строки, дальше надо её парсить в формат datetime
letter_id = msg["Message-ID"] #айди письма
letter_from = msg["Return-path"] # e-mail отправителя

print((letter_date))

imap.list()
imap.select("inbox")
result, data = imap.search(None, "ALL")

ids = data[0]
id_list = ids.split()
latest_email_id = id_list[-1]

result, data = imap.fetch(latest_email_id, "(RFC822)")
raw_email = data[0][1]
raw_email_string = raw_email.decode('utf-8')
raw_email_string

import email
import html2text

email_message = email.message_from_string(raw_email_string)

if email_message.is_multipart():
    for payload in email_message.get_payload():
        body = payload.get_payload(decode=True).decode('utf-8')
        h = html2text.HTML2Text()
        h.ignore_links = False

        print(h.handle(body))

else:
    body = email_message.get_payload(decode=True).decode('utf-8')
    print(body)

imap.select("inbox", readonly = False)
result, data = imap.search(None, "ALL")
ids = data[0]
id_list = ids.split()
print(ids)
imap.create('INBOX.Completed')
imap.create("'INBOX.Обращения'")
for mail_id in id_list:
    copy_res = imap.copy(mail_id, 'INBOX.Completed')
    print(copy_res)

msg["Subject"] #если тема письма написана латиницей, то извлекается так же

msg2 = email.message_from_bytes(msg2[0][1])

msg2["Subject"]

decode_header(msg2["Subject"])

decode_header(msg2["Subject"])[0][0].decode()

for part in msg.walk():
    print(part.get_content_type())

for part in msg2.walk():
    if part.get_content_maintype() == 'text' and part.get_content_subtype() == 'plain':
        print(part.get_payload())