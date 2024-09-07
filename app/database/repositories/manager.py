from app.database.postgres import SessionLocal
from app.database.repositories.enterprise import EnterpriseRepository
from app.database.repositories.exclude_products import ExcludeProductsRepository
from app.database.repositories.immunization import ImmunizationRepository
from app.database.repositories.research import ResearchRepository
from app.database.repositories.vetis_user import UserRepository


class RepositoryManager:
    vetis_user: UserRepository
    enterprise: EnterpriseRepository
    research: ResearchRepository
    immunization: ImmunizationRepository
    exclude_products: ExcludeProductsRepository

    def __init__(self):
        self.session = None

    def __enter__(self):
        self.session = SessionLocal()
        self.vetis_user = UserRepository(self.session)
        self.enterprise = EnterpriseRepository(self.session)
        self.research = ResearchRepository(self.session)
        self.immunization = ImmunizationRepository(self.session)
        self.exclude_products = ExcludeProductsRepository(self.session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.session.commit()
        else:
            self.session.rollback()
        self.session.close()
