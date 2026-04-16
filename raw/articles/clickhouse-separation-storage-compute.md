---
title: "Separation of storage and compute | ClickHouse Docs"
source: "https://clickhouse.com/docs/guides/separation-storage-compute"
author:
published:
created: 2026-04-16
description: "Guide to using ClickHouse with S3 for separated storage and compute."
tags:
  - "clippings"
---
This guide explains how to use ClickHouse with S3 so compute resources and storage resources can be managed independently.

## Captured points

- The architecture improves scalability, cost efficiency, and flexibility because compute and storage can scale separately.
- It is especially useful when performance on colder data is less critical.
- Self-managed separation of storage and compute is more complicated than standard deployments.
- ClickHouse Cloud is recommended if you want this architecture without manual configuration, using `SharedMergeTree`.
- The guide shows `storage_configuration` with an `s3_disk`, an `s3_cache`, and a `storage_policy` named `s3_main`.
- Tables can be created with `MergeTree` plus `SETTINGS storage_policy = 's3_main'`; ClickHouse handles the S3-backed storage underneath.
- Replication for fault tolerance can be layered on top with `ReplicatedMergeTree`.

## Warnings

- Do not configure AWS or GCS life cycle policies for these buckets; the guide says this can break tables.
- Multi-region replication is possible, but fault tolerance introduces another layer of design and coordination.
