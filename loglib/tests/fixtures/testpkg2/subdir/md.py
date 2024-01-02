from logpackage import PackageLogger, LogFuncEndPoint

collector = PackageLogger()
program_start_end_logger = collector.getInfoLogger('program_start_end_logger')


class MultiDivide:
    def __init__(self, num1: int, num2: int):
        """
        주어진 두 숫자에 대해 곱셈, 나눗셈 연산을 하는 클래스. 
        """
        self.num1 = num1
        self.num2 = num2
        collector.logVariable('num2')

    @LogFuncEndPoint(program_start_end_logger)
    def getMultipliedResult(self, additional_num: int = 0):
        total = 1
        total *= self.num1 * self.num2
        self.num1 += additional_num
        collector.logVariable('num2')
        return total
    
    @LogFuncEndPoint(program_start_end_logger)
    def getDividedResult(self, additional_num: int = 0):
        total = 1
        total = self.num1 / self.num2
        self.num1 += additional_num
        collector.logVariable('num2')
        return total
