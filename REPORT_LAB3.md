# Отчёт по лабораторной работе №3

**Дисциплина:** Инфраструктура больших данных  
**Тема:** Размещение секретов в хранилище  
**Хранилище по варианту:** Ansible Vault

## 1. Цель

Получить навыки хранения секретов в защищённом хранилище и использования этих секретов в сервисе модели при доступе к БД.

## 2. Что было сделано

1. ЛР3 выполнена в отдельной ветке `lab3`, ответвлённой от ветки ЛР2 (`lab2`).
2. Добавлен отдельный контейнер хранилища секретов `vault-init`:
   - `docker/vault/Dockerfile`
   - `docker/vault/init_vault.sh`
   - `docker/vault/export_secrets.sh`
3. Инициализация Ansible Vault выполняется на этапе **сборки контейнера** `vault-init`:
   - создаётся временный YAML с данными Redis;
   - данные шифруются `ansible-vault encrypt`;
   - plaintext удаляется.
4. При запуске контейнера `vault-init` секреты расшифровываются и публикуются в shared volume.
5. Сервис модели и Redis используют секреты только из файлов в volume:
   - `REDIS_HOST_FILE`
   - `REDIS_PORT_FILE`
   - `REDIS_DB_FILE`
   - `REDIS_PASSWORD_FILE`
6. В сервисе модели реализовано получение секретов при обращении к БД:
   - `src/prediction_store.py` собирает Redis URL из secret files/env;
   - `src/api_service.py` использует этот слой доступа при каждом обращении к Redis.
7. Локальные конфигурационные файлы с реальными секретами не хранятся в git:
   - только шаблон `.env.example`.
8. Переиспользованы и обновлены CI/CD pipeline:
   - `CI/Jenkinsfile`;
   - `CD/Jenkinsfile`.
9. Добавлены/обновлены тесты и функциональный сценарий:
   - `src/unit_tests/test_prediction_store.py`;
   - `src/unit_tests/test_api.py`;
   - `src/functional_api_test.py`.

## 3. Docker Compose

`docker-compose.yml` включает сервисы:
- `vault-init` — инициализация/выгрузка секретов из Ansible Vault;
- `redis` — БД с `requirepass` из secret volume;
- `web` — API модели;
- `functional-tests` — функциональная проверка по сценарию.

## 4. Безопасность

- В исходном коде нет хардкоженных пар логин/пароль к Redis для runtime.
- Секреты runtime поступают из хранилища (Ansible Vault → volume).
- Шаблон `.env.example` не содержит реальных секретов.

## 5. CI/CD

- CI: unit tests + coverage + функциональные контейнерные тесты (`vault-init + redis + web`) + build/push docker image.
- CD: запуск контейнеров, заполнение Redis тестовыми данными, функциональная проверка, сбор логов.

## 6. Результаты

- Репозиторий: `https://github.com/mshanturov/classic_developer_ml_cicle`
- Ветка ЛР3: `lab3`
- DockerHub image: `https://hub.docker.com/r/mshanturov/classic_developer_ml_cicle`
- Дистрибутив ЛР3: `dist/lab3_distribution.zip`

## 7. Вывод

В ЛР3 реализован полный цикл работы с секретами:
- секреты для доступа к Redis помещаются в Ansible Vault,
- извлекаются при запуске контейнеров,
- используются сервисом модели без хранения в локальных конфигурациях.
