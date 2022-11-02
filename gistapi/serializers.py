from pydantic import BaseModel


class GistSearchBody(BaseModel):
    username: str
    pattern: str
