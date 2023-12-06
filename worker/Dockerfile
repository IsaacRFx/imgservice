FROM python:3.10.11-bullseye


COPY . /worker
WORKDIR /worker
RUN pip install -r requirements.txt
RUN chmod 644 worker.py

CMD ["python", "worker.py"]