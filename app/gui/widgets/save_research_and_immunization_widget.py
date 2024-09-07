from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QPushButton, QHBoxLayout

from app.gui.signals import SaveResearchAndImmunizationButtonSignals


class SaveResearchAndImmunizationWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.button = QPushButton("Сохранить")
        self.button.setFixedWidth(100)
        self.button.clicked.connect(self.save_button_clicked)

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.button)
        self.setLayout(layout)

    @staticmethod
    def save_button_clicked():
        SaveResearchAndImmunizationButtonSignals().btn_clicked.emit()
