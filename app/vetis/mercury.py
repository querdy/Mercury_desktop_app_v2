import re
from typing import Dict

import httpx
from bs4 import BeautifulSoup, Tag
from loguru import logger

from app.schema.research import ResearchSchema, SpecialResearchSchema
from app.vetis.base import BaseSession


class Mercury:
    def __init__(self, login: str, password: str):
        self.session = BaseSession()
        self.service_url = 'https://mercury.vetrf.ru/gve/operatorui'
        self.user = None
        self.is_auth = self.login(login, password)

    def auth(self, login: str, password: str) -> bool:
        try:
            response = self.session.fetch(self.service_url)
            soup = BeautifulSoup(response.text, 'html5lib')
            form = soup.find('form')
            fields = form.findAll('input')
            form_data = {field.get('name'): field.get('value') for field in fields if field.get('name') is not None}

            response = self.session.fetch(form['action'], data=form_data)
            form_data['j_username'] = login
            form_data['j_password'] = password
            form_data['_eventId_proceed'] = ''
            form_data['ksid'] = 'kekw'
            response = self.session.fetch(response.history[0].headers['Location'], data=form_data)

            soup = BeautifulSoup(response.text, 'html5lib')
            form = soup.find('form')
            fields = form.findAll('input')
            form_data = {field.get('name'): field.get('value') for field in fields if field.get('name') is not None}
            response = self.session.fetch(form['action'], data=form_data)
            soup = BeautifulSoup(response.text, 'html5lib')
            self.user = ' '.join((soup.find('div', {'id': 'loggedas'}).find('b')).text.split()[:-1])
            logger.info(f"Login successful: {self.user}")

            self.save_cookies()
            return True
        except (httpx.RequestError, ValueError):
            logger.error("Authorization failed. Check login and password")
            return False

    def check_cookies_validity(self) -> bool:
        try:
            self.read_cookies()
        except FileNotFoundError:
            logger.warning("No saved cookies found.")
            return False

        response = self.session.fetch(self.service_url)
        soup = BeautifulSoup(response.text, 'html5lib')
        if soup.find('div', {'id': 'loggedas'}):
            self.user = ' '.join(soup.find('div', {'id': 'loggedas'}).find('b').text.split()[:-1])
            logger.info(f"Cookies are valid for user: {self.user}")
            return True
        else:
            self.session.clear_cookies()
            logger.warning("Cookies are not valid. Cleared.")
            return False

    def login(self, login: str, password: str) -> bool:
        if not self.check_cookies_validity():
            return self.auth(login, password)
        return True  # Если куки прочитаны успешно или были успешно авторизованы

    def get_available_research(self, traffic_pk: str) -> tuple[ResearchSchema, ...]:
        research_result_mapper = {
            "положительный": "1",
            "отрицательный": "2",
            "не нормируется": "3"
        }
        data = {
            '_action': 'showRealTrafficVUForm',
            'trafficPk': traffic_pk
        }
        response = self.session.fetch(self.service_url, data=data)
        soup = BeautifulSoup(response.content, 'html5lib')
        research_table = soup.find(
            "h4", text=re.compile("Лабораторные исследования:")
        ).find_next("table").find_next("table")
        if research_table is None:
            return ()
        available_research = tuple(
            ResearchSchema(
                sampling_number=row[0].text,
                sampling_date=row[1].text,
                operator=row[2].text,
                method=row[5].text,
                disease=row[3].text,
                date_of_research=row[4].text,
                expertise_id=row[6].text,
                result=research_result_mapper[row[7].text],
                conclusion=row[8].text,
            )
            for research in research_table.find_all("tr", {'class': 'added'})
            if (row := research.find_all("td")) and research_result_mapper[row[7].text] != 0
        )
        return available_research

    def get_products(self, transaction_pk: str) -> Dict[str, str]:
        data = {
            '_action': 'showTransactionForm',
            'transactionPk': transaction_pk,
            'pageList': '1',
            'cancelAction': 'listTransaction',
            'anchor': ''
        }
        response = self.session.fetch(self.service_url, data=data)
        soup = BeautifulSoup(response.content, 'html5lib')

        all_products = soup.find_all('a')
        created_products = {}

        for product in all_products:
            product_link = product.get('href')
            if 'listProduced&stateMenu=2' in product_link:
                traffic_pk = product_link.split('&')[1].split('=')[1]
                raw_product_name = product.getText()
                product_name = raw_product_name[:raw_product_name.rfind('-')].strip()

                if product_name not in created_products:
                    created_products[product_name] = traffic_pk
                else:
                    created_products[f"{product_name}_{traffic_pk}"] = traffic_pk
        return created_products

    def get_products_in_incomplete_transaction(self, transaction_pk: str) -> Dict[str, str]:
        data = {
            '_action': 'listProduceOperationAjax',
            'transactionPk': transaction_pk,
        }
        response = self.session.fetch(self.service_url, data=data)
        soup = BeautifulSoup(response.content, 'html.parser')
        all_products = soup.find_all("tr")
        created_products = {}
        for product in all_products:
            try:
                traffic_pk = product.find("a").getText()
                product_name = product.find_all('td')[2].getText().strip()
                if created_products.get(product_name) is None:
                    created_products.update({product_name: traffic_pk})
                else:
                    created_products.update({f"{product_name}_{traffic_pk}": traffic_pk})
            except AttributeError:
                continue
        return created_products

    def get_mercury_username(self) -> str:
        url = 'https://mercury.vetrf.ru/gve/operatorui'
        mercury_page = self.session.fetch(url)
        soup = BeautifulSoup(mercury_page.content, 'html5lib')
        user_name = soup.find("div", {"id": "loggedas"}).find("b").getText().split('(')[0].strip()
        return user_name

    def push_research(self, traffic_pk: str, research: ResearchSchema):
        data = {
            'actNumber': research.sampling_number,
            'actDate': research.sampling_date,
            'laboratory': research.operator,
            'disease': research.disease,
            'researchDate': research.date_of_research,
            'method': research.method,
            'expertiseNumber': research.expertise_id,
            'result': research.result,
            'conclusion': research.conclusion,
            '_action': 'addLaboratoryForm',
            'realTrafficVUPk': traffic_pk
        }
        response = self.session.fetch(self.service_url, data=data)
        return response.status_code == 200

    def is_traffic_enabled(self, traffic_pk: str):
        data = {
            '_action': 'showTransactionForm',
            'trafficPk': traffic_pk
        }
        return self.session.fetch(self.service_url, data=data).status_code == 200

    def save_cookies(self) -> None:
        self.session.save_cookies()

    def read_cookies(self) -> None:
        self.session.read_cookies()

    def clear_cookies(self) -> None:
        self.session.clear_cookies()

    def close(self) -> None:
        self.session.close()
