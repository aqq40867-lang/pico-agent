# Pico 本地 coding agent 的 Docker 镜像
FROM python:3.12-slim

# git：Pico 启动时要读仓库的 branch/status/log
# safe.directory：挂载进来的目录属主和容器用户不同，不加这行 git 会报 dubious ownership
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/* \
    && git config --system --add safe.directory '*'

# 给 agent 的 run_shell 用：它跑测试时常用 uv / pytest
RUN pip install --no-cache-dir uv pytest

WORKDIR /opt/pico
COPY pyproject.toml README.md ./
COPY pico ./pico
RUN pip install --no-cache-dir .

# 要让 agent 工作的仓库挂载到这里
WORKDIR /workspace
ENV PYTHONUNBUFFERED=1 PYTHONIOENCODING=utf-8

ENTRYPOINT ["pico", "--cwd", "/workspace"]
