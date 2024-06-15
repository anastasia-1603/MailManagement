from tkinter import messagebox
from typing import Any
from customtkinter import *
from service import *
from CTkMessagebox import CTkMessagebox
import configparser
import logger
from PIL import Image, ImageTk
import threading

text_color = "#d9edff"
bg_color = "#1d1e1e"
fg_color_red = "#854442"

mail_service: MailService = None
categories = ["Вопросы", "Готово к публикации",
              "Доработка", "Другое", "Отклонена",
              "Подача статьи", "Проверка статьи", "Рецензирование"]


def set_mail_service(mailservice):
    global mail_service
    mail_service = mailservice


def on_destroy():
    print('outer destroy')


def copy_to_folder(mail, folder):
    if folder != 'Нет категории':
        res = mail_service.copy_to_folder(mail, folder)
        if 'OK' in res:
            CTkMessagebox(width=200, height=100, title="Успешно", icon="check",
                          message="Успешно скопировано", option_1="Ок")
        else:
            CTkMessagebox(width=200, height=100, title="Ошибка", message=res,
                          icon="warning", option_1="Повторить")


class App(CTk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.log = logger.Logger(None)
        self.geometry("500x400")
        set_appearance_mode("dark")
        self.title("Классификация почты")
        self.configure(bg='lightblue')

        self.container = CTkFrame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        self.show_auth_frame(self.container)

    def show_auth_frame(self, container):

        frame = AuthFrame(parent=container, controller=self, log=self.log)
        self.frames[AuthFrame] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()

    def show_settings_frame(self, container):
        if mail_service is not None:
            mail_service.set_done(True)
            frame = SettingsFrame(parent=container, controller=self)
            self.frames[SettingsFrame] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            frame.tkraise()

    def show_test_frame(self, container):
        frame = TestFrame(master=container, controller=self)
        self.frames[TestFrame] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()

    def show_last_msg_page(self, container):
        if mail_service is not None:
            frame = LastMessageFrame(master=container, controller=self)
            self.frames[LastMessageFrame] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            frame.tkraise()

    # def show_sort_folder_page(self, container):
    #     if mail_service is not None:
    #         frame = SortFolderPage(master=container, controller=self)
    #         frame.grid(row=0, column=0, sticky="nsew")
    #         frame.tkraise()

    def show_statistic_page(self, container):
        if mail_service is not None:
            frame = Statistic(master=container, controller=self)
            self.frames[Statistic] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            frame.tkraise()

    def show_sort_new_mails_page(self, container):
        if mail_service is not None:
            frame = SortNewMails(master=container, controller=self)
            self.frames[SortNewMails] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            frame.tkraise()

    def show_auto_classification_page(self, container):
        if mail_service is not None:
            frame = AutomaticClassification(master=container, controller=self, log=self.log)
            self.frames[AutomaticClassification] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            frame.tkraise()

    def logout(self, container):
        if mail_service is not None:
            mail_service.logout()
            self.show_auth_frame(container)

    def on_destroy_frame(self):
        print('on_destroy_frame')
        frame = self.frames.get(AutomaticClassification)
        if frame:
            frame.stop()
        for widgets in self.winfo_children():
            widgets.destroy()
        self.destroy()


class AuthFrame(CTkFrame):
    def __init__(self, parent: Any, controller, log=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.log = log
        welcome_label = CTkLabel(master=self, text="Добро пожаловать!",
                                 font=("Arial", 20), text_color=text_color)

        select_service_lbl = CTkLabel(master=self, text="Выберите почтовый сервис:",
                                      font=("Arial", 16), text_color=text_color)
        services = ["cs.vsu.ru", "Mail.ru"]

        self.service_dropdown = CTkComboBox(master=self, values=services,
                                            command=self.combobox_callback)

        self.config = configparser.ConfigParser()  # создаём объект парсера
        self.config.read("config.ini")
        choice = self.service_dropdown.get()
        remember = self.config[choice]["remember"]
        passw = self.config[choice]["password"]
        user = self.config[choice]["username"]

        login_label = CTkLabel(self, text="Введите логин:", text_color=text_color, font=('Arial', 16))
        self.login_entry = CTkEntry(self)

        password_label = CTkLabel(self, text="Введите пароль:", text_color=text_color, font=('Arial', 16))
        self.password_entry = CTkEntry(self, show="*")

        submit_button = CTkButton(master=self,
                                  text="Войти",
                                  command=lambda: self.submit(parent=parent, controller=controller),
                                  corner_radius=32,
                                  font=('Arial', 16))
        self.grid_columnconfigure(1, weight=1)
        welcome_label.grid(row=0, column=0, pady=20, padx=30, columnspan=2, sticky='ew')
        select_service_lbl.grid(row=1, column=0, pady=15, padx=10, sticky='e')
        self.service_dropdown.grid(row=1, column=1, pady=15, padx=30, sticky='w')
        login_label.grid(row=2, column=0, pady=15, padx=10, sticky='e')
        self.login_entry.grid(row=2, column=1, pady=15, padx=30, sticky='ew')
        password_label.grid(row=3, column=0, pady=15, padx=10, sticky='e')
        self.password_entry.grid(row=3, column=1, pady=15, padx=30, sticky='ew')
        submit_button.grid(row=5, column=0, pady=15, padx=10, columnspan=2)
        self.checkbox = CTkCheckBox(master=self, text="Запомнить меня")
        self.checkbox.grid(row=4, column=1, pady=15, padx=10, sticky='w')
        self.configure_fields(remember, passw, user)

    def combobox_callback(self, choice):
        remember = self.checkbox.get() == 1
        passw = ''
        user = ''
        if choice in self.config:
            remember = self.config[choice]["remember"]
            passw = self.config[choice]["password"]
            user = self.config[choice]["username"]
        self.configure_fields(remember, passw, user)

    def save_user_data(self, username, password, remember):
        choice = self.service_dropdown.get()
        if choice not in self.config:
            self.config[choice] = {}
        self.config[choice]["username"] = username
        self.config[choice]["password"] = password
        self.config[choice]["remember"] = str(remember)

        # with open("config.ini", "w") as configfile:
        #     self.config.write(configfile)

    # def clear_user_data(self):
    #     choice = self.service_dropdown.get()
    #     if choice in self.config:
    #         del self.config[choice]
    #
    #     with open("config.ini", "w") as configfile:
    #         self.config.write(configfile)

    def configure_fields(self, remember, passw, user):
        if remember == "True":
            self.checkbox.select()
            if passw.strip() != '':
                self.password_entry.delete(0, END)
                self.password_entry.insert(0, passw)

            if user.strip() != '':
                self.login_entry.delete(0, END)
                self.login_entry.insert(0, user)
        else:
            self.checkbox.deselect()
            self.password_entry.delete(0, END)
            self.login_entry.delete(0, END)

    def submit(self, parent, controller: App):
        service = self.service_dropdown.get()
        login = self.login_entry.get()
        password = self.password_entry.get()

        config = configparser.ConfigParser()  # создаём объекта парсера
        config.read("settings.ini")  # читаем конфиг
        set_mail_service(MailService(service, login, password, self.log))
        res = mail_service.auth()
        if res[0] != 'OK':
            CTkMessagebox(title="Не удалось войти", message=res[1],
                          icon="warning", option_1="Retry")
        else:
            if self.checkbox.get() == 1:
                self.save_user_data(login, password, True)

            # with open('config.ini', 'w') as configfile:
            #     config.write(configfile)
            # controller.set_mail_service(mail_service)
            controller.show_settings_frame(parent)


class SettingsFrame(CTkFrame):
    def __init__(self, parent: Any, controller, **kwargs):
        super().__init__(parent, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        # CTkButton(master=self,
        #           text="Статистика",
        #           command=lambda: controller.show_statistic_page(parent),
        #           corner_radius=32,
        #           font=('Arial', 16)).grid(row=0, column=0, padx=10, pady=10, sticky='w')

        CTkButton(master=self,
                  text="Классифицировать последнее сообщение",
                  command=lambda: controller.show_last_msg_page(parent),
                  corner_radius=32,
                  font=('Arial', 16)).grid(row=1, column=0, padx=10, pady=10, sticky='w')

        # CTkButton(master=self,
        #           text="Классифицировать письма за сегодня",
        #           command=lambda: controller.show_day_sort_page(parent),
        #           corner_radius=32,
        #           font=('Arial', 16)).grid(row=2, column=0, padx=10, pady=10, sticky='w')

        CTkButton(master=self,
                  text="Классифицировать несколько писем",
                  command=lambda: controller.show_sort_new_mails_page(parent),
                  corner_radius=32,
                  font=('Arial', 16)).grid(row=3, column=0, padx=10, pady=10, sticky='w')

        CTkButton(master=self,
                  text="Автоматическая классификация",
                  command=lambda: controller.show_auto_classification_page(parent),
                  corner_radius=32,
                  font=('Arial', 16)).grid(row=4, column=0, padx=10, pady=10, sticky='w')

        CTkButton(master=self,
                  text="Классифицировать тестовое сообщение",
                  command=lambda: controller.show_test_frame(parent),
                  corner_radius=32,
                  font=('Arial', 16)).grid(row=5, column=0, padx=10, pady=10, sticky='w')

        CTkButton(master=self,
                  text="Выйти",
                  fg_color=fg_color_red,
                  command=lambda: controller.logout(parent),
                  corner_radius=32,
                  font=('Arial', 16)).grid(row=6, column=0, padx=10, pady=10, sticky='w')


class TestFrame(CTkFrame):
    def __init__(self, master: Any, controller, **kwargs):
        super().__init__(master, **kwargs)

        # self.grid_rowconfigure(0, weight=1)  # Растягиваем строку 0
        self.grid_columnconfigure(0, weight=1)  # Растягиваем столбец 0
        # CTkLabel(self, text="Тест", text_color=text_color, font=('Arial', 16)).grid(row=0)
        t = CTkTextbox(self, corner_radius=10)
        t.grid(row=0, padx=10, column=0, pady=10, sticky='ew')
        CTkButton(master=self,
                  text="Определить категорию",
                  command=lambda: self.test_category(t.get('0.0', 'end')),
                  corner_radius=32,
                  font=('Arial', 14)).grid(row=1, column=0, padx=10, pady=10)
        self.lbl = CTkLabel(self, text="", text_color=text_color, font=('Arial', 16))
        self.lbl.configure(justify='left')
        self.lbl.grid(row=2, column=0, padx=10, pady=10, sticky='ew')
        CTkButton(master=self,
                  text="Назад",
                  command=lambda: controller.show_settings_frame(container=master),
                  corner_radius=32,
                  font=('Arial', 10)).grid(row=3, sticky='s')

    def test_category(self, text):
        res = predict_category(text)
        lbl_text = f'{res[0]} : {res[1]}'
        self.lbl.configure(text=lbl_text)


class LastMessageFrame(CTkFrame):
    def __init__(self, master: Any, controller, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        (CTkLabel(self, text="Последнее сообщение", text_color=text_color, font=('Arial', 16))
         .grid(row=0, column=0, columnspan=2))
        mail = mail_service.get_latest_mail()
        message_lbl = CTkTextbox(self, text_color=text_color, font=('Arial', 14))
        message_lbl.insert('0.0', mail.to_str())
        message_lbl.grid(row=1, padx=5, pady=5, sticky='ew', columnspan=2)
        message_lbl.configure(state='disabled')
        (CTkButton(master=self,
                   text="Определить категорию",
                   command=lambda: self.test_category(mail),
                   corner_radius=32,
                   font=('Arial', 14))
         .grid(row=2, column=0, padx=10, pady=10, sticky='w'))

        self.combobox = CTkComboBox(self, values=categories)

        # self.lbl = CTkLabel(self, text="", text_color=text_color, font=('Arial', 16))
        # self.lbl.configure(justify='left')
        # self.lbl.grid(row=2, column=1, padx=10, pady=10, sticky='w')
        CTkButton(master=self,
                  text="Копировать в предложенную папку",
                  command=lambda: copy_to_folder(mail, self.combobox.get()),
                  corner_radius=32,
                  font=('Arial', 14)).grid(row=3, column=0, padx=10, pady=10,
                                           sticky='w', columnspan=2)

        CTkButton(master=self,
                  text="Назад",
                  command=lambda: controller.show_settings_frame(container=master),
                  corner_radius=32,
                  font=('Arial', 14)).grid(row=5, column=0, padx=10, pady=10, sticky='w')

    def test_category(self, mail: Mail):
        categ = mail_service.classify_mail(mail)
        self.combobox.set(categ)
        self.combobox.grid(row=2, column=1, padx=10, pady=10, sticky='ew')
        # self.lbl.configure(text=categ)
        return categ


class Statistic(CTkFrame):
    def __init__(self, master: Any, controller, **kwargs):
        super().__init__(master, **kwargs)
        CTkLabel(self, text="Статистика", text_color=text_color, font=('Arial', 16)).grid(row=0, columnspan=2)
        CTkLabel(self, text="Категоризированных писем: 15", text_color=text_color, font=('Arial', 16)).grid(row=1,
                                                                                                            columnspan=2)
        CTkLabel(self, text="Не распределено: 10", text_color=text_color, font=('Arial', 16)).grid(row=2, columnspan=2)
        folders = mail_service.get_folders_list()
        folders_names = ["Вопросы", "Готово к публикации",
                         "Доработка", "Другое", "Отклонена",
                         "Подача статьи", "Проверка статьи", "Рецензирование"]
        row = 3
        for folder_name in folders_names:
            size = 0
            if folder_name in folders:
                size = mail_service.get_folder_size(folder_name)

            label_folder = CTkLabel(self, text=f"{folder_name} - {size} писем", text_color=text_color,
                                    font=('Arial', 14), padx=4, pady=4)
            label_folder.grid(row=row, column=0, sticky="w", padx=4, pady=4)
            # CTkButton(master=self,
            #           text="Посмотреть",
            #           command=lambda: self.check(mail_service, mail),
            #           corner_radius=32,
            #           font=('Arial', 14)).grid(row=3, column=0, padx=10, pady=10,
            #                                    sticky='w', columnspan=2)
            row += 1


class SortFolderPage(CTkFrame):
    def __init__(self, master: Any, controller, **kwargs):
        super().__init__(master, **kwargs)
        (CTkLabel(self, text="Выберите папку", text_color=text_color, font=('Arial', 16))
         .grid(row=0, column=0, padx=10, pady=10))

        existing = mail_service.get_raw_folders_list()
        combobox = CTkComboBox(master=self, values=existing)
        combobox.grid(row=0, column=1, padx=10, pady=10)
        self.lbl = CTkLabel(self, text_color=text_color, font=('Arial', 16))
        combobox.configure(command=self.update_size)
        self.lbl.grid(row=1, column=0, padx=10, pady=10)
        self.update_size(combobox.get())

        (CTkButton(master=self,
                   text="Рассортировать по папкам",
                   command=lambda: self.sort(combobox.get()),
                   corner_radius=32,
                   font=('Arial', 14))
         .grid(row=2, column=0, padx=10, pady=10, sticky='w'))

    def update_size(self, choice):
        size = mail_service.get_folder_size(choice)
        self.lbl.configure(text=f"Размер папки: {size} сообщений")

    def sort(self, folder):
        mails = mail_service.get_all_folder_emails(folder)
        i = 0
        for m in mails:
            i = i + 1
            if i < 10:
                c = predict(m.to_str())
                res = mail_service.copy_to_folder(m, c, initial_folder=folder)
                if res[0] != 'OK':
                    CTkMessagebox(title="Ошибка!", message=res[1],
                                  icon="warning", option_1="Повторить")
                    return
        CTkMessagebox(title="Успешно!",
                      icon="check", option_1="Ок")


default_count = 10


class SortNewMails(CTkFrame):
    def __init__(self, master: Any, controller, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        (CTkLabel(self, text="Проверить несколько последних писем: ", text_color=text_color, font=('Arial', 16))
         .grid(row=0, column=0, padx=10, pady=5))
        self.count_entry = CTkEntry(self, placeholder_text=str(default_count))
        self.count_entry.insert(0, '10')
        self.count_entry.grid(row=0, column=1, padx=10, pady=5)

        CTkButton(master=self,
                  text="Обновить",
                  command=self.update_count,
                  corner_radius=32,
                  font=('Arial', 14)).grid(row=1, column=0, sticky='w', padx=10, pady=5)
        self.warning = CTkLabel(self, text="",
                                text_color=fg_color_red, font=('Arial', 12))
        self.scrollable_frame = CTkScrollableFrame(self)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_rowconfigure(index=0, weight=1)
        self.mails = []
        self.categs = []
        self.mail_categ = {}
        self.update_count()
        self.scrollable_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        # self.sort_checkbox = CTkCheckBox(self, text="Сортировать по папкам")
        # self.sort_checkbox.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        accept_button = CTkButton(master=self,
                                  text="Сортировать по папкам",
                                  command=lambda: self.accept(),
                                  corner_radius=32,
                                  font=('Arial', 14))
        accept_button.grid(row=3, column=1, padx=10, pady=10, sticky="e")

        back_button = CTkButton(master=self,
                                text="Назад",
                                command=lambda: controller.show_settings_frame(container=master),
                                corner_radius=32,
                                font=('Arial', 14))
        back_button.grid(row=3, column=0, padx=10, pady=10, sticky="w")

    def update_count(self):
        try:
            count = self.count_entry.get()
            if count == '':
                self.warning.configure(text='Введите корректное число')
                count = default_count
            count = int(count)
            limit = int(mail_service.get_folder_size())
            if count <= 0:
                self.warning.configure(text='Введите число больше 0')

            elif count > limit:
                self.warning.configure(text=f"Введите число меньше {limit}")

            else:
                self.scrollable_frame.destroy()
                self.scrollable_frame = CTkScrollableFrame(self)
                self.scrollable_frame.grid_columnconfigure(0, weight=1)
                self.scrollable_frame.grid_rowconfigure(index=0, weight=1)
                # self.scrollable_frame.grid_columnconfigure(1, weight=1)
                self.mails = mail_service.get_latest_mails(int(count))
                self.categs = [mail_service.classify_mail(m) for m in self.mails]
                self.mail_categ = dict(zip(self.mails, self.categs))
                for i, m in zip(range(count), self.mail_categ.keys()):
                    card_frame = CTkFrame(self.scrollable_frame)
                    card_frame.grid_columnconfigure(0, weight=1)
                    # card_frame.grid_columnconfigure(1, weight=1)
                    text_field = CTkTextbox(card_frame)
                    text_field.insert('0.0', m.to_str())
                    text_field.configure(state='disabled')
                    combobox = CTkComboBox(
                        card_frame,
                        values=categories)
                    # pred = predict_category(m.to_str())[0]
                    # command=lambda uid=m.uid, category=combobox.get(): self.combobox_command(uid, category)
                    # combobox.configure(command=lambda categ=combobox.get(): self.categs.insert(i, categ))
                    # todo придумать, как сделать, чтобы фиксировалось значение комбобокса
                    category = mail_service.classify_mail(m)
                    combobox.set(category)
                    # self.combobox_command(category)
                    card_frame.grid(row=i, column=0, sticky="ew", pady=5)
                    text_field.grid(row=0, column=0, sticky="ew")
                    combobox.grid(row=0, column=1, sticky="e", padx=20)
                self.scrollable_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        except ValueError:
            self.warning.configure(text='Введите корректное число')
        self.warning.grid(row=1, column=1, sticky='n')

    def combobox_command(self, choice):
        pass
        # self.mail_categ[uid] = categ

    def accept(self):
        # count = self.count_entry.get()
        # print(count)
        # print(len(self.mails))
        # copy = self.sort_checkbox.get() == 1
        for m in self.mails:
            copy_to_folder(m, self.mail_categ[m.uid])


class AutomaticClassification(CTkFrame):
    def __init__(self, master: Any, controller, log, **kwargs):
        super().__init__(master, **kwargs)
        self.log = log
        self.master = master
        self.controller = controller
        self.master = master
        self.grid_rowconfigure(index=2, weight=1)
        self.grid_columnconfigure(index=0, weight=1)
        self.isAlive = True
        lbl = CTkLabel(self, text="Автоматическая классификация", text_color=text_color, font=('Arial', 16))
        lbl.grid(row=0, column=0, columnspan=2, padx=10, pady=5)
        self.start_button = CTkButton(master=self,
                                      text="Начать классификацию",
                                      command=lambda: self.start_classification(),
                                      corner_radius=32,
                                      font=('Arial', 14))
        self.start_button.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.lbl2 = CTkLabel(self, text="Процесс не запущен", text_color=text_color, font=('Arial', 14))
        self.lbl2.grid(row=1, column=1, padx=10, pady=5, sticky='e')

        self.text_field = CTkTextbox(self)
        # self.text_field.configure(state='disabled')
        self.text_field.grid(row=2, column=0, padx=10,
                             pady=10, columnspan=2, sticky="nsew")
        self.stop_button = CTkButton(master=self,
                                     text="Остановить",
                                     command=lambda: self.stop(),
                                     corner_radius=32,
                                     font=('Arial', 14))
        self.stop_button.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        back_button = CTkButton(master=self,
                                text="Назад",
                                command=lambda: controller.show_settings_frame(container=master),
                                corner_radius=32,
                                font=('Arial', 14))
        back_button.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.log.setCallback(self.print_to_text_field)
        self.thread: threading.Thread = None
        # self.stop_ = True

    def __del__(self):
        print('del')
        self.stop()

    def back(self):
        self.controller.show_settings_frame(container=self.master)
        self.stop()

    def print_to_text_field(self, text):
        self.text_field.insert('end', f"{text}\n")
        self.text_field.update()

    def stop(self):
        if self.thread is not None:
            mail_service.stop()
            self.thread.join()
            self.thread = None
            # self.log.log("Stopped")
            self.lbl2.configure(text="Процесс остановлен")
            self.stop_button.configure(state="disabled")
            self.start_button.configure(state="normal")

    def start_classification(self):
        if self.thread is None:
            self.thread = threading.Thread(target=mail_service.check_updates)
            self.thread.start()
            print(threading.main_thread().name)
            print(self.thread.name)
            self.check_thread(self.thread)
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")

    def check_thread(self, thread):
        if thread.is_alive():
            self.lbl2.configure(text="Процесс запущен")
            # self.log.log('thread alive')
            self.after(10, lambda: self.check_thread(thread))
        else:
            self.log.log('Завершено')
            self.lbl2.configure(text="Процесс остановлен")


app = App()
app.protocol('WM_DELETE_WINDOW', app.on_destroy_frame)
app.mainloop()
