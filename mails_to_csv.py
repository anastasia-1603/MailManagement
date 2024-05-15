import re
import dateparser
import pandas as pd
from imap_tools import MailBox


def mails_to_csv(host, username, password, email_folder_name, csv_name, csv_path):
    mailbox = login_mailbox(password="7PP4ZDXqnv", username="lazutkina@cs.vsu.ru", host="info.vsu.ru")
    mailbox.folder.set(email_folder_name)
    mails = mailbox.fetch()
    df = mails_to_df(mails)
    clean_df(df)
    df.to_csv(csv_path+csv_name, index=False)


def login_mailbox(host, username, password):
    mailbox = MailBox(host)
    mailbox.login(username=username, password=password)
    return mailbox


def mails_to_df(mails):
    columns = ['id', 'subject', 'from', 'text', 'date', 'attachment_filename', 'attachment_content_type']
    mails_list = []
    for msg in mails:
        attachment_filename = ",".join(str(att.filename) for att in msg.attachments)
        attachment_content_type = ",".join(str(att.content_type) for att in msg.attachments)
        mails_list.append([msg.uid, msg.subject, msg.from_, msg.text, msg.date_str,
                           attachment_filename, attachment_content_type])

    df = pd.DataFrame(data=mails_list)
    df.columns = columns
    return df


def preprocess_fwd(df: pd.DataFrame):
    for index, row in df.iterrows():
        text = row['text']
        if text:
            if 'Пересылаемое сообщение' in text:
                sender = re.search(r'От кого: (.*?)\n', text).group(1)
                df.at[index, 'from'] = sender
                date = re.search(r'Дата: (.*?)\n', text).group(1)
                df.at[index, 'date'] = date
                subject = re.search(r'Тема: (.*?)\n', text)
                if subject is not None:
                    message = text.split(subject.group(1))[1]
                else:
                    message = text.split(date)[1]
                df.at[index, 'text'] = message

        else:
            df.at[index, 'text'] = 'Нет тела сообщения'
    return df


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


def preprocess_date(dates):
    column = []
    for date in dates:
        column.append(dateparser.parse(date).strftime("%d.%m.%Y %H:%M:%S"))
    return column


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


# password = "7PP4ZDXqnv"
# username = "lazutkina@cs.vsu.ru"
# host = "info.vsu.ru"

mails_to_csv(password="7PP4ZDXqnv", username="lazutkina@cs.vsu.ru", host="info.vsu.ru", email_folder_name='INBOX/тест',
             csv_name='output3.csv', csv_path='')
