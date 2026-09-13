# classic_developer_ml_cicle

Классический MLE-проект в стиле `mle-template`, адаптированный под ЛР №1
по курсу «Инфраструктура больших данных» (ИТМО, весна 2026).

## Структура (как в шаблоне)

- `src/preprocess.py` — подготовка и split данных.
- `src/train.py` — обучение набора классических моделей.
- `src/predict.py` — smoke/func тестирование обученных моделей.
- `src/logger.py` — логирование.
- `src/api_service.py` — FastAPI API для инференса.
- `src/unit_tests` — unit/API тесты.
- `tests/test_*.json` — функциональные JSON-сценарии.
- `CI/Jenkinsfile` — CI pipeline.
- `CD/Jenkinsfile` — CD pipeline.
- `Dockerfile`, `docker-compose.yml`, `config.ini`, `requirements.txt`, `dev_sec_ops.yml`, `scenario.json`.

## Запуск локально

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 src/preprocess.py
python3 src/train.py --model ALL --use-config
python3 src/predict.py -m RAND_FOREST -t smoke
coverage run src/unit_tests/test_preprocess.py
coverage run -a src/unit_tests/test_training.py
coverage run -a src/unit_tests/test_api.py
coverage report -m
```

## API

```bash
python3 -m uvicorn src.api_service:app --host 0.0.0.0 --port 8000
```

- `GET /health`
- `POST /predict?model=RAND_FOREST`

## Docker

```bash
docker compose up --build web
```

Dev-режим:

```bash
docker compose --profile dev up --build web-dev
```

Функциональное тестирование контейнера (CD-этап):

```bash
docker compose --profile cd run --rm functional-tests
```

## DVC

```bash
python3 -m dvc add data
```

После этого в git коммитится `data.dvc`, сами данные остаются в DVC-кеше.
