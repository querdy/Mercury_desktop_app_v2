from PyQt6.QtWidgets import  QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QWidget


class TableWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Таблица с добавлением и удалением строк")
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()

        # Кнопка для добавления строки
        self.add_button = QPushButton("Добавить строку")
        self.add_button.clicked.connect(self.add_row)
        self.layout.addWidget(self.add_button)  # Добавляем кнопку в верхнюю часть

        self.table = QTableWidget(0, 2)  # 0 строк, 2 столбца
        self.table.setHorizontalHeaderLabels(["Данные", "Удалить"])
        self.layout.addWidget(self.table)  # Добавляем таблицу под кнопкой

        self.setLayout(self.layout)

    def add_row(self):
        # Получаем индекс выделенной строки
        current_row = self.table.currentRow()

        # Если строка не выделена, добавляем в конец
        if current_row == -1:
            current_row = self.table.rowCount()

        # Добавляем новую строку
        self.table.insertRow(current_row)

        # Добавляем кнопку для удаления строки
        delete_button = QPushButton("Удалить")
        delete_button.clicked.connect(lambda checked, row=current_row: self.delete_row(row))
        self.table.setCellWidget(current_row, 1, delete_button)

    def delete_row(self):
        self.table.removeRow(self.table.currentRow())
        self.table.clearSelection()
