from sqlalchemy import Column, Integer, String
from base_lib.infra.db.mysql_database import Base


class Genders(Base):
    __tablename__ = "Genders"

    genderId = Column(Integer, primary_key=True, autoincrement=True)
    genderName = Column(String(50), nullable=False)
    genderNameCaption = Column(String(100), nullable=True)
    genderNameCaptionUI = Column(String(100), nullable=True)

    def __str__(self):
        return self.genderName
