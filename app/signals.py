from PyQt6.QtCore import QObject, pyqtSignal


class MainSignals(QObject):
    enterprise_changed = pyqtSignal()
