"""logpackage.py의 LogFileManager 클래스 테스트 모듈."""

import unittest
import sys
import os
import time
import shutil

from dirimporttool import get_super_dir_directly

for i in range(1, 2+1):
    super_dir = get_super_dir_directly(__file__, i)
    sys.path.append(super_dir)

from logpackage import LogFileManager
from sub_modules.fdhandler import TextFileHandler
from sub_modules.dirsearch import validate_if_your_dir_with_ext
from tools import DateTools, DateOptions

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

    tfh = TextFileHandler(root_dir)
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


class TestRotateDirs(unittest.TestCase):
    """rotateDateDirs() 메서드 테스트 클래스."""
    made_test_ent: bool = False

    def setUp(self):
        self.maxDiff = None

        self.rootdir = os.path.abspath(r'..\fixtures\rotatedirs')
        try:
            os.mkdir(self.rootdir)
        except FileExistsError:
            pass

        self.fixtures = [
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
        if not TestRotateDirs.made_test_ent:
            make_entities_with_delay(self.rootdir, self.fixtures)
            TestRotateDirs.made_test_ent = True

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


if __name__ == '__main__':
    unittest.main()
    