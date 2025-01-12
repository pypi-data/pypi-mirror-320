from enum import Enum, auto
import json
import logging
from typing import Iterator, Union
from pydantic import BaseModel
from requests import Response

class SSEEvent(BaseModel):
  event_name:str
  event_value:Union[str,dict]

class SSEDataType(Enum):
  TEXT=auto()
  JSON=auto()

def _parse_sse(line:bytes):
  first_comma = line.find(b': ', 0)
  if first_comma == -1:
    raise ValueError(f'sse parse error (1)##{line}')

  name = line[:first_comma] 
  value = line[first_comma+2:]
  return name.decode(),value.decode()


def decode_sse(response:Response, data_type:SSEDataType, eoe:str='[DONE]')->Iterator[SSEEvent]:
  ct = response.headers.get('Content-Type') # Content-Type: text/event-stream; utf-8
  ct_values = ct.split(';')
  assert ct_values[0] == 'text/event-stream', f"response content-type does not 'text/event-stream' but '{ct_values[0]}'"

  #current_event = None
  for line in response.iter_lines(delimiter=b'\n'):
    if len(line) == 0:
      # SKIP empty line
      continue
    if line == b'\r':
      # for gemini.. maybe data delimiter is \r\n
      continue

    parsed_line = _parse_sse(line)

    if parsed_line[0] == 'event':
      #logging.debug(f'got event: {parsed_line[1]}')
      #current_event = parsed_line[0]
      continue

    if parsed_line[0] == 'data' and parsed_line[1] == eoe:
      #logging.debug("END OF EVENT")
      break

    #logging.debug(f'event({current_event}), value({parsed_line[1]})')

    value:str
    if SSEDataType.JSON == data_type:
      value = json.loads(parsed_line[1])
    #elif SSEDataType.TEXT == data_type:
    else:
      value = parsed_line[1]

    yield SSEEvent(event_name=parsed_line[0], event_value=value)
  