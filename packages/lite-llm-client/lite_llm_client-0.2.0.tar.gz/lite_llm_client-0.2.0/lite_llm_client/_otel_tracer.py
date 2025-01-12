import json
import os
from typing import Any, List, Literal

from lite_llm_client._types import _ITracer

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from opentelemetry.trace import get_current_span, Span
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

from openinference.semconv.resource import ResourceAttributes

otlp_exporter = OTLPSpanExporter(
    endpoint=os.environ["LLC_OTLP_ENDPOINT"],
    insecure=True # TODO: need consideration
)

PHOENIX_PROJECT = os.getenv("LLC_PHOENIX_PROJECT")
OTLP_SERVICE_NAME = os.getenv("LLC_OTLP_SERVICE_NAME")

_resource_attributes = {
  SERVICE_NAME: "lite-llm-client" if not OTLP_SERVICE_NAME else OTLP_SERVICE_NAME,
}

if PHOENIX_PROJECT:
  # phoenix에 프로젝트 이름 표시하는 용도
  _resource_attributes[ResourceAttributes.PROJECT_NAME] = PHOENIX_PROJECT #https://github.com/Arize-ai/arize-otel-python/blob/main/src/arize_otel/_register.py#L6

resource = Resource(attributes=_resource_attributes)

# 트레이서 프로바이더 설정
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

from openinference.semconv.trace import SpanAttributes, MessageAttributes, MessageContentAttributes
from openinference.semconv.trace import OpenInferenceSpanKindValues, OpenInferenceMimeTypeValues

class _OtelTracer(_ITracer):

  def start_as_current_span(self, name):
    return tracer.start_as_current_span(name)

  def add_llm_info(self, llm_provider:str, model_name:str, messages:List[dict], extra_args:dict):
    span = get_current_span()

    span.set_attribute(SpanAttributes.OPENINFERENCE_SPAN_KIND, OpenInferenceSpanKindValues.LLM.value)
    span.set_attribute(SpanAttributes.LLM_PROVIDER, llm_provider)
    span.set_attribute(SpanAttributes.LLM_MODEL_NAME, model_name)

    for index, m in enumerate(messages):
      span.set_attribute(f'{SpanAttributes.LLM_INPUT_MESSAGES}.{index}.{MessageAttributes.MESSAGE_ROLE}', m["role"])
      span.set_attribute(f'{SpanAttributes.LLM_INPUT_MESSAGES}.{index}.{MessageAttributes.MESSAGE_CONTENT}', m["content"])

    span.set_attribute(SpanAttributes.INPUT_VALUE, messages[-1]["content"])

    span.set_attribute(SpanAttributes.LLM_INVOCATION_PARAMETERS, json.dumps(extra_args))

  def add_llm_output(self, output:Any, output_type:Literal['text', 'json']='json'):
    r"""
    LLM의 출력 값을 설정합니다.

    :param output: 출력 값
    :param output_type: 'text' or 'json' - output의 데이터 형식을 입력.
    """
    span = get_current_span()

    value = output
    if output_type == 'text':
      span.set_attribute(SpanAttributes.OUTPUT_MIME_TYPE, OpenInferenceMimeTypeValues.TEXT.value)
    elif output_type == 'json':
      span.set_attribute(SpanAttributes.OUTPUT_MIME_TYPE, OpenInferenceMimeTypeValues.JSON.value)

      if isinstance(output, dict):
        value = json.dumps(output, ensure_ascii=False)
    else:
      raise ValueError(f"unknown type ({output_type})")
    span.set_attribute(SpanAttributes.OUTPUT_VALUE, value)

    span.set_status(status=Status(StatusCode.OK))

  def add_llm_usage(self, prompt_tokens:int, completion_tokens:int, total_tokens:int):
    span = get_current_span()
    span.set_attribute(SpanAttributes.LLM_TOKEN_COUNT_PROMPT, prompt_tokens)
    span.set_attribute(SpanAttributes.LLM_TOKEN_COUNT_COMPLETION, completion_tokens)
    span.set_attribute(SpanAttributes.LLM_TOKEN_COUNT_TOTAL, total_tokens)


