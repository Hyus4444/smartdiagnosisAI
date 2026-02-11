#Documento que define un esquema de paginación genérico utilizando Pydantic. Este esquema se utiliza para estructurar la respuesta de las API que devuelven listas de 
#elementos, proporcionando información sobre el total de elementos, la cantidad de elementos devueltos, y la cantidad de elementos a omitir (skip) y a limitar (limit) 
#en la consulta. El uso de un modelo genérico permite reutilizar este esquema para diferentes tipos de datos, lo que facilita la implementación de paginación en diversas 
#partes de la aplicación.
from typing import Generic, TypeVar, List
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")
class Page(GenericModel, Generic[T]):
    items: List[T]
    total: int
    skip: int
    limit: int
