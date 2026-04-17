# 数据库连接配置
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# MySQL连接地址格式：mysql+pymysql://用户名:密码@主机:端口/数据库名
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:GNL20040215@localhost:3306/api_test_platform?charset=utf8mb4"

# 创建数据库引擎（发动机，负责和数据库通信）
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 创建会话工厂（每次操作数据库都从工厂拿一个“会话”，用完归还）
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 基类，所有ORM模型都继承它
Base = declarative_base()

# 依赖函数：每个请求获取独立的数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()