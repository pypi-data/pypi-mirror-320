import os
import sys

sys.path.append(os.path.abspath('.'))
import logging
from _share import get_test_messages
from lite_llm_client import GeminiConfig, GeminiModel
from lite_llm_client import LiteLLMClient
from lite_llm_client import InferenceOptions

def gen_instance()->LiteLLMClient:
  client = LiteLLMClient(GeminiConfig(
    model=GeminiModel.GEMINI_1_5_PRO
    ))
  client = LiteLLMClient(GeminiConfig(
    model='gemma-2-9b-it'
    ))

  return client

def test_gemini_sync():
  client = gen_instance()
  options = InferenceOptions()

  answer = client.chat_completions(messages=get_test_messages(), options=options)
  logging.info("{}".format(answer))
  logging.info(options.inference_result)

def test_gemini_async():
  client = gen_instance()
  options = InferenceOptions()

  answer = client.async_chat_completions(messages=get_test_messages(), options=options)
  for a in answer:
    logging.info(a)

  logging.info(options.inference_result)