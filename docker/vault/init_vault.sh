#!/usr/bin/env sh
set -eu

mkdir -p /vault/store

cat > /tmp/redis_secrets.yml <<EOF
redis:
  host: redis
  port: 6379
  db: 0
  password: ${BOOTSTRAP_REDIS_PASSWORD}
EOF

printf "%s" "${BOOTSTRAP_VAULT_PASSWORD}" > /tmp/.vault_pass
ansible-vault encrypt /tmp/redis_secrets.yml \
  --output /vault/store/redis_secrets.vault \
  --vault-password-file /tmp/.vault_pass

rm -f /tmp/redis_secrets.yml /tmp/.vault_pass
