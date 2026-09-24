Log Alert Demo

A log monitoring system that watches an app's logs in real time and emails me the moment something breaks.

What this is

Two containers talking through a shared log volume —

app — a small Flask service with two endpoints. /health is a plain readiness check. /crash intentionaly throws an error so I can trigger the alert flow on demand instead of waiting around for a random failure. Logs are written as structured JSON, not plain text.
log-watcher — sits there tailing that log file (like tail -f), watching for ERROR entries, and fires off an email the moment it sees one.

The two never talk to each other directly. The log file, sitting in a shared Docker volume, is the only thing connecting them — write on one side, read on the other.

Why this method?

what makes it a production level ?

Cooldown (60s) — if the app throws 50 errors in a row, I get one email, not 50. This is basically alert-fatigue prevention.
Retry with exponential backoff — if sending the email fails (SMTP hiccup, brief network issue), it retries 3 times with increasing delay rather than just giving up silently.
Self-healing — both containers run with restart: unless-stopped, so a crash fixes itself.
Health-checked startup — the watcher won't even start until Docker confirms the app is actually healthy, which avoids a race condition where it goes looking for a log file that isn't there yet.
Resource limits — capped CPU/memory per container so one misbehaving service can't take down the whole box.
Secrets stay out of the code — SMTP credentials live in .env, loaded as environment variables, and .gitignore makes sure .env never gets committed.
Run it
docker compose up --build
Trigger a test alert
curl http://localhost:8080/crash

Check your inbox — the email should land within a few seconds.

Production considerations I kept in mind
Restart policies for self-healing
Health checks before dependent services start
Resource limits to avoid the noisy-neighbor problem
Alert cooldown to prevent spam (60s window)
Retry logic for transient email failures (3 attempts, exponential backoff)
Unbuffered Python output so logs show up in real time, not batched
Secrets via .env, excluded from version control
What I'd change if this were actually going to production

This works well as a single-host demo, but I'd be the first to point out its limits:

Not distributed — it watches one log file on one host. Real systems have logs scattered across many services and machines.
No alert history — nothing gets persisted. If I miss the email, there's no record it ever happened.

what will i add on - in future to make it production grade ?-
Given more time, the natural next step is swapping this custom watcher for Filebeat → Elasticsearch → Kibana. Filebeat does the same tailing job as watch.py, Elasticsearch replaces the shared volume as a searchable central store, and Kibana takes over alerting, throttling, and email delivery — through configuration instead of code I have to maintain myself. I scoped this project the way I did so I could build and control the full pipeline end-to-end in the time I had — the production version is the same ideas, just running at scale.
