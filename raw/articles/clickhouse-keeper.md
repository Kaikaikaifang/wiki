---
title: "ClickHouse Keeper | ClickHouse Docs"
source: "https://clickhouse.com/docs/guides/sre/keeper/clickhouse-keeper"
author:
published:
created: 2026-04-16
description: "ClickHouse Keeper positioning, configuration patterns, ZooKeeper compatibility boundaries, and migration notes."
tags:
  - "clippings"
---
This guide explains ClickHouse Keeper as the coordination service for ClickHouse clusters.

## Captured positioning

- ClickHouse Keeper is protocol-compatible with ZooKeeper clients used by ClickHouse.
- It is implemented with Raft and is meant to handle replication metadata, distributed DDL coordination, and related cluster state.
- Production deployments typically run Keeper as a separate odd-numbered cluster such as three or five nodes.
- The guide documents standalone, mixed, and migration-related configuration patterns, but mixed ZooKeeper and Keeper usage inside one ClickHouse cluster is not supported.

## Captured compatibility boundaries

- Keeper is not a universal replacement for every ZooKeeper use case.
- External integrations are not supported in the same way as a general-purpose ZooKeeper ensemble.
- Dynamic reconfiguration behavior is not fully identical to ZooKeeper, and `enable_reconfiguration` is disabled by default.
- Migration requires explicit snapshot conversion or controlled cutover steps rather than an in-place mixed cluster.

## Captured operational notes

- The guide documents four-letter commands, feature flags, and recovery procedures, which shows Keeper is expected to be operated directly in production.
- `async_replication` can improve performance, but it changes the write acknowledgment path and needs an explicit durability tradeoff decision.
- Operators are expected to understand quorum sizing, server IDs, network ports, and recovery modes instead of treating Keeper as a hidden internal detail.
