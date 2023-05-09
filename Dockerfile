FROM python:latest
WORKDIR /usr
ADD Dir /usr/Dir
RUN pip3 install -r /usr/Dir/requirements.txt
CMD ["python3", "/usr/Dir/server/summarize.py"]
