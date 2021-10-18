FROM nginx:1.15.8

#change timezone on Moskow
ENV TZ=Europe/Moscow
RUN apt-get update && apt-get install -yy tzdata
RUN cp /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN rm /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/
RUN rm /etc/nginx/conf.d/default.conf
COPY main_server.conf /etc/nginx/conf.d/
#COPY ssl/certificate.crt /etc/ssl/certificate.crt
#COPY ssl/private.key /etc/ssl/private.key
