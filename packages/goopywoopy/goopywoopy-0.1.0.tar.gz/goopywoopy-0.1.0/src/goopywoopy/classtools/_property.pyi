from typing import TypeVar, Type, Generic
from typing import Union, Callable
from typing import overload
from typing import Any, Tuple

E = TypeVar('Exception', bound=Exception)
T = TypeVar('T')

class Property(Generic[T]):
    """
    Dynamic property generator class.

    In a `.py` file,
    ```python
    class SomeClass:
        Property_A = Property(...) # this will work

        def someFunction(self):
            self.Property_B = Property(...) # this will not work
    ```

    In a `.pyi` (stub) file,
    ```python
    class SomeClass:
        @property
        def Property_A(self) -> Any:
            \"\"\"docstring here\"\"\"
    ```

    NOTE: The `Property` class is not related to the built-in `property`
    class. However, the working is the same and is dynamic providing a
    diverse range of automation. Writing `@property` in the stub file
    does not interrupt or hinder execution and is only for type hints.
    """

    @overload
    def __init__(
            self,
            *,
            attribute: str,
            setter: bool = False,
            deleter: bool = False,
            error: E = None,
            default: Any = None,
            setter_error_arguments: Tuple[Any] = (),
            deleter_error_arguments: Tuple[Any] = (),
            deleter_deletes_attribute: bool = False,
    ) -> None:
        """Create a `Property`, bound to an attribute.
        
        #### Parameter Description

        `attribute` is the name of the attribute to bind the `getter`
        function, which internally, fetches the value of the `attribute`.

        If `setter` is set to `True`, the `setter` will be enabled, and the
        attribute can be set using the property.

        >>> object.property_name = value # runs the setter

        If `deleter` is set to `True`, the `deleter` will be enabled and the
        attribute can be deleted using the property.

        >>> del object.property_name # runs the deleter

        `error` will be raised if either `setter` or `deleter` or both are
        set to `False`. This prevents the user to set or delete a property.
        Provide the error class such as `ValueError` or `IndexError` or some
        custom exception to be raised. The Exception will be raised with either
        `setter_error_arguments` or `deleter_error_arguments`.
        
        Basically, `ValueError(*setter_error_arguments)` and so on.

        If `default` is provided, if the attribute does not exist or unbound,
        prevents from raising `AttributeError`.

        The `deleter_deletes_attribute` is by default `False` and sets the attribute
        to `None` when the deleter runs. However, setting it to `True` will actually
        delete the attribute.
        """
        ...
    
    @overload
    def __init__(
            self,
            *,
            getter: Callable[[Any], T],
            setter: Union[Callable[[Any, Any], None], None] = None,
            deleter: Union[Callable[[Any], None], None] = None,
            error: E = None,
            setter_error_arguments: Tuple[Any] = (),
            deleter_error_arguments: Tuple[Any] = (),
    ) -> None:
        """
        Create a `Property` object, with an explicit, `getter`, `setter`
        and `deleter`.

        #### Parameter Description

        `getter` accesses an attribute/returns a value based on it.

        ```python
        class XYZ:
            def __init__(self, value) -> None:
                self._value = value
            
            x = Property(getter=lambda cls: cls._value)
            x_is_not_none = Property(
                getter=lambda cls: cls._value is not None
            )
        ```

        `setter` is by default `None`, if `error` is provided, it will raise
        the error. If `setter` is provided, it will be used instead.

        ```python
        class XYZ:
            def __init__(self, value) -> None:
                self._value = value
            
            x = Property(
                getter=lambda cls: cls._value,
                setter=lambda cls, value: setattr(cls, '_value', value),
            )
        ```

        `deleter` is by default `None` and will raise `error` if provided.
        If `deleter` is provided, it will be used instead.

        ```python
        class XYZ:
            def __init__(self, value) -> None:
                self._value = value
            
            x = Property(
                getter=lambda cls: cls._value,
                setter=lambda cls, value: setattr(cls, '_value', value),
                deleter=lambda cls: del cls._value
            )
        ```

        If either `setter` or `deleter` or both are not provided, and `error`
        is provided, it will raise the error, with `setter_error_arguments`
        or `deleter_error_arguments` respectively.

        `error` can take values such as `ValueError` or `IndexError` or any
        class that inherits the `Exception` class or `Exception` class itself.
        """
        ...


    def __get__(self, instance: Any, owner: Type[Any]) -> T: ...
    def __set__(self, instance: Any, value: Any) -> None: ...
    def __delete(self, instance: Any) -> None: ...
    def __docstring__(self) -> Union[str, None]: ...