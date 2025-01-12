# Lite LLM Client

This project made for very light llm client.
the main idea is `do not use any llm client library`.

# setup

## How to pass `API_KEY`

1. use parameter of LLMConfig
```python
from lite_llm_client import LiteLLMClient, OpenAIConfig, LLMMessage, LLMMessageRole

client = LiteLLMClient(OpenAIConfig(api_key="YOUR API KEY"))
answer = client.chat_completions(messages=[LLMMessage(role=LLMMessage.USER, content="hello ai?")])

print(answer)
```
2. use .env
    - rename `.env_example` to `.env`
    - replace YOUR KEY to real api_key

```bash
OPENAI_API_KEY=YOUR KEY
ANTHROPIC_API_KEY=YOUR KEY
GEMINI_API_KEY=YOUR KEY
```


# Known issue

- gemini path may not stable. guide code has `/v1beta/...`. sometimes gemini returns http 500 error

# Roadmap

## Future version
- [ ] support multimodal (image and text)
- [ ] apply opentelemetry in async functions

## 0.2.0
- [x] `2025-01-11` support json mode(OpenAI)
- [x] `2024-11-01` apply opentelemetry in sync functions

## 0.1.2
- [x] `2024-10-25` fix exception when use new model name as str type

## 0.1.0
- [x] `2024-07-21` support OpenAI
- [x] `2024-07-25` support Anthropic
- [x] `2024-07-27` add options for inference
- [x] `2024-07-28` support Gemini
- [x] `2024-07-30` support streaming (OpenAI). simple SSE implement.
- [x] `2024-07-31` support streaming (Anthropic).
- [x] `2024-08-01` support streaming (Gemini). unstable google gemini.
- [x] `2024-08-13` support inference result(token count, stop readon)



# Reference

- [OpenAI REST API](https://platform.openai.com/docs/api-reference/chat/create)
- [Gemini REST API](https://ai.google.dev/gemini-api/docs/get-started/tutorial?lang=rest)