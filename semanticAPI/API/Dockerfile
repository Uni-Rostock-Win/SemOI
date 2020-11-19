FROM python:3.8.6

MAINTAINER Achim Reiz <achim.reiz@uni-rostock.de>

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN /usr/local/bin/python -m pip install --upgrade pip && \
    pip install pipenv 

RUN mkdir /home/semanticAPI
VOLUME /home/semanticAPI
WORKDIR /home/semanticAPI
EXPOSE 8000

ADD / /home/semanticAPI/
RUN pipenv install --system
#ENTRYPOINT /bin/bash

ENTRYPOINT ["python", "manage.py", "runserver", "0.0.0.0:8000"] 