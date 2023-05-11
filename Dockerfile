FROM python:latest
WORKDIR /usr

ADD Extension /usr/Extension
RUN pip3 install -r /usr/Extension/requirements.txt
EXPOSE 8080


CMD [ "python3","/usr/Extension/server/server.py"]