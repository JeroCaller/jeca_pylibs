from logpackage import PackageLogger, LogFuncEndPoint

collector = PackageLogger()
program_start_end_logger = collector.getInfoLogger('program_start_end_logger')


class PlusMinus():
    def __init__(self, num1: int, num2: int):
        """
        두 숫자에 대한 덧셈, 뺼셈 연산을 하는 계산기 클래스. 
        """
        self.num1 = num1
        self.num2 = num2
        collector.logVariable('num1')

    @LogFuncEndPoint(program_start_end_logger)
    def getSumResult(self, additional_num: int = 0):
        total = 0
        total += self.num1 + self.num2
        self.num2 += additional_num
        collector.logVariable('num1')
        return total
    
    @LogFuncEndPoint(program_start_end_logger)
    def getSubtractResult(self, additional_num: int = 0):
        total = 0
        total = self.num1 - self.num2
        self.num2 += additional_num
        collector.logVariable('num1')
        return total
