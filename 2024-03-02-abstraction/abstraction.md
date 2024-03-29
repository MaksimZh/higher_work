# Что такое абстракция: разминочное

## 1. Рефлексия по теории
Очень люблю математику!
Она вся построена на абстракциях и прекрасно себя чувствует.
Только встраивание в мозг новых абстракций
требует времени и заметных усилий.
При этом оно, увы, не является необратимым процессом:
неиспользуемые абстракции со временем выветриваются.
Некоторые из них, однако, настолько мощны, что затраты с лихвой окупаются.

Самая моя любимая абстракция, наверное, это Гильбертово пространство.
Она позволяет думать об очень сложных задачах
в терминах векторов и координат,
известных и интуитивно понятных ещё со школы.

В программировании можно что-то похожее организовать.
Например, отобразил "сложный" алгоритм в набор `map`/`reduce`,
и вот он уже простой и помещается в 2-3 строки.


## 2. Логика
Есть в физике полупроводников три задачи,
которые решаются с помощью примерно одного и того же уравнения,
вот только решать это уравнение нужно по-разному.

Найти волновые функции в непрерывном спектре:
 1. донора в приближении эффективной массы;
 2. акцептора в модели Латтинжера;
 3. акцептора в модели Кейна.

Общий вид уравнения известен,
и на определённом уровне абстракции он будет спрятан внутри функции.
Для решения нужно просто задать энергию состояния и начальные условия
и вместе с этой функцией передать их в солвер
из любимой математической библиотеки.

А вот теперь добавляем новое требование:
решение должно иметь физический смысл.
Казалось бы, это требование очевидно вытекает из условия задачи,
но как только физическая задача превращается в математическую,
возникает соблазн "забыть" ряд неявных условий и решать задачу "в лоб".
Потом с удивлением смотрим на ответ и вспоминаем про физический смысл.

В первом случае наивная реализация работает, и мы получаем правильный ответ.

Во втором случае малое изменение энергии может радикально изменить решение.
Для каждой энергии существует два решения, и они представляют собой
как бы две ортогональные координатные оси на плоскости.
Систему координат можно выбрать произвольно,
поэтому из-за, например, ограниченной точности чисел с плавающей точкой
мы получим псевдослучайный угол поворота этих осей.
Нужно будет следить за непрерывностью ответа как функции энергии,
или он будет выглядеть как шум.

В третьем случае дифференциальное уравнение будет неустойчивым,
и метод решения Эйлеровского типа даст сбой.
Есть пара способов победить эту неустойчивость,
но на первоначальную реализацию это будет совсем-совсем не похоже.


## 3. Полиморфизм и боксинг
Посмотрел старое упражнение про полиморфизм,
и к своему удовольствию заметил, что не использовал боксинг
(запихивание нескольких функций в одну с кучей параметров и условий).
Даже наоборот - разобрал одну такую функцию
с помощью добавления новой абстракции.

Вообще для меня полиморфизм почти противоположен боксингу.
Он должен уменьшать количество ветвлений в коде за счёт того,
что делает разные вещи локально одинаковыми -
там, где используются их общие свойства.


## 4. Перенаправление
В другие файлы при разборе своего кода обычно не залезаю.
Бывает, что в рамках одного файла возникают цепочки вложенных функций.
Стараюсь уходить от этого, создавая универсальные полиморфные функции,
для которых в месте вызова понятно что она делает.
Примеры таких функций в стандартной библиотеке: `sort`, `map`, `reduce`.
Примеры моих функций:
`unwrap_iterables`, `assume_single`, `find_duplicates`.

Меня лично очень раздражает, когда в чужом коде
приходится скакать через 2-3 файла,
чтобы собрать в голове логику какой-то функции.
Хорошая идея для обфускатора - раскидывать код одной функции по нескольким
классам и файлам.


## Рефлексия
Посреди выполнения этого упражнения выступал на конференции по физике,
что дало вдохновение для пункта 2
и помогло шире взглянуть на понятие абстракции.

Зачем вообще заниматься абстракцией,
то есть отображением одной системы в другую,
с риском нарушить какие-то важные свойства?
Затем, что если мы сохраним важные для нас свойства,
то в новой системе можем заработать радикальное упрощение
манипулирования этими свойствами.

В физике принять отображать всё в математику,
а в программировании, увы, не всегда.
Здесь, скорее, обратный эффект:
математический анализ с его непрерывностью,
бесконечно малыми величинами и пределами
отображается в операции с числами с плавающей точкой.
Вот тут-то и начинаются приключения.

В случае с численным решением физических задач
мы последовательно осуществляем две абстракции:
в матанализ, а затем в дискретную математику.
При этом у нас сразу два места, где можно накосячить.
Наш преподаватель по вычислительной математике как-то сказал:
"Вы сначала представляете цепочку грузиков и пружинок как
непрерывную струну и пишите для неё дифуры,
а потом для решения этих дифуров, опять разбиваете струну на кусочки.
Зачем? Останьтесь здесь!
(т.е. сразу решайте задачу для цепочки, без перехода к струне)".
Только теперь я понял, насколько фундаментальную вещь он говорил.
