__author__ = "ziyan.yin"
__date__ = "2025-01-05"


from abc import ABCMeta
from typing import Annotated, Any

from fastapi.params import Depends


default_dependency_override = {}


class DependencyMetaClass(ABCMeta):
    __root__: Any = None
    
    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        attrs: dict,
        root: bool = False,
        override: bool = False
    ):
        new_cls = super().__new__(mcs, name, bases, attrs)
        if not root:
            if new_cls.__root__ is None:
                new_cls.__root__ = new_cls
            elif override:
                default_dependency_override[new_cls.__root__] = new_cls
            return Annotated[new_cls, Depends(new_cls)]
        return new_cls



class Service(metaclass=DependencyMetaClass, root=True):
    __slot__ = ()
    