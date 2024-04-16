# Добиваемся совместимости между (унаследованными) типами

# 1. Free object
> Тип A будет свободным объектом,
  если для любого возможного альтернативного типа B
  (который поддерживает подмножество операций из A),
  можно преобразовать значение типа A в точно такое же значение типа B,
  которое мы получили бы, если бы начали с **тех же входных данных**
  и выполнили **те же операции**.

Для простоты представим, что значение типа A
можно представить точкой на координатной оси a,
а операции перемещают эту точку.
Если в одно и то же состояние можно попасть разными путями,
такое перемещение необратимо,
т.е. невозможно восстановить траекторию по конечной точке,
особенно если мы потеряли данные об операциях.

Хорошо, путь данные об операциях лежат на оси x,
и мы их не потеряли.
Даже в этом случае некоторые шаги могут происходить с потерей данных a.
Простой пример - остаток от деления.
Даже если мы знаем и делитель, и остаток - делимое неоднозначно.
То есть, нужно хранить координаты всех промежуточных точек (a, x).
Входные данные тут будут иметь вид (a0, Ox),
где Ox означает отсутствие операции,
или (Oa, x0), где Oa - "чистое" исходное состояние,
а x0 - входные данные.

Теперь пусть значения типа B лежат на оси b.
Тогда у нас будет две траектории: [..., (a, x), ...] и [..., (b, x), ...].
Даже если какая-то из них будет иметь самопересечения,
между каждой парой точек (a, x) и (b, x) можно установить
взаимно-однозначное соответствие,
поскольку помимо координат у них есть ещё и порядковые номера:
(n, a, x), (n, b, x).

Пусть какая-то операция (номер 5) для A идёт с потерей данных, а для B - нет:
```
a[4] != a'[4]   b[4] != b'[4]
a[5] == a'[5]   b[5] != b'[5]
```
Как зная только a[5] найти b[5] и b'[5]?
Никак.
Если же мы знаем a[4] и a'[4],
в точке до того, как две траектории в пространстве A схлопнулись,
то можем построить две разные траектории в пространстве B.