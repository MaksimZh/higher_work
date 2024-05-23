# Как правильно готовить юнит-тесты

## 1. Выводы по теории
Нужно тестировать не случайное поведение, а желаемые свойства.
Сложность в том, что один сценарий поведения
может затрагивать несколько свойств,
и выделение этих свойств - это математическая задача.
Она похожа на вычисление проекций вектора на оси координат.
Сначала, конечно, нужно определиться с системой координат,
а потом уже искать проекции.
В случае с векторами - процедура известная,
но для свойств системы - это настоящее искусство.

Не удивлюсь, если есть математики,
которые стремятся это искусство формализовать,
и уже достигли в этом направлении каких-то успехов.
К сожалению, похоже, что применительно к программированию
эти знания пока не очень распространены.


## 2. Новые юниттесты

### 2.1.
```Python
class Test_RawParams(unittest.TestCase):
    ...

    def merge(self):
        o = dict[str, Set[Any]]()
        x = {"x": {1, 2}}
        y = {"y": {1, 2}}
        z = {"z": {5, 6}}

        for raw, ready, src in [
                (o, o, o),
                (o, o, x),
                (x, o, o),
                (x, o, y),
                (o, x, o),
                (o, x, y),
                (x, y, o),
                (x, y, z),
                ]:
            params = RawParams(Params(raw), Params(ready))
            self.assertEqual(
                params.merge(src),
                RawParams(Params(raw), Params(ready).merge(src)))
            self.assertEqual(
                params.merge(Params(src)),
                params.merge(src))
    
    ...
```
Желаемое поведение вынесено в тело цикла.
который перебирает разные комбинации входных данных.
Сразу понятно чего мы хотим:
  - `merge` добавляет новые данные только к `ready`;
  - аргумент, обёрнутый в `Params` ведёт себя так же как простой словарь.


### 2.2.
```Python
class Test_RawParams(unittest.TestCase):
    ...

    def test_find_extract_prepare(self):
        o = dict[str, Set[Any]]()
        a = {"a": {1, 2, "x", "y"}, "b": {3, 4}, "c": {"u", "v"}}
        b = {"a": {5, 6, "i", "j"}, "b": {7, 8}, "c": {"k", "l"}}
        is_one: Callable[[Any], bool] = lambda x: x == 1
        is_int: Callable[[Any], bool] = lambda x: isinstance(x, int)
        for raw_dict, ready_dict, pred in [
                (o, o, is_one),
                (o, o, is_int),
                (a, o, is_one),
                (a, o, is_int),
                (o, a, is_one),
                (o, a, is_int),
                (a, b, is_one),
                (a, b, is_int),
                ]:
            raw = Params(raw_dict)
            ready = Params(ready_dict)
            raw_rest, raw_pred = raw.extract(pred)
            ready_rest, ready_pred = ready.extract(pred)
            all_pred = merge_set_mappings(raw_pred, ready_pred)
            params = RawParams(raw, ready)
            
            self.assertEqual(
                params.find(pred),
                all_pred)
            self.assertEqual(
                params.extract(pred),
                (RawParams(raw_rest, ready_rest), all_pred))
            self.assertEqual(
                params.prepare(pred),
                RawParams(raw_rest, ready.merge(raw_pred)))
  
    ...
```
Все три функции работают с предикатами схожими способами.
Поэтому я поместил их в один тест.
Здесь снова цикл по наборам данных и предикатам.


### 2.3.
```Python
class Test_SymmetricMatrixTensor(unittest.TestCase):

    def test_success(self):
        a = Axis("a")
        b = Axis("b")
        c = Axis("c")
        d = Axis("d")
        e = Axis("e")
        f = Axis("f")
        
        self.assertIsNotNone(
            SymmetricMatrixTensor(np.zeros((2, 2, 3, 4)), a(COL), b(ROW), c, d))
        self.assertIsNotNone(
            SymmetricMatrixTensor(
                np.zeros((2, 3, 2, 3, 4, 5)),
                a(COL), b(COL), c(ROW-a), d(ROW-b), e, f))
    
    ...
```
Объединённый тест для тензоров ранга 4 и 6.
Здесь тестируется общее свойство -
успешное создание массива симметричных матриц с правильной размерностью осей.


### 2.4.
```Python
class Test_SymmetricMatrixTensor(unittest.TestCase):
    ...

    def test_fail(self):
        a = Axis("a")
        b = Axis("b")
        c = Axis("c")
        d = Axis("d")
        e = Axis("e")
        f = Axis("f")
        
        self.assertRaises(
            AssertionError, lambda:
            SymmetricMatrixTensor(np.zeros((2, 3)), a(COL), b(ROW)))
        self.assertRaises(
            AssertionError, lambda:
            SymmetricMatrixTensor(
                np.zeros((2, 3, 3, 2, 4, 5)),
                a(COL), b(COL), c(ROW-a), d(ROW-b), e, f))
```
Объединённый тест для тензоров ранга 4 и 6.
Здесь тестируется общее свойство -
ошибка при попытке создать симметричную матрицу
из массива с несимметричными размерами осей.


### 2.5.
```Python
class Test_AxisKind(unittest.TestCase):

    def test_instantiating(self):
        self.assertRaises(TypeError, lambda: A())
        self.assertIsNotNone(AA())
        self.assertRaises(TypeError, lambda: AB())
        self.assertIsNotNone(ABA())
        self.assertIsNotNone(ABB())
        self.assertRaises(TypeError, lambda: B())
        self.assertIsNotNone(BA())
        self.assertIsNotNone(BB())

    def test_cluster(self):
        self.assertIsNone(AA().cluster)
        self.assertEqual(AA(1).cluster, 1)
        self.assertEqual(AA("one").cluster, "one")
```
Отдельно тестируем, что для некоторых типов можно создавать экземпляры,
а для других (абстрактных) - нет.

Отдельно тестируем свойство -
хранение кластера, заданного при вызове конструктора.


### Выводы
Тесты с циклами кажутся сложными,
но это только на первый взгляд.
Для анализа кода куда сложнее туча вызовов с конкретными параметрами,
для которых непонятно какое поведение вообще ожидается.

Местами тело такого цикла очень похоже на код тестируемой функции.
Если тест пишется до функции по TDD - это хорошо.
Это значит, код функции вытекает из ожидаемой логики работы приложения.


## Общие выводы
Это можно было бы назвать "Property Driven Development",
а если свойства описаны достаточно формально, то "Math Driven Development".
Если эту тему развивать, то можно добраться до автоматической генерации кода
по набору свойств.
Тогда описание свойств может оказаться настолько сложным,
что баги будут уже в нём.

Давным-давно я участвовал в проекте, где было ядро, написанное на C++,
к которому предоставлялся интерфейс на Tcl,
чтобы можно было писать скрипты на "более удобном" языке.
За 10 лет развития проекта (к моменту моего прихода туда)
эти скрипты стали настолько сложными, что нужно было уже их отлаживать,
и отсутствие статической типизации в "более удобном" языке
создавало дополнительные проблемы.

Вот интересно, наверняка в математике уже есть направление,
в котором логические утверждения параметризуются и комбинируются
как функции в функциональном программировании.
Тогда можно разрабатывать формальные описания программ
аналогично разработке самих программ:
с помощью абстракций которые ограничивают рост сложности.
В Python такое вряд ли получится, а в Haskell - весьма вероятно.
