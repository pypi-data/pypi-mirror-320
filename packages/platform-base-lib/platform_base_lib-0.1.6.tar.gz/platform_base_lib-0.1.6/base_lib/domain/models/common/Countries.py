from sqlalchemy import Column, Integer, String
from base_lib.infra.db.mysql_database import Base


class Country(Base):
    __tablename__ = "Countries"

    countryID = Column(Integer, primary_key=True, autoincrement=True)
    countryName = Column(String(100), nullable=False)

    def __str__(self):
        return self.countryName
