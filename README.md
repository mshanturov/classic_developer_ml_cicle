# classic_developer_ml_cicle

Проект лабораторных работ по дисциплине «Инфраструктура больших данных» (ИТМО, весна 2026).

- **ЛР1**: классический MLE-пайплайн (подготовка данных, обучение, API, тесты, DVC, Docker, CI/CD).
- **ЛР2**: интеграция API модели с Redis.
- **ЛР3**: хранение секретов через **Ansible Vault** и получение секретов при доступе к Redis.

## Структура

- `src/preprocess.py` — подготовка данных и split.
- `src/train.py` — обучение моделей.
- `src/predict.py` — smoke/func проверка.
- `src/prediction_store.py` — работа с Redis и сборка URL из секретов.
- `src/api_service.py` — FastAPI API с Redis-backed хранилищем предсказаний.
- `src/seed_redis_data.py` — загрузка тестовых запросов в Redis.
- `src/functional_api_test.py` — e2e сценарий API.
- `docker/vault/*` — инициализация/использование Ansible Vault в отдельном контейнере.
- `CI/Jenkinsfile`, `CD/Jenkinsfile` — CI/CD pipeline.

## Локальный запуск (Python)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python3 src/preprocess.py
python3 src/train.py --model ALL --use-config
python3 src/predict.py -m RAND_FOREST -t smoke
```

Для API без Redis можно использовать in-memory backend:

```bash
PREDICTION_STORE_BACKEND=inmemory python3 -m uvicorn src.api_service:app --host 0.0.0.0 --port 8000
```

## ЛР3: запуск через docker-compose (Vault + Redis)

1. Скопировать шаблон env:

```bash
cp .env.example .env
```

2. Запустить контейнеры:

```bash
docker compose up --build -d vault-init redis web
```

3. Прогнать функциональный тест:

```bash
docker compose --profile cd run --rm functional-tests
```

4. Остановить окружение:

```bash
docker compose down -v
```

### Что происходит в ЛР3

- Контейнер `vault-init` на этапе сборки создаёт зашифрованный vault-файл с секретами Redis.
- При старте `vault-init` расшифровывает секреты (по `ANSIBLE_VAULT_PASSWORD`) и кладёт их в общий volume.
- `redis` и `web` читают секреты только из volume (`*_FILE`), а не из локальных конфигов.
- API-сервис использует эти секреты для подключения к Redis.

## API (Redis-backed)

- `GET /health`
- `POST /inference-requests/{request_key}`
- `POST /predict?model=RAND_FOREST`
- `POST /predict/from-redis?request_key=...&model=RAND_FOREST`
- `GET /predictions/{request_id}`

## Тесты

```bash
python3 -m coverage erase
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
python3 scripts/make_distribution.py --lab 3
```

- `dist/lab1_distribution.zip`
- `dist/lab2_distribution.zip`
- `dist/lab3_distribution.zip`
