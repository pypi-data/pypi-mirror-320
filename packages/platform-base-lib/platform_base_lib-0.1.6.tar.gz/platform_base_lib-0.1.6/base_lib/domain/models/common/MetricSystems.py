from sqlalchemy import Column, Integer, String
from base_lib.infra.db.mysql_database import Base


class MetricSystem(Base):
    __tablename__ = "MetricSystems"

    metricSystemID = Column(Integer, primary_key=True, autoincrement=True)
    metricSystemName = Column(String(50), nullable=False)
    metricSystemNameCaption = Column(String(100), nullable=True)
    metricSystemNameCaptionUI = Column(String(100), nullable=True)

    def __str__(self):
        return self.metricSystemName
