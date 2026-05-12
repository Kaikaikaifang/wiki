---
title: 交互模型
type: topic
tags: [Agent, 多模态, 实时交互, 人机协作]
source_count: 1
updated: 2026-05-12
---

> 这篇文章让我重新理解了一个问题：我们之前说的 "ACI" 其实还停留在一个很浅的层面——它讨论的是 agent 怎么调用工具，但完全没有触及 agent 怎么和人类共处同一个时间流。

## 为什么 turn-based 是瓶颈

现有 AI 系统的人类被排除在循环之外，不是因为工作不需要他们，而是因为**接口没有为人类留出空间**。模型在用户完成输入前完全等待，生成过程中又冻结感知。这就像试图通过电子邮件解决一场关键分歧——信息可以传递，但协作带宽被严重压缩。

更深层的问题在于，现有的 "实时" 系统本质上是在 turn-based 模型外面套一层 harness：VAD 检测语音边界、对话管理组件预测 turn 切换、独立编码器处理音频视频。这些组件的智能水平显著低于模型本身，因此无法支持真正的主动性交互——比如 "在我犯错时打断我" 或 "在我写出 bug 时告诉我"。

## Interaction model 的核心范式

Thinking Machines Lab 提出的 interaction model 把交互能力从外部 harness **下沉到模型的一级能力**。关键不是让模型 "更快地完成 turn"，而是**彻底取消 turn 的概念**。

模型以 200ms 的 micro-turns 持续运行：每 200ms 接收一批多模态输入，同时生成一批输出。输入和输出流被交错成单一 token 序列，人类感知中的并发音频、视频流在模型内部被统一处理。这带来几个本质变化：

- **打断和重叠成为原生行为**，而非需要特殊 harness 支持的异常模式
- **时间感知内建到模型**，可以回答 "我跑一英里用了多久" 这类需要主动计时的问题
- **视觉主动性**：模型可以根据视觉变化主动选择说话，而非等待音频 trigger
- **并发能力**：在说话的同时搜索、调用工具或生成 UI

## 双模型架构

Interaction model 不是孤军奋战。当任务需要超出瞬时响应的深度推理时，它会将**完整对话上下文**（而非独立查询）委托给一个 background model。这个模型异步运行，结果流式返回，由 interaction model 在合适的时刻自然融入对话。

这个分工非常精确：interaction model 负责**presence**——让用户感觉到一个持续在场的协作者；background model 负责**depth**——处理需要规划的复杂任务。两者都是智能的，但各自优化了不同的延迟-智能权衡。

我觉得这个架构对 agentic systems 的启示在于：它把 "实时交互" 和 "深度推理" 从同一个模型的矛盾需求中解放出来，变成了两个可以独立优化、再协同工作的组件。这与 [[topics/multi-agent-systems]] 中的 orchestrator-worker 模式有相似之处，但分工维度不同——不是按任务并行度拆分，而是按**时间尺度**拆分。

## 对 ACI 的重新定义

[[topics/agent-computer-interface]] 之前讨论的是 agent 如何调用工具，而 interaction model 把这个概念推进了一层：**ACI 也应该包括 agent 如何与人类在同一个时间流中协作**。

当模型可以在你听它说话时同时浏览网页、生成代码界面、观察你的屏幕并适时插话，"接口"就不再是一套函数签名，而是一种**共在状态**。这对未来 agent 系统的设计提出了全新的问题：如何管理并发注意力？如何在多模态流中保持一致的个性与边界？如何在实时交互中保持安全对齐？

## 技术实现的取舍

**Encoder-free early fusion**
：放弃独立的 Whisper 式音频编码器和 TTS 式解码器，改用 dMel 直接输入、flow head 直接输出。这个选择的代价是失去现成编码器的成熟度，但收益是整个系统可以端到端训练，交互行为随模型规模同步提升——符合 "the bitter lesson" 的精神。

**Streaming sessions**
：200ms chunks 的频繁小 prefill 对现有推理系统是巨大的挑战。通过在 GPU 内存中持久化拼接序列，他们把 per-turn 开销降到可接受范围。这个优化已经 upstream 到 SGLang，说明它不只是某个实验室的内部 trick。

**Trainer-sampler alignment**
：在多并行策略训练中保持比特级一致，这对调试和稳定性很重要，但对于大多数工程团队来说，这属于 "如果不到那个规模就不需要担心" 的范畴。

## 评估的挑战

现有的交互基准（如 FD-bench）只能测量 turn-taking latency 和基本响应质量，无法捕捉 interaction model 带来的定性跃迁。Thinking Machines 为此开发了内部基准：

- TimeSpeak：测量时间感知和主动发起语音的能力
- CueSpeak：测量在正确时刻给出正确语义回应的能力
- RepCount-A / ProactiveVideoQA / Charades：测量视觉主动性

这些基准的共同点是：**它们惩罚 "说得对但时机错" 和 "时机对但说得错" 同样严厉**。这反映出交互质量不是单一维度的得分，而是语义正确性与时间正确性的联合优化。

## 一个判断句

如果一个 AI 系统需要人类去适应它的 turn 节奏、等待它完成生成才能提供新信息、或者通过特殊的打断按钮来 "申请发言"，那么它还没有真正进入实时协作的范式——它只是在模拟协作。

---

来源：[[sources/interaction-models]]

相关页面：[[topics/agent-computer-interface]] · [[topics/agentic-systems]] · [[topics/multi-agent-systems]] · [[entities/thinking-machines-lab]] · [[topics/ai-agent-harness]] · [[topics/long-horizon-agents]]
