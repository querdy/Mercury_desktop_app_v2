import re

from PyQt6.QtCore import Qt, QThreadPool
from PyQt6.QtWidgets import (
    QWidget, QStatusBar, QGridLayout, QPushButton, QLineEdit, QComboBox,
    QFrame, QTableWidget, QGroupBox, QMessageBox, QTableWidgetItem, QLabel
)
from loguru import logger
from sqlalchemy.orm import Session

from app.database.crud.enterprise import create_enterprise, delete_enterprise, get_all_enterprise
from app.database.crud.research import (update_research,
                                        update_special_research, get_base_research_by_enterprise_uuid,
                                        get_special_research_by_enterprise_uuid,
                                        update_exclude_products, get_exclude_products_by_enterprise_uuid
                                        )
from app.database.crud.user import get_user
from app.schema.enterprise import EnterpriseSchema
from app.schema.research import ResearchSchema, SpecialResearchSchema, ExcludeProductSchema
from app.signals import MainSignals
from app.vetis.mercury import Mercury


class ResearchSettings(QWidget):
    RESULT_OPTIONS = {
        "Отрицательно": "2",
        "Положительно": "1",
        "Не определено": "3"
    }

    def __init__(self, status_bar: QStatusBar, db_session: Session, signals: MainSignals, parent=None):
        super().__init__(parent)
        self.status_bar = status_bar
        self.db_session = db_session
        self.thread_pool = QThreadPool()
        self.signals = signals
        self.signals.enterprise_changed.connect(self.load_enterprises)

        self.layout = QGridLayout()
        self.layout.setVerticalSpacing(10)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.layout)

        # Инициализация таблиц
        self.main_lab_table = QTableWidget()
        self.exclude_lab_table = QTableWidget()
        self.special_lab_table = QTableWidget()

        self.init_ui()

    def init_ui(self):
        self.save_button = self.create_button("Сохранить", self.save_button_clicked, 0, 0)
        self.new_enterprise_label = self.create_label('Название', 0, 2, 55)
        self.new_enterprise = self.create_line_edit(0, 3, 100)
        self.new_enterprise_pk_label = self.create_label('RU', 0, 4, 15)
        self.new_enterprise_pk = self.create_line_edit(0, 5, 100)
        self.add_enterprise_button = self.create_button("+ предприятие", self.add_enterprise_button_clicked, 0,
                                                        6)
        self.delete_enterprise_button = self.create_button("- предприятие", self.delete_enterprise_button_clicked,
                                                           0, 7)

        self.main_lab_table_frame = self.create_table_frame("main", self.main_lab_table_columns(), self.main_lab_table,
                                                            2, 0, 1, 9)
        self.exclude_lab_table_frame = self.create_table_frame("Не вносить (общие)", self.exclude_lab_table_columns(),
                                                               self.exclude_lab_table, 2, 9, 1, 3)
        self.special_lab_table_frame = self.create_table_frame("Вносятся на указанную продукцию",
                                                               self.special_lab_table_columns(), self.special_lab_table,
                                                               3, 0, 1, 12)
        self.transaction_pk_line_edit = self.create_line_edit(0, 8, 100)
        self.download_research_button = self.create_button("Загрузить исследования",
                                                           self.download_research_button_clicked, 0, 9)
        self.special_to_base_research_button = self.create_button("Special -> base",
                                                                  self.special_to_base_research_button_clicked, 0, 10)

    def special_to_base_research_button_clicked(self):
        special_research = self.get_special_research()
        base_research = list(dict.fromkeys([ResearchSchema(**research.dict()) for research in special_research]))
        self.fill_main_table(base_research)

    def download_research_button_clicked(self):
        self.download_research_button.setEnabled(False)
        transaction_pk = self.transaction_pk_line_edit.text().strip()
        user = get_user(db=self.db_session)
        mercury = Mercury(login=user.login, password=user.password)
        self.status_bar.showMessage(f"auth: {mercury.is_auth}")
        if not mercury.is_auth:
            return
        created_products = mercury.get_products(transaction_pk=transaction_pk)
        self.status_bar.showMessage(f"created products: {created_products}")
        available_research = []
        for traffic_pk, product in created_products.items():
            available_research.extend([
                SpecialResearchSchema(product=product, **research.dict())
                for research in mercury.get_available_research(traffic_pk)
            ])
        self.status_bar.showMessage(f"available research: {available_research}")
        available_research.extend(self.get_special_research())
        try:
            self.fill_special_table(list(dict.fromkeys(available_research)))
        except Exception as e:
            logger.error(f"{type(e)} {e}")
            self.status_bar.showMessage(f"{type(e)} {e}")
        self.download_research_button.setEnabled(True)

    def create_label(self, text, row, col, maxsize: int = 1000):
        label = QLabel(text)
        label.setMaximumWidth(maxsize)
        self.layout.addWidget(label, row, col, 1, 1)
        return label

    def create_button(self, text, callback, row, col):
        button = QPushButton(text)
        button.clicked.connect(callback)
        self.layout.addWidget(button, row, col, 1, 1)
        return button

    def create_line_edit(self, row, col, max_width):
        line_edit = QLineEdit()
        line_edit.setMaximumWidth(max_width)
        self.layout.addWidget(line_edit, row, col, 1, 1)
        return line_edit

    def create_table_frame(self, title, columns, table, row, col, row_span, col_span):
        frame = QGroupBox(title)
        frame_layout = QGridLayout()
        table.setFrameShape(QFrame.Shape.NoFrame)
        table.setColumnCount(len(columns))
        table.setRowCount(1)
        table.setHorizontalHeaderLabels(columns)
        table.resizeColumnsToContents()
        self.add_table_buttons(table, columns)
        frame_layout.addWidget(self.create_add_button(table), 0, 0, 1, 1)
        frame_layout.addWidget(table, 1, 0, 1, len(columns))
        frame.setLayout(frame_layout)
        self.layout.addWidget(frame, row, col, row_span, col_span)
        return frame

    def create_add_button(self, table):
        button = QPushButton("Добавить")
        button.clicked.connect(lambda: self.add_new_row(table))
        return button

    def add_table_buttons(self, table, columns):
        for idx in range(table.rowCount()):
            if "результат" in columns:
                table.setCellWidget(idx, columns.index("результат"), self.get_result_combobox())
            table.setCellWidget(idx, columns.index("X"), self.get_delete_button(table))

    @staticmethod
    def main_lab_table_columns():
        return ["№ а.о.п.", "дата отбора проб", "лаборатория", "показатель", "протокол", "дата пол-я рез-та", "метод",
                "результат", "заключение", "X"]

    @staticmethod
    def exclude_lab_table_columns():
        return ["наименование продукции", "X"]

    @staticmethod
    def special_lab_table_columns():
        return ["наименование продукции", "№ а.о.п.", "дата отбора проб", "лаборатория", "показатель", "протокол",
                "дата пол-я рез-та", "метод", "результат", "заключение", "X"]

    @staticmethod
    def get_result_combobox(current: str = None):
        combobox = QComboBox()
        for text, data in ResearchSettings.RESULT_OPTIONS.items():
            combobox.addItem(text, data)
        if current is not None:
            index = combobox.findData(current)
            combobox.setCurrentIndex(index)
        return combobox

    def get_delete_button(self, table):
        button = QPushButton("X")
        button.clicked.connect(lambda: self.delete_row(table))
        return button

    @staticmethod
    def delete_row(table):
        table.removeRow(table.currentRow())
        table.clearSelection()

    def add_new_row(self, table):
        table.setRowCount(table.rowCount() + 1)
        row_idx = table.rowCount() - 1
        columns = [table.horizontalHeaderItem(i).text() for i in range(table.columnCount())]
        if "результат" in columns:
            table.setCellWidget(row_idx, columns.index("результат"), self.get_result_combobox())
        table.setCellWidget(row_idx, columns.index("X"), self.get_delete_button(table))

    def add_enterprise_button_clicked(self):
        try:
            enterprise = self.new_enterprise.text().strip()
            enterprise_pk = re.sub(r'\D', '', self.new_enterprise_pk.text())
            if enterprise and enterprise_pk:
                create_enterprise(
                    db=self.db_session,
                    enterprise=EnterpriseSchema(name=enterprise, pk=enterprise_pk)
                )
            else:
                self.status_bar.showMessage(f'Необходимо указать название шаблона и номер предприятия в реестре')

        except Exception as e:
            logger.error(f"{type(e)}, {e}")
        finally:
            self.new_enterprise.setText("")
            self.new_enterprise_pk.setText("")
            try:
                self.signals.enterprise_changed.emit()
            except Exception as e:
                logger.error(f"{type(e)} {e}")

    def delete_enterprise_button_clicked(self):
        reply = QMessageBox.question(self, 'Подтверждение', 'Вы уверены?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                delete_enterprise(db=self.db_session, enterprise_uuid=self.enterprise_combobox.currentData())
            finally:
                self.signals.enterprise_changed.emit()

    def load_enterprises(self):
        enterprises = get_all_enterprise(db=self.db_session)
        self.enterprise_combobox = QComboBox()
        for item in enterprises:
            self.enterprise_combobox.addItem(item.name, item.uuid)
        self.enterprise_combobox.currentIndexChanged.connect(self.enterprise_combobox_changed)
        self.load_research_data()
        self.layout.addWidget(self.enterprise_combobox, 0, 1, 1, 1)

    def enterprise_combobox_changed(self):
        self.load_research_data()

    def load_research_data(self):
        current_enterprise_uuid = self.enterprise_combobox.currentData()
        base_research = get_base_research_by_enterprise_uuid(self.db_session, current_enterprise_uuid)
        special_research = get_special_research_by_enterprise_uuid(self.db_session, current_enterprise_uuid)
        exclude_products = get_exclude_products_by_enterprise_uuid(self.db_session, current_enterprise_uuid)
        self.fill_main_table([ResearchSchema.from_orm(item) for item in base_research])
        self.fill_special_table([SpecialResearchSchema.from_orm(item) for item in special_research])
        self.fill_exclude_product_table([ExcludeProductSchema.from_orm(item) for item in exclude_products])

    def fill_main_table(self, research_data: list[ResearchSchema]):
        self.main_lab_table.clearContents()
        self.main_lab_table.setRowCount(len(research_data))
        for row, research in enumerate(research_data):
            self.main_lab_table.setItem(row, 0, QTableWidgetItem(research.sampling_number))
            self.main_lab_table.setItem(row, 1, QTableWidgetItem(research.sampling_date))
            self.main_lab_table.setItem(row, 2, QTableWidgetItem(research.operator))
            self.main_lab_table.setItem(row, 3, QTableWidgetItem(research.disease))
            self.main_lab_table.setItem(row, 4, QTableWidgetItem(research.expertise_id))
            self.main_lab_table.setItem(row, 5, QTableWidgetItem(research.date_of_research))
            self.main_lab_table.setItem(row, 6, QTableWidgetItem(research.method))
            self.main_lab_table.setCellWidget(row, 7, self.get_result_combobox(research.result))
            self.main_lab_table.setItem(row, 8, QTableWidgetItem(research.conclusion))
            self.main_lab_table.setCellWidget(row, 9, self.get_delete_button(self.main_lab_table))

    def fill_special_table(self, research_data: list[SpecialResearchSchema]):
        self.special_lab_table.clearContents()
        self.special_lab_table.setRowCount(len(research_data))
        for row, research in enumerate(research_data):
            self.special_lab_table.setItem(row, 0, QTableWidgetItem(research.product))
            self.special_lab_table.setItem(row, 1, QTableWidgetItem(research.sampling_number))
            self.special_lab_table.setItem(row, 2, QTableWidgetItem(research.sampling_date))
            self.special_lab_table.setItem(row, 3, QTableWidgetItem(research.operator))
            self.special_lab_table.setItem(row, 4, QTableWidgetItem(research.disease))
            self.special_lab_table.setItem(row, 5, QTableWidgetItem(research.expertise_id))
            self.special_lab_table.setItem(row, 6, QTableWidgetItem(research.date_of_research))
            self.special_lab_table.setItem(row, 7, QTableWidgetItem(research.method))
            self.special_lab_table.setCellWidget(row, 8, self.get_result_combobox(research.result))
            self.special_lab_table.setItem(row, 9, QTableWidgetItem(research.conclusion))
            self.special_lab_table.setCellWidget(row, 10, self.get_delete_button(self.special_lab_table))

    def fill_exclude_product_table(self, products: list[ExcludeProductSchema]):
        self.exclude_lab_table.clearContents()
        self.exclude_lab_table.setRowCount(len(products))
        for row, product in enumerate(products):
            self.exclude_lab_table.setItem(row, 0, QTableWidgetItem(product.product))
            self.exclude_lab_table.setCellWidget(row, 1, self.get_delete_button(self.exclude_lab_table))

    def save_button_clicked(self):
        try:
            current_base_research = self.get_base_research()
            base_research = update_research(db=self.db_session,
                                            enterprise_uuid=self.enterprise_combobox.currentData(),
                                            research=current_base_research)
            self.fill_main_table([ResearchSchema.from_orm(item) for item in base_research])

            current_special_research = self.get_special_research()
            special_research = update_special_research(db=self.db_session,
                                                       enterprise_uuid=self.enterprise_combobox.currentData(),
                                                       research=current_special_research)
            self.fill_special_table([SpecialResearchSchema.from_orm(item) for item in special_research])

            exclude_products = self.get_exclude_products()
            exclude_products = update_exclude_products(
                db=self.db_session,
                products=exclude_products,
                enterprise_uuid=self.enterprise_combobox.currentData()
            )
            self.fill_exclude_product_table([ExcludeProductSchema.from_orm(item) for item in exclude_products])

            self.status_bar.showMessage("Исследования сохранены")
        except Exception as e:
            self.status_bar.showMessage(f"{type(e)} {e}")
            logger.error(f"{type(e)} {e}")

    def get_base_research(self) -> list[ResearchSchema]:
        number_of_rows = self.main_lab_table.rowCount()
        researches = []
        for i in range(number_of_rows):
            try:
                sampling_number = self.main_lab_table.item(i, 0).text()
            except AttributeError:
                sampling_number = ""
            try:
                sampling_date = self.main_lab_table.item(i, 1).text()
            except AttributeError:
                sampling_date = ""
            try:
                method = self.main_lab_table.item(i, 6).text()
            except AttributeError:
                method = ""
            try:
                operator = self.main_lab_table.item(i, 2).text()
                disease = self.main_lab_table.item(i, 3).text()
                expertise_id = self.main_lab_table.item(i, 4).text()
                date_of_research = self.main_lab_table.item(i, 5).text()
                result = self.main_lab_table.cellWidget(i, 7).currentData()
                conclusion = self.main_lab_table.item(i, 8).text()
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
                self.status_bar.showMessage(f"Не все необходимые поля заполнены. Строка {i + 1}. Таблица main")
                return
            except ValueError as error:
                logger.error(f"{type(error)}: {error}")
                self.status_bar.showMessage(f"Неверный ввод данных. Строка {i + 1}. Таблица main")
                return
        return list(dict.fromkeys(researches))

    def get_exclude_products(self) -> list[ExcludeProductSchema]:
        number_of_rows = self.exclude_lab_table.rowCount()
        products = []
        for i in range(number_of_rows):
            try:
                products.append(ExcludeProductSchema(product=self.exclude_lab_table.item(i, 0).text()))
            except AttributeError as error:
                logger.error(f"{type(error)}: {error}")
        return list(dict.fromkeys(products))

    def get_special_research(self) -> list[SpecialResearchSchema]:
        number_of_rows = self.special_lab_table.rowCount()
        researches = []
        for i in range(number_of_rows):
            try:
                sampling_number = self.special_lab_table.item(i, 1).text()
            except AttributeError:
                sampling_number = ""
            try:
                sampling_date = self.special_lab_table.item(i, 2).text()
            except AttributeError:
                sampling_date = ""
            try:
                method = self.special_lab_table.item(i, 7).text()
            except AttributeError:
                method = ""
            try:
                product = self.special_lab_table.item(i, 0).text()
                operator = self.special_lab_table.item(i, 3).text()
                disease = self.special_lab_table.item(i, 4).text()
                expertise_id = self.special_lab_table.item(i, 5).text()
                date_of_research = self.special_lab_table.item(i, 6).text()
                result = self.special_lab_table.cellWidget(i, 8).currentData()
                conclusion = self.special_lab_table.item(i, 9).text()
                researches.append(
                    SpecialResearchSchema(
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
                self.status_bar.showMessage(f"Не все необходимые поля заполнены. Строка {i + 1}. Таблица special")
                return
            except ValueError as error:
                logger.error(f"{type(error)}: {error}")
                self.status_bar.showMessage(f"Неверный ввод данных. Строка {i + 1}. Таблица special")
                return
        return list(dict.fromkeys(researches))
