from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    start_date = Column(Date, nullable=True)

    places = relationship("Place", back_populates="project", cascade="all, delete-orphan")

class Place(Base):
    __tablename__ = "places"
    __table_args__ = (
        UniqueConstraint('project_id', 'external_id', name='uq_project_external_place'),
    )

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    external_id = Column(Integer, index=True, nullable=False) # Represents Art Institute API ID
    notes = Column(String, nullable=True)
    is_visited = Column(Boolean, default=False)

    project = relationship("Project", back_populates="places")
