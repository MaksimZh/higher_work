# Что такое абстракция - 2

# 1. Теория
Если абстракция - это **отображение** реального мира в математический,
то можно применить к ней математическую абстракцию для отображений,
например, функции.
Это будет метаабстракция.

Компьютер умеет работать только с целыми числами в линейной памяти.
И это нам с виртуальной памятью ещё повезло:
этой абстракцией процессор занимается сам.
А то в старых учебниках по ассемблеру про страницы памяти такое пишут...
Процессор ещё и числами с плавающей точкой (иногда - запятой) занимается,
а внутри, каждое из них состоит из двух целых чисел: мантиссы и экспоненты.
Что делать, если захотелось чего-то посложнее?

Есть в вычислительной математике такая штука - **параметризация**.
Это отображение некоторого подмножества (или подтипа) в числовые кортежи.
Оно взаимно-однозначное и работает в обе стороны.
Программа получает на вход набор чисел, который интерпретируется
как параметризация некоторых абстрактных сущностей.
Программа работает с ними и выдаёт ответ, а точнее -
его параметризацию в виде набора чисел.

Это происходит не только на уровне логики.
При использовании достаточно развитых языков программирования
и специализированных библиотек,
можно писать код на достаточно высоком уровне абстракции.
Например, можно перемножать матрицы в одну строчку,
и это будут именно матрицы на уровне системы типов,
а не двумерные массивы, про которые мы думаем, что они матрицы.


# 2. Практика