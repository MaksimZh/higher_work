def foo(a, b, c, d):
    odd_names = []
    even_names = []
    for name, value in zip(["A", "B", "C", "D"], [a, b, c, d]):
        (even_names if value % 2 == 0 else odd_names).append(name)
    return _answer_generators[len(odd_names)](odd_names, even_names)

_answer_generators = [
    lambda odd, even: 'Все числа четные',
    lambda odd, even: f'Все числа четные, кроме числа {odd[0]}',
    lambda odd, even: f'Числа {even[0]} и {even[1]} четные, а {odd[0]} и {odd[1]} нет',
    lambda odd, even: f'Все числа нечетные, кроме числа {even[0]}',
    lambda odd, even: 'Все числа нечетные',
]

assert(foo(2, 4, 6, 8) == 'Все числа четные')
assert(foo(3, 4, 6, 8) == 'Все числа четные, кроме числа A')
assert(foo(2, 5, 6, 8) == 'Все числа четные, кроме числа B')
assert(foo(2, 4, 7, 8) == 'Все числа четные, кроме числа C')
assert(foo(2, 4, 6, 9) == 'Все числа четные, кроме числа D')
assert(foo(3, 5, 6, 8) == 'Числа C и D четные, а A и B нет')
assert(foo(3, 4, 7, 8) == 'Числа B и D четные, а A и C нет')
assert(foo(3, 4, 6, 9) == 'Числа B и C четные, а A и D нет')
assert(foo(2, 5, 7, 8) == 'Числа A и D четные, а B и C нет')
assert(foo(2, 4, 7, 9) == 'Числа A и B четные, а C и D нет')
assert(foo(2, 5, 6, 9) == 'Числа A и C четные, а B и D нет')
assert(foo(2, 5, 7, 9) == 'Все числа нечетные, кроме числа A')
assert(foo(3, 4, 7, 9) == 'Все числа нечетные, кроме числа B')
assert(foo(3, 5, 6, 9) == 'Все числа нечетные, кроме числа C')
assert(foo(3, 5, 7, 8) == 'Все числа нечетные, кроме числа D')
assert(foo(3, 5, 7, 9) == 'Все числа нечетные')
