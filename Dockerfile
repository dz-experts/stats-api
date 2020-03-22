FROM tiangolo/uvicorn-gunicorn:python3.7

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 80
    