# Сила низкоуровневых подходов

## 1. Выводы по теории
Язык C всегда мне нравился своей близостью к железу.
Изучать программирование я начал с Pascal,
и там указатели были каким-то сакральным знанием.
В C они настолько естественны, что легко и быстро приучаешься думать
о программе именно в терминах памяти и указателей.
Даже указатели на функции воспринимаются легко.

Всё это, конечно, очень удобно для обмена данными и кодом между программами.
Какие бы абстракции не использовал высокоуровневый язык,
в конечном счёте всё сводится к линейной памяти,
в которой лежат данные и команды (и между ними нет принципиальной разницы).


## 2. Закрытые форматы данных

### 2.1 Спектры
Спектрометры фирмы Bruker хранят результаты измерений
в собственном бинарном формате.
Давным давно у меня была необходимость регулярно вручную конвертировать
в текст по несколько десятков спектров (по одному файлу, естественно).
Очень быстро я переключился на более творческую задачу -
обратный инженерный анализ формата данных
на основе весьма скудной документации.
Мне удалось сделать скрипт, который пачками переводил спектры
в простой текстовый формат.

Тот скрипт давно устарел, но у нас теперь есть
[brukeropusreader](https://github.com/qedsoftware/brukeropusreader).
А вообще, важный урок для меня - не придумывать свои форматы
для простых и давно известных вещей вроде пар координат (x, y).

В моих расчётных программах все данные и результаты хранятся
в открытых форматах: TSV, YAML, HDF5.
Первые два из них даже текстовые, а третий - двоичный - для тяжёлых случаев.


### 2.2 Графики
В нашей лаборатории для хранения и обработки экспериментальных данных
используется Origin с его форматом файлов opj.
Конечно, кроме Ориджина ничем их не открыть и не прочитать,
и библиотеки для Python я пока не видел.

Тут нет ничего сверхъестественного - просто таблицы чисел и данные
для построения графиков на их основе.
Вот бы это всё хранилось в HDF5, например.
Тогда бы я некоторые результаты расчётов сразу оформлял в виде
ориджиновских графиков, на радость коллегам.


### Выводы
Других взаимодействий с проприетарными форматами у меня не было,
вероятно в силу специфики профессии.
Уже из этого опыта очевидно сколько работы добавляет использование
малоизвестных, закрытых, нишевых форматов данных.
Некоторые приятные вещи становятся практически невозможными.

Если посмотреть на это с точки зрения математики
и представить программу как функцию для преобразования данных,
то у этой функции нет выходных данных.
Действительно, чтобы прочитать файл, нужно снова запускать программу -
это больше похоже на бесконечную рекурсию.
Выходными данными будут результаты экспорта в формат,
который может прочитать другая программа
(или печать документа, для формата DOC, например).
Сложно комбинировать инструменты, у которых нет точек входа и выхода.