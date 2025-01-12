import importlib
import logging
import os
from typing import Any, List, Literal

from lite_llm_client._types import _ITracer


class _DummyTracer(_ITracer):
  """
  open telemetry가 활성화 되지 않았을때 아무것도 안할 tracer
  """
  def start_as_current_span(self, name):
    def decorator(func):
      def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
      return wrapper
    return decorator

  def add_llm_info(self, llm_provider:str, model_name:str, messages:List[dict], extra_args:dict):
    pass

  def add_llm_output(self, output:Any, output_type:Literal['text', 'json']='json'):
    pass

  def add_llm_usage(self, prompt_tokens:int, completion_tokens:int, total_tokens:int):
    pass


tracer:_ITracer=None

try:
    # opentelemetry 모듈이 로딩 가능하면 _Tracer 객체 생성
    importlib.import_module('opentelemetry')

    OTLP_ENDPOINT = os.getenv("LLC_OTLP_ENDPOINT")
    OTLP_SERVICE_NAME = os.getenv("LLPC_OTLP_SERVICE_NAME")
    PHOENIX_PROJECT = os.getenv("LLC_PHOENIX_PROJECT")

    if PHOENIX_PROJECT is None:
      logging.warning("Please ensure that LLC_PHOENIX_PROJECT is specified in the environment")

    if OTLP_ENDPOINT:
      from lite_llm_client._otel_tracer import _OtelTracer
      logging.info(f'Using LLC_OTLP_ENDPOINT({OTLP_ENDPOINT})')
      tracer = _OtelTracer()
    else:
      logging.warning("Please ensure that LLC_OTLP_ENDPOINT is specified in the environment")
      logging.warning("Using `dummy tracer`")
      tracer = _DummyTracer()


except ImportError as e:
    # opentelemetry 모듈이 없으면 _DummyTracer 객체 생성
    logging.warning(e)
    tracer = _DummyTracer()

logging.info(f"Loaded tracer={tracer}")