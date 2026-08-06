#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

created_env_file="false"
if [[ ! -f ".env" ]]; then
  cp .env.example .env
  created_env_file="true"
fi

cleanup() {
  docker compose down -v --remove-orphans
  if [[ "$created_env_file" == "true" ]]; then
    rm -f .env
  fi
}
trap cleanup EXIT

docker compose up -d --build db api nginx

for _ in {1..30}; do
  status_code="$(curl -s -o /tmp/cyberlab-login-ok.json -w "%{http_code}" \
    -H "Content-Type: application/json" \
    -d '{"login":"admin","password":"12345"}' \
    http://localhost:8080/api/login || true)"
  if [[ "$status_code" == "200" ]]; then
    break
  fi
  sleep 2
done

if [[ "${status_code:-}" != "200" ]]; then
  echo "Expected /api/login to return 200, got ${status_code:-none}" >&2
  docker compose logs --no-color api nginx db
  exit 1
fi

invalid_status="$(curl -s -o /tmp/cyberlab-login-bad.json -w "%{http_code}" \
  -H "Content-Type: application/json" \
  -d '{"login":"admin","password":"wrong-password"}' \
  http://localhost:8080/api/login || true)"

if [[ "$invalid_status" != "401" ]]; then
  echo "Expected invalid credentials to return 401, got ${invalid_status}" >&2
  docker compose logs --no-color api nginx db
  exit 1
fi

echo "Integration smoke test passed."
