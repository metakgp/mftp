FROM python:3.10-slim

WORKDIR /code

COPY . .

RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "mftp.py"]

CMD ["--smtp"]



