# API请求/响应的数据结构（Pydantic模型）

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# 创建用例时前端需要传的数据（哪些字段必填，哪些选填）
class CaseCreate(BaseModel):
    name: str
    url: str
    method: str = "GET"
    headers: Optional[str] = None
    request_body: Optional[str] = None
    expected_status: Optional[int] = None
    expected_response: Optional[str] = None

# 返回给前端的用例数据（包含id和创建时间等）
class CaseResponse(BaseModel):
    id: int
    name: str
    url: str
    method: str
    headers: Optional[str]
    request_body: Optional[str]
    expected_status: Optional[int]
    expected_response: Optional[str]
    created_at: datetime
    updated_at: datetime

    # 告诉Pydantic可以从ORM对象直接转换
    class Config:
        from_attributes = True

#CaseCreate是输入模型，CaseResponse是输出模型。FastAPI会根据这些模型自动校验数据格式。

class CaseExecuteResult(BaseModel):
    case_id: int
    case_name: str
    actual_status: int                    # 实际返回的状态码
    expected_status: Optional[int]        # 期望状态码
    status_match: bool                    # 状态码是否匹配
    actual_response: str                  # 实际响应体（截取前500字符）
    expected_response_contains: Optional[str]  # 期望包含的关键词
    response_match: bool                  # 响应内容是否包含关键词
    passed: bool                          # 整体是否通过
    execution_time_ms: int                # 执行耗时（毫秒）