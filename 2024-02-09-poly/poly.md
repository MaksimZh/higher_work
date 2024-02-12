# Повышаем полиморфность кода

## 1. Выводы по изучению материла


## 2. Работа с кодом

## 2.1
```Python
def assume_single[T](source: set[T] | frozenset[T]) -> T:
    assert len(source) == 1
    return next(iter(source))
```
```Python
def single_value[T](source: Iterable[T]) -> T:
    match tuple(source):
        case (val,):
            return val
        case _:
            assert False
```


# 2.2
```Python
def all_single_values(source: dict[Any, set[Any]]) -> bool:
    return all(len(v) == 1 for v in source.values())
```
```Python
def all_single_values(source: Mapping[Any, Sized]) -> bool:
    return all(len(v) == 1 for v in source.values())
```


# 2.3
```Python
def assume_single_values[K, V](source: dict[K, set[V]]) -> dict[K, V]:
    return {k: assume_single(v) for k, v in source.items()}
```
```Python
def assume_single_values[K, V](source: Mapping[K, Iterable[V]]) -> dict[K, V]:
    return {k: single_value(v) for k, v in source.items()}
```
