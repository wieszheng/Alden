FROM python:3.12.0-slim as builder
WORKDIR /alden
COPY ./requirements.txt .

RUN python -m venv /alden/venv  \
    && /alden/venv/bin/pip install --upgrade pip \
    && /alden/venv/bin/pip install --index-url https://pypi.tuna.tsinghua.edu.cn/simple \
    --no-cache-dir -r requirements.txt

RUN apt update -y \
    && apt install -y tzdata wget \
    && apt clean



FROM python:3.12.0-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /alden
COPY . .
COPY --from=builder /alden/venv/ /alden/venv/
COPY --from=builder /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

EXPOSE 5021
CMD ["/alden/venv/bin/supervisord", "-c", "/alden/supervisor.conf"]