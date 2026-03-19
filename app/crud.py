from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from . import models, schemas

async def get_project(db: AsyncSession, project_id: int):
    stmt = select(models.Project).options(selectinload(models.Project.places)).filter(models.Project.id == project_id)
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_projects(db: AsyncSession, skip: int = 0, limit: int = 10):
    stmt = select(models.Project).options(selectinload(models.Project.places)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_project(db: AsyncSession, project: schemas.ProjectCreate):
    db_project = models.Project(
        name=project.name,
        description=project.description,
        start_date=project.start_date
    )
    db.add(db_project)
    await db.flush()
    if project.places:
        for place in project.places:
            db_place = models.Place(
                project_id=db_project.id,
                external_id=place.external_id,
                notes=place.notes
            )
            db.add(db_place)
    await db.commit()
    return await get_project(db, db_project.id)

async def update_project(db: AsyncSession, project_id: int, project_update: schemas.ProjectUpdate):
    db_project = await get_project(db, project_id)
    if not db_project:
        return None
    
    update_data = project_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_project, key, value)
        
    await db.commit()
    return await get_project(db, project_id)

async def delete_project(db: AsyncSession, project_id: int):
    db_project = await get_project(db, project_id)
    if db_project:
        await db.delete(db_project)
        await db.commit()
    return True

async def get_places(db: AsyncSession, project_id: int, skip: int = 0, limit: int = 10):
    stmt = select(models.Place).filter(models.Place.project_id == project_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_place(db: AsyncSession, place_id: int, project_id: int):
    stmt = select(models.Place).filter(models.Place.id == place_id, models.Place.project_id == project_id)
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_place_by_external_id(db: AsyncSession, project_id: int, external_id: int):
    stmt = select(models.Place).filter(models.Place.project_id == project_id, models.Place.external_id == external_id)
    result = await db.execute(stmt)
    return result.scalars().first()

async def count_places_in_project(db: AsyncSession, project_id: int):
    stmt = select(func.count(models.Place.id)).filter(models.Place.project_id == project_id)
    result = await db.execute(stmt)
    return result.scalar()

async def create_place(db: AsyncSession, project_id: int, place: schemas.PlaceCreate):
    db_place = models.Place(
        project_id=project_id,
        external_id=place.external_id,
        notes=place.notes
    )
    db.add(db_place)
    await db.commit()
    return await get_place(db, db_place.id, project_id)

async def update_place(db: AsyncSession, place_id: int, project_id: int, place_update: schemas.PlaceUpdate):
    db_place = await get_place(db, place_id=place_id, project_id=project_id)
    if not db_place:
        return None
        
    update_data = place_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_place, key, value)
        
    await db.commit()
    return await get_place(db, place_id, project_id)

def is_project_completed(db_project: models.Project) -> bool:
    if not getattr(db_project, 'places', None):
        return False
    if not db_project.places:
        return False
    return all(p.is_visited for p in db_project.places)
