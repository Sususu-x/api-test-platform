FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖：unzip、Java 运行时
RUN apt-get update && \
    apt-get install -y unzip default-jre-headless && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 安装 Allure
COPY allure-2.39.0.zip /tmp/
RUN unzip /tmp/allure-2.39.0.zip -d /opt && \
    chmod +x /opt/allure-2.39.0/bin/allure && \
    ln -s /opt/allure-2.39.0/bin/allure /usr/local/bin/allure && \
    rm /tmp/allure-2.39.0.zip

# 复制项目代码
COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]