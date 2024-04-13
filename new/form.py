from typing import Any

from customtkinter import *

from new import main

text_color = "#d9edff"


class App(CTk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.geometry("500x400")
        set_appearance_mode("dark")
        self.title("Выбор почтового сервиса")
        self.configure(bg='lightblue')
        container = CTkFrame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}

        for F in (AuthFrame, SettingsFrame):
            frame = F(container, self)

            # initializing frame of that object from
            # startpage, page1, page2 respectively with
            # for loop
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(AuthFrame)

    def show_frame(self, cont):
        frame = self.frames[cont]
        # frame.pack()
        frame.tkraise()


class AuthFrame(CTkFrame):
    def __init__(self, master: Any, controller,  **kwargs):
        super().__init__(master, **kwargs)
        welcome_label = CTkLabel(master=self, text="Добро пожаловать!",
                                 font=("Arial", 20), text_color=text_color)

        select_service_lbl = CTkLabel(master=self, text="Выберите почтовый сервис:",
                                      font=("Arial", 16), text_color=text_color)
        services = ["cs.vsu.ru", "Mail.ru", "Gmail", "Inbox", "Outlook"]
        self.service_dropdown = CTkComboBox(master=self, values=services)

        login_label = CTkLabel(self, text="Введите логин:", text_color=text_color, font=('Arial', 16))

        self.login_entry = CTkEntry(self)

        password_label = CTkLabel(self, text="Введите пароль:", text_color=text_color, font=('Arial', 16))

        self.password_entry = CTkEntry(self, show="*")

        submit_button = CTkButton(master=self,
                                  text="Войти",
                                  command=lambda: self.submit(controller),
                                  corner_radius=32,
                                  font=('Arial', 16))

        welcome_label.pack(anchor="s", expand=True, pady=10, padx=30)
        select_service_lbl.pack(anchor="s", expand=True, pady=10, padx=30)
        self.service_dropdown.pack(anchor="s", expand=True, pady=10, padx=30)
        login_label.pack(anchor="s", expand=True, pady=10, padx=30)
        self.login_entry.pack(anchor="s", expand=True, pady=10, padx=30)
        password_label.pack(anchor="s", expand=True, pady=10, padx=30)
        self.password_entry.pack(anchor="s", expand=True, pady=10, padx=30)
        submit_button.pack(anchor="n", expand=True, pady=20, padx=30)

    def submit(self, controller):
        service = self.service_dropdown.get()
        login = self.login_entry.get()
        password = self.password_entry.get()
        mail_service = main.MailService(service, login, password)
        res = mail_service.auth()
        print(res)
        controller.show_frame(SettingsFrame)
        # settings_frame = SettingsFrame(self, controller)
        # settings_frame.pack()
        # settings_frame.tkraise()
        # if res[0] == "OK":
        #     controller.show_frame(SettingsFrame)


class SettingsFrame(CTkFrame):
    def __init__(self, master: Any, controller,  **kwargs):
        super().__init__(master, **kwargs)

        # Создание кнопки добавления новой папки
        self.add_folder_button = CTkButton(self, text="Добавить новую папку", command=self.add_new_folder)
        self.add_folder_button.pack()

    def add_new_folder(self):
        # Создание нового окна для добавления новой папки
        new_folder_window = CTkToplevel(self)
        new_folder_window.title("Новая папка")

        # Поле для ввода получателя
        recipient_label = CTkLabel(new_folder_window, text="Получатель:")
        recipient_label.pack()
        recipient_entry = CTkEntry(new_folder_window)
        recipient_entry.pack()

        # Кнопка сохранить
        save_button = CTkButton(new_folder_window, text="Сохранить")
        save_button.pack()


app = App()
app.mainloop()
