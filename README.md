# Cyberlab

Cyberlab is a containerized security lab combining:
- a small web application stack (`nginx` + `api` + `postgres`)
- an attacker workstation (`kali`)
- a Wazuh monitoring stack (`wazuh manager/indexer/dashboard + agent`)

This repository is intended for security learning, detection engineering, and controlled offensive/defensive exercises.

## Architecture boundaries

### Attack lab boundary (`/home/runner/work/Cyberlab/Cyberlab/compose.yaml`)
- `nginx` serves `/api/site/index.html` and proxies `/api/*` to Flask.
- `api` exposes login/auth endpoints and reads users from PostgreSQL.
- `db` stores users and seeded lab data.
- `kali` lives on the attack network for traffic generation and attack simulation.

Networks:
- `monitoring_network`: application and telemetry path.
- `star_wars`: attack surface network (`nginx` + `kali`).

### Monitoring boundary (`/home/runner/work/Cyberlab/Cyberlab/monitoring/docker-compose.monitoring.yml`)
- `wazuh.agent` collects Docker/host logs.
- `wazuh.manager` processes events and applies rules.
- `wazuh.indexer` stores security events (OpenSearch).
- `wazuh.dashboard` provides UI and alert investigation.

Custom detection content:
- Decoder: `/home/runner/work/Cyberlab/Cyberlab/monitoring/wazuh-manager/decoders/local_decoder.xml`
- Rule: `/home/runner/work/Cyberlab/Cyberlab/monitoring/wazuh-manager/rules/local_rules.xml`

## Quick start

### 1) Start the application lab
```bash
cd /home/runner/work/Cyberlab/Cyberlab
cp .env.example .env
docker compose up --build -d
```

Access:
- Web UI: `http://localhost:8080`
- API via proxy: `http://localhost:8080/api/login`
- PostgreSQL: `localhost:5432`

Default seeded credentials:
- login: `admin`
- password: `12345`

### 2) Start monitoring stack
```bash
cd /home/runner/work/Cyberlab/Cyberlab/monitoring
cp .env.example .env
docker compose -f docker-compose.monitoring.yml up --pull always -d
```

If indexer certificates are missing:
```bash
cd /home/runner/work/Cyberlab/Cyberlab/monitoring/single-node
docker compose -f generate-indexer-certs.yml run --rm generator
```

Dashboard:
- `https://localhost:443`

## Development workflow

### API local run (without Docker)
```bash
cd /home/runner/work/Cyberlab/Cyberlab/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DB_USER=postgres
export DB_PASSWORD=password
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=postgres
python -m flask --app app run --host 0.0.0.0 --port 8000
```

### Security mode toggle
- Default mode: hashed password verification.
- Optional training mode (intentionally insecure plaintext auth):
  set `ALLOW_INSECURE_PLAINTEXT_AUTH=true` in Flask config overrides for controlled exercises only.

## Test commands

### Unit tests
```bash
cd /home/runner/work/Cyberlab/Cyberlab
PYTHONPATH=api python -m unittest discover -s api/tests -p "test_*.py"
```

### Integration smoke test (real containers)
```bash
cd /home/runner/work/Cyberlab/Cyberlab
scripts/integration_smoke_test.sh
```

## CI quality gate

Workflow: `/home/runner/work/Cyberlab/Cyberlab/.github/workflows/ci.yml`

It enforces:
- Python lint (`ruff`)
- YAML lint (`yamllint`)
- shell lint (`shellcheck`)
- Dockerfile lint (`hadolint`)
- unit tests
- containerized integration smoke test
- dependency vulnerability scan (`pip-audit`)
- API image vulnerability scan (`trivy`)

## Troubleshooting

- Missing environment variables at API startup:
  ensure `.env` exists in repository root and contains DB values.
- `api` not healthy:
  `docker compose logs api db`.
- `nginx` not healthy:
  `docker compose logs nginx`.
- monitoring stack startup issues:
  verify certs and run `docker compose -f docker-compose.monitoring.yml logs -f`.
- Wazuh alerts not appearing:
  confirm `wazuh.agent` can read `/var/lib/docker/containers` and manager connection settings.

## Threat model and intentional insecurity

Cyberlab is for controlled security practice.

Intentionally high-risk elements may be present during exercises:
- exposed test credentials
- attack tooling in `kali`
- optional insecure auth mode for demonstrations

Do not deploy this stack as-is in production. Restrict execution to isolated lab environments.
