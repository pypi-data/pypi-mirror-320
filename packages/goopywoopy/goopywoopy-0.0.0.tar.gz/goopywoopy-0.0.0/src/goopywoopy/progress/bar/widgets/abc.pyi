"""`abc` Module (for `Widgets`)

This module contains abstract classes for creating custom widgets. Any Basic Widget must inherit
from `Widget` Base class and any `Bar` Type Widget must inherit from `CustomRender` Base class.
Similarly, creation of widget wrappers such as the `Tint` widget wrapper, must be done by inheriting
the `WidgetWrapper` class.

Each `Widget` and `CustomRender` must inherit the `Precursor` Feature from
`modkit.progress.bar._features` if they require `precursor` access. The `precursor` stores all information
such as `time elapsed`, `percentage of task completed` and as such. Therefore, inheriting from the
`Precursor` feature class enables them access to the `Precursor` Thread Handler Class.
"""

from abc import (
    ABC,
    ABCMeta,
    abstractmethod
)
from typing import Union, Any
from ..types import UnknownLength, Precursor, Widget as WidgetType, CustomRender as CustomRenderType
from ....tools.terminal import Color as _color
from threading import Thread

Color = _color

class InCaseWrapperMeta(ABCMeta, type):
    """Meta Class for Handling `WidgetWrapper` checks.

    This class overrides the `__instancecheck__` mechanism of `Widget` ABC class,
    such that, when an instance of `WidgetWrapper` is given, it should check the
    `instance.widget` attribute instead of `instance` itself. This makes sure
    that whenever an `WidgetWrapper` is used in the arg 1 of `isinstance`, it should
    check the underlying widget and not the wrapper itself.

    This ensures that any `WidgetWrapper` is just a shell and ultimately the underlying
    widget is the main entity.
    """
    def __isinstancecheck__(cls, instance: Any) -> bool: ...

class Widget(ABC, object, metaclass=InCaseWrapperMeta):
    """ABC Base class for all Widget type objects.
    
    This is a default architecture for all widgets, regardless
    of their type. Must contain:
    - `render` method.
    - `thread` property.
    - `is_sensitive` property.
    - `precursor` property with `fset`, `fget` and `fdel`. (Use
        `PrecursorType`).
    - `length` property
    """

    @abstractmethod
    def render(self) -> str:
        """Renders widget's current state and returns a string."""
    
    @property
    @abstractmethod
    def thread(self) -> Thread:
        """The underlying thread that is responsible for updating
        this widget's precursor attribute."""

    @property
    @abstractmethod
    def is_sensitive(self) -> bool:
        """True if thread needs to be run separately for constant
        update."""

    @property
    @abstractmethod
    def precursor(self) -> Precursor:
        """Precursor getter, setter, deleter."""

    @property
    @abstractmethod
    def length(self) -> Union[int, UnknownLength]:
        """Absolute fixed length of the widget."""

class CustomRender(Widget, ABC):
    """Derived ABC class for custom rendering of widgets based
    on available space and further normalization required."""
    @abstractmethod
    def render(self) -> str:
        """Renders widget's current state based on possible length and normalization."""
    @abstractmethod
    def set_possible_length(self, length: float) -> None:
        """Set possible length for custom rendering."""
    def set_normalization(self, normalization: float) -> None:
        """Set normalization for custom rendering."""

class WidgetWrapper(Widget, ABC):
    """Derived ABC class for wrapping Widgets. This class facilitaties
    wrapping the base widgets for adding external functionalities.
    The subclass must contain a `widget` attribute.
    """
    widget: Union[WidgetType, CustomRenderType]