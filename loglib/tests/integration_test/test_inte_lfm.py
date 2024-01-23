import unittest
import sys
import os
import re

from dirimporttool import get_super_dir_directly

for i in range(1, 2+1):
    super_dir = get_super_dir_directly(__file__, i)
    sys.path.append(super_dir)

import helpers
from tools import DateOptions
from logpackage import LogFileManager, EasySetLogFileEnv
from logpackage import DEFAULT_LEVEL_LOG_FILE_NAMES
from sub_modules.fdhandler import (TextFileHandler, JsonFileHandler)
from sub_modules.dirsearch import (get_all_in_rootdir)
from tests.testdata.testpkg.main import mainfunc

def record_deleted_datedir(
        prev_json_path: str, 
        target_basedir: str,
        del_txt_path: str,
        limit_datedirs_num: int
    ):
    """rotate 기능이 적용된 로그 파일 저장 베이스 디렉토리 내
    삭제된 날짜 디렉토리명을 기록하는 함수.

    Parameters
    ----------
    prev_json_path : str
        이전 날짜 디렉토리명들을 기록할 json 파일명 (경로 포함)
    target_basedir : str
        베이스 디렉토리 경로
    del_txt_path : str
        여태까지 삭제된 날짜 디렉토리명을 기록할 텍스트 파일명. (경로 포함)
    limit_datedirs_num : int
        보관할 날짜 디렉토리 제한 수.
    
    """
    tfh = TextFileHandler(del_txt_path)
    jfh = JsonFileHandler(prev_json_path)

    cur_datedirs = os.listdir(target_basedir)

    # == 주어진 경로에 파일이 없을 때 자동 생성 ==
    if not os.path.exists(prev_json_path):
        jfh.write(cur_datedirs)
        return

    prev_datedirs: list[str] = jfh.read()

    cur_only = list(set(cur_datedirs) - set(prev_datedirs))
    prev_only = list(set(prev_datedirs) - set(cur_datedirs))
    if len(prev_datedirs) < limit_datedirs_num:
        prev_datedirs.extend(cur_only)
    elif cur_only == prev_only == []:
        return
    else:
        tfh.appendText('\n' + prev_only[0])
        prev_datedirs.remove(prev_only[0])
        prev_datedirs.append(cur_only[0])
    jfh.write(prev_datedirs)


class InitLogConfig():
    def __init__(self, dateopt: DateOptions):
        self.base_dir_location = r'..\testdata\testpkg'
        if dateopt == DateOptions.DAY:
            self.base_dir_name_date = 'logfile_rot_day'
        elif dateopt == DateOptions.WEEK:
            self.base_dir_name_date = 'logfile_rot_week'
        elif dateopt == DateOptions.MONTH:
            self.base_dir_name_date = 'logfile_rot_month'
        elif dateopt == DateOptions.YEAR:
            self.base_dir_name_date = 'logfile_rot_year'

        self.init_log_env = EasySetLogFileEnv()
        self.init_log_env.setEssentialLogEnv(
            base_dir=self.base_dir_location,
            base_dir_name=self.base_dir_name_date,
            level_option=True,
            date_opt=dateopt
        )
        self.basedir = self.init_log_env.base_dir  # 외부 이용 용도.
        self.log_fm = LogFileManager(self.basedir)

    def setup(
            self,
            test_classname: unittest.TestCase,
            on_error_log: bool,
            limit_datedir_num: int
        ):
        # mainfunc 다수 호출에 의해 생성될 수 있는 불필요한 로그 기록 방지용.
        if not test_classname.main_init:
            mainfunc(
                self.init_log_env,
                raise_error_log=on_error_log,
                print_result=False,
                log_file_manager=self.log_fm,
                limit_datedir_num=limit_datedir_num
            )
            test_classname.main_init = True


class TestRotateDirLog(unittest.TestCase):
    """rotateDateDirs() 메서드 테스트. 
    테스트 testdata 패키지 내 실제 로깅 과정에서 사용하여 
    실제 해당 메서드가 잘 작동하는지 테스트. 

    제대로 된 테스트를 위해 실제 로깅 날짜에 따라 날짜 디렉토리를 생성, 보관하므로, 
    제대로 된 테스트를 위해선 며칠 이상 매일 이 테스트 코드를 실행시켜야 함.

    """
    main_init: bool = False

    def setUp(self):
        self.json_path_day = r'..\testdata\datedirrecord\day.json'
        self.del_rec_txt_path_day = r'..\testdata\datedirrecord\day.txt'
        self.dopt = DateOptions()

        self.initconfigday = InitLogConfig(self.dopt.DAY)
        self.datedir_day_num = 3
        self.initconfigday.setup(
            TestRotateDirLog, False, self.datedir_day_num
        )

    def testDateDirsDay(self):
        leaf_entities = get_all_in_rootdir(self.initconfigday.basedir)
        datedirs = helpers.get_datedir_path(leaf_entities)
        if len(datedirs) < self.datedir_day_num:
            self.skipTest('테스트를 위한 데이터가 충분하지 않아 스킵됩니다.')

        # 현재 베이스 디렉토리 내 삭제된 날짜 디렉토리명을 기록.
        record_deleted_datedir(
            self.json_path_day,
            self.initconfigday.basedir,
            self.del_rec_txt_path_day,
            self.datedir_day_num
        )
        
        # 전체 날짜 디렉토리 개수 확인.
        logfiles = helpers.get_datedir_filenames(leaf_entities)
        self.assertEqual(len(datedirs), self.datedir_day_num)

        # 각 날짜 디렉토리 안에 존재해야할 로그 파일들이 있는지 확인.
        ex_re = sorted(list(DEFAULT_LEVEL_LOG_FILE_NAMES.copy().values()))
        for v_list in logfiles.values():
            temp = []
            for v in v_list:
                mat = re.search('_\d+-\d+-\d+', v)
                filename = v.replace(mat.group(), '')
                temp.append(filename)
            temp.sort()
            self.assertEqual(temp, ex_re)


if __name__ == '__main__':
    @helpers.WorkCWD(__file__)
    def exec_test():
        unittest.main()

    exec_test()
