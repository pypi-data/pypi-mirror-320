from typing import TypeVar, Generic, Callable, Union
from typing import Iterable, Tuple, List, Dict
from typing import overload

from ...classtools import Property

R = TypeVar('R')
C = TypeVar('C', bound=Callable)
B = TypeVar('B')

class Random(Generic[R, C]):
    @staticmethod
    def SEED() -> int:
        import time
        return int((time.time() * 1000000) % 1000000)

    @overload
    @staticmethod
    def RANDINT() -> int: ...
    @overload
    @staticmethod
    def RANDINT(range: Tuple[int, int], /) -> int: ...
    @overload
    @staticmethod
    def RANDINT(range: List[int], /) -> int: ...
    @overload
    @staticmethod
    def RANDINT(
            range: Dict[int, int],
            *,
            include_left: bool = True,
            include_right: bool = True,
    ) -> int: ...

    @staticmethod
    def RANDINT(
            range: Union[Tuple[int, int], List[int], Dict[int, int]] = [-10000, 10000],
            include_left: bool = True,
            include_right: bool = True
    ) -> int:
        _seed = Random.SEED()
        if isinstance(range, Tuple):
            # non inclusive (a, b)
            return (range[0] + 1) + (_seed % (range[1] - (range[0] + 1)))
        elif isinstance(range, List):
            # inclusive [a, b]
            return range[0] + (_seed % (range[1] - range[0] + 1))
        elif isinstance(range, Dict):
            if len(range) != 1:
                raise ValueError("There should only be one interval in the dict: {int: int}.")
            
            minimum = list(range.keys())[0]
            maximum = range[minimum]

            # both inclusive
            if include_left and include_right:
                return Random.RANDINT([minimum, maximum])
            elif not include_left and not include_right:
                return Random.RANDINT((minimum, maximum))
            elif include_left and not include_right:
                # first inclusive, second non-inclusive (a, b]
                return minimum + (_seed % (maximum - minimum))
            else:
                return (minimum + 1) + (_seed % (maximum - (minimum + 1)))
        else:
            raise ValueError(f"The range parameter should be a Tuple, List or Dict, found: {type(range)}.")  
    
    @staticmethod
    def DEFAULT(pool: Iterable[B], /) -> B:
        index = Random.RANDINT({0: len(pool)}, include_right=False)
        return pool[index]
    
    @staticmethod
    def SHUFFLE(pool: Iterable[B], /) -> B:
        shuffled = pool[:]
        for i in range(len(shuffled) - 1, 0, -1):
            j = Random.RANDINT([0, i])
            shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
        return shuffled[0]
    
    @staticmethod
    def WEIGHTED(pool: Iterable[B], /) -> B:
        if not all(isinstance(item, (str, int, List, Tuple, Dict)) for item in pool):
            raise ValueError("All elements must have measurable length for weights.")
        
        weights = [len(str(item)) if isinstance(item, int) else len(item) for item in pool]
        total = sum(weights)
        random_value = Random.RANDINT([0, total])
        current_sum = 0

        for value, weight in zip(pool, weights):
            current_sum += weight
            if random_value < current_sum:
                return value
    
    @staticmethod
    def REJECTION_SAMPLING(pool: Iterable[B], *, condition: Callable[[B], bool]) -> Union[B, None]:
        eligible = [value for value in pool if condition(value)]

        if not eligible:
            return None
        
        return Random.DEFAULT(eligible)
    
    @staticmethod
    def WALK(pool: Iterable[B], /) -> B:
        index = Random.RANDINT({0: len(pool)}, include_right=False)
        steps = Random.RANDINT([-2, 2])
        new_index = (index + steps) % len(pool)
        return pool[new_index]
    
    @staticmethod
    def MIDDLE_OUT(pool: Iterable[B], /) -> B:
        middle = len(pool) // 2
        offset = Random.RANDINT({0: len(pool)}, include_right=False)
        index = (middle + offset) % len(pool)
        return pool[index]
    
    @staticmethod
    def REVERSE_WALK(pool: Iterable[B], /) -> B:
        index = Random.RANDINT({0: len(pool)}, include_right=False)
        steps = Random.RANDINT([-2, 2])
        new_index = (index - steps) % len(pool)
        return pool[new_index]
    
    @staticmethod
    def CYCLIC(pool: Iterable[B], /) -> B:
        start = Random.RANDINT({0, len(pool)}, include_right=False)
        cycle_index = (start + Random.RANDINT([0, len(pool)-1])) % len(pool)
        return pool[cycle_index]
    
    @staticmethod
    def FREQUENCY(pool: Iterable[B], /) -> B:
        from collections import Counter
        freq_counter = Counter(pool)
        elements, frequencies = zip(*freq_counter.items())
        total_frequency = sum(frequencies)
        random_value = Random.RANDINT([0, total_frequency-1])
        cumulative = 0

        for element, freq in zip(elements, frequencies):
            cumulative += freq
            if random_value < cumulative:
                return element
    
    @staticmethod
    def BINARY_SPLIT(pool: Iterable[B], /) -> B:
        mid = len(pool) // 2
        if Random.RANDINT([0, 1]) == 0:
            return Random.DEFAULT(pool[:mid])
        else:
            return Random.DEFAULT(pool[mid:])
    
    @staticmethod
    def HASHED(pool: Iterable[B], /) -> B:
        import hashlib
        obj = hashlib.sha256(str(Random.SEED()).encode())
        obj_int = int(obj.hexdigest(), 16)
        return pool[obj_int % len(pool)]
    
    @staticmethod
    def ROTATED(pool: Iterable[B], /) -> B:
        steps = Random.RANDINT([0, len(pool) - 1])
        rotated = pool[steps:] + pool[:steps]
        return rotated[0]
    
    @staticmethod
    def SUM(pool: Iterable[B], /) -> B:
        if not all(isinstance(item, (str, int, List, Tuple, Dict)) for item in pool):
            raise ValueError("All elements must have measurable length for `Random.SUM` Algorithm.")
        
        cumulative_sum = 0
        cumulative_values = []

        for value in pool:
            cumulative_sum += len(value)
            cumulative_values.append(cumulative_sum)
        
        random_sum = Random.RANDINT([0, cumulative_sum - 1])

        for i, cum in enumerate(cumulative_values):
            if random_sum < cum:
                return pool[i]

    def __init__(
            self,
            pool: Iterable[R],
            algorithm: C,
            condition: Union[Callable[[R], bool], None] = None,
    ) -> None:
        self._pool = pool
        self._algorithm = algorithm
        self._condition = condition

        self._initial = self.__random__()
    
    def __random__(self) -> R:
        if self._algorithm != Random.REJECTION_SAMPLING:
            return self._algorithm(self._pool)
        elif self._algorithm == Random.REJECTION_SAMPLING and self._condition is None:
            raise TypeError("'Random.REJECTION_SAMPLING' is a TYPE2 ALGORITHM. Select a condition for the 'condition' parameter of '__init__'.")
        elif self._algorithm == Random.REJECTION_SAMPLING and self._condition is not None:
            return self._algorithm(self._pool, condition=self._condition)
    
    redo = Property(
        getter=lambda cls: cls.__random__(),
        setter=None,
        deleter=None,
        error=AttributeError,
        setter_error_arguments=("Cannot set 'redo' property.",),
        deleter_error_arguments=("Cannot delete 'redo' property.",)
    )

    def __call__(self) -> R:
        return self._initial
    
    def __int__(self) -> int:
        if isinstance(self._initial, int):
            return self._initial
        else:
            try:
                return int(self._initial)
            except Exception:
                raise TypeError(f"Random value is not int and cannot be converted to int: {self._initial}")
    
    def __float__(self) -> float:
        if isinstance(self._initial, (int, float)):
            return float(self._initial)
        else:
            raise TypeError(f"Random value chosen is not int or float: {self._initial}")
    
    def __get__(self, instance, owner) -> R:
        return self._initial
    
    def __set__(self, instance, value) -> None:
        raise AttributeError(f"Cannot set random value when 'Random' is used as a 'Descriptor'.")
    
    def __len__(self) -> int:
        if hasattr(self._initial, '__len__'):
            return len(self._initial)
        elif isinstance(self._initial, (float, int)):
            return len(str(self._initial))
        else:
            raise TypeError(f"Random value does not have __len__ attribute: {self._initial}")
    
    def __str__(self) -> str:
        return str(self._initial)
    
    def __repr__(self) -> str:
        return self.__str__()
    
