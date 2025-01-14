class Base:
    def __init__(self):
        self.pi = 3.14


    def addition(self, num1, num2, *args):
        """
        simple addition numbers
        exemple : calc.addition(1, 1, 2)
        :param num1: number(int or float or complexe)
        :param num2: number(int or float or complexe)
        :param args: number(int or float or complexe)
        :return: number(int or float or complexe)
        """
        res = num1 + num2
        for num in args:
            res += num
        return res

    def substraction(self, num1, num2, *args):
        """
        simple substraction numbers
        exemple : calc.substraction(6, 2)
        :param num1: number(int or float or complexe)
        :param num2: number(int or float or complexe)
        :param args: number(int or float or complexe)
        :return: number(int or float or complexe)
        """
        res = num1 - num2
        for num in args:
            res -= num
        return res

    def multiplication(self, num1, num2, *args):
        """
        simple multiplication numbers
        exemple : calc.multiplication(6, 2)
        :param num1: number(int or float or complexe)
        :param num2: number(int or float or complexe)
        :param args: number(int or float or complexe)
        :return: number(int or float or complexe)
        """
        res = num1 * num2
        for num in args:
            res *= num
        return res

    def division(self, num1, num2, *args):
        """
        simple division numbers
        exemple : calc.division(6, 2)
        :param num1: number(int or float or complexe)
        :param num2: number(int or float or complexe)
        :param args: number(int or float or complexe)
        :return: number(int or float or complexe)
        """
        res = num1 / num2
        for num in args:
            res /= num
        return res

    def squarreMeter(self, num):
        """
        simple squarre meter of numbers
        exemple : calc.squarreMeter(3)
        :param num: number(int or float or complexe)
        :return:
        """
        return num ** 2