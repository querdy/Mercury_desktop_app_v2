from typing import Sequence

from PyQt6.QtCore import QThreadPool
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from loguru import logger

from app.database.repositories.manager import RepositoryManager
from app.gui.widgets.events_adder_widget import EventsAdderWidget
from app.gui.widgets.text_info_widget import TextInfoWindow
from app.schema.immunization import ImmunizationSchema
from app.schema.research import ResearchSchema
from app.threads import FWorker
from app.vetis.mercury import Mercury


class EventsAdderTab(QWidget):
    def __init__(self, ):
        super().__init__()

        layout = QVBoxLayout()

        self.adder = EventsAdderWidget()
        self.text_info = TextInfoWindow()

        layout.addWidget(self.adder)
        layout.addWidget(self.text_info)
        self.setLayout(layout)

        self.adder.button.clicked.connect(self.add_events_button_clicked)

    def add_events_button_clicked(self):
        self.adder.button.setEnabled(False)
        self.adder.checkbox.setEnabled(False)
        self.adder.transaction_pk_input.setEnabled(False)
        self.adder.traffic_pk_input.setEnabled(False)
        self.adder.combobox.setEnabled(False)
        enterprise_uuid = self.adder.combobox.currentData()
        traffic_pk = self.adder.traffic_pk_input.text().strip()
        transaction_pk = self.adder.transaction_pk_input.text().strip()
        worker = FWorker(self.add_events, enterprise_uuid, traffic_pk, transaction_pk)
        worker.signals.finished.connect(lambda: self.adder.button.setEnabled(True))
        worker.signals.finished.connect(lambda: self.adder.checkbox.setEnabled(True))
        worker.signals.finished.connect(lambda: self.adder.transaction_pk_input.setEnabled(True))
        worker.signals.finished.connect(lambda: self.adder.traffic_pk_input.setEnabled(True))
        worker.signals.finished.connect(lambda: self.adder.combobox.setEnabled(True))
        worker.signals.finished.connect(lambda: self.text_info.remove_logger())
        QThreadPool().globalInstance().start(worker)
        self.text_info.add_logger()

    def get_research_for_product(
            self,
            product: str,
            base_research: Sequence[ResearchSchema],
            exclude_products: set[str],
            enterprise_uuid: str
    ) -> list[ResearchSchema]:
            research_for_product = []
            with RepositoryManager() as repo:
                special_research = repo.research.get_special_for_product_by_enterprise_uuid(enterprise_uuid, product)
            research_for_product.extend(special_research)
            if not research_for_product and product not in exclude_products:
                research_for_product.extend(base_research)
            elif self.adder.checkbox.isChecked() and product not in exclude_products:
                research_for_product.extend(base_research)
            return research_for_product

    def get_immunization_for_product(
            self,
            product: str,
            base_immunization: Sequence[ImmunizationSchema],
            enterprise_uuid: str
    ) -> list[ImmunizationSchema]:
        immunization_for_product = []
        with RepositoryManager() as repo:
            special_immunization = repo.immunization.get_special_for_product_by_enterprise_uuid(
                enterprise_uuid, product
            )
        immunization_for_product.extend(special_immunization)
        if not immunization_for_product or self.adder.checkbox.isChecked():
            immunization_for_product.extend(base_immunization)
        return immunization_for_product

    def add_events(self, enterprise_uuid: str, traffic_pk: str = "", transaction_pk: str = ""):
        try:
            if enterprise_uuid is None:
                logger.warning('Не указано предприятие для внесения ветеринарных мероприятий')
                return
            if all([bool(traffic_pk), bool(transaction_pk)]):
                logger.warning(f"Необходимо указать что-то одно: номер транзакции или номер записи журнала")
                return
            with RepositoryManager() as repo:
                user = repo.vetis_user.receive()
                enterprise = repo.enterprise.get(enterprise_uuid)
                base_research = repo.research.get_base_by_enterprise_uuid(enterprise_uuid)
                exclude_products = repo.exclude_products.get_by_enterprise_uuid(enterprise_uuid)
                base_immunization = repo.immunization.get_base_by_enterprise_uuid(enterprise_uuid)
            if user is None:
                logger.warning(f"Не указан пользователь меркурия для авторизации")
                return
            mercury = Mercury(login=user.login, password=user.password)
            if not mercury.is_auth:
                return
            mercury.choose_enterprise(enterprise_pk=enterprise.pk)
            created_products = mercury.get_created_products(transaction_pk, traffic_pk)
            for traffic_pk, product in created_products.items():
                real_traffic_pk = mercury.get_real_traffic_pk(traffic_pk)
                immunization_for_product = self.get_immunization_for_product(
                    product, base_immunization, enterprise_uuid)
                research_for_product = self.get_research_for_product(
                    product, base_research, {item.product for item in exclude_products}, enterprise_uuid)
                if immunization_for_product:
                    if mercury.is_traffic_enabled_for_immunization(real_traffic_pk):
                        available_immunization = mercury.get_available_immunization(real_traffic_pk)
                        for immunization in immunization_for_product:
                            if immunization in available_immunization:
                                logger.info(f"Продукт: {product} - иммунизация {immunization.illness} "
                                            f"- <b>уже было добавлено</b>")
                                continue
                            if immunization_added := mercury.push_immunization(real_traffic_pk, immunization):
                                logger.info(
                                    f"Продукт: {product} - иммунизация {immunization.illness} - <b>добавлено</b>")
                            else:
                                logger.info(
                                    f"Продукт: {product} - иммунизация {immunization.illness} - <b>не удалось добавить</b>")
                    else:
                        logger.info(f'Запись {product} - <b>невозможно добавить иммунизацию</b>. '
                                    f'Вероятно, запись журнала - не живое животное')

                if mercury.is_traffic_enabled_for_lab(real_traffic_pk):
                    if not research_for_product:
                        logger.info(f"Продукт: {product} - <b>не указаны лабораторные исследования</b>")
                    available_research = mercury.get_available_research(real_traffic_pk)
                    for research in research_for_product:
                        if research in available_research:
                            logger.info(f"Продукт: {product} - исследование {research.disease} "
                                        f"- <b>уже было добавлено</b>")
                            continue
                        if research_added := mercury.push_research(traffic_pk, research):
                            logger.info(f"Продукт: {product} - исследование {research.disease} - <b>добавлено</b>")
                else:
                    logger.info(f'Продукт: {product} - <b>запись не активна</b>')
            self.text_info.write("--------------------------------------------------")
        except Exception as e:
            print(e)
