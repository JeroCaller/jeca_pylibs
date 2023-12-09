import unittest
import sys

from dirimporttool import get_super_dir_directly

for i in range(1, 2+1):
    super_dir = get_super_dir_directly(__file__, i)
    sys.path.append(super_dir)

import dirsearch as dirs
from submodules.tree import PathTree, LENGTH


class TestLengthSort(unittest.TestCase):
    def setUp(self):
        self.fixture_text = [
            r'C:\test_folder\backup\잃어버린 나비의 꿈.txt',
            r'C:\test_folder\myzip.zip',
            r'C:\test_folder\backup\some_text.txt',
            r'C:\test_folder\subfolder\새 텍스트 20230423002632.txt',
            r'C:\test_folder\some_text.txt',
        ]

    def testSort(self):
        actual_result = dirs.sort_length_order(self.fixture_text)
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
            self.fixture_text, False)
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
        self.test_root_dir_path = "..\\fixtures\\testpkg"
        self.fixture_path = [
            r'testpkg\file6.txt',
            r'testpkg\sub_dir1\file1.txt',
            r'testpkg\sub_dir1\file2.txt',
            r'testpkg\sub_dir1\sub_sub_dir1\file3.txt',
            r'testpkg\sub_dir2\sub_sub_dir2\file4.txt',
            r'testpkg\sub_dir2\sub_sub_dir2\file5.txt',
            r'testpkg\sub_dir2\sub_sub_dir3',
        ]
        self.fixture_path = dirs.sort_length_order(self.fixture_path)

    def testRootDirSearch(self):
        """dirsearch.get_all_leaf_entity_path() 함수 테스트."""
        results = dirs.get_all_in_rootdir(self.test_root_dir_path, False)
        results = dirs.sort_length_order(results)
        for i, path in enumerate(results):
            self.assertEqual(path, self.fixture_path[i])

    def testPathTreeFromSearch(self):
        """get_pathtree_obj_from_root_dir() 함수 테스트."""
        result = dirs.get_ptree_from_rootdir(
            self.test_root_dir_path, False)
        self.assertIsInstance(result, PathTree)
        leafpath = result.getAllLeafAbs(how_to_sort=LENGTH)
        for i, path in enumerate(leafpath):
            self.assertEqual(path, self.fixture_path[i])


if __name__ == '__main__':
    unittest.main()
