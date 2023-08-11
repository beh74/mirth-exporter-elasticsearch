FROM python:3-alpine

RUN apk update
RUN apk upgrade

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
 
COPY main.py .

COPY crontab.file /var/spool/cron/crontabs/root

CMD ["crond", "-l","2","-f"]