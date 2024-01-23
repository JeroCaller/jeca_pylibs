import unittest
import sys
import os
import datetime
import logging

from dirimporttool import (get_super_dir_directly)

for i in range(1, 2+1):
    super_dir = get_super_dir_directly(__file__, i)
    sys.path.append(super_dir)

import helpers  # 특정 테스트 케이스만 실행하고자 할 때 필요.
from logpackage import (EasySetLogFileEnv, LogFileManager)
from logpackage import (LOGGERTREE, LoggerLevel, 
DEFAULT_LEVEL_LOG_FILE_NAMES)
from tools import DateOptions, DateTools
from tests.testdata.testpkg import main

# 특정 테스트케이스를 실행하고자 한다면 여기서 True로 바꾼다.
TEST_ON: bool = False

def get_today_logfile_names() -> (dict[LoggerLevel, str]):
    """로그 수준별 오늘 날짜 문자열이 뒤에 붙은 로그 파일명 반환.

    Returns
    -------
    dict[LoggerLevel, str]

    """
    before = DEFAULT_LEVEL_LOG_FILE_NAMES.copy()
    result = {}
    today_str = datetime.date.today().isoformat()
    for level, filename in before.items():
        name, ext = filename.split('.')
        filename = '_'.join([name, today_str])
        filename = '.'.join([filename, ext])
        result[level] = filename
    return result


class InitLogFileOpt():
    def __init__(
            self, 
            dateopt: DateOptions
        ):
        self.base_dir_location = '..\\testdata\\testpkg'
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
            short_desc: unittest.TestCase.shortDescription
        ):
        if short_desc == 'error_log_mode' and TEST_ON:
            main.mainfunc(self.init_log_env, True, False)
        elif short_desc == 'all_in_one_mode':
            main.mainfunc(
                self.init_log_env_all_in_one, 
                print_result=False
            )
        elif short_desc == 'all_in_one_and_error_log_mode':
            main.mainfunc(
                self.init_log_env_all_in_one, True, False
            )
        else:
            main.mainfunc(self.init_log_env, print_result=False)


class TestLogFileOptionsDay(unittest.TestCase):
    """loglib\\tests\\testdata\\testpkg의 mainfunc 함수 테스트.
    day 모드만 테스트함.
    
    해당 테스트 클래스에서 테스트하고자 하는 것들.
    1. 날짜별 로그 파일 분류가 되고, 로깅도 그에 따라 잘 되는가.
    2. 로그 수준별 파일 분류가 되고, 로깅도 그에 따라 잘 되는가.
    
    """

    def setUp(self):
        self.initsetup = InitLogFileOpt(DateOptions.DAY)

        # mainfunc 다수 호출에 의해 생성될 수 있는 불필요한 로그 기록 방지용.
        self.desc = self.shortDescription()
        self.initsetup.setupForPrevMultiLogs(self.desc)

        self.today_logfile_names = get_today_logfile_names()
    
    def tearDown(self):
        self.logmanager = LogFileManager(self.initsetup.base_dir_path)
        self.logmanager.eraseAllInDateDir(
            os.path.basename(self.initsetup.today_dir_path)
        )

    def testDayBaseDirExists(self):
        """일별 로그 파일 저장 베이스 디렉토리 생성 여부 확인."""
        is_base_dir = os.path.isdir(self.initsetup.base_dir_path)
        self.assertTrue(is_base_dir)

    def testDayDirOfTodayExists(self):
        """일별 로그 파일 저장용 디렉토리 형성 여부 확인.
        (이 코드를 실행하는 오늘 날짜 기준)
        """
        is_today_dir = os.path.isdir(self.initsetup.today_dir_path)
        self.assertTrue(is_today_dir)

    def testLevelLogFilesExist(self):
        """오늘 날짜 디렉토리 내에 로그 수준별 로그 파일들이 
        생성되는지 확인.
        """
        # 테스트 실패 시 정확히 어디서 실패했는지 확인하기
        # 위해 각 로그 수준별로 코드를 분리해서 테스트 코드 설정함.
        debug_path = os.path.join(
            self.initsetup.today_dir_path,
            self.today_logfile_names[logging.DEBUG]
        )
        is_file = os.path.isfile(debug_path)
        self.assertTrue(is_file)

        info_path = os.path.join(
            self.initsetup.today_dir_path,
            self.today_logfile_names[logging.INFO]
        )
        is_file = os.path.isfile(info_path)
        self.assertTrue(is_file)

        error_path = os.path.join(
            self.initsetup.today_dir_path,
            self.today_logfile_names[logging.ERROR]
        )
        is_file = os.path.isfile(error_path)
        self.assertTrue(is_file)

        loggertree_path = os.path.join(
            self.initsetup.today_dir_path,
            self.today_logfile_names[LOGGERTREE]
        )
        is_file = os.path.isfile(loggertree_path)
        self.assertTrue(is_file)

    def testDebugLogFile(self):
        """디버그 파일에 로깅이 되었는지 확인하는 테스트."""
        debug_filepath = os.path.join(
            self.initsetup.today_dir_path,
            self.today_logfile_names[logging.DEBUG]
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
            self.initsetup.today_dir_path,
            self.today_logfile_names[LOGGERTREE]
        )
        with open(logger_tree_filepath, 'r', encoding='utf-8') as f:
            log_data = f.read()
        today = datetime.date.today().isoformat()
        levelname = logging.getLevelName(logging.INFO)
        self.assertIn(today, log_data)
        self.assertIn(levelname, log_data)
        self.assertIn('root', log_data)

    @unittest.skipUnless(TEST_ON, '')
    def testErrorLogFile(self):
        """error_log_mode

        에러 발생 시 에러가 로깅되는지 확인하는 테스트.
        """
        error_filepath = os.path.join(
            self.initsetup.today_dir_path,
            self.today_logfile_names[logging.ERROR]
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
            self.initsetup.today_dir_path,
            self.today_logfile_names[logging.INFO]
        )
        with open(info_filepath, 'r', encoding='utf-8') as f:
            log_data = f.read()
        today = datetime.date.today().isoformat()
        levelname = logging.getLevelName(logging.INFO)
        self.assertIn(today, log_data)
        self.assertIn(levelname, log_data)
        self.assertIn('mainfunc', log_data)


class TestLogFileOptWeek(unittest.TestCase):
    """loglib\\tests\\testdata\\testpkg의 mainfunc 함수 테스트.
    week 모드만 테스트함.

    해당 테스트 클래스에서 테스트하고자 하는 것들.
    1. 주별 로그 파일 분류가 되고, 로깅도 그에 따라 잘 되는가.
    2. 로그 수준별 파일 분류가 되고, 로깅도 그에 따라 잘 되는가.
    """

    def setUp(self):
        self.initsetup = InitLogFileOpt(DateOptions.WEEK)

        # mainfunc 다수 호출에 의해 생성될 수 있는 불필요한 로그 기록 방지용.
        self.desc = self.shortDescription()
        self.initsetup.setupForPrevMultiLogs(self.desc)

        self.today_logfile_names = get_today_logfile_names()

    def tearDown(self):
        self.logmanager = LogFileManager(self.initsetup.base_dir_path)
        for logfile in self.today_logfile_names.values():
            self.logmanager.eraseAllInLogFile(
                os.path.basename(self.initsetup.today_dir_path),
                logfile
            )
        self.logmanager.eraseAllInLogFile(
            os.path.basename(self.initsetup.today_dir_path),
            datetime.date.today().isoformat() + '.log'
        )

    def testWeekBaseDirExists(self):
        """주별 로그 파일 저장 베이스 디렉토리 생성 여부 확인."""
        is_base_dir = os.path.isdir(self.initsetup.base_dir_path)
        self.assertTrue(is_base_dir)

    def testWeekDirOfTodayExists(self):
        """주별 로그 파일 저장용 디렉토리 형성 여부 확인.
        (이 코드를 실행하는 오늘 날짜 기준)
        """
        is_today_dir = os.path.isdir(self.initsetup.today_dir_path)
        self.assertTrue(is_today_dir)

    def testLevelLogFilesExist(self):
        """오늘 날짜 디렉토리 내에 로그 수준별 로그 파일들이 
        생성되는지 확인.
        """
        debug_path = os.path.join(
            self.initsetup.today_dir_path,
            self.today_logfile_names[logging.DEBUG]
        )
        is_file = os.path.isfile(debug_path)
        self.assertTrue(is_file)

        info_path = os.path.join(
            self.initsetup.today_dir_path,
            self.today_logfile_names[logging.INFO]
        )
        is_file = os.path.isfile(info_path)
        self.assertTrue(is_file)

        error_path = os.path.join(
            self.initsetup.today_dir_path,
            self.today_logfile_names[logging.ERROR]
        )
        is_file = os.path.isfile(error_path)
        self.assertTrue(is_file)

        loggertree_path = os.path.join(
            self.initsetup.today_dir_path,
            self.today_logfile_names[LOGGERTREE]
        )
        is_file = os.path.isfile(loggertree_path)
        self.assertTrue(is_file)

    def testDebugLogFile(self):
        """디버그 파일에 로깅이 되었는지 확인하는 테스트."""
        debug_filepath = os.path.join(
            self.initsetup.today_dir_path,
            self.today_logfile_names[logging.DEBUG]
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
            self.initsetup.today_dir_path,
            self.today_logfile_names[LOGGERTREE]
        )
        with open(logger_tree_filepath, 'r', encoding='utf-8') as f:
            log_data = f.read()
        today = datetime.date.today().isoformat()
        levelname = logging.getLevelName(logging.INFO)
        self.assertIn(today, log_data)
        self.assertIn(levelname, log_data)
        self.assertIn('root', log_data)

    @unittest.skipUnless(TEST_ON, '')
    def testErrorLogFile(self):
        """error_log_mode

        에러 발생 시 에러가 로깅되는지 확인하는 테스트.
        """
        error_filepath = os.path.join(
            self.initsetup.today_dir_path,
            self.today_logfile_names[logging.ERROR]
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
            self.initsetup.today_dir_path,
            self.today_logfile_names[logging.INFO]
        )
        with open(info_filepath, 'r', encoding='utf-8') as f:
            log_data = f.read()
        today = datetime.date.today().isoformat()
        levelname = logging.getLevelName(logging.INFO)
        self.assertIn(today, log_data)
        self.assertIn(levelname, log_data)
        self.assertIn('mainfunc', log_data)


class TestLogFileOptMonth(unittest.TestCase):
    """loglib\\tests\\testdata\\testpkg의 mainfunc 함수 테스트.
    month 모드만 테스트함.

    해당 테스트 클래스에서 테스트하고자 하는 것들.
    1. 월별 로그 파일 분류가 되고, 로깅도 그에 따라 잘 되는가.
    2. 로그 수준별 파일 분류가 되고, 로깅도 그에 따라 잘 되는가.
    """

    def setUp(self):
        self.initsetup = InitLogFileOpt(DateOptions.MONTH)

        # mainfunc 다수 호출에 의해 생성될 수 있는 불필요한 로그 기록 방지용.
        self.desc = self.shortDescription()
        self.initsetup.setupForPrevMultiLogs(self.desc)

        self.today_logfile_names = get_today_logfile_names()

    def tearDown(self):
        self.logmanager = LogFileManager(self.initsetup.base_dir_path)
        for logfile in self.today_logfile_names.values():
            self.logmanager.eraseAllInLogFile(
                os.path.basename(self.initsetup.today_dir_path),
                logfile
            )
        self.logmanager.eraseAllInLogFile(
            os.path.basename(self.initsetup.today_dir_path),
            datetime.date.today().isoformat() + '.log'
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
        # 테스트 실패 시 정확히 어디서 실패했는지 확인하기
        # 위해 각 로그 수준별로 코드를 분리해서 테스트 코드 설정함.
        debug_path = os.path.join(
            self.initsetup.today_dir_path,
            self.today_logfile_names[logging.DEBUG]
        )
        is_file = os.path.isfile(debug_path)
        self.assertTrue(is_file)

        info_path = os.path.join(
            self.initsetup.today_dir_path,
            self.today_logfile_names[logging.INFO]
        )
        is_file = os.path.isfile(info_path)
        self.assertTrue(is_file)

        error_path = os.path.join(
            self.initsetup.today_dir_path,
            self.today_logfile_names[logging.ERROR]
        )
        is_file = os.path.isfile(error_path)
        self.assertTrue(is_file)

        loggertree_path = os.path.join(
            self.initsetup.today_dir_path,
            self.today_logfile_names[LOGGERTREE]
        )
        is_file = os.path.isfile(loggertree_path)
        self.assertTrue(is_file)

    def testDebugLogFile(self):
        """디버그 파일에 로깅이 되었는지 확인하는 테스트."""
        debug_filepath = os.path.join(
            self.initsetup.today_dir_path,
            self.today_logfile_names[logging.DEBUG]
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
            self.initsetup.today_dir_path,
            self.today_logfile_names[LOGGERTREE]
        )
        with open(logger_tree_filepath, 'r', encoding='utf-8') as f:
            log_data = f.read()
        today = datetime.date.today().isoformat()
        levelname = logging.getLevelName(logging.INFO)
        self.assertIn(today, log_data)
        self.assertIn(levelname, log_data)
        self.assertIn('root', log_data)

    @unittest.skipUnless(TEST_ON, '')
    def testErrorLogFile(self):
        """error_log_mode

        에러 발생 시 에러가 로깅되는지 확인하는 테스트.
        """
        error_filepath = os.path.join(
            self.initsetup.today_dir_path,
            self.today_logfile_names[logging.ERROR]
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
            self.initsetup.today_dir_path,
            self.today_logfile_names[logging.INFO]
        )
        with open(info_filepath, 'r', encoding='utf-8') as f:
            log_data = f.read()
        today = datetime.date.today().isoformat()
        levelname = logging.getLevelName(logging.INFO)
        self.assertIn(today, log_data)
        self.assertIn(levelname, log_data)
        self.assertIn('mainfunc', log_data)


class TestLogFileOptYear(unittest.TestCase):
    """loglib\\tests\\testdata\\testpkg의 mainfunc 함수 테스트.
    year 모드만 테스트함.

    해당 테스트 클래스에서 테스트하고자 하는 것들.
    1. 연별 로그 파일 분류가 되고, 로깅도 그에 따라 잘 되는가.
    2. 로그 수준별 파일 분류가 되고, 로깅도 그에 따라 잘 되는가.
    """

    def setUp(self):
        self.initsetup = InitLogFileOpt(DateOptions.YEAR)

        # mainfunc 다수 호출에 의해 생성될 수 있는 불필요한 로그 기록 방지용.
        self.desc = self.shortDescription()
        self.initsetup.setupForPrevMultiLogs(self.desc)

        self.today_logfile_names = get_today_logfile_names()

    def tearDown(self):
        self.logmanager = LogFileManager(self.initsetup.base_dir_path)
        for logfile in self.today_logfile_names.values():
            self.logmanager.eraseAllInLogFile(
                os.path.basename(self.initsetup.today_dir_path),
                logfile
            )
        self.logmanager.eraseAllInLogFile(
            os.path.basename(self.initsetup.today_dir_path),
            datetime.date.today().isoformat() + '.log'
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
        # 테스트 실패 시 정확히 어디서 실패했는지 확인하기
        # 위해 각 로그 수준별로 코드를 분리해서 테스트 코드 설정함.
        debug_path = os.path.join(
            self.initsetup.today_dir_path,
            self.today_logfile_names[logging.DEBUG]
        )
        is_file = os.path.isfile(debug_path)
        self.assertTrue(is_file)

        info_path = os.path.join(
            self.initsetup.today_dir_path,
            self.today_logfile_names[logging.INFO]
        )
        is_file = os.path.isfile(info_path)
        self.assertTrue(is_file)

        error_path = os.path.join(
            self.initsetup.today_dir_path,
            self.today_logfile_names[logging.ERROR]
        )
        is_file = os.path.isfile(error_path)
        self.assertTrue(is_file)

        loggertree_path = os.path.join(
            self.initsetup.today_dir_path,
            self.today_logfile_names[LOGGERTREE]
        )
        is_file = os.path.isfile(loggertree_path)
        self.assertTrue(is_file)

    def testDebugLogFile(self):
        """디버그 파일에 로깅이 되었는지 확인하는 테스트."""
        debug_filepath = os.path.join(
            self.initsetup.today_dir_path,
            self.today_logfile_names[logging.DEBUG]
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
            self.initsetup.today_dir_path,
            self.today_logfile_names[LOGGERTREE]
        )
        with open(logger_tree_filepath, 'r', encoding='utf-8') as f:
            log_data = f.read()
        today = datetime.date.today().isoformat()
        levelname = logging.getLevelName(logging.INFO)
        self.assertIn(today, log_data)
        self.assertIn(levelname, log_data)
        self.assertIn('root', log_data)

    @unittest.skipUnless(TEST_ON, '')
    def testErrorLogFile(self):
        """error_log_mode

        에러 발생 시 에러가 로깅되는지 확인하는 테스트.
        """
        error_filepath = os.path.join(
            self.initsetup.today_dir_path,
            self.today_logfile_names[logging.ERROR]
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
            self.initsetup.today_dir_path,
            self.today_logfile_names[logging.INFO]
        )
        with open(info_filepath, 'r', encoding='utf-8') as f:
            log_data = f.read()
        today = datetime.date.today().isoformat()
        levelname = logging.getLevelName(logging.INFO)
        self.assertIn(today, log_data)
        self.assertIn(levelname, log_data)
        self.assertIn('mainfunc', log_data)


if __name__ == '__main__':
    @helpers.WorkCWD(__file__)
    def exec_test():
        # 다음 코드들 중 한 줄만 택해 주석해제하여 테스트.
        # (원한다면 모든 코드를 주석 해제하여 테스트해도 됨.)
        unittest.main()
        #helpers.test_only_one(TestLogFileOptionsDay)
        #helpers.test_only_one(TestLogFileOptWeek)
        #helpers.test_only_one(TestLogFileOptMonth)
        #helpers.test_only_one(TestLogFileOptYear)

        # 각 케이스에 대해 따로 테스트하고자 할 때, unittest.main() 줄은 주석처리한 후,
        # 원하는 줄만 주석해제 하여 실행하면 된다.
        #helpers.test_only_one(TestLogFileOptionsDay)
        #helpers.test_only_one(TestLogFileOptWeek)
        #helpers.test_only_one(TestLogFileOptMonth)
        #helpers.test_only_one(TestLogFileOptYear)

    exec_test()
    