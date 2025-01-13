
from typing import TypeVar, Type
from typing import Literal, Optional, Union

from .exceptions import MethodOverrideError

import inspect

CLASS = TypeVar('CLASS')
METHOD = TypeVar('METHOD')

class override:
    _look_in: Literal['topmost', 'recent'] = 'recent'

    @classmethod
    def look_in(cls, baseclass: Literal['topmost', 'recent'] = 'recent') -> None:
        cls._look_in = baseclass
    
    @staticmethod
    def cls(cls: CLASS) -> CLASS:
        # For all members
        for name, member in inspect.getmembers(cls):

            # Handling missing property methods.
            if isinstance(member, property):

                # Try to find the property of current class
                # in base class, if no base class, exit.

                try:
                    all_bases = cls.__bases__
                except AttributeError:
                    continue

                if override._look_in == 'recent':
                    try:
                        base_member: Optional[property] = getattr(cls.__bases__[0], name)
                    except (IndexError, AttributeError):
                        continue
                elif override._look_in == 'topmost':
                    if not all_bases:
                        continue
                    
                    base = all_bases[0]
                    while all_bases:
                        base = all_bases[0]
                        try:
                            all_bases = base.__bases__
                            if all_bases[0] is object:
                                break
                        except AttributeError:
                            break
                    
                    try:
                        base_member: Union[property, None] = getattr(base, name)
                    except AttributeError:
                        continue
                
                # if property found in base class.
                if isinstance(base_member, property):
                    # if the setter of the property in current class
                    # is not set, but found in base class, use it.
                    if member.fset is None and base_member.fset is not None:
                        new_property = property(
                            fget=member.fget,
                            fset=base_member.fset,
                            fdel=member.fdel if member.fdel is not None else base_member.fdel,
                            # use base memeber's fdel if fdel is also not there.
                        )
                        setattr(cls, name, new_property)
                    
                    # if the deleter for the property in current class
                    # is not set, but found in base class, use it.
                    if member.fdel is None and base_member.fdel is not None:
                        new_property = property(
                            fget=member.fget,
                            fset=member.fset if member.fset is not None else base_member.fset,
                            # use base member's fset if member's is not present.
                            fdel=base_member.fdel
                        )
                        setattr(cls, name, new_property)
            elif inspect.isfunction(member) and hasattr(member, '__override__') and getattr(member, '__override__') == True:
                
                # At this point of time, the method is found to be
                # set as override.

                try:
                    all_bases = cls.__bases__
                except AttributeError:
                    # Case: No base class found but method is overriden
                    error = "{} method is found to be overriden but no base class found for {}"
                    raise MethodOverrideError(error, name, cls.__name__)

                if override._look_in == 'recent':
                    try:
                        base_method: Union[function, None] = getattr(cls.__bases__[0], name)
                    except AttributeError:
                        # Case: Base class is present but no method of such name found in the base class.
                        # and the method is overriden
                        error = "{} method is found to be overriden but no such method is found in the base class of {}. base_class_considered: {}"
                        raise MethodOverrideError(error, name, cls.__name__, cls.__bases__[0].__name__)

                    # Case: If found, do nothing. Only errors are captured here.
                elif override._look_in == 'topmost':

                    if not all_bases:
                        # method found but no base class.
                        error = "{} method is found to be overriden but no base class found for {}"
                        raise MethodOverrideError(error, name, cls.__name__)
                    
                    base = None
                    while all_bases:
                        base = all_bases[0]
                        try:
                            all_bases = base.__bases__
                            if all_bases[0] is object:
                                break
                        except AttributeError:
                            break
                    
                    try:
                        base_method: Optional[function] = getattr(base, name)
                    except AttributeError:
                        error = "{} method is found to be overriden but no such method is found in the base class of {}. base_class_considered: {}"
                        raise MethodOverrideError(error, name, cls.__name__, base.__name__)

        return cls
    
    @staticmethod
    def mtd(mtd: METHOD) -> METHOD:
        setattr(mtd, '__override__', True)
        return mtd