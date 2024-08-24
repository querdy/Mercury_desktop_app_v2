import re

from PyQt6.QtCore import QThreadPool, Qt
from PyQt6.QtWidgets import QWidget, QStatusBar, QGridLayout, QTableWidget, QComboBox, QPushButton, QMessageBox, \
    QLineEdit, QGroupBox, QFrame, QTableWidgetItem, QLabel
from loguru import logger
from sqlalchemy.orm import Session

from app.database.crud.immunization import get_base_immunization_by_enterprise_uuid, \
    get_special_immunization_by_enterprise_uuid, update_immunization, update_special_immunization
from app.database.crud.enterprise import get_all_enterprise, create_enterprise, delete_enterprise
from app.database.crud.user import get_user
from app.schema.enterprise import EnterpriseSchema
from app.schema.immunization import ImmunizationSchema, SpecialImmunizationSchema
from app.signals import MainSignals
from app.vetis.mercury import Mercury


class ImmunizationSettings(QWidget):
    RESULT_OPTIONS = {
        "Иммунизация": "1",
        "Обработка": "0",
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
        self.main_immunization_table = QTableWidget()
        self.special_immunization_table = QTableWidget()

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

        self.main_immunization_table_frame = self.create_table_frame("main", self.main_immunization_table_columns(),
                                                                     self.main_immunization_table,
                                                                     2, 0, 1, 12)
        self.special_immunization_table_frame = self.create_table_frame("Вносятся на указанную продукцию",
                                                                        self.special_immunization_table_columns(),
                                                                        self.special_immunization_table,
                                                                        3, 0, 1, 12)
        self.transaction_pk_line_edit = self.create_line_edit(0, 8, 100)
        self.download_immunization_button = self.create_button("Загрузить иммунизации",
                                                               self.download_immunization_button_clicked, 0, 9)
        self.special_to_base__button = self.create_button("Special -> base",
                                                          self.special_to_base_button_clicked, 0, 10
                                                          )

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
        self.add_table_buttons(table, columns)
        table.resizeColumnsToContents()
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
            if "тип" in columns:
                table.setCellWidget(idx, columns.index("тип"), self.get_result_combobox())
            table.setCellWidget(idx, columns.index("X"), self.get_delete_button(table))

    def get_delete_button(self, table):
        button = QPushButton("X")
        button.clicked.connect(lambda: self.delete_row(table))
        return button

    @staticmethod
    def delete_row(table):
        table.removeRow(table.currentRow())
        table.clearSelection()

    @staticmethod
    def get_result_combobox(current: str = None):
        combobox = QComboBox()
        for text, data in ImmunizationSettings.RESULT_OPTIONS.items():
            combobox.addItem(text, data)
        if current is not None:
            index = combobox.findData(current)
            combobox.setCurrentIndex(index)
        return combobox

    def add_new_row(self, table):
        table.setRowCount(table.rowCount() + 1)
        row_idx = table.rowCount() - 1
        columns = [table.horizontalHeaderItem(i).text() for i in range(table.columnCount())]
        if "тип" in columns:
            table.setCellWidget(row_idx, columns.index("тип"), self.get_result_combobox())
        table.setCellWidget(row_idx, columns.index("X"), self.get_delete_button(table))

    def download_immunization_button_clicked(self):
        self.download_immunization_button.setEnabled(False)
        transaction_pk = self.transaction_pk_line_edit.text().strip()
        user = get_user(db=self.db_session)
        mercury = Mercury(login=user.login, password=user.password)
        if not mercury.is_auth:
            return
        created_products = mercury.get_products(transaction_pk=transaction_pk)
        available_immunization = []
        for traffic_pk, product in created_products.items():
            available_immunization.extend([
                SpecialImmunizationSchema(product=product, **immunization.dict())
                for immunization in mercury.get_available_immunization(traffic_pk)
            ])
        available_immunization.extend(self.get_special_immunization())
        try:
            self.fill_special_table(list(dict.fromkeys(available_immunization)))
        except Exception as e:
            logger.error(f"{type(e)} {e}")
        self.download_immunization_button.setEnabled(True)

    def special_to_base_button_clicked(self):
        special_immunization = self.get_special_immunization()
        base_immunization = [ImmunizationSchema(**immunization.dict()) for immunization in special_immunization]
        self.fill_main_table(base_immunization)

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

    def save_button_clicked(self):
        try:
            current_base_immunization = self.get_base_immunization()
            base_immunization = update_immunization(db=self.db_session,
                                                    enterprise_uuid=self.enterprise_combobox.currentData(),
                                                    immunization=current_base_immunization)
            self.fill_main_table([ImmunizationSchema.from_orm(item) for item in base_immunization])

            current_special_immunization = self.get_special_immunization()
            special_immunization = update_special_immunization(db=self.db_session,
                                                               enterprise_uuid=self.enterprise_combobox.currentData(),
                                                               immunization=current_special_immunization)
            self.fill_special_table([SpecialImmunizationSchema.from_orm(item) for item in special_immunization])

            self.status_bar.showMessage("Данные об иммунизации сохранены")
        except Exception as e:
            self.status_bar.showMessage(f"{type(e)} {e}")
            logger.error(f"{type(e)} {e}")

    def get_base_immunization(self) -> list[ImmunizationSchema]:
        number_of_rows = self.main_immunization_table.rowCount()
        immunization = []
        for i in range(number_of_rows):
            try:
                vaccine_name = self.main_immunization_table.item(i, 3).text()
            except AttributeError:
                vaccine_name = ""
            try:
                vaccine_serial = self.main_immunization_table.item(i, 4).text()
            except AttributeError:
                vaccine_serial = ""
            try:
                vaccine_date_to = self.main_immunization_table.item(i, 5).text()
            except AttributeError:
                vaccine_date_to = ""

            try:
                operation_type = self.main_immunization_table.cellWidget(i, 0).currentData()
                illness = self.main_immunization_table.item(i, 1).text()
                operation_date = self.main_immunization_table.item(i, 2).text()
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
                self.status_bar.showMessage(f"Не все необходимые поля заполнены. Строка {i + 1}. Таблица main")
                return
            except ValueError as error:
                logger.error(f"{type(error)}: {error}")
                self.status_bar.showMessage(f"Неверный ввод данных. Строка {i + 1}. Таблица main")
                return
        return list(dict.fromkeys(immunization))

    def get_special_immunization(self) -> list[SpecialImmunizationSchema]:
        number_of_rows = self.special_immunization_table.rowCount()
        immunization = []
        for i in range(number_of_rows):
            try:
                vaccine_name = self.special_immunization_table.item(i, 4).text()
            except AttributeError:
                vaccine_name = ""
            try:
                vaccine_serial = self.special_immunization_table.item(i, 5).text()
            except AttributeError:
                vaccine_serial = ""
            try:
                vaccine_date_to = self.special_immunization_table.item(i, 6).text()
            except AttributeError:
                vaccine_date_to = ""

            try:
                product = self.special_immunization_table.item(i, 0).text()
                operation_type = self.special_immunization_table.cellWidget(i, 1).currentData()
                illness = self.special_immunization_table.item(i, 2).text()
                operation_date = self.special_immunization_table.item(i, 3).text()
                immunization.append(
                    SpecialImmunizationSchema(
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
                self.status_bar.showMessage(f"Не все необходимые поля заполнены. Строка {i + 1}. Таблица special")
                return
            except ValueError as error:
                logger.error(f"{type(error)}: {error}")
                self.status_bar.showMessage(f"Неверный ввод данных. Строка {i + 1}. Таблица special")
                return
        return list(dict.fromkeys(immunization))

    def load_enterprises(self):
        enterprises = get_all_enterprise(db=self.db_session)
        self.enterprise_combobox = QComboBox()
        for item in enterprises:
            self.enterprise_combobox.addItem(item.name, item.uuid)
        self.enterprise_combobox.currentIndexChanged.connect(self.enterprise_combobox_changed)
        self.load_immunization_data()
        self.layout.addWidget(self.enterprise_combobox, 0, 1, 1, 1)

    def enterprise_combobox_changed(self):
        self.load_immunization_data()

    def load_immunization_data(self):
        current_enterprise_uuid = self.enterprise_combobox.currentData()
        base_immunization = get_base_immunization_by_enterprise_uuid(self.db_session, current_enterprise_uuid)
        special_immunization = get_special_immunization_by_enterprise_uuid(self.db_session, current_enterprise_uuid)
        self.fill_main_table([ImmunizationSchema.from_orm(item) for item in base_immunization])
        self.fill_special_table([SpecialImmunizationSchema.from_orm(item) for item in special_immunization])

    def fill_main_table(self, immunization_data: list[ImmunizationSchema]):
        self.main_immunization_table.clearContents()
        self.main_immunization_table.setRowCount(len(immunization_data))
        for row, immunization in enumerate(immunization_data):
            self.main_immunization_table.setCellWidget(
                row, 0, self.get_result_combobox(immunization.operation_type)
            )
            self.main_immunization_table.setItem(row, 1, QTableWidgetItem(immunization.illness))
            self.main_immunization_table.setItem(row, 2, QTableWidgetItem(immunization.operation_date))
            self.main_immunization_table.setItem(row, 3, QTableWidgetItem(immunization.vaccine_name))
            self.main_immunization_table.setItem(row, 4, QTableWidgetItem(immunization.vaccine_serial))
            self.main_immunization_table.setItem(row, 5, QTableWidgetItem(immunization.vaccine_date_to))
            self.main_immunization_table.setCellWidget(
                row, 6, self.get_delete_button(self.main_immunization_table)
            )

    def fill_special_table(self, immunization_data: list[ImmunizationSchema]):
        self.special_immunization_table.clearContents()
        self.special_immunization_table.setRowCount(len(immunization_data))
        for row, immunization in enumerate(immunization_data):
            self.special_immunization_table.setItem(row, 0, QTableWidgetItem(immunization.product))
            self.special_immunization_table.setCellWidget(
                row, 1, self.get_result_combobox(immunization.operation_type)
            )
            self.special_immunization_table.setItem(row, 2, QTableWidgetItem(immunization.illness))
            self.special_immunization_table.setItem(row, 3, QTableWidgetItem(immunization.operation_date))
            self.special_immunization_table.setItem(row, 4, QTableWidgetItem(immunization.vaccine_name))
            self.special_immunization_table.setItem(row, 5, QTableWidgetItem(immunization.vaccine_serial))
            self.special_immunization_table.setItem(row, 6, QTableWidgetItem(immunization.vaccine_date_to))
            self.special_immunization_table.setCellWidget(
                row, 7, self.get_delete_button(self.special_immunization_table)
            )

    @staticmethod
    def main_immunization_table_columns():
        return ["тип", "наименование болезни", "дата проведения иммунизации/обработки",
                "название и производитель препарата", "номер серии препарата", "действие до", "X"]

    @staticmethod
    def special_immunization_table_columns():
        return ["наименование из справочника", "тип", "наименование болезни", "дата проведения иммунизации",
                "название и производитель препарата", "номер серии препарата", "действие до", "X"]
