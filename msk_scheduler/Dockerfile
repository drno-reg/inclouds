FROM ubuntu:latest
MAINTAINER Nikolay Baranenko 'drno-reg@mail.ru'
#RUN apt-get update -y --fix-missing
#change timezone on Moskow
ENV TZ=Europe/Moscow
RUN apt-get update && apt-get install -yy tzdata
RUN cp /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
# fping - для работы template_ping
RUN apt-get install -y python3-pip python3-venv build-essential telnet iputils-ping fping
RUN ls -las
COPY . /msk_scheduler
WORKDIR /msk_scheduler
RUN pip3 install --no-cache-dir -r requirements.txt


CMD ["python3", "main_scheduler.py"]

