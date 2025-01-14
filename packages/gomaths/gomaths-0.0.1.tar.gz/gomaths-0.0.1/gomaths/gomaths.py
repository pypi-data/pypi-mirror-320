from .base import Base


class Calcul(Base):
    def __init__(self):
        super().__init__()
        self.base = Base()

    def AreaSquarre(self, *args):
        """
        s: side
        exemple: calc.AreaSquarre(s)
        :param args: number(int or float or complexe)
        :return: Area of Squarre
        """
        s = args[0]
        return self.base.squarreMeter(s)

    def AreaRectangle(self, *args):
        """
        l: length
        w: width
        exemple: calc.AreaRectangle(l, w)
        :param args: number(int or float or complexe)
        :return: Area of Rectangle
        """
        l = args[0]
        w = args[1]
        return self.base.multiplication(l, w)

    def AreaCircle(self, *args):
        """
        r: radius
        exemple: calc.AreaCircle(r)
        :param args: number(int or float or complexe)
        :return: Area of Circle
        """
        pi = self.pi
        r_squarre = self.base.squarreMeter(args[0])
        return self.base.multiplication(pi, r_squarre)


    def AreaTriangle(self, *args):
        """
        b: base
        h: height
        exemple: calc.AreaCircle(b, h)
        :param args: number(int or float or complexe)
        :return: Area of Circle
        """
        b = args[0]
        h = args[1]
        res = self.base.multiplication(b, h)
        return self.base.division(res, 2)

