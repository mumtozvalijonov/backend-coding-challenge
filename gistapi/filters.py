from pydantic import BaseModel


class GistSearchQuery(BaseModel):
    limit: int = 10
    offset: int = 0
