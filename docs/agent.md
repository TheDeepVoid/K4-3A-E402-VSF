# Agent Documentation

## What Was Done

This section logs the work completed by previous agents.

### Agent 1 (Initial Setup)

**Date**: September 2026

**Completed Tasks**:

1. **Created AI Provider Infrastructure**
   - `codebase/providers/base.py` - Abstract base class for all AI providers
   - `codebase/providers/openai_provider.py` - OpenAI implementation
   - `codebase/providers/gemini_provider.py` - Google Gemini implementation
   - `codebase/providers/openrouter_provider.py` - OpenRouter implementation
   - `codebase/providers/omniroute_provider.py` - OmniRoute with fallback support

2. **Created Template System**
   - `codebase/docs/system_prompt_template.md` - System prompt templates for VLearn Pulse
   - `codebase/docs/test_cases_template.md` - 15 test cases for evaluation

3. **Created Evaluation Framework**
   - `codebase/eval.py` - Evaluation script that loads test cases from MD file
   - `codebase/tests/test_cases.py` - Loads test cases from `test_cases_template.md`
   - `codebase/config/system_prompt.py` - Loads prompt from MD file

4. **Created Configuration**
   - `codebase/config/env.py` - Loads API keys from .env file
   - `.env.example` - Template for API keys
   - `codebase/requirements.txt` - Python dependencies

5. **Documentation**
   - `codebase/README.md` - Project overview
   - Translated templates to Vietnamese

6. **Git Management**
   - All changes committed to `TheDeepVoid` branch
   - Note: GitHub push failed due to authentication

### Agent 2 (Cheapest live models)

**Date**: September 2026

**Completed Tasks**:

- Looked up official pricing / deprecation pages (OpenAI, Gemini, OpenRouter, OmniRoute).
- Switched demo/eval defaults to the cheapest **still-served** chat models.
- Documented IDs that are retired or should not be used.

---

## Cheapest still-served models (as of Sep 2026)

Use these IDs. Do **not** use deprecated aliases (`gpt-3.5-turbo`, `gemini-pro`, `gemini-1.5-flash`).

| Provider | Model ID | Why this one | Approx. price |
| --- | --- | --- | --- |
| **OpenAI** | `gpt-5-nano` | Cheapest currently listed chat model on OpenAI pricing | $0.05 / $0.40 per 1M tokens |
| **Gemini** | `gemini-2.5-flash-lite` | Cheapest current Gemini text model; 1.5 / 2.0 / `gemini-pro` are deprecated | $0.10 / $0.40 per 1M tokens |
| **OpenRouter** | `google/gemma-4-31b-it:free` | $0 on OpenRouter (rate-limited). Paid fallback: `mistralai/mistral-nemo` | Free / ~$0.02–$0.03 per 1M |
| **OmniRoute** | `gpt-5-nano` | OmniRoute is an OpenAI-compatible router; start with the cheapest OpenAI-class ID so it can pick the cheapest route | Routed; list price follows the upstream model |

**Do not use (retired / being shut down):**

- OpenAI: `gpt-3.5-turbo`, `gpt-3.5-turbo-16k`, old `gpt-4` snapshots — migrate to `gpt-5-nano` (cheap) or `gpt-4.1-mini` (quality).
- Gemini: `gemini-pro`, `gemini-1.5-flash`, `gemini-1.5-pro`, `gemini-2.0-flash` — migrate to `gemini-2.5-flash-lite`.
- OpenRouter: bare `gpt-3.5-turbo` without a vendor prefix — use `google/gemma-4-31b-it:free` or `openai/gpt-5-nano`.

Sources checked: [OpenAI pricing](https://developers.openai.com/api/docs/pricing), [OpenAI deprecations](https://developers.openai.com/api/docs/deprecations), [Gemini deprecations](https://ai.google.dev/gemini-api/docs/deprecations), [OpenRouter `/api/v1/models`](https://openrouter.ai/api/v1/models), [OmniRoute](https://www.omniroute.online/).

---

## Instructions for Next Agent

To continue this work, follow these steps.

### 1. Setup Environment

```bash
# Navigate to project
cd /home/aminix/Projects/K4-3A-E402-VSF

# Copy .env.example to .env and add your API keys
cp .env.example .env

# Install dependencies
pip install -r codebase/requirements.txt
```

### 2. Run the Pipeline (cheapest live models)

```bash
# Demo — cheapest still-served model per provider
python codebase/demo.py --provider openai --model gpt-5-nano
python codebase/demo.py --provider gemini --model gemini-2.5-flash-lite
python codebase/demo.py --provider openrouter --model google/gemma-4-31b-it:free
python codebase/demo.py --provider omniroute --model gpt-5-nano

# Evaluation — same cheapest IDs
python codebase/eval.py --provider openai --model gpt-5-nano
python codebase/eval.py --provider gemini --model gemini-2.5-flash-lite
python codebase/eval.py --provider openrouter --model google/gemma-4-31b-it:free
python codebase/eval.py --provider omniroute --model gpt-5-nano
```

If an OpenRouter `:free` model is rate-limited, fall back to:

```bash
python codebase/eval.py --provider openrouter --model mistralai/mistral-nemo
```

### 3. Add New Providers

To add a new AI provider:

1. Create `codebase/providers/<provider_name>_provider.py`
2. Inherit from `BaseAIProvider` in `base.py`
3. Implement `chat_completion()` and `get_embeddings()` methods
4. Add to `codebase/providers/__init__.py`

### 4. Update Test Cases

Edit `codebase/docs/test_cases_template.md` to add/modify test cases. The eval.py will automatically load from this file.

### 5. Update System Prompt

Edit `codebase/docs/system_prompt_template.md` to modify AI behavior. The config will automatically load from this file.

### 6. Commit Changes

```bash
git add -A
git commit -m "feat: description of changes"
git push origin TheDeepVoid
```

---

## Project Structure

```
K4-3A-E402-VSF/
├── .env.example              # API keys template
├── codebase/
│   ├── providers/            # AI provider implementations
│   │   ├── base.py
│   │   ├── openai_provider.py
│   │   ├── gemini_provider.py
│   │   ├── openrouter_provider.py
│   │   └── omniroute_provider.py
│   ├── docs/
│   │   ├── system_prompt_template.md
│   │   └── test_cases_template.md
│   ├── config/
│   │   ├── env.py
│   │   └── system_prompt.py
│   ├── tests/
│   │   └── test_cases.py
│   ├── eval.py
│   ├── demo.py
│   └── requirements.txt
└── docs/
    ├── agent.md          # This file
    └── tutorial.md       # Vietnamese tutorial
```

---

## Notes

- Providers load API keys from `.env` file using `config/env.py`
- Test cases are defined in `codebase/docs/test_cases_template.md` (Markdown)
- System prompts are defined in `codebase/docs/system_prompt_template.md` (Markdown)
- Default chat model is `gpt-5-nano` (cheapest still-served OpenAI ID)
- All changes should be committed to `TheDeepVoid` branch
- Push to GitHub manually if auth fails
- Re-check provider pricing pages before a live demo; cheapest IDs change
