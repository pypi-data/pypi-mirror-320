from abc import ABC
from abc import abstractmethod

from typing import TypeVar, Generic

from ._property import Property
from .exceptions import PropertyError

PI = TypeVar('ParentInstance')
C = TypeVar('Content', bound=object)

class Possibility(ABC, Generic[C]):

    def __init__(
            self,
            parent: PI,
            attribute: str,
            value: C,
    ) -> None:
        self._value = value
        self._parent = parent
        self._attribute = attribute
    
    value: Property[C] = Property(attribute='_value', setter=True, deleter=True)
        
    parent: Property[PI] = Property(
        attribute='_parent',
        error=PropertyError,
        setter_error_arguments=("Setting 'parent' property is not permitted",),
        deleter_error_arguments=("Deleting 'parent' property is not permitted.",),
    )
    
    attribute: Property[str] = Property(
        attribute='_attribute',
        error=PropertyError,
        setter_error_arguments=("Setting 'attribute' property is not permitted.",),
        deleter_error_arguments=("Deleting 'attribute' property is not permitted.",),
    )

    @abstractmethod
    def __bool__(self) -> bool:
        pass

    def __call__(self, instance, owner) -> C:
        return self.value