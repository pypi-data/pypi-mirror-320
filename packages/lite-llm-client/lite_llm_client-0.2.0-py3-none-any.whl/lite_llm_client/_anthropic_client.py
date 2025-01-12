from enum import Enum
import logging
from typing import Iterator, List

import requests
from lite_llm_client._config import AnthropicConfig
from lite_llm_client._http_sse import SSEDataType, decode_sse
from lite_llm_client._interfaces import InferenceOptions, InferenceResult, LLMClient, LLMMessage, LLMMessageRole
from lite_llm_client._tracer import tracer


class AnthropicClient(LLMClient):
  config: AnthropicConfig
  
  def __init__(self, config:AnthropicConfig):
    self.config = config

  def _make_and_send_request(self, messages:List[LLMMessage], options:InferenceOptions, use_sse=False)->requests.Response:
    _options = options if options else InferenceOptions()
    msgs = []
    system_prompt = []
    for msg in messages:
      role = None
      if msg.role == LLMMessageRole.USER:
        role = "user"
      elif msg.role == LLMMessageRole.SYSTEM:
        system_prompt.append(msg.content)
        continue
      elif msg.role == LLMMessageRole.ASSISTANT:
        role = "assistant"
      else:
        logging.fatal("unknown role")

      msgs.append({"role": role, "content": msg.content})

    """
    https://docs.anthropic.com/en/api/messages
    
    system_prompt does not include messages.
    """
    model_name = self.config.model.value if isinstance(self.config.model, Enum) else self.config.model
    request = {
      "model": model_name,
      'max_tokens': self.config.max_tokens,
      "temperature": _options.temperature,
    }

    if _options.top_k:
      request['top_k'] = _options.top_k
    if _options.top_p:
      request['top_p'] = _options.top_p

    if use_sse:
      request['stream'] = True

    tracer.add_llm_info(llm_provider="OpenAI", model_name=model_name, messages=msgs, extra_args=request)

    request["messages"] = msgs

    if len(system_prompt) > 0:
      request['system'] = "\n".join(system_prompt)

    http_response = requests.api.post(
      self.config.get_chat_completion_url(),
      headers={
        'Content-Type': 'application/json',
        'x-api-key': f'{self.config.api_key}',
        'anthropic-version': '2023-06-01',
        },
      json=request
      )

    if http_response.status_code != 200:
      logging.fatal(f'response={http_response.text}')
      raise Exception(f'bad status_code: {http_response.status_code}')

    return http_response

  def _parse_response(self, inference_result:InferenceResult, response:dict):
    reason_map = {
      'end_turn': 'stop'
    }

    if 'stop_reason' in response:
      stop_reason = response['stop_reason']
      inference_result.finish_reason = reason_map[stop_reason]

    if 'delta' in response:
      delta = response['delta']
      if 'stop_reason' in delta:
        stop_reason = delta['stop_reason']
        inference_result.finish_reason = reason_map[stop_reason]

    if 'usage' in response:
      usage = response['usage']

      if 'input_tokens' in usage:
        inference_result.prompt_tokens = usage['input_tokens']

      if 'output_tokens' in usage:
        inference_result.completion_tokens = usage['output_tokens']

      if inference_result.prompt_tokens > 0 and inference_result.completion_tokens > 0:
        inference_result.total_tokens = inference_result.prompt_tokens + inference_result.completion_tokens

  def async_chat_completions(self, messages:List[LLMMessage], options:InferenceOptions)->Iterator[str]:
    http_response = self._make_and_send_request(messages=messages, options=options, use_sse=True)

    for event in decode_sse(http_response, data_type=SSEDataType.JSON):
      #logging.info(event.event_value)
      self._parse_response(options.inference_result, event.event_value)

      """
      event_value example:
      {"type":"message_start","message":{"id":"msg_01C4SDTbBPX6yQiFSrgnY8jD","type":"message","role":"assistant","model":"claude-3-opus-20240229","content":[],"stop_reason":null,"stop_sequence":null,"usage":{"input_tokens":13,"output_tokens":3}}             }
      """
      event_type = event.event_value['type']
      if event_type == 'message_start':
        # just start signal
        continue

      if event_type == 'content_block_start':
        # ok start
        continue

      if event_type == 'ping':
        # what the ping
        continue

      if event_type == 'content_block_stop':
        continue
      if event_type == 'message_delta':
        """
        {"type":"message_delta","delta":{"stop_reason":"end_turn","stop_sequence":null},"usage":{"output_tokens":12}              }
        """
        continue
      if event_type == 'message_stop':
        continue

      if event_type == 'content_block_delta':
        """delta example:
        {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"Hello! How"} }
        """
        delta = event.event_value['delta']
        char = delta['text']
        yield char


  def chat_completions(self, messages:List[LLMMessage], options:InferenceOptions):
    http_response = self._make_and_send_request(messages=messages, options=options)
    response = http_response.json()

    #logging.info(response)
    inference_result = InferenceResult()
    self._parse_response(inference_result, response)
    tracer.add_llm_usage(
      prompt_tokens=inference_result.prompt_tokens,
      completion_tokens=inference_result.completion_tokens,
      total_tokens=inference_result.total_tokens,
      )
    if options is not None:
      options.inference_result = inference_result

    content = response['content'][0]
    return content['text']