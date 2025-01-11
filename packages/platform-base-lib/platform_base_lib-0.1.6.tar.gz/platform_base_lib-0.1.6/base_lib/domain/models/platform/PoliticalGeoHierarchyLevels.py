from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship, Mapped
from base_lib.infra.db.mysql_database import Base


class PoliticalGeoHierarchyLevel(Base):
    __tablename__ = "PoliticalGeoHierarchyLevels"

    politicalGeoHierarchyLevelID = Column(Integer, primary_key=True, autoincrement=True)
    politicalGeoHierarchyLevelName = Column(String(50), nullable=False)
    politicalGeoHierarchyLevelNameCaption = Column(String(100), nullable=True)
    politicalGeoHierarchyLevelNameCaptionUI = Column(String(100), nullable=True)
    parentPoliticalGeoHierarchyLeveLevelId = Column(
        Integer,
        ForeignKey("PoliticalGeoHierarchyLevels.political_geo_hierarchy_level_id"),
        nullable=True,
    )
    isLeaf = Column(Boolean, nullable=False, default=False)
    isRoot = Column(Boolean, nullable=False, default=False)

    # Self-referential relationship
    parent: Mapped["PoliticalGeoHierarchyLevel"] = relationship(
        "PoliticalGeoHierarchyLevel",
        remote_side=[politicalGeoHierarchyLevelID],
        backref="children",
    )

    def __str__(self):
        return self.politicalGeoHierarchyLevelName
