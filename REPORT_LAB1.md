# Отчёт по ЛР №1

## Тема
Классический жизненный цикл разработки ML-модели.

## Что сделано

1. Проект перестроен в стиле шаблона `mle-template`:
   - структура `src/preprocess.py`, `src/train.py`, `src/predict.py`, `src/logger.py`;
   - `CI/Jenkinsfile` и `CD/Jenkinsfile`;
   - unit-тесты в `src/unit_tests` и JSON-тесты в `tests`.
2. Датасет Wheat Seeds подготовлен, выделены train/test.
3. Обучены классические модели (LogReg, RandomForest, KNN, SVM, GNB, DecisionTree).
4. Реализован API (`src/api_service.py`) с endpoint `/predict`.
5. Добавлена контейнеризация (Dockerfile, docker-compose).
6. Добавлен DVC (`data.dvc`) для версионирования данных.
7. Реализованы CI/CD pipeline (Jenkins):
   - CI: подготовка, обучение, тесты, сборка и push образа;
   - CD: запуск контейнера и функциональные API-тесты по `scenario.json`.

## Обязательные артефакты

- `config.ini`
- `Dockerfile`
- `docker-compose.yml`
- `requirements.txt`
- `dev_sec_ops.yml`
- `scenario.json`
- `CI/Jenkinsfile`
- `CD/Jenkinsfile`

## Результат

- Репозиторий: `https://github.com/mshanturov/classic_developer_ml_cicle.git`
- Docker image: `mshanturov/classic_developer_ml_cicle` (push выполняется CI)
- Дистрибутив: `dist/lab1_distribution.zip`
