# ITMO Big Data Infrastructure — Lab 1

Проект для ЛР №1 по дисциплине «Инфраструктура больших данных»:
классический жизненный цикл разработки ML-модели (Seeds dataset).

## Что реализовано

- Подготовка данных (split train/test) для датасета Wheat Seeds (UCI/Kaggle mirror).
- Классическая модель классификации (`RandomForestClassifier`).
- API сервис на FastAPI с endpoint'ами:
  - `GET /health`
  - `POST /predict`
- Unit и functional тесты (`pytest`).
- DVC pipeline для этапов prepare/train/evaluate.
- Dockerfile + docker-compose (dev/prod + functional CD profile).
- CI/CD на GitHub Actions:
  - **CI**: trigger на `pull_request` в `main`, тесты + сборка и push образа в DockerHub.
  - **CD**: trigger вручную или по успеху CI, запуск контейнера и функциональные тесты.

## Структура

- `src/ml_pipeline` — подготовка данных, обучение, оценка модели.
- `src/api` — API слой и сервис инференса.
- `scripts` — скрипты загрузки данных, подготовки, обучения, оценки, сборки дистрибутива.
- `tests` — unit/functional тесты.
- `.github/workflows` — CI/CD пайплайны.
- `notebooks` — notebook + конвертированный `.py`.

## Быстрый старт

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 scripts/download_data.py
python3 -m dvc repro
python3 -m pytest --cov=src --cov-report=term-missing -k "not container_scenario"
```

## Запуск API локально

```bash
uvicorn src.api.app:app --host 0.0.0.0 --port 8000
```

Пример запроса:

```bash
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "area": 15.26,
    "perimeter": 14.84,
    "compactness": 0.871,
    "kernel_length": 5.763,
    "kernel_width": 3.312,
    "asymmetry_coefficient": 2.221,
    "groove_length": 5.22
  }'
```

## Docker

### PROD
```bash
docker compose up --build
```

### DEV
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

### Функциональные тесты в контейнере (CD профиль)
```bash
docker compose --profile cd up --build --abort-on-container-exit --exit-code-from functional-tests
```

## DVC

```bash
python3 -m dvc repro
python3 -m dvc metrics show
```

## Конфиги, требуемые ЛР

- `config.ini`
- `Dockerfile`
- `docker-compose.yml`
- `requirements.txt`
- `dev_sec_ops.yml`
- `scenario.json`

## Примечание про GitHub/DockerHub

Для CI push образа нужны секреты репозитория:
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`
