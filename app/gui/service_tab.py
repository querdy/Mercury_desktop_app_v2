from PyQt6.QtCore import QThreadPool
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from loguru import logger

from app.database.repositories.manager import RepositoryManager
from app.gui.signals import MainWindowSignals
from app.gui.widgets.mercury_web_login_widget import MercuryWebLoginWidget
from app.gui.widgets.text_info_widget import TextInfoWindow
from app.schema.vetis_user import VetisUserCreateSchema
from app.threads import FWorker
from app.vetis.mercury import Mercury


class ServiceTab(QWidget):
    def __init__(self):
        super().__init__()

        self.mercury_web_login = MercuryWebLoginWidget()
        self.text_info_window = TextInfoWindow()

        layout = QVBoxLayout()
        layout.addWidget(self.mercury_web_login)
        layout.addWidget(self.text_info_window)

        self.setLayout(layout)

        self.mercury_web_login.button.clicked.connect(self.check_and_save_button_clicked)

    def check_and_save(self):
        login = self.mercury_web_login.login_input.text().strip()
        self.mercury_web_login.login_input.setText("")
        password = self.mercury_web_login.password_input.text().strip()
        self.mercury_web_login.password_input.setText("")
        try:
            if Mercury(login=login, password=password, clean=True).is_auth:
                with RepositoryManager() as repo:
                    repo.vetis_user.create(VetisUserCreateSchema(login=login, password=password))
                MainWindowSignals().change_title.emit()
        except Exception as e:
            logger.error(f"{type(e)} {e}")

    def check_and_save_button_clicked(self):
        self.mercury_web_login.button.setEnabled(False)
        worker = FWorker(self.check_and_save)
        worker.signals.finished.connect(lambda: self.mercury_web_login.button.setEnabled(True))
        worker.signals.finished.connect(lambda: self.text_info_window.remove_logger())
        self.text_info_window.add_logger()
        QThreadPool().globalInstance().start(worker)
