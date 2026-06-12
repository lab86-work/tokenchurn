# tokenchurn

**Multi-model, multi-provider coding harness — optimized for token economics.**

Routing prompts across frontier models to maximize output quality per dollar spent.

---

## Why Token Economics?

Every LLM call costs something. Frontier models (Claude 4 Sonnet, GPT-4.5, Gemini 2.5 Pro) deliver high quality but at high cost. Small, local models (Llama 3, Qwen, DeepSeek) are cheap but lack reasoning depth. No single model is optimal for every task.

Tokenchurn treats model selection as an optimization problem: **assign each subtask to the cheapest model capable of solving it correctly.** The result is dramatically lower cost without sacrificing output quality.

```
Cost Efficiency (tasks/dollar)
─────────────────────────────────────────
Always-cheap     ████████████████  2.4x  (fast, but quality loss)
Always-expensive ████████████████  1.0x  (reference baseline)
Tokenchurn       ████████████████  3.8x  (same quality, lower cost)
```

*Projected figures. Real benchmarks to follow.*

---

## Core Concepts

### 1. Task Decomposition
A coding task is broken into granular subtasks (spec writing, implementation, review, linting, testing). Each subtask has a measured complexity score.

### 2. Model Tiering
Models are assigned to tiers based on benchmarked capability and cost-per-token. Tier 1 is cheap & fast, Tier 3 is expensive & deep.

### 3. Intelligent Routing
A lightweight router examines each subtask's complexity and routes it to the cheapest tier with a high probability of success. Failed tasks escalate to the next tier (circuit-breaker pattern).

### 4. Cost Attribution
Every token spent is tracked and attributed to a subtask, model, and outcome. This generates a cost-quality ledger that feeds back into the router.

---

## Architecture (Planned)

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   User CLI   │────▶│  Dispatcher  │────▶│   Router     │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                    ┌─────────────────────────────┼──────────────┐
                    │                             │              │
               ┌────▼────┐                 ┌─────▼─────┐  ┌────▼────┐
               │ Tier 1  │   ...   ...     │  Tier 2   │  │ Tier 3  │
               │ (Cheap) │                 │ (Balanced)│  │(Premium)│
               └────┬────┘                 └─────┬─────┘  └────┬────┘
                    │                             │              │
                    └─────────────────────────────┼──────────────┘
                                                  │
                                             ┌────▼────┐
                                             │ Results │
                                             │ & Costs │
                                             └─────────┘
```

**Components:**
- **Dispatcher** — Accepts tasks, manages workspace context, returns results.
- **Router** — Scores subtask complexity, selects model tier, handles fallbacks.
- **Providers** — Pluggable backends (OpenAI, Anthropic, OpenRouter, Ollama, etc.) abstracted behind a unified interface.
- **Ledger** — Records every token spent, model used, and outcome for cost analysis.
- **Verifier** — Validates outputs (syntax checks, test runs, lint) before merging.

---

## Provider Support (Planned)

| Provider    | Models                                  | Tier    |
|-------------|-----------------------------------------|---------|
| Anthropic   | Claude 4 Sonnet, Claude 3.5 Haiku       | T3 / T2 |
| OpenAI      | GPT-4.5, GPT-4o mini                    | T3 / T2 |
| OpenRouter  | 200+ models via unified API             | All     |
| Ollama      | Local models (Llama 3, Qwen, DeepSeek)   | T1      |
| Gemini      | Gemini 2.5 Pro, Flash                    | T3 / T2 |

---

## Roadmap

- [x] Project scaffolding & documentation
- [ ] Core task decomposition engine
- [ ] Model tier definitions & cost tables
- [ ] Router with complexity scoring
- [ ] Provider adapters (Anthropic, OpenAI, OpenRouter, Ollama)
- [ ] Cost ledger & reporting
- [ ] Workspace context management (git-aware)
- [ ] Verifier (lint + test + syntax validation)
- [ ] Benchmark suite (quality vs. cost)
- [ ] Multi-agent debate/review mode
- [ ] Plugin system for custom routers & providers

---

## Getting Started

*Coming soon. No code has been written yet — this is the design phase.*

```bash
# Future state:
pip install tokenchurn
tokenchurn run "Implement a rate limiter in Rust"
```

---

## Related Projects

- **[llm-council](https://github.com/karpathy/llm-council)** — Multi-model debate via OpenRouter. The inspiration for multi-model orchestration.
- **[Aider](https://github.com/paul-gauthier/aider)** — Git-first coding agent with repository maps.
- **[LiteLLM](https://github.com/BerriAI/litellm)** — Standardized API for 100+ LLM providers.
- **[Promptfoo](https://github.com/promptfoo/promptfoo)** — LLM evaluation and red-teaming.

---

## License

MIT
