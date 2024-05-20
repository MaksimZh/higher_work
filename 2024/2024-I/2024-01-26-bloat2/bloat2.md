# Про раздутость кода

## 1. Выводы по изучению материала
Исторически сложилось так, что обучение программированию начинается
с императивного стиля и, чаще всего, на этом и заканчивается.
Текстовые языки программирования очень хорошо тут подходят,
так как в тексте уже есть выделенное направление - последовательность
символов, и последовательность команд на неё хорошо ложится.
Даже если использовать функциональный язык, то программа всё равно
читается сверху вниз и по привычке воспринимается
как последовательность команд.
В лучшем случае - как последовательность команд для компилятора.

В некоторых западных университетах обучение программированию
начинается с функционального стиля,
но подозреваю, что в школах там подход всё равно традиционный.
Отсюда привычка думать кодом, а не данными.
Раз уж от текста (пока) никуда не деться,
придётся учиться смотреть на него нелинейно,
выделяя взглядом и комментариями смысловые блоки,
намешанные в "лапше" из команд.


## 2. Работа с кодом

### 2.1 Разбиение осей на группы
```Python
# Split axis sets into groups: common and specific for tensors
common_axes = h.axes & energy.axes
common_axes_tuple = tuple(common_axes)
extra_energy_axes_tuple = tuple(energy.axes - common_axes)
non_matrix_axes = h.axes - h.axes_of_kind(MatrixAxis)
extra_h_axes_tuple = tuple(non_matrix_axes - {k_left, k_right} - common_axes)
```
Есть общие оси для обоих тензоров и свои для каждого.
Для двух тензоров всего три подмножества, но для трёх - уже 8.
Надо что-то с этим делать.


### 2.2 Выделение строк и столбцов в одном и том же порядке
```Python
# Get column and row axes in the same order
matching_axes = tuple(h.matching_axes)
cols = tuple(ma.col for ma in matching_axes)
rows = tuple(ma.row for ma in matching_axes)
```


### 2.3 Согласованная распаковка тензоров
```Python
# Common axis pattern:
#     k_left, k_right
#     common_axes_tuple
#     extra_h_axes_tuple
#     extra_energy_axes_tuple
#     col, row
raw_h_energy = \
    h.unwrap(
        k_left, k_right,
        common_axes_tuple,
        extra_h_axes_tuple,
        add(extra_energy_axes_tuple),
        merge(cols), merge(rows)) - \
    energy_pattern.unwrap(
        k_left, k_right,
        add(common_axes_tuple),
        add(extra_h_axes_tuple),
        add(extra_energy_axes_tuple),
        col, row) * \
    energy.unwrap(
        +k_left, +k_right,
        common_axes_tuple,
        add(extra_h_axes_tuple),
        extra_energy_axes_tuple,
        +col, +row)
```
Не всегда это делается в одном выражении, но принцип тот же:
добавляя и комбинируя оси тензоров нужно добиться,
чтобы у получившихся массивов было одинаковое количество осей,
и их размеры были согласованы.


### 2.4 Копирование параметров осей тензоров
```Python
return type(self)(
    raw_result,
    common_axes,
    extra_self_axes,
    extra_other_axes,
    merge(
        # Copy parameters and sizes from source
        non_matrix_params.add_to(ax)(COL)[self.sizes[ax]]
        for ax in cols),
    merge(
        # Copy parameters and sizes from source
        other_non_matrix_params.add_to(ax)(ROW >> col)[other.sizes[ax]]
        for ax, col in zip(rows, cols)))
```
Вроде код одинаковый, но я и так уже функцию `add_to` сделал.
Можно, правда, ещё с размерами что-то придумать.


### 2.5 Смена типа тензора
```Python
# Change tensor type
right_coefs = WaveCoefTensor(
    eye_like(tm_start).unwrap(
        dir_col, ext_cols,
        merge(dir_row, ext_rows),
        array_axes),
    dir_col(SOL, wave_dir_basis),
    (ax(SOL) for ax in ext_cols),
    test_axis,
    array_axes)
```
Распаковка тензора и упаковка результата в другой тип
с новыми параметрами осей.


### Выводы
В 2.1 и 2.3 выделить какой-то блок в функцию не получается,
но если присмотреться, то информация из пункта 2.1 используется в 2.3,
и для более чем двух тензоров тут очень сложно будет не запутаться.
В коде такая комбинация встречается очень часто,
и её лучше выделить в отдельную абстракцию, общую для двух пунктов.

В пункте 2.4 можно уравнять в правах размеры и параметры.
Это сильно упростит код даже без придумывания новых функций.


## Общие выводы
В ходе размышлений над типовыми блоками кода,
которые приведены в предыдущем разделе,
пришло понимание, что функции - далеко не единственный и не всегда лучший
способ избегать дублирования.
Иногда нужно работать как раз с типами данных.

Один и тот же алгоритм в одной системе типов будет спагетти-кодом,
а в другой его можно разбить на элегантные процедуры.
Например, несколько значений, которые вместе создаются и вместе используются,
можно объединить в одно значение.
