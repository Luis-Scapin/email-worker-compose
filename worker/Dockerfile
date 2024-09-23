FROM python:3.6

LABEL maintainer "Luis @ Cod3r Cursos"

ENV PYTHONUNBUFFERED=1

RUN python -m pip install --upgrade pip
RUN pip install redis==2.10.5 requests==2.27.1

ENTRYPOINT [ "/usr/local/bin/python" ]