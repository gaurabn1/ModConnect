FROM python:3.11-slim-bullseye

ENV PYTHONUNBUFFERED=1

WORKDIR /code/

RUN pip install --upgrade pip

COPY requirements.txt .

RUN pip install -r requirements.txt \
    --no-cache-dir \
    --index-url https://mirrors.aliyun.com/pypi/simple/


RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6


COPY . .

COPY ./entrypoint.sh /

ENTRYPOINT ["sh", "/entrypoint.sh"]

