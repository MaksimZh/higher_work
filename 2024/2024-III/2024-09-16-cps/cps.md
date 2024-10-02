# Дефункционализация + CPS

# 1. Теория
Дефункционализация - это превращение кода в "удобные" данные,
которые можно хранить на диске и передавать по сети.
В комбинации с CPS (continuation passing style)
это позволяет делать выполнение кода распределённым
во времени и в пространстве,
то есть, сохранять код продолжения, чтобы выполнить его
в другое время или на другой машине.

Если рассматривать программу как преобразование данных,
то мы получаем очень высокий уровень абстракции от среды выполнения.
Программа выполняется в нескольких сессиях (за несколько запусков),
а её отдельные части выполняются на разных машинах.
При этом алгоритм всё тот же, только записан в виде данных
(дефункционализированный вид),
которые можно свободно хранить и передавать.


# 2. Практика
Научные рассчёты часто требуют большого времени,
поэтому их часто выполняют параллельно на нескольких машинах
и в течение очень большого времени.
Выполнение программы может прерваться из-за аппаратной проблемы,
или из-за некритической ошибки в данных
(например, алгоритм не сходится, и нужно пробовать другие начальные условия).

Чтобы не начинать всё с самого начала,
хорошо бы сохранять промежуточные результаты вместе с оставшимися командами.
Эти же данные можно передавать на другие узлы кластера,
чтобы сбалансировать нагрузку.

Это можно реализовать в формате dataflow-графа,
где вычисленные процедуры отбрасываются,
а вместо них подставляются узлы промежуточных данных.
Естественно, удобнее хранить процедуры в дефункционализированном формате.

Сам граф данных и процедур - это обобщение CPS,
когда у нас есть не один поток данных, а несколько,
которые могут объединяться и разделяться.


# Общие выводы
В школьные годы чтение учебника по Ассемблеру дало очень мощный эффект
демистификации компьютеров вообще и языков программирования в частности.
В Ассемблере нет if-ов и while-ов, так же как и функций,
"возвращающих" значения.
Есть только поток команд, который может продолжаться
с самых разных позиций в коде.
На этом уровне нет разницы между входом в процедуру,
возвратом из неё, выбором ветки условного оператора,
или очередной итерацией цикла.

Структурное программирование и вычислительная модель со стеком -
это стандарт императивных языков,
который одинаково далёк и от низкоуровневой работы ЭВМ,
и от логики потока данных, лежащей в основе программы.
Вложенные блоки команд, из которых программа обязана вернуться наверх -
это только одна из возможных абстракций,
которая, к тому же, отравлена идеей, что код -
это трансцендентная сущность, которая с данными не смешивается.
Вероятно, это не самая удачная модель.

Дефункционализация, которая превращает код в данные,
и CPS, который идёт вразрез с привычным представлением о потоке выполнения, -
это основа для альтернативной вычислительной модели.
Этот подход куда лучше адаптирован к распространённым сейчас
распределённым и отложенным вычислениям.