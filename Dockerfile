FROM python:3.11

# 更稳的 Python 运行体验
# ENV PYTHONDONTWRITEBYTECODE=1 \
#     PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple uwsgi

COPY . .

ENV PORT=10000

EXPOSE 10000

CMD ["./start.sh"]
