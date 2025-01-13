
from typing import TypeVar, Type
from typing import Literal, Optional, Union

from .exceptions import MethodOverrideError

import inspect

CLASS = TypeVar('CLASS')
METHOD = TypeVar('METHOD')

class override:
    """`override` brings the `@override` decorator feature
    (introduced in python3.12), for all python versions.

    With a bit of tinkering with all existing python mechanisms,
    `override` class provides a simplistic (all complex operations
    kept hidden) way to keep your code error free.

    #### Working:

    `override` provides two static-methods to work with,
    `cls` and `mtd`.

    `mtd` sets the `__override__` attribute of any
    method it is decorated on top of, as True.

    `cls` is a decorator for `class` objects and
    should be used only on classes that are inheriting some
    other base class. On classes, that do not inherit any other
    base class it will do nothing.

    While using `cls`, if the child class has properties
    that are overloaded, and either `fset` or `fdel` or both are not
    defined in the child class, `cls` will make the child
    class use the base class's `fdel` and `fset`.

    Additionally, if any method found in the child class has an
    `__override__` attribute set to True (as a result of
    `mtd` decorator), It will check if the base class has
    that method or not, if not, it will raise `MethodOverrideError`
    (ultimately contributing towards maintaing large code bases (as
    it was for `typing.override`)).

    It will also check, any method having `metd` decorator
    is a child class or not (inheritance is present or not)
    If found it is not, `MethodOverrideError` will be raised.

    The methods or properties that are not explicitly defined in the child
    class, will be taken from the base class (no contribution here).

    #### Usage:

    NOTE: This is to be used only in the `.py` file and not in the stubs
    (`.pyi` file). Any method that is overriden does not need to be added
    in the stubs of the child class unless you want a different description
    docstring for that overriden method, it will fetch from the base class
    by default. Remember that this is a runtime check and static type
    checkers wont trigger any errors.

    ```python
    from modkit.typing import override

    class Base:
        def some_method(self) -> None: ...

        @property
        def some_property(self) -> int: ...
        
        @some_property.setter
        def some_property(self, value) -> None: ...
        
        @some_property.deleter
        def some_property(self) -> None: ...
    
    @override.cls
    class Child(Base):
        
        @override.mtd
        def some_method(self, some_value) -> None: ... # This is valid

        @override.mtd
        def some_other_method(self) -> None: ... # This is invalid

        @property
        def some_property(self) -> str: ...  # overloaded property
        # This property has no setter or deleter defined here
        # It will use the Base's setter and deleter.
    ```

    #### Extra Features and Working:

    `override.cls` looks for the methods and propeties in
    the recent or direct parent of the child class.

    To look at the top most, class for methods and properties,
    `override.look_in` can be used to set the default lookup.

    By default it is set to `'recent'`.

    Example:

    ```python
    from modkit.typing import override

    # At this point, defaut lookup is `recent`

    class Top:
        def some_method(self) -> None: ...
    
    @override.cls
    class Mid(Top):
        
        @override.mtd
        def some_method(self) -> str: ...

        def some_other_method(self) -> None: ...
    
    # still lookup is `recent`

    @override.cls
    class Bottom(Mid):
        
        @override.mtd
        def some_method(self) -> int: ...

        @override.mtd
        def some_other_method(self) -> str: ... # This is valid.
    ```

    However, if the lookup is set to `topmost` (can take only `topmost`
    or `recent`) as values.

    ```python
    from modkit.typing import override

    override.look_in('topmost')
    # This can be done in any point of time.

    class Top:
        def some_method(self) -> None: ...
    
    @override.cls
    class Mid(Top):
        
        @override.mtd
        def some_method(self) -> str: ...
        # This is valid as the top most class (Top) has a method
        # named some_method

        def some_other_method(self) -> None: ...
    
    @override.cls
    class Bottom(Mid):
        
        @override.mtd
        def some_method(self) -> int: ...

        @override.mtd
        def some_other_method(self) -> str: ... # This is invalid.
        # The topmost class `Top` does not have any method named
        # some_other_method.
    ```

    For default and general usage, do not change lookup for convenience.
    """

    @classmethod
    def look_in(cls, baseclass: Literal['topmost', 'recent'] = 'recent') -> None:
        """Change the default lookup.
        
        `override.cls` looks for the methods and propeties in
        the recent or direct parent of the child class.

        To look at the top most, class for methods and properties,
        `override.look_in` can be used to set the default lookup.

        By default it is set to `'recent'`.

        Example:

        ```python
        from modkit.typing import override

        # At this point, defaut lookup is `recent`

        class Top:
            def some_method(self) -> None: ...
        
        @override.cls
        class Mid(Top):
            
            @override.mtd
            def some_method(self) -> str: ...

            def some_other_method(self) -> None: ...
        
        # still lookup is `recent`

        @override.cls
        class Bottom(Mid):
            
            @override.mtd
            def some_method(self) -> int: ...

            @override.mtd
            def some_other_method(self) -> str: ... # This is valid.
        ```

        However, if the lookup is set to `topmost` (can take only `topmost`
        or `recent`) as values.

        ```python
        from modkit.typing import override

        override.look_in('topmost')
        # This can be done in any point of time.

        class Top:
            def some_method(self) -> None: ...
        
        @override.cls
        class Mid(Top):
            
            @override.mtd
            def some_method(self) -> str: ...
            # This is valid as the top most class (Top) has a method
            # named some_method

            def some_other_method(self) -> None: ...
        
        @override.cls
        class Bottom(Mid):
            
            @override.mtd
            def some_method(self) -> int: ...

            @override.mtd
            def some_other_method(self) -> str: ... # This is invalid.
            # The topmost class `Top` does not have any method named
            # some_other_method.
        ```

        For default and general usage, do not change lookup for convenience.
        """
        ...
    
    @staticmethod
    def cls(cls: CLASS) -> CLASS:
        """Override decorator for Child Class.

        `cls` is a decorator for `class` objects and
        should be used only on classes that are inheriting some
        other base class. On classes, that do not inherit any other
        base class it will do nothing.

        While using `cls`, if the child class has properties
        that are overloaded, and either `fset` or `fdel` or both are not
        defined in the child class, `cls` will make the child
        class use the base class's `fdel` and `fset`.

        Additionally, if any method found in the child class has an
        `__override__` attribute set to True (as a result of
        `mtd` decorator), It will check if the base class has
        that method or not, if not, it will raise `MethodOverrideError`
        (ultimately contributing towards maintaing large code bases (as
        it was for `typing.override`)).

        It will also check, any method having `metd` decorator
        is a child class or not (inheritance is present or not)
        If found it is not, `MethodOverrideError` will be raised.

        The methods or properties that are not explicitly defined in the child
        class, will be taken from the base class (no contribution here).
        """
        ...
    
    @staticmethod
    def mtd(mtd: METHOD) -> METHOD:
        """Override decorator for method.
        
        `mtd` sets the `__override__` attribute of any
        method it is decorated on top of, as True.
        """