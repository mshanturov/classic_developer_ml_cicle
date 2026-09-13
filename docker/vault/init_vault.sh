#!/usr/bin/env sh
set -eu

mkdir -p /vault/store

cat > /tmp/infra_secrets.yml <<EOF
redis:
  host: redis
  port: 6379
  db: 0
  password: ${BOOTSTRAP_REDIS_PASSWORD}
kafka:
  bootstrap_servers: ${BOOTSTRAP_KAFKA_BOOTSTRAP_SERVERS}
  topic: ${BOOTSTRAP_KAFKA_TOPIC}
  group_id: ${BOOTSTRAP_KAFKA_GROUP_ID}
EOF

printf "%s" "${BOOTSTRAP_VAULT_PASSWORD}" > /tmp/.vault_pass
ansible-vault encrypt /tmp/infra_secrets.yml \
  --output /vault/store/infra_secrets.vault \
  --vault-password-file /tmp/.vault_pass

rm -f /tmp/infra_secrets.yml /tmp/.vault_pass
