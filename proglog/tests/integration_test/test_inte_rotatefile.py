"""로그 파일 용량에 따른 자동 rotation 기능 테스트.

testdata\\testpkg2 를 이용함.

"""
import unittest
import sys
import os
import re

from dirimporttool import get_super_dir_directly

for i in range(1, 2+1):
    super_dir = get_super_dir_directly(__file__, i)
    sys.path.append(super_dir)

import helpers
from logpackage import EasySetLogFileEnv
from tools import DateOptions, DateTools
from sub_modules.dirsearch import get_all_in_rootdir
from tests.testdata.testpkg2.main import mainfunc

# 전역 상수 정의
TEST_ON: bool = False

def extract_info(filename: str) -> (tuple[str, str, int, str]):
    """주어진 파일 이름으로부터 
    로그 수준, 로그 날짜, rotated된 로그 파일 번호, 확장자
    정보를 반환한다. 
    단, 인식되지 않은 정보는 각각 None으로 표기된다.
    (단, 로그 파일 번호가 없을 경우 0으로 표기됨)

    ex1) 'debug_2023-12-18 (1).log'
    -> ['debug', '2023-12-18', 1, '.log']

    ex2) 'wow_2023-12-18.log'
    -> [None, '2023-12-18', 0, '.log']
    """
    result = [None] * 4
    dopt = DateOptions()
    dtool = DateTools()

    name, ext = os.path.splitext(filename)
    if ext:
        result[-1] = ext
    
    log_levels = ['debug', 'info', 'error', 'logger_tree']
    for lev in log_levels:
        if lev in name:
            result[0] = lev
            break
    
    # 정해진 날짜 형식을 가지는 날짜 문자열이 존재하는지 검사.
    date_pat = {
        dopt.DAY: '\d+-\d+-\d+',
        dopt.WEEK: '\d+-\d+-\d+[주]',
        dopt.MONTH: '\d+-\d+',
        dopt.YEAR: '\d+',
    }
    for pat in date_pat.values():
        mat = re.search(pat, name)
        if mat and dtool.isDateStr(mat.group()):
            result[1] = mat.group()
            break
    
    mat = re.search('\([0-9]+\)', name)
    if mat:
        res = mat.group().replace('(', '').replace(')', '')
        result[2] = int(res)
    
    return tuple(result)

def process_data(data: list[tuple]) -> (dict[str, int]):
    # { log_level + date (str): num }
    result = {}
    for level, date, num, _ in data:
        base_file_name = '=>'.join([level, date])
        if base_file_name not in result:
            if num is None:
                result[base_file_name] = 0
            else:
                result[base_file_name] = num
        elif num is not None and result[base_file_name] < num:
            result[base_file_name] = num
    return result


class InitLogFileOpt():
    def __init__(
            self,
            dateopt: DateOptions,
            **handler_kwargs
        ):
        self.base_dir_location = '..\\testdata\\testpkg2'
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

        self.init_log_env = EasySetLogFileEnv()
        self.init_log_env.setCustomRotatingFileHandler(
            **handler_kwargs
        )
        self.init_log_env.setEssentialLogEnv(
            base_dir=self.base_dir_location,
            base_dir_name=self.base_dir_name_date,
            level_option=True,
            date_opt=dateopt
        )

        self.basedir = self.init_log_env.base_dir # 외부 이용 용도.
        self.today_dir_path = os.path.join(
            self.base_dir_path,
            DateTools().getDateStr(dateopt, True)
        )

    def setupForPrevMultiLogs(
            self,
            test_classname: unittest.TestCase,
            short_desc: unittest.TestCase.shortDescription
        ):
        if short_desc == 'error_log_mode' and TEST_ON:
            if not test_classname.main_error_mode_called:
                mainfunc(self.init_log_env, True, False)
                test_classname.main_error_mode_called = True
        else:
            if not test_classname.main_called:
                mainfunc(self.init_log_env, print_result=False)
                test_classname.main_called = True


class TestRotateLogFileDay(unittest.TestCase):
    """CustomRotatingFileHandler()에 따라 잘 작동되는지 확인하는 테스트."""
    main_called: bool = False
    main_error_mode_called: bool = False

    def setUp(self):
        self.backup_count = 3
        self.initsetup = InitLogFileOpt(
            DateOptions.DAY,
            maxBytes=30, backupCount=self.backup_count, encoding='utf-8'
        )

        self.desc = self.shortDescription()
        self.initsetup.setupForPrevMultiLogs(
            TestRotateLogFileDay, self.desc
        )

    def testIfRotate(self):
        all_files = get_all_in_rootdir(self.initsetup.today_dir_path, False)
        files_info: list[tuple[str, str, int, str]] = []
        for file in all_files:
            filename = os.path.basename(file)
            files_info.append(extract_info(filename))

        for tup in files_info:
            self.assertEqual(tup[-1], '.log')  # 모두 '.log' 확장자를 가지는 파일인가?

        data = process_data(files_info)
        self.assertEqual(len(data), 4)  # debug, error, info, logger_tree

        log_levels = ['debug', 'info', 'error', 'logger_tree']
        for name, num in data.items():
            lev_name = name.split('=>')[0]
            try:
                log_levels.remove(lev_name)
            except ValueError:
                pass
            # 원하는 대로, rotating된 파일들이 정해진 개수만큼 존재하는가?
            # (원본 로그 파일 제외)
            self.assertLessEqual(num, self.backup_count)
        # 날짜 디렉토리 안의 로그 파일들에는 'debug', 'error', 'info', 'logger_tree'
        # 로 시작하는 파일들만 존재하는가?
        self.assertEqual(log_levels, [])


if __name__ == '__main__':
    @helpers.WorkCWD(__file__)
    def exec_test():
        unittest.main()
        
    exec_test()
    