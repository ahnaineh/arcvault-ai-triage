#!/usr/bin/env bash
set -euo pipefail
# Opt in explicitly; existing images only, isolated network and tmpfs data.
: "${ARCVAULT_INFRA_OPT_IN:?set to yes}"
[ "$ARCVAULT_INFRA_OPT_IN" = yes ]
p=arcvault-infra-$(cat /proc/sys/kernel/random/uuid)
containers=()
network_id=
cleanup() {
  trap - EXIT INT TERM
  for id in "${containers[@]}"; do docker rm -f "$id" >/dev/null 2>&1 || true; done
  if [ -n "$network_id" ]; then docker network rm "$network_id" >/dev/null 2>&1 || true; fi
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
network_id=$(docker network create "$p")
start() {
  local id
  id=$(docker create "$@")
  containers+=("$id")
  docker start "$id" >/dev/null
}
start --pull=never --name "$p-db" --network "$p" --network-alias db --tmpfs /var/lib/postgresql -e POSTGRES_PASSWORD=infrastructure-test postgres:18.3
start --pull=never --name "$p-redis" --network "$p" --network-alias redis redis:8.6.1 redis-server --save '' --appendonly no
args=(--pull=never --network "$p" -v "$PWD:/workspace:ro" -w /workspace -e PYTHONPATH=/workspace -e DJANGO_SECRET_KEY=infrastructure-test -e DJANGO_DEBUG=true -e DJANGO_ALLOWED_HOSTS=web,localhost -e POSTGRES_HOST=db -e POSTGRES_USER=postgres -e POSTGRES_DB=postgres -e POSTGRES_PASSWORD=infrastructure-test -e REDIS_URL=redis://redis:6379/0 -e INTAKE_BEARER_TOKEN=infrastructure-test)
for i in {1..30}; do docker exec "$p-db" pg_isready -U postgres >/dev/null 2>&1 && break; sleep 1; done
start "${args[@]}" arcvault-review-sol-3-web:latest python manage.py migrate --noinput
docker wait "${containers[-1]}" | grep -qx 0
for role in worker web; do start --name "$p-$role" --network-alias "$role" "${args[@]}" arcvault-review-sol-3-web:latest python tests/infrastructure/runtime.py "$role" >/dev/null; done
start --name "$p-client" "${args[@]}" arcvault-review-sol-3-web:latest python tests/infrastructure/runtime.py verify
docker logs -f "${containers[-1]}"
docker wait "${containers[-1]}" | grep -qx 0
