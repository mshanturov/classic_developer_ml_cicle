FROM python:3.12-slim

ARG BOOTSTRAP_VAULT_PASSWORD=lab3-vault-password
ARG BOOTSTRAP_REDIS_PASSWORD=lab3-redis-password

ENV BOOTSTRAP_VAULT_PASSWORD=${BOOTSTRAP_VAULT_PASSWORD}
ENV BOOTSTRAP_REDIS_PASSWORD=${BOOTSTRAP_REDIS_PASSWORD}

WORKDIR /vault

RUN pip install --no-cache-dir ansible-core==2.17.8 pyyaml==6.0.2

COPY docker/vault/init_vault.sh /vault/init_vault.sh
COPY docker/vault/export_secrets.sh /vault/export_secrets.sh

RUN chmod +x /vault/init_vault.sh /vault/export_secrets.sh && /vault/init_vault.sh

CMD ["/vault/export_secrets.sh"]
