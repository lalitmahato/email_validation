FROM python:3.12
ENV PYTHONUNBUFFERED 1
WORKDIR /code
ADD ./ /code
RUN apt-get update
RUN apt-get install -y gettext
COPY requirements.txt /code/requirements.txt
RUN pip install -r /code/requirements.txt