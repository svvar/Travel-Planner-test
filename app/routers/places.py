from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from .. import crud, schemas, database, auth
from ..services import check_place_exists

router = APIRouter(
    prefix="/projects/{project_id}/places",
    tags=["places"],
    dependencies=[Depends(auth.get_current_username)]
)

@router.post("/", response_model=schemas.Place)
async def create_place_for_project(
    project_id: int, place: schemas.PlaceCreate, db: AsyncSession = Depends(database.get_db)
):
    db_project = await crud.get_project(db, project_id=project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    count = await crud.count_places_in_project(db, project_id=project_id)
    if count >= 10:
        raise HTTPException(status_code=400, detail="Project already has maximum number of places (10)")
        
    existing_place = await crud.get_place_by_external_id(db, project_id=project_id, external_id=place.external_id)
    if existing_place:
        raise HTTPException(status_code=400, detail="Place already exists in this project")
        
    exists = await check_place_exists(place.external_id)
    if not exists:
        raise HTTPException(status_code=400, detail="Place not found in external API")
        
    return await crud.create_place(db=db, project_id=project_id, place=place)

@router.get("/", response_model=List[schemas.Place])
async def read_places(
    project_id: int, skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100), db: AsyncSession = Depends(database.get_db)
):
    db_project = await crud.get_project(db, project_id=project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return await crud.get_places(db, project_id=project_id, skip=skip, limit=limit)

@router.get("/{place_id}", response_model=schemas.Place)
async def read_place(project_id: int, place_id: int, db: AsyncSession = Depends(database.get_db)):
    db_place = await crud.get_place(db, place_id=place_id, project_id=project_id)
    if db_place is None:
        raise HTTPException(status_code=404, detail="Place not found in project")
    return db_place

@router.put("/{place_id}", response_model=schemas.Place)
async def update_place_for_project(
    project_id: int, place_id: int, place: schemas.PlaceUpdate, db: AsyncSession = Depends(database.get_db)
):
    db_place = await crud.update_place(db, place_id=place_id, project_id=project_id, place_update=place)
    if db_place is None:
        raise HTTPException(status_code=404, detail="Place not found in project")
    return db_place
