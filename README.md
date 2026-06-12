# tokenchurn

**Multi-model, multi-provider coding harness — budget-first token economics.**

Set a dollar budget. Tokenchurn selects the optimal mix of models to maximize solution quality within that budget.

---

## The Problem

Frontier models (Claude 4 Sonnet, GPT-4.5) are expensive. Small models (Llama 3, DeepSeek V4 Flash) are cheap. The same model served by different providers costs different amounts at different quantization levels. There is no single "best model" — only the best model *for your budget*.

Tokenchurn moves the reasoning work from expensive token generation into the harness itself. Cheap models explore, generate, narrow down. The frontier model does minimal validation — not full thinking.

## The Approach

### Budget, Not Tiers

No hard tier system. Every model lives in a single flat registry annotated with:
- **Price** per input/output token (including reasoning tokens, with ballpark estimates)
- **Quality rank** (benchmark-based capability score)
- **Context window size**
- **Quantization** (FP16, INT8, INT4, etc.)
- **Free vs paid**
- **Reasoning token support** (paid reasoning like o1/o3 vs free chain-of-thought)

You set a target spend — `$0.10`, `$1`, `$5`, `$10`, `$20` — and the system builds a model selection plan to stay within that range.

### Council Strategy

1. **Scout** — Fan out to all free + local models to understand the task and generate multiple candidate approaches. Cost: near zero.
2. **Narrow** — Use cheap paid models to critique, combine, and refine candidates. Compress the context aggressively.
3. **Validate** — Present the shortlist to a frontier model. Ask for a minimal answer (select best option, one-line justification). Control reasoning token spend by keeping the prompt tight.

The harness does the heavy orchestration — decomposition, comparison, compression — so the frontier model only does what only it can do.

### Cost Control

- **Reasoning token budgets** — Set a max reasoning spend per model. Frontier models estimate their reasoning cost upfront (ballpark), and the router enforces caps.
- **Output compression** — Prefer multiple-choice (A/B/C/D) validation over open-ended generation for expensive models.
- **Fail-fast** — If a cheap model fails, escalate to the next cheapest — not the most expensive.
- **Full attribution** — Every token is logged against a subtask, provider, model, and outcome. The ledger feeds back into future routing decisions.

---

## Example Flow

```
User: "Implement a rate limiter in Rust. Budget: $2.00"

Step 1 ─ Scout (free + local, ~$0.00)
         ├── llama3.1:70b (Ollama) → spec outline
         ├── deepseek-v4:latest (Ollama) → implementation draft A
         ├── mistral-small (OpenRouter free) → implementation draft B
         └── qwen2.5:32b (Ollama) → test suite

Step 2 ─ Narrow (cheap paid, ~$0.30)
         ├── gpt-4o-mini → critique drafts, merge into 2 candidates
         └── claude-3-haiku → reduce to 1 candidate, compress context

Step 3 ─ Validate (premium, ~$1.50)
         └── claude-4-sonnet → "Which of these implementations is correct?
                                Answer A, B, or C. One sentence why."

Total: ~$1.80  (under budget)
```

---

## Architecture (Planned)

```
┌──────────────┐
│   User CLI   │  "Budget: $5. implement X in Python"
└──────┬───────┘
       │
┌──────▼──────────────────────────────────────┐
│              Budget Planner                   │
│  "Model A ($0.001/tok) + Model B ($0.01/tok)"│
│  = estimated $4.80 — 6 candidates → validate │
└──────┬──────────────────────────────────────┘
       │
┌──────▼──────────────────────────────────────┐
│           Model Registry (flat)              │
│  ┌────────┬──────────┬──────┬────┬────────┐ │
│  │ Model  │ Provider │$/1Ktok│Rank│Quant   │ │
│  ├────────┼──────────┼──────┼────┼────────┤ │
│  │ Sonnet │ Anthropic│ $3.00│ 95 │ FP16   │ │
│  │ V4 Flash│ OpenRouter│$0.15│ 88 │ INT8   │ │
│  │ V4 Flash│ ProviderB│$0.09│ 85 │ INT4   │ │
│  │ Haiku  │ Anthropic│ $0.25│ 78 │ FP16   │ │
│  │ Llama3 │ Ollama   │$0.00│ 65 │ Q4_K_M │ │
│  └────────┴──────────┴──────┴────┴────────┘ │
└──────┬──────────────────────────────────────┘
       │
┌──────▼──────┐  ┌──────────────┐  ┌──────────┐
│  Dispatcher │──│   Providers  │──│  Ledger   │
│ (decompose, │  │ (Anthropic,  │  │ (cost per │
│  orchestrate)│  │  OpenAI, OR, │  │  subtask, │
│             │  │  Ollama...)  │  │  outcome) │
└─────────────┘  └──────────────┘  └──────────┘
       │
┌──────▼──────┐
│  Synthesizer │  → compress, deduplicate, format for validation
└──────┬──────┘
       │
┌──────▼──────┐
│  Validator   │  → cheap + premium model cross-check
└─────────────┘
```

---

## Provider Support (Planned)

| Provider    | Models                                        |
|-------------|-----------------------------------------------|
| Anthropic   | Claude 4 Sonnet, Claude 4 Opus, Claude 3.5 Haiku |
| OpenAI      | GPT-4.5, GPT-4o, GPT-4o mini, o3-mini         |
| OpenRouter  | 200+ models, multiple providers per model, various quant levels |
| Ollama      | All local models (Llama, Qwen, DeepSeek, Mistral) |
| Gemini      | Gemini 2.5 Pro, Gemini 2.5 Flash              |

---

## Roadmap

- [x] Project scaffolding & documentation
- [ ] Flat model registry with price, rank, quantization, reasoning cost
- [ ] Budget planner — given $X, select optimal model mix
- [ ] Scout phase — free/local parallel fan-out
- [ ] Narrow phase — cheap paid critique & compression
- [ ] Validate phase — minimal frontier model cross-check
- [ ] Reasoning token budget enforcement
- [ ] Provider adapters (Anthropic, OpenAI, OpenRouter, Ollama)
- [ ] Cost ledger & reporting
- [ ] Benchmark suite (quality vs. cost)
- [ ] Plugin system for custom selection strategies

---

## Getting Started

*Coming soon. No code has been written yet — this is the design phase.*

```bash
# Future state:
pip install tokenchurn
tokenchurn run --budget 5.00 "Implement a rate limiter in Rust"
```

---

## Related Projects

- **[llm-council](https://github.com/karpathy/llm-council)** — Multi-model debate via OpenRouter. The inspiration for council-style orchestration.
- **[Aider](https://github.com/paul-gauthier/aider)** — Git-first coding agent with repository maps.
- **[LiteLLM](https://github.com/BerriAI/litellm)** — Standardized API for 100+ LLM providers with cost tracking.
- **[Promptfoo](https://github.com/promptfoo/promptfoo)** — LLM evaluation and red-teaming harness.

---

## License

MIT
