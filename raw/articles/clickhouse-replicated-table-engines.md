---
title: "Replicated* table engines | ClickHouse Docs"
source: "https://clickhouse.com/docs/engines/table-engines/mergetree-family/replication#converting-from-mergetree-to-replicatedmergetree"
author:
published:
created: 2026-04-16
description: "Replication engine behavior and official conversion paths from MergeTree to ReplicatedMergeTree."
tags:
  - "clippings"
---
This section of the replication documentation describes official ways to convert existing MergeTree-family tables into replicated ones.

## Captured official conversion methods

- Detached tables can be reattached as replicated using `ATTACH TABLE ... AS REPLICATED`.
- A table can also be converted on server restart by creating an empty `convert_to_replicated` file in the table's data path.
- The restart-based conversion relies on `default_replica_path` and `default_replica_name`.
- A manual method exists: rename the old table, create a new replicated table with the original name, move data into `detached`, and attach partitions.

## Captured caveats

- The documentation explicitly warns to synchronize data first if replicas differ, or keep data on only one source replica before conversion.
- For restart-based conversion, operators may need to query `system.tables` for `data_paths` and `system.replicas` for the replicated path.
- The examples frame conversion as a supported migration path, but one that still requires deliberate operational control.
