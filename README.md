# classic_developer_ml_cicle

Проект лабораторных работ по дисциплине «Инфраструктура больших данных» (ИТМО, весна 2026).

- **ЛР1**: классический MLE-пайплайн (подготовка данных, обучение, API, тесты, DVC, Docker, CI/CD).
- **ЛР2**: взаимодействие модели с источником данных **Redis** (входные запросы + сохранение результатов предсказаний).

## Структура проекта

- `src/preprocess.py` — подготовка данных и train/test split.
- `src/train.py` — обучение классических моделей.
- `src/predict.py` — smoke/func проверки моделей.
- `src/api_service.py` — FastAPI сервис модели.
- `src/prediction_store.py` — слой доступа к Redis (или in-memory backend для тестов).
- `src/seed_redis_data.py` — наполнение Redis тестовыми запросами для инференса.
- `src/functional_api_test.py` — сценарий функционального теста контейнеров.
- `src/unit_tests` — unit/API тесты.
- `CI/Jenkinsfile`, `CD/Jenkinsfile` — CI/CD pipeline.

## Требования

- Python 3.11+
- Docker + Docker Compose

## Подготовка окружения

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Базовый запуск ML-пайплайна

```bash
python3 src/preprocess.py
python3 src/train.py --model ALL --use-config
python3 src/predict.py -m RAND_FOREST -t smoke
python3 src/predict.py -m RAND_FOREST -t func
```

## Запуск API локально (ЛР2)

Для локального запуска без Redis можно включить in-memory backend:

```bash
PREDICTION_STORE_BACKEND=inmemory python3 -m uvicorn src.api_service:app --host 0.0.0.0 --port 8000
```

Для запуска с Redis передай `REDIS_URL` и `REDIS_KEY_PREFIX`.

## Docker Compose (обязательно для ЛР2)

1. Создать `.env` из шаблона:

```bash
cp .env.example .env
```

2. Запустить сервис модели + Redis:

```bash
docker compose up --build redis web
```

3. Прогнать функциональный тест контейнеров:

```bash
docker compose --profile cd run --rm functional-tests
```

4. Остановить:

```bash
docker compose down -v
```

## Примеры API (с Redis)

- `POST /inference-requests/{request_key}` — сохранить входные признаки в Redis.
- `POST /predict` — выполнить предсказание и записать результат в Redis.
- `POST /predict/from-redis` — взять вход из Redis и выполнить предсказание.
- `GET /predictions/{request_id}` — получить сохранённый результат по request_id.

## Тесты

```bash
python3 -m coverage run src/unit_tests/test_preprocess.py
python3 -m coverage run -a src/unit_tests/test_training.py
python3 -m coverage run -a src/unit_tests/test_prediction_store.py
python3 -m coverage run -a src/unit_tests/test_api.py
python3 -m coverage report -m
```

## DVC

```bash
python3 -m dvc add data
```

## Дистрибутивы

```bash
python3 scripts/make_distribution.py --lab 1
python3 scripts/make_distribution.py --lab 2
```

- `dist/lab1_distribution.zip`
- `dist/lab2_distribution.zip`
