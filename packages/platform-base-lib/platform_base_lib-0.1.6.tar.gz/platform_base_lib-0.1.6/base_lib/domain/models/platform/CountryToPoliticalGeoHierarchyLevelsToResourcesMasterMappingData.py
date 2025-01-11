from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from base_lib.domain.models.platform.CountryToPoliticalGeoHierarchyLevelsMapping import (
    CountryToPoliticalGeoHierarchyLevelMapping,
)
from base_lib.infra.db.mysql_database import Base


class CountryToPoliticalGeoHierarchyLevelsToResourcesMasterMappingData(Base):
    __tablename__ = "CountryToPoliticalGeoHierarchyLevelsToResourcesMasterMappingData"

    geoResourceID = Column(Integer, primary_key=True, autoincrement=True)
    countryToPoliticalGeoHierarchyLevelMappingId = Column(
        Integer,
        ForeignKey(
            "CountryToPoliticalGeoHierarchyLevelsMapping.country_to_political_geo_hierarchy_level_mapping_id"
        ),
        nullable=False,
    )
    name = Column(String(100), nullable=False)
    nameCaption = Column(String(100), nullable=True)
    nameCaptionUI = Column(String(100), nullable=True)
    codeIfAny = Column(String(20), nullable=True)
    parentGeoResourceId = Column(
        Integer,
        ForeignKey(
            "CountryToPoliticalGeoHierarchyLevelsToResourcesMasterMappingData.geo_resource_id"
        ),
        nullable=True,
    )

    # Relationships
    mapping: Mapped["CountryToPoliticalGeoHierarchyLevelMapping"] = relationship(
        "CountryToPoliticalGeoHierarchyLevelMapping"
    )
    parent: Mapped[
        "CountryToPoliticalGeoHierarchyLevelsToResourcesMasterMappingData"
    ] = relationship(
        "CountryToPoliticalGeoHierarchyLevelsToResourcesMasterMappingData",
        remote_side=[geoResourceID],
        backref="children",
    )

    def __str__(self):
        return self.name
