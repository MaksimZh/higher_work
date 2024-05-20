# Божественная линия кода

## 1.
В одной строке вычисляется матрица и её определитель
```Python
detQ.append(np.linalg.det(solver.calc_localization_matrix(model, energy, meshParams)))
```
```Python
loc_matrix = solver.calc_localization_matrix(model, energy, meshParams)
detQ.append(np.linalg.det(loc_matrix))
```

## 2.
В одной строке нетривиальным образом вычисляются индексы и производится "выборка" по этим индексам
```Python
calcEnergies = energies_meV[np.logical_not(
    np.isclose(energies_meV[:, np.newaxis], oldEnergies).any(1))]
```
```Python
intersection_indices = \
    np.isclose(energies_meV[:, np.newaxis], oldEnergies).any(1)
calcEnergies = energies_meV[np.logical_not(intersection_indices)]
```

## 3.
Две операции деления подряд, которые по логике алгоритма лучше явно выделить
```Python
remainder_matrix[:, column : column + 1] = \
    a @ inv_right_matrix[:, column : column + 1] // factor_powers[exponent] % factor
```
```Python
column_vector = a @ inv_right_matrix[:, column : column + 1]
higher_pow_coef = column_vector // factor_powers[exponent]
remainder_matrix[:, column : column + 1] = higher_pow_coef % factor
del column_vector, higher_pow_coef
```

## 4.
В одной строке вычисляем границу сравниваем значение с ней
```Python
if (np.abs(ai - bi) > abstol + reltol * max(np.abs(ai))).any():
    ...
```
```Python
max_error = abstol + reltol * max(np.abs(ai))
if (np.abs(ai - bi) > max_error).any():
    ...
```

## 5.
В одной строке решаем уравнение, объединяем разные решения и сортируем
```Python
return np.array(sorted(list(np.roots(self.coefs(en))) + [k2a]))
```
```Python
eq_roots = np.roots(self.coefs(en))
solutions = list(eq_roots) + [k2a]
return np.array(sorted(solutions))
```
