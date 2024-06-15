import re
from email.header import decode_header
import dateparser
from dateparser.search import search_dates
from imap_tools import AND, A
from imap_tools import MailBox
from imap_tools import MailMessage
from imap_tools import MailboxLoginError
from sentence_embeddings import *
import time, socket, imaplib, traceback
from imap_tools import MailboxLoginError, MailboxLogoutError
import logging
from transliterate import translit, get_available_language_codes

categ_flag_dict = {"вопросы": "VOPROSY", "готово к публикации": "GOTOVO_K_PUBLIKATSII",
                   "доработка": "DORABOTKA", "другое": "DRUGOE",
                   "отклонена": "OTKLONENA", "подача статьи": "PODACHA_STAT'I",
                   "проверка статьи": "PROVERKA_STAT'I", "рецензирование": "RETSENZIROVANIE"}

logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")


def get_categ_by_flag(flag):
    if flag in categ_flag_dict.values():
        categ = list(categ_flag_dict.keys())[list(categ_flag_dict.values()).index(flag)]
    else:
        categ = 'Нет категории'  # todo фиг знает
    return categ


def get_flag_by_categ(category):
    if category in categ_flag_dict.keys():
        return categ_flag_dict[category.lower()]


def get_host(service):
    hosts = {"cs.vsu.ru": "info.vsu.ru", "Mail.ru": "imap.mail.ru"}
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


def predict_category(text):
    """
    Возвращает категорию с большой буквы и вероятность
    @param text:
    @return:
    """
    res = predict(text)
    res = res.split(sep='\n')[0].split(sep=':')
    categ = res[0].strip()
    acc = res[1].strip()
    return categ, acc


def write_log(msg):
    logging.info(msg)


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
        # self.category = 'Нет категории'

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

    # def set_category(self, category):
    #     self.category = category

    def classify(self):
        """
        Возвращает категорию с большой буквы
        @return:
        """
        text = self.to_str()
        pred = predict_category(text)

        # self.category = pred[0]
        return pred[0]

    def to_str(self):
        return f"Тема: {self.subject}\nВложения: {self.attachment_name}\n{self.body}"


def auth(username, password, host):
    mailbox = MailBox(host)
    res = mailbox.login(username=username, password=password)
    return res, mailbox


class MailService:
    def __init__(self, service, username, password, logger=None):
        self.host = get_host(service)
        self.username = username
        self.password = password
        self.mailbox = None
        self.done = True
        self.logger = logger
        # res, self.imap = auth(password=password, username=username, host=host)

    def auth(self):
        mailbox = MailBox(self.host)
        try:
            self.mailbox = mailbox.login(username=self.username, password=self.password)
            res = self.mailbox.login_result
            logging.info(f"New connection {time.asctime()}. Login result {res}")
            self.logger.log(f"New connection {time.asctime()}. Login result {res}")
        except MailboxLoginError as e:
            res = e.command_result
            logging.error(f"Try connection {time.asctime()}. Login result {res}")
            self.logger.log(f"Try connection {time.asctime()}. Login result {res}")
        return res

    def get_folders_list(self):
        folders = []
        for i in self.mailbox.folder.list('INBOX'):
            k = i.name.split('/')
            folders.append(k[1])
        return folders

    def get_raw_folders_list(self):
        folders = []
        for i in self.mailbox.folder.list('INBOX'):
            k = i.name
            folders.append(k)
        return folders

    def get_folder_size(self, folder='INBOX'):

        # folder = 'INBOX/' + folder
        stat = self.mailbox.folder.status(folder)
        # {'MESSAGES': 41, 'RECENT': 0, 'UIDNEXT': 11996, 'UIDVALIDITY': 1, 'UNSEEN': 5}
        return stat['MESSAGES']

    def get_mail(self, mail_id):
        msgs = self.mailbox.fetch(AND(uid=mail_id), mark_seen=False)
        msg = [m for m in msgs][0]
        return Mail(msg)

    def flag_classified(self, uid, category):
        mail = self.get_mail(uid)
        if 'CHECKED' in mail.msg.flags:
            flags = ['VOPROSY', 'GOTOVO_K_PUBLIKATSII', 'DORABOTKA',
                     'DRUGOE', 'OTKLONENA', "PODACHA_STAT'I",
                     "PROVERKA_STAT'I", 'RETSENZIROVANIE']
            self.mailbox.flag(uid, flags, False)
        # flag = translit(category, 'ru', reversed=True)
        # flag = '_'.join(flag.split()).upper()
        flag = get_flag_by_categ(category)
        res = self.mailbox.flag(uid, ['CHECKED', flag], True)
        logging.info(f"Try to flag mail {uid} with flag {flag}. Result {res}")
        self.logger.log(f"Try to flag mail {uid} with flag {flag}. Result {res}")
        return res

    # def classify_mail_by_uid(self, uid):
    #     mail = self.get_mail(uid)
    #     return self.classify_mail(mail)

    def classify_and_flag_mail(self, mail):
        """
        Возвращает категорию с большой буквы.
        Присваивает сообщению флаг.
        @param mail:
        @return:
        """
        categ = mail.classify()
        self.flag_classified(mail.uid, categ)
        logging.info(f"Classify email {mail.uid} in category {categ}")
        self.logger.log(f"Classify email {mail.uid} in category {categ}")
        return categ

    def classify_mail(self, mail):
        """
        Возвращает категорию с большой буквы.
        @param mail:
        @return:
        """
        categ = mail.classify()
        logging.info(f"Classify email {mail.uid} in category {categ}")
        self.logger.log(f"Сообщение {mail.uid} отнесено к категории {categ}")
        return categ

    def flag_classified_mail(self, mail):
        res = self.flag_classified(mail.uid, mail.category)
        return res

    def get_latest_mail(self):
        mails = self.mailbox.fetch(limit=1, reverse=True, mark_seen=False)
        msg = [m for m in mails][0]
        return Mail(msg)

    def get_latest_mails(self, count):
        mails = self.mailbox.fetch(limit=count, reverse=True, mark_seen=False)
        msgs = [Mail(msg) for msg in mails]
        return msgs

    def get_all_emails(self):
        # columns = ['id', 'subject', 'from', 'text', 'date', 'attachment_filename', 'attachment_content_type']
        mails_list = [Mail]
        mails = self.mailbox.fetch(mark_seen=False)
        for msg in mails:
            mail = Mail(msg)
            mails_list.append(mail)
        return mails_list

    def get_all_folder_emails(self, folder):
        mails_list = []
        self.mailbox.folder.set(folder)
        mails = self.mailbox.fetch(mark_seen=False)
        for msg in mails:
            mail = Mail(msg)
            mails_list.append(mail)
        return mails_list

    def mail_is_already_in_folder(self, uid, folder):
        mails = self.get_all_folder_emails(folder)
        uids = [m.uid for m in mails]
        return uid in uids

    # def copy_mails_to_folder(self, mails, folder):
    #     for m in mails:
    #         self.copy_to_folder(m, folder)

    def copy_to_folder(self, mail, folder, initial_folder="INBOX"):
        if folder != '':
            f = initial_folder + '/' + folder
        else:
            f = initial_folder
        exist = self.mailbox.folder.exists(f)
        res = ''
        if exist:
            if not self.mail_is_already_in_folder(mail.uid, f):
                res = self.mailbox.copy(mail.uid, f)
                logging.info(f"Copy mail {mail.uid} to folder {f}. Result {res}")
                if 'ОК' in res:
                    self.logger.log(f"Сообщение {mail.uid} успешно скопировано в папку {f}.")
                else:
                    self.logger.log(f"Сообщение {mail.uid} не получилось скопировать в папку {f}. Ошибка {str(res[1])}")
            else:
                res = 'Mail already in folder'
                logging.info(f"Mail {mail.uid} already in folder {f}")
                self.logger.log(f"Сообщение {mail.uid} уже находится в папке {f}")
        else:
            res_create = self.mailbox.folder.create(f)
            logging.info(f"Trying create folder {f}. Result {res_create}")

            if 'OK' in res_create:
                logging.info(f"Success create folder {f}")
                self.logger.log(f"Успешно создана папка {f}")
                res = self.mailbox.copy(mail.uid, f)

                if 'OK' in res:
                    logging.info(f"Mail {mail.uid} successfully copied to folder {f}")
                    self.logger.log(f"Сообщение {mail.uid} успешно скопировано в папку {f}")
                else:
                    logging.error(f"Error copying mail {mail.uid} to folder {f}: {str(res[1])}")
                    self.logger.log(f"Сообщение {mail.uid} не получилось скопировать в папку {f}. Ошибка {str(res[1])}")
            else:
                logging.error(f"Error creating folder {f}: {str(res_create[1])}")
                self.logger.log(f"Не получилось создать папку {f}. Ошибка {str(res_create[1])}")
        return res

    def set_done(self, is_done):
        self.done = is_done
        print(f'set done {is_done}\n')
        if self.done:
            logging.info("Stopping")
            self.logger.log("Завершение...")

    def check_updates(self):
        self.set_done(False)

        while not self.done:
            connection_start_time = time.monotonic()
            connection_live_time = 0.0
            try:
                date = dateparser.parse(time.asctime()).strftime("%d.%m.%Y %H:%M:%S")

                logging.info(f"Начато отслеживание {date}")
                self.logger.log(f"Начато отслеживание {date}")
                # was_log = False
                while not self.done and connection_live_time < 29 * 60:

                    try:
                        responses = self.mailbox.idle.wait(timeout=20)
                        if self.done:
                            print('self.stop')
                            return

                        date = dateparser.parse(time.asctime()).strftime("%d.%m.%Y %H:%M:%S")
                        logging.info(f"{date} IDLE responses: {responses}")
                        # self.logger.log(f"{time.asctime()} IDLE responses: {responses}")
                        if responses:
                            # was_log = False
                            for msg in self.mailbox.fetch(A(seen=False)):
                                date = dateparser.parse(str(msg.date)).strftime("%d.%m.%Y %H:%M:%S")

                                logging.info(f"-> {str(msg.date)} {msg.subject}")
                                self.logger.log(f"--> Новое сообщение {msg.uid}: {date} Тема: {msg.subject}")
                                mail = Mail(msg)
                                category = self.classify_mail(mail)
                                self.copy_to_folder(mail, category)
                        else:
                            # if not was_log:
                            self.logger.log('Нет новых сообщений...')
                            # was_log = True

                    except KeyboardInterrupt:
                        logging.warning('~KeyboardInterrupt')
                        self.done = True
                        break
                    connection_live_time = time.monotonic() - connection_start_time
            except (TimeoutError, ConnectionError,
                    imaplib.IMAP4.abort, MailboxLoginError, MailboxLogoutError,
                    socket.herror, socket.gaierror, socket.timeout) as e:
                logging.error(f'## Error {e}. {traceback.format_exc()}. reconnect in a minute...')
                self.logger.log(f'## Ошибка {e}. Переподключение через минуту...')
                time.sleep(60)
        # self.logger.log("Завершено")
        print('done updates')

    def logout(self):
        self.done = True
        logging.info("Logout")
        return self.mailbox.logout()

    def stop(self):
        self.set_done(True)
