# Отчёт по лабораторной работе №1

**Дисциплина:** Инфраструктура больших данных  
**Тема:** Классический жизненный цикл разработки моделей машинного обучения  
**Датасет:** Wheat Seeds (UCI / Kaggle mirror)

---

## 1. Цель работы

Получить практические навыки построения CI/CD pipeline для ML-модели:
от подготовки данных и обучения до контейнеризации и автоматического тестирования.

## 2. Выполненные этапы

1. Создан отдельный ML-проект в git-репозитории с коммит-историей.
2. Реализована подготовка данных:
   - загрузка датасета;
   - разбиение на train/test.
3. Построена классическая модель классификации (`RandomForestClassifier`).
4. Реализован API-сервис FastAPI с методом предсказания.
5. Код покрыт тестами:
   - unit тесты подготовки данных;
   - unit тесты обучения/оценки;
   - API тесты валидации и успешного предсказания;
   - функциональный сценарий контейнера.
6. Интегрирован DVC pipeline (`prepare -> train -> evaluate`).
7. Добавлены Dockerfile и docker-compose для запуска сервиса.
8. Подготовлены обязательные конфигурационные файлы:
   - `config.ini`
   - `Dockerfile`
   - `docker-compose.yml`
   - `requirements.txt`
   - `dev_sec_ops.yml`
   - `scenario.json`
9. Настроен CI pipeline (`.github/workflows/ci.yml`):
   - trigger по PR в `main`;
   - прогон тестов;
   - сборка и push docker image в DockerHub.
10. Настроен CD pipeline (`.github/workflows/cd.yml`):
   - trigger вручную или по завершению CI;
   - запуск контейнеров;
   - функциональное тестирование контейнера по сценарию.
11. Сформирован дистрибутив в zip-архиве (`dist/lab1_distribution.zip`).

## 3. Метрики и артефакты

- Метрики качества сохраняются в:
  - `artifacts/metrics.json`
  - `artifacts/metrics_cd.json`
- Обученная модель:
  - `artifacts/model.joblib`

## 4. Ссылки (для заполнения после публикации)

- Репозиторий GitHub: `TODO`
- Docker image в DockerHub: `TODO`
- Zip-дистрибутив: `dist/lab1_distribution.zip`

## 5. Комментарии по качеству реализации

Учтены типичные замечания по ЛР:
- нет широких `except Exception`;
- API-обработка запросов через строгую валидацию Pydantic;
- healthcheck в compose выполнен через `sh + curl`;
- код организован в ООП-структуре (классы preprocessor/trainer/evaluator/service);
- разделены dev/prod сценарии docker-compose.
