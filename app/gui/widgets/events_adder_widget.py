from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, \
    QGroupBox

from app.gui.widgets.edit_enterprise_widget import EnterpriseComboBox


class EventsAdderWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        group_box = QGroupBox("Внесение ветеринарных мероприятий")
        group_layout = QVBoxLayout()

        row1_layout = QHBoxLayout()
        row1_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        row2_layout = QHBoxLayout()
        row2_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        label_traffic_pk = QLabel("Запись журнала:")
        label_traffic_pk.setFixedWidth(label_traffic_pk.sizeHint().width())
        self.traffic_pk_input = QLineEdit()
        self.traffic_pk_input.setFixedWidth(150)

        label_transaction_pk = QLabel("Транзакция:")
        label_transaction_pk.setFixedWidth(label_transaction_pk.sizeHint().width())
        self.transaction_pk_input = QLineEdit()
        self.transaction_pk_input.setFixedWidth(150)

        self.combobox = EnterpriseComboBox()
        self.button = QPushButton("Начать")
        self.button.setFixedWidth(100)
        self.button.setEnabled(False)

        row1_layout.addWidget(label_traffic_pk)
        row1_layout.addWidget(self.traffic_pk_input)
        row1_layout.addWidget(label_transaction_pk)
        row1_layout.addWidget(self.transaction_pk_input)
        row1_layout.addWidget(self.combobox)
        row1_layout.addWidget(self.button)

        self.checkbox = QCheckBox("Вносить базовые мероприятия, даже если есть специальные")

        row2_layout.addWidget(self.checkbox)

        group_layout.addLayout(row1_layout)
        group_layout.addLayout(row2_layout)
        group_box.setLayout(group_layout)
        layout.addWidget(group_box)
        self.setLayout(layout)

        self.transaction_pk_input.textChanged.connect(self.check_multiple_input)
        self.traffic_pk_input.textChanged.connect(self.check_multiple_input)

    def check_multiple_input(self):
        transaction_pk = self.transaction_pk_input.text()
        traffic_pk = self.traffic_pk_input.text()
        if transaction_pk and traffic_pk:
            self.button.setEnabled(False)
        else:
            self.button.setEnabled(bool(transaction_pk or traffic_pk))
