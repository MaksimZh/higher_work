# Думаем на уровне дизайна

Метод TDD я использую уже пару лет, а вот о дизайне до курса по ООП практически не думал. 

До изучения (повторного) материалов про три уровня рассуждений о программной системе
я склонен был писать тесты, которые тестируют не интерфейс компонента,
а его внутреннее состояние.
То есть, с помощью интерфейса я проверял, находится ли компонент в нужном состоянии.

В курсе по ООП это проявляется особенно ярко.
У объектов есть команды, запросы и статусы, и в моих тестах в начале курса
они всегда смешивались.
Например, сначала я тестировал пустую очередь, вызывая подряд
все команды и запросы, включая запросы статусов.
Потом делал то же самое для очереди из одного элемента и т.д:
```Python
def test_empty(self):
    q = Queue()
    self.assertEqual(q.get_get_front_status(), self.Queue.GetFrontStatus.NIL)
    self.assertEqual(q.get_pop_front_status(), self.Queue.PopFrontStatus.NIL)
    self.assertEqual(q.get_size(), 0)
    q.get_front()
    self.assertEqual(q.get_get_front_status(), self.Queue.GetFrontStatus.EMPTY)
    q.pop_front()
    self.assertEqual(q.get_pop_front_status(), self.Queue.PopFrontStatus.EMPTY)

def test_one(self):
    q = self.Queue()
    q.put_tail(1)
    self.assertEqual(q.get_size(), len(values))
    self.assertEqual(q.get_front(), values[0])
    self.assertEqual(q.get_get_front_status(), self.Queue.GetFrontStatus.OK)
    q.pop_front()
    self.assertEqual(q.get_pop_front_status(), self.Queue.PopFrontStatus.OK)
```

Теперь я рассматриваю элементы интерфейса отдельно:
```Python
def test_put(self):
    a = NativeDictionary()
    self.check(a, dict())
    a.put("a", 0)
    self.check(a, {"a": 0})
    a.put("a", 1)
    self.check(a, {"a": 1})
    a.put("b", 2)
    self.check(a, {"a": 1, "b": 2})

def test_get(self):
    a = NativeDictionary()
    self.assertEqual(a.get_get_status(), NativeDictionary.GetStatus.NIL)
    a.put("a", 1)
    a.put("b", 2)
    a.put("c", 3)
    self.assertEqual(a.get("b"), 2)
    self.assertEqual(a.get_get_status(), NativeDictionary.GetStatus.OK)
    a.get("foo")
    self.assertEqual(a.get_get_status(), NativeDictionary.GetStatus.NOT_FOUND)

def test_delete(self):
    a = NativeDictionary()
    self.assertEqual(a.get_delete_status(), NativeDictionary.DeleteStatus.NIL)
    a.put("a", 1)
    a.put("b", 2)
    a.put("c", 3)
    self.check(a, {"a": 1, "b": 2, "c": 3})
    a.delete("b")
    self.assertEqual(a.get_delete_status(), NativeDictionary.DeleteStatus.OK)
    self.check(a, {"a": 1, "c": 3})
    a.delete("foo")
    self.assertEqual(a.get_delete_status(), NativeDictionary.DeleteStatus.NOT_FOUND)
    a.delete("b")
    self.assertEqual(a.get_delete_status(), NativeDictionary.DeleteStatus.NOT_FOUND)
```

Ещё одна особенность - ускорение разработки за счёт того,
что большая часть теста пишется сразу целиком на основе дизайна,
а не пока код его не провалит (как это рекомендуется в классическом TDD).

Например, раньше я сначала добавлял проверку статуса команды на `NIL`
и добавлял запрос статуса, который всегда возвращает `NIL`.
Потом добавлял следующую проверку и **переделывал** запрос, чтобы он возвращал
значение поля.
Таких этапов могло быть несколько и постоянно нужно было переключаться
между кодом и тестами даже внутри одного метода или функции.
Из-за этого у меня в голове логика работы этой функции часто "разваливалась".

Теперь алгоритм выглядит так:
1. выделить в дизайне программы какой-то элемент, который не зависит
от ещё не реализованных элементов (дизайна!);
2. написать тест для этого элемента на основе дизайна;
3. написать код для реализации этого элемента дизайна, а не чтобы тест прошёл
(но так, чтобы тест всё же прошёл :));
4. провести ревизию тестов (например, учёт граничных случаев, но на основе дизайна, а не кода)
и дополнить их;
5. перейти к другим элементам дизайна.

При этом на этапе 3. могут и ошибки в тестах выявиться.

Тесты для проверки кода "на прочность" откладываются до этапа тестирования.
