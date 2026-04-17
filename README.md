# API自动化测试平台

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📖 项目简介
一个从0到1独立开发的轻量级API自动化测试平台，支持接口用例管理、批量回归测试、可视化报告生成，并计划集成AI能力辅助用例生成。旨在解决中小团队手工测试效率低、回归成本高的痛点。

## 项目结构

- `backend/`：FastAPI 后端服务
- `frontend/`：Vue3 + Element Plus 前端界面
- `docker-compose.yml`：一键部署配置（规划中）

## ✨ 核心功能
- **用例管理**：增删改查接口用例，支持 GET/POST/PUT/DELETE 等常见方法。
- **自动化执行**：单用例实时测试 + 批量用例异步后台执行，不阻塞前端。
- **专业报告**：集成 Allure 生成可视化测试报告，包含通过率、耗时、请求/响应详情。
- **数据驱动**：基于 Pytest 参数化动态加载数据库用例，无需修改代码。
- **一键部署**：支持 Docker 容器化部署（规划中），提供完整的 API 文档。

## 🛠 技术栈
| 层级 | 技术选型 |
|------|----------|
| 后端框架 | FastAPI |
| ORM | SQLAlchemy |
| 数据库 | MySQL |
| 测试框架 | Pytest + Allure |
| 前端 | Vue 3 + Element Plus (开发中) |
| 部署 | Docker (规划中) |


## 快速开始
1. 克隆项目: `git clone <你的仓库地址>`
2. 安装依赖: `pip install -r requirements.txt`
3. 配置数据库: 修改 `database.py` 中的连接信息
4. 运行服务: `uvicorn main:app --reload`
5. 访问文档: `http://127.0.0.1:8000/docs`
6. 测试报告: http://127.0.0.1:8000/allure-report

## 开发计划
1. 前端管理界面 (Vue3 + Element Plus)
2. AI 辅助生成测试用例 (集成大模型API)
3. 定时任务与邮件通知 
4. Docker 一键部署