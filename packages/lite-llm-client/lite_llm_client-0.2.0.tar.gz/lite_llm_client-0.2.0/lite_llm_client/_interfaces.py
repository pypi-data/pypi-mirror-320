from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntEnum
from typing import Iterator, List, Literal, Optional
from pydantic import BaseModel

@dataclass
class LLMConfig(ABC):
  @abstractmethod
  def get_chat_completion_url(self)->str:
    raise NotImplementedError

class LLMMessageRole(IntEnum):
  USER=1
  SYSTEM=2
  ASSISTANT=3

  def to_str(self):
    if self.value == 1:
      return "user"
    elif self.value == 2:
      return "system"
    elif self.value == 3:
      return "assistant"

class LLMMessage(BaseModel):
  role: LLMMessageRole
  content: str

class InferenceResult(BaseModel):
  finish_reason:Literal['empty', 'stop']='empty'
  prompt_tokens:int=0
  completion_tokens:int=0
  total_tokens:int=0

class InferenceOptions(BaseModel):
  top_p:Optional[float]=None
  top_k:Optional[float]=None
  max_tokens: Optional[int]=None
  temperature:float=0.0
  inference_result:InferenceResult=InferenceResult()


class LLMClient(ABC):

  @abstractmethod
  def chat_completions(self, messages:List[LLMMessage], options:InferenceOptions)->str:
    raise NotImplementedError

  @abstractmethod
  def async_chat_completions(self, messages:List[LLMMessage], options:InferenceOptions)->Iterator[str]:
    raise NotImplementedError