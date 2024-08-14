# syntax=docker/dockerfile:1.4
FROM python

WORKDIR /code
COPY requirements.txt /code
RUN pip3 install -r requirements.txt

COPY . .

ENV FLASK_APP server.py
ENV FLASK_ENV development
ENV FLASK_RUN_PORT 6000
ENV FLASK_RUN_HOST 0.0.0.0

EXPOSE 6000

CMD ["flask", "run"]
