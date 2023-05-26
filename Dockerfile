FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY code/ /app

EXPOSE 8888

CMD [ "python", "app.py" ]