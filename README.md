# Wazuh Monitoring Stack

Single-node Wazuh deployment with agent monitoring via Docker Compose.

## Quick Start

```bash
# Launch the entire stack
docker compose -f docker-compose.monitoring.yml up --pull always -d

# View logs
docker compose -f docker-compose.monitoring.yml logs -f

# Stop
docker compose -f docker-compose.monitoring.yml down
```

## Access

- **Wazuh Dashboard**: https://localhost:443
  - Username: `admin`
  - Password: `SecretPassword`
- **API**: https://localhost:55000
  - Username: `wazuh-wui`
  - Password: `MyS3cr37P450r.*-`

## Components

- **wazuh.manager**: Wazuh manager (port 1514, 1515, 55000)
- **wazuh.indexer**: OpenSearch indexer (port 9200)
- **wazuh.dashboard**: Dashboard/UI (port 443)
- **wazuh.agent**: Docker monitoring agent (internal only)

## Configuration

All config files are in:
- `single-node/config/` — Manager, indexer, dashboard configs
- `wazuh-agent/config/` — Agent configuration

Certificates are pre-generated in `single-node/config/wazuh_indexer_ssl_certs/`.

## First Run

If certificates are missing:

```bash
cd single-node
docker compose -f generate-indexer-certs.yml run --rm generator
cd ..
```

## Notes

- Agent monitors Docker socket and host logs (`/var/log`, `/etc`)
- All containers use the `monitoring_network` bridge network
- Persistent volumes for manager, indexer, and dashboard data
