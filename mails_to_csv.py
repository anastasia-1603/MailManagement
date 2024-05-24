import re
import dateparser
import pandas as pd
from imap_tools import MailBox
from email.header import decode_header

# def mails_to_csv_source(host, username, password, email_folder_name, csv_name, csv_path):
#     mailbox = login_mailbox(password=password, username=username, host=host)
#     mailbox.folder.set(email_folder_name)
#     mails = mailbox.fetch()
#     df = mails_to_df(mails)
#     # clean_df(df)
#     df.to_csv(csv_path + csv_name, index=False)


def login_mailbox(host, username, password, initial_folder='INBOX'):
    mailbox = MailBox(host)
    mailbox.login(username=username, password=password, initial_folder=initial_folder)
    return mailbox


def mails_to_df(mails):
    columns = ['id', 'subject', 'from', 'text', 'date', 'attachment_filename', 'attachment_content_type', 'headers']
    mails_list = []
    for msg in mails:
        attachment_filename = ",".join(str(att.filename) for att in msg.attachments)
        attachment_content_type = ",".join(str(att.content_type) for att in msg.attachments)

        mails_list.append(
            [msg.uid, msg.subject, msg.from_, msg.text, msg.date_str, attachment_filename, attachment_content_type,
             msg.headers])

    df = pd.DataFrame(data=mails_list)
    df.columns = columns
    return df


def preprocess_fwd(df: pd.DataFrame):
    for index, row in df.iterrows():
        text = row['text']
        if text:
            if 'Пересылаемое сообщение' in text:
                sender = re.search(r'От кого: (.*?)\n', text)
                df.at[index, 'from'] = sender
                date = re.search(r'Дата: (.*?)\n', text).group(1)
                df.at[index, 'date'] = date
                subject = re.search(r'Тема: (.*?)\n', text)
                if sender is not None:
                    sender = sender.group(1)
                else:
                    sender = ''
                if subject is not None:
                    message = text.split(subject.group(1))[1]
                else:
                    message = text.split(date)[1]
                df.at[index, 'text'] = message

        else:
            df.at[index, 'text'] = 'Нет тела сообщения'
    return df


def preprocess_from(df):
    for index, row in df.iterrows():
        headers = row['headers']
        text = row['text']
        x_from = ''
        if 'x-original-from' in headers:
            x_from = headers['x-original-from'][0]

        elif 'From:' in text:
            x_from = re.search(r'From: (.*?)\n', text).group(1)

        if len(decode_header(x_from)) == 2:
            name = decode_header(x_from)[0][0].decode()
            address = decode_header(x_from)[1][0].decode()
            x_from = name + ' ' + address

        df.at[index, 'from'] = x_from


def clean_df(df):
    df['subject'] = preprocess_subject(df['subject'])
    preprocess_fwd(df)
    df['date'] = preprocess_date(df['date'])
    df['text'] = preprocess_text(df['text'])


def preprocess_subject(subjects: list[str]):
    column = []
    for s in subjects:
        if s:
            column.append(s.removeprefix("Fwd: "))
        else:
            column.append('Нет темы')
    return column


def preprocess_date(df):
    for index, row in df.iterrows():
        headers = row['headers']
        text = row['text']
        if 'x-original-date' in headers:
            x_orig_date = headers['x-original-date'][0]
            df.at[index, 'date'] = x_orig_date
        if 'Sent:' in text:
            date = re.search(r'Sent: (.*?)\n', text).group(1)
            df.at[index, 'date'] = date
    return df


def preprocess_text(texts):
    column = []
    for t in texts:
        t = re.sub(r'\n+', ' ', t)
        # delete punctuation
        # t = re.sub("[" + string.punctuation + "]", " ", t)
        t = re.sub(r'-{2,}', '', t)
        t = re.sub(r'\s+', ' ', t)
        column.append(t)
    return column


#
# mails_to_csv_source(password="7PP4ZDXqnv", username="lazutkina@cs.vsu.ru", host="info.vsu.ru",
#                     email_folder_name='INBOX',
#                     csv_name='vestnik.csv', csv_path='')

password = "7PP4ZDXqnv"
username = "lazutkina@cs.vsu.ru"
host = "info.vsu.ru"
email_folder_name = 'INBOX'
csv_name = 'vestnik.csv'
csv_path = ''

mailbox = login_mailbox(password=password, username=username, host=host)
mails = mailbox.fetch()
df = mails_to_df(mails)
# clean_df(df)
df.to_csv(csv_path + csv_name, index=False)
