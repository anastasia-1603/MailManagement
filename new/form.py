from typing import Any
import tkinter as tk
from tkinter import ttk
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
        auth_frame = AuthFrame(container, self)
        auth_frame.grid(row=0, column=0, sticky="nsew")
        auth_frame.tkraise()
        # for F in (AuthFrame, SettingsFrame):
        #     frame = F(container, self)
        #
        #     # initializing frame of that object from
        #     # startpage, page1, page2 respectively with
        #     # for loop
        #     self.frames[F] = frame
        #     frame.grid(row=0, column=0, sticky="nsew")

        # self.show_frame(AuthFrame)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class AuthFrame(CTkFrame):
    def __init__(self, master: Any, controller, **kwargs):
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
        mail_pass = "7PP4ZDXqnv"
        username = "lazutkina@cs.vsu.ru"
        service = self.service_dropdown.get()
        # login = self.login_entry.get()

        login = username
        password = mail_pass
        # password = self.password_entry.get()
        mail_service = main.MailService(service, login, password)
        res = mail_service.auth()
        print(res)

        settings_frame = SettingsFrame(controller, self, mail_service)
        settings_frame.tkraise()


class SettingsFrame(CTkFrame):
    def __init__(self, master: Any, controller, mail_service, **kwargs):
        super().__init__(master, **kwargs)

        folders = mail_service.get_folders()

        folders_data = {
            "Folder1": {"messages": 10, "recipients": ["recipient1", "recipient2"]},
            "Folder2": {"messages": 5, "recipients": ["recipient3", "recipient4"]},
            "Folder3": {"messages": 8, "recipients": ["recipient5", "recipient6"]}
        }

        CTkLabel(self, text="Папки", text_color=text_color, font=('Arial', 16)).grid(row=0, column=0)

        row = 1
        for folder in folders:
            label_folder = CTkLabel(self, text=f"{folder}", text_color=text_color,
                                    font=('Arial', 14), padx=4, pady=4)
            label_folder.grid(row=row, column=0, sticky="w", padx=4, pady=4)

            # label_messages = CTkLabel(self, text=f"{data['messages']} писем",
            #                           text_color=text_color, font=('Arial', 14),
            #                           padx=4, pady=4)
            # label_messages.grid(row=row, column=1, sticky="ew", padx=4, pady=4,)
            #
            # label_recipients = CTkLabel(self, text=f"Получатели: {', '.join(data['recipients'])}",
            #                             text_color=text_color, font=('Arial', 14),
            #                             padx=4, pady=4)
            # label_recipients.grid(row=row, column=2, sticky="e", padx=4, pady=4,)

            row += 1

            # label_folder = CTkLabel(self, text=f"Folder: {folder}")
            # label_folder.pack()
            #
            # label_messages = CTkLabel(self, text=f"Messages: {data['messages']} писем")
            # label_messages.pack()
            #
            # label_recipients = CTkLabel(self, text=f"Recipients: {', '.join(data['recipients'])}")
            # label_recipients.pack()


app = App()
app.mainloop()
