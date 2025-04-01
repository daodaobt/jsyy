FROM python:3.10.11-slim

# 设置清华 APT 镜像源
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list && \
    sed -i 's/security.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list

# 设置清华 PyPI 镜像源
RUN pip install --no-cache-dir --upgrade pip && \
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 安装系统依赖
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libssl-dev \
    pkg-config \
    default-libmysqlclient-dev \
    libmariadb-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app



# 确保目录存在并复制道具文件
RUN mkdir -p /app/data
COPY data/item.txt /app/data/item.txt

# 仅复制必要文件（非代码）
COPY wait-for-it.sh .
COPY data/item.txt /app/data/item.txt


RUN mkdir -p /app/static /app/media && \
    chmod +x /app/wait-for-it.sh && \
    chmod 755 /app/wait-for-it.sh

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt


EXPOSE 8000