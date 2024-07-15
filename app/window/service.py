from PyQt6.QtCore import QThreadPool, Qt
from PyQt6.QtWidgets import QWidget, QStatusBar, QGridLayout, QGroupBox, QLabel, QLineEdit, QPushButton
from loguru import logger
from sqlalchemy.orm import Session

from app.database.crud.user import create_user
from app.schema.user import VetisUserSchema
from app.threads.base import Worker
from app.vetis.mercury import Mercury
from app.window.log_window import LogWindow


class Service(QWidget):
    def __init__(self, status_bar: QStatusBar, db_session: Session, parent=None):
        super().__init__(parent)

        self.status_bar = status_bar
        self.db_session = db_session
        self.parent = parent

        self.log_window = LogWindow()
        self.thread_pool = QThreadPool()

        self.init_ui()

    def init_ui(self):
        self.layout = QGridLayout()
        self.layout.setVerticalSpacing(10)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.layout)

        self.init_api_settings()
        self.init_log_window()

    def init_log_window(self):
        self.layout.addWidget(self.log_window, 1, 0, 1, 1)

    def init_api_settings(self):
        self.api_frame = QGroupBox("Настройки доступа")
        self.frame_layout = QGridLayout()

        # Логин пользователя
        self.initiator_label = QLabel("Логин пользователя:")
        self.initiator_line_edit = QLineEdit()
        self.initiator_line_edit.setMaximumWidth(500)
        self.frame_layout.addWidget(self.initiator_label, 0, 0, 1, 1)
        self.frame_layout.addWidget(self.initiator_line_edit, 0, 1, 1, 7)

        # Пароль пользователя
        self.initiator_password_label = QLabel("Пароль пользователя:")
        self.initiator_password_line_edit = QLineEdit()
        self.initiator_password_line_edit.setMaximumWidth(500)
        self.frame_layout.addWidget(self.initiator_password_label, 1, 0, 1, 1)
        self.frame_layout.addWidget(self.initiator_password_line_edit, 1, 1, 1, 7)

        # Кнопка "Сохранить"
        self.save_api_settings_button = QPushButton("Сохранить")
        self.save_api_settings_button.clicked.connect(self.save_button_clicked)
        self.frame_layout.addWidget(self.save_api_settings_button, 2, 0, 1, 1)

        self.api_frame.setLayout(self.frame_layout)
        self.layout.addWidget(self.api_frame, 0, 0, 1, 2)

    def save_button_clicked(self):
        self.save_api_settings_button.setEnabled(False)
        worker = Worker(self.try_login_and_save_auth_data)
        worker.signals.finished.connect(lambda: self.save_api_settings_button.setEnabled(True))
        worker.signals.finished.connect(lambda: self.log_window.remove_logger())
        self.thread_pool.start(worker)
        self.log_window.add_logger()

    def try_login_and_save_auth_data(self):
        login = self.initiator_line_edit.text()
        self.initiator_line_edit.setText("")
        password = self.initiator_password_line_edit.text()
        self.initiator_password_line_edit.setText("")
        try:
            if Mercury(login=login.strip(), password=password.strip()).is_auth:
                create_user(self.db_session, user=VetisUserSchema(
                    login=login,
                    password=password
                ))
                self.parent.change_window_title()
        except Exception as e:
            logger.error(f"{type(e)} {e}")
