import unittest
import logging
import sys
import datetime
import os

from dirimporttool import (get_super_dir_directly,
get_current_absdir)

for i in range(1, 2+1):
    super_dir = get_super_dir_directly(__file__, i)
    sys.path.append(super_dir)

from logpackage import (LogFuncEndPoint, DetectErrorAndLog,
_LoggerPathTree, _LoggerHierarchy, CustomizablePackageLogger, 
EasySetLogFileEnv)
from logexc import LogLowestLevelError
from tools import DateOptions, DateTools
from tests.fixtures.testpkg3 import main

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
        return None
    return data

def get_fixture_logger(
        logger_name: str | None = None,
        level: int = logging.DEBUG
    ) -> (logging.Logger):
    """테스트용 로거 객체 생성 및 설정 함수."""
    if logger_name is None:
        logger_name = 'test_log'
    fixture_logger = logging.getLogger(logger_name)
    fixture_logger.setLevel(level)
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
    fixture_logger.addHandler(file_handler)
    return fixture_logger


class TestLogDecor(unittest.TestCase):
    def setUp(self):
        self.logger = get_fixture_logger('test_log', logging.DEBUG)

    def tearDown(self):
        self.logger.setLevel(logging.DEBUG)
        # 로그 파일 내 내용 리셋.
        with open(LOGFILE, 'w', encoding='utf-8'): pass

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
                return data
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
        self.lpt = _LoggerPathTree()

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
        self.lh = _LoggerHierarchy()

    @unittest.skip("""외부 fixture 패키지 임포트하여 테스트 시도 시 
    이 메서드를 스킵해야 예외 상황 발생하지 않음.
    """)
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


class InitLogFileOpt():
    def __init__(
            self, 
            dateopt: DateOptions
        ):
        self.base_dir_location = '..\\fixtures\\testpkg3'
        if dateopt == DateOptions.DAY:
            self.base_dir_name_date = 'logfiles_day'
        elif dateopt == DateOptions.WEEK:
            self.base_dir_name_date = 'logfiles_week'
        elif dateopt == DateOptions.MONTH:
            self.base_dir_name_date = 'logfiles_month'
        elif dateopt == DateOptions.YEAR:
            self.base_dir_name_date = 'logfiles_year'
        else:
            self.base_dir_name_date = ''
        self.base_dir_path = os.path.join(
            self.base_dir_location, self.base_dir_name_date
        )
        self.today_dir_path = os.path.join(
            self.base_dir_path,
            DateTools().getDateStr(dateopt, True)
        )

        self.init_log_env = EasySetLogFileEnv()
        self.init_log_env.setEssentialLogEnv(
            base_dir=self.base_dir_location,
            base_dir_name=self.base_dir_name_date,
            level_option=True,
            date_opt=dateopt
        )
        self.init_log_env_all_in_one = EasySetLogFileEnv()
        self.init_log_env_all_in_one.setEssentialLogEnv(
            base_dir=self.base_dir_location,
            base_dir_name=self.base_dir_name_date,
            level_option=False,
            date_opt=dateopt
        )

    def setupForPrevMultiLogs(
            self,
            test_classname: unittest.TestCase,
            short_desc: unittest.TestCase.shortDescription
        ):
        if short_desc == 'error_log_mode':
            if not test_classname.main_error_mode_called:
                main.mainfunc(self.init_log_env, True, False)
                test_classname.main_error_mode_called = True
        elif short_desc == 'all_in_one_mode':
            if not test_classname.all_in_one_mode_called:
                main.mainfunc(
                    self.init_log_env_all_in_one, 
                    print_result=False
                )
                test_classname.all_in_one_mode_called = True
        elif short_desc == 'all_in_one_and_error_log_mode':
            if not test_classname.all_in_one_and_error_mode_called:
                main.mainfunc(
                    self.init_log_env_all_in_one, True, False
                )
                test_classname.all_in_one_and_error_mode_called = True
        else:
            if not test_classname.main_called:
                main.mainfunc(self.init_log_env, print_result=False)
                test_classname.main_called = True


class TestLogFileOptionsDay(unittest.TestCase):
    """loglib\\tests\\fixtures\\testpkg3의 mainfunc 함수 테스트.
    day 모드만 테스트함.
    
    해당 테스트 클래스에서 테스트하고자 하는 것들.
    1. 날짜별 로그 파일 분류가 되고, 로깅도 그에 따라 잘 되는가.
    2. 로그 수준별 파일 분류가 되고, 로깅도 그에 따라 잘 되는가.
    
    """
    main_called: bool = False
    main_error_mode_called: bool = False
    all_in_one_and_error_mode_called: bool = False
    all_in_one_mode_called: bool = False

    def setUp(self):
        self.initsetup = InitLogFileOpt(DateOptions.DAY)

        # mainfunc 다수 호출에 의해 생성될 수 있는 불필요한 로그 기록 방지용.
        self.desc = self.shortDescription()
        self.initsetup.setupForPrevMultiLogs(
            TestLogFileOptionsDay,
            self.desc
        )

    def testDayBaseDirExists(self):
        """일별 로그 파일 저장 베이스 디렉토리 생성 여부 확인."""
        is_base_dir = os.path.isdir(self.initsetup.base_dir_path)
        self.assertTrue(is_base_dir)

    def testDayDirOfTodayExists(self):
        """일별 로그 파일 저장용 디렉토리 형성 여부 확인.
        (이 코드를 실행하는 오늘 날짜 기준)
        """
        today_date = datetime.date.today()
        today_date = today_date.isoformat()
        is_today_dir = os.path.isdir(
            os.path.join(self.initsetup.base_dir_path, today_date)
        )
        self.assertTrue(is_today_dir)

    def testLevelLogFilesExist(self):
        """오늘 날짜 디렉토리 내에 로그 수준별 로그 파일들이 
        생성되는지 확인.
        """
        filename_list = [
            'debug.log', 'error.log',
            'info.log', 'logger_tree.log'
        ]

        def test_level_log_file(fnames: list[str]):
            for f_name in fnames:
                filepath = os.path.join(self.initsetup.today_dir_path, f_name)
                is_file = os.path.isfile(filepath)
                self.assertTrue(is_file)

        test_level_log_file(filename_list)

    def testDebugLogFile(self):
        """디버그 파일에 로깅이 되었는지 확인하는 테스트."""
        debug_filepath = os.path.join(
            self.initsetup.today_dir_path, 'debug.log'
        )
        with open(debug_filepath, 'r', encoding='utf-8') as f:
            log_data = f.readlines()
        today = datetime.date.today().isoformat()
        debug_level = logging.getLevelName(logging.DEBUG)
        self.assertIn(today, log_data[0])
        self.assertIn(debug_level, log_data[0])
        self.assertIn('variable', log_data[2])

    def testLoggerTreeLogFile(self):
        """logger_tree.log 파일에 로깅이 되었는지 테스트."""
        logger_tree_filepath = os.path.join(
            self.initsetup.today_dir_path, 'logger_tree.log'
        )
        with open(logger_tree_filepath, 'r', encoding='utf-8') as f:
            log_data = f.readlines()
        today = datetime.date.today().isoformat()
        levelname = logging.getLevelName(logging.INFO)
        self.assertIn(today, log_data[0])
        self.assertIn(levelname, log_data[0])
        self.assertIn('root', log_data[1])

    @unittest.skip('')
    def testErrorLogFile(self):
        """error_log_mode

        에러 발생 시 에러가 로깅되는지 확인하는 테스트.
        """
        error_filepath = os.path.join(
            self.initsetup.today_dir_path, 'error.log'
        )
        with open(error_filepath, 'r', encoding='utf-8') as f:
            log_data = f.readlines()
        today = datetime.date.today().isoformat()
        levelname = logging.getLevelName(logging.ERROR)
        self.assertIn(today, log_data[0])
        self.assertIn(levelname, log_data[0])
        self.assertIn('division by zero', log_data[1])

    def testInfoLogFile(self):
        """Info 로깅 여부 확인 테스트."""
        info_filepath = os.path.join(
            self.initsetup.today_dir_path, 'info.log'
        )
        with open(info_filepath, 'r', encoding='utf-8') as f:
            log_data = f.readlines()
        today = datetime.date.today().isoformat()
        levelname = logging.getLevelName(logging.INFO)
        self.assertIn(today, log_data[0])
        self.assertIn(levelname, log_data[0])
        self.assertIn('mainfunc', log_data[1])


class TestLogFileOptWeek(unittest.TestCase):
    """loglib\\tests\\fixtures\\testpkg3의 mainfunc 함수 테스트.
    week 모드만 테스트함.

    해당 테스트 클래스에서 테스트하고자 하는 것들.
    1. 주별 로그 파일 분류가 되고, 로깅도 그에 따라 잘 되는가.
    2. 로그 수준별 파일 분류가 되고, 로깅도 그에 따라 잘 되는가.
    """
    main_called: bool = False
    main_error_mode_called: bool = False
    all_in_one_and_error_mode_called: bool = False
    all_in_one_mode_called: bool = False

    def setUp(self):
        self.initsetup = InitLogFileOpt(DateOptions.WEEK)

        # mainfunc 다수 호출에 의해 생성될 수 있는 불필요한 로그 기록 방지용.
        self.desc = self.shortDescription()
        self.initsetup.setupForPrevMultiLogs(
            TestLogFileOptWeek,
            self.desc
        )

    def testWeekBaseDirExists(self):
        """주별 로그 파일 저장 베이스 디렉토리 생성 여부 확인."""
        is_base_dir = os.path.isdir(self.initsetup.base_dir_path)
        self.assertTrue(is_base_dir)

    def testWeekDirOfTodayExists(self):
        """일별 로그 파일 저장용 디렉토리 형성 여부 확인.
        (이 코드를 실행하는 오늘 날짜 기준)
        """
        is_today_dir = os.path.isdir(self.initsetup.today_dir_path)
        self.assertTrue(is_today_dir)

    def testLevelLogFilesExist(self):
        """오늘 날짜 디렉토리 내에 로그 수준별 로그 파일들이 
        생성되는지 확인.
        """
        filename_list = [
            'debug.log', 'error.log',
            'info.log', 'logger_tree.log'
        ]

        def test_level_log_file(fnames: list[str]):
            for f_name in fnames:
                filepath = os.path.join(self.initsetup.today_dir_path, f_name)
                is_file = os.path.isfile(filepath)
                self.assertTrue(is_file)

        test_level_log_file(filename_list)

    def testDebugLogFile(self):
        """디버그 파일에 로깅이 되었는지 확인하는 테스트."""
        debug_filepath = os.path.join(
            self.initsetup.today_dir_path, 'debug.log'
        )
        with open(debug_filepath, 'r', encoding='utf-8') as f:
            log_data = f.read()
        today = datetime.date.today().isoformat()
        debug_level = logging.getLevelName(logging.DEBUG)
        self.assertIn(today, log_data)
        self.assertIn(debug_level, log_data)
        self.assertIn('variable', log_data)

    def testLoggerTreeLogFile(self):
        """logger_tree.log 파일에 로깅이 되었는지 테스트."""
        logger_tree_filepath = os.path.join(
            self.initsetup.today_dir_path, 'logger_tree.log'
        )
        with open(logger_tree_filepath, 'r', encoding='utf-8') as f:
            log_data = f.read()
        today = datetime.date.today().isoformat()
        levelname = logging.getLevelName(logging.INFO)
        self.assertIn(today, log_data)
        self.assertIn(levelname, log_data)
        self.assertIn('root', log_data)

    @unittest.skip('')
    def testErrorLogFile(self):
        """error_log_mode

        에러 발생 시 에러가 로깅되는지 확인하는 테스트.
        """
        error_filepath = os.path.join(
            self.initsetup.today_dir_path, 'error.log'
        )
        with open(error_filepath, 'r', encoding='utf-8') as f:
            log_data = f.read()
        today = datetime.date.today().isoformat()
        levelname = logging.getLevelName(logging.ERROR)
        self.assertIn(today, log_data)
        self.assertIn(levelname, log_data)
        self.assertIn('division by zero', log_data)

    def testInfoLogFile(self):
        """Info 로깅 여부 확인 테스트."""
        info_filepath = os.path.join(
            self.initsetup.today_dir_path, 'info.log'
        )
        with open(info_filepath, 'r', encoding='utf-8') as f:
            log_data = f.read()
        today = datetime.date.today().isoformat()
        levelname = logging.getLevelName(logging.INFO)
        self.assertIn(today, log_data)
        self.assertIn(levelname, log_data)
        self.assertIn('mainfunc', log_data)


class TestLogFileOptMonth(unittest.TestCase):
    """loglib\\tests\\fixtures\\testpkg3의 mainfunc 함수 테스트.
    month 모드만 테스트함.

    해당 테스트 클래스에서 테스트하고자 하는 것들.
    1. 월별 로그 파일 분류가 되고, 로깅도 그에 따라 잘 되는가.
    2. 로그 수준별 파일 분류가 되고, 로깅도 그에 따라 잘 되는가.
    """
    main_called: bool = False
    main_error_mode_called: bool = False
    all_in_one_and_error_mode_called: bool = False
    all_in_one_mode_called: bool = False

    def setUp(self):
        self.initsetup = InitLogFileOpt(DateOptions.MONTH)

        # mainfunc 다수 호출에 의해 생성될 수 있는 불필요한 로그 기록 방지용.
        self.desc = self.shortDescription()
        self.initsetup.setupForPrevMultiLogs(
            TestLogFileOptMonth,
            self.desc
        )

    def testMonthBaseDirExists(self):
        """월별 로그 파일 저장 베이스 디렉토리 생성 여부 확인."""
        is_base_dir = os.path.isdir(self.initsetup.base_dir_path)
        self.assertTrue(is_base_dir)

    def testMonthDirOfTodayExists(self):
        """월별 로그 파일 저장용 디렉토리 형성 여부 확인.
        (이 코드를 실행하는 오늘 날짜 기준)
        """
        is_today_dir = os.path.isdir(self.initsetup.today_dir_path)
        self.assertTrue(is_today_dir)

    def testLevelLogFilesExist(self):
        """오늘 날짜 디렉토리 내에 로그 수준별 로그 파일들이 
        생성되는지 확인.
        """
        filename_list = [
            'debug.log', 'error.log',
            'info.log', 'logger_tree.log'
        ]

        def test_level_log_file(fnames: list[str]):
            for f_name in fnames:
                filepath = os.path.join(self.initsetup.today_dir_path, f_name)
                is_file = os.path.isfile(filepath)
                self.assertTrue(is_file)

        test_level_log_file(filename_list)

    def testDebugLogFile(self):
        """디버그 파일에 로깅이 되었는지 확인하는 테스트."""
        debug_filepath = os.path.join(
            self.initsetup.today_dir_path, 'debug.log'
        )
        with open(debug_filepath, 'r', encoding='utf-8') as f:
            log_data = f.read()
        today = datetime.date.today().isoformat()
        debug_level = logging.getLevelName(logging.DEBUG)
        self.assertIn(today, log_data)
        self.assertIn(debug_level, log_data)
        self.assertIn('variable', log_data)

    def testLoggerTreeLogFile(self):
        """logger_tree.log 파일에 로깅이 되었는지 테스트."""
        logger_tree_filepath = os.path.join(
            self.initsetup.today_dir_path, 'logger_tree.log'
        )
        with open(logger_tree_filepath, 'r', encoding='utf-8') as f:
            log_data = f.read()
        today = datetime.date.today().isoformat()
        levelname = logging.getLevelName(logging.INFO)
        self.assertIn(today, log_data)
        self.assertIn(levelname, log_data)
        self.assertIn('root', log_data)

    @unittest.skip('')
    def testErrorLogFile(self):
        """error_log_mode

        에러 발생 시 에러가 로깅되는지 확인하는 테스트.
        """
        error_filepath = os.path.join(
            self.initsetup.today_dir_path, 'error.log'
        )
        with open(error_filepath, 'r', encoding='utf-8') as f:
            log_data = f.read()
        today = datetime.date.today().isoformat()
        levelname = logging.getLevelName(logging.ERROR)
        self.assertIn(today, log_data)
        self.assertIn(levelname, log_data)
        self.assertIn('division by zero', log_data)

    def testInfoLogFile(self):
        """Info 로깅 여부 확인 테스트."""
        info_filepath = os.path.join(
            self.initsetup.today_dir_path, 'info.log'
        )
        with open(info_filepath, 'r', encoding='utf-8') as f:
            log_data = f.read()
        today = datetime.date.today().isoformat()
        levelname = logging.getLevelName(logging.INFO)
        self.assertIn(today, log_data)
        self.assertIn(levelname, log_data)
        self.assertIn('mainfunc', log_data)


class TestLogFileOptYear(unittest.TestCase):
    """loglib\\tests\\fixtures\\testpkg3의 mainfunc 함수 테스트.
    year 모드만 테스트함.

    해당 테스트 클래스에서 테스트하고자 하는 것들.
    1. 연별 로그 파일 분류가 되고, 로깅도 그에 따라 잘 되는가.
    2. 로그 수준별 파일 분류가 되고, 로깅도 그에 따라 잘 되는가.
    """
    main_called: bool = False
    main_error_mode_called: bool = False
    all_in_one_and_error_mode_called: bool = False
    all_in_one_mode_called: bool = False

    def setUp(self):
        self.initsetup = InitLogFileOpt(DateOptions.YEAR)

        # mainfunc 다수 호출에 의해 생성될 수 있는 불필요한 로그 기록 방지용.
        self.desc = self.shortDescription()
        self.initsetup.setupForPrevMultiLogs(
            TestLogFileOptYear,
            self.desc
        )

    def testYearBaseDirExists(self):
        """연별 로그 파일 저장 베이스 디렉토리 생성 여부 확인."""
        is_base_dir = os.path.isdir(self.initsetup.base_dir_path)
        self.assertTrue(is_base_dir)

    def testYearDirOfTodayExists(self):
        """연별 로그 파일 저장용 디렉토리 형성 여부 확인.
        (이 코드를 실행하는 오늘 날짜 기준)
        """
        is_today_dir = os.path.isdir(self.initsetup.today_dir_path)
        self.assertTrue(is_today_dir)

    def testLevelLogFilesExist(self):
        """오늘 날짜 디렉토리 내에 로그 수준별 로그 파일들이 
        생성되는지 확인.
        """
        filename_list = [
            'debug.log', 'error.log',
            'info.log', 'logger_tree.log'
        ]

        def test_level_log_file(fnames: list[str]):
            for f_name in fnames:
                filepath = os.path.join(self.initsetup.today_dir_path, f_name)
                is_file = os.path.isfile(filepath)
                self.assertTrue(is_file)

        test_level_log_file(filename_list)

    def testDebugLogFile(self):
        """디버그 파일에 로깅이 되었는지 확인하는 테스트."""
        debug_filepath = os.path.join(
            self.initsetup.today_dir_path, 'debug.log'
        )
        with open(debug_filepath, 'r', encoding='utf-8') as f:
            log_data = f.read()
        today = datetime.date.today().isoformat()
        debug_level = logging.getLevelName(logging.DEBUG)
        self.assertIn(today, log_data)
        self.assertIn(debug_level, log_data)
        self.assertIn('variable', log_data)

    def testLoggerTreeLogFile(self):
        """logger_tree.log 파일에 로깅이 되었는지 테스트."""
        logger_tree_filepath = os.path.join(
            self.initsetup.today_dir_path, 'logger_tree.log'
        )
        with open(logger_tree_filepath, 'r', encoding='utf-8') as f:
            log_data = f.read()
        today = datetime.date.today().isoformat()
        levelname = logging.getLevelName(logging.INFO)
        self.assertIn(today, log_data)
        self.assertIn(levelname, log_data)
        self.assertIn('root', log_data)

    @unittest.skip('')
    def testErrorLogFile(self):
        """error_log_mode

        에러 발생 시 에러가 로깅되는지 확인하는 테스트.
        """
        error_filepath = os.path.join(
            self.initsetup.today_dir_path, 'error.log'
        )
        with open(error_filepath, 'r', encoding='utf-8') as f:
            log_data = f.read()
        today = datetime.date.today().isoformat()
        levelname = logging.getLevelName(logging.ERROR)
        self.assertIn(today, log_data)
        self.assertIn(levelname, log_data)
        self.assertIn('division by zero', log_data)

    def testInfoLogFile(self):
        """Info 로깅 여부 확인 테스트."""
        info_filepath = os.path.join(
            self.initsetup.today_dir_path, 'info.log'
        )
        with open(info_filepath, 'r', encoding='utf-8') as f:
            log_data = f.read()
        today = datetime.date.today().isoformat()
        levelname = logging.getLevelName(logging.INFO)
        self.assertIn(today, log_data)
        self.assertIn(levelname, log_data)
        self.assertIn('mainfunc', log_data)


if __name__ == '__main__':
    def test_only_logger_hierarchy():
        suite_obj = unittest.TestSuite()
        suite_obj.addTest(unittest.makeSuite(TestLoggerHierarchy))

        runner = unittest.TextTestRunner()
        runner.run(suite_obj)

    def test_only_one_logopt_date(test_classname):
        suite_obj = unittest.TestSuite()
        suite_obj.addTest(unittest.makeSuite(test_classname))

        runner = unittest.TextTestRunner()
        runner.run(suite_obj)

    # 다음 코드들 중 한 줄만 택해 주석해제하여 테스트.
    # (원한다면 모든 코드를 주석 해제하여 테스트해도 됨.)
    #test_only_logger_hierarchy()
    unittest.main()
    #test_only_one_logopt_date(TestLogFileOptionsDay)
    #test_only_one_logopt_date(TestLogFileOptWeek)
    #test_only_one_logopt_date(TestLogFileOptMonth)
    #test_only_one_logopt_date(TestLogFileOptYear)