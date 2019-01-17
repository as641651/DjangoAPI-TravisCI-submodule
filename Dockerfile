FROM python:3.7-alpine
MAINTAINER senesence

# Ensures python output is print to the terminal
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt

# Postgres dependences
# apk is the package manager that comes with alpine
# --update : update registry before we add it
# --no-cache: Do not store index locally. Used to keep container small
RUN apk add --update --no-cache postgresql-client
# --virtual: an alias which can be used to remove dependencies later
# Eg. We need gcc to compile the program but do not need it later
RUN apk add --update --no-cache --virtual .tmp-build-deps \
      gcc libc-dev linux-headers postgresql-dev

RUN pip install -r /requirements.txt

# Delete temporary dependencies
RUN apk del .tmp-build-deps

RUN mkdir /app
WORKDIR /app
COPY ./app /app

# Create a user. -D represents this user can only run apps.
# This is recommended. Otherwise, the image will be run from root account
RUN adduser -D user
# Switch to this user
USER user
