# 使用轻量级的 Python 3.10 镜像
FROM python:3.10-slim

# 设置环境变量，防止 Python 写入 pyc 文件并强制无缓冲输出
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# 设置工作目录
WORKDIR /app

# 安装系统依赖（如果 chroma 需要编译依赖，可能需要 build-essential）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目源代码
COPY . .

# 暴露 FastAPI 端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
