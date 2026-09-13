FROM python:3.12-slim

ARG BOOTSTRAP_VAULT_PASSWORD=lab3-vault-password
ARG BOOTSTRAP_REDIS_PASSWORD=lab3-redis-password
ARG BOOTSTRAP_KAFKA_BOOTSTRAP_SERVERS=kafka:9092
ARG BOOTSTRAP_KAFKA_TOPIC=model-predictions
ARG BOOTSTRAP_KAFKA_GROUP_ID=model-prediction-consumer

ENV BOOTSTRAP_VAULT_PASSWORD=${BOOTSTRAP_VAULT_PASSWORD}
ENV BOOTSTRAP_REDIS_PASSWORD=${BOOTSTRAP_REDIS_PASSWORD}
ENV BOOTSTRAP_KAFKA_BOOTSTRAP_SERVERS=${BOOTSTRAP_KAFKA_BOOTSTRAP_SERVERS}
ENV BOOTSTRAP_KAFKA_TOPIC=${BOOTSTRAP_KAFKA_TOPIC}
ENV BOOTSTRAP_KAFKA_GROUP_ID=${BOOTSTRAP_KAFKA_GROUP_ID}

WORKDIR /vault

RUN pip install --no-cache-dir ansible-core==2.17.8 pyyaml==6.0.2

COPY docker/vault/init_vault.sh /vault/init_vault.sh
COPY docker/vault/export_secrets.sh /vault/export_secrets.sh

RUN chmod +x /vault/init_vault.sh /vault/export_secrets.sh && /vault/init_vault.sh

CMD ["/vault/export_secrets.sh"]
