FROM python:3.8-slim

COPY . /worker
WORKDIR /worker
RUN pip install -r requirements.txt
RUN chmod 644 main.py

CMD ["python", "main.py"]