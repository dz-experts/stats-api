FROM tiangolo/uvicorn-gunicorn:python3.7

WORKDIR /app

COPY . .

RUN pip install fastapi
RUN pip install requests

EXPOSE 80
