from abc import (
    ABC,
    ABCMeta,
    abstractmethod
)
from typing import Any, Union
from ..types import Precursor, UnknownLength, Widget as WidgetType, CustomRender as CustomRenderType
from ....tools.terminal import Color
from threading import Thread

class InCaseWrapperMeta(ABCMeta):
    def __instancecheck__(cls, instance: Any) -> bool:
        if hasattr(instance, 'widget') and instance.widget is not None: 
            return isinstance(instance.widget, cls)
        return super().__instancecheck__(instance)

class Widget(ABC, object, metaclass=InCaseWrapperMeta):
    @abstractmethod
    def render(self) -> str: ...
    
    @property
    @abstractmethod
    def thread(self) -> Thread: ...

    @property
    @abstractmethod
    def is_sensitive(self) -> bool: ...

    @property
    @abstractmethod
    def precursor(self) -> Precursor: ...

    @precursor.setter
    @abstractmethod
    def precursor(self, precur: Precursor) -> None: ...

    @precursor.deleter
    @abstractmethod
    def precursor(self) -> None: ...

    @property
    @abstractmethod
    def length(self) -> Union[int, UnknownLength]: ...

class CustomRender(Widget, ABC):
    @abstractmethod
    def set_possible_length(self, length: float) -> None: ...

    @abstractmethod
    def set_normalization(self, normalization: float) -> None: ...

class WidgetWrapper(Widget, ABC):
    widget: Union[WidgetType, CustomRenderType] = None