FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

RUN python3 src/preprocess.py \
    && python3 src/train.py --model ALL --use-config

EXPOSE 8000

CMD ["python3", "-m", "uvicorn", "src.api_service:app", "--host", "0.0.0.0", "--port", "8000"]
