"""This module is the `core` of `Widgets` module.

This class contains definitons for different pre-made widgets. Currently it has
- `Label` Widget
- `Bar` Widget
- `Time` Widget
- `Tint` Widget Wrapper
"""

from ..types import Precursor, UnknownLength, Widget as WidgetType, CustomRender as CustomRenderType
from .abc import Widget, CustomRender, WidgetWrapper
from .._features.precursor import Precursor as PrecursorFeature
from ....tools.terminal import Color as _color
from threading import Thread
from typing import Union, Dict
import datetime

PrecursorError: Precursor.PrecursorError
Color: _color

class Label(Widget):
    """Progress Status Label Widget.
    
    This is a static widget with predefined length based calculated
    during initialization with no precursor requirements. Therefore,
    accessing precursor features will result in raising an exception.
    Rendering the widget returns the currently set label.
    """
    __name__: str
    def __init__(self, label: str = 'Loading', separator: str = ':') -> None:
        """Create a label widget with custom text."""

class Bar(CustomRender, PrecursorFeature):
    """Progess Status Bar Widget.
    
    This is a dynamically updating widget that depends completely on
    precursor backbone. Initially, it wont show any length. However,
    after first render, the length property can be accessed. The
    render method takes additional parameters to generate the bar at
    a given instant (supports extra normalization) with precursor
    support.
    """
    __name__: str
    def __init__(
            self,
            finished_marker: str = '█',
            unfinished_marker: str = '░',
            start_marker: str = '|',
            end_marker: str = '|'
    ) -> None:
        """Create a Bar widget with customizations."""

class Time(Widget, PrecursorFeature):
    """Elapsed Time (`HH:MM:SS`) Widget.
    
    This is a dynamically updating widget that depends completely on
    precursor backbone. It has a predefined length and returns the
    elapsed time at any given instant when the render method is called.
    """
    __name__: str
    def __init__(self, format: str = 'Elapsed Time: {}') -> None:
        """Create a Time widget with custom format.
        
        The format must contain `{}` which will be replaced by the
        elapsed time in `HH:MM:SS` format.
        """

class Tint(WidgetWrapper):
    """`Tint` Widget Wrapper class.
    
    This class wraps any widget and returns colored rendered output.
    Performance may differ based on how frequently the widget's
    output is rendered. Typically, `Label` does not cost any
    performance while `Bar` may or may not cost performance based on
    how intensive the task is or how fast the bar fills. This class
    automatically sets `__name__` and `__precursor__` based on the
    underlying widget and works exactly like any widget, except for
    colored rendering.

    NOTE: Using `isinstance` on this class will return
    `isinstance(self.widget, <class>)` and not `isinstance(self, <class>)`

    #### Usage

    Use the parameters of `__init__` of the widget to set color for
    that particular parameter.

    ```python
    from modkit.progress.bar import ProgressBar
    from modkit.progress.bar.widgets import Label, Tint, Color
    
    # colored Label
    colored_label = Tint(
        Label(
            label='loading',
            separator=':'
        ),
        label=Color.RED,
        separator=Color.WHITE
    )

    # colored Bar
    colored_bar = Tint(
        Bar(
            finished_marker='#',
            unfinished_marker='_',
            start_marker='>',
            end_marker='<',
        ),
        finished_marker=Color.GREEN,
        unfinished_marker=Color.YELLOW,
        start_marker=Color.RED,
        end_marker=Color.RED,
    )

    pbar = ProgressBar(
        10,
        100,
        colored_label,
        colored_bar,
        Time(), # Normal no color Elapsed Time.
    )
    ```
    """
    __name__: str
    widget: Union[WidgetType, CustomRenderType]
    def __init__(
            self,
            widget: Union[WidgetType, CustomRenderType],
            **kwargs: str
    ) -> None:
        """Create a Tint object with any widget.
        
        #### Usage

        Use the parameters of `__init__` of the widget to set color for
        that particular parameter.

        ```python
        from modkit.progress.bar import ProgressBar
        from modkit.progress.bar.widgets import Label, Tint, Color
        
        # colored Label
        colored_label = Tint(
            Label(
                label='loading',
                separator=':'
            ),
            label=Color.RED,
            separator=Color.WHITE
        )

        # colored Bar
        colored_bar = Tint(
            Bar(
                finished_marker='#',
                unfinished_marker='_',
                start_marker='>',
                end_marker='<',
            ),
            finished_marker=Color.GREEN,
            unfinished_marker=Color.YELLOW,
            start_marker=Color.RED,
            end_marker=Color.RED,
        )

        pbar = ProgressBar(
            10,
            100,
            colored_label,
            colored_bar,
            Time(), # Normal no color Elapsed Time.
        )
        ```
        """