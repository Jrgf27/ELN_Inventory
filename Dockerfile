FROM python:3-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN     apt-get update -y &&\
        apt-get upgrade -y &&\
        pip install -r requirements.txt


COPY . .

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
