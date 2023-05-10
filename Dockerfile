FROM python:latest
WORKDIR /usr

ADD Dir /usr/Dir
RUN pip3 install -r /usr/Dir/requirements.txt
EXPOSE 8080


CMD [ "python3","/usr/Dir/server/summarize.py"]