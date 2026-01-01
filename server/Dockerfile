FROM python:3.10-slim

# 设置时区为上海
ENV TZ=Asia/Shanghai
RUN sed -i 's@deb.debian.org@mirrors.aliyun.com@g' /etc/apt/sources.list.d/debian.sources
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    tzdata \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app

# Set the working directory
WORKDIR /app

# 安装依赖
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple \
&& pip config set global.trusted-host mirrors.aliyun.com \
&& pip install --upgrade pip \
&& pip install -r requirements.txt --no-warn-script-location

EXPOSE 8080

CMD python3 run.py
#CMD ["python3", "-m", "uvicorn", "run:app", "--host", "0.0.0.0", "--port ", "80"]