from abc import ABC
from abc import abstractmethod

from typing import TypeVar, Generic
from typing import Any

PI = TypeVar('ParentInstance')
C = TypeVar('Content', bound=object)

class Possibility(ABC, Generic[C]):
    """
    A class that further extends the functionality of return values
    of a method or property.

    #### Requirement Case:

    Let us assume there is a class called `some_class`,
    >>> obj = some_class()
    
    And, this class has a `property/method` that returns a value, say, `int`.
    
    ```python
    >>> obj.property_name
    10 # say it was 10
    ```
    
    Now, we cannot further create/access any method such that,
    
    >>> obj.property_name.<extra-method/property>
    
    This is where `Possibility` comes in.

    #### Usage:

    Continuing, the above example, let us create that 
    `<extra-method/property>` using `Possibility`.

    First, lets create a class named `Extra` (could be anything). Remember,
    we have to inherit the `Possibility` class and mandatorily create
    `__bool__` method. (as this is an abstract method.)

    ```python
    from modkit.classtools import Possibility
    from typing import Generic, TypeVar

    T = TypeVar('T')

    # inherit Possibility,
    # the generic class is just optional, it is for type hints.
    class Extra(Possibility, Generic[T]):
        # no need to define __init__
        # let us define __bool__ first
        # the Extra class will inherit 3 properties named:
        # `value`, `parent`, `attribute`.
        # where, `parent` has an attribute named `attribute` whose 
        # value is `value`.

        # for a basic example, lets say it checks if the value property
        # is 0 or not.
        def __bool__(self) -> bool:
            return self.value == 0
            # returns True if 0 else False.
        
        # let us create a method named <is_10>
        def is_10(self) -> bool:
            return self.value == 10
    ```

    Once we are done creating the `Extra` class. Let us now look at the
    `some_class`, let's say we are modifying a property named, `index`
    (could be anything).

    ```python
    class some_class:
        ... # rest of the code.

        @property
        def index(self) -> int:
            return 10
        
        ... # rest of the code.
    ```

    We will modify this in the following way:

    ```python
        ... # rest of the code.

        @property
        def index(self) -> Extra[int]:
            return Extra(parent=self, attribute='index', value=10)
        
        ... # rest of the code.
    ```

    This will add the functionality we defined earlier named `is_10` which
    checks if the value is 10 or not.

    ```python
    >>> obj = some_class()
    >>> obj.index.is_10()
    True

    # however, to access the value (i.e., `10`)
    >>> obj.index() # even though it was a property.
    10
    ```
    """

    def __init__(
            self,
            parent: PI,
            attribute: str,
            value: C,
    ) -> None:
        """
        Initialize the derived class of `Possibility` class.

        #### Parameter Description

        `parent` refers to the parent class of `attribute`.

        `attribute` is the name of the attribute to be used.

        `value` is the value of the attribute.

        ### Warning
        
        Do not override this method.
        """
        ...
    
    @abstractmethod
    def __bool__(self) -> bool:
        """Implement this method for `if <derived-class>` statements."""
        ...
    
    def __call__(self, instance: Any, owner: Any) -> C: ...