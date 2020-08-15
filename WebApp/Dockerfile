FROM python:3.7.7

MAINTAINER Team SEMA <henry.hilse@uni-rostock.de>

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN /usr/local/bin/python -m pip install --upgrade pip && \
    pip install djangorestframework && \
    pip install django-crispy-forms && \
    pip install pillow && \
	pip install tensorflow && \
	pip install tensorflow-hub && \
	pip install matplotlib && \
    rm -rf /var/cache/apk/*
	
RUN mkdir /home/WebApp
VOLUME /home/WebApp
WORKDIR /home/WebApp
EXPOSE 8000

ADD / /home/WebApp/
#ENTRYPOINT /bin/bash

ENTRYPOINT ["python", "manage.py", "runserver", "0.0.0.0:8000"] 