FROM python:3.13
WORKDIR /usr/local/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY parse.py dataset.csv ./

CMD ["python3", "parse.py", "dataset.csv"]