ARG BASE_IMAGE=python:3.11

FROM $BASE_IMAGE

ENV PYTHONUNBUFFERED=1
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV SERVICE_HOST 0.0.0.0
ENV SERVICE_PORT 5000

CMD ["python", "server.py"]
