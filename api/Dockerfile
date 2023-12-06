FROM python:3.10.11-bullseye

COPY . /worker
WORKDIR /worker
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN chmod 644 main.py

CMD ["python", "main.py"]