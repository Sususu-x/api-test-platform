from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routers import environment_router
from database import engine
import models
from routers import case_router
import time
from sqlalchemy import text


models.Base.metadata.create_all(bind=engine)

# 等待数据库就绪
max_retries = 30
for i in range(max_retries):
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ 数据库连接成功")
        break
    except Exception as e:
        print(f"⏳ 等待数据库启动... ({i+1}/{max_retries})")
        time.sleep(2)
else:
    raise Exception("❌ 数据库连接失败，请检查配置")

app = FastAPI(title="API自动化测试平台", version="1.0.0")

origins = [
    "http://localhost:5173",  # Vue 开发服务器的默认端口
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 挂载用例路由
app.include_router(case_router.router)

# 注册环境管理路由  ← 关键！！！
app.include_router(environment_router.router)

# 挂载Allure报告目录为静态文件
app.mount("/allure-report", StaticFiles(directory="allure_report", html=True), name="allure_report")

@app.get("/")
def root():
    return {"message": "测试平台运行中，访问 /docs 查看接口文档"}