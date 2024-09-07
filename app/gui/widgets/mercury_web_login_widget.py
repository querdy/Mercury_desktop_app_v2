from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLineEdit, QLabel, QPushButton


class MercuryWebLoginWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        login_layout = QHBoxLayout()
        login_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        password_layout = QHBoxLayout()
        password_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        group_box = QGroupBox("Настройки доступа")
        group_layout = QVBoxLayout()

        self.login_label = QLabel("Логин пользователя:")
        self.login_input = QLineEdit()
        self.login_input.setMaximumWidth(250)

        self.password_label = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setMaximumWidth(250)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        label_width = max(self.login_label.sizeHint().width(), self.password_label.sizeHint().width())
        self.login_label.setFixedWidth(label_width)
        self.password_label.setFixedWidth(label_width)

        login_layout.addWidget(self.login_label)
        login_layout.addWidget(self.login_input)
        password_layout.addWidget(self.password_label)
        password_layout.addWidget(self.password_input)

        self.button = QPushButton("Проверить и сохранить")
        self.button.setFixedWidth(self.button.sizeHint().width())
        self.password_input.returnPressed.connect(self.button.click)

        group_layout.addLayout(login_layout)
        group_layout.addLayout(password_layout)
        group_layout.addWidget(self.button)

        group_box.setLayout(group_layout)
        layout.addWidget(group_box)
        self.setLayout(layout)
