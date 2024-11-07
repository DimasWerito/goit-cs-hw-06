FROM python:3.9-slim

WORKDIR /app

COPY main.py ./
COPY index.html ./
COPY message.html ./
COPY error.html ./
COPY style.css ./

RUN pip install pymongo

CMD ["python", "main.py"]
