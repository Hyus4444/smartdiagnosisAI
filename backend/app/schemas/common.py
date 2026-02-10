from typing import Generic, TypeVar, List
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")
class Page(GenericModel, Generic[T]):
    items: List[T]
    total: int
    skip: int
    limit: int
