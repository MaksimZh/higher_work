# Модули важнее всего

## 1. Теория
В теории, вроде бы, всё просто:
если у модулей одинаковые интерфейсы, то они взаимозаменяемы.
На практике же всё гораздо сложнее.

Во-первых, понятие модуля в конкретном языке программирования
может означать всё что угодно,
и чаще всего это либо пространство имён, либо файл,
либо какая-то комбинация этих двух объектов.
Это вообще не про интерфейсы и замену реализации.

Во-вторых, понятие интерфейса довольно расплывчатое.
Чаще всего под этим понимаются сигнатуры набора функций,
но это на самом деле ничего не означает.
В Python достаточно имён функций, но можно и без них обойтись.
Где-то уже требуются типы аргументов, только это ничего не гарантирует.
Если сигнатуры функций совпадают, но они их реализация не следует спецификации,
то такой модуль не подходит.
При этом компилятор жаловаться не будет,
потому что в большинстве языков совсем нет средств
для выражения правил спецификации сложнее,
чем типы аргументов и возвращаемого значения.

Увы, на данный момент признаком развитой системы типов
считается не возможность кодирования спецификаций,
а требование писать `x + 2.0f` вместо `x + 2`.
Так что за модульностью нужно следить "вручную" - на уровне документации.


## 2. Одна реализация - несколько интерфейсов

### 2.1. "Мир есть атомы, движущиеся в пустоте"
В одной из моих программ есть модуль (ещё не законченный),
который просто умеет выводить на экран пачки треугольников
с натянутой текстурой, в которой по особым правилам подменяются цвета.

Изначально это было нужно для рисования разноцветных геометрических фигур.
Потом появились и другие задачи и оказалось,
что при весьма ограниченном интерфейсе этот модуль умеет рисовать:

 1. геометрические фигуры из заранее заданного набора форм и цветов;
 1. линии произвольной формы и даже со стрелками (цвета из того же набора);
 1. текст (цветной);
 1. виджеты графического интерфейса (и их тоже можно красить!);
 1. изображения как они есть (без подкрашивания).

Всё делает один шейдер, и поэтому его не нужно менять посреди отрисовки кадра.
Он работает на чистой арифметике без `if`-ов,
чтобы не приходилось презагружать конвееры ядер видеокарты.
На одной текстуре нарисованы нужные геометрические формы,
символы для текста и палитры цветов.

```GLSL
// цвет точки спрайта
vec4 tex = texture(texture0, texCoord);

// палитры нарисованы на той же текстуре
// palIndex - грубая настройка (выбор палитры)
// зелёная и синяя компоненты (tex.gb) - выбор цвета внутри двумерной палитры
float origin = palOrigin + palIndex * palStride + tex.gb * palWindow;

// у каждой палитры есть двойник, смещённый на palDelta
vec4 pal0 = texture(texture0, origin);
vec4 pal1 = texture(texture0, origin + palDelta);
// красная компонента задаёт цвет между основой палитрой и двойником
// эта линейная интерполяция используется для градиентов в спрайтах
vec4 pal = mix(pal0, pal1, tex.r);

// если палитра прозрачная (pal.a == 0) - берём цвет из спрайта
// если нет (pal.a == 1) - красим точку по правилам выше
outColor = vec4(mix(tex.rgb, pal, pal.a), tex.a);
```


### 2.2. Парное программирование
Если бы в стандартной библиотеке Python был тип `Pair`,
был бы велик соблаза использовать именно его.
Однако смысловая нагрузка элементов тут очень важна:
это аргумент (тег) и то, к чему он цепляется:

```Python
class Tagged[T, A]:
    @property
    def target(self) -> T: ...

    @property
    def arg(self) -> A: ...

    ...
```

Потомки этого класса не меняют сути,
только добавляют возможность применения разных операторов
и, иногда, интерпретацию свойств.

```Python
a(b, c, d)     # Parameterized[T, P]        ~ Tagged[T, Set[P]]
a[i]           # Indexed[T]                 ~ Tagged[T, int]
a[i](b, c, d)  # IndexedParameterized[T, P] ~ Tagged[T, tuple[int, Set[P]]]
```

Все эти конструкции - пары.


## 2.3. Тензоры
Пары из предыдущего примера - это вспомогательный элемент
для другой абстракции - тензоров -
многомерных массивов, оси (размерности, позиции индексов) которых
являются важными сущностями на уровне логики и кода программы.
Вот что можно представить в виде тензора:

 1. пространственные сетки для расчётов;
 1. многочлены, в том числе - матричные многочлены;
 1. как следствие - системы дифуров с полиномиальными коэффициентами;
 1. операторы из квантовой механики;
 1. волновые функции;
 1. распределение электрического поля;
 1. ...

Что конкретно кодирует тензор - вопрос интерпретации осей.
Его базовые функции, такие как сечение массивов и арифметика,
имеют смысл и используются для всех этих случаев.
Было время, когда я успешно использовал библиотеки XArray
и даже чистый NumPy, пока не запутался.

Теперь у класса `Tensor` есть потомки,
которые умеют (и проверяют) больше, чем работа с осями.
То есть, часть логики, которая раньше была только на уровне спецификации,
переместилась в код - в систему типов проекта.
Класс `Tensor` собрал ту часть этой логики,
которая оказалась общей для всех блоков данных.


### Выводы
Абстрактные реализации, подходящие под несколько интерфейсов -
следствие стремления к повторному использованию кода.
Где-то это удобно для сопровождения (`Tagged`, `Tensor`),
а где-то даёт реальный выигрыш в производительности
(один шейдер, одна текстура, один буфер).

С другой стороны, всё равно есть стремление
обернуть эти абстрактные реализации
в конкретные интерфейсы даже на уровне системы типов.
Например, для `Tagged` есть несколько типов-потомков,
а для `Tensor` их на порядок больше.
Это позволяет не путать те сущности,
которые отличаются на уровне логики, но похожи на уровне кода.
Даже в случае рендерера, исходные данные имеют разные типы,
а уже при отрисовке преобразуются в однородный набор
текстурированных треугольников.


## Общие выводы
Жаль, что нельзя полностью описать спецификацию для модуля на уровне кода.
Это бы сняло целую кучу вопросов, в частности,
по поводу формального доказательства корректности программ.
Конечно, тогда создание даже простейшей структуры данных
превратилось бы в хорошую математическую задачу университетского уровня.
Такой подход поднял бы разработку ПО по уровню сложности и надёжности
на уровень конструирования современных авиадвигателей,
которое могут позволить себе 5-6 стран.
Тогда название профессии software **engine**er заиграет новыми красками.

Конечно, "самолёт" можно и в гараже собрать,
но он, скорее всего, упадёт, и может причинить серьёзный вред.
Поэтому в этой сфере так высоки требования к качеству.
То же ждёт и мир ПО, тем более, что оно уже повлияло на ряд катастроф
космических аппаратов с большими финансовыми потерями
и самолётов с человеческими жертвами.

Так что лично мне точно имеет смысл изучать те средства,
которые позволяют кодировать сложные формальные спецификации.
