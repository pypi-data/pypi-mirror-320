import logging
from typing import Iterator, List
from lite_llm_client._anthropic_client import AnthropicClient
from lite_llm_client._config import GeminiConfig, LLMConfig, OpenAIConfig, AnthropicConfig
from lite_llm_client._gemini_client import GeminiClient
from lite_llm_client._interfaces import InferenceOptions, LLMClient, LLMMessage, LLMMessageRole
from lite_llm_client._openai_client import OpenAIClient

from lite_llm_client._tracer import tracer

class LiteLLMClient():
  """
  This is lite-llm-client class.
  it supports three types of client

  OpenAI usage:

  >>> from lite_llm_client import LiteLLMClient, OpenAIConfig
  >>> client = LiteLLMClient(OpenAIConfig(api_key="your api key"))

  Gemini usage:

  >>> from lite_llm_client import LiteLLMClient, GeminiConfig
  >>> client = LiteLLMClient(GeminiConfig(api_key="your api key"))

  Anthropic usage:

  >>> from lite_llm_client import LiteLLMClient, AnthropicConfig
  >>> client = LiteLLMClient(AnthropicConfig(api_key="your api key"))
  """
  config:LLMConfig
  client:LLMClient=None

  def __init__(self, config:LLMConfig):
    self.config = config

    if isinstance(config, OpenAIConfig):
      self.client = OpenAIClient(config)
    elif isinstance(config, AnthropicConfig):
      self.client = AnthropicClient(config)
    elif isinstance(config, GeminiConfig):
      self.client = GeminiClient(config)

    if not self.client:
      raise NotImplementedError()
    
  def chat_completion(
      self,
      query:str,
      context:str=None,
      system_prompt:str=None,
      json_schema:dict=None,
      options:InferenceOptions=InferenceOptions()
      ):

    messages:List[LLMMessage]= []
    if system_prompt:
      messages.append(LLMMessage(role=LLMMessageRole.SYSTEM, content=system_prompt))
    if context:
      content = f'{context}\n{query}'
    else:
      content = query
    messages.append(LLMMessage(role=LLMMessageRole.USER, content=content))


    return self.chat_completions(messages=messages, json_schema=json_schema, options=options)

  @tracer.start_as_current_span("chat_completions")
  def chat_completions(self, messages:List[LLMMessage], json_schema:dict=None, options:InferenceOptions=InferenceOptions()):
    r"""chat completions
    
    :param messages: messages
    :param options: (optional) options for chat completions
    :return answer of LLM

    """

    completion = self.client.chat_completions(messages=messages, json_schema=json_schema, options=options)
    tracer.add_llm_output(output=completion)
    return completion

  @tracer.start_as_current_span("async_chat_completions")
  def async_chat_completions(self, messages:List[LLMMessage], options:InferenceOptions=InferenceOptions())->Iterator[str]:
    r"""chat completions
    
    :param messages: messages
    :param options: (optional) options for chat completions
    :return parts of answer. use generator

    """

    return self.client.async_chat_completions(messages=messages, options=options)