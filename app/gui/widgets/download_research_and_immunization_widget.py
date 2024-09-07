from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QPushButton, QLineEdit, QLabel, QHBoxLayout, QVBoxLayout, QWidget


class DownloadResearchAndImmunizationDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Загрузить исследования и иммунизации")
        self.setFixedSize(250, 100)

        self.transaction_pk_label = QLabel("Номер транзакции:")
        self.traffic_pk_label = QLabel("Номер записи журнала:")
        self.transaction_pk_input = QLineEdit()
        self.traffic_pk_input = QLineEdit()

        label_width = max(self.transaction_pk_label.sizeHint().width(), self.traffic_pk_label.sizeHint().width())
        self.transaction_pk_label.setFixedWidth(label_width)
        self.traffic_pk_label.setFixedWidth(label_width)

        self.transaction_pk_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.traffic_pk_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.download_button = QPushButton("Загрузить")
        self.cancel_button = QPushButton("Отмена")

        self.download_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.reject)

        transaction_layout = QHBoxLayout()
        transaction_layout.addWidget(self.transaction_pk_label)
        transaction_layout.addWidget(self.transaction_pk_input)

        traffic_pk_layout = QHBoxLayout()
        traffic_pk_layout.addWidget(self.traffic_pk_label)
        traffic_pk_layout.addWidget(self.traffic_pk_input)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.download_button)
        button_layout.addWidget(self.cancel_button)

        layout = QVBoxLayout()
        layout.addLayout(transaction_layout)
        layout.addLayout(traffic_pk_layout)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.transaction_pk_input.textChanged.connect(self.check_multiple_input)
        self.traffic_pk_input.textChanged.connect(self.check_multiple_input)

    def check_multiple_input(self):
        transaction_pk = self.transaction_pk_input.text()
        traffic_pk = self.traffic_pk_input.text()
        if transaction_pk and traffic_pk:
            self.download_button.setEnabled(False)
        else:
            self.download_button.setEnabled(bool(transaction_pk or traffic_pk))


class DownloadResearchAndImmunizationWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.download_button = QPushButton("Загр. иссл. и иммун.")
        self.download_button.clicked.connect(self.open_dialog)

        self.dialog = DownloadResearchAndImmunizationDialog()

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.download_button)
        self.setLayout(layout)

    def open_dialog(self):
        self.dialog.exec()
