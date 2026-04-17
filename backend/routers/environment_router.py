from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import crud
import schemas
import models
from database import get_db

router = APIRouter(prefix="/api/environments", tags=["environments"])

@router.post("/", response_model=schemas.EnvironmentResponse)
def create_environment(env: schemas.EnvironmentCreate, db: Session = Depends(get_db)):
    return crud.create_environment(db, env)

@router.get("/", response_model=List[schemas.EnvironmentResponse])
def list_environments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_environments(db, skip, limit)

@router.get("/active", response_model=schemas.EnvironmentResponse)
def get_active_environment_api(db: Session = Depends(get_db)):
    env = crud.get_active_environment(db)
    if not env:
        raise HTTPException(status_code=404, detail="没有激活的环境")
    return env

@router.put("/{env_id}", response_model=schemas.EnvironmentResponse)
def update_environment(env_id: int, env_update: schemas.EnvironmentUpdate, db: Session = Depends(get_db)):
    env = crud.update_environment(db, env_id, env_update)
    if not env:
        raise HTTPException(status_code=404, detail="环境不存在")
    return env

@router.delete("/{env_id}")
def delete_environment(env_id: int, db: Session = Depends(get_db)):
    env = crud.delete_environment(db, env_id)
    if not env:
        raise HTTPException(status_code=404, detail="环境不存在")
    return {"message": "删除成功"}

@router.post("/activate/{env_id}")
def set_active_environment(env_id: int, db: Session = Depends(get_db)):
    env = crud.get_environment(db, env_id)
    if not env:
        raise HTTPException(status_code=404, detail="环境不存在")
    db.query(models.Environment).update({models.Environment.is_active: False})
    env.is_active = True
    db.commit()
    return {"message": f"环境 '{env.name}' 已激活"}