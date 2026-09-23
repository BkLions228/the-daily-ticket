# Daily Ticket 02: Secure a Containerized Health Service

## Objective

Package a Python health-check service into a hardened Docker image and validate
its application health, runtime identity, filesystem restrictions, temporary
storage, and logging behavior.

## Workplace Scenario

A development team needs to deploy a lightweight health service to a managed
container platform such as AWS ECS or Azure Container Apps.

Before approving the image, the platform team requires evidence that the
container runs without root privileges, provides an application-level health
check, supports a read-only root filesystem, and sends logs to standard output.

## Acceptance Criteria

- Build the image from `python:3.12-slim`.
- Run the application as a non-root user.
- Use UID and GID `10001`.
- Return HTTP `200` from `/health`.
- Report `healthy` through Docker.
- Run with a read-only root filesystem.
- Mount temporary memory-backed storage at `/tmp`.
- Avoid installing `curl`, `wget`, or an application framework.
- Write logs to standard output.
- Capture repeatable validation evidence.
- Create no cloud resources.

## Architecture and Approach

The solution contains a Python service packaged into a Docker image. The service
listens on port `8080` and exposes `/health`.

The image uses these security controls:

- A dedicated `appuser` account
- UID and GID `10001`
- No home directory
- A noninteractive login shell
- Application files owned by `appuser`
- A Python-based Docker health check
- No unnecessary health-check package

Runtime controls add:

- A read-only root filesystem
- A memory-backed `/tmp` filesystem
- `noexec` and `nosuid` restrictions on `/tmp`
- Explicit host-to-container port mapping

## Repository Structure

```text
ticket-02-secure-container/
├── .dockerignore
├── app.py
├── Dockerfile
├── README.md
└── evidence/
    ├── container-inspect.txt
    ├── container-logs.txt
    ├── docker-build.txt
    ├── health-response.json
    ├── readonly-test.txt
    └── runtime-identity.txt
```

## Prerequisites

- Windows with WSL 2
- Docker Desktop using the Linux-container engine
- Git Bash
- Python 3
- Git
- Visual Studio Code or another editor

Verify Docker:

```bash
docker version
docker run --rm hello-world
wsl.exe --list --verbose
```

## Implementation

### Application

[`app.py`](app.py) uses Python's standard-library HTTP server. It returns a JSON
response from `/health` and returns `404` for other paths.

The application writes startup and request messages to standard output so a
container platform can collect them without accessing files inside the
container.

### Container image

[`Dockerfile`](Dockerfile) performs the following operations:

1. Uses the `python:3.12-slim` base image.
2. Creates `appuser` with UID and GID `10001`.
3. Copies the application with the correct ownership.
4. Changes the runtime identity to `appuser`.
5. exposes port `8080`.
6. Configures an application-level health check.
7. Starts the service with an exec-form command.

### Build context

[`.dockerignore`](.dockerignore) excludes Git metadata, evidence, documentation,
logs, and Python cache files from the image build context.

## Build Procedure

From the repository root:

```bash
TICKET_DIR="tickets/containers/ticket-02-secure-container"

docker build \
  --tag daily-ticket-health:1.0 \
  "$TICKET_DIR"
```

## Runtime Procedure

Git Bash can translate Linux-style paths into Windows paths. Setting
`MSYS_NO_PATHCONV=1` preserves the `/tmp` mount destination.

```bash
MSYS_NO_PATHCONV=1 docker run \
  --detach \
  --rm \
  --name daily-ticket-health \
  --publish 8080:8080 \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=16m \
  daily-ticket-health:1.0
```

## Validation

### Application response

```bash
curl --fail --silent --show-error \
  http://localhost:8080/health
```

Expected response:

```json
{"status": "healthy", "service": "daily-ticket-health"}
```

### Runtime identity

```bash
docker exec daily-ticket-health id
```

Validated result:

```text
uid=10001(appuser) gid=10001(appuser) groups=10001(appuser)
```

### Runtime controls

```bash
docker inspect \
  --format='User={{.Config.User}} ReadOnly={{.HostConfig.ReadonlyRootfs}} Health={{.State.Health.Status}}' \
  daily-ticket-health
```

Validated result:

```text
User=appuser ReadOnly=true Health=healthy
```

### Read-only filesystem

```bash
docker exec daily-ticket-health \
  sh -c 'touch /app/should-fail'
```

The write operation failed with exit code `1` because `/app` was read-only.

## Validation Evidence

- [`docker-build.txt`](evidence/docker-build.txt)
- [`health-response.json`](evidence/health-response.json)
- [`runtime-identity.txt`](evidence/runtime-identity.txt)
- [`container-inspect.txt`](evidence/container-inspect.txt)
- [`readonly-test.txt`](evidence/readonly-test.txt)
- [`container-logs.txt`](evidence/container-logs.txt)

## Security and Governance Considerations

Running as a high-numbered non-root UID reduces the impact of a container
compromise and avoids depending on a privileged account.

The read-only root filesystem prevents the application from modifying its image
at runtime. The explicitly mounted `/tmp` filesystem provides controlled
temporary storage without creating persistent application state.

The health check uses Python's existing standard library, which avoids adding
another package and its associated vulnerabilities.

Build files, validation evidence, and security decisions are version controlled
and reviewed through a pull request.

## Troubleshooting

### Git Bash cannot find Docker

Add Docker's CLI directory to the Git Bash profile:

```bash
export PATH="$PATH:/c/Program Files/Docker/Docker/resources/bin"
```

### Docker cannot connect to the engine

Start Docker Desktop and wait until it reports that the engine is running.

### The container remains in `starting` status

Wait at least 10 seconds and inspect the health-check output:

```bash
docker inspect \
  --format='{{json .State.Health}}' \
  daily-ticket-health
```

### Port 8080 is already in use

Find and stop the conflicting container:

```bash
docker ps
docker stop CONTAINER_NAME
```

Alternatively, publish a different host port, such as `8081:8080`.

### The group receives an unexpected GID

Create the group explicitly with GID `10001` before creating the user. Relying
on an automatically assigned system group can produce a different numeric GID.

### Git Bash changes the `/tmp` path

Prefix the `docker run` command with:

```bash
MSYS_NO_PATHCONV=1
```

## Architecture Tradeoffs

A read-only, non-root container has a smaller attack surface and is easier to
replace safely. Applications that depend on writing to their installation
directory must be redesigned to use temporary mounts or external storage.

The health check runs every five seconds, which provides fast failure detection
but creates additional requests and log entries. Production intervals should
balance detection speed with resource consumption.

The Dockerfile uses a readable base-image tag. Production delivery should pin a
reviewed image digest and use automated vulnerability scanning.

## Business Value

This implementation provides a repeatable container baseline that can be tested
locally and adapted for AWS ECS, Azure Container Apps, or Kubernetes. It reduces
runtime privilege, improves failure detection, and produces evidence that
reviewers can verify before deployment.

## Career Connection

This ticket demonstrates the container packaging, runtime hardening,
observability, and stateless-design skills expected from Cloud Engineers and
evaluated by Cloud Architects.