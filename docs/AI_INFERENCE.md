# Local AI Inference Architecture (Google Gemma 4)

## Overview
DME AgentFlow rejects third-party AI APIs (e.g. OpenAI, Anthropic, cloud Gemini) to guarantee total enterprise sovereignty. All inference executes locally on customer-controlled compute through `llama.cpp` using optimized GGUF quantizations.

## Recommended Models

| Model | Architecture | Quantization | RAM / VRAM Req | Target Use Case |
|---|---|---|---|---|
| **Gemma 4 E4B Instruct** | Dense Transformer | Q4_K_M | 4 GB | High-throughput classification, routing, and extraction |
| **Gemma 4 12B Instruct** | Dense Transformer | Q4_K_M | 9 GB | Complex business document reasoning and synthesis |
| **Gemma 4 26B A4B** | MoE (Active 4B) | Q4_K_M | 16 GB | High-capacity multi-turn complex decision trees |
| **Gemma 4 31B Instruct** | Dense Transformer | Q4_K_M | 22 GB | Enterprise legal, contractual, and technical drafting |

## Structured JSON Generation
To guarantee deterministic execution of workflow branches, Gemma 4 is prompted with precise JSON schemas and constrained sampling parameters:
- `temperature`: `0.1` to `0.3`
- `grammar`: Constrained BNF/JSON grammar where supported
- Fallback sanitizer: Cleans Markdown code blocks (` ```json `) to guarantee valid JSON serialization.
