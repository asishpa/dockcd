# DockCD

DockCD is a deployment and operations platform for Docker Compose environments.
It gives application teams self-service control over routine operations that were previously handled manually by DevOps.

## What Problem We Had And How DockCD Solves It

### Problem: Teams had to ask DevOps to run routine commands

Developers and customer support teams needed DevOps support for common tasks like setup and maintenance commands.

Solution:
DockCD allows controlled self-service command execution. Commands are approved first, then executed through the platform by authorized users.

### Problem: Logs were not easily available to the people debugging issues

Developers often had to wait for DevOps to fetch deployment or container logs.

Solution:
DockCD centralizes logs and also supports live streaming while deployment or runtime events are happening.

### Problem: Deployments were manual and repetitive

The old flow required pushing code, logging in to servers, pulling code manually, and running Docker Compose manually in each folder.

Solution:
DockCD automates deployment execution with queued handling, controlled ordering, and both manual and webhook-driven triggers.

### Problem: Operational access was hard to control safely

Different users needed different levels of power, but manual workflows made this difficult to enforce consistently.

Solution:
DockCD applies role-based access control so sensitive actions stay restricted while day-to-day work remains self-service.

## How Features Work

### Authentication and user management

DockCD starts by bootstrapping an admin user. After that, users authenticate and receive role-based access.
Admins manage account lifecycle tasks like creating users, enabling/disabling users, and resetting passwords.

### RBAC

DockCD uses three operational roles:

- Admin
- Developer
- Viewer

Each role has a different capability boundary. This keeps high-risk operations limited while still allowing developers to work independently.

### Application registration

Application registration is where deployment context is defined once and reused everywhere.

During registration, teams provide:

- repository source information
- target branch
- deployment path on the server

How deployment path is handled:

- the path acts as the root location for that application's deployed files
- the system uses this path consistently during deployment execution and related service operations
- path rules ensure the deployment stays within the expected managed area

### Service setup and deployment order

After an application is registered, services are attached to it.
Each service points to its compose configuration and runtime location.

How deployment order is handled:

- services are assigned an execution order
- when a deployment starts, service deployments follow that configured order
- if a service is already being deployed, new work is queued and processed next
- this prevents out-of-order rollouts and avoids overlapping actions on the same service

### Command allowlist

DockCD does not treat command execution as open shell access.

How it works:

- commands are approved and registered first
- when a user runs a command, the request is validated against the approved list
- unauthorized commands are rejected

This is the core control that makes self-service command execution safe.

### Deployment management

Deployments can be started manually or triggered automatically from source-control events.
Each deployment is tracked through lifecycle states, and progress is visible through logs.

### Realtime logging

Log output is captured during execution and made available in two ways:

- persisted history for later review
- live stream for active troubleshooting

### Webhook-driven automation

DockCD can receive source-control events and decide what needs deployment.
It ignores duplicate or irrelevant events and only schedules work that matches configured services.

### Alerts

DockCD supports rule-based alerts and notification channels for runtime issues so teams can respond quickly when containers are unhealthy.

## Architecture Details

DockCD is organized into five runtime layers:

- request layer for user actions
- webhook layer for incoming repository events
- execution layer for deployments and service actions
- realtime layer for streaming output
- data layer for persistent state and history

How these layers work together:

- users register applications and services
- deployments are created from user action or webhook events
- execution workers process deployments in order
- locks prevent overlapping work for the same service
- logs are streamed in realtime and stored for history
- role checks are applied before privileged actions

## End-to-End Deployment Flow

1. Application and services are configured, including deployment path and service order.
2. A deployment request is created manually or from a webhook.
3. The system creates service-level deployment tasks in the configured order.
4. The executor processes each task and prevents overlap using per-service locking.
5. Deployment output is streamed and stored.
6. Queued work continues automatically until all related services are completed.

## Operational Guarantees

- one active deployment per service at a time
- ordered processing across services in a deployment
- full deployment history and logs retained
- live visibility while deployments are running
- role-gated access for privileged operations

## Summary

DockCD replaces manual server-side deployment operations with a controlled, self-service platform.
It improves speed, visibility, and safety by combining command control, realtime logs, automated deployment flow, and RBAC in one system.

## Server Deployment Guide (Production)

This section explains how to deploy DockCD on a Linux server with Docker Compose, including:

- required containers
- volume mounts
- folder permissions needed for repository cloning and service deployment

### 1. Server prerequisites

Install these on the target server:

- Docker Engine (with Docker Compose plugin)
- Git
- A Linux user for DockCD runtime (recommended: `dockcd`)

Verify:

```bash
docker --version
docker compose version
git --version
```

### 2. Create runtime user and folders

Use a dedicated user and predictable folder layout.

```bash
sudo useradd -m -s /bin/bash dockcd || true
sudo mkdir -p /opt/dockcd
sudo mkdir -p /srv/dockcd/apps
sudo mkdir -p /srv/dockcd/data/postgres
sudo mkdir -p /srv/dockcd/data/redis
sudo chown -R dockcd:dockcd /opt/dockcd /srv/dockcd
sudo chmod -R 775 /srv/dockcd
```

Why this matters:

- `/opt/dockcd` stores the DockCD platform code and compose files
- `/srv/dockcd/apps` is where DockCD clones managed application repositories
- `/srv/dockcd/data/*` stores persistent data for stateful containers

### 3. Allow DockCD to run Docker commands

DockCD executes `docker compose` commands for managed services. Add the runtime user to the `docker` group:

```bash
sudo usermod -aG docker dockcd
newgrp docker
```

If you skip this step, clone/deploy actions may fail when DockCD tries to start or inspect containers.

### 4. Clone DockCD repository with correct ownership

```bash
sudo -u dockcd -H bash -lc 'cd /opt/dockcd && git clone <your-dockcd-repo-url> .'
```

Keep ownership aligned with the runtime user:

```bash
sudo chown -R dockcd:dockcd /opt/dockcd
```

### 5. Define environment file

Create an environment file at `/opt/dockcd/.env.prod`:

```env
ENVIRONMENT=production
DEBUG=False
ALLOWED_HOSTS=your-server-domain,127.0.0.1,localhost

DB_NAME=dockcd
DB_USER=postgres
DB_PASSWORD=change-me
DB_HOST=postgres
DB_PORT=5432

REDIS_PASSWORD=change-me
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
```

### 6. Required containers (minimum stack)

For production, run DockCD as multiple containers:

- `postgres` (database)
- `redis` (broker, caching, channel layer)
- `dockcd-web` (Django API)
- `dockcd-worker` (Celery worker)
- `dockcd-beat` (Celery beat scheduler)
- optional: `nginx` reverse proxy

### 7. Example production compose with volume mounts

Create `/opt/dockcd/docker-compose.prod.yml`:

```yaml
services:
	postgres:
		image: postgres:16
		restart: always
		environment:
			POSTGRES_DB: ${DB_NAME}
			POSTGRES_USER: ${DB_USER}
			POSTGRES_PASSWORD: ${DB_PASSWORD}
		volumes:
			- /srv/dockcd/data/postgres:/var/lib/postgresql/data

	redis:
		image: redis:7
		command: ["redis-server", "--requirepass", "${REDIS_PASSWORD}"]
		restart: always
		volumes:
			- /srv/dockcd/data/redis:/data

	dockcd-web:
		build:
			context: .
			dockerfile: devops/Dockerfile
		env_file:
			- .env.prod
		command: gunicorn --bind 0.0.0.0:8000 --workers 3 dockcd.wsgi:application
		depends_on:
			- postgres
			- redis
		restart: always
		ports:
			- "8000:8000"
		volumes:
			- /var/run/docker.sock:/var/run/docker.sock
			- /srv/dockcd/apps:/srv/dockcd/apps

	dockcd-worker:
		build:
			context: .
			dockerfile: devops/Dockerfile
		env_file:
			- .env.prod
		command: celery -A dockcd worker -l info
		depends_on:
			- postgres
			- redis
		restart: always
		volumes:
			- /var/run/docker.sock:/var/run/docker.sock
			- /srv/dockcd/apps:/srv/dockcd/apps

	dockcd-beat:
		build:
			context: .
			dockerfile: devops/Dockerfile
		env_file:
			- .env.prod
		command: celery -A dockcd beat -l info
		depends_on:
			- postgres
			- redis
		restart: always
		volumes:
			- /var/run/docker.sock:/var/run/docker.sock
			- /srv/dockcd/apps:/srv/dockcd/apps
```

Important volume notes:

- `/var/run/docker.sock:/var/run/docker.sock` lets DockCD control Docker on the host
- `/srv/dockcd/apps:/srv/dockcd/apps` ensures cloned repositories and compose files are shared and persistent
- `/srv/dockcd/data/postgres:/var/lib/postgresql/data` persists database state

### 8. Bring up the platform

```bash
cd /opt/dockcd
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build
```

Run migrations and create admin user:

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml exec dockcd-web python manage.py migrate
docker compose --env-file .env.prod -f docker-compose.prod.yml exec dockcd-web python manage.py createsuperuser
```

### 9. Folder permissions required for application cloning

DockCD must be able to create and update directories under `/srv/dockcd/apps` while handling webhook/manual deployments.

Recommended permissions:

```bash
sudo chown -R dockcd:docker /srv/dockcd/apps
sudo chmod -R 2775 /srv/dockcd/apps
```

`2775` sets the group sticky bit so newly created directories inherit the same group, reducing permission drift across clone/pull operations.

Quick validation from host:

```bash
sudo -u dockcd -H bash -lc 'mkdir -p /srv/dockcd/apps/permission-test && rm -rf /srv/dockcd/apps/permission-test'
```

### 10. Operational checks

Use these checks after deployment:

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f dockcd-web
docker compose -f docker-compose.prod.yml logs -f dockcd-worker
docker compose -f docker-compose.prod.yml logs -f dockcd-beat
```

If repository cloning fails, check:

- credentials/access to the application repository
- write permission on `/srv/dockcd/apps`
- Docker socket mount and docker group membership
