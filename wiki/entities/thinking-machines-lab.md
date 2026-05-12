---
title: Thinking Machines Lab
type: entity
tags: [AI实验室, AGI, 安全对齐]
source_count: 1
updated: 2026-05-12
---

Thinking Machines Lab 是由前 OpenAI 首席科学家 Ilya Sutskever 于 2024 年创立的研究实验室，总部位于纽约，致力于安全通用人工智能（AGI）的研究。实验室名称向 1980 年代 MIT 的 Thinking Machines Corporation 致敬，但目标从并行计算转向了智能本身的安全扩展。

## 核心定位

实验室将**安全性**与**能力扩展**视为同等重要的研究维度，而非事后补救。Sutskever 在多次公开表达中强调，超级智能的出现是不可避免的，关键问题是如何确保它安全、可控地到来。这种理念直接影响了实验室的研究优先级：不是先造出更强的模型再考虑安全，而是把安全机制内建到能力扩展的过程中。

## 主要研究方向

**Interaction models**
：2026 年 5 月发布的研究预览，提出将实时多模态交互能力原生内建到模型中，而非通过外部 harness 拼接。采用 interaction model + background model 的双模型架构，以 200ms micro-turns 实现真正的双向实时协作。

**Scaling laws 与推理**
：延续 Sutskever 在 OpenAI 期间对 scaling laws 的研究兴趣，探索模型规模扩展与推理能力涌现之间的关系。

**安全对齐**
：研究如何在模型能力增长的同时保持对齐稳定性，包括实时交互场景下的拒绝策略和长程鲁棒性。

## 产品发布节奏

截至 2026 年 5 月，Thinking Machines Lab 尚未发布面向消费者的通用产品，主要通过研究预览和技术博客与外部交流。interaction model 的研究预览计划先开放有限的研究访问，随后在今年晚些时候进行更广泛发布。

相关页面：[[topics/interaction-models]] · [[sources/interaction-models]]
