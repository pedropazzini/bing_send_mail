FROM alpine:3.1 
RUN  echo "http://nl.alpinelinux.org/alpine/edge/testing">>/etc/apk/repositories 
RUN apk update
RUN apk add python-dev curl libxml2-dev libxslt-dev libffi-dev gcc musl-dev libgcc openssl-dev py-pip

#ONBUILD COPY requirements.txt /tmp/requirements.txt

ADD requirements.txt /

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

MAINTAINER Pedro Pazzini <pedro.pazzini@gmail.com>

ENV PYTHONUNBUFFERED 0

COPY bing_send_mail.py /src/bing_send_mail.py
COPY script.py /src/script.py

CMD ["python", "/src/bing_send_mail.py"]
