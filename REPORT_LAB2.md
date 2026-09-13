# Отчёт по лабораторной работе №2

**Дисциплина:** Инфраструктура больших данных  
**Тема:** Взаимодействие с источниками данных  
**Источник данных по варианту:** Redis

## 1. Цель работы

Получить практические навыки интеграции ML-сервиса с внешним источником данных (Redis):
- чтение входных данных,
- запись результатов предсказания,
- настройка аутентификации при подключении,
- запуск функционального тестирования контейнеров через docker-compose.

## 2. Выполненные задачи

1. Взята за основу модель из ЛР1 и продолжена разработка в том же репозитории с сохранением истории коммитов.
2. Реализован слой доступа к источнику данных:
   - файл `src/prediction_store.py`;
   - backend `RedisPredictionStore` для production/CD;
   - backend `InMemoryPredictionStore` для unit-тестов.
3. Реализована интеграция API с Redis (`src/api_service.py`):
   - `POST /inference-requests/{request_key}` — запись входного запроса в Redis;
   - `POST /predict` — предсказание и сохранение результата в Redis;
   - `POST /predict/from-redis` — чтение входа из Redis + предсказание;
   - `GET /predictions/{request_id}` — чтение результата из Redis.
4. Обеспечена аутентификация/авторизация через переменные окружения:
   - `REDIS_URL`
   - `REDIS_KEY_PREFIX`
   - `PREDICTION_STORE_BACKEND`
   (в исходном коде нет захардкоженных пар логин/пароль, адресов и токенов).
5. Добавлен скрипт наполнения Redis (`src/seed_redis_data.py`) для тестовых инференс-запросов.
6. Переиспользованы и расширены CI/CD pipeline:
   - `CI/Jenkinsfile`: unit-тесты, контейнерный functional test с Redis, build+push в DockerHub;
   - `CD/Jenkinsfile`: запуск Redis+API, наполнение Redis, functional test, сбор логов.
7. Добавлены/обновлены тесты:
   - `src/unit_tests/test_prediction_store.py`;
   - `src/unit_tests/test_api.py`.
8. Реализован сценарий функционального тестирования контейнера `scenario.json` + `src/functional_api_test.py`.

## 3. Docker Compose

`docker-compose.yml` содержит сервисы:
- `redis` — источник данных с паролем (`--requirepass`);
- `web` — API модели;
- `web-dev` — dev-профиль;
- `functional-tests` — запуск сценария тестирования.

Для конфигурации используется `.env` (шаблон `.env.example`).

## 4. Результаты тестирования

Локально подтверждены:
- подготовка данных и обучение моделей;
- smoke/functional проверки модели;
- unit/API тесты с покрытием;
- функциональный сценарий API (включая сохранение и чтение из Redis) в контейнерном профиле.

## 5. Ссылки и артефакты

- Репозиторий GitHub: `https://github.com/mshanturov/classic_developer_ml_cicle`
- DockerHub image: `https://hub.docker.com/r/mshanturov/classic_developer_ml_cicle`
- Дистрибутив ЛР2: `dist/lab2_distribution.zip`

## 6. Вывод

В лабораторной работе №2 реализован production-like поток работы ML-сервиса с внешним источником данных Redis:
- безопасное подключение через переменные окружения,
- чтение/запись данных инференса,
- запуск и функциональная проверка в docker-compose,
- переиспользование CI/CD для автоматизации процесса поставки.
