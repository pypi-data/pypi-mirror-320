from typing import Any, TypeVar, Generic, Callable, Union
from typing import Iterable, Tuple, List, Dict
from typing import overload, Protocol

R = TypeVar('R')
C = TypeVar('C', bound=Callable)
B = TypeVar('B')

class RandomAlgorithmHelper(Protocol):
    def __call__(self) -> int:
        """Returns a random SEED based on current system time."""
        ...

class RandomIntegerProtocol(Protocol):
    @overload
    def __call__(self) -> int:
        """Returns a random integer between -10000 and 10000."""
        ...
    @overload
    def __call__(self, range: Tuple[int, int], /) -> int:
        """Returns a random integer between two values (ends non-inclusive)."""
        ...
    @overload
    def __call__(self, range: List[int], /) -> int:
        """Returns a random integer between two values (ends inclusive)."""
        ...
    @overload
    def __call__(self, range: Dict[int, int], *, include_left: bool = True, include_right: bool = True) -> int:
        """Use a Dict to define a custom range.
        
        For example:
        ```python
        range = {0: 100} # 0 to 100
        ```

        and use the `include` parameters to set which side to include.
        """
        ...

class RandomAlgorithmType_I(Protocol):
    def __call__(self, pool: Iterable[B], /) -> B:
        """Takes a pool of values to randomly choose one and return it."""
        ...

class RandomAlgorithmType_II(Protocol):
    def __call__(self, pool: Iterable[B], *, condition: Callable[[B], bool]) -> B:
        """Takes a pool of values and chooses eligible elements based on condition,
        and then chooses a random value from the eligible elements.
        """
        ...

class Random(Generic[R, C]):
    """`Random`.
    
    As the name suggests, this class helps choose a random value from a
    given pool of possible values. This class contains several pre-defined
    protocols/algorithms to get the random element.

    The protocols can be either passed to the constructor or can be used
    independently.
    ```python
    >>> randomvalue = Random([1, 2, 3, 4], algorithm=Random.DEFAULT) # valid
    >>> Random.DEFAULT([1, 2, 3])
    3 # or some other random value.
    ```

    Protocols:
    - `SEED` (Generates a random value based on system time) `(cannot be used in the constructor)`
    - `RANDINT` (Generates a random integer) `(cannot be used in the constructor)`
    - `DEFAULT` (Default random function)
    - `SHUFFLE` (Shuffles the pool and returns the first element)
    - `WEIGHTED` (Considers length of each element as a factor) `(elements must support len function or elements must be int)`
    - `WALK` (Takes a random walk from left to right)
    - `REVERSE_WALK` (Takes a random walk from right to left)
    - `MIDDLE_OUT` (Start from the middle and randomly choose a value outward)
    - `CYCLIC` (Cycle through the pool starting at a random index)
    - `FREQUENCY` (Considers frequency of an element as a factor)
    - `BINARY_SPLIT` (Split and randomly select an element from either from the front or end)
    - `HASHED` (Uses Hash of the Seed to select a random value)
    - `ROTATED` (Rotate the pool by a random number of steps and returns the first element)
    - `SUM` (Computes cumulative sum of weights and chooses a random range and then a random element)

    It can be used as a `Descriptor`, For example:
    ```python
    class SomeClass:
        attribute = Random([2, 3, 5, 20], Random.WALK)
        # here the attribute will have the final `int` value
        # and not the `Random` class object.
    ```

    The random choice can be directly assigned during initialization,
    For example:
    ```python
    >>> value = Random([1, 2, 3], Random.HASHED)()
    # the parenthesis at the end calls
    # the __call__ method of Random class and assigns
    # the random value to `value` variable
    ```
    """
    
    # Helper and Randint
    SEED: RandomAlgorithmHelper
    RANDINT: RandomIntegerProtocol

    # TYPE I algorithms
    DEFAULT: RandomAlgorithmType_I
    SHUFFLE: RandomAlgorithmType_I
    WEIGHTED: RandomAlgorithmType_I
    WALK: RandomAlgorithmType_I
    REVERSE_WALK: RandomAlgorithmType_I
    MIDDLE_OUT: RandomAlgorithmType_I
    CYCLIC: RandomAlgorithmType_I
    FREQUENCY: RandomAlgorithmType_I
    BINARY_SPLIT: RandomAlgorithmType_I
    HASHED: RandomAlgorithmType_I
    ROTATED: RandomAlgorithmType_I
    SUM: RandomAlgorithmType_I

    # TYPE II algorithms
    REJECTION_SAMPLING: RandomAlgorithmType_II

    @overload
    def __init__(self, pool: Iterable[R], algorithm: C) -> None:
        """Create a `Random` object with an iterable of possible values.
        
        The `algorithm` parameter can be chosen from the pre-defined `TYPE_I`
        values.

        If the algorithm is chosen to be a custom made one, it must take an
        iterable of values and return one randomly.

        NOTE: This definition is for `TYPE_I` algorithms only.
        """
        ...
    @overload
    def __init__(self, pool: Iterable[R], algorithm: C, condition: Callable[[R], bool]) -> None:
        """Create a `Random` object with an iterable of possible values.
        
        The `algorithm` parameter can be chosed from the pre-defined `TYPE_II`
        values.

        If the algorithm is chosen to be a custom made one, it must take an iterable
        of values and a `condition` parameter which determines the eligible pool from
        which the final random value will be chosen.

        NOTE: This definiton is for `TYPE_II` algorithms only.
        """
        ...
    
    def __random__(self) -> R:
        """Processor method for `Random`.
        
        It is responsible for picking a random value from the pool. This method
        is run automatically during initialization and calling it repeatedly
        will keep on changing the random choice.
        """
        ...
    
    @property
    def redo(self) -> R:
        """Choose again and return the value."""
        ...
    
    def __call__(self) -> R:
        """Called object for `Random`.
        
        This method, when called, returns the chosen random value.
        """
        ...
    
    def __int__(self) -> int: ...
    def __float__(self) -> float: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...

    def __len__(self) -> int:
        """Returns the length of any integer or value that supports __len__."""
        ...
    
    def __get__(self, instance: type, owner: type) -> R:
        """Descriptor function to return the random choice directly to any attribute."""
        ...