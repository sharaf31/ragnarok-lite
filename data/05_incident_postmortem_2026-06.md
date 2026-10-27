# Postmortem: Skylark Cloud data ingestion outage

- Incident ID: INC-2026-0117
- Date: 18 June 2026
- Severity: SEV-2
- Author: Agnieszka Wilk (Head of Platform Engineering)
- Status: Closed

## Summary
Between **06:12 and 09:47 CEST** on 18 June 2026, Skylark Cloud stopped ingesting readings from about 41% of connected hubs. No data was permanently lost, because hubs buffer readings locally and re-uploaded them once ingestion recovered. Alerts (rain, wind, frost) were delayed for the affected users during the outage window.

## Impact
- Duration: 3 hours 35 minutes
- Affected hubs: about 26,400 of 64,300 online
- Delayed alerts: 3,912
- Support tickets opened: 287
- Customers compensated with one free month of Skylark Cloud: all affected subscribers

## Root cause
A scheduled TLS certificate rotation on the regional ingestion load balancer (eu-central) deployed a certificate chain missing an intermediate certificate. Hubs running firmware 2.2.x and older validate the full chain strictly and rejected the connection. Hubs on 2.3.x tolerated the missing intermediate because of a newer TLS library, which is why only part of the fleet was affected.

## Timeline (CEST)
- 06:00 — Automated certificate rotation runs.
- 06:12 — Ingestion rate drops by 40%. The alert fires, but it is routed to a deprecated on-call channel.
- 07:58 — A support agent in Porto escalates after a spike in "no outdoor data" tickets.
- 08:20 — On-call engineer identifies TLS handshake failures from older firmware.
- 09:31 — Corrected certificate chain deployed.
- 09:47 — Ingestion back to normal. Buffered data backfilled by 11:30.

## What went well
- Hub-side buffering prevented data loss.
- Porto support spotted the pattern quickly from ticket volume.

## What went wrong
- Ingestion alerts were routed to a channel no one monitored after the May on-call tool migration.
- The certificate rotation pipeline had no pre-flight chain validation.
- 18% of the fleet was still on firmware older than 2.3.

## Action items
| # | Action | Owner | Due | Status |
|---|---|---|---|---|
| 1 | Add full-chain validation step to certificate pipeline | Platform team | 30 Jun 2026 | Done |
| 2 | Audit all alert routing after on-call migration | SRE | 15 Jul 2026 | Done |
| 3 | Push auto-update to fleet on firmware < 2.3 | Firmware team | 31 Aug 2026 | Done |
| 4 | Canary certificate rotations on 5% of load balancer nodes first | Platform team | 30 Sep 2026 | In progress |
