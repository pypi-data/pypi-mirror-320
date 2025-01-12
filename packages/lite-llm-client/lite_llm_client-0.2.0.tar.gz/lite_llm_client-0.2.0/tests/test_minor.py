import os
import sys
from typing import List

sys.path.append(os.path.abspath('.'))
import logging
from _share import get_test_messages
from lite_llm_client._config import OpenAIConfig
from lite_llm_client._lite_llm_client import LiteLLMClient
from lite_llm_client import LLMMessage, LLMMessageRole
from lite_llm_client._tracer import tracer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ],
    force=True
)



client = OpenAIConfig()
llc = LiteLLMClient(client)
#answer = llc.chat_completion('hi', context="친절하게 답해줘", system_prompt="you are helpful assistant.")
#logging.info(answer)

from opentelemetry.trace import Span, get_current_span
from openinference.semconv.trace import (
    SpanAttributes,
    OpenInferenceSpanKindValues,
    EmbeddingAttributes,
    DocumentAttributes,
    RerankerAttributes,
)

def llm(query:str):
    messages = []
    messages.append(LLMMessage(role=LLMMessageRole.SYSTEM, content="you are helpful assistant"))
    messages.append(LLMMessage(role=LLMMessageRole.USER, content="나는 세개의 계란을 가지고 있어."))
    messages.append(LLMMessage(role=LLMMessageRole.ASSISTANT, content="네, 당신은 세개의 계란을 가지고 있습니다."))
    messages.append(LLMMessage(role=LLMMessageRole.USER, content=query))
    answer = llc.chat_completions(messages=messages)
    logging.info(answer)
    return answer

@tracer.start_as_current_span("_embedding function")
def _embedding(query:str, docs:List[str]):
    span = get_current_span()
    span.set_attribute(SpanAttributes.OPENINFERENCE_SPAN_KIND, OpenInferenceSpanKindValues.EMBEDDING.value)
    span.set_attribute(SpanAttributes.EMBEDDING_MODEL_NAME, "bge-m3")

    vecs = []
    for doc in docs:
        vecs.append([1.231, 1.331, 0.8, -0.77])

    for index, vec in enumerate(vecs):
        span.set_attribute(f'{SpanAttributes.EMBEDDING_EMBEDDINGS}.{index}.{EmbeddingAttributes.EMBEDDING_TEXT}', docs[index])
        span.set_attribute(f'{SpanAttributes.EMBEDDING_EMBEDDINGS}.{index}.{EmbeddingAttributes.EMBEDDING_VECTOR}', vec)

@tracer.start_as_current_span("_retriever function")
def _retriever(query:str):
    span = get_current_span()
    span.set_attribute(SpanAttributes.OPENINFERENCE_SPAN_KIND, OpenInferenceSpanKindValues.RETRIEVER.value)

    docs = ['관련문서X', '관련문서1', '관련문서2']
    span.set_attribute(SpanAttributes.INPUT_VALUE, query)

    for index, doc in enumerate(docs):
        span.set_attribute(f'{SpanAttributes.RETRIEVAL_DOCUMENTS}.{index}.{DocumentAttributes.DOCUMENT_ID}', index)
        span.set_attribute(f'{SpanAttributes.RETRIEVAL_DOCUMENTS}.{index}.{DocumentAttributes.DOCUMENT_CONTENT}', doc)
        span.set_attribute(f'{SpanAttributes.RETRIEVAL_DOCUMENTS}.{index}.{DocumentAttributes.DOCUMENT_METADATA}', '{"METADATA": "test", "src":"/mnt/d/test"}')
        span.set_attribute(f'{SpanAttributes.RETRIEVAL_DOCUMENTS}.{index}.{DocumentAttributes.DOCUMENT_SCORE}', 0.8217)

    _embedding(query, docs)

    return docs

@tracer.start_as_current_span("_rerank function")
def _rerank(query:str, docs:List[str]):
    span = get_current_span()
    span.set_attribute(SpanAttributes.OPENINFERENCE_SPAN_KIND, OpenInferenceSpanKindValues.RERANKER.value)
    span.set_attribute(RerankerAttributes.RERANKER_MODEL_NAME, 'bge-m3-reranker')
    span.set_attribute(RerankerAttributes.RERANKER_QUERY, query)
    span.set_attribute(RerankerAttributes.RERANKER_TOP_K, 10)

    for index, doc in enumerate(docs):
        span.set_attribute(f'{RerankerAttributes.RERANKER_INPUT_DOCUMENTS}.{index}.{DocumentAttributes.DOCUMENT_ID}', index)
        span.set_attribute(f'{RerankerAttributes.RERANKER_INPUT_DOCUMENTS}.{index}.{DocumentAttributes.DOCUMENT_CONTENT}', doc)
        span.set_attribute(f'{RerankerAttributes.RERANKER_INPUT_DOCUMENTS}.{index}.{DocumentAttributes.DOCUMENT_METADATA}', '{"METADATA": "test", "src":"/mnt/c/test"}')
        span.set_attribute(f'{RerankerAttributes.RERANKER_INPUT_DOCUMENTS}.{index}.{DocumentAttributes.DOCUMENT_SCORE}', 0.8821)

    ordered_docs = sorted(docs) # RERANK를 이용한 재정렬

    for index, doc in enumerate(ordered_docs):
        span.set_attribute(f'{RerankerAttributes.RERANKER_OUTPUT_DOCUMENTS}.{index}.{DocumentAttributes.DOCUMENT_ID}', index)
        span.set_attribute(f'{RerankerAttributes.RERANKER_OUTPUT_DOCUMENTS}.{index}.{DocumentAttributes.DOCUMENT_CONTENT}', doc)
        span.set_attribute(f'{RerankerAttributes.RERANKER_OUTPUT_DOCUMENTS}.{index}.{DocumentAttributes.DOCUMENT_METADATA}', '{"METADATA": "test", "src":"/mnt/c/test"}')
        span.set_attribute(f'{RerankerAttributes.RERANKER_OUTPUT_DOCUMENTS}.{index}.{DocumentAttributes.DOCUMENT_SCORE}', 0.8821)

    return ordered_docs

@tracer.start_as_current_span("test_chain 시작")
def test_chain():
    span = get_current_span()
    span.set_attribute(SpanAttributes.OPENINFERENCE_SPAN_KIND, OpenInferenceSpanKindValues.CHAIN.value)

    query = "여기에서 내가 두개를 먹으면 몇개가 남지?"
    span.set_attribute(SpanAttributes.INPUT_VALUE, query)
    docs = _retriever(query) # RETRIEVER
    ordered_docs = _rerank(query, docs) # RERANK

    answer = "N개"
    answer = llm(query=query) # LLM
    import json
    tracer.add_llm_output({"result":answer}, 'json')

@tracer.start_as_current_span("/http_test")
def test_http():
    logging.info("BEGIN")
    print(tracer)
    span = get_current_span()
    span.set_attribute('http.method', 'POST')
    span.set_attribute('http.server_name', '0.0.0.0')
    span.set_attribute('http.scheme', 'http')
    span.set_attribute('net.host.port', 8082)
    span.set_attribute('host.port', '172.16.10.14:8082')
    span.set_attribute('http.target', '/http_test?query1=value')
    span.set_attribute('http.user_agent', 'Mozilla...')
    span.set_attribute('http.flavor', '1.1')
    span.set_attribute('http.route', '/http_test')
    span.set_attribute('http.status_code', 200)


    print('test done')

if __name__ == "__main__":
    print("gogo chain")
    #test_chain()
    test_http()