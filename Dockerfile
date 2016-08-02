FROM jfloff/alpine-python:2.7-onbuild

MAINTAINER Pedro Pazzini <pedro.pazzini@gmail.com>

# Bundle app source
COPY bing_send_mail.py /src/bing_send_mail.py

#EXPOSE  8000
#CMD ["python", "/src/bing_send_mail.py", "-p 8000"]
CMD ["python", "/src/bing_send_mail.py"]
