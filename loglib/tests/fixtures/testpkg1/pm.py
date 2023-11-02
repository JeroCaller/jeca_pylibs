import sys

from dirimporttool import get_super_dir_directly

super_dir = get_super_dir_directly(__file__, 3)
sys.path.append(super_dir)

from logpackage import PackageLogger

collector = PackageLogger()


class PlusMinus():
    def __init__(self, num1: int, num2: int):
        """
        두 숫자에 대한 덧셈, 뺼셈 연산을 하는 계산기 클래스. 
        """
        self.num1 = num1
        self.num2 = num2
        collector.logVariable('num2')

    def getSumResult(self, additional_num: int = 0):
        total = 0
        total += self.num1 + self.num2
        self.num2 += additional_num
        collector.logVariable('num2')
        return total

    def getSubtractResult(self, additional_num: int = 0):
        total = 0
        total = self.num1 - self.num2
        self.num2 += additional_num
        collector.logVariable('num2')
        return total
