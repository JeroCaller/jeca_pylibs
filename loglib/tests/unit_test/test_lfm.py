"""logpackage.py의 LogFileManager 클래스 테스트 모듈."""

import unittest
import sys
import os
import time
import shutil
import re

from dirimporttool import get_super_dir_directly

for i in range(1, 2+1):
    super_dir = get_super_dir_directly(__file__, i)
    sys.path.append(super_dir)

from logpackage import LogFileManager, EasySetLogFileEnv
from logpackage import DEFAULT_LEVEL_LOG_FILE_NAMES
from sub_modules.fdhandler import (TextFileHandler, JsonFileHandler,
make_package)
from sub_modules.dirsearch import (validate_if_your_dir_with_ext,
get_all_in_rootdir)
from tools import DateTools, DateOptions
from tests.testdata.testpkg.main import mainfunc

def make_entities_with_delay(
        root_dir: str, 
        entities: list[tuple[int, str]],
        allow_print: bool = True
    ):
    """테스트를 위한 디렉토리 또는 파일 생성 함수.

    Parameters
    ----------
    root_dir : str
        루트 디렉토리 경로. 실존해야 함.
    entities : list[tuple[int, str]]
        루트 디렉토리 아래에 만들 하위 디렉토리 또는 파일들의 경로 리스트. 
        int 부분에는 파일을 생성하기 전 딜레이할 시간을 초로 표시.

    """
    if allow_print:
        print("테스트를 위한 디렉토리 또는 파일 생성 중... 시간이 다소 걸립니다.")
        print("생성된 디렉토리 및 파일 목록.")

    tfh = TextFileHandler(create_dir_ok=False)
    count_entity_made = 0
    
    for t, en in entities:
        fullpath = os.path.join(root_dir, en)
        if os.path.exists(fullpath): continue
        time.sleep(t)
        if os.path.splitext(en)[1]:
            dirpath = os.path.dirname(fullpath)
            os.makedirs(dirpath, exist_ok=True)
            tfh.setTxtFilePath(fullpath)
            tfh.createTxtFile()
        else:
            os.makedirs(fullpath, exist_ok=True)
        if allow_print:
            print(fullpath)
        count_entity_made += 1
    
    if allow_print:
        print(f"생성 완료. 총 {count_entity_made}개 생성됨.")
        print("이미 존재하는 디렉토리 및 파일은 새로 생성되지 않습니다.")

def datedir_without_datetime(data):
    """
    Parameters
    ----------
    data : list[tuple[
        tools.DateOptions.DateType, 
        datetime.datetime,
        datedir_path,
        ]]
    
    """
    result = []
    for dtype, _, dpath in data:
        if validate_if_your_dir_with_ext(dpath, ['.log'])[0]:
            datestr = os.path.basename(dpath)
            result.append((dtype, datestr))
    return result

def get_datedir_path(leaf_entities: list[str]) -> (list[str]):
    """특정 루트 디렉토리 내 하위 디렉토리와 그 안의 파일들의 경로들을 
    리스트로 받아왔을 때, 각 파일들의 디렉토리 경로를 추출하여 리스트로 반환.
    이 때, 경로가 겹치면 중복되는 경로들은 추가하지 않은 상태로 반환된다.

    Parameters
    ----------
    leaf_entities : list[str(dirpath)]
        get_all_in_rootdir() 리턴값
    
    """
    results = []
    for en in leaf_entities:
        dirpath = os.path.dirname(en)
        if dirpath not in results:
            results.append(dirpath)
    return results

def get_datedir_filenames(leaf_entities: list[str]):
    """루트 디렉토리 내 하위 디렉토리 내 파일들의 경로를 받았을 때 
    날짜 디렉토리와 그 디렉토리 아래 파일들의 이름을 아이템으로 하는 
    딕셔너리 반환 함수.

    Parameters
    ----------
    leaf_entities : list[str(dirpath)]
        get_all_in_rootdir() 리턴값

    Returns
    ------
    dict[str, list[str]]
        dict[날짜 디렉토리명, [해당 디렉토리 내 파일명 리스트]]
    
    """
    results: dict[str, list[str]] = {}  # dict[datedir: list[filenames]]
    for en in leaf_entities:
        if not os.path.isfile(en): continue
        
        datedir = os.path.basename(os.path.dirname(en))
        filename = os.path.basename(en)
        if datedir not in results:
            results[datedir] = [filename]
        elif filename not in results[datedir]:
            results[datedir].append(filename)
    return results

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


class TestRotateDirsUnittest(unittest.TestCase):
    """rotateDateDirs() 메서드 유닛테스트 클래스."""
    made_test_ent: bool = False

    def setUp(self):
        self.maxDiff = None

        self.rootdir = os.path.abspath(r'..\testdata\rotatedirs')
        try:
            os.mkdir(self.rootdir)
        except FileExistsError:
            pass

        self.testdatas = [
            (0, r'2023-12-24\info.log'),
            (1, r'2023-12-25\error.log'),
            (3, r'2023-12-32\debug.log'),
            (2, r'2024-01-01\info.log'),
            (1, r'2024-01-2\error.log'),
            (2, r'2123-02-03\debug.log'),
            (1, r'2024-01-5주\info.log'),
            (3, r'2024-2\error.log'),
            (2, r'2025\debug.log'),
            (1, r'2022-01-01\logger_tree.log'),
            (0, r'2023-12-24\hi.txt')
        ]
        if not TestRotateDirsUnittest.made_test_ent:
            make_entities_with_delay(self.rootdir, self.testdatas)
            TestRotateDirsUnittest.made_test_ent = True

        self.lfm = LogFileManager(self.rootdir)
        self.dtool = DateTools()
        self.dopt = DateOptions()
    
    def tearDown(self):
        shutil.rmtree(self.rootdir)

    def testIfRotate(self):
        self.lfm.rotateDateDirs(5)
        datedirs = self.dtool.searchDateDirBirth(self.rootdir)
        proc_datedirs = datedir_without_datetime(datedirs)

        ex_re = [
            (self.dopt.DAY, '2023-12-25'),
            (self.dopt.DAY, '2024-01-01'),
            (self.dopt.DAY, '2024-01-2'),
            (self.dopt.DAY, '2123-02-03'),
            (self.dopt.WEEK, '2024-01-5주'),
            (self.dopt.MONTH, '2024-2'),
            (self.dopt.YEAR, '2025'),
            (self.dopt.DAY, '2022-01-01'),
        ]
        self.assertEqual(proc_datedirs, ex_re[3:])

        excluded_dirs = [
            '2023-12-32', '2023-12-24', 
        ]
        for d in excluded_dirs:
            fullpath = os.path.join(self.rootdir, d)
            does_it_exists = os.path.exists(fullpath)
            self.assertTrue(does_it_exists)


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
        datedirs = get_datedir_path(leaf_entities)
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
        logfiles = get_datedir_filenames(leaf_entities)
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


def write_log(rootdir: str, msg: str):
    """루트 디렉토리 내 모든 .log 파일을 찾아 
    일괄적으로 임의의 로그 메시지를 입력, 저장한다.
    """
    tfh = TextFileHandler()
    leaf_entities = get_all_in_rootdir(rootdir)
    for en in leaf_entities:
        fullpath = os.path.join(rootdir, en)
        if os.path.splitext(en)[1] != '.log':
            continue
        tfh.setTxtFilePath(fullpath)
        tfh.writeNew(msg)


class TestEraseLogFile(unittest.TestCase):
    """로그 파일 내용을 지우는 메서드들에 대한 테스트 클래스."""
    def setUp(self):
        self.testdir = r'..\testdata\for-erase-log'
        self.lfm = LogFileManager()
        self.logmsg = "Test log message."
        self.txthandler = TextFileHandler()

    def tearDown(self):
        shutil.rmtree(self.testdir)
        self.txthandler.setTxtFilePath('')
        self.lfm.setBaseDirPath('')

    def testInitConfig(self):
        """테스트를 위한 초기 설정이 잘 되는지 테스트."""
        # 테스트를 위한 초기 설정.
        test_basedir = os.path.join(self.testdir, 'erase-all-1')
        entities = [
            'debug.log',
            r'2024-01-12\\debug.log'
        ]
        make_package(test_basedir, entities)
        write_log(test_basedir, self.logmsg)

        # 초기 설정 여부 확인용 테스트.
        self.assertTrue(os.path.exists(test_basedir))
        for en in entities:
            fullpath = os.path.join(test_basedir, en)
            self.txthandler.setTxtFilePath(fullpath)
            self.assertTrue(self.txthandler.readContent('read'))

    def testEraseAllInLogFileCase1(self):
        """eraseAllInLogFile() 메서드에 대한 테스트."""
        # 테스트를 위한 초기 설정.
        test_basedir = os.path.join(self.testdir, 'erase-all-1')
        entities = [
            'debug.log',
            r'2024-01-12\\debug.log'
        ]
        make_package(test_basedir, entities)
        write_log(test_basedir, self.logmsg)
        self.lfm.setBaseDirPath(test_basedir)

        result = self.lfm.eraseAllInLogFile(*os.path.split(entities[1]), True)
        self.assertTrue(result)

        # test 1
        for en in entities:
            fullpath = os.path.join(test_basedir, en)
            self.txthandler.setTxtFilePath(fullpath)
            self.assertEqual(
                self.txthandler.readContent('read'), '', 
                fullpath
            )


if __name__ == '__main__':
    def test_only_one(test_classname):
        suite_obj = unittest.TestSuite()
        try:
            suite_obj.addTest(unittest.makeSuite(test_classname))
        except TypeError:
            suite_obj.addTest(test_classname)

        runner = unittest.TextTestRunner()
        runner.run(suite_obj)
    
    #unittest.main()
    test_only_one(TestEraseLogFile)