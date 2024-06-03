from typing import Any
from customtkinter import *
from service import *
from CTkMessagebox import CTkMessagebox
import configparser
from sentence_embeddings import *

text_color = "#d9edff"
bg_color = "#1d1e1e"


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


class AuthFrame(CTkFrame):
    def __init__(self, parent: Any, controller, **kwargs):
        super().__init__(parent, **kwargs)
        welcome_label = CTkLabel(master=self, text="Добро пожаловать!",
                                 font=("Arial", 20), text_color=text_color)

        select_service_lbl = CTkLabel(master=self, text="Выберите почтовый сервис:",
                                      font=("Arial", 16), text_color=text_color)
        services = ["cs.vsu.ru", "Mail.ru", "Gmail", "Inbox", "Outlook"]
        self.service_dropdown = CTkComboBox(master=self, values=services)
        config = configparser.ConfigParser()  # создаём объекта парсера
        config.read("config.ini")  # читаем конфиг

        login_label = CTkLabel(self, text="Введите логин:", text_color=text_color, font=('Arial', 16))

        self.login_entry = CTkEntry(self)

        password_label = CTkLabel(self, text="Введите пароль:", text_color=text_color, font=('Arial', 16))

        self.password_entry = CTkEntry(self, show="*")

        passw = config['DEFAULT']["password"]
        if passw.strip() != '':
            self.password_entry.insert(END, passw)
        user = config['DEFAULT']["username"]
        if user.strip() != '':
            self.login_entry.insert(END, user)

        submit_button = CTkButton(master=self,
                                  text="Войти",
                                  command=lambda: self.submit(parent=parent, controller=controller),
                                  corner_radius=32,
                                  font=('Arial', 16))

        welcome_label.pack(anchor="s", expand=True, pady=5, padx=30)
        select_service_lbl.pack(anchor="s", expand=True, pady=5, padx=30)
        self.service_dropdown.pack(anchor="s", expand=True, pady=5, padx=30)
        login_label.pack(anchor="s", expand=True, pady=5, padx=30)
        self.login_entry.pack(anchor="s", expand=True, pady=5, padx=30)
        password_label.pack(anchor="s", expand=True, pady=5, padx=30)
        self.password_entry.pack(anchor="s", expand=True, pady=5, padx=30)
        submit_button.pack(anchor="n", expand=True, pady=10, padx=30)
        self.checkbox = CTkCheckBox(master=self, text="Запомнить меня")
        self.checkbox.pack(anchor="n", expand=True, pady=5, padx=30)

    def submit(self, parent, controller: App):
        service = self.service_dropdown.get()
        login = self.login_entry.get()
        password = self.password_entry.get()
        config = configparser.ConfigParser()  # создаём объекта парсера
        config.read("settings.ini")  # читаем конфиг
        mail_service = MailService(service, login, password)
        res = mail_service.auth()
        print(self.checkbox.get())
        if res[0] != 'OK':
            CTkMessagebox(title="Warning!", message=res[1],
                          icon="warning", option_1="Retry")
        else:
            if self.checkbox.get() == 1:
                config['DEFAULT']['password'] = password
                config['DEFAULT']['username'] = login
            controller.set_mail_service(mail_service)
            controller.show_settings_frame(parent)


class SettingsFrame(CTkFrame):
    def __init__(self, parent: Any, controller, mail_service: MailService, **kwargs):
        super().__init__(parent, **kwargs)

        # folders = mail_service.get_folders_list()

        # CTkLabel(self, text="Папки", text_color=text_color, font=('Arial', 16)).grid(row=1, column=0)

        # row = 2
        # for folder in folders:
        #     label_folder = CTkLabel(self, text=f"{folder}", text_color=text_color,
        #                             font=('Arial', 14), padx=4, pady=4)
        #     label_folder.grid(row=row, column=0, sticky="w", padx=4, pady=4)
        #     row += 1

        c1 = CTkButton(master=self,
                       text="Получить последнее сообщение",
                       command=lambda: controller.show_last_msg_page(parent),
                       corner_radius=32,
                       font=('Arial', 16))
        c1.grid(row=0, column=0, padx=10)
        c2 = CTkButton(master=self,
                       text="Тест",
                       command=lambda: controller.show_test_frame(parent),
                       corner_radius=32,
                       font=('Arial', 16))
        c2.grid(row=2, column=0, padx=10)


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
        CTkLabel(self, text="Последнее сообщение", text_color=text_color, font=('Arial', 16)).grid(row=0)
        mail = mail_service.get_latest_mail()
        message_lbl = CTkTextbox(self, text_color=text_color, font=('Arial', 14))
        message_lbl.insert('0.0', mail.to_str())
        message_lbl.grid(row=1, padx=5, pady=5, sticky='ew')
        message_lbl.configure(state='disabled')
        CTkButton(master=self,
                  text="Определить категорию",
                  command=lambda: self.test_category(mail),
                  corner_radius=32,
                  font=('Arial', 14)).grid(row=2, column=0, padx=10, pady=10)

        self.lbl = CTkLabel(self, text="", text_color=text_color, font=('Arial', 16))
        self.lbl.configure(justify='left')
        self.lbl.grid(row=3, column=0, padx=10, pady=10, sticky='ew')
        CTkButton(master=self,
                  text="Копировать в предложенную папку",
                  command=lambda: self.copy_to_folder(mail_service, mail),
                  corner_radius=32,
                  font=('Arial', 14)).grid(row=4, column=0, padx=10, pady=10)

        CTkButton(master=self,
                  text="Назад",
                  command=lambda: controller.show_settings_frame(container=master),
                  corner_radius=32,
                  font=('Arial', 10)).grid(row=5, sticky='s')

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
                          icon="warning", option_1="Retry")
        else:
            CTkMessagebox(title="Успешно!", message=res[1],
                          icon="warning", option_1="Ок")



class MailClassification(CTkFrame):
    def __init__(self, master: Any, controller, **kwargs):
        super().__init__(master, **kwargs)


def start():
    app = App()
    app.mainloop()


app = App()
app.mainloop()
