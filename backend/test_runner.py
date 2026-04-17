import pytest
import requests
import json
import re
import allure
from urllib.parse import urlparse
from jsonpath_ng import parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 导入数据库会话和 CRUD 函数
from database import SessionLocal
from crud import get_active_environment


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

if not case_ids:
    pytest.skip("数据库中没有用例，跳过测试")

@pytest.mark.parametrize("case_id", case_ids)
def test_api_case(case_id):
    """单个用例测试函数，被pytest自动调用"""
    from models import ApiCase
    db = SessionLocal()
    case = db.query(ApiCase).filter(ApiCase.id == case_id).first()
    db.close()

    if not case:
        pytest.skip(f"用例ID {case_id} 不存在")

    # 设置Allure报告的标题和描述
    allure.dynamic.title(case.name)
    allure.dynamic.description(f"请求方法: {case.method} | URL: {case.url}")

    # 获取激活环境
    db = SessionLocal()
    env = get_active_environment(db)
    db.close()

    # 拼接完整 URL
    full_url = case.url
    if env and not case.url.startswith(('http://', 'https://')):
        full_url = env.base_url.rstrip('/') + '/' + case.url.lstrip('/')

    # 准备请求头（合并全局头）
    headers = {}
    if env and env.global_headers:
        try:
            headers.update(json.loads(env.global_headers))
        except:
            pass
    if case.headers:
        try:
            headers.update(json.loads(case.headers))
        except:
            pass

    # 准备请求体
    body = json.loads(case.request_body) if case.request_body else None

    # 校验 URL 格式（使用拼接后的 full_url）
    parsed = urlparse(full_url)
    if not parsed.scheme:
        pytest.fail(f"URL格式错误：缺少协议头（http/https），当前值为 '{full_url}'")

    # ========== 步骤1：发送HTTP请求 ==========
    with allure.step(f"发送 {case.method} 请求"):
        # 附加请求详情（完整信息）
        request_detail = (
            f"URL: {full_url}\n"
            f"Method: {case.method}\n"
            f"Headers: {json.dumps(headers, indent=2, ensure_ascii=False) if headers else '无'}\n"
            f"Body: {json.dumps(body, indent=2, ensure_ascii=False) if body else '无'}"
        )
        allure.attach(request_detail, name="请求详情", attachment_type=allure.attachment_type.TEXT)

        try:
            if case.method.upper() == "GET":
                resp = requests.get(full_url, headers=headers, timeout=10)
            elif case.method.upper() == "POST":
                resp = requests.post(full_url, headers=headers, json=body, timeout=10)
            elif case.method.upper() == "PUT":
                resp = requests.put(full_url, headers=headers, json=body, timeout=10)
            elif case.method.upper() == "DELETE":
                resp = requests.delete(full_url, headers=headers, timeout=10)
            else:
                pytest.fail(f"不支持的请求方法: {case.method}")
        except Exception as e:
            pytest.fail(f"请求发送失败: {str(e)}")

        # 附加响应详情
        response_detail = (
            f"Status Code: {resp.status_code}\n"
            f"Headers: {dict(resp.headers)}\n"
            f"Body (前1000字符):\n{resp.text[:1000]}"
        )
        allure.attach(response_detail, name="响应详情", attachment_type=allure.attachment_type.TEXT)

        # 如果响应是JSON，额外附加格式化的JSON附件
        if resp.headers.get('content-type', '').startswith('application/json'):
            try:
                formatted_json = json.dumps(resp.json(), indent=2, ensure_ascii=False)
                allure.attach(formatted_json, name="响应JSON (格式化)", attachment_type=allure.attachment_type.JSON)
            except:
                allure.attach(resp.text, name="响应内容", attachment_type=allure.attachment_type.TEXT)
        else:
            allure.attach(resp.text, name="响应内容", attachment_type=allure.attachment_type.TEXT)

    # ========== 步骤2：断言状态码 ==========
    if case.expected_status is not None:
        with allure.step(f"断言状态码 == {case.expected_status}"):
            assert resp.status_code == case.expected_status, \
                f"状态码不匹配: 期望 {case.expected_status}, 实际 {resp.status_code}"

    # ========== 步骤3：断言响应内容 ==========
    if case.expected_response and case.assert_type:
        with allure.step(f"断言响应内容 [{case.assert_type}]"):
            if case.assert_type == 'contains':
                assert case.expected_response in resp.text, \
                    f"响应中未找到关键词: '{case.expected_response}'"
            elif case.assert_type == 'jsonpath':
                try:
                    json_data = resp.json()
                    jsonpath_expr = parse(case.assert_target or "$")
                    matches = [match.value for match in jsonpath_expr.find(json_data)]
                    if not matches:
                        pytest.fail(f"JSONPath '{case.assert_target}' 无匹配结果")
                    if case.expected_response:
                        actual = str(matches[0])
                        expected = str(case.expected_response)
                        assert actual == expected, \
                            f"JSONPath '{case.assert_target}' 提取值为 {actual}，期望 {expected}"
                except Exception as e:
                    pytest.fail(f"JSONPath断言失败: {str(e)}")
            elif case.assert_type == 'regex':
                pattern = re.compile(case.assert_target or case.expected_response)
                assert pattern.search(resp.text), \
                    f"正则表达式 '{pattern.pattern}' 未匹配到任何内容"
            else:
                pytest.fail(f"不支持的断言类型: {case.assert_type}")
