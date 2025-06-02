FROM python:3.8-slim

RUN pip install flask

COPY serve.py /serve.py
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["/entrypoint.sh"]
