FROM python:slim-buster
WORKDIR /app
COPY . /app

RUN ["apt-get", "update"]
RUN ["apt-get", "-y", "install", "build-essential"]
RUN ["pip3", "install", "Flask", "pytesseract", "flask-cors"]

CMD python /app/server.py
