FROM python:3.6

MAINTAINER Achim Reiz <achim.reiz@uni-rostock.de>

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN pip install django && \
    pip install djangorestframework && \
    pip install rdflib && \
    pip install sparqlwrapper && \
    pip install markdown # Markdown support for the browsable API. && \
    pip cache purge && \
    rm -rf /var/cache/apk/*
RUN mkdir /home/semanticAPI
VOLUME /home/semanticAPI
WORKDIR /home/semanticAPI
EXPOSE 8000

ADD / /home/semanticAPI/
#ENTRYPOINT /bin/bash

ENTRYPOINT ["python", "manage.py", "runserver", "0.0.0.0:8000"] 