FROM ubuntu:latest
MAINTAINER Nikolay Baranenko 'drno-reg@mail.ru'
COPY . /msk_scope
WORKDIR /msk_scope
ENV LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    PYTHONPATH=/msk_scope \
    FLASK_APP=/msk_scope/scope/ \
    FLASK_CONFIG=/msk_scope/flask_run.py \
    FLASK_ENV=development \
    FLASK_DEBUG=1 \
    TZ=Europe/Moscow
RUN apt-get update && apt-get install -yy tzdata \
    && apt-get install -y python3-pip python3-venv build-essential telnet iputils-ping gunicorn \
    && pip3 install --no-cache-dir -r requirements.txt
RUN cp /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
#RUN apt-get install -y python-gevent
#RUN flask --version
#RUN gunicorn --version
#ENTRYPOINT ['export FLASK_APP=flask_run.py']

#CMD ["flask", "run", "-p", "5000", "-h", "0.0.0.0"]

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8228", "wsgi:scope"]

#CMD ["/bin/bash"]
