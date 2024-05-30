# Делаем тесты хорошими

## 1. Выводы по теории
"Разделяй и властвуй" (с)

Свойства программы, которые являются независимыми на уровне логики,
должны независимо тестироваться на уровне кода тестов.
Свойство A не зависит от свойства B,
когда возможна реализация, при которой A есть, а B - нет.

Как это ни странно, даже если B явно используется в коде,
сам сценарий его использования может быть тем самым A,
которое не зависит от B, только от его интерфейса.
Простой пример - функция поиска `find(predicate, collection)`,
у которой сам алгоритм не зависит ни от конкретного `predicate`,
ни от конкретной `collection`.
Какие у неё есть свои собственные свойства?
Как на счёт такого:
```Python
assert predicate(find(predicate, collection))
```
Это если нам нужен один любой элемент, удовлетворяющий условию.
А если первый элемент?
```Python
e = find(predicate, collection)
# Условие выполняется для выбранного элемента
assert predicate(e)
# Условие не выполняется для предыдущих элементов
assert all(not predicate(e1) for e1 in collection[:e])
```
А если нам нужны все элементы?
```Python
found = find(predicate, collection)
# Условие выполняется для найденных элементов
assert all(predicate(e) for e in found)
# Условие не выполняется для остальных элементов
assert all(not predicate(e) for e in collection if e not in found)
```
И это всё для любого `predicate` и любой `collection`
с заданными (лучше - на уровне типов) интерфейсами.

Что плохого тестировать именно с теми аргументами, которые нам нужны?
Пусть `collection` - огромная выборка из БД.
А ещё нам не свезло, и `predicate` не реально включить в SQL запрос,
(иначе нам `find` бы и не понадобился).
Каждый тест будет выполняться, например, пару секунд, что неприемлемо,
если подобных тестов сотни.
Поэтому не надо тестировать `find` в связке с таким кодом,
даже если в программе он используется именно так и только так.
На помощь идут моки - простые версии `predicate` и `collection`,
для которых тест идёт считанные микросекунды
(ну ладно, в Python - миллисекунды) даже со всеми обвесами
в виде `assert all(...)`.


## 2. Работа с кодом

### 2.1. Царь-формула
```Python
def test(self):
    ...
    # 200 строк формул
    ...
    h = calc_kane8_band_hamiltonian(params)
    self.assertIs(h.bases[k_left], k_basis_1xyz)
    self.assertIs(h.bases[k_right], k_basis_1xyz)
    h_array = h.unwrap(*h.band_axes, k_left, k_right)
    np.testing.assert_allclose(h_array, test_array)
```
Этот тест в >200 строк является просто старым способом
вычисления гамильтониана Кейна,
и шанс посадить ошибку в тесте куда выше, чем тестируемом коде.

Почему же так всё сложно?
Потому, что гамильтониан строится на основе большого объёма данных,
но этот факт скрывается за большим объёмом формул.
Сам код организован так, что сделать "правильный" тест не получится,
и приходится тестировать данные в жёсткой сцепке с алгоритмом их обработки.

В новой версии будет новый алгоритм,
который может строить гамильтониан из любых данных.
Тестировать его нужно будет один раз,
а данные проверять вручную при занесении их в компьютер из таблиц.

По правилам TDD тест можно написать уже сейчас:
```Python
def test(self):
    tensors = {
        "a": Tensor(...),
        "b": Tensor(...),
    }
    np.testing.assert_allclose(
        calc_hamiltonian(tensors, {"a": 2, "b": 3}),
        tensors["a"] * 2 + tensors["b"] * 3)
    np.testing.assert_allclose(
        calc_hamiltonian(tensors, {"a": 2}),
        tensors["a"] * 2)
    np.testing.assert_allclose(
        calc_hamiltonian(tensors, {"a": 2, "с": 3}),
        tensors["a"] * 2)
```


### 2.2. И швец и жнец
```Python
def test(self):

    class A(Sliceable, Parameterizeable):
        pass

    a = A()

    self.assertEqual(extract_params(a), (a, Params[A]({})))
    self.assertEqual(extract_params(a(1)), (a, Params({a: {1}})))
    self.assertEqual(extract_params(a[1]), (a, Params({a: {SizeTag(1)}})))
    self.assertEqual(
        extract_params(a[1](2)),
        (a, Params({a: {SizeTag(1), 2}})))
```
Переменная `a` умеет и в квадратные и в круглые скобки, но зачем?
Функция `extract_params` работает с результатом применения скобок.
Можно просто передавать этот результат и не издеваться над перменной `a`,
она может быть, например, строкой.
```Python
def test(self):
    self.assertEqual(
        extract_params("a"),
        ("a", Params[str]({})))
    self.assertEqual(
        extract_params(Parameterized("a", {1})),
        ("a", Params({"a": {1}})))
    self.assertEqual(
        extract_params(Sliced("a", 1)),
        ("a", Params({"a": {SizeTag(1)}})))
    self.assertEqual(
        extract_params(Parameterized(Sliced("a", 1), {2})),
        ("a", Params({"a": {SizeTag(1), 2}})))
```


### 2.3. Великий ~~Комбинатор~~ `Combinable`
```Python
def test_apply(self):
    class A(Combinable):
        pass
    a = A()
    b = A()
    x = A()
    y = A()
    z = A()
    p = Params({x: {1, 2}, y: {3, 4}, z: {5, 6}})

    self.assertEqual(p.apply(a), (a,))
    self.assertEqual(p.apply(x), (Parameterized(x, {1, 2}),))
    self.assertEqual(p.apply(+x), (+Parameterized(x, {1, 2}),))
    self.assertEqual(p.apply(~x), (~Parameterized(x, {1, 2}),))
    self.assertEqual(p.apply(-x), (-x,))
    self.assertEqual(p.apply(a * x), (a * Parameterized(x, {1, 2}),))
    self.assertEqual(
        p.apply(x * y),
        (Parameterized(x, {1, 2}) * Parameterized(y, {3, 4}),))
    self.assertEqual(p.apply(a >> b), (a >> b,))
    self.assertEqual(p.apply(x >> a), (x >> a,))
    self.assertEqual(p.apply(a >> x), (a >> Parameterized(x, {1, 2}),))
    self.assertEqual(p.apply(x >> y), (x >> Parameterized(y, {3, 4}),))
    self.assertEqual(
        p.apply(a * x >> y * z),
        (a * x >> Parameterized(y, {3, 4}) * Parameterized(z, {5, 6}),))
    self.assertEqual(
        p.apply(
            a,
            x,
            +y,
            -z,
            x * y,
            a * x >> y * z,
        ), (
            a,
            Parameterized(x, {1, 2}),
            +Parameterized(y, {3, 4}),
            -z,
            Parameterized(x, {1, 2}) * Parameterized(y, {3, 4}),
            a * x >> Parameterized(y, {3, 4}) * Parameterized(z, {5, 6}),
        ))
```
Аналогично 2.2. мы притащили целых 4 интерфейса:
```Python
class Combinable(
        Addable,
        Droppable,
        Mergeable,
        RepackSource):
    pass
```
Но по спецификации нам здесь вообще не нужна перегрузка операторов,
и будет ошибкой, если внутри `apply` она где-то используется.
Да, тест станет более громоздким, но он будет более чистым.

Хотя... Зачем громоздким?
Нам не нужно тестировать все эти `+`, `~` и `>>`,
потому что они уже протестированы для замечательной функции `dest_map`:
```Python
def test_apply(self):
    p = Params({10: {1, 2}, 20: {3, 4}, 30: {5, 6}})

    self.assertEqual(p.apply(11), (11,))
    self.assertEqual(p.apply(10), (Parameterized(10, {1, 2}),))
    
    patterns = (
        11,
        10,
        Added(20),
        Dropped(30),
        Merged(10, 20),
        Repack(Merged(11, 10), Merged(20, 30)))
    self.assertEqual(
        p.apply(*patterns),
        dest_map(lambda x: p.apply(x)[0], patterns))
```
Здесь мы сначала проверяем, что `apply` правильно работает для ключей,
которые есть в параметрах, и которых там нет.
Затем мы проверяем, что эта операция правильно "пробрасывается"
внутрь всяких `Added` и `Repack`.

От использования строк в качестве ключей пришлось отказаться,
потому что в Python они считаются
последовательностями строк из одного символа.
А каждая строка из одного символа -
это последовательность из одной строки из одного символа.
Функция `apply` раскрывает все последовательности
и попадает в бесконечную рекурсию.


### 2.4. Идём в глубину
В 2.3. упоминается функция `dest_map`, так вот её юниттест:
```Python
def test(self):
    @dataclass
    class X(Combinable):
        s: str

    @dataclass
    class Y(Combinable):
        s: str
    
    def func(x: X) -> Y:
        return Y(x.s)
    
    self.assertEqual(dest_map(func, (X("a"),)), (Y("a"),))
    self.assertEqual(dest_map(func, (+X("a"),)), (+Y("a"),))
    self.assertEqual(dest_map(func, (~X("a"),)), (~Y("a"),))
    self.assertEqual(dest_map(func, (-X("a"),)), (-X("a"),))
    self.assertEqual(
        dest_map(func, (X("a") * X("b"),)),
        (Y("a") * Y("b"),))
    self.assertEqual(
        dest_map(func, (X("a") >> X("b"),)),
        (X("a") >> Y("b"),))
    self.assertEqual(
        dest_map(func, (X("a") * X("b") >> X("c") * X("d"),)),
        (X("a") * X("b") >> Y("c") * Y("d"),))
```
Снова `Combinable`, даже два,
а ещё все тесты только для одноэлементных последовательностей.
```Python
def test(self):
    self.assertEqual(
        dest_map(str, (1,)),
        ("1",))
    self.assertEqual(
        dest_map(str, (Added(1),)),
        (Added("1"),))
    self.assertEqual(
        dest_map(str, (Ensured(1),)),
        (Ensured("1"),))
    self.assertEqual(
        dest_map(str, (Dropped(1),)),
        (Dropped(1),))
    self.assertEqual(
        dest_map(str, (Merged(1, 2),)),
        (Merged("1", "2"),))
    self.assertEqual(
        dest_map(str, (Repack(1, 2),)),
        (Repack(1, "2"),))
    self.assertEqual(
        dest_map(str, (Repack(Merged(1, 2), Merged(3, 4)),)),
        (Repack(Merged(1, 2), Merged("3", "4")),))
    self.assertEqual(
        dest_map(str, (
            1, 2, Added(3), Ensured(4), Dropped(5),
            Merged(6, 7), Repack(8, 9),
            Repack(Merged(1, 2), Merged(3, 4)))),
        (
            "1", "2", Added("3"), Ensured("4"), Dropped(5),
            Merged("6", "7"), Repack(8, "9"),
            Repack(Merged(1, 2), Merged("3", "4"))))
```
В чём сила новых тестов - минимум подготовительного кода.
Сразу к делу.


### 2.5. Родной брат
Функция `dest_map_reduce` - моя любимая в коде тензоров.
Только она может собрать все параметры с комбинированных осей,
не нарушив ни одной комбинации.
```Python
def test(self):
    @dataclass
    class X(Combinable):
        s: str

    @dataclass
    class Y(Combinable):
        s: str
    
    def func(x: X, s: str) -> tuple[Y, str]:
        return Y(x.s), s + x.s
    
    self.assertEqual(
        dest_map_reduce(func, (X("a"),), "!"),
        ((Y("a"),), "!a"))
    self.assertEqual(
        dest_map_reduce(func, (+X("a"),), "!"),
        ((+Y("a"),), "!a"))
    self.assertEqual(
        dest_map_reduce(func, (~X("a"),), "!"),
        ((~Y("a"),), "!a"))
    self.assertEqual(
        dest_map_reduce(func, (-X("a"),), "!"),
        ((-X("a"),), "!"))
    self.assertEqual(
        dest_map_reduce(func, (X("a") * X("b"),), "!"),
        ((Y("a") * Y("b"),), "!ab"))
    self.assertEqual(
        dest_map_reduce(func, (X("a") >> X("b"),), "!"),
        ((X("a") >> Y("b"),), "!b"))
    self.assertEqual(
        dest_map_reduce(func, (X("a") * X("b") >> X("c") * X("d"),), "!"),
        ((X("a") * X("b") >> Y("c") * Y("d"),), "!cd"))
```
И снова нам нужны именно комбинации, а не комбинаторы.
```Python
def test(self):
    def func(x: int, s: str) -> tuple[str, str]:
        y = str(x)
        return y, s + y
    
    self.assertEqual(
        dest_map_reduce(func, (1,), "!"),
        (("1",), "!1"))
    self.assertEqual(
        dest_map_reduce(func, (Added(1),), "!"),
        ((Added("1"),), "!1"))
    self.assertEqual(
        dest_map_reduce(func, (Ensured(1),), "!"),
        ((Ensured("1"),), "!1"))
    self.assertEqual(
        dest_map_reduce(func, (Dropped(1),), "!"),
        ((Dropped(1),), "!"))
    self.assertEqual(
        dest_map_reduce(func, (Merged(1, 2),), "!"),
        ((Merged("1", "2"),), "!12"))
    self.assertEqual(
        dest_map_reduce(func, (Repack(1, 2),), "!"),
        ((Repack(1, "2"),), "!2"))
    self.assertEqual(
        dest_map_reduce(func, (Repack(Merged(1, 2), Merged(3, 4)),), "!"),
        ((Repack(Merged(1, 2), Merged("3", "4")),), "!34"))
```

### Выводы
Основная проблема с этими тестами - недостаточная абстракция.
Тестируется одно конкретное свойство,
но подопытные типы тянутся из сценариев, где используется
несколько свойств.
Более того, тесты начинают зависеть от побочных свойств,
что ухудшает сопровождение кода.

Что касается царь-формулы (2.1.),
то меня такие тесты всегда раздражали.
Потому что в код переписываются два разных учебника,
и шансы посадить ошибку возрастают вдвое.
Теперь я зная что с этим делать - сводить сложные формулы
к простым алгоритмам обработки не очень сложных данных.
Тестировать только алгоритмы, а данные - проверять глазами,
и ещё какие-то контрольные суммы для них посчитать.


## 3. Абстрактные эффекты

### 3.1. Царь-формула
Тест проверяет, что функция построения гамильтониана:
  -  складывает тензоры с заданными коэффициентами;
  -  игнорирует тензоры, для которых нет коэффициентов;
  -  игнорирует коэффициенты, для которых нет тензоров.

Под каждый пункт есть отдельная проверка в тесте,
то есть, эти свойства явно выражены в коде.


### 3.2. И швец и жнец
### 3.3. Великий `Combinable`
### 3.4. Идём в глубину
### 3.5. Родной брат
