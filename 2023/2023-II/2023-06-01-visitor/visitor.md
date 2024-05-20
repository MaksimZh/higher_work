# Истинное наследование

## Неистинное наследование
```Python
class Widget:

    def draw(self, canvas: Canvas) -> None:
        pass

    ...


class Button(Widget):
    __text: str

    def draw(self, canvas: Canvas) -> None:
        canvas.draw_rect(self.get_rect())
        text_position = ...
        canvas.draw_text(text_position, self.__text)

    ...


class ImageButton(Button):
    __image: Image

    # Метод переопределяется, потому что текст нужно рисовать в другом месте
    def draw(self, canvas: Canvas) -> None:
        canvas.draw_rect(self.get_rect())
        image_position = ...
        text_position = ... # другие координаты, не как у обычной кнопки
        canvas.draw_image(image_position, self.__image)
        canvas.draw_text(text_position, self.get_text())

    ...
```
Пример придуманный, но до прохождения курсов по ООАП я бы примерно так и сделал.
Моделируется ситуация, когда кнопку с картинкой и текстом захотелось добавить
после реализации обычной кнопки с текстом.
Чтобы не дублировать код и не думать "лишний" раз над архитектурой,
я бы использовал наследование и по-минимуму переопределял методы.

Помимо неистинного наследования здесь есть ещё минимум один недостаток.
Метод рисования, который выглядит как команда,
меняет свой аргумент `canvas`, а вовсе не сам объект.
То есть, это и не команда, и не запрос, а кнопка тогда вовосе неправильный АТД.


## Visitor
```Python
class Widget:

    def visit(self, visitor: "Visitor") -> None:
        pass

    ...


class Button(Widget):
    __text: str

    def visit(self, visitor: "Visitor") -> None:
        visitor.visit_button(self)

    ...


class ImageButton(Button):
    __image: Image


    def visit(self, visitor: "Visitor") -> None:
        visitor.visit_image_button(self)

    ...


class Visitor:
    def visit_button(self, button: Button) -> None:
        pass

    def visit_image_button(self, image_button: ImageButton) -> None:
        pass


class DrawingVisitor(Visitor):
    __canvas: Canvas
    ...

    def visit_button(self, button: Button) -> None:
        canvas.draw_rect(button.get_rect())
        text_position = ...
        canvas.draw_text(text_position, button.get_text())

    def visit_image_button(self, image_button: ImageButton) -> None:
        canvas.draw_rect(image_button.get_rect())
        image_position = ...
        text_position = ... # другие координаты, не как у обычной кнопки
        canvas.draw_image(image_position, image_button.get_image())
        canvas.draw_text(text_position, image_button.get_text())
```
После применения паттерна Visitor метод `Button.visit`
всё равно переопределяется, но это переопределение происходит только
на уровне кода, а не на уровне логики.
Это тривиальный шаблонный метод, логика работы которого
одинакова для всех классов в иерархии - вызвать метод посетителя,
соответствующий типу данного объекта.

Дополнительный бонус: мы больше не таскаем `canvas` по всем виджетам,
а спрятали его внутри `DrawingVisitor`.
Теперь, если нам потребуется изменить способ отображения,
соответствующий код собран в одном месте.
Хотя, конечно, при должной проработке и "заморозке" спецификации `Canvas`
это не было бы проблемой и в старой версии.

Теперь, правда, легче следовать принципу DRY:
```Python
class DrawingVisitor(Visitor):
    __canvas: Canvas
    ...

    def draw_button_rect(self, button: Button) -> None:
        canvas.draw_rect(button.get_rect())

    def visit_button(self, button: Button) -> None:
        self.draw_button_rect(button)
        text_position = ...
        canvas.draw_text(text_position, button.get_text())

    def visit_image_button(self, image_button: ImageButton) -> None:
        self.draw_button_rect(image_button)
        image_position = ...
        text_position = ... # другие координаты, не как у обычной кнопки
        canvas.draw_image(image_position, image_button.get_image())
        canvas.draw_text(text_position, image_button.get_text())
```
