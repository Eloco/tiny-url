# 基础镜像
FROM python:3.10-alpine

EXPOSE 8080

# 设置工作目录
WORKDIR /app

# 将本地文件添加到容器中
ADD . /app

# 安装所需的包
RUN pip install -r requirements.txt

# 设置环境变量
ENV SECRET_KEY mysecretkey
ENV SQLALCHEMY_DATABASE_URI sqlite:///urls.db
ENV REMOVAL_INTERVAL 30

# 启动命令
CMD ["python", "app.py"]
