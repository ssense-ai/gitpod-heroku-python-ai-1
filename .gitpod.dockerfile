FROM gitpod/workspace-full

RUN ["npm", "install", "-g", "http-server"]
RUN ["npm", "install", "-g", "vercel"]

USER root
RUN ["apt-get", "-y", "install", "build-essential"]
#RUN ["pip3", "install", "Flask", "flask-cors", "numpy", "pandas", "scikit-learn", "xgboost"]
RUN ["pip3", "install", "-r", "requirements.txt"]

RUN curl https://cli-assets.heroku.com/install.sh | sh
RUN chown -R gitpod:gitpod /home/gitpod/.cache/heroku

USER gitpod
