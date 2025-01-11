from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import mapped_column

from base_lib.infra.db.mysql_database import Base


class Timezones(Base):
    __tablename__ = "Timezones"

    timezoneID: int = mapped_column(Integer, primary_key=True, autoincrement=True)
    timezone: str = mapped_column(String(50), nullable=False)

    def __str__(self):
        return self.timezone
