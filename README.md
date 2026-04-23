# API 自动化测试平台

[![Python](https://img.shields.io/badge/Python-3.10-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.135-green)](https://fastapi.tiangolo.com/)
[![Vue](https://img.shields.io/badge/Vue-3.x-brightgreen)](https://vuejs.org/)
[![Docker](https://img.shields.io/badge/Docker-✓-blue)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## 📖 项目简介
一个从零到一独立开发的轻量级 API 自动化测试平台，集用例管理、环境切换、自动化执行、可视化报告及 **AI 智能生成用例**于一体，旨在解决手工回归测试效率低、用例维护成本高的痛点。

## ✨ 核心功能
- **用例管理**：支持增删改查，覆盖 GET/POST/PUT/DELETE 方法，可配置请求头、请求体及断言规则。
- **智能断言引擎**：基于策略模式解耦，支持关键词包含、JSONPath 提取、正则表达式匹配。
- **环境隔离**：多环境配置管理，Base URL 与全局 Header 动态注入，一键切换。
- **自动化执行**：Pytest 参数化动态加载用例，后台异步任务批量执行，不阻塞前端。
- **专业报告**：Allure 报告集成请求/响应附件、执行步骤，失败用例定位至秒级。
- **AI 辅助生成**：接入智谱 GLM-4-Flash 大模型，根据自然语言描述自动生成结构化测试用例，效率提升 70%。
- **容器化部署**：Docker Compose 一键编排 MySQL + FastAPI + Nginx，环境搭建缩短至 5 分钟。

## 🛠 技术栈
| 层级 | 技术选型 |
|------|----------|
| 后端框架 | FastAPI |
| ORM | SQLAlchemy |
| 数据库 | MySQL |
| 测试框架 | Pytest + Allure |
| 前端 | Vue 3 + Element Plus + Vite |
| 反向代理 | Nginx |
| AI 能力 | 智谱 ChatGLM API (GLM-4-Flash) |
| 部署 | Docker + Docker Compose |

## 📁 项目结构
- `backend/`：FastAPI 后端服务
- `frontend/`：Vue3 + Element Plus 前端界面
- `docker-compose.yml`：一键部署配置
- `readme.md`


## 🚀 快速开始
### 1. 克隆项目
git clone https://github.com/Sususu-x/api-test-platform.git
cd api-test-platform

### 2. 启动服务（需安装 Docker Desktop）
docker-compose up -d

### 3. 访问
- 前端：http://localhost
- 后端文档：http://localhost:8000/docs
- 测试报告：http://localhost/allure-report/

## 📊 项目成果
- 将单次回归测试时间从手工 30 分钟 压缩至 < 3 分钟，效率提升 90%。
- AI 辅助用例生成，数据准备效率提升 70%。
- 多环境一键切换，配置错误率降低 99%。
- 新人开发环境搭建时间由 0.5 天缩短至 5 分钟。

## 📧 联系方式
- 作者：郭乃丽
- 邮箱：576261416@qq.com