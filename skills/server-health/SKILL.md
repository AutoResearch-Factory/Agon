---
name: server-health
description: Use when you need project-specific compute/server notes to pick a server or confirm a running task, if the project has filled its server manual or monitoring hooks.
---

# Server health snapshot

Placeholder for project-specific compute availability.

This release intentionally ships no private server names, accounts, paths, queues, credentials, or monitoring scripts. Projects should fill `references/servers_manual.md` or replace this skill with their own health collector.

## Usage Contract

- First read `${CLAUDE_PLUGIN_ROOT}/references/servers_manual.md`.
- Use only project-provided server labels, paths, queues, and monitoring commands.
- If the project has not configured compute resources, report `UNKNOWN` and ask the user for server information.
- Do not guess private hostnames, usernames, storage roots, queues, or GPU availability.

## Expected Project Notes

The server manual should define:

- host labels and access method
- GPU/CPU/RAM inventory
- scheduler or launch rules
- canonical remote project root
- dataset/cache/checkpoint/result locations
- how to check load, jobs, disk, and running experiments
