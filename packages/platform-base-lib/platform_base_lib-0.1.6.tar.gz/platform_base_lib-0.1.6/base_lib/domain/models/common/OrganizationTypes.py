from sqlalchemy import Column, Integer, String
from base_lib.infra.db.mysql_database import Base


class OrganizationType(Base):
    __tablename__ = "OrganisationTypes"

    organisationTypeID = Column(Integer, primary_key=True, autoincrement=True)
    organisationTypeName = Column(String(50), nullable=False)
    organisationTypeNameCaption = Column(String(100), nullable=True)
    organisationTypeNameCaptionUI = Column(String(100), nullable=True)

    def __str__(self):
        return self.organisationTypeName
