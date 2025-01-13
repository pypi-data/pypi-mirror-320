from typing import TypeVar, Type, Generic
from typing import Union, Callable
from typing import Any, Tuple

E = TypeVar('Exception', bound=Exception)
T = TypeVar('T')

class Property(Generic[T]):
    def __init__(
            self,
            *,
            attribute: Union[str, None] = None,
            getter: Union[Callable[[Any], T],  None] = None,
            setter: Union[bool, Callable[[Any, Any], None], None] = False,
            deleter: Union[bool, Callable[[Any], None], None] = False,
            error: E = None,
            doc: Union[str, None] = None,
            default: Any = None,
            setter_error_arguments: Tuple[Any] = (),
            deleter_error_arguments: Tuple[Any] = (),
            deleter_deletes_attribute: bool = False,
    ) -> None:
        if getter is None: # treat it like a = Property(attribute='attrname')

            def _setter(cls, value) -> None: # default, sets the attribute
                setattr(cls, attribute, value)
                return None

            def _deleter(cls) -> None: # default, sets to None or deletes
                if deleter_deletes_attribute:
                    delattr(cls, attribute)
                else:
                    setattr(cls, attribute, None)
                return None
        
            if error is not None: # if error is provided.
                if isinstance(setter, bool) and not setter: # if setter is set to false, raise error if called
                    def _setter(cls, value) -> None:
                        raise error(*setter_error_arguments)
                if isinstance(deleter, bool) and not deleter: # if deleter is set to false, raise error if called
                    def _deleter(cls) -> None:
                        raise error(*deleter_error_arguments)
        
            self.property = property(lambda cls: getattr(cls, attribute, default), _setter, _deleter, doc)
        
        elif isinstance(getter, Callable):
        # treat it like
        # a = Property(attribute = 'attrname', logic = lambda: name is not None )

            # logic is callable here,
            def _getter(cls) -> Any:
                return getter(cls)
            
            if isinstance(setter, Callable):
                _setter = setter
            else:
                _setter = None
            
            if isinstance(deleter, Callable):
                _deleter = deleter
            else:
                _deleter = None
            
            if error is not None:
                if setter is None or setter is False:
                    def _setter(cls, value) -> None:
                        raise error(*setter_error_arguments)
                
                if deleter is None or deleter is False:
                    def _deleter(cls) -> None:
                        raise error(*deleter_error_arguments)
            
            self.property = property(_getter, _setter, _deleter, doc)

        self.__doc__ = doc
        self.__error__ = error
    
    def __get__(self, instance: Any, owner: Type[Any]) -> T:
        if instance is None:
            if self.__error__ is not None:
                raise self.__error__(f"Propeties cannot be accessed without initializing the class.")
            else:
                raise AttributeError(f"Propeties cannot be accessed without initializing the class.")
        return self.property.fget(instance)
    
    def __set__(self, instance: Any, value: Any) -> None:
        if instance is None:
            if self.__error__ is not None:
                raise self.__error__(f"Propeties cannot be accessed without initializing the class.")
            else:
                raise AttributeError(f"Propeties cannot be accessed without initializing the class.")
        return self.property.fset(instance, value)
    
    def __delete__(self, instance: Any) -> None:
        if instance is None:
            if self.__error__ is not None:
                raise self.__error__(f"Propeties cannot be accessed without initializing the class.")
            else:
                raise AttributeError(f"Propeties cannot be accessed without initializing the class.")
        return self.property.fdel(instance)
    
    def __docstring__(self) -> Union[str, None]:
        return self.__doc__