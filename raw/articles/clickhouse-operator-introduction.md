---
title: "Introduction to the ClickHouse Operator | ClickHouse Docs"
source: "https://clickhouse.com/docs/clickhouse-operator/guides/introduction"
author:
published:
created: 2026-04-16
description: "Operator concepts, Keeper requirements, schema replication behavior, and production recommendation to use Replicated databases."
tags:
  - "clippings"
---
This page introduces the ClickHouse Operator for Kubernetes and clarifies what it automates versus what ClickHouse itself still handles.

## Captured operator responsibilities

- The operator manages ClickHouse cluster lifecycle, Keeper integration, config generation, storage provisioning, and rolling updates.
- Every ClickHouseCluster requires a dedicated KeeperCluster referenced through `keeperClusterRef`.
- One KeeperCluster cannot be shared across multiple ClickHouseClusters in this operator model.

## Captured replication behavior

- The operator automatically synchronizes `Replicated` database definitions across replicas.
- It also synchronizes integration database engines such as PostgreSQL and MySQL.
- It does not synchronize non-replicated databases like `Atomic`, and it does not replicate table data.
- Table data replication is still handled by ClickHouse table engines and replication mechanisms.

## Captured production recommendation

- The page explicitly recommends always using the `Replicated` database engine for production deployments.
- The stated benefits are automatic schema replication, simpler table management, sync support for new replicas, and more consistent schema across the cluster.
- The page therefore separates schema-level replication from data-level replication: the operator helps with the former, but table engines still decide the latter.
