---
title: "Does ClickHouse support multi-region replication? | ClickHouse Docs"
source: "https://clickhouse.com/docs/knowledgebase/multi-region-replication"
author:
published:
created: 2026-04-16
description: "FAQ for multi-region replication in ClickHouse."
tags:
  - "clippings"
---
This knowledge base entry gives a short answer to the question of whether ClickHouse supports multi-region replication.

## Captured points

- The short answer is yes.
- ClickHouse recommends keeping latency between all regions or datacenters in the two-digit millisecond range.
- If latency is higher, write performance suffers because replication goes through a distributed consensus protocol.
- Replication between US coasts is given as likely fine; replication between the US and Europe is given as an example that likely will not work well.
- Configuration is otherwise the same as single-region replication: replicas just live in different locations.
