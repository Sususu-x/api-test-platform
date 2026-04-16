import pytest
import requests
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 数据库连接（和database.py里一样）
DATABASE_URL = "mysql+pymysql://root:GNL20040215@localhost:3306/api_test_platform?charset=utf8mb4"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def get_all_cases():
    """从数据库获取所有用例"""
    from models import ApiCase
    db = SessionLocal()
    cases = db.query(ApiCase).all()
    db.close()
    return cases


# 生成测试用例ID列表（pytest参数化需要）
case_list = get_all_cases()
case_ids = [case.id for case in case_list]


@pytest.mark.parametrize("case_id", case_ids)
def test_api_case(case_id):
    """单个用例测试函数，被pytest自动调用"""
    from models import ApiCase
    db = SessionLocal()
    case = db.query(ApiCase).filter(ApiCase.id == case_id).first()
    db.close()

    if not case:
        pytest.skip(f"用例ID {case_id} 不存在")

    # 准备请求
    headers = json.loads(case.headers) if case.headers else {}
    body = json.loads(case.request_body) if case.request_body else None

    # 发送请求
    if case.method.upper() == "GET":
        resp = requests.get(case.url, headers=headers, timeout=10)
    elif case.method.upper() == "POST":
        resp = requests.post(case.url, headers=headers, json=body, timeout=10)
    elif case.method.upper() == "PUT":
        resp = requests.put(case.url, headers=headers, json=body, timeout=10)
    elif case.method.upper() == "DELETE":
        resp = requests.delete(case.url, headers=headers, timeout=10)
    else:
        pytest.fail(f"不支持的请求方法: {case.method}")

    # 添加Allure报告附件（可选，让报告更详细）
    import allure
    allure.attach(f"请求URL: {case.url}\n方法: {case.method}",
                  name="请求信息",
                  attachment_type=allure.attachment_type.TEXT)
    allure.attach(resp.text,
                  name="响应内容",
                  attachment_type=allure.attachment_type.JSON if resp.headers.get('content-type', '').startswith(
                      'application/json') else allure.attachment_type.TEXT)

    # 断言
    if case.expected_status:
        assert resp.status_code == case.expected_status, \
            f"状态码不匹配: 期望 {case.expected_status}, 实际 {resp.status_code}"

    if case.expected_response:
        assert case.expected_response in resp.text, \
            f"响应内容不包含期望关键词: '{case.expected_response}'"