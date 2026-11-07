#!/usr/bin/env bash
set -euo pipefail
# Opt in explicitly; existing images only, isolated network and tmpfs data.
: "${ARCVAULT_INFRA_OPT_IN:?set to yes}"
[ "$ARCVAULT_INFRA_OPT_IN" = yes ]
p=arcvault-infra-verify
cleanup() { docker rm -f "$p-client" "$p-web" "$p-worker" "$p-db" "$p-redis" >/dev/null 2>&1 || true; docker network rm "$p" >/dev/null 2>&1 || true; }
trap cleanup EXIT
docker network create "$p" >/dev/null
docker run -d --pull=never --name "$p-db" --network "$p" --network-alias db --tmpfs /var/lib/postgresql -e POSTGRES_PASSWORD=infrastructure-test postgres:18.3 >/dev/null
docker run -d --pull=never --name "$p-redis" --network "$p" --network-alias redis redis:8.6.1 redis-server --save '' --appendonly no >/dev/null
args=(--pull=never --network "$p" -v "$PWD:/workspace:ro" -w /workspace -e PYTHONPATH=/workspace -e DJANGO_SECRET_KEY=infrastructure-test -e DJANGO_DEBUG=true -e DJANGO_ALLOWED_HOSTS=web,localhost -e POSTGRES_HOST=db -e POSTGRES_USER=postgres -e POSTGRES_DB=postgres -e POSTGRES_PASSWORD=infrastructure-test -e REDIS_URL=redis://redis:6379/0 -e INTAKE_BEARER_TOKEN=infrastructure-test)
for i in {1..30}; do docker exec "$p-db" pg_isready -U postgres >/dev/null 2>&1 && break; sleep 1; done
docker run --rm "${args[@]}" arcvault-review-sol-3-web:latest python manage.py migrate --noinput >/dev/null
for role in worker web; do docker run -d --name "$p-$role" --network-alias "$role" "${args[@]}" arcvault-review-sol-3-web:latest python tests/infrastructure/runtime.py "$role" >/dev/null; done
docker run --name "$p-client" "${args[@]}" arcvault-review-sol-3-web:latest python tests/infrastructure/runtime.py verify
