# Избавляемся от stateful через глобальное состояние

## 1. Теория
Проблема состояний не в самих состояниях.
В конце концов, изменяемые состояния используются в компьютере
при выполнении любых программ,
хоть декларативных, хоть императивных.
Сложности возникают, когда состояния становятся частью логики программы,
когда о них нужно думать при проектировании и сопровождении кода.
Проблема именно во внутренних состояниях,
которые не относя ко входным или выходным данным,
и поэтому их значения нельзя записать, прочитать, подменить, воспроизвести.
Отладчик необходим именно для этого -
чтобы сделать внутренние состояния внешними.
Без этого найти ошибку в императивном коде было бы на порядок сложнее.

Итак, если отладчик делает понимание кода проще,
почему бы сразу не сделать понимание кода проще?
Что делает отладчик?
Превращает локальное состояние (доступное только изнутри программы)
в глобальное (доступное извне).
Так не лучше ли сразу сделать все состояния глобальными?


## 2. Практика
Проект редактора графического кода многомерных программ
замечателен тем, что он обладает GUI, и потому принципиально интерактивный.
Его нельзя просто превратить в обработчик файлов.
Ещё один плюс - работа только началась,
и есть возможность сразу принять ряд хороших решений,
чтобы потом всё не исправлять.

В этом редакторе предвидится целая куча состояний:
 1. документ, или граф, являющийся исходным кодом программы;
    понятно, что он будет меняться в процессе редактирования;
 2. настройки редактора (глобальные и привязанные к конкретному проекту);
 3. состояние интерфейса (где что выбрано или нажато).

С первыми двумя пунктами всё очевидно.
Эта та информация, которую всё равно нужно хранить в файлах,
а состояние в памяти - это просто кэш.
Если все изменения немедленно отображаются в файл,
то это ещё и облегчает восстановление после сбоев.
В качестве бонуса тут появится возможность
хранения истории изменений для команд Undo/Redo
с функцией интеграции этого дела с системой контроля версий.

Поскольку документ у нас графический, а настройки задаются через GUI,
велик соблазн сделать эти два пункта состояниями GUI.
Документ - это набор связанных виджетов,
а настройки - свойства других виджетов
(например, установлена галочка на форме, или нет).
Такой подход, однако, был бы злостным нарушением
принципа единственной ответственности,
а также размазал был логически связанные данные
по набору локальных трудноизвлекаемых состояний.

Теперь переходим к состоянию интерфейса.
Полностью избавиться от него не получится,
значит нужно сделать его максимально безопасным.
Все действительно важные элементы этого состояния
относятся либо к документу, либо к настройкам.
Даже если мы оторвали конец связи от одного узла и потащили к другому -
это изменение кода, и такое состояние должно быть допустимым и сохраняемым,
пусть даже статический анализатор разукрасит код яркими цветами,
сетуя на недоделанность программы.
Даже если мы просто сменили активную вкладку на панели инструментов -
это изменение настроек, и при следующем запуске новая вкладка будет
отображаться по умолчанию.
Всё, что в итоге останется внутренним состоянием интерфейса
будет несущественно для работы программы,
например, текущий кадр анимации, или состояние кнопок мыши.


## Выводы
Когда я заканчивал университет, при обработке моего личного дела в военкомате
произошёл сбой, виной которому было как раз локальное состояние.
После запуска сбора документов для призывной комиссии
моё личное дело перекочевало из общего хранилища в кабинет врача.
Несколько дней спустя началась обработка другого запроса:
выселение из общежития и смена военкомата.
А личного дела в хранилище нету.

Место хранения личного дела - это внутреннее состояние военкомата,
недоступное извне.
В поликлиниках та же ерунда регулярно случается
с бумажными карточками пациентов.

Если бы вместо переноса личного дела из кабинета в кабинет
в нём делались бы соответствующие пометки,
а само оно хранилось бы в строго определённом месте,
система была бы устойчивей.
Это был бы аналог глобального, общедоступного состояния.
Да, это требует дополнительных расходов времени,
ведь удобнее хранить бумаги, с которыми работаешь, у себя в кабинете,
но, если с ними работает кто-то ещё, лучше пусть лежат в общедоступном месте.

В программировании есть множество возможностей
для работы с глобальным состоянием,
которые в бумажном документообороте так просто не реализовать.
Например, журналы изменений, резервное копирование, транзакции -
для всего этого не нужно строить "регистратуры"
и нанимать дополнительных людей.
Поэтому имеет смысл сразу вкладываться
в перенос локальных состояний в глобальные.
Это стоит не так дорого, а затраты окупятся
за счёт упрощения внесения изменений и сопровождения.