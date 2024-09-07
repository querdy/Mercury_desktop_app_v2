from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget, QLineEdit, QLabel
from controllers.user import UserController


class UserView(QWidget):
    def __init__(self, ):
        super().__init__()
        self.controller = UserController()

        self.layout = QVBoxLayout()
        self.user_list = QListWidget()
        self.load_users_button = QPushButton("Load Users")
        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.add_user_button = QPushButton("Add User")

        self.load_users_button.clicked.connect(self.load_users)
        self.add_user_button.clicked.connect(self.add_user)

        self.controller.users_loaded.connect(self.update_user_list)  # Подключаем сигнал

        self.layout.addWidget(QLabel("Name:"))
        self.layout.addWidget(self.name_input)
        self.layout.addWidget(QLabel("Email:"))
        self.layout.addWidget(self.email_input)
        self.layout.addWidget(self.add_user_button)
        self.layout.addWidget(self.user_list)
        self.layout.addWidget(self.load_users_button)
        self.setLayout(self.layout)

    def load_users(self):
        self.controller.get_users()  # Запрашиваем пользователей

    def update_user_list(self, users):
        self.user_list.clear()
        for user in users:
            self.user_list.addItem(f"{user.name} - {user.email}")

    def add_user(self):
        name = self.name_input.text()
        email = self.email_input.text()
        if name and email:
            self.controller.add_user(name, email)
            self.load_users()  # Обновляем список пользователей
            self.name_input.clear()
            self.email_input.clear()