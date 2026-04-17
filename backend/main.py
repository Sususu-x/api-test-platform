from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routers import environment_router
from database import engine
import models
from routers import case_router

models.Base.metadata.create_all(bind=engine)

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