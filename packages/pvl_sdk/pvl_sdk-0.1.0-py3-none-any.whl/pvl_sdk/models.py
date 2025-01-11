from typing import List, Optional
from pydantic import BaseModel


class Node(BaseModel):
    id: str
    name: str
    interfaces: List[str]


class Lab(BaseModel):
    id: str
    name: str
    nodes: List[str]
