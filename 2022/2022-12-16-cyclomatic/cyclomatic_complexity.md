# Функция со сложными математическими расчётами

## Исходная версия
Цикломатическая сложность: 11
```python
def _calcCoefs(mxL, lj, coefsNum, atol):
    mxSize = mxL[0].shape[0]
    factor = ArrayPoly([-lj, 1])
    dtype = np.common_type(mxL[0].coefs, factor.coefs)
    mxX, mxY, kappa = \
        _calcSmithN(mxL[0], num=coefsNum, factor=factor, atol=atol)
    alpha, beta = _calcAlphaBeta(kappa)
    mxXt = _calcXt(p=factor, x=mxX, kappa=kappa)
    mxLt = _calcLt(mxL=mxL, p=factor, beta=beta)
    kernelSize = sum(k > 0 for k in kappa[0])
    jordanChainsLen = kappa[0][-kernelSize:]
    del mxX, factor, kappa
    # TODO - move calculation of ct to separate function
    ct = []
    for k in range(kernelSize):
        ctk = np.zeros((coefsNum, alpha + jordanChainsLen[k], mxSize, 1),
            dtype=dtype)
        for n in range(coefsNum):
            nDeriv = beta[n] + jordanChainsLen[k]
            if n == 0:
                b = [_ort(mxSize, -1 - kernelSize + k + 1)]
            else:
                b = _calcB(mxY[n], mxLt[n], lj, ctk[:n, :nDeriv])
            ctk[n, :nDeriv] = _calcCt(mxXt[n], lj, b, nDeriv)
            del nDeriv, b
        ct.append(ctk)
        del ctk
    del mxY, mxXt, mxLt
    # TODO - move calculation of g to separate function
    g = []
    for k in range(kernelSize):
        gk = []
        for q in range(jordanChainsLen[k]):
            gkq = np.zeros((coefsNum, alpha + q + 1, mxSize, 1), dtype=complex)
            for n in range(coefsNum):
                num_ln_terms = beta[n] + q
                pow_deriv_coef = factorial(alpha + q) / factorial(num_ln_terms)
                for m in range(num_ln_terms + 1):
                    gkq[n, m] = pow_deriv_coef * ct[k][n, num_ln_terms - m]
                    pow_deriv_coef *= (num_ln_terms - m) / (m + 1)
                del num_ln_terms, pow_deriv_coef
            while gkq.shape[1] > 1 and np.max(np.abs(gkq[:, -1])) < atol:
                gkq = gkq[:, :-1]
            gk.append(gkq)
            del gkq
        g.append(gk)
        del gk
    return g
```

## Списки вместо массивов
Вычисление величин `ct` и `g` (помечены TODO-комментариями) связано через большое количество избыточных параметров.
Это вызвано тем, что в функции активно используются многомерные массивы,
и дополнительные параметры нужны, чтобы знать какую часть массива использовать, а какую нет.

Переход к вложенным спискам позволил избавиться от лишних элементов и необходимости хранить дополнительную информацию.

## Вынос логики в отдельные функции
Теперь можно вынести два этапа вычислений в отдельные функции,
сделав функцию верхнего уровня почти тривиальной.

## Новая версия
Цикломатическая сложность: 2
```python
def _calcCoefs(mxL, lj, atol):
    ct = _calcAllCt(mxL, lj, atol)
    return [_calcG(ctk, atol) for ctk in ct]
```


# Функция со сложными математическими расчётами 2

## Исходная версия
Цикломатическая сложность: 7
```python
def _calcAllCt(mxL, lj, atol):
    coefsNum = len(mxL)
    mxSize = mxL[0].shape[0]
    factor = ArrayPoly([-lj, 1])
    mxX, mxY, kappa = \
        _calcSmithN(mxL[0], num=coefsNum, factor=factor, atol=atol)
    kernelSize = sum(k > 0 for k in kappa[0])
    jordanChainsLen = kappa[0][-kernelSize:]
    ct = []
    for k in range(kernelSize):
        ctk = []
        for n in range(coefsNum):
            if n == 0:
                beta = [0]
            else:
                beta.append(beta[-1] + kappa[n][-1])
            nDeriv = jordanChainsLen[k] + beta[-1]
            if n == 0:
                beta = [0]
                b = [_ort(mxSize, -1 - kernelSize + k + 1)]
                mxXt1 = mxX[0]
            else:
                mxZ = [trim(factor**(beta[n - 1] - beta[m]) * mxL[n - m](ArrayPoly([m, 1]))) \
                        for m in range(n)]
                b = _calcB(mxY[n], mxZ, lj, ctk, nDeriv)
                mxXt1 = _calcXt1(factor, mxX[n], kappa[n])
            ctk.append(_calcCt(mxXt1, lj, b, nDeriv))
            del b
            del nDeriv
        ct.append(ctk)
        del ctk
    return ct
```

## Сокращение количества условных операторов
Вместо проверки `n == 0` внутри двух вложенных циклов
поменяем порядок циклов и вынесем вычисления для первого шага
из цикла, а затем - в отдельную функцию.

## Рекурсия вместо цикла
Избавимся от цикла по `n`, заменив его рекурсивным вызовом.

## Вынос логики в отдельные функции
Обработка начального шага рекурсии и последующих шагов достаточно сложная,
поместим их в отдельные функции.

## Новая версия
Цикломатическая сложность: 2
```python
def _calcAllCt(mxL, lj, atol):
    if len(mxL) == 1:
        return _calcInitialCt(mxL[0], lj, atol)
    ct = _calcAllCt(mxL[:-1], lj, atol)
    return _calcNextCt(mxL, ct, lj, atol)
```


# Функция с сайта www.govnokod.ru

## Исходная версия
Цикломатическая сложность: 61
```python
def foo(a, b, c, d):
    if a % 2 == 0 and  b % 2 == 0 and c % 2 == 0 and d % 2 == 0:
        return 'Все числа четные'
    elif a % 2 != 0 and  b % 2 == 0 and c % 2 == 0 and d % 2 == 0:
        return 'Все числа четные, кроме числа А'
    elif a % 2 == 0 and  b % 2 != 0 and c % 2 == 0 and d % 2 == 0:
        return 'Все числа четные, кроме числа B'
    elif a % 2 == 0 and  b % 2 == 0 and c % 2 != 0 and d % 2 == 0:
        return 'Все числа четные, кроме числа C'
    elif a % 2 == 0 and  b % 2 == 0 and c % 2 == 0 and d % 2 != 0:
        return 'Все числа четные, кроме числа D'
    elif a % 2 != 0 and  b % 2 != 0 and c % 2 == 0 and d % 2 == 0:
        return 'Числа C и D четные, а А и B нет'
    elif a % 2 != 0 and  b % 2 == 0 and c % 2 != 0 and d % 2 == 0:
        return 'Числа B и D четные, а А и C нет'
    elif a % 2 != 0 and  b % 2 == 0 and c % 2 == 0 and d % 2 != 0:
        return 'Числа B и C четные, а А и D нет'
    elif a % 2 == 0 and  b % 2 != 0 and c % 2 != 0 and d % 2 == 0:
        return 'Числа A и D четные, а B и C нет'
    elif a % 2 == 0 and  b % 2 == 0 and c % 2 != 0 and d % 2 != 0:
        return 'Числа A и B четные, а C и D нет'
    elif a % 2 == 0 and  b % 2 != 0 and c % 2 == 0 and d % 2 != 0:
        return 'Числа A и C четные, а B и D нет'
    elif a % 2 == 0 and  b % 2 != 0 and c % 2 != 0 and d % 2 != 0:
        return 'Все числа нечетные, кроме числа А'
    elif a % 2 != 0 and  b % 2 == 0 and c % 2 != 0 and d % 2 != 0:
        return 'Все числа нечетные, кроме числа B'
    elif a % 2 != 0 and  b % 2 != 0 and c % 2 == 0 and d % 2 != 0:
        return 'Все числа нечетные, кроме числа C'
    elif a % 2 != 0 and  b % 2 != 0 and c % 2 != 0 and d % 2 == 0:
        return 'Все числа нечетные, кроме числа D'
    else:
        return 'Все числа нечетные'
```

## Избавляемся от лишних логических выражений и условий
Все возвращаемые значения можно разделить на 4 группы.

Цикломатическая сложность: 7
```python
def foo(a, b, c, d):
    odd_numbers = []
    even_numbers = []
    for name, value in zip(["A", "B", "C", "D"], [a, b, c, d]):
        (even_numbers if value % 2 == 0 else odd_numbers).append(name)
    if len(odd_numbers) == 0:
        return 'Все числа четные'
    elif len(odd_numbers) == 1:
        return f'Все числа четные, кроме числа {odd_numbers[0]}'
    elif len(odd_numbers) == 2:
        return f'Числа {even_numbers[0]} и {even_numbers[1]} четные, а {odd_numbers[0]} и {odd_numbers[1]} нет'
    elif len(odd_numbers) == 3:
        return f'Все числа нечетные, кроме числа {even_numbers[0]}'
    else:
        return 'Все числа нечетные'
```

## Используем список функций вместо условий
Размер списка нечётных чисел - индекс в списке генераторов результата.

Цикломатическая сложность: 3
```python
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
```
