import os
import sys
from typing import List, Union

sys.path.append(os.path.abspath('.'))
import logging
from _share import get_test_messages
from lite_llm_client import AnthropicConfig 
from lite_llm_client import AnthropicModel
from lite_llm_client import InferenceOptions
from lite_llm_client import LiteLLMClient

logging.basicConfig(level='debug')

def gen_instance()->LiteLLMClient:
  client = LiteLLMClient(AnthropicConfig(model=AnthropicModel.CLAUDE_3_OPUS_20240229))

  return client

def test_anthropic_sync():
  client = gen_instance()
  options = InferenceOptions()

  answer = client.chat_completions(messages=get_test_messages(), options=options)
  logging.info("{}".format(answer))
  logging.info(options.inference_result)


def test_anthropic_async():
  client = gen_instance()
  options = InferenceOptions()

  answer = client.async_chat_completions(messages=get_test_messages(), options=options)
  for a in answer:
    logging.info(a)
  logging.info(options.inference_result)

