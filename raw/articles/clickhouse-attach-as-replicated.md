---
title: "ATTACH Statement | ClickHouse Docs"
source: "https://clickhouse.com/docs/sql-reference/statements/attach#attach-mergetree-table-as-replicatedmergetree"
author:
published:
created: 2026-04-16
description: "ATTACH syntax for converting MergeTree tables to ReplicatedMergeTree and the required replica metadata steps."
tags:
  - "clippings"
---
This page documents the dedicated `ATTACH` syntax for switching a detached MergeTree-family table into replicated mode.

## Captured syntax

- `ATTACH TABLE [db.]name AS REPLICATED`
- Typical flow: `DETACH TABLE`, `ATTACH TABLE ... AS REPLICATED`, then `SYSTEM RESTORE REPLICA`.

## Captured caveats

- The statement does not modify ZooKeeper or Keeper metadata by itself.
- After attach, operators must either create metadata with `SYSTEM RESTORE REPLICA` or remove stale metadata with `SYSTEM DROP REPLICA ... FROM ZKPATH ...`.
- When trying to add a replica to an existing replicated table, local data in the converted MergeTree table will be detached.

## Why this matters

- This command reduces the amount of manual file movement needed for in-place conversion.
- But it does not remove the need to understand the replication metadata path and restore semantics.
