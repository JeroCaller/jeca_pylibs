import unittest
import logging
import sys
from dirimporttool import get_super_dir_directly, get_current_absdir
for i in range(1, 2+1):
    super_dir = get_super_dir_directly(__file__, i)
    sys.path.append(super_dir)

from logpackage import (LogFuncEndPoint, DetectErrorAndLog, LoggerWHT)
from logexp import LogLowestLevelError

LOGFILE = "\\".join([get_current_absdir(__file__), 'test_log.log'])

def get_log_data(filename: str = LOGFILE) -> (str | None):
    """
    주어진 로그 파일 주소로부터 해당 로그 파일 내 텍스트를 읽어들여 
    이를 반환. 
    """
    try:
        with open(filename, 'r', encoding='utf-8') as logfile:
            data = logfile.read()
    except FileNotFoundError:
        print("Error from function get_log_data.")
        print("해당 로그 파일을 찾지 못했습니다.")
        return
    else:
        return data


class TestLogDecor(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger('test_log')
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s:\n%(message)s"
        )
        file_handler = logging.FileHandler(
            filename=LOGFILE,
            mode='w',
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def tearDown(self):
        self.logger.setLevel(logging.DEBUG)
        # 로그 파일 내 내용 리셋.
        with open(LOGFILE, 'w'): pass

    def testLogFuncEndPointError(self):
        """
        Logger 객체의 최소 수준을 잘못 설정했을 때 예측되는 
        예외를 발생시키는지 테스트.
        """
        self.logger.setLevel(logging.WARNING)

        with self.assertRaises(LogLowestLevelError):
            @LogFuncEndPoint(self.logger)
            def calculator(a: int, b: int):
                four_arithmetics = {
                    'sum': a + b,
                    'sub': a - b,
                    'mul': a * b,
                    'div': a / b,
                }
                return four_arithmetics
            
            calculator(4, 2)
        
        log_data = get_log_data()
        self.assertEqual(log_data, "")
        self.assertNotIn("INFO", log_data)

    def testLogFuncEndPointNormal(self):
        """
        Logger 객체의 최소 수준을 적절히 설정했을 때 
        로깅이 잘되는지 테스트.
        """
        self.logger.setLevel(logging.DEBUG)

        @LogFuncEndPoint(self.logger)
        def calculator(a: int, b: int):
            four_arithmetics = {
                'sum': a + b,
                'sub': a - b,
                'mul': a * b,
                'div': a / b,
            }
            return four_arithmetics
        
        calculator(4, 2)
        log_data = get_log_data()
        self.assertNotEqual(log_data, "")
        self.assertIn('INFO', log_data)

    def testDetectErrorAndLog(self):
        @DetectErrorAndLog(self.logger)
        def some_error_func():
            return 1 / 0
        
        some_error_func()
        
        log_data = get_log_data()
        #print(log_data)
        self.assertIn("ERROR", log_data)

    def testDetectErrorAndLogFromDeep(self):
        """
        어떤 함수 내부의 함수에서 에러가 나도 예외 로깅이 
        되는지 테스트.
        """
        @DetectErrorAndLog(self.logger)
        def outer_func():
            def inner_func():
                data = int('hi')
                return 'hi'
            return inner_func()
        
        outer_func()

        log_data = get_log_data()
        #print(log_data)
        self.assertIn('ERROR', log_data)

    def testDetectErrorAndLogError(self):
        """
        DetectErrorAndLogError 데코레이터 사용 시 
        발생할 수 있는 예외 테스트.
        """
        self.logger.setLevel(logging.CRITICAL)

        # test 1
        with self.assertRaises(LogLowestLevelError):
            @DetectErrorAndLog(self.logger)
            def some_error_func():
                return 1 / 0
        
            some_error_func()

        # test 2
        # 예외가 발생하지 않을 거라 예측되는 테스트.
        self.logger.setLevel(logging.ERROR)
        @DetectErrorAndLog(self.logger)
        def some_error_func():
            return 1 / 0
        
        some_error_func()
        log_data = get_log_data()
        #print(log_data)
        self.assertIn("ERROR", log_data)


class TestLoggerWHT(unittest.TestCase):
    def testLoggerTree(self):
        """
        LoggerWHT 클래스를 이용하여 logging.Logger처럼 
        새 로거 객체 이름을 생성할 경우 
        LoggerTree() 클래스에 로거 트리가 형성되는지 테스트. 
        """
        logger_a = LoggerWHT('a')
        logger_b = LoggerWHT('a.b')
        logger_c = LoggerWHT('a.b.a.c')
        self.assertEqual(LoggerWHT.logtree.lenTree(), 4)
        self.assertEqual(
            LoggerWHT.logtree.getAllLeafAbs(),
            ['a.b.a.c']
        )
        LoggerWHT().clear()
        self.assertEqual(LoggerWHT.logtree.lenTree(), 0)
        self.assertEqual(LoggerWHT.logtree.getRoot(), '<root>')


if __name__ == '__main__':
    unittest.main()