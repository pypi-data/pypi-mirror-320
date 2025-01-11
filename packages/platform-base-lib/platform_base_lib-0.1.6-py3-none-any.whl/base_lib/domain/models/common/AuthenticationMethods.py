from sqlalchemy import Column, Integer, String
from base_lib.infra.db.mysql_database import Base


class AuthenticationMethod(Base):
    __tablename__ = "AuthenticationMethods"

    authenticationMethodID = Column(Integer, primary_key=True, autoincrement=True)
    authenticationMethodName = Column(String(50), nullable=False)
    authenticationMethodCaption = Column(String(100), nullable=True)
    authenticationMethodCaptionUI = Column(String(100), nullable=True)

    def __str__(self):
        return self.authenticationMethodName
