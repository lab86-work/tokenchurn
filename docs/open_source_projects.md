Here is the comprehensive list of the open-source projects, coding tools, and agent frameworks for building multi-model architectures.

The list is categorized by their core function within an agentic pipeline to help you select the exact layers you need for your custom harness.

### Multi-Model Debate & Blueprint Repositories

These are the foundational reference projects that demonstrate how to constrain models or force them into debate and consensus loops.

*   **karpathy/llm-council:** A minimal harness using OpenRouter to fan-out queries to multiple models, force them into a blind peer review, and synthesize a final answer using a "Chairman" model.

*   **karpathy/autoresearch:** A highly constrained autonomous ML engineer loop that strictly isolates an agent to a single file, forces a 5-minute training loop, and evaluates the output to accept or reject the commit.

*   **ChatArena / FastChat:** Environments for side-by-side LLM execution, blind judging, and multi-agent game theory. Essential for building the state management of model-vs-model debates.

*   **Promptfoo:** A testing and evaluation harness that allows you to hit multiple model APIs in parallel with the same prompt and programmatically grade their outputs.


### Open-Source Coding Agents & IDE Integrations

These projects are complete applications designed specifically for software engineering. You can fork them or extract their context-management logic for your own harness.

**ProjectPrimary FocusKey FeaturesAider**Git-first terminal workflowBuilds a comprehensive repository map using tree-sitter. Treats all AI outputs as git commits for easy rollbacks and reviews.**Cline**VS Code integrated autonomyUses a strict "Plan then Act" loop. Heavily leverages the Model Context Protocol (MCP) to interact securely with local tools and browsers.**OpenHands**Fully sandboxed autonomyPreviously OpenDevin. Provides a secure Dockerized environment where the agent can run bash scripts, edit files, and test code without host machine risk.**Roo-Code**Autonomous editor pluginHighly active fork of Cline. Focuses on rapid iteration and execution of coding tasks directly within the IDE ecosystem.**SWE-agent**Autonomous bug fixingUses a custom Agent-Computer Interface (ACI) to autonomously navigate GitHub repositories, read issues, and submit pull requests.**OpenCode**Modern terminal IDESupports running multiple parallel agents simultaneously, integrating heavily with Language Server Protocols (LSP) for code accuracy.

### Multi-Agent Orchestration Frameworks

If you are building a harness where multiple models need to maintain state, pass messages to one another, or assume specific roles (e.g., Coder vs. Reviewer), these are the core Python/TypeScript frameworks to use.

**FrameworkArchitecture StyleBest Use CaseLangGraph**Graph-based state machineComplex, stateful, multi-step agent architectures requiring cyclic reasoning, built-in persistence layers, and human-in-the-loop approvals.**Microsoft AutoGen**Conversational orchestrationResearch and advanced experimental workflows where different models debate, collaborate, and hand off tasks natively.**CrewAI**Role-based teamsFast prototyping of specialized agent teams. Maps workflows to distinct personas (e.g., QA, Developer, Architect) with defined boundaries.**OpenAI Agents SDK**Provider-agnostic routingA lightweight Python framework built around tool calling, MCP, and guardrails. It supports OpenAI APIs alongside 100+ other local and cloud models.**MetaGPT**Simulated software companySimulates an entire software development pipeline. You assign different LLMs to act as Product Managers, Architects, and Engineers.**Mastra**TypeScript-firstOpen-source TypeScript framework for agents and workflows, featuring built-in evaluations, memory, and a unified router for 40+ model providers.**EvoAgentX**Self-evolving workflowsA modular framework designed to automatically construct multi-agent workflows and continuously test/optimize agent behavior through iterative loops.

### Model Routing & API Gateways

To build a multi-model harness, you must abstract the API layer so your code does not have to manage the distinct formats of OpenAI, Anthropic, Google, and local servers.

*   **LiteLLM:** An open-source Python library that standardizes over 100+ LLM APIs into the exact same OpenAI format. It handles translation, rate limits, fallbacks, and cost tracking natively.

*   **OpenRouter:** A unified API gateway that provides a single key to access almost every proprietary and open-weight model in existence.

*   **Ollama:** The standard open-source application for running LLMs locally. Crucial if your harness utilizes a fast, local model for rapid verification or syntax checking.
