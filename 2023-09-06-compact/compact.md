# 3.

## 3.1 Параметр, скрытый в другом параметре
```Python
class BandBasis(Basis):
    @property
    @abstractmethod
    def valence_band_size(self) -> int:
        assert False

class Kane8Basis(BandBasis):
    @property
    def size(self) -> int:
        return 8
    
    @property
    def valence_band_size(self) -> int:
        return 6

...

basis = Kane8Basis()
hamiltonian = BandHamiltonian.wrap(source, u_ket(basis), u_bra(u_ket))
```
Размер валентной зоны для `hamiltonian` передаётся внутри параметра `basis`
в виде свойства `BandBasis.valence_band_size`.

Во-первых, это создаёт дополнительную когнитивную нагрузку при чтении кода.

Во-вторых, в тензоре, хранящем решения уравнения после их отбора,
размер валентной зоны может быть произвольным (задаётся пользователем).
Тогда, информация, хранящаяся в `basis` будет ложной.

Просто передавать размер валнетной зоны через базис - плохая идея.
Для этого нужно использовать отдельный явный механизм:
```Python
class ValenceBandSize(DualTag)
    __value: int

    def __init__(self, value: int) -> None:
        self.__value = value

    @property
    def conj(self) -> "ValenceBandSize": # для автоматического копирования этих данных из u_ket в u_bra
        return self

...

hamiltonian = BandHamiltonian.wrap(source, u_ket(basis, ValenceBandSize(6)), u_bra(u_ket))
```


## 3.2 Передача информации с помощью динамической типизации
В общем случае это не плохо, но в предыдущем примере - не очень:
```Python
hamiltonian = BandHamiltonian.wrap(source, u_ket(basis, ValenceBandSize(6)), u_bra(u_ket))
```
Названия переменных имеют физический смысл, но вот эквивалентный пример
```Python
t = SomeTensorType.wrap(source, a(b, SomeSize(6)), c(a))
```
Как быстро понять, что `b` - базис, а не ось?
Как быть уверенными, что под `c(a)`
подразумевается именно `a`-строки и `c`-столбцы,
а не опечатка при передаче чего-то другого в качестве параметра к `c`? 

Лучше сделать передачу параметров (`a(b)`) более явной,
отделив её от связывания осей (`c(a)`):
```Python
t = SomeTensorType.wrap(source, a(basis=b, some_size=6), c(a))
```


## 3.3 Связывание осей не нужно
Связывание осей и разделение их на строки и столбцы на уровне логики
является более фундаментальным, чем просто передача параметров.
Например, этот механизм управляет копированием параметров
между связанными осями.

Лучше связать оси друг с другом независимо от тензоров, добавив к ним
операцию сопряжения:
```Python
t = SomeTensorType.wrap(source, a(basis=b, some_size=6), a.conj)
```

Дополнительно мы избавляемся от необходимости ряда проверок входных данных,
например, уже не получится привязать две оси к одной:
```Python
# нужна дополнительная проверка параметров
t = SomeTensorType.wrap(src, a, b(a), c(a))
```
```Python
# будет отловлено проверкой на повторяющиеся оси: a.conj == a.conj
t = SomeTensorType.wrap(src, a, a.conj, a.conj)
```
