FROM python:3.12-slim

WORKDIR /app

COPY main.py /app/
COPY preprocessing.py /app/
COPY bayesian_optimization.py /app/
COPY bot_initialize.py /app/
COPY api_keys.py /app/
COPY requirements.txt /app/
COPY btc_data.csv /app/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]