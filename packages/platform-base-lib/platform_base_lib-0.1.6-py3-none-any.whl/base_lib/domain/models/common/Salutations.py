from base_lib.infra.db.mysql_database import Base
from sqlalchemy import Column, Integer, String


class Salutations(Base):
    __tablename__ = "Salutations"

    prefixId = Column(Integer, primary_key=True, autoincrement=True)
    prefixName = Column(String(50), nullable=False)
    prefixNameCaption = Column(String(50), nullable=True)
    prefixNameCaptionUI = Column(String(50), nullable=True)

    def __str__(self):
        return self.prefixName
