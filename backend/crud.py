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

def get_cases(db: Session, skip: int = 0, limit: int = 100):
    """获取用例列表（分页）"""
    return db.query(models.ApiCase).offset(skip).limit(limit).all()

def get_case(db: Session, case_id: int):
    """根据ID获取单条用例"""
    return db.query(models.ApiCase).filter(models.ApiCase.id == case_id).first()