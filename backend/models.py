# 数据库表对应的Python类（ORM模型）
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base

class ApiCase(Base):
    __tablename__ = "api_case"  # 对应数据库中的表名

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)
    method = Column(String(10), nullable=False, default="GET")
    headers = Column(Text, nullable=True)
    request_body = Column(Text, nullable=True)
    expected_status = Column(Integer, nullable=True)
    expected_response = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    assert_type = Column(String(20), default='contains')
    assert_target = Column(String(200), nullable=True)

#通过这个类，可以用db.add(ApiCase(name="测试", url="/test"))来插入数据，而不用写INSERT语句。