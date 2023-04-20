from typing import Type, TypeVar, Generic

T = TypeVar("T", bound="Singleton")

class Singleton_Meta(type):
    @property
    def instance(cls:Type[T]) -> T: # type: ignore
        return cls()
    
class Singleton(Generic[T], metaclass=Singleton_Meta):
    """单例类，通过instance属性访问唯一实例"""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance