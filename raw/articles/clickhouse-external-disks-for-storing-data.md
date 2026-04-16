---
title: "External disks for storing data | ClickHouse Docs"
source: "https://clickhouse.com/docs/operations/storing-data"
author:
published:
created: 2026-04-16
description: "Configuration guide for external storage and cache disks in ClickHouse."
tags:
  - "clippings"
---
This page describes how `MergeTree` and `Log` family tables can store data on external storage such as S3 and Azure Blob Storage, and how local cache can sit in front of remote disks.

## Captured storage primitives

- Tables can use `storage_policy` or `disk` settings to decide where data is stored.
- Remote object storage is available through disk types such as `s3`, `azure_blob_storage`, and newer `object_storage` configuration.
- Metadata can remain local even when data files live in object storage.
- Local cache can be configured over remote disks with disk type `cache`.
- Cache size, path, write-through behavior, hit thresholds, bypass thresholds, and per-query limits are configurable.
- Cache state is observable through `system.filesystem_cache`, `system.filesystem_cache_log`, and cache-related commands.

## Deployment implication

These storage primitives are the basis for tiered storage:

- cold or capacity-heavy data can live on object storage,
- hot working sets can be served through local filesystem cache,
- table-level `storage_policy` decides which layout a table uses.

The page itself is mostly a configuration reference, but it exposes the building blocks needed for hot/cold data layering.
