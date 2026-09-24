---
name: server-health
description: Check server load and resource availability to choose a server or verify a running experiment.
---

# Server health

Read `${CLAUDE_PLUGIN_ROOT}/references/servers_manual.md` for server labels,
access methods, and monitoring commands.

## Choose a server

Use the access and monitoring commands in the server manual to check:

- CPU load and available system memory
- GPU utilization, free GPU memory, and running processes
- Free space on the project's data and output filesystems
- Scheduler allocation and queue status, when applicable
- Existing project jobs and the location of required data or checkpoints

If load history is available, compare recent averages with the current sample.
Recommend a server based on the run's requirements and data location.

## Verify a running experiment

Use the run's recorded host, remote directory, and job/session ID to check:

- Job or process status and owner
- Resource utilization
- Latest log entries and output timestamps
- Completion status, exit code, or error messages

Distinguish running, queued, completed, failed, and unverified tasks. A session
existing by itself does not establish that the experiment is progressing.

## Report

For server selection, summarize each candidate's available resources, current
jobs, and observation time. For task checks, report the task status and the
log, process, or scheduler evidence supporting it.

If a check fails or monitoring is unavailable, report `UNKNOWN` with the
specific missing information or failed command. Do not interpret missing data
as an idle server or a completed task.
