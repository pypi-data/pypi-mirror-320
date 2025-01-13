from goopywoopy.tools import Random

class A:
    x = Random([1, 2, 3, 'ab'], Random.BINARY_SPLIT)
    y = Random([1, 56, 23, 11, 22, 55, 44, 10, 12, 66], Random.REJECTION_SAMPLING, lambda x: x%2 == 0)

def test_class():
    assert isinstance(A().x, (int, str))
    assert isinstance(A().y, int)