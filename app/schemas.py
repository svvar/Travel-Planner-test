from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import date

class PlaceBase(BaseModel):
    external_id: int
    notes: Optional[str] = None
    is_visited: bool = False

class PlaceCreate(BaseModel):
    external_id: int
    notes: Optional[str] = None

class PlaceUpdate(BaseModel):
    notes: Optional[str] = None
    is_visited: Optional[bool] = None

class Place(PlaceBase):
    id: int
    project_id: int
    
    model_config = ConfigDict(from_attributes=True)

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    start_date: Optional[date] = None

class ProjectCreate(ProjectBase):
    places: Optional[List[PlaceCreate]] = Field(default=None, max_length=10)

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    start_date: Optional[date] = None

class Project(ProjectBase):
    id: int
    is_completed: bool = False
    
    model_config = ConfigDict(from_attributes=True)

class ProjectWithPlaces(Project):
    places: List[Place] = []
