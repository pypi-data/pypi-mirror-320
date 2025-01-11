from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from base_lib.domain.models.common.Countries import Country
from base_lib.domain.models.platform.PoliticalGeoHierarchyLevels import (
    PoliticalGeoHierarchyLevel,
)
from base_lib.infra.db.mysql_database import Base


class CountryToPoliticalGeoHierarchyLevelMapping(Base):
    __tablename__ = "CountryToPoliticalGeoHierarchyLevelsMapping"

    countryToPoliticalGeoHierarchyLevelMappingId = Column(
        Integer, primary_key=True, autoincrement=True
    )
    countryId = Column(Integer, ForeignKey("Countries.country_id"), nullable=False)
    politicalGeoHierarchyLevelId = Column(
        Integer,
        ForeignKey("PoliticalGeoHierarchyLevels.political_geo_hierarchy_level_id"),
        nullable=False,
    )
    countryPoliticalHierarchyName = Column(String(100), nullable=False)
    countryPoliticalHierarchyNameCaption = Column(String(100), nullable=True)
    countryPoliticalHierarchyNameCaptionUI = Column(String(100), nullable=True)
    countryPoliticalHierarchyNameCode = Column(String(20), nullable=True)

    # Relationships
    country: Mapped["Country"] = relationship("Country")
    political_geo_hierarchy_level: Mapped["PoliticalGeoHierarchyLevel"] = relationship(
        "PoliticalGeoHierarchyLevel"
    )

    def __str__(self):
        return self.countryPoliticalHierarchyName
