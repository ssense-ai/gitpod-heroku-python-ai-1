FROM python:slim-buster
WORKDIR /app
COPY . /app

RUN ["apt-get", "update"]
RUN ["apt-get", "-y", "install", "build-essential"]
RUN ["pip3", "install", "Flask", "flask-cors", "numpy", "pandas", "scikit-learn", "xgboost", "lightgbm"]
#RUN ["pip3", "install", "-r", "requirements.txt"]

CMD python /app/server.py
