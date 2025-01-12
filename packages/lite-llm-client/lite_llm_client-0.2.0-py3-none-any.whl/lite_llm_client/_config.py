import os
from dotenv import load_dotenv
from enum import Enum
from typing import Optional, Union

from lite_llm_client._interfaces import LLMConfig

# load .env
load_dotenv()

###################################################
class OpenAIModel(Enum):
  GPT_4O = "gpt-4o"
  GPT_4O_MINI = "gpt-4o-mini"
  GPT_4_TURBO = "gpt-4-turbo"

class OpenAIConfig(LLMConfig):
  base_url: str
  api_key: str
  chat_completion_path: Optional[str] ="/v1/chat/completions"
  model:Union[OpenAIModel,str]

  def __init__(self,
               base_url:str="https://api.openai.com",
               api_key:str=None,
               model:Union[OpenAIModel,str]=OpenAIModel.GPT_4O):
    """
    parameters
    - api_key: if None, use environment variable "OPENAI_API_KEY"
    """

    self.base_url = base_url
    self.api_key = api_key
    if not self.api_key and "OPENAI_API_KEY" in os.environ:
      self.api_key = os.environ["OPENAI_API_KEY"]
    assert self.api_key and len(self.api_key) > 0, "api_key must be exists(check argument or environment variable OPENAI_API_KEY)"
    self.model = model
  
  def get_chat_completion_url(self)->str:
    return f'{self.base_url}{self.chat_completion_path}'

###################################################
class AnthropicModel(Enum):
  CLAUDE_3_5_SONNET_20240620="claude-3-5-sonnet-20240620"
  CLAUDE_3_OPUS_20240229="claude-3-opus-20240229"

class AnthropicConfig(LLMConfig):
  base_url: str
  api_key: str
  chat_completion_path: Optional[str] ="/v1/messages"
  model:Union[AnthropicModel,str]

  max_tokens:int=1024

  def __init__(self,
               base_url:str="https://api.anthropic.com",
               api_key:str=None,
               model:Union[AnthropicModel,str]=AnthropicModel.CLAUDE_3_5_SONNET_20240620):
    """
    parameters
    - api_key: if None, use environment variable "ANTHROPIC_API_KEY"
    """

    self.base_url = base_url
    self.api_key = api_key
    if not self.api_key and "ANTHROPIC_API_KEY" in os.environ:
      self.api_key = os.environ["ANTHROPIC_API_KEY"]
    assert self.api_key and len(self.api_key) > 0, "api_key must be exists(check argument or environment variable ANTHROPIC_API_KEY)"
    self.model = model

  def get_chat_completion_url(self)->str:
    return f'{self.base_url}{self.chat_completion_path}'

###################################################
class GeminiModel(Enum):
  GEMINI_1_5_FLASH="gemini-1.5-flash"
  GEMINI_1_5_PRO="gemini-1.5-pro"

class GeminiConfig(LLMConfig):
  base_url: str
  api_key: str
  chat_completion_path: Optional[str] ="/v1/models"
  model:str

  max_tokens:int=1024

  def __init__(self,
               base_url:str="https://generativelanguage.googleapis.com",
               api_key:str=None,
               model:Union[GeminiModel,str]=GeminiModel.GEMINI_1_5_FLASH):
    """
    parameters
    - api_key: if None, use environment variable "GEMINI_API_KEY"
    """

    self.base_url = base_url
    self.api_key = api_key
    if not self.api_key and "GEMINI_API_KEY" in os.environ:
      self.api_key = os.environ["GEMINI_API_KEY"]
    
    assert self.api_key and len(self.api_key) > 0, "api_key must be exists(check argument or environment variable GEMINI_API_KEY)"
    self.model = model if isinstance(model, str) else model.value

    #if not self.api_key:
    #  raise NotImplementedError()

  def get_chat_completion_url(self)->str:
    return f'{self.base_url}{self.chat_completion_path}/{self.model}'
