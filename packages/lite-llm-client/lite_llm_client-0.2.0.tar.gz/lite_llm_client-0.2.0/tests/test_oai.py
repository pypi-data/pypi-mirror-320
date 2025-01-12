import os
import sys

sys.path.append(os.path.abspath('.'))
import logging
from _share import get_json_schema, get_json_test_messages, get_test_messages
from lite_llm_client import OpenAIConfig, OpenAIModel
from lite_llm_client import LiteLLMClient
from lite_llm_client import InferenceOptions

def gen_instance()->LiteLLMClient:
  client = LiteLLMClient(OpenAIConfig(
    model=OpenAIModel.GPT_4O_MINI
    ))

  return client

def test_oai_sync():
  client = gen_instance()
  options = InferenceOptions()

  answer = client.chat_completions(messages=get_test_messages(), options=options)
  logging.info("{}".format(answer))
  logging.info(options.inference_result)

def test_oai_json_sync():
  client = gen_instance()
  options = InferenceOptions()

  answer = client.chat_completions(messages=get_json_test_messages(), json_schema=get_json_schema(), options=options)
  logging.info("{}".format(answer))
  logging.info(options.inference_result)

def test_oai_async():
  client = gen_instance()
  options = InferenceOptions()

  answer = client.async_chat_completions(messages=get_test_messages(), options=options)
  for a in answer:
    logging.debug(a)

  logging.info(options.inference_result)
  

