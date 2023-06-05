FROM python:3.8-slim-buster

WORKDIR /app

EXPOSE 8000

COPY requirements.txt requirements.txt

RUN apt-get update && apt-get install -y krb5-config

RUN pip3 install -r requirements.txt

ENV PYTHONUNBUFFERED=1

COPY . .

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]