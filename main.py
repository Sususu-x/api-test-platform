from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from database import engine
import models
from routers import case_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API自动化测试平台", version="1.0.0")

# 挂载用例路由
app.include_router(case_router.router)

# 挂载Allure报告目录为静态文件
app.mount("/allure-report", StaticFiles(directory="allure_report", html=True), name="allure_report")

@app.get("/")
def root():
    return {"message": "测试平台运行中，访问 /docs 查看接口文档"}