# Отчёт по лабораторной работе №4

**Дисциплина:** Инфраструктура больших данных  
**Тема:** Интеграция Apache Kafka сервиса  
**Контекст:** продолжение ЛР3 (Vault + Redis)

## 1. Цель работы

Реализовать Kafka Producer и Kafka Consumer, интегрировать их с сервисом модели и сохранить безопасную схему работы с секретами.

## 2. Выполненные задачи

1. Создана отдельная ветка `lab4`, ответвлённая от `lab3`.
2. Реализован Kafka Producer на уровне сервиса модели:
   - `src/kafka_bus.py`
   - API после предсказания публикует событие `prediction.created` в Kafka.
3. Реализован Kafka Consumer отдельным сервисом в контейнере:
   - `src/kafka_consumer_service.py`
   - consumer принимает события из Kafka и сохраняет их в Redis.
4. Выполнена интеграция Kafka c сервисом секретов (Ansible Vault):
   - `vault-init` контейнер хранит в vault не только Redis-секреты, но и Kafka-параметры;
   - `export_secrets.sh` выгружает секреты в shared volume;
   - `web` и `kafka-consumer` читают `KAFKA_*_FILE` и `REDIS_*_FILE`.
5. Сохранено защищённое обращение к БД (Redis):
   - пароль Redis не хранится в локальных plaintext конфигурациях.
6. Переиспользованы и расширены CI/CD pipeline:
   - `CI/Jenkinsfile`
   - `CD/Jenkinsfile`
7. Подготовлено функциональное тестирование сценария producer/consumer:
   - `src/functional_api_test.py`
   - `scenario.json`
   - проверка endpoint `GET /consumed-events/{request_id}`.

## 3. Архитектура ЛР4

Сервисы `docker-compose`:
- `vault-init` — инициализация и расшифровка vault;
- `kafka` — брокер сообщений;
- `redis` — хранилище данных модели/событий;
- `web` — API модели + Kafka producer;
- `kafka-consumer` — обработчик Kafka событий;
- `functional-tests` — сценарные проверки.

Поток данных:
1. `POST /predict` -> модель выдаёт результат;
2. результат сохраняется в Redis;
3. producer отправляет событие в Kafka;
4. consumer читает событие и сохраняет отметку обработки в Redis;
5. `GET /consumed-events/{request_id}` подтверждает факт обработки consumer-ом.

## 4. Секреты

Используются секреты из Ansible Vault:
- Redis: host, port, db, password;
- Kafka: bootstrap_servers, topic, group_id.

Реальные значения не хранятся в git, локально используется `.env.example` как шаблон.

## 5. Результаты

- Репозиторий: `https://github.com/mshanturov/classic_developer_ml_cicle`
- Ветка ЛР4: `lab4`
- DockerHub image: `https://hub.docker.com/r/mshanturov/classic_developer_ml_cicle`
- Дистрибутив ЛР4: `dist/lab4_distribution.zip`

## 6. Вывод

В ЛР4 реализована интеграция Kafka producer/consumer с ML API и сохранена защищённая схема работы с Redis через Vault. Решение разворачивается через docker-compose и проверяется функциональными тестами в CI/CD.
