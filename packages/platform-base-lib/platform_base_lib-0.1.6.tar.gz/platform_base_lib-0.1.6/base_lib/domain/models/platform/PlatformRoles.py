from sqlalchemy import Column, Integer, String
from base_lib.infra.db.mysql_database import Base


class PlatformRole(Base):
    __tablename__ = "PlatformRoles"

    platformRoleID = Column(Integer, primary_key=True, autoincrement=True)
    platformRoleName = Column(String(50), nullable=False)
    noOfUsersAllowed = Column(Integer, nullable=True)

    def __str__(self):
        return self.platformRoleName
