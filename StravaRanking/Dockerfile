# pull official base image
FROM python:3.8.3-alpine

# set work directory
WORKDIR /usr/src/StravaRanking

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

# lint
RUN pip install --upgrade pip
COPY . .

# install dependencies
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/StravaRanking/wheels -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh $APP_HOME

# copy project
COPY . .

# run entrypoint.sh
ENTRYPOINT ["/home/StravaRanking/web/entrypoint.sh"]