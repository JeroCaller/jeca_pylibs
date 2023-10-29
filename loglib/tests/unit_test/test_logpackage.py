import unittest
import logging
import sys
from dirimporttool import get_super_dir_directly, get_current_absdir
for i in range(1, 2+1):
    super_dir = get_super_dir_directly(__file__, i)
    sys.path.append(super_dir)

from logpackage import (LogFuncEndPoint, DetectErrorAndLog, 
LoggerPathTree, LoggerHierarchy)
from logexc import LogLowestLevelError

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


class TestLoggerPathTree(unittest.TestCase):
    def setUp(self):
        self.lpt = LoggerPathTree()

    def tearDown(self):
        self.lpt.clear()

    def testEmtpyTree(self):
        self.assertEqual(self.lpt.getRoot(), 'root')
        self.assertEqual(self.lpt.lenTree(), 1)

    def testAppendAbs(self):
        # test 1
        self.lpt.appendAbs('root')
        self.assertEqual(self.lpt.lenTree(), 1)
        self.assertEqual(self.lpt.getAllLeafAbs()[0], 'root')

        # test 2
        self.lpt.appendAbs('a')
        self.assertEqual(self.lpt.lenTree(), 2)
        self.assertEqual(self.lpt.getAllLeafAbs()[0], 'root.a')

        # test 3
        self.lpt.appendAbs('b.c')
        self.assertEqual(self.lpt.lenTree(), 4)
        self.assertIn('root.b.c', self.lpt.getAllLeafAbs())

        # test 4
        self.lpt.appendAbs('root.wow.hello.good')
        self.assertEqual(self.lpt.lenTree(), 7)
        self.assertIn('root.wow.hello.good', self.lpt.getAllLeafAbs())


class TestLoggerHierarchy(unittest.TestCase):
    def setUp(self):
        self.lh = LoggerHierarchy()

    def testLoggerHierarchy(self):
        # test 1
        current_num = 2
        self.assertEqual(self.lh.getNumberofNodes(), current_num)

        # test 2
        logger1 = logging.getLogger('unittest.tlh')
        logger2 = logging.getLogger('test.is.boring')
        self.assertEqual(self.lh.getNumberofNodes(), current_num)
        self.lh.updateLoggerInfo()
        current_num += 5
        self.assertEqual(self.lh.getNumberofNodes(), current_num)
        self.assertIn('root.unittest.tlh', self.lh.getLeafLoggersName())
        self.assertIn('root.test.is.boring', self.lh.getLeafLoggersName())

        # test 3
        logger3 = logging.getLogger('unittest.tlh')
        self.assertEqual(self.lh.getNumberofNodes(), current_num)
        self.assertIn('root.unittest.tlh', self.lh.getLeafLoggersName())


if __name__ == '__main__':
    def test_only_logger_hierarchy():
        suite_obj = unittest.TestSuite()
        suite_obj.addTest(unittest.makeSuite(TestLoggerHierarchy))
        
        runner = unittest.TextTestRunner()
        runner.run(suite_obj)
    
    # 다음 코드들 중 한 줄만 택해 주석해제하여 테스트.
    # (원한다면 모든 코드를 주석 해제하여 테스트해도 됨.)
    #test_only_logger_hierarchy()
    unittest.main()
