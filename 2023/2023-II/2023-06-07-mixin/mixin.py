class Shape:
    def get_border_points(self) -> str:
        return "Shape.get_border_points"

class FillTriangleMixin:

    def __init__(self) -> None:
        # у миксина нет родителя
        # так вызывается конструктор следующего класса в MRO
        super().__init__()

    def get_colored_triangles(self) -> str:
        border_points = self.get_border_points()
        return "FillTriangleMixin.get_colored_triangles <- " + border_points

class VisibleShape(FillTriangleMixin, Shape):
    pass

class BezierMixin:
    
    def get_border_points(self) -> str:
        base_points = super().get_border_points()
        return "BezierMixin.get_border_points <- " + base_points

class VisibleBezierShape(BezierMixin, FillTriangleMixin, Shape):
    pass

class RoundCornerMixin:
    
    def get_border_points(self) -> str:
        border_points = super().get_border_points()
        return "RoundCornerMixin.get_border_points <- " + border_points

# Порядок наследования важен!
class VisibleRoundCornerShape(FillTriangleMixin, BezierMixin, RoundCornerMixin, Shape):
    ...

s = VisibleRoundCornerShape()
print(s.get_colored_triangles())
