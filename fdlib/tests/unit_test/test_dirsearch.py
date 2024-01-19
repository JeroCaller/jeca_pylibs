import unittest
import sys
import os

from dirimporttool import get_super_dir_directly

for i in range(1, 2+1):
    super_dir = get_super_dir_directly(__file__, i)
    sys.path.append(super_dir)

import dirsearch as dirs
from submodules.tree import PathTree, LENGTH


class TestLengthSort(unittest.TestCase):
    def setUp(self):
        self.testdata_text = [
            r'C:\test_folder\backup\잃어버린 나비의 꿈.txt',
            r'C:\test_folder\myzip.zip',
            r'C:\test_folder\backup\some_text.txt',
            r'C:\test_folder\subfolder\새 텍스트 20230423002632.txt',
            r'C:\test_folder\some_text.txt',
        ]

    def testSort(self):
        actual_result = dirs.sort_length_order(self.testdata_text)
        expected_result = [
            r'C:\test_folder\myzip.zip',
            r'C:\test_folder\some_text.txt',
            r'C:\test_folder\backup\some_text.txt',
            r'C:\test_folder\backup\잃어버린 나비의 꿈.txt',
            r'C:\test_folder\subfolder\새 텍스트 20230423002632.txt',
        ]
        for i, data in enumerate(actual_result):
            self.assertEqual(data, expected_result[i])

        actual_result2 = dirs.sort_length_order(
            self.testdata_text, False)
        expected_result2 = [ 
            r'C:\test_folder\subfolder\새 텍스트 20230423002632.txt',
            r'C:\test_folder\backup\잃어버린 나비의 꿈.txt',
            r'C:\test_folder\backup\some_text.txt',
            r'C:\test_folder\some_text.txt',
            r'C:\test_folder\myzip.zip',
        ]
        for i, data in enumerate(actual_result2):
            self.assertEqual(data, expected_result2[i])


class TestDirSearch(unittest.TestCase):
    def setUp(self):
        self.test_root_dir_path = "..\\testdata\\testpkg"
        self.testdata_path = [
            r'file6.txt',
            r'sub_dir1\file1.txt',
            r'sub_dir1\file2.txt',
            r'sub_dir1\sub_sub_dir1\file3.txt',
            r'sub_dir2\sub_sub_dir2\file4.txt',
            r'sub_dir2\sub_sub_dir2\file5.txt',
            r'sub_dir2\sub_sub_dir3',
        ]
        self.testdata_path = dirs.sort_length_order(self.testdata_path)

    def testRootDirSearch(self):
        """dirsearch.get_all_in_rootdir() 함수 테스트."""
        # test 1
        results = dirs.get_all_in_rootdir(self.test_root_dir_path, False)
        results = dirs.sort_length_order(results)
        for i, path in enumerate(results):
            self.assertEqual(path, self.testdata_path[i])

        # test 2
        # 빈 디렉토리일 경우.
        temp_dirpath = r'..\testdata\emptydir'
        os.makedirs(temp_dirpath, exist_ok=True)
        results = dirs.get_all_in_rootdir(temp_dirpath)
        self.assertEqual(results, [])
        # 생성된 빈 디렉토리 삭제
        os.rmdir(temp_dirpath)

    def testPathTreeFromSearch(self):
        """get_ptree_from_rootdir() 함수 테스트."""
        result = dirs.get_ptree_from_rootdir(
            self.test_root_dir_path, False)
        self.assertIsInstance(result, PathTree)
        leafpath = result.getAllLeafAbs(how_to_sort=LENGTH)
        for i, path in enumerate(leafpath):
            self.assertEqual(path, self.testdata_path[i])


class TestValidateIfDir(unittest.TestCase):
    """validate_if_your_dir_with_ext() 함수 테스트."""
    def setUp(self):
        self.fixt_dirs_path = [
            r'..\testdata\validatedirs\dir1',
            r'..\testdata\validatedirs\dir2',
            r'..\testdata\validatedirs\dir3',
            r'..\testdata\validatedirs\2023-12-24',
        ]

    def testValidateIfDir(self):
        # test 1
        is_valid, no_allowed = dirs.validate_if_your_dir_with_ext(
            root_dir=self.fixt_dirs_path[0],
            include=['.txt', '.log'],
            not_include_ok=True
        )
        self.assertTrue(is_valid)
        self.assertEqual(no_allowed, [])

        # test 2
        is_valid, no_allowed = dirs.validate_if_your_dir_with_ext(
            self.fixt_dirs_path[1],
            ['.txt', '.log'],
        )
        self.assertEqual(is_valid, False)
        self.assertEqual(no_allowed, ['how_to_use_sample.jpg'])

        # test 3
        is_valid, no_allowed = dirs.validate_if_your_dir_with_ext(
            self.fixt_dirs_path[2],
            ['.txt'],
            dir_include_ok=True
        )
        self.assertEqual(is_valid, True)
        self.assertEqual(no_allowed, [])

        # test 4
        is_valid, no_allowed = dirs.validate_if_your_dir_with_ext(
            self.fixt_dirs_path[1],
            ['.txt', '.log', '.png'],
            not_include_ok=False
        )
        self.assertEqual(is_valid, False)
        self.assertEqual(no_allowed, ['how_to_use_sample.jpg', 'no .png'])

        # test 5
        is_valid, no_allowed = dirs.validate_if_your_dir_with_ext(
            self.fixt_dirs_path[2],
            ['.txt'],
            dir_include_ok=False
        )
        self.assertEqual(is_valid, False)
        self.assertEqual(no_allowed, ['log'])

        # test 6
        is_valid, no_allowed = dirs.validate_if_your_dir_with_ext(
            self.fixt_dirs_path[3],
            ['.log']
        )
        self.assertEqual(is_valid, False)
        self.assertEqual(no_allowed, ['hi.txt'])


if __name__ == '__main__':
    def test_only(casename):
        """
        Parameters
        ----------
        casename : callable
            테스트 하고자 하는 테스트 클래스명 또는 메서드명
        
        """
        suite_obj = unittest.TestSuite()
        try:
            suite_obj.addTest(unittest.makeSuite(casename))
        except TypeError:
            suite_obj.addTest(casename)

        runner = unittest.TextTestRunner()
        runner.run(suite_obj)

    # 테스트하고자 하는 코드만 주석 해제하여 진행.
    unittest.main()
    #test_only(TestDirSearch)