import typing as tp

from pydantic import BaseModel


class Message(BaseModel):
    content: str
    role: tp.Literal['system', 'user', 'assistant']


class ActionGenerationResponse(BaseModel):
    new_messages: list[Message]
    action: str
