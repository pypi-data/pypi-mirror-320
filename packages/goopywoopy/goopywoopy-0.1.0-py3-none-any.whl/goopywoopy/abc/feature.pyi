"""Feature Module

This module contains abstract classes related to creating
features for a class.
"""

from abc import (
    ABC,
    abstractmethod,
)

class Feature(ABC):
    """ABC Base Class for defining a Feature.
    
    A Feature is a single unit that is added to a class for
    extending it's capabilities. Inherit this class to create
    a feature that can then be inherited by the main software
    class.

    Example:
    ```python
    class Feature_1(Feature):
    # inherit the Feature class to create a feature.

        def feature_1_function(self, number: int) -> int:
            return self.value * number
            # here, self.value does not exist in this feature class
            # however, it will be available in the software class.
    
    class software(Feature_1):
    # inherit the feature
        def __init__(self, value: int) -> int:
            self.value = value
    ```

    Now that we have defined a software and it's feature,

    ```python
    # let us call the feature.
    obj = software(10)
    obj.feature_1_function(10) # valid, returns 100
    ```

    Multiple features can be inherited by the software class.
    ```python
    # example
    class software(feat_1, feat_2, ...): ...
    ```
    """