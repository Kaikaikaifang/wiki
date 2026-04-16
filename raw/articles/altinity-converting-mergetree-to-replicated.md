---
title: "Converting MergeTree to Replicated | Altinity Knowledge Base"
source: "https://kb.altinity.com/altinity-kb-setup-and-maintenance/altinity-kb-converting-mergetree-to-replicated/"
author:
published:
created: 2026-04-16
description: "Altinity KB summary of practical migration paths from MergeTree to ReplicatedMergeTree."
tags:
  - "clippings"
---
This knowledge base article summarizes several practical ways to add replication to an existing MergeTree table.

## Captured migration options

- Create a replicated table and copy data with `INSERT INTO ... SELECT` for small tables.
- Create a replicated table beside the old table and move partitions with `ALTER TABLE ... ATTACH PARTITION ... FROM ...`.
- Convert in place using the official replication documentation and filesystem-level manipulation.
- Use backup and restore tooling to recover the data as `ReplicatedMergeTree`.
- Use the newer embedded `ATTACH TABLE ... AS REPLICATED` command for supported versions.

## Captured operational advice

- The side-by-side `ATTACH PARTITION` method is attractive for large tables because it uses filesystem hard links and does not require extra disk space proportional to the data volume.
- The article's example stops merges, generates partition attach commands from `system.parts`, validates row counts, then renames the original and replicated tables for cutover.
- Keeping the original table after rename is presented as a cheap rollback buffer until new writes accumulate.
