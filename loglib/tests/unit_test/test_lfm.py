"""logpackage.py의 LogFileManager 클래스 테스트 모듈."""

import unittest
import sys
import os
import shutil

from dirimporttool import get_super_dir_directly

for i in range(1, 2+1):
    super_dir = get_super_dir_directly(__file__, i)
    sys.path.append(super_dir)

import helpers
from logpackage import LogFileManager
from sub_modules.fdhandler import (TextFileHandler,
make_package, decompress_zip)
from sub_modules.dirsearch import (validate_if_your_dir_with_ext,
get_all_in_rootdir)
from tools import DateTools, DateOptions

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
            helpers.make_entities_with_delay(self.rootdir, self.testdatas)
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
        self.txthandler = TextFileHandler(create_dir_ok=False)

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

        # test
        for en in entities:
            fullpath = os.path.join(test_basedir, en)
            self.txthandler.setTxtFilePath(fullpath)
            self.assertEqual(
                self.txthandler.readContent('read'), '', 
                fullpath
            )
    
    def testEraseAllInLogFileCase2(self):
        """eraseAllInLogFile() 메서드에 대한 테스트."""
        # 테스트를 위한 초기 설정
        test_basedir = os.path.join(self.testdir, 'erase-all-2')
        entities = [
            'debug.log',
            r'2024-01-16\debug.log',
            r'2024-01-17\debug.log',
            r'2024-01-17\info.log',
            r'2024-01-17\debug (1).log',
        ]
        make_package(test_basedir, entities)
        write_log(test_basedir, self.logmsg)
        self.lfm.setBaseDirPath(test_basedir)

        # test
        result = self.lfm.eraseAllInLogFile('2024-01-17', 'debug.log')
        self.assertTrue(result)

        for en in entities:
            fullpath = os.path.join(test_basedir, en)
            self.txthandler.setTxtFilePath(fullpath)
            logmsg = self.txthandler.readContent('read')
            if en == r'2024-01-17\debug.log':
                self.assertEqual(logmsg, '', fullpath)
            else:
                self.assertEqual(logmsg, self.logmsg, fullpath)

    def testEraseAllInDateDirCase1(self):
        """eraseAllInDateDir() 메서드 테스트."""
        # 테스트를 위한 초기 설정
        test_basedir = os.path.join(self.testdir, 'erase-date-1')
        entities = [
            'debug.log',
            r'2024-01-16\debug.log',
            r'2024-01-17\debug.log',
            r'2024-01-17\debug (1).log',
            r'2024-01-17\info.log',
            r'2024-01-17\info (1).log',
            r'2024-01-17\error.log',
            r'2024-01-17\error (1).log',
            r'2024-01-17\logger_tree.log',
            r'2024-01-17\logger_tree (1).log',
        ]
        make_package(test_basedir, entities)
        write_log(test_basedir, self.logmsg)
        self.lfm.setBaseDirPath(test_basedir)

        # test
        result = self.lfm.eraseAllInDateDir('2024-01-17')
        self.assertTrue(result)

        for en in entities:
            fullpath = os.path.join(test_basedir, en)
            self.txthandler.setTxtFilePath(fullpath)
            logmsg = self.txthandler.readContent('read')
            if os.path.dirname(en) == '2024-01-17':
                self.assertEqual(logmsg, '', fullpath)
            else:
                self.assertEqual(logmsg, self.logmsg, fullpath)


class TestDeleteLogFile(unittest.TestCase):
    """로그 파일들을 삭제하는 메서드들에 대한 테스트 클래스."""
    def setUp(self):
        self.testdir = r'..\testdata\for-del-log'
        self.lfm = LogFileManager()
        self.logmsg = "Test log message."
        self.txthandler = TextFileHandler(create_dir_ok=False)

    def tearDown(self):
        shutil.rmtree(self.testdir)
        self.lfm.setBaseDirPath('')
        self.txthandler.setTxtFilePath('')

    def testInitConfig(self):
        """테스트를 위한 초기 설정이 잘 되는지 테스트."""
        # 테스트를 위한 초기 설정.
        test_basedir = os.path.join(self.testdir, 'del-all-1')
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

    def testDeleteLogFileCase1(self):
        """deleteLogFile() 메서드 테스트."""
        # 테스트를 위한 초기 설정.
        test_basedir = os.path.join(self.testdir, 'del-all-1')
        entities = [
            'debug.log',
            r'2024-01-12\\debug.log',
            r'2024-01-17\\debug.log',
            r'2024-01-17\\debug (1).log',
            r'2024-01-17\\info.log',
        ]
        make_package(test_basedir, entities)
        write_log(test_basedir, self.logmsg)
        self.lfm.setBaseDirPath(test_basedir)

        # test 
        result = self.lfm.deleteLogFile('2024-01-17', 'debug.log', True)
        self.assertTrue(result)

        for en in entities:
            fullpath = os.path.join(test_basedir, en)
            if os.path.basename(en) == 'debug.log':
                self.assertFalse(os.path.exists(fullpath), fullpath)
            else:
                self.assertTrue(os.path.exists(fullpath), fullpath)
                self.txthandler.setTxtFilePath(fullpath)
                self.assertEqual(
                    self.txthandler.readContent('read'), self.logmsg, 
                    fullpath
                )

        # 테스트 디렉토리 내 남은 파일 수 테스트
        all_leaf = get_all_in_rootdir(test_basedir)
        self.assertEqual(len(all_leaf), 3)

    def testDeleteLogFileCase2(self):
        """deleteLogFile() 메서드 테스트."""
        # 테스트를 위한 초기 설정.
        test_basedir = os.path.join(self.testdir, 'del-all-2')
        entities = [
            'debug.log',
            r'2024-01-12\debug.log',
            r'2024-01-17\debug.log',
            r'2024-01-17\debug (1).log',
            r'2024-01-17\info.log',
        ]
        make_package(test_basedir, entities)
        write_log(test_basedir, self.logmsg)
        self.lfm.setBaseDirPath(test_basedir)

        # test
        target = r'2024-01-17\debug.log'
        result = self.lfm.deleteLogFile(*os.path.split(target))
        self.assertTrue(result)
        
        for en in entities:
            fullpath = os.path.join(test_basedir, en)
            if en == target:
                self.assertFalse(os.path.exists(fullpath), fullpath)
            else:
                self.assertTrue(os.path.exists(fullpath), fullpath)
                self.txthandler.setTxtFilePath(fullpath)
                self.assertEqual(
                    self.txthandler.readContent('read'), self.logmsg,
                    fullpath
                )
        
        # 테스트 디렉토리 내 남은 파일 수 테스트
        all_leaf = get_all_in_rootdir(test_basedir)
        self.assertEqual(len(all_leaf), 4)

    def testDeleteAllInDateDirCase1(self):
        """deleteAllInDateDir() 메서드 테스트."""
        # 테스트를 위한 초기 설정.
        test_basedir = os.path.join(self.testdir, 'del-date-1')
        entities = [
            'debug.log',
            r'2024-01-12\debug.log',
            r'2024-01-12\info.log',
            r'2024-01-17\debug.log',
            r'2024-01-17\debug (1).log',
            r'2024-01-17\info.log',
            r'2024-01-18\error.log',
        ]
        make_package(test_basedir, entities)
        write_log(test_basedir, self.logmsg)
        self.lfm.setBaseDirPath(test_basedir)

        # test
        target_dir = '2024-01-17'
        result = self.lfm.deleteAllInDateDir(target_dir)
        self.assertTrue(result)
        
        target_dir_fullpath = os.path.join(test_basedir, target_dir)
        self.assertTrue(os.path.exists(target_dir_fullpath))

        for en in entities:
            fullpath = os.path.join(test_basedir, en)
            if os.path.dirname(en) == target_dir:
                self.assertFalse(os.path.exists(fullpath), fullpath)
            else:
                self.assertTrue(os.path.exists(fullpath), fullpath)
                self.txthandler.setTxtFilePath(fullpath)
                self.assertEqual(
                    self.txthandler.readContent('read'),
                    self.logmsg,
                    fullpath
                )

        # 테스트 디렉토리 내 남은 파일 수 테스트
        all_leaf = get_all_in_rootdir(test_basedir)
        self.assertEqual(len(all_leaf), 5)

    def testDeleteAllInDateDirCase2(self):
        """deleteAllInDateDir() 메서드 테스트."""
        # 테스트를 위한 초기 설정.
        test_basedir = os.path.join(self.testdir, 'del-date-2')
        entities = [
            'debug.log',
            r'2024-01-12\debug.log',
            r'2024-01-12\info.log',
            r'2024-01-17\debug.log',
            r'2024-01-17\debug (1).log',
            r'2024-01-17\info.log',
            r'2024-01-18\error.log',
        ]
        make_package(test_basedir, entities)
        write_log(test_basedir, self.logmsg)
        self.lfm.setBaseDirPath(test_basedir)

        # test
        target_dir = '2024-01-17'
        result = self.lfm.deleteAllInDateDir(target_dir, True)
        self.assertTrue(result)
        
        target_dir_fullpath = os.path.join(test_basedir, target_dir)
        self.assertFalse(os.path.exists(target_dir_fullpath))

        for en in entities:
            fullpath = os.path.join(test_basedir, en)
            if os.path.dirname(en) == target_dir:
                self.assertFalse(os.path.exists(fullpath), fullpath)
            else:
                self.assertTrue(os.path.exists(fullpath), fullpath)
                self.txthandler.setTxtFilePath(fullpath)
                self.assertEqual(
                    self.txthandler.readContent('read'),
                    self.logmsg,
                    fullpath
                )

        # 테스트 디렉토리 내 남은 파일 수 테스트
        all_leaf = get_all_in_rootdir(test_basedir)
        self.assertEqual(len(all_leaf), 4)


class TestZip(unittest.TestCase):
    """LogFileManager() 클래스 내 zip 관련 메서드 테스트."""
    def setUp(self):
        self.test_rootdir_path = r'..\testdata\forzipdir'
        self.entities = [
            '2024-01-16\\debug_2024-01-16.log',
            '2024-01-16\\error_2024-01-16.log',
            '2024-01-16\\info_2024-01-16.log',
            '2024-01-16\\logger_tree_2024-01-16.log',
            '2024-01-17\\debug_2024-01-17.log',
            '2024-01-17\\error_2024-01-17.log',
            '2024-01-17\\info_2024-01-17.log',
            '2024-01-17\\logger_tree_2024-01-17.log',
            '2024-01-19\\debug_2024-01-19.log',
            '2024-01-19\\error_2024-01-19.log',
            '2024-01-19\\info_2024-01-19.log',
            '2024-01-19\\logger_tree_2024-01-19.log'
        ]
        if not os.path.exists(self.test_rootdir_path):
            make_package(self.test_rootdir_path, self.entities)
        
        self.datedirs = helpers.get_datedir_path(self.entities)
        self.datefd = helpers.get_datedir_filenames(self.entities)
        
        # zip 파일 압축 해제한 결과물을 임시로 저장할 경로.
        self.tempdir = r'..\testdata\zipresults'
        self.zipsave = r'..\testdata\zipsave'
        self.zipdirlist = [self.tempdir, self.zipsave]
        for zd in self.zipdirlist:
            os.makedirs(zd, exist_ok=True)

        self.lfm = LogFileManager(self.test_rootdir_path)
        
    def tearDown(self):
        shutil.rmtree(self.test_rootdir_path)
        for zd in self.zipdirlist:
            shutil.rmtree(zd)

    def testZipAllDateDirsCase1(self):
        """zipAllDateDirs() 메서드 테스트."""
        self.lfm.zipAllDateDirs()

        # zip 파일이 지정된 곳에 생성되었는지, 
        # 로그 파일들은 그대로 남아있는지 테스트.
        zippath = []
        for datedir in os.listdir(self.test_rootdir_path):
            dirpath = os.path.join(self.test_rootdir_path, datedir)
            lognum = 0
            for file in os.listdir(dirpath):
                filepath = os.path.join(dirpath, file)
                if filepath.endswith('.log'):
                    lognum += 1
                else:
                    filename, ext = os.path.splitext(file)
                    self.assertEqual(filename, datedir)
                    self.assertEqual(ext, '.zip')
                    zippath.append(filepath)
            self.assertEqual(lognum, len(self.datefd[datedir]))

        # zip 파일 내부 구조 테스트.
        for i, zipfile in enumerate(zippath):
            subdirpath = os.path.join(self.tempdir, f'temp{i+1}')
            os.mkdir(subdirpath)
            decompress_zip(zipfile, subdirpath)

            zip_leaf = get_all_in_rootdir(subdirpath, False)
            zipname = os.path.splitext(os.path.basename(zipfile))[0]
            self.assertEqual(os.listdir(subdirpath)[0], zipname)
            self.assertEqual(len(zip_leaf), 4)
            for en in zip_leaf:
                self.assertEqual(os.path.splitext(en)[1], '.log')

    def testZipAllDateDirsCase2(self):
        """zipAllDateDirs() 메서드 테스트.
        로그 파일들을 zip 파일로 압축한 후, 원본 로그 파일들을 
        지우는 기능에 대한 테스트.
        """
        self.lfm.zipAllDateDirs(False)

        # zip 파일이 지정된 곳에 생성되었는지, 
        # 로그 파일들은 삭제되었는지 테스트.
        zippath = []
        for datedir in os.listdir(self.test_rootdir_path):
            dirpath = os.path.join(self.test_rootdir_path, datedir)
            lognum = 0
            for file in os.listdir(dirpath):
                filepath = os.path.join(dirpath, file)
                if filepath.endswith('.log'):
                    lognum += 1
                else:
                    filename, ext = os.path.splitext(file)
                    self.assertEqual(filename, datedir)
                    self.assertEqual(ext, '.zip')
                    zippath.append(filepath)
            self.assertEqual(lognum, 0)

        # zip 파일 내부 구조 테스트.
        for i, zipfile in enumerate(zippath):
            subdirpath = os.path.join(self.tempdir, f'temp{i+1}')
            os.mkdir(subdirpath)
            decompress_zip(zipfile, subdirpath)

            zip_leaf = get_all_in_rootdir(subdirpath, False)
            zipname = os.path.splitext(os.path.basename(zipfile))[0]
            self.assertEqual(os.listdir(subdirpath)[0], zipname)
            self.assertEqual(len(zip_leaf), 4)
            for en in zip_leaf:
                self.assertEqual(os.path.splitext(en)[1], '.log')

    def testZipTodayDateDir(self):
        """zipTodayDateDir() 메서드 테스트."""
        # 실행 날짜 기준 날짜 디렉토리 및 하위 로그 파일 생성
        today_dir = DateTools().getTodaysDateStr()
        todaydirpath = os.path.join(self.test_rootdir_path, today_dir)
        os.makedirs(todaydirpath, exist_ok=True)
        logfiles = ['debug.log', 'error.log', 'info.log', 'logger_tree.log']
        for logf in logfiles:
            filepath = os.path.join(todaydirpath, logf)
            with open(filepath, 'w'): pass
        
        zipfilename = '.'.join([today_dir, 'zip'])
        zippath = os.path.join(todaydirpath, zipfilename)
        
        exec_result = self.lfm.zipTodayDateDir()
        self.assertTrue(exec_result)
        self.assertTrue(os.path.exists(zippath))
        
        # 실행 날짜 디렉토리 내 zip 파일 생성 여부 및 로그 파일 존재 여부 테스트.
        in_todaydir = os.listdir(todaydirpath)
        self.assertIn(zipfilename, in_todaydir)
        for file in in_todaydir:
            if file.endswith('.zip'):
                continue
            self.assertTrue(file.endswith('.log'))
        
        # 생성된 zip 파일 내부 구조 확인 테스트.
        decompress_zip(zippath, self.tempdir)
        decom_dir = os.listdir(self.tempdir)[0]
        self.assertEqual(decom_dir, today_dir)
        in_decom_dir = os.listdir(os.path.join(self.tempdir, decom_dir))
        for file in in_decom_dir:
            self.assertIn(file, logfiles)

    def testZipBaseDirCase1(self):
        """zipBaseDir() 메서드 테스트.
        zip 파일을 로그 베이스 디렉토리 안에 저장하는 경우 테스트.
        """
        self.lfm.zipBaseDir()

        zipfilename = '.'.join(
            [os.path.basename(self.test_rootdir_path), 'zip']
        )
        zippath = os.path.join(self.test_rootdir_path, zipfilename)
        in_basedir = os.listdir(self.test_rootdir_path)
        # zip 파일이 생성되었는지, 그리고 의도된 이름을 가진 zip 파일인지 확인.
        self.assertIn(zipfilename, in_basedir)
        self.assertTrue(os.path.exists(zippath))

        in_basedir.remove(zipfilename)

        # 로그 파일들이 그대로 있는지, 
        # 의도치 않게 zip 파일이 생성되진 않았는지 확인.
        for datedir in in_basedir:
            dirpath = os.path.join(self.test_rootdir_path, datedir)
            lognum = 0
            for file in os.listdir(dirpath):
                filepath = os.path.join(dirpath, file)
                if filepath.endswith('.log'):
                    lognum += 1
            self.assertEqual(lognum, len(self.datefd[datedir]))

        # zip 파일 내부 구조 확인 테스트.
        decompress_zip(zippath, self.tempdir)
        in_zip = os.listdir(self.tempdir)
        rootdirname = in_zip[0]
        self.assertEqual(len(in_zip), 1)
        self.assertEqual(
            rootdirname, os.path.basename(self.test_rootdir_path)
        )
        in_root = get_all_in_rootdir(
            os.path.join(self.tempdir, rootdirname), False
        )
        in_root.sort()
        self.entities.sort()
        self.assertEqual(in_root, self.entities)

    def testZipBaseDirCase2(self):
        """zipBaseDir() 메서드 테스트.
        zip 파일을 로그 베이스 디렉토리 밖에 저장하는 경우 테스트.
        """
        target_dir = r'..\testdata\zipsave'
        self.lfm.zipBaseDir(target_dir)

        zipfilename = '.'.join(
            [os.path.basename(self.test_rootdir_path), 'zip']
        )
        zippath = os.path.join(target_dir, zipfilename)
        # 실제 원하는 위치에 zip 파일이 생성되었는지 확인.
        self.assertTrue(os.path.exists(zippath))
        in_target_dir = os.listdir(target_dir)
        self.assertEqual(in_target_dir[0], zipfilename)
        self.assertEqual(len(in_target_dir), 1)

        # 기존 로그 베이스 디렉토리 내부는 zip 파일 생성 없이 
        # 그대로 존재하는지 테스트. 
        leaf_base = get_all_in_rootdir(self.test_rootdir_path, False)
        for leaf in leaf_base:
            self.assertFalse(leaf.endswith('.zip'))
        leaf_base.sort()
        self.entities.sort()
        self.assertEqual(leaf_base, self.entities)

        # zip 파일 내부 구조 확인 테스트.
        decompress_zip(zippath, self.tempdir)
        in_zip = os.listdir(self.tempdir)
        rootdirname = in_zip[0]
        self.assertEqual(len(in_zip), 1)
        self.assertEqual(
            rootdirname, os.path.basename(self.test_rootdir_path)
        )
        in_root = get_all_in_rootdir(
            os.path.join(self.tempdir, rootdirname), False
        )
        in_root.sort()
        self.assertEqual(in_root, self.entities)


if __name__ == '__main__':
    # 다음 중 원하는 테스트의 코드만 주석 해제할 것.
    unittest.main()
    #helpers.test_only_one(TestEraseLogFile)
    #helpers.test_only_one(TestDeleteLogFile)
    #helpers.test_only_one(TestZip)
    #helpers.test_only_one(TestZip('testZipTodayDateDir'))
    #helpers.test_only_one(TestZip('testZipBaseDirCase1'))
    #helpers.test_only_one(TestZip('testZipBaseDirCase2'))
    #helpers.test_only_one(TestRotateDirsUnittest)
