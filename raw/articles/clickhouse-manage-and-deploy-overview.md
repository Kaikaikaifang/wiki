---
title: "Manage and deploy overview | ClickHouse Docs"
source: "https://clickhouse.com/docs/guides/manage-and-deploy-index"
author:
published:
created: 2026-04-16
description: "Overview of ClickHouse manage and deploy documentation topics."
tags:
  - "clippings"
---
This page is the entry point for ClickHouse operational documentation around deployment and management.

## Captured topics

- Deployment and Scaling: working deployment examples produced from ClickHouse support and services experience.
- Separation of Storage and Compute: guide for using ClickHouse with S3 so compute and storage can be managed independently.
- Configuring ClickHouse Keeper: configuration patterns for the coordination layer.
- Re-balancing Shards: guidance for moving data when shard distribution becomes uneven.
- Does ClickHouse support multi-region replication?: FAQ for latency and topology boundaries.
- External Disks for Storing Data: storage configuration with S3, Azure, HDFS (unsupported), cache disks, and storage policies.
- Monitoring, quotas, distributed DDL, upgrades, backups, troubleshooting, workload scheduling.

## Why this matters

The page shows that ClickHouse treats deployment as a combination of several concerns rather than one cluster recipe:

- topology and scaling,
- coordination with Keeper,
- storage and object storage integration,
- network and security,
- background operations and observability.
