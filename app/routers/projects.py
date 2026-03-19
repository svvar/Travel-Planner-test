from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from .. import crud, schemas, database, auth
from ..services import check_place_exists

router = APIRouter(
    prefix="/projects",
    tags=["projects"],
    dependencies=[Depends(auth.get_current_username)]
)

@router.post("/", response_model=schemas.Project)
async def create_project(project: schemas.ProjectCreate, db: AsyncSession = Depends(database.get_db)):
    if project.places:
        external_ids = set()
        for p in project.places:
            if p.external_id in external_ids:
                raise HTTPException(status_code=400, detail="Duplicate external_id in request")
            external_ids.add(p.external_id)
            
            exists = await check_place_exists(p.external_id)
            if not exists:
                raise HTTPException(status_code=400, detail=f"Place with external_id {p.external_id} not found in external API")
                
    db_project = await crud.create_project(db=db, project=project)
    db_project.is_completed = crud.is_project_completed(db_project)
    return db_project

@router.get("/", response_model=List[schemas.ProjectWithPlaces])
async def read_projects(
    skip: int = Query(0, ge=0), 
    limit: int = Query(10, ge=1, le=100), 
    name: Optional[str] = None,
    db: AsyncSession = Depends(database.get_db)
):
    stmt = select(crud.models.Project).options(selectinload(crud.models.Project.places))
    if name:
        stmt = stmt.filter(crud.models.Project.name.ilike(f"%{name}%"))
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    db_projects = result.scalars().all()
    
    for p in db_projects:
        p.is_completed = crud.is_project_completed(p)
        
    return db_projects

@router.get("/{project_id}", response_model=schemas.ProjectWithPlaces)
async def read_project(project_id: int, db: AsyncSession = Depends(database.get_db)):
    db_project = await crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    db_project.is_completed = crud.is_project_completed(db_project)
    return db_project

@router.put("/{project_id}", response_model=schemas.Project)
async def update_project(project_id: int, project: schemas.ProjectUpdate, db: AsyncSession = Depends(database.get_db)):
    db_project = await crud.update_project(db, project_id=project_id, project_update=project)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    db_project.is_completed = crud.is_project_completed(db_project)
    return db_project

@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: int, db: AsyncSession = Depends(database.get_db)):
    db_project = await crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
        
    if db_project.places:
        for p in db_project.places:
            if p.is_visited:
                raise HTTPException(status_code=400, detail="Cannot delete project containing visited places")
            
    await crud.delete_project(db, project_id=project_id)
    return None
