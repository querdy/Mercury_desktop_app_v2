from PyQt6.QtCore import pyqtSignal, QObject


class SingletonMeta(type(QObject), type):
    def __init__(cls, name, bases, dict):
        super().__init__(name, bases, dict)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class EnterpriseSignals(QObject, metaclass=SingletonMeta):
    enterprise_changed = pyqtSignal()
    enterprise_list_changed = pyqtSignal()
    delete_current_enterprise = pyqtSignal()


class SaveResearchAndImmunizationButtonSignals(QObject, metaclass=SingletonMeta):
    btn_clicked = pyqtSignal()


class MainWindowSignals(QObject, metaclass=SingletonMeta):
    change_title = pyqtSignal()
