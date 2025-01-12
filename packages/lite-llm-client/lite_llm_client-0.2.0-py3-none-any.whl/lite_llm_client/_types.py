
from abc import ABC, abstractmethod
from typing import Any, List, Literal


class _ITracer(ABC):
  @abstractmethod
  def start_as_current_span(self, name):
   raise NotImplementedError

  @abstractmethod
  def add_llm_info(self, llm_provider:str, model_name:str, messages:List[dict], extra_args:dict):
   raise NotImplementedError

  @abstractmethod
  def add_llm_output(self, output:Any, output_type:Literal['text', 'json']='json'):
   raise NotImplementedError

  @abstractmethod
  def add_llm_usage(self, prompt_tokens:int, completion_tokens:int, total_tokens:int):
   raise NotImplementedError
