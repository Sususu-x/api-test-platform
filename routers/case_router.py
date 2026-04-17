# 用例相关的接口路由
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import crud
import schemas
from database import get_db
import requests
import json
import time
from schemas import CaseExecuteResult
from fastapi import BackgroundTasks
import subprocess
import os
import shutil

# 创建路由器，所有接口以 /api/cases 开头
router = APIRouter(prefix="/api/cases", tags=["cases"])

@router.post("/", response_model=schemas.CaseResponse)
def create_case(case: schemas.CaseCreate, db: Session = Depends(get_db)):
    """新增测试用例"""
    return crud.create_case(db=db, case=case)

@router.get("/", response_model=List[schemas.CaseResponse])
def read_cases(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取用例列表"""
    cases = crud.get_cases(db, skip=skip, limit=limit)
    return cases


@router.post("/{case_id}/execute", response_model=CaseExecuteResult)
def execute_case(case_id: int, db: Session = Depends(get_db)):
    """执行单条用例"""
    # 1. 从数据库获取用例
    case = crud.get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="用例不存在")

    # 2. 解析headers和body（数据库存的是JSON字符串）
    headers = json.loads(case.headers) if case.headers else {}
    body = json.loads(case.request_body) if case.request_body else None

    # 3. 发送HTTP请求
    start_time = time.time()
    try:
        # 根据method选择请求方式
        if case.method.upper() == "GET":
            response = requests.get(case.url, headers=headers, timeout=10)
        elif case.method.upper() == "POST":
            response = requests.post(case.url, headers=headers, json=body, timeout=10)
        elif case.method.upper() == "PUT":
            response = requests.put(case.url, headers=headers, json=body, timeout=10)
        elif case.method.upper() == "DELETE":
            response = requests.delete(case.url, headers=headers, timeout=10)
        else:
            raise HTTPException(status_code=400, detail=f"不支持的请求方法: {case.method}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"请求执行失败: {str(e)}")

    execution_time = int((time.time() - start_time) * 1000)

    # 4. 断言比对
    actual_status = response.status_code
    status_match = (actual_status == case.expected_status) if case.expected_status else True

    actual_response_text = response.text
    expected_contains = case.expected_response
    response_match = (expected_contains in actual_response_text) if expected_contains else True

    passed = status_match and response_match

    # 5. 返回执行结果
    return CaseExecuteResult(
        case_id=case.id,
        case_name=case.name,
        actual_status=actual_status,
        expected_status=case.expected_status,
        status_match=status_match,
        actual_response=actual_response_text[:500],  # 截取前500字符，防止响应太长
        expected_response_contains=expected_contains,
        response_match=response_match,
        passed=passed,
        execution_time_ms=execution_time
    )


@router.post("/execute-batch")
async def execute_batch(background_tasks: BackgroundTasks, case_ids: List[int] = None):
    """
    批量执行用例（异步）
    - 如果不传case_ids，默认执行全部用例
    - 任务在后台运行，立即返回“任务已提交”
    """
    if case_ids:
        # 使用 pytest 参数化生成的测试函数名精确匹配：test_api_case[case_id]
        ids_str = " or ".join([f"test_api_case[{cid}]" for cid in case_ids])
        cmd = f"pytest test_runner.py -v --alluredir=allure_results -k \"{ids_str}\""
    else:
        cmd = "pytest test_runner.py -v --alluredir=allure_results"

    def run_pytest():
        # 清空历史结果目录
        results_dir = "allure_results"
        if os.path.exists(results_dir):
            shutil.rmtree(results_dir)
        os.makedirs(results_dir, exist_ok=True)

        # 执行 pytest，生成新结果
        subprocess.run(cmd, shell=True, cwd=os.getcwd())

        # 生成报告
        subprocess.run("allure generate allure_results -o allure_report --clean", shell=True, cwd=os.getcwd())

    background_tasks.add_task(run_pytest)

    return {
        "message": "批量执行任务已提交，正在后台运行",
        "report_url": "/allure-report"
    }