from typing import Any
from customtkinter import *
from service import *
from CTkMessagebox import CTkMessagebox
import configparser
from sentence_embeddings import *

text_color = "#d9edff"
bg_color = "#1d1e1e"
fg_color_red = "#854442"


class App(CTk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.geometry("500x400")
        set_appearance_mode("dark")
        self.title("Классификация почты")
        self.configure(bg='lightblue')
        self.mail_service: MailService = None

        container = CTkFrame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.show_auth_frame(container)

    def set_mail_service(self, mail_service):
        self.mail_service = mail_service

    def show_auth_frame(self, container):
        frame = AuthFrame(parent=container, controller=self)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()

    def show_settings_frame(self, container):
        if self.mail_service is not None:
            frame = SettingsFrame(parent=container, controller=self,
                                  mail_service=self.mail_service)
            frame.grid(row=0, column=0, sticky="nsew")
            frame.tkraise()

    def show_test_frame(self, container):
        frame = TestFrame(master=container, controller=self)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()

    def show_last_msg_page(self, container):
        frame = LastMessageFrame(master=container, controller=self, mail_service=self.mail_service)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()

    def show_sort_folder_page(self, container):
        frame = SortFolderPage(master=container, controller=self, mail_service=self.mail_service)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()

    def show_statistic_page(self, container):
        frame = Statistic(master=container, controller=self, mail_service=self.mail_service)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()

    def logout(self, container):
        self.show_auth_frame(container)
        self.mail_service.logout()


class AuthFrame(CTkFrame):
    def __init__(self, parent: Any, controller, **kwargs):
        super().__init__(parent, **kwargs)
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
        mail_service = MailService(service, login, password)
        res = mail_service.auth()
        if res[0] != 'OK':
            CTkMessagebox(title="Не удалось войти", message=res[1],
                          icon="warning", option_1="Retry")
        else:
            if self.checkbox.get() == 1:
                self.save_user_data(login, password, True)

            # with open('config.ini', 'w') as configfile:
            #     config.write(configfile)
            controller.set_mail_service(mail_service)
            controller.show_settings_frame(parent)


class SettingsFrame(CTkFrame):
    def __init__(self, parent: Any, controller, mail_service: MailService, **kwargs):
        super().__init__(parent, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        CTkButton(master=self,
                  text="Статистика",
                  command=lambda: controller.show_statistic_page(parent),
                  corner_radius=32,
                  font=('Arial', 16)).grid(row=0, column=0, padx=10, pady=10, sticky='w')

        CTkButton(master=self,
                  text="Классифицировать последнее сообщение",
                  command=lambda: controller.show_last_msg_page(parent),
                  corner_radius=32,
                  font=('Arial', 16)).grid(row=1, column=0, padx=10, pady=10, sticky='w')

        CTkButton(master=self,
                  text="Классифицировать письма за сегодня",
                  command=lambda: controller.show_sort_page(parent),
                  corner_radius=32,
                  font=('Arial', 16)).grid(row=2, column=0, padx=10, pady=10, sticky='w')

        CTkButton(master=self,
                  text="Классифицировать новые письма",
                  command=lambda: controller.show_sort_page(parent),
                  corner_radius=32,
                  font=('Arial', 16)).grid(row=3, column=0, padx=10, pady=10, sticky='w')

        CTkButton(master=self,
                  text="Классифицировать письма в папке",
                  command=lambda: controller.show_sort_folder_page(parent),
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
        res = predict(text)
        res = res.split(sep='\n')[0]
        self.lbl.configure(text=res)


class LastMessageFrame(CTkFrame):
    def __init__(self, master: Any, controller, mail_service: MailService, **kwargs):
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

        self.lbl = CTkLabel(self, text="", text_color=text_color, font=('Arial', 16))
        self.lbl.configure(justify='left')
        self.lbl.grid(row=2, column=1, padx=10, pady=10, sticky='w')
        CTkButton(master=self,
                  text="Копировать в предложенную папку",
                  command=lambda: self.copy_to_folder(mail_service, mail),
                  corner_radius=32,
                  font=('Arial', 14)).grid(row=3, column=0, padx=10, pady=10,
                                           sticky='w', columnspan=2)

        CTkButton(master=self,
                  text="Назад",
                  command=lambda: controller.show_settings_frame(container=master),
                  corner_radius=32,
                  font=('Arial', 10)).grid(row=5, column=0, padx=10, pady=10, sticky='w')

    def test_category(self, mail: Mail):
        text = mail.to_str()
        res = predict(text)
        res = res.split(sep='\n')[0]
        categ = res.split(sep=':')[0].strip()
        self.lbl.configure(text=categ)
        return categ

    def copy_to_folder(self, mail_service, mail):
        folder_str = self.test_category(mail)
        res = mail_service.copy_to_folder(mail, folder_str)
        if res[0] != 'OK':
            CTkMessagebox(title="Ошибка!", message=res[1],
                          icon="warning", option_1="Повторить")
        else:
            CTkMessagebox(title="Успешно!", message=res[1],
                          icon="check", option_1="Ок")


class Statistic(CTkFrame):
    def __init__(self, master: Any, controller, mail_service: MailService, **kwargs):
        super().__init__(master, **kwargs)
        CTkLabel(self, text="Статистика", text_color=text_color, font=('Arial', 16)).grid(row=0, columnspan=2)
        CTkLabel(self, text="Категоризированных писем: 15", text_color=text_color, font=('Arial', 16)).grid(row=1, columnspan=2)
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
    def __init__(self, master: Any, controller, mail_service: MailService, **kwargs):
        super().__init__(master, **kwargs)
        (CTkLabel(self, text="Выберите папку", text_color=text_color, font=('Arial', 16))
         .grid(row=0, column=0, padx=10, pady=10))
        self.mail_service = mail_service
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
        size = self.mail_service.get_folder_size(choice)
        self.lbl.configure(text=f"Размер папки: {size} сообщений")

    def sort(self, folder):
        mails = self.mail_service.get_all_folder_emails(folder)
        i = 0
        for m in mails:
            i = i + 1
            if i<10:
                c = predict(m.to_str())
                res = self.mail_service.copy_to_folder(m, c, initial_folder=folder)
                if res[0] != 'OK':
                    CTkMessagebox(title="Ошибка!", message=res[1],
                                  icon="warning", option_1="Повторить")
                    return
        CTkMessagebox(title="Успешно!",
                      icon="check", option_1="Ок")

    def copy_to_folder(self, mail_service, mail):
        folder_str = self.test_category(mail)
        res = mail_service.copy_to_folder(mail, folder_str)
        if res[0] != 'OK':
            CTkMessagebox(title="Ошибка!", message=res[1],
                          icon="warning", option_1="Повторить")
        else:
            CTkMessagebox(title="Успешно!", message=res[1],
                          icon="check", option_1="Ок")


class SortNewMails(CTkFrame):
    def __init__(self, master: Any, controller, mail_service: MailService, **kwargs):
        super().__init__(master, **kwargs)
        (CTkLabel(self, text="Новые письма (непрочитанные): ", text_color=text_color, font=('Arial', 16))
         .grid(row=0, column=0, padx=10, pady=10))
        self.mail_service = mail_service
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


app = App()
app.mainloop()
