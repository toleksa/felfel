# Dockerfile

FROM python:3.12.0-alpine3.18 
COPY requirements.txt /requirements.txt
#RUN apk add --no-cache --virtual build-deps build-base \
#    && pip install -r /requirements.txt \
#    && apk del build-deps
RUN pip install -r /requirements.txt
RUN ln -sf /usr/share/zoneinfo/Europe/Zurich /etc/localtime

EXPOSE 8080
STOPSIGNAL SIGTERM

WORKDIR /app
COPY app.py ./
CMD python3 /app/app.py

