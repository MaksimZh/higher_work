# Отказываемся от хранения логических значений

## 1. Теория
Логические значения это, обычно, оптимизация -
результат вычисления какого-то условия.
В этом условии может быть гораздо больше информации,
но, если она не нужна, то её можно забыть,
оставив только логический результат.

Всё бы хорошо, но как узнать наперёд,
какая информация всегда будет избыточной,
а какая может понадобиться при развитии проекта.
Когда речь идёт о каких-то сервисах с базами данных,
работающих продолжительно время (десятки лет),
то любую информацию стоит подозревать в том,
что в перспективе она понадобится.

То есть, вместо логических значений лучше бы хранить
исходные аргументы логического выражения.
Вдруг они понадобятся для чего-то ещё.


## 2. Примеры
На данный момент у меня нет проектов, где используются базы данных.
Поэтому пофантазируем.

### 2.1. Привилегированные игроки
Пусть в какой-то онлайн игре получаемые бонусы
(опыт персонажа, ресурсы и т.п.)
зависят от того, активна ли у игрока премиум подписка.
Если в начале планировалась только покупка перманентной подписки,
то велик соблазн просто добавить каждому игроку поле с логическим значением,
где `True` - премиум, а `False` - обычный аккаунт.

Потом кому-то может прийти мысль о продаже подписки ограниченной во времени,
и для неё придётся добавлять в базе другие поля.
Если же мы захотим давать игрокам регулярные плюшки за "премиум-стаж",
то где брать информацию о том, когда он начался?
Можно сразу сохранять время активации премиума
и количество оставшихся дней до его окончания
(предусмотрев особое значение для перманентной подписки).
Вместе с текущей датой этой информации достаточно для вычисления
статуса подписки `True`/`False`.


### 2.2. Мы знаем, что вы постили прошлым летом
Пусть какая-то страна вдруг разонравилась сразу большому количеству
иностранных граждан, и они успели понаписать про неё гадостей в соцсетях.
Потом эти граждане передумали и решили в эту страну переехать.
В аэропорту их встречает местная служба государственной безопасности,
заносит имигрантов в базу данных и присваивает статус `False` всем,
у кого находит "неправильные" лайки и репосты.
Конечно, никого с `False` в эту удивительную страну не пускают.

Пусть местное население в этой гипотетической стране
отличается добрым нравом и гостеприимством
и решает всё же пускать тех, кто совершил суровую аскезу:
`N` лет не писать и не лайкать гадости.
Тогда лучше при первой встрече вместо `False`
записывать в базу дату последней нежелательной активности.
В этом случае придётся проверять только прошло ли `N` лет
и не было ли за это время новых пакостей.


### 2.3. Напарники
Пусть в каком-то онлайн-тренинге участники должны выполнять
некоторое задание в парах.
Кто нашёл пару и сделал задание - тем мы ставим `True`,
а остальные выбирают напарника из списка `False`.
Потом нам захочется несколько таких заданий
(и под каждое придётся заводить поле в базе),
несколько попыток с разными напарниками
(ещё поля? ну нет!) и т.д.
От таких тербований заказчика "логическая" схема рушится на глазах.

Куда лучше записывать в отдельную таблицу
информацию о каждом выполненном задании каждой парой
(задание, время, участники).
Такая схема гибче, потому что при её развитии
не нужно плодить новые поля в других таблицах.


### Выводы по практике
Осталось ощущение какой-то антиоптимизации.
Приходилось думать: как бы сохранить побольше данных,
хотя в школе меня учили такие вещи наоборот - сокращать.
Это одно из отличий школьного/олимпиадного программирования
от взрослого - промышленного.
Экономия памяти и вычислительных ресурсов уже не в приоритете,
куда важнее гибкость системы - обратная стоимость изменения
под новые требования.
Этот параметр включает в себя сложность апгрейда базы данных под новую логику,
и тут избыточность данных играет только в плюс.


## Общие выводы
Если чуть расширить тему, не ограничиваясь только логическими значениями,
то можно прийти к выводу, что база данных должна содержать
максимально конкретную информацию, не нагруженную лишними абстракциями.
Вместо интерпретации события следует хранить
максимально подробное описание самого события,
вместо флага - время его установки,
вместо списка друзей - время отправки и принятия приглашения в друзья
и т.д.
Тогда на основе этих "сырых" событий можно будет выстраивать
более сложную логику,
и чем более низкоуровневыми являются такие записи,
тем более сложными и разнообразными могут быть абстракции-надстройки.
