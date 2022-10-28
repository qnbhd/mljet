ARG BASE_IMAGE=python:3.11

FROM $BASE_IMAGE
RUN apt update -y && apt install -y gcc g++ libssl-dev libcurl4-openssl-dev
ENV PYTHONUNBUFFERED=1
COPY requirements.txt requirements.txt
RUN pip install --user --no-cache-dir -r requirements.txt
COPY . .

CMD [ "python3", "app.py", "run" ]
