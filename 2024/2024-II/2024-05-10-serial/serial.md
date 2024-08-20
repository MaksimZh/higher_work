# Об опасности стандартных подходов

## 1. Выводы по теории
В книге "Чистая Архитектура" Роберт Мартин советует рассматривать
сеть просто как ещё одно устройство ввода-вывода.
При таком подходе при разработке логики приложения
вообще не будешь обращать внимания на форматы сериализации -
это же просто способ передачи данных.
Трудно представить себе программу, где все структуры данных
базируются на массивах 25x80 символов по стандартному размеру
старых устройств вывода.

Кстати, всегда следует ожидать, что с устройства ввода
могут поступить вредоносные данные,
а вывод может быть доступен кому угодно.
Поэтому при таком восприятии обмена данными как-то сами собой
приходят правильные мысли об их безопасности.

Противоположный подход - превращать приложение в подобие плагина
к какому-нибудь веб-фреймворку,
когда ядро размазано и насквозь пропитано вызовами внешнего API.
Тут и проблемы с зависимостями и трудности проектирования
из-за привыкания обдумывать логику приложения
в терминах конкретного инструмента.

Что ещё более печально - слишком много внешнего кода вызывается в ядре
в самых неожиданных местах и прямо с внутренними форматами данных
в качестве параметров.
Понятно как это сказывается на безопасности, если даже для простых
библиотек сериализации/десериализации мы видим такие предупреждения:

> Warning The pickle module is not secure. Only unpickle data you trust.
>
> It is possible to construct malicious pickle data which will
> **execute arbitrary code during unpickling**.
> Never unpickle data that could have come from an untrusted source,
> or that could have been tampered with.

Одно дело отдельные параметры, другое - целые записи с кучей полей,
по которым можно восстановить часть содержимого базы данных.

Может пусть лучше этот внешний код работает с зашифрованными данными?


## 2. Важные структуры данных в моём коде
Очень много усилий уже было (и ещё будет) потрачено 
как раз на разработку структур данных на основе тензоров.
Раньше использовались просто массивы NumPy, потом XArray с информацией,
кодируемой в названиях осей, но это всё не то.
Это всё слишком общие типы данных, конкретный смысл в которые
вкладывается кодом, который из обрабатывает.

Теперь ядром расчётной программы является библиотека тензоров,
которая позволяет создавать и комбинировать
(с помощью множественного наследования)
абстракции на основе многомерных массивов
с произвольными параметрами у осей.
Каждому отдельному свойству объектов в предметной области
соответствует отдельный тип.
Каждому классу объектов с определённым набором свойств
также соответствует отдельный тип.


## 3. REST API без глобального хранилища
Как работать без общего доступа к глобальному хранилищу?

### 3.1. Локальные идентификаторы
После аутентификации клиента ему сообщается его временный id,
который знает и сервер.
Клиенту необязательно знать какой ключ у него в БД сервера.

Когда клиенту выдаётся информация о каких-то объектах (строках в БД),
например, в виде списка,
для них также генерируются временные id.
Эти идентификаторы используются при обмене информацией с данным клиентом.

Важно, что сам клиент в хранилище не лезет и не имеет доступа
(так что и ORM ему не нужен).
За дополнительной информацией он обращается к серверу,
используя временные id.


### 3.2. Инкапсуляция
А вообще, зачем клиентам знать, про какие-то записи в БД?
Интерфейс взаимодействия между подсистемами
может опираться на свои структуры данных,
в которых нет лишней информации.

Если мы, например, в соцсети передаём список друзей,
то клиент видит только этот список,
и ему не важно, как сервер его собирал.
(может, с других серверов и с помощью других типов данных).
Тут также используется локальный id,
но он относится только к списку,
и не обязательно должно быть возможным отображение
этих id в что-то в хранилище данных.


### 3.3. Stateless
Никаких временных id, никакого общего доступа к глобальному хранилищу.

Если на уровне логики есть сущности, которые нужно идентифицировать,
то для них должны существовать id,
по которым можно найти информацию и в БД,
и в передаваемых клиентам структурах данных.
Пример - уникальный логин пользователя.

Состояние есть только у хранилища данных (оно может быть распределённым)
и у клиентов с графическим интерфейсом пользователя.


## Общие выводы
Как велик соблазн дать всем элементам системы доступ к БД
и обмениваться ключами!
Кажется, что это сэкономит кучу трафика, например
(нет, и ещё нагрузка на БД возрастёт).

Но тогда система будет монолитной,
и тестирование отдельных подсистем потребует хотя бы тестовой БД,
а также кучи заглушек и приляпок.
Такие системы хранения данных -
это особая форма глобальных переменных,
со всеми их недостатками.

Если уж мы стараемся избегать явной работы с изменяемыми состояниями
даже для локальных систем,
то для распределённых систем это вообще засада.
Так что лучше уж обмениваться сообщениями
и сразу закладывать асинхронность,
т.е., например, уметь обрабатывать ситуации,
когда, старые данные пришли после того, как мы отравили новые.