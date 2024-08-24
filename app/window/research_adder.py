from PyQt6.QtCore import Qt, QThreadPool
from PyQt6.QtWidgets import QWidget, QStatusBar, QGridLayout, QPushButton, QLineEdit, QComboBox, QGroupBox, QCheckBox, \
    QLabel
from loguru import logger
from sqlalchemy.orm import Session

from app.database.crud.enterprise import get_all_enterprise, get_enterprise_by_uuid
from app.database.crud.immunization import get_base_immunization_by_enterprise_uuid, \
    get_special_immunization_for_product
from app.database.crud.research import get_base_research_by_enterprise_uuid, \
    get_exclude_products_by_enterprise_uuid, get_special_research_for_product
from app.database.crud.user import get_user
from app.schema.immunization import ImmunizationSchema, SpecialImmunizationSchema
from app.schema.research import ResearchSchema, SpecialResearchSchema
from app.signals import MainSignals
from app.threads.base import Worker
from app.vetis.mercury import Mercury
from app.window.log_window import LogWindow


class ResearchAdder(QWidget):
    def __init__(self, status_bar: QStatusBar, db_session: Session, signals: MainSignals, parent=None):
        super().__init__(parent)
        self.status_bar = status_bar
        self.db_session = db_session
        self.thread_pool = QThreadPool()
        self.signals = signals
        self.signals.enterprise_changed.connect(self.load_enterprises)

        self.log_window = LogWindow()

        self.init_ui()

    def init_ui(self):
        self.layout = QGridLayout()
        self.layout.setVerticalSpacing(10)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.layout)

        self.init_adder_frame()
        self.init_log_window()

    def init_log_window(self):
        self.layout.addWidget(self.log_window, 1, 0, 1, 1)

    def init_adder_frame(self):
        self.api_frame = QGroupBox("Добавить лабораторные исследования")
        self.frame_layout = QGridLayout()

        self.traffic_label = self.create_label("Запись журнала:", 0, 0)
        self.traffic_pk_line_edit = self.create_line_edit(0, 1, 150)
        self.transaction_label = self.create_label("Транзакция:", 0, 2)
        self.transaction_pk_line_edit = self.create_line_edit(0, 3, 150)
        self.start_button = self.create_button("Начать", self.start_button_clicked, 0, 5, 1, 1)
        self.all_lab_checkbox = self.create_checkbox("Вносить базовые исследования даже если есть специальные",
                                                     0, 6, 1, 2)

        self.api_frame.setLayout(self.frame_layout)
        self.layout.addWidget(self.api_frame, 0, 0, 1, 2)

    def create_label(self, text: str, row, col, rowspan=1, colspan=1):
        label = QLabel()
        label.setText(text)
        label.setMaximumWidth(75)
        self.frame_layout.addWidget(label, row, col, rowspan, colspan)
        return label

    def create_checkbox(self, message, row, col, rowspan=1, colspan=1):
        checkbox = QCheckBox(message)
        self.frame_layout.addWidget(checkbox, row, col, rowspan, colspan)
        return checkbox

    def create_button(self, text, callback, row, col, rowspan=1, colspan=1):
        button = QPushButton(text)
        button.setMaximumWidth(100)
        button.clicked.connect(callback)
        self.frame_layout.addWidget(button, row, col, rowspan, colspan)
        return button

    def create_line_edit(self, row, col, max_width):
        line_edit = QLineEdit()
        line_edit.setMaximumWidth(max_width)
        self.frame_layout.addWidget(line_edit, row, col, 1, 1)
        return line_edit

    def start_button_clicked(self):
        self.start_button.setEnabled(False)
        self.all_lab_checkbox.setEnabled(False)
        self.transaction_pk_line_edit.setEnabled(False)
        self.traffic_pk_line_edit.setEnabled(False)
        self.enterprise_combobox.setEnabled(False)
        worker = Worker(self.research_adder)
        worker.signals.finished.connect(lambda: self.start_button.setEnabled(True))
        worker.signals.finished.connect(lambda: self.all_lab_checkbox.setEnabled(True))
        worker.signals.finished.connect(lambda: self.transaction_pk_line_edit.setEnabled(True))
        worker.signals.finished.connect(lambda: self.traffic_pk_line_edit.setEnabled(True))
        worker.signals.finished.connect(lambda: self.enterprise_combobox.setEnabled(True))
        worker.signals.finished.connect(lambda: self.log_window.remove_logger())
        self.thread_pool.start(worker)
        self.log_window.add_logger()

    def research_adder(self):
        current_enterprise_uuid = self.enterprise_combobox.currentData()
        transaction_pk = self.transaction_pk_line_edit.text().strip()
        traffic_pk = self.traffic_pk_line_edit.text().strip()
        if all([bool(traffic_pk), bool(transaction_pk)]):
            logger.warning(f"Необходимо указать что-то одно: номер транзакции или номер записи журнала")
            return
        try:
            user = get_user(db=self.db_session)
            if user is None:
                logger.warning(f"Не указан пользователь меркурия для авторизации")
                return
            mercury = Mercury(login=user.login, password=user.password)
            if not mercury.is_auth:
                return

            enterprise = get_enterprise_by_uuid(db=self.db_session, enterprise_uuid=current_enterprise_uuid)
            mercury.choose_enterprise(enterprise_pk=enterprise.pk)

            base_research = get_base_research_by_enterprise_uuid(self.db_session, current_enterprise_uuid)
            base_research = [ResearchSchema.from_orm(item) for item in base_research]

            exclude_products = get_exclude_products_by_enterprise_uuid(self.db_session, current_enterprise_uuid)
            exclude_products = {item.product for item in exclude_products}

            base_immunization = get_base_immunization_by_enterprise_uuid(self.db_session, current_enterprise_uuid)
            base_immunization = [ImmunizationSchema.from_orm(item) for item in base_immunization]

            created_products = {}
            if transaction_pk:
                created_products = mercury.get_products(transaction_pk=transaction_pk)
                if not created_products:
                    created_products = mercury.get_products_in_incomplete_transaction(transaction_pk=transaction_pk)
                    if created_products:
                        logger.info("Получена продукция из транзакции незавершенного производства")
                    else:
                        logger.warning("Не удалось обнаружить выработанную продукцию. "
                                       "Возможно, номер транзакции указан неверно")
                else:
                    logger.info("Получена продукция из обычной транзакции")
            elif traffic_pk:
                try:
                    created_products = {traffic_pk: mercury.get_product_name_from_traffic(traffic_pk)}
                except AttributeError:
                    logger.warning("Не удалось обнаружить выработанную продукцию. "
                                   "Возможно, номер записи журнала указан неверно")
            else:
                logger.warning(f"Не указан номер транзакции или номер записи журнала")
            for traffic_pk, product in created_products.items():
                real_traffic_pk = mercury.get_real_traffic_pk(traffic_pk)
                immunization_for_product = self.get_immunization_for_product(
                    product, base_immunization, current_enterprise_uuid)
                if immunization_for_product:
                    if mercury.is_traffic_enabled_for_immunization(real_traffic_pk):
                        available_immunization_for_product = mercury.get_available_immunization(real_traffic_pk)
                        for immunization in immunization_for_product:
                            if immunization in available_immunization_for_product:
                                logger.info(f"Продукт: {product} - иммунизация {immunization.illness} "
                                            f"- <b>уже было добавлено</b>")
                                continue
                            if immunization_added := mercury.push_immunization(real_traffic_pk, immunization):
                                logger.info(
                                    f"Продукт: {product} - иммунизация {immunization.illness} - <b>добавлено</b>")
                    else:
                        logger.info(f'Запись {product} - <b>невозможно добавить иммунизацию</b>. '
                                    f'Вероятно, запись журнала - не живое животное')

                if mercury.is_traffic_enabled_for_lab(real_traffic_pk):
                    research_for_product = self.get_research_for_product(
                        product, base_research, exclude_products, current_enterprise_uuid
                    )
                    if research_for_product:
                        available_research = mercury.get_available_research(real_traffic_pk)
                        for research in research_for_product:
                            if research in available_research:
                                logger.info(f"Продукт: {product} - исследование {research.disease} "
                                            f"- <b>уже было добавлено</b>")
                                continue
                            if research_added := mercury.push_research(traffic_pk, research):
                                logger.info(f"Продукт: {product} - исследование {research.disease} - <b>добавлено</b>")
                    else:
                        logger.info(f"Продукт: {product} - <b>не указаны лабораторные исследования</b>")
                else:
                    logger.info(f'Продукт: {product} - <b>запись не активна</b>')
                self.log_window.write("--------------------------------------------------")

        except Exception as e:
            logger.error(f"{type(e)} {e}")

    def get_research_for_product(
            self,
            product: str,
            base_research: list[ResearchSchema],
            exclude_products: set[str],
            enterprise_uuid: str
    ) -> list[ResearchSchema]:
        research_for_product = []
        special_research = get_special_research_for_product(self.db_session, enterprise_uuid, product)
        special_research = [SpecialResearchSchema.from_orm(item) for item in special_research]
        research_for_product.extend(special_research)
        if not research_for_product and product not in exclude_products:
            research_for_product.extend(base_research)
        elif self.all_lab_checkbox.isChecked() and product not in exclude_products:
            research_for_product.extend(base_research)
        return research_for_product

    def get_immunization_for_product(
            self,
            product: str,
            base_immunization: list[ImmunizationSchema],
            enterprise_uuid: str
    ) -> list[ImmunizationSchema]:
        immunization_for_product = []
        special_immunization = get_special_immunization_for_product(self.db_session, enterprise_uuid, product)
        special_immunization = [SpecialImmunizationSchema.from_orm(item) for item in special_immunization]
        immunization_for_product.extend(special_immunization)
        if not immunization_for_product or self.all_lab_checkbox.isChecked():
            immunization_for_product.extend(base_immunization)
        return immunization_for_product

    def load_enterprises(self):
        enterprises = get_all_enterprise(db=self.db_session)
        self.enterprise_combobox = QComboBox()
        self.enterprise_combobox.setMaximumWidth(250)
        for item in enterprises:
            self.enterprise_combobox.addItem(item.name, item.uuid)
        self.frame_layout.addWidget(self.enterprise_combobox, 0, 4, 1, 1)
