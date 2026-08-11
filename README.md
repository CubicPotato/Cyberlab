[![CI](https://github.com/CubicPotato/Cyberlab/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/your-repo/actions/workflows/ci.yml) [![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)

**CyberLab** — Environnement Docker pédagogique pour tests de sécurité et monitoring

Ce dépôt contient une collection de services Docker destinés à construire un laboratoire d'exercices (CyberLab) :

- Une API simple en Flask (service `api`) avec authentification basique et accès web statique.
- Un reverse-proxy `nginx` servant la page statique et proxyfiante `/api/` vers l'API.
- Un service `db` PostgreSQL initialisé avec un utilisateur `admin` par défaut.
- Un conteneur `kali` (image Kali Linux) pour simuler une machine d'attaque dans le réseau `attack`.
- Un dossier `monitoring/` proposant un déploiement Wazuh (stack de surveillance) en mode single-node.

Ce README présente l'architecture, l'installation, l'utilisation et les tests pour le projet.

**Table des matières**
- [Architecture](#architecture)
- [Prérequis](#prérequis)
- [Démarrage rapide (Docker)](#démarrage-rapide-docker)
- [Développement local (API)](#développement-local-api)
- [Tests](#tests)
- [Endpoints API](#endpoints-api)
- [Structure du dépôt](#structure-du-dépôt)
- [Contribuer](#contribuer)
- [Licence](#licence)

**Architecture**

Le fichier de composition principal est [compose.yaml](compose.yaml). Il définit 4 réseaux/volumes et les services listés ci-dessus. Le trafic HTTP public est exposé via `nginx` (port 8080 sur l'hôte), l'API écoute sur `8000` en interne et la base PostgreSQL sur `5432`.

Diagramme d'architecture (Mermaid)

```mermaid
graph LR
	NGNX[nginx (reverse-proxy)] -->|proxy /api| API[Flask API]
	NGNX --> SITE[Static site (/usr/share/nginx/html)]
	API --> DB[PostgreSQL]
	KALI[Kali container] --- ATTACK_NET((attack network))
	API --- ATTACK_NET
	MON[Wazuh Monitoring stack] --- MON_NET((monitoring network))
	NGNX --- MON_NET
	DB --- MON_NET
	API --- MON_NET
```

Remarque: remplacez `your-username/your-repo` dans les badges ci-dessus par votre nom d'utilisateur et le nom du dépôt GitHub pour activer le badge Actions.

**Prérequis**
- Docker / Docker Compose (v2 recommandé)
- (Optionnel) Python 3.12 pour exécuter l'API en local sans conteneurs

**Démarrage rapide (Docker)**

1. Copier le fichier d'environnement exemple et ajuster les variables si besoin :

```
cp .env.example .env
```

2. Construire et lancer l'ensemble du laboratoire (depuis la racine du dépôt) :

```
docker compose up --build -d
```

3. Pages accessibles :
- Frontend statique (login) via `http://localhost:8080`
- API (interne) via `http://localhost:8000` (normalement proxifiée par `nginx`)

Pour arrêter et supprimer les conteneurs :

```
docker compose down
```

Remarque : le dossier `monitoring/` contient un déploiement Wazuh séparé. Pour lancer uniquement la stack Wazuh (single-node), utilisez :

```
cd monitoring
docker compose -f docker-compose.monitoring.yml up --pull always -d
```

**Développement local (API)**

L'API Flask se trouve dans le dossier [api/app](api/app). Pour exécuter l'API sans Docker :

```
python -m venv .venv
source .venv/bin/activate    # PowerShell: .venv\Scripts\Activate.ps1
pip install -r api/requirements.txt

# Variables d'environnement requises (ex. pour PostgreSQL local)
export DB_USER=postgres
export DB_PASSWORD=password
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=postgres

cd api
python -m flask --app app run --host 0.0.0.0 --port 8000
```

L'API charge la configuration de la chaîne SQL depuis les variables d'environnement (voir [api/app/__init__.py](api/app/__init__.py)).

**Tests**

Des tests unitaires sont fournis dans `api/tests`. Ils utilisent le module `unittest` et une base SQLite en mémoire pour les tests d'intégration de l'API.

Pour exécuter les tests :

```
python -m unittest discover -s api/tests
```

**Endpoints API**

- POST `/api/login` — connexion via JSON {"login": "user", "password": "pwd"}. Retourne `{ "login": "..." }` si authentifié.
- GET `/api/me` — route protégée par HTTP Basic; renvoie l'utilisateur courant `{ "login": "..." }`.

Exemples `curl` :

```
# login
curl -X POST -H "Content-Type: application/json" -d '{"login":"admin","password":"12345"}' http://localhost:8080/api/login

# accéder à /api/me avec basic auth
curl -u admin:12345 http://localhost:8080/api/me
```

**Structure du dépôt (sélection)**
- [compose.yaml](compose.yaml) — composition principale (api, nginx, kali, db)
- [api/](api/) — code de l'API Flask
	- [api/Dockerfile](api/Dockerfile)
	- [api/requirements.txt](api/requirements.txt)
	- [api/app](api/app) — application Flask (routes, modèles, extensions)
	- [api/tests](api/tests) — tests unitaires
- [db/init](db/init) — configuration et script d'initialisation PostgreSQL
- [nginx/](nginx) — configuration et Dockerfile du reverse-proxy
- [monitoring/](monitoring) — stack Wazuh (optionnelle)



---

Si vous voulez que je rende ce README encore plus visuel (diagramme mermaid, captures d'écran, badge CI), dites-moi ce que vous préférez et je l'ajouterai.
