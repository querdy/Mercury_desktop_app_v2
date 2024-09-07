from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QTabWidget
from loguru import logger

from app.database.repositories.manager import RepositoryManager
from app.gui.edit_research_and_immunization_tab import EditResearchAndImmunizationTab
from app.gui.events_adder_tab import EventsAdderTab
from app.gui.service_tab import ServiceTab
from app.gui.signals import MainWindowSignals
from app.settings import settings


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(settings.APPLICATION_TITLE)
        self.setMinimumSize(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        self.setWindowIcon(QIcon(settings.ICON))
        # self.setGeometry(100, 100, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)

        self.events_adder = EventsAdderTab()
        self.research_and_immunization_settings = EditResearchAndImmunizationTab()
        self.service = ServiceTab()

        tab_widget = QTabWidget()
        tab_widget.addTab(self.events_adder, "Внесение")
        tab_widget.addTab(self.research_and_immunization_settings, "Редактирование")
        tab_widget.addTab(self.service, "Сервис")

        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(tab_widget)
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.change_window_title()
        MainWindowSignals().change_title.connect(self.change_window_title)

    def change_window_title(self):
        try:
            self.setWindowTitle(f"{settings.APPLICATION_TITLE} {settings.VERSION}")
            with RepositoryManager() as repo:
                user = repo.vetis_user.receive()
            if user is None:
                self.setWindowTitle(f"{settings.APPLICATION_TITLE} {settings.VERSION}: пользователь не указан")
            else:
                self.setWindowTitle(f"{settings.APPLICATION_TITLE} {settings.VERSION}: [{user.login}]")
        except Exception as e:
            logger.error(f"{type(e)} {e}")
