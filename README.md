# Log Alert 

A self-healing log monitoring system that emails alerts on application errors.

## Architecture
App container writes structured JSON logs to a shared volume.
A log-watcher container tails the log, detects ERROR entries,
and sends an email alert (with cooldown + retry logic).

## Run it
docker compose up --build

## Trigger a test alert
curl http://localhost:8080/crash

## Production considerations
- Restart policies for self-healing
- Health checks before dependent services start
- Resource limits to prevent noisy-neighbor issues
- Alert cooldown to prevent spam (60s window)
- Retry logic for transient email failures (3 attempts, exponential backoff)
- Unbuffered Python output for real-time log visibility
- Secrets via .env, excluded from version control

## Next steps for Prodcution setup
Replace custom watcher with Filebeat -> Elasticsearch -> Kibana alerting
for centralized logging across many services.
# log-alert-demo
