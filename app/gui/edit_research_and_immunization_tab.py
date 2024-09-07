from PyQt6.QtCore import Qt, QThreadPool
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLayout
from loguru import logger

from app.database.repositories.manager import RepositoryManager
from app.gui.signals import SaveResearchAndImmunizationButtonSignals
from app.gui.widgets.download_research_and_immunization_widget import DownloadResearchAndImmunizationWidget
from app.gui.widgets.edit_enterprise_widget import EditEnterpriseWidget
from app.gui.widgets.some_table_widget import ResearchTables, ImmunizationTables
from app.gui.widgets.save_research_and_immunization_widget import SaveResearchAndImmunizationWidget
from app.schema.immunization import ImmunizationSchema
from app.schema.research import ResearchSchema
from app.threads import FWorker
from app.vetis.mercury import Mercury


class EditResearchAndImmunizationTab(QWidget):
    def __init__(self, ):
        super().__init__()

        self.save_button = SaveResearchAndImmunizationWidget()
        self.edit_enterprise = EditEnterpriseWidget()
        self.download_research = DownloadResearchAndImmunizationWidget()
        self.research_tables = ResearchTables()
        self.immunization_tables = ImmunizationTables()

        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        buttons_layout = QHBoxLayout()
        # buttons_layout.setContentsMargins(10, 0, 10, 0)
        main_layout.addLayout(buttons_layout)

        tab_widget = QTabWidget()
        tab_widget.addTab(self.research_tables, "Лабораторные исследование")
        tab_widget.addTab(self.immunization_tables, "Иммунизации/обработки")

        main_layout.addWidget(tab_widget)

        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.edit_enterprise)
        buttons_layout.addWidget(self.download_research)
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        buttons_layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)

        self.setLayout(main_layout)

        SaveResearchAndImmunizationButtonSignals().btn_clicked.connect(self.save_button_clicked)
        self.edit_enterprise.combobox.currentIndexChanged.connect(self.load_research_data)
        self.edit_enterprise.combobox.currentIndexChanged.connect(self.load_immunization_data)
        self.download_research.dialog.download_button.clicked.connect(self.download_button_clicked)
        self.load_research_data()
        self.load_immunization_data()

    def save_button_clicked(self):
        self.save_research()
        self.save_immunization()

    def save_research(self):
        current_base_research = self.research_tables.get_base()
        current_special_research = self.research_tables.get_special()
        current_research = current_base_research + current_special_research
        current_exclude_products = self.research_tables.get_exclude_products()
        with RepositoryManager() as repo:
            created_researches = repo.research.update(
                self.edit_enterprise.combobox.currentData(), current_research
            )
            created_exclude_products = repo.exclude_products.update(
                self.edit_enterprise.combobox.currentData(), current_exclude_products
            )
        created_base_research = []
        created_special_research = []
        for research in created_researches:
            if research.product is None:
                created_base_research.append(research)
            else:
                created_special_research.append(research)
        self.research_tables.fill_main_table(created_base_research)
        self.research_tables.fill_special_table(created_special_research)
        self.research_tables.fill_exclude_product_table(created_exclude_products)

    def save_immunization(self):
        try:
            current_base_immunization = self.immunization_tables.get_base()
            current_special_immunization = self.immunization_tables.get_special()
            current_immunization = current_base_immunization + current_special_immunization
            with RepositoryManager() as repo:
                created_immunization = repo.immunization.update(
                    self.edit_enterprise.combobox.currentData(), current_immunization
                )
            created_base_immunization = []
            created_special_immunization = []
            for immunization in created_immunization:
                if immunization.product is None:
                    created_base_immunization.append(immunization)
                else:
                    created_special_immunization.append(immunization)
            self.immunization_tables.fill_main_table(created_base_immunization)
            self.immunization_tables.fill_special_table(created_special_immunization)
        except Exception as e:
            print(type(e), e)

    def load_research_data(self):
        current_enterprise_uuid = self.edit_enterprise.combobox.currentData()
        with RepositoryManager() as repo:
            base_research = repo.research.get_base_by_enterprise_uuid(current_enterprise_uuid)
            special_research = repo.research.get_special_by_enterprise_uuid(current_enterprise_uuid)
            exclude_products = repo.exclude_products.get_by_enterprise_uuid(current_enterprise_uuid)
        self.research_tables.fill_main_table(base_research)
        self.research_tables.fill_special_table(special_research)
        self.research_tables.fill_exclude_product_table(exclude_products)

    def load_immunization_data(self):
        current_enterprise_uuid = self.edit_enterprise.combobox.currentData()
        with RepositoryManager() as repo:
            base_immunization = repo.immunization.get_base_by_enterprise_uuid(current_enterprise_uuid)
            special_immunization = repo.immunization.get_special_by_enterprise_uuid(current_enterprise_uuid)
        self.immunization_tables.fill_main_table(base_immunization)
        self.immunization_tables.fill_special_table(special_immunization)

    def download_button_clicked(self):
        transaction_pk = self.download_research.dialog.transaction_pk_input.text().strip()
        traffic_pk = self.download_research.dialog.traffic_pk_input.text()
        enterprise_uuid = self.edit_enterprise.combobox.currentData()
        if transaction_pk or traffic_pk:
            self.download_research.download_button.setEnabled(False)
            worker = FWorker(self.download, enterprise_uuid, transaction_pk=transaction_pk, traffic_pk=traffic_pk)
            worker.signals.finished.connect(lambda: self.download_research.download_button.setEnabled(True))
            worker.signals.result.connect(self.fill_tables_after_download)
            QThreadPool().globalInstance().start(worker)
            self.download_research.dialog.transaction_pk_input.setText("")
            self.download_research.dialog.traffic_pk_input.setText("")
            self.download_research.dialog.accept()

    def download(self, enterprise_uuid: str, transaction_pk: str = "", traffic_pk: str = ""):
        try:
            with RepositoryManager() as repo:
                user = repo.vetis_user.receive()
                enterprise = repo.enterprise.get(enterprise_uuid)
            mercury = Mercury(login=user.login, password=user.password)
            if not mercury.is_auth:
                return
            mercury.choose_enterprise(enterprise.pk)
            created_products = mercury.get_created_products(transaction_pk, traffic_pk)
            available_research = []
            available_immunization = []
            for traffic_pk, product in created_products.items():
                try:
                    available_research.extend([
                        ResearchSchema(product=product, **research.model_dump(exclude_none=True))
                        for research in mercury.get_available_research(traffic_pk)
                    ])
                    available_immunization.extend([
                        ImmunizationSchema(product=product, **immunization.model_dump(exclude_none=True))
                        for immunization in mercury.get_available_immunization(traffic_pk)
                    ])
                except AttributeError:
                    continue
            available_research.extend(self.research_tables.get_special())
            available_immunization.extend(self.immunization_tables.get_special())
            return {
                "research": list(dict.fromkeys(available_research)),
                "immunization": list(dict.fromkeys(available_immunization))
            }
        except Exception as e:
            logger.error(f"{type(e)} {e}")

    def fill_tables_after_download(self, data: dict):
        self.research_tables.fill_special_table(data["research"])
        self.immunization_tables.fill_special_table(data["immunization"])
