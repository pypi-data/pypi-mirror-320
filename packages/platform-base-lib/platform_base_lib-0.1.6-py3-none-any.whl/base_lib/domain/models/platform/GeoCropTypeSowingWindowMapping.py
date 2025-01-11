from sqlalchemy import Column, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship, Mapped

from base_lib.domain.models.platform.CountryToPoliticalGeoHierarchyLevelsToResourcesMasterMappingData import (
    CountryToPoliticalGeoHierarchyLevelsToResourcesMasterMappingData,
)
from base_lib.infra.db.mysql_database import Base


class GeoCropTypeSowingWindowMapping(Base):
    __tablename__ = "GeoCropTypeSowingWindowMapping"

    uniqueId = Column(Integer, primary_key=True, autoincrement=True)
    geoResourceID = Column(
        Integer,
        ForeignKey(
            "CountryToPoliticalGeoHierarchyLevelsToResourcesMasterMappingData.geo_resource_id"
        ),
        nullable=False,
    )
    sowingStart = Column(Date, nullable=False)
    sowingEnd = Column(Date, nullable=False)
    deltaNoOfDays = Column(Integer, nullable=True)
    # crop_id = Column(Integer, ForeignKey('Crops.crop_id'), nullable=False)

    # Relationships
    geo_resource: Mapped[
        "CountryToPoliticalGeoHierarchyLevelsToResourcesMasterMappingData"
    ] = relationship("CountryToPoliticalGeoHierarchyLevelsToResourcesMasterMappingData")
    # crop = relationship("Crop")

    def __str__(self):
        return f"Sowing Window for Resource {self.geoResourceID}"
