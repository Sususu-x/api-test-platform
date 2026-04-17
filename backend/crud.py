# 增删改查的具体操作函数

from sqlalchemy.orm import Session
import models
import schemas

def create_case(db: Session, case: schemas.CaseCreate):
    """新增一个用例到数据库"""
    # 把Pydantic模型转成SQLAlchemy模型
    db_case = models.ApiCase(**case.model_dump())
    db.add(db_case)          # 添加到会话
    db.commit()              # 提交事务
    db.refresh(db_case)      # 刷新，获取数据库生成的id和时间
    return db_case

def update_case(db: Session, db_case: models.ApiCase, case_update: schemas.CaseCreate):
    update_data = case_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_case, field, value)
    db.commit()
    db.refresh(db_case)
    return db_case

def get_cases(db: Session, skip: int = 0, limit: int = 100):
    """获取用例列表（分页）"""
    return db.query(models.ApiCase).offset(skip).limit(limit).all()

def get_case(db: Session, case_id: int):
    """根据ID获取单条用例"""
    return db.query(models.ApiCase).filter(models.ApiCase.id == case_id).first()

# ---------- 环境管理 CRUD ----------
def get_active_environment(db: Session):
    return db.query(models.Environment).filter(models.Environment.is_active == True).first()

def get_environments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Environment).offset(skip).limit(limit).all()

def get_environment(db: Session, env_id: int):
    return db.query(models.Environment).filter(models.Environment.id == env_id).first()

def create_environment(db: Session, env: schemas.EnvironmentCreate):
    # 如果新环境设为激活，先将其他所有环境设为非激活
    if env.is_active:
        db.query(models.Environment).update({models.Environment.is_active: False})
    db_env = models.Environment(**env.model_dump())
    db.add(db_env)
    db.commit()
    db.refresh(db_env)
    return db_env

def update_environment(db: Session, env_id: int, env_update: schemas.EnvironmentUpdate):
    db_env = db.query(models.Environment).filter(models.Environment.id == env_id).first()
    if not db_env:
        return None
    update_data = env_update.model_dump(exclude_unset=True)
    if update_data.get('is_active'):
        db.query(models.Environment).update({models.Environment.is_active: False})
    for field, value in update_data.items():
        setattr(db_env, field, value)
    db.commit()
    db.refresh(db_env)
    return db_env

def delete_environment(db: Session, env_id: int):
    db_env = db.query(models.Environment).filter(models.Environment.id == env_id).first()
    if db_env:
        db.delete(db_env)
        db.commit()
    return db_env