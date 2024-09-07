from typing import Sequence

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QGroupBox, QWidget, QTableWidget, QPushButton, QComboBox, QTableWidgetItem
from loguru import logger

from app.schema.immunization import ImmunizationSchema
from app.schema.research import ResearchSchema, ExcludeProductSchema


class SomeTableWidgetMixin(QWidget):
    def __init__(self):
        super().__init__()
        self.RESULT_OPTIONS = {
            "Отрицательно": "2",
            "Положительно": "1",
            "Не определено": "3"
        }
        self.TYPE_OPTIONS = {
            "Иммунизация": "1",
            "Обработка": "0",
        }

    @staticmethod
    def create_table(headers: list[str]):
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.resizeColumnsToContents()
        return table

    def create_add_button(self, table: QTableWidget):
        button = QPushButton("Добавить")
        button.setFixedWidth(button.sizeHint().width())
        button.clicked.connect(lambda: self.add_row(table))
        return button

    def add_row(self, table: QTableWidget):
        current_row = table.currentRow()
        if current_row == -1:
            current_row = table.rowCount()
        else:
            current_row += 1
        table.insertRow(current_row)
        columns = [table.horizontalHeaderItem(i).text() for i in range(table.columnCount())]
        if "тип" in columns:
            table.setCellWidget(current_row, columns.index("тип"), self.get_type_combobox())
            table.resizeColumnToContents(columns.index("тип"))
        if "результат" in columns:
            table.setCellWidget(current_row, columns.index("результат"), self.get_result_combobox())
            table.resizeColumnToContents(columns.index("результат"))
        table.setCellWidget(current_row, table.columnCount() - 1, self.get_remove_row_button(table))

    def get_result_combobox(self, current: str = None):
        combobox = QComboBox()
        for text, data in self.RESULT_OPTIONS.items():
            combobox.addItem(text, data)
        if current is not None:
            index = combobox.findData(current)
            combobox.setCurrentIndex(index)
        return combobox

    def get_type_combobox(self, current: str = None):
        combobox = QComboBox()
        for text, data in self.TYPE_OPTIONS.items():
            combobox.addItem(text, data)
        if current is not None:
            index = combobox.findData(current)
            combobox.setCurrentIndex(index)
        return combobox

    def get_remove_row_button(self, table: QTableWidget):
        button = QPushButton("X")
        button.clicked.connect(lambda: self.remove_row(table))
        return button

    @staticmethod
    def remove_row(table: QTableWidget):
        current_row = table.currentRow()
        if current_row >= 0:
            table.removeRow(current_row)
            table.clearSelection()


class ResearchTables(SomeTableWidgetMixin):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout()

        self.group_main = QGroupBox("main")
        main_table_headers = ["№ а.о.п.", "дата отбора проб", "лаборатория", "показатель", "протокол",
                              "дата пол-я рез-та", "метод", "результат", "заключение", "X"]
        self.table_main = self.create_table(main_table_headers)
        self.add_button_main = self.create_add_button(self.table_main)
        self.group_main_layout = QVBoxLayout()
        self.group_main_layout.addWidget(self.add_button_main)
        self.group_main_layout.addWidget(self.table_main)
        self.group_main.setLayout(self.group_main_layout)

        self.group_exclude = QGroupBox("Не вносятся (main)")
        exclude_table_headers = ["наименование продукции", "X"]
        self.table_exclude = self.create_table(exclude_table_headers)
        self.add_button_exclude = self.create_add_button(self.table_exclude)
        self.group_exclude_layout = QVBoxLayout()
        self.group_exclude_layout.addWidget(self.add_button_exclude)
        self.group_exclude_layout.addWidget(self.table_exclude)
        self.group_exclude.setLayout(self.group_exclude_layout)

        self.group_special = QGroupBox("Вносятся на указанную продукцию")
        special_table_headers = ["наименование из справочника", "№ а.о.п.", "дата отбора проб", "лаборатория",
                                 "показатель",
                                 "протокол", "дата пол-я рез-та", "метод", "результат", "заключение", "X"]
        self.table_special = self.create_table(special_table_headers)
        self.add_button_special = self.create_add_button(self.table_special)
        self.special_to_base_button = QPushButton("Перенести в main")
        self.special_to_base_button.setFixedWidth(self.special_to_base_button.sizeHint().width())
        self.special_to_base_button.clicked.connect(self.special_to_base_button_clicked)
        self.group_special_layout = QVBoxLayout()
        self.group_special_btn_layout = QHBoxLayout()
        self.group_special_btn_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.group_special_btn_layout.addWidget(self.add_button_special)
        self.group_special_btn_layout.addWidget(self.special_to_base_button)
        self.group_special_layout.addLayout(self.group_special_btn_layout)
        self.group_special_layout.addWidget(self.table_special)
        self.group_special.setLayout(self.group_special_layout)

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.group_main, 7)  # 70% ширины
        h_layout.addWidget(self.group_exclude, 3)  # 30% ширины

        main_layout.addLayout(h_layout)
        main_layout.addWidget(self.group_special)  # 100% ширины

        self.setLayout(main_layout)

    def get_base(self) -> list[ResearchSchema]:
        number_of_rows = self.table_main.rowCount()
        researches = []
        for i in range(number_of_rows):
            try:
                sampling_number = self.table_main.item(i, 0).text()
            except AttributeError:
                sampling_number = ""
            try:
                sampling_date = self.table_main.item(i, 1).text()
            except AttributeError:
                sampling_date = ""
            try:
                method = self.table_main.item(i, 6).text()
            except AttributeError:
                method = ""
            try:
                operator = self.table_main.item(i, 2).text()
                disease = self.table_main.item(i, 3).text()
                expertise_id = self.table_main.item(i, 4).text()
                date_of_research = self.table_main.item(i, 5).text()
                result = self.table_main.cellWidget(i, 7).currentData()
                conclusion = self.table_main.item(i, 8).text()
                researches.append(
                    ResearchSchema(
                        sampling_number=sampling_number,
                        sampling_date=sampling_date,
                        operator=operator,
                        disease=disease,
                        expertise_id=expertise_id,
                        date_of_research=date_of_research,
                        method=method,
                        result=result,
                        conclusion=conclusion,
                    )
                )
            except AttributeError as error:
                logger.error(f"{type(error)}: {error}")
                continue
            except ValueError as error:
                logger.error(f"{type(error)}: {error}")
                return []
        return list(dict.fromkeys(researches))

    def get_special(self) -> list[ResearchSchema]:
        number_of_rows = self.table_special.rowCount()
        researches = []
        for i in range(number_of_rows):
            try:
                sampling_number = self.table_special.item(i, 1).text()
            except AttributeError:
                sampling_number = ""
            try:
                sampling_date = self.table_special.item(i, 2).text()
            except AttributeError:
                sampling_date = ""
            try:
                method = self.table_special.item(i, 7).text()
            except AttributeError:
                method = ""
            try:
                product = self.table_special.item(i, 0).text()
                operator = self.table_special.item(i, 3).text()
                disease = self.table_special.item(i, 4).text()
                expertise_id = self.table_special.item(i, 5).text()
                date_of_research = self.table_special.item(i, 6).text()
                result = self.table_special.cellWidget(i, 8).currentData()
                conclusion = self.table_special.item(i, 9).text()
                researches.append(
                    ResearchSchema(
                        product=product,
                        sampling_number=sampling_number,
                        sampling_date=sampling_date,
                        operator=operator,
                        disease=disease,
                        date_of_research=date_of_research,
                        method=method,
                        expertise_id=expertise_id,
                        result=result,
                        conclusion=conclusion,
                    )
                )
            except AttributeError as error:
                logger.error(f"{type(error)}: {error}")
                continue
            except ValueError as error:
                logger.error(f"{type(error)}: {error}")
                return []
        return list(dict.fromkeys(researches))

    def get_exclude_products(self) -> list[ExcludeProductSchema]:
        number_of_rows = self.table_exclude.rowCount()
        products = []
        for i in range(number_of_rows):
            try:
                products.append(ExcludeProductSchema(product=self.table_exclude.item(i, 0).text()))
            except AttributeError as error:
                logger.error(f"{type(error)}: {error}")
                continue
        return list(dict.fromkeys(products))

    def fill_main_table(self, research_data: Sequence[ResearchSchema]):
        self.table_main.clearContents()
        self.table_main.setRowCount(len(research_data))
        for row, research in enumerate(research_data):
            self.table_main.setItem(row, 0, QTableWidgetItem(research.sampling_number))
            self.table_main.setItem(row, 1, QTableWidgetItem(research.sampling_date))
            self.table_main.setItem(row, 2, QTableWidgetItem(research.operator))
            self.table_main.setItem(row, 3, QTableWidgetItem(research.disease))
            self.table_main.setItem(row, 4, QTableWidgetItem(research.expertise_id))
            self.table_main.setItem(row, 5, QTableWidgetItem(research.date_of_research))
            self.table_main.setItem(row, 6, QTableWidgetItem(research.method))
            self.table_main.setCellWidget(row, 7, self.get_result_combobox(research.result))
            self.table_main.resizeColumnToContents(7)
            self.table_main.setItem(row, 8, QTableWidgetItem(research.conclusion))
            self.table_main.setCellWidget(row, 9, self.get_remove_row_button(self.table_main))

    def fill_special_table(self, research_data: Sequence[ResearchSchema]):
        self.table_special.clearContents()
        self.table_special.setRowCount(len(research_data))
        for row, research in enumerate(research_data):
            self.table_special.setItem(row, 0, QTableWidgetItem(research.product))
            self.table_special.setItem(row, 1, QTableWidgetItem(research.sampling_number))
            self.table_special.setItem(row, 2, QTableWidgetItem(research.sampling_date))
            self.table_special.setItem(row, 3, QTableWidgetItem(research.operator))
            self.table_special.setItem(row, 4, QTableWidgetItem(research.disease))
            self.table_special.setItem(row, 5, QTableWidgetItem(research.expertise_id))
            self.table_special.setItem(row, 6, QTableWidgetItem(research.date_of_research))
            self.table_special.setItem(row, 7, QTableWidgetItem(research.method))
            self.table_special.setCellWidget(row, 8, self.get_result_combobox(research.result))
            self.table_special.resizeColumnToContents(8)
            self.table_special.setItem(row, 9, QTableWidgetItem(research.conclusion))
            self.table_special.setCellWidget(row, 10, self.get_remove_row_button(self.table_special))

    def fill_exclude_product_table(self, products: Sequence[ExcludeProductSchema]):
        self.table_exclude.clearContents()
        self.table_exclude.setRowCount(len(products))
        for row, product in enumerate(products):
            self.table_exclude.setItem(row, 0, QTableWidgetItem(product.product))
            self.table_exclude.setCellWidget(row, 1, self.get_remove_row_button(self.table_exclude))

    def special_to_base_button_clicked(self):
        items = self.get_special()
        if not items:
            return
        if isinstance(items[0], ResearchSchema):
            unique_items = [
                ResearchSchema(
                    product=None,
                    sampling_number=item.sampling_number,
                    sampling_date=item.sampling_date,
                    operator=item.operator,
                    method=item.method,
                    disease=item.disease,
                    date_of_research=item.date_of_research,
                    expertise_id=item.expertise_id,
                    result=item.result,
                    conclusion=item.conclusion
                )
                for item in items
            ]
            self.fill_main_table(list(dict.fromkeys(unique_items)))
        elif isinstance(items[0], ImmunizationSchema):
            unique_items = [
                ImmunizationSchema(
                    product=None,
                    operation_type=item.operation_type,
                    illness=item.illness,
                    operation_date=item.operation_date,
                    vaccine_name=item.vaccine_name,
                    vaccine_serial=item.vaccine_serial,
                    vaccine_date_to=item.vaccine_date_to
                )
                for item in items
            ]
            self.fill_main_table(list(dict.fromkeys(unique_items)))


class ImmunizationTables(SomeTableWidgetMixin):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout()

        self.group_main = QGroupBox("main")
        main_table_headers = ["тип", "наименование болезни", "дата проведения",
                              "название и производитель препарата",
                              "номер серии препарата", "действие до", "X"]
        self.table_main = self.create_table(main_table_headers)
        self.add_button_main = self.create_add_button(self.table_main)
        self.group_main_layout = QVBoxLayout()
        self.group_main_layout.addWidget(self.add_button_main)
        self.group_main_layout.addWidget(self.table_main)
        self.group_main.setLayout(self.group_main_layout)

        self.group_special = QGroupBox("Вносятся на указанную продукцию")
        special_table_headers = ["наименование из справочника", "тип", "наименование болезни", "дата проведения",
                                 "название и производитель препарата", "номер серии препарата", "действие до", "X"]
        self.table_special = self.create_table(special_table_headers)
        self.add_button_special = self.create_add_button(self.table_special)
        self.special_to_base_button = QPushButton("Перенести в main")
        self.special_to_base_button.setFixedWidth(self.special_to_base_button.sizeHint().width())
        self.special_to_base_button.clicked.connect(self.special_to_base_button_clicked)
        self.group_special_layout = QVBoxLayout()
        self.group_special_btn_layout = QHBoxLayout()
        self.group_special_btn_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.group_special_btn_layout.addWidget(self.add_button_special)
        self.group_special_btn_layout.addWidget(self.special_to_base_button)
        self.group_special_layout.addLayout(self.group_special_btn_layout)
        self.group_special_layout.addWidget(self.table_special)
        self.group_special.setLayout(self.group_special_layout)

        main_layout.addWidget(self.group_main)
        main_layout.addWidget(self.group_special)

        self.setLayout(main_layout)

    def get_base(self) -> list[ImmunizationSchema]:
        number_of_rows = self.table_main.rowCount()
        immunization = []
        for i in range(number_of_rows):
            try:
                vaccine_name = self.table_main.item(i, 3).text()
            except AttributeError:
                vaccine_name = ""
            try:
                vaccine_serial = self.table_main.item(i, 4).text()
            except AttributeError:
                vaccine_serial = ""
            try:
                vaccine_date_to = self.table_main.item(i, 5).text()
            except AttributeError:
                vaccine_date_to = ""

            try:
                operation_type = self.table_main.cellWidget(i, 0).currentData()
                illness = self.table_main.item(i, 1).text()
                operation_date = self.table_main.item(i, 2).text()
                immunization.append(
                    ImmunizationSchema(
                        operation_type=operation_type,
                        illness=illness,
                        operation_date=operation_date,
                        vaccine_name=vaccine_name,
                        vaccine_serial=vaccine_serial,
                        vaccine_date_to=vaccine_date_to
                    )
                )
            except AttributeError as error:
                logger.error(f"{type(error)}: {error}")
                continue
            except ValueError as error:
                logger.error(f"{type(error)}: {error}")
                return []
        return list(dict.fromkeys(immunization))

    def get_special(self) -> list[ImmunizationSchema]:
        number_of_rows = self.table_special.rowCount()
        immunization = []
        for i in range(number_of_rows):
            try:
                vaccine_name = self.table_special.item(i, 4).text()
            except AttributeError:
                vaccine_name = ""
            try:
                vaccine_serial = self.table_special.item(i, 5).text()
            except AttributeError:
                vaccine_serial = ""
            try:
                vaccine_date_to = self.table_special.item(i, 6).text()
            except AttributeError:
                vaccine_date_to = ""

            try:
                product = self.table_special.item(i, 0).text()
                operation_type = self.table_special.cellWidget(i, 1).currentData()
                illness = self.table_special.item(i, 2).text()
                operation_date = self.table_special.item(i, 3).text()
                immunization.append(
                    ImmunizationSchema(
                        product=product,
                        operation_type=operation_type,
                        illness=illness,
                        operation_date=operation_date,
                        vaccine_name=vaccine_name,
                        vaccine_serial=vaccine_serial,
                        vaccine_date_to=vaccine_date_to
                    )
                )
            except AttributeError as error:
                logger.error(f"{type(error)}: {error}")
                continue
            except ValueError as error:
                logger.error(f"{type(error)}: {error}")
                return []
        return list(dict.fromkeys(immunization))

    def fill_main_table(self, immunization_data: Sequence[ImmunizationSchema]):
        self.table_main.clearContents()
        self.table_main.setRowCount(len(immunization_data))
        for row, immunization in enumerate(immunization_data):
            self.table_main.setCellWidget(
                row, 0, self.get_type_combobox(immunization.operation_type)
            )
            self.table_main.resizeColumnToContents(0)
            self.table_main.setItem(row, 1, QTableWidgetItem(immunization.illness))
            self.table_main.setItem(row, 2, QTableWidgetItem(immunization.operation_date))
            self.table_main.setItem(row, 3, QTableWidgetItem(immunization.vaccine_name))
            self.table_main.setItem(row, 4, QTableWidgetItem(immunization.vaccine_serial))
            self.table_main.setItem(row, 5, QTableWidgetItem(immunization.vaccine_date_to))
            self.table_main.setCellWidget(
                row, 6, self.get_remove_row_button(self.table_main)
            )

    def fill_special_table(self, immunization_data: Sequence[ImmunizationSchema]):
        self.table_special.clearContents()
        self.table_special.setRowCount(len(immunization_data))
        for row, immunization in enumerate(immunization_data):
            self.table_special.setItem(row, 0, QTableWidgetItem(immunization.product))
            self.table_special.setCellWidget(
                row, 1, self.get_type_combobox(immunization.operation_type)
            )
            self.table_special.resizeColumnToContents(1)
            self.table_special.setItem(row, 2, QTableWidgetItem(immunization.illness))
            self.table_special.setItem(row, 3, QTableWidgetItem(immunization.operation_date))
            self.table_special.setItem(row, 4, QTableWidgetItem(immunization.vaccine_name))
            self.table_special.setItem(row, 5, QTableWidgetItem(immunization.vaccine_serial))
            self.table_special.setItem(row, 6, QTableWidgetItem(immunization.vaccine_date_to))
            self.table_special.setCellWidget(
                row, 7, self.get_remove_row_button(self.table_special)
            )

    def special_to_base_button_clicked(self):
        self.fill_main_table(self.get_special())
