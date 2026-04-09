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
