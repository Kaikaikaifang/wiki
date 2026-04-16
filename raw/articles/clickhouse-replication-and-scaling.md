---
title: "Replication + scaling | ClickHouse Docs"
source: "https://clickhouse.com/docs/architecture/cluster-deployment"
author:
published:
created: 2026-04-16
description: "Example ClickHouse cluster with replication and scaling."
tags:
  - "clippings"
---
This guide walks through a ClickHouse cluster with two shards, two replicas, and a three-node ClickHouse Keeper cluster.

## Captured structure

- Dedicated Keeper hosts are recommended in production, even though Keeper can run on the same hosts as ClickHouse Server.
- Keeper nodes can be smaller than database nodes; the guide notes that 4 GB RAM is often enough until the ClickHouse servers become large.
- `remote_servers` defines shards and replicas.
- `internal_replication = true` means writes go to one replica per shard instead of all replicas.
- `ON CLUSTER` is for distributed DDL, not DML.
- `Distributed` tables are used as the write and query interface across shards.
- `ReplicatedMergeTree` provides replica-level data redundancy.

## Captured operational tradeoffs

- Two shards reduce per-node storage and I/O pressure and allow parallel query execution.
- Two replicas improve fault tolerance because each shard has a backup copy.
- Storage overhead roughly doubles compared with a non-replicated layout.
- Single-node failure can be tolerated, but some two-node failure combinations can still break the cluster.
