# classic_developer_ml_cicle

Проект лабораторных работ по дисциплине «Инфраструктура больших данных» (ИТМО, весна 2026).

- **ЛР1**: базовый MLE-пайплайн.
- **ЛР2**: интеграция с Redis.
- **ЛР3**: управление секретами через Ansible Vault.
- **ЛР4**: интеграция Kafka Producer/Consumer + Vault + Redis.

## Ключевые компоненты (ЛР4)

- `src/api_service.py` — FastAPI сервис модели; после предсказания публикует событие в Kafka.
- `src/kafka_bus.py` — Kafka Producer abstraction.
- `src/kafka_consumer_service.py` — Kafka Consumer (чтение событий и сохранение в Redis).
- `src/prediction_store.py` — Redis store + чтение секретов Redis/Kafka из secret files/env.
- `docker/vault/*` — контейнер инициализации/выгрузки секретов Ansible Vault.
- `docker-compose.yml` — оркестрация `vault-init + kafka + redis + web + kafka-consumer + functional-tests`.

## Локальный запуск Python (без Kafka/Redis)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python3 src/preprocess.py
python3 src/train.py --model ALL --use-config
python3 src/predict.py -m RAND_FOREST -t smoke
python3 -m coverage run src/unit_tests/test_preprocess.py
python3 -m coverage run -a src/unit_tests/test_training.py
python3 -m coverage run -a src/unit_tests/test_prediction_store.py
python3 -m coverage run -a src/unit_tests/test_kafka_bus.py
python3 -m coverage run -a src/unit_tests/test_api.py
python3 -m coverage report -m
```

## ЛР4: запуск через docker-compose (Vault + Kafka + Redis)

1. Создать `.env`:

```bash
cp .env.example .env
```

2. Запуск окружения:

```bash
docker compose up --build -d vault-init kafka redis web kafka-consumer
```

3. Функциональное тестирование сценария:

```bash
docker compose --profile cd run --rm functional-tests
```

4. Остановка:

```bash
docker compose down -v
```

## API

- `GET /health`
- `POST /inference-requests/{request_key}`
- `POST /predict?model=RAND_FOREST`
- `POST /predict/from-redis?request_key=...&model=RAND_FOREST`
- `GET /predictions/{request_id}`
- `GET /consumed-events/{request_id}`

Последний endpoint подтверждает, что событие было доставлено producer-ом и обработано consumer-ом.

## Секреты

Runtime-секреты не хранятся в plaintext-конфигах:
- `vault-init` расшифровывает vault и кладёт секреты в volume;
- `web`, `redis`, `kafka-consumer` читают секреты через `*_FILE` переменные.

## CI/CD

- `CI/Jenkinsfile`: unit tests + coverage + docker compose functional tests + build/push image.
- `CD/Jenkinsfile`: запуск `vault-init/kafka/redis/web/kafka-consumer`, seed данных, functional tests, сбор логов.

## Дистрибутивы

```bash
python3 scripts/make_distribution.py --lab 1
python3 scripts/make_distribution.py --lab 2
python3 scripts/make_distribution.py --lab 3
python3 scripts/make_distribution.py --lab 4
```

- `dist/lab1_distribution.zip`
- `dist/lab2_distribution.zip`
- `dist/lab3_distribution.zip`
- `dist/lab4_distribution.zip`
