# Абстрагируем управляющие паттерны

## Запуск солвера
```Python
solver.put("arg1", arg1)
solver.put("arg2", arg2)
solver.run()
assert solver.is_status("run", "OK")
result1 = solver.get("result1")
result2 = solver.get("result2")
```
Интерфейс солвера спроектирован в рамках объектно-ориентированной
вычислительной модели, но при создании сложных солверов на основе более простых
используется декларативная модель.
Из-за этого возникают сложности при использовании солверов - нужно запускать их
вручную и проверять результат, причём в случае ошибки нет информации от том,
что именно пошло не так.

Решение - сделать солверы ближе к декларативной модели, уменьшив количество
явных состояний, и выбрасывать исключение в случае ошибки.
```Python
solver.put("arg1", arg1)
solver.put("arg2", arg2)
result1 = solver.get("result1")
result2 = solver.get("result2")
```
При попытке прочитать результат будут выполнены вычисления (ленивый подход).
Если для них не хватает данных, или что-то пошло не так - выбрасывается
исключение.

Раньше по умолчанию ошибки игнорировались.
Было легко забыть `assert`.
Теперь по умолчанию при ошибке программа падает.
Это желаемое поведение, т.к. точность вычислений здесь важнее устойчивости системы.

При возникновении исключения в нём сохраняется информация о проблемном солвере.
Благодаря этому мы можем прочитать входные данные и понять где ошибка.


## Обратная связь
```Python
class MySolver(Solver):
    ...
    
    def run(self) -> None:
        ...
        print("Begin")
        ...
        #print(f"energy = {energy}")
        ...
        print("End")
        ...
...
for x in x_list:
    my_solver.put("x", x)
    print(f"x = {x}")
    y.append(my_solver.get("y"))
```
Обратная связь жёстко закодирована как вывод на экран и разбросана внутри
солвера и в управляющем коде.
Очень неудобно управлять уровнем детализации сообщений - приходится править
код в разных местах (есть ещё и нарушение принципа закрытости).

Решение - использовать шаблон "Наблюдатель", чтобы обрабатывать события
в не солвера.
```Python
class MySolver(Solver):
    ...

    def _make_event(self, name: str, *args: Any) -> None:
        self.__observer.put_event(name, *args)
    
    def run(self) -> None:
        ...
        self._make_event("begin")
        ...
        self._make_event("energy step", energy)
        ...
        self._make_event("end")
        ...

class MyObserver:
    def put_event(self, name: str, *args: Any) -> None:
        # вывод на экран или сохранение в логах - что захотим
        ...

...

my_solver.add_observer(my_observer)
for x in x_list:
    my_solver.put("x", x)
    y.append(my_solver.get("y"))
```


## Циклы
```Python
class A(Solver):
    ...

class B(Solver):
    
    def __init__(self) -> None:
        self.a = A()
    
    ...

    def run(self) -> None:
        ...
        for x in x_list:
            self.a.put("x", x)
            y.append(self.a.get("y"))
        ...
```
Циклы встречаются слишком часто.
В декларативной модели для обработки всех элементов коллекции лучше использовать
отдельный солвер, куда "тело цикла" передаётся в качестве параметра:
```Python
class A(Solver):
    ...

class Map(Solver):
    ...

class B(Solver):
    
    def __init__(self) -> None:
        self.m = Map()
        self.m.set("proc", A())
    
    ...

    def run(self) -> None:
        ...
        self.m.put("x", x_list)
        y = self.m.get("y")
        ...
```
