FROM python:3.7-alpine
MAINTAINER senesence

# Ensures python output is print to the terminal
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN mkdir /app
WORKDIR /app
COPY ./app /app

# Create a user. -D represents this user can only run apps.
# This is recommended. Otherwise, the image will be run from root account
RUN adduser -D user
# Switch to this user
USER user
