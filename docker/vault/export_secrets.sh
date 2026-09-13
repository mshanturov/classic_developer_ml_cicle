#!/usr/bin/env sh
set -eu

if [ -z "${ANSIBLE_VAULT_PASSWORD:-}" ]; then
  echo "ANSIBLE_VAULT_PASSWORD is required"
  exit 1
fi

mkdir -p /vault/output

printf "%s" "${ANSIBLE_VAULT_PASSWORD}" > /tmp/.vault_pass
ansible-vault view /vault/store/infra_secrets.vault --vault-password-file /tmp/.vault_pass > /tmp/infra_secrets.yml

python3 - <<'PY'
from pathlib import Path
import yaml

secret_data = yaml.safe_load(Path('/tmp/infra_secrets.yml').read_text(encoding='utf-8'))
redis_data = secret_data['redis']
kafka_data = secret_data['kafka']

output = Path('/vault/output')
output.mkdir(parents=True, exist_ok=True)
(output / 'redis_host').write_text(str(redis_data['host']), encoding='utf-8')
(output / 'redis_port').write_text(str(redis_data['port']), encoding='utf-8')
(output / 'redis_db').write_text(str(redis_data['db']), encoding='utf-8')
(output / 'redis_password').write_text(str(redis_data['password']), encoding='utf-8')
(output / 'kafka_bootstrap_servers').write_text(str(kafka_data['bootstrap_servers']), encoding='utf-8')
(output / 'kafka_topic').write_text(str(kafka_data['topic']), encoding='utf-8')
(output / 'kafka_group_id').write_text(str(kafka_data['group_id']), encoding='utf-8')
PY

rm -f /tmp/infra_secrets.yml /tmp/.vault_pass

echo "Vault secrets exported successfully"
