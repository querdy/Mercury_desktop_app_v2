from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QGridLayout, QWidget
from sqlalchemy.orm import Session

from app.database.crud.user import get_user
from app.signals import MainSignals
from app.window.research_adder import ResearchAdder
from app.window.research_settings import ResearchSettings
from app.window.service import Service


class MainWindow(QMainWindow):
    def __init__(self, db_session: Session, parent=None):
        super().__init__(parent)
        self.db_session = db_session
        # self.setFixedSize(1280, 720)
        self.setWindowIcon(QIcon('favicon.ico'))
        self.status_bar = self.statusBar()
        self.signals = MainSignals()
        self.change_window_title()

        self.research_settings = ResearchSettings(
            self.status_bar, db_session=self.db_session, signals=self.signals,
            parent=self
        )
        self.research_adder = ResearchAdder(
            self.statusBar(), db_session=self.db_session, signals=self.signals,
            parent=self
        )
        self.service = Service(self.statusBar(), db_session=self.db_session, parent=self)

        tab_widget = QTabWidget()
        tab_widget.addTab(self.research_adder, "Внесение")
        tab_widget.addTab(self.research_settings, "Редактирование")
        tab_widget.addTab(self.service, "Сервис")

        main_widget = QWidget()
        main_layout = QGridLayout()
        main_layout.addWidget(tab_widget, 0, 0, 5, 1)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.signals.enterprise_changed.emit()

    def change_window_title(self):
        base_window_title = "Veterinary events adder"
        version = "v1.0"
        self.setWindowTitle(f"{base_window_title} {version}")
        user = get_user(self.db_session)
        if user is None:
            self.setWindowTitle(f"{base_window_title} {version}: пользователь не указан")
        else:
            self.setWindowTitle(f"{base_window_title} {version}: [{user.login}]")
