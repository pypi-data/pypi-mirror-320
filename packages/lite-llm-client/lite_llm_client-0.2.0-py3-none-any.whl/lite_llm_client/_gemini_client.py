import logging
from typing import Iterator, List

import requests
from lite_llm_client._config import GeminiConfig
from lite_llm_client._http_sse import SSEDataType, decode_sse
from lite_llm_client._interfaces import InferenceResult, LLMClient, LLMMessageRole, LLMMessage, InferenceOptions, InferenceOptions, LLMMessage, LLMMessageRole


class GeminiClient(LLMClient):
  config: GeminiConfig
  
  def __init__(self, config:GeminiConfig):
    self.config = config

  def _make_and_send_request(self, messages:List[LLMMessage], options:InferenceOptions, use_sse=False)->requests.Response:
    _options = options if options else InferenceOptions(temperature=1.0, max_tokens=800, top_p=0.8, top_k=10)
    msgs = []
    system_prompt = []
    for msg in messages:
      role = None
      if msg.role == LLMMessageRole.USER:
        role = "user"
      elif msg.role == LLMMessageRole.SYSTEM:
        role = "system"
        continue
      elif msg.role == LLMMessageRole.ASSISTANT:
        role = "assistant"
      else:
        logging.fatal("unknown role")

      msgs.append({"role": role, "parts": [{'text':msg.content}]})

    
    generationConfig = {
      "temperature": _options.temperature,
      "maxOutputTokens": _options.max_tokens,
      "topP": _options.top_p,
      "topK": _options.top_k,
    }
    request = {
      "contents": msgs,
      "generationConfig": generationConfig,
    }

    if len(system_prompt) > 0:
      request['system'] = "\n".join(system_prompt)

    logging.info(f'request={request}')

    action = 'generateContent'
    alt = ''
    if use_sse:
      action = 'streamGenerateContent'
      alt = 'alt=sse&'
    url = f'{self.config.get_chat_completion_url()}:{action}?{alt}key={self.config.api_key}'
    http_response = requests.api.post(
      url,
      headers={
        'Content-Type': 'application/json',
        },
      json=request
      )

    if http_response.status_code != 200:
      logging.fatal(f'status_code={http_response.status_code} response={http_response.text}')
      raise Exception(f'bad status_code: {http_response.status_code}')

    return http_response

  def _parse_response(self, inference_result:InferenceResult, response:dict):
    reason_map = {
      'STOP': 'stop'
    }

    candidates0 = response['candidates'][0]

    finishReason = candidates0['finishReason']
    inference_result.finish_reason = reason_map[finishReason]

    usageMetadata = response['usageMetadata']
    inference_result.prompt_tokens = usageMetadata['promptTokenCount']
    inference_result.completion_tokens = usageMetadata['candidatesTokenCount']
    inference_result.total_tokens = usageMetadata['totalTokenCount']

  def async_chat_completions(self, messages:List[LLMMessage], options:InferenceOptions)->Iterator[str]:
    http_response = self._make_and_send_request(messages=messages, options=options, use_sse=True)

    for event in decode_sse(response=http_response, data_type=SSEDataType.JSON):

      """ value example:
      {"candidates": [{"content": {"parts": [{"text": " project's source code, organized into folders and files.\n* **Documentation:**  Some projects have a dedicated \"docs\" folder or a link to external documentation.\n* **Issues:**  This section lists any reported problems or feature"}],"role": "model"},"finishReason": "STOP","index": 0,"safetyRatings": [{"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT","probability": "NEGLIGIBLE"},{"category": "HARM_CATEGORY_HATE_SPEECH","probability": "NEGLIGIBLE"},{"category": "HARM_CATEGORY_HARASSMENT","probability": "NEGLIGIBLE"},{"category": "HARM_CATEGORY_DANGEROUS_CONTENT","probability": "NEGLIGIBLE"}]}],"usageMetadata": {"promptTokenCount": 45,"candidatesTokenCount": 192,"totalTokenCount": 237}}
      """
      self._parse_response(options.inference_result, event.event_value)
      content = event.event_value['candidates'][0]['content']['parts'][0]
      char = content['text']
      yield char

  def chat_completions(self, messages:List[LLMMessage], options:InferenceOptions):
    http_response = self._make_and_send_request(messages=messages, options=options)
    response = http_response.json()
    logging.info(response)
    self._parse_response(options.inference_result, response)

    content = response['candidates'][0]['content']['parts'][0]
    return content['text']