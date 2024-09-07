import re

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QComboBox, \
    QLayout

from app.database.repositories.manager import RepositoryManager
from app.gui.signals import EnterpriseSignals
from app.schema.enterprise import EnterpriseCreateSchema


class CreateEnterpriseDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Создать шаблон предприятия")
        self.setFixedSize(250, 100)

        self.name_label = QLabel("Название:")
        self.ru_label = QLabel("RU:")
        self.name_input = QLineEdit()
        self.ru_input = QLineEdit()

        label_width = max(self.name_label.sizeHint().width(), self.ru_label.sizeHint().width())
        self.name_label.setFixedWidth(label_width)
        self.ru_label.setFixedWidth(label_width)

        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ru_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.create_button = QPushButton("Создать")
        self.cancel_button = QPushButton("Отмена")

        self.create_button.setEnabled(False)
        self.create_button.clicked.connect(self.create_record)
        self.cancel_button.clicked.connect(self.reject)

        name_layout = QHBoxLayout()
        name_layout.addWidget(self.name_label)
        name_layout.addWidget(self.name_input)

        ru_layout = QHBoxLayout()
        ru_layout.addWidget(self.ru_label)
        ru_layout.addWidget(self.ru_input)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.create_button)
        button_layout.addWidget(self.cancel_button)

        layout = QVBoxLayout()
        layout.addLayout(name_layout)
        layout.addLayout(ru_layout)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.name_input.textChanged.connect(self.check_multiple_input)
        self.ru_input.textChanged.connect(self.check_multiple_input)

    def create_record(self):
        name = self.name_input.text().strip()
        ru = re.sub(r'\D', '', self.ru_input.text())
        if name and ru:
            with RepositoryManager() as repo:
                repo.enterprise.create(EnterpriseCreateSchema(name=name, pk=ru))
            EnterpriseSignals().enterprise_list_changed.emit()
            self.accept()

    def check_multiple_input(self):
        if self.name_input.text() and re.sub(r'\D', '', self.ru_input.text()):
            self.create_button.setEnabled(True)
        else:
            self.create_button.setEnabled(False)


class DeleteEnterpriseDialog(QDialog):
    def __init__(self, enterprise_name: str, enterprise_uuid: str):
        super().__init__()

        self.setWindowTitle("Удалить запись?")
        self.setFixedSize(200, 100)

        self.enterprise_name = enterprise_name
        self.enterprise_uuid = enterprise_uuid

        self.confirm_label = QLabel(f"Действительно удалить \n{self.enterprise_name}?")
        self.confirm_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.delete_button = QPushButton("Да")
        self.cancel_button = QPushButton("Нет")

        self.delete_button.clicked.connect(self.delete_record)
        self.cancel_button.clicked.connect(self.reject)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.cancel_button)

        layout = QVBoxLayout()
        layout.addWidget(self.confirm_label)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def delete_record(self):
        with RepositoryManager() as repo:
            repo.enterprise.delete(self.enterprise_uuid)
        EnterpriseSignals().enterprise_list_changed.emit()
        self.accept()


class EnterpriseComboBox(QComboBox):
    def __init__(self):
        super().__init__()
        self.load_enterprises()
        EnterpriseSignals().enterprise_list_changed.connect(self.load_enterprises)

    def set_combo_box_width(self):
        min_w = 100
        max_w = 200
        if self.count() == 0:
            self.setFixedWidth(min_w)
            return
        max_width = max(self.fontMetrics().boundingRect(self.itemText(i)).width() for i in range(self.count()))
        self.setFixedWidth(max(min_w, min(max_width, max_w)))

    def load_enterprises(self):
        with RepositoryManager() as repo:
            enterprises = repo.enterprise.get_all()
        self.clear()
        for item in enterprises:
            self.addItem(f"{item.name} (RU{item.pk})", item.uuid)
        self.set_combo_box_width()


class EditEnterpriseWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.combobox = EnterpriseComboBox()
        self.add_button = QPushButton("+ Предприятие")
        self.delete_button = QPushButton("- Предприятие")

        self.add_button.clicked.connect(self.open_create_dialog)
        self.delete_button.clicked.connect(self.open_delete_dialog)

        self.set_button_width(self.add_button)
        self.set_button_width(self.delete_button)

        layout = QHBoxLayout()
        layout.addWidget(self.combobox)
        layout.addWidget(self.add_button)
        layout.addWidget(self.delete_button)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.setLayout(layout)

    @staticmethod
    def set_button_width(button: QPushButton):
        size_hint = button.sizeHint()
        button.setFixedWidth(min(max(size_hint.width(), 100), 200))

    @staticmethod
    def open_create_dialog():
        dialog = CreateEnterpriseDialog()
        dialog.exec()

    def open_delete_dialog(self):
        dialog = DeleteEnterpriseDialog(self.combobox.currentText(), self.combobox.currentData())
        dialog.exec()
