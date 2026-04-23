from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json
import os
import re

from zhipuai import APIAuthenticationError

router = APIRouter(prefix="/api/ai", tags=["AI"])


class GenerateRequest(BaseModel):
    description: str


class GenerateResponse(BaseModel):
    cases: list


def clean_json_response(raw_text: str) -> str:
    """
    清理模型返回的文本，提取纯 JSON 数组。
    大模型有时会在 JSON 前后加说明文字，或使用 markdown 代码块。
    """
    # 尝试提取 markdown 代码块中的 JSON
    code_block_match = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", raw_text, re.DOTALL)
    if code_block_match:
        return code_block_match.group(1)

    # 直接查找第一个 [ 到最后一个 ] 之间的内容
    json_start = raw_text.find("[")
    json_end = raw_text.rfind("]") + 1
    if json_start != -1 and json_end > json_start:
        return raw_text[json_start:json_end]

    # 如果都没找到，返回原文本让 JSON 解析器报错
    return raw_text


@router.post("/generate-cases")
async def generate_cases(req: GenerateRequest):
    """
    根据接口描述，调用大模型生成结构化测试用例。
    返回的每条用例包含：name, url, method, expected_status, expected_response, assert_type, assert_target
    """
    try:
        from zhipuai import ZhipuAI

        api_key = os.getenv("ZHIPU_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="未配置 ZHIPU_API_KEY 环境变量")

        client = ZhipuAI(api_key=api_key)

        # Few-Shot Prompt：用示例告诉模型你期望的输出格式
        system_prompt = """你是一个专业的测试工程师。请根据用户提供的接口描述，生成 3-5 条 API 测试用例。

你必须返回严格的 JSON 数组，不要任何额外解释。每个元素必须包含以下字段：
- name: 用例名称（清晰描述测试场景，如"正常登录"、"密码错误"、"缺少参数"）
- url: 接口路径（如 /api/login）
- method: 请求方法（GET/POST/PUT/DELETE）
- request_body: 请求体 JSON 字符串，无则填 null
- expected_status: 期望状态码（如 200、401、400）
- expected_response: 期望响应关键词（如"token"、"成功"）
- assert_type: 断言类型（contains/jsonpath/regex），默认 contains
- assert_target: 断言目标，仅 jsonpath/regex 时填写，否则为 null

示例输入："用户登录接口，POST /api/login，参数 username 和 password，成功返回 token"

示例输出：
[
  {
    "name": "正常登录-正确账号密码",
    "url": "/api/login",
    "method": "POST",
    "request_body": "{\"username\": \"admin\", \"password\": \"123456\"}",
    "expected_status": 200,
    "expected_response": "token",
    "assert_type": "contains",
    "assert_target": null
  },
  {
    "name": "异常登录-密码错误",
    "url": "/api/login",
    "method": "POST",
    "request_body": "{\"username\": \"admin\", \"password\": \"wrong\"}",
    "expected_status": 401,
    "expected_response": "密码错误",
    "assert_type": "contains",
    "assert_target": null
  },
  {
    "name": "异常登录-缺少参数",
    "url": "/api/login",
    "method": "POST",
    "request_body": "{\"username\": \"admin\"}",
    "expected_status": 400,
    "expected_response": "password",
    "assert_type": "contains",
    "assert_target": null
  }
]
"""

        response = client.chat.completions.create(
            model="glm-4-flash",  # 免费模型
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"接口描述：{req.description}"}
            ],
            temperature=0.3,  # 低温度保证输出稳定
            max_tokens=2000
        )

        content = response.choices[0].message.content

        # 清理并解析 JSON
        cleaned_json = clean_json_response(content)

        try:
            cases = json.loads(cleaned_json)
        except json.JSONDecodeError as e:
            # 如果解析失败，返回原始内容以便调试
            raise HTTPException(
                status_code=500,
                detail=f"AI 返回格式错误：{str(e)}。原始内容：{content[:200]}"
            )

        # Pydantic 强校验：确保每条用例包含必要字段
        required_fields = ["name", "url", "method", "expected_status", "expected_response", "assert_type"]
        for case in cases:
            for field in required_fields:
                if field not in case:
                    case[field] = None if field in ["assert_target"] else ""
            # 确保 method 是大写
            if case.get("method"):
                case["method"] = case["method"].upper()
            # 默认断言类型
            if not case.get("assert_type"):
                case["assert_type"] = "contains"

        return GenerateResponse(cases=cases)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 调用失败：{str(e)}")
    except APIAuthenticationError:
        raise HTTPException(status_code=401, detail="AI 服务认证失败，请联系管理员更新 API Key")

# 备选：DeepSeek 版本（如需切换，注释掉上面，启用下面）
# @router.post("/generate-cases")
# async def generate_cases_deepseek(req: GenerateRequest):
#     from openai import OpenAI
#
#     api_key = os.getenv("DEEPSEEK_API_KEY")
#     if not api_key:
#         raise HTTPException(status_code=500, detail="未配置 DEEPSEEK_API_KEY")
#
#     client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
#
#     # ... 相同的 prompt 逻辑 ...
#
#     response = client.chat.completions.create(
#         model="deepseek-chat",
#         messages=[...],
#         temperature=0.3
#     )