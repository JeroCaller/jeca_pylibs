import unittest
import sys
import os
import shutil
import json
import zipfile

from dirimporttool import get_super_dir_directly

for i in range(1, 2+1):
    super_dir = get_super_dir_directly(__file__, i)
    sys.path.append(super_dir)

import fdhandler as fdh
import dirsearch as dirs

TEXT_SAMPLE = """바다는 푸른 물결이 흐르고, 물 위에는 태양이 빛나고 있습니다. 
파도는 한 번씩 몰려와 모래사장에 부딪히며 화려한 물줄기를 만듭니다. 
해변가에는 시원한 바람이 불어와 신선한 바다 냄새가 퍼져나갑니다. 
사람들은 모래 위에 발을 내딛고 파도와 함께 춤을 추며 자유로움을 느낍니다.
The ocean is a vast expanse of blue, stretching out as far as the eye can see.
The waves crash against the shore, creating a mesmerizing symphony of sound.
The salty breeze carries with it a sense of tranquility and adventure.
As the sun sets on the horizon, 
its golden rays paint the sky in hues of orange and pink.
"""


class TestTxtHandler(unittest.TestCase):
    def setUp(self):
        self.testdata_txtpath = r'..\testdata\testtext.txt'
        self.txthandler = fdh.TextFileHandler(self.testdata_txtpath)
        self.onoff_teardown: bool = True

    def tearDown(self):
        if self.onoff_teardown:
            try:
                os.remove(self.testdata_txtpath)
            except FileNotFoundError:
                pass

    def testCreateTxtFile(self):
        """지정된 경로에 텍스트 파일이 생성되었는지 확인하는 테스트."""
        self.onoff_teardown = True
        self.txthandler.createTxtFile()
        self.assertTrue(os.path.exists(self.testdata_txtpath))
        self.assertTrue(os.path.isfile(self.testdata_txtpath))

    def testWriteNew(self):
        """지정된 경로에 생성한 텍스트 파일에 텍스트가 삽입되었는지 테스트."""
        self.onoff_teardown = True
        self.txthandler.writeNew(TEXT_SAMPLE)
        with open(self.testdata_txtpath, 'r', encoding='utf-8') as f:
            txtdata = f.read()
        self.assertTrue(txtdata)
        self.assertEqual(txtdata, TEXT_SAMPLE)

    def testWriteNewly(self):
        """지정된 텍스트 파일에 기존 텍스트는 사라지고 새로 삽입한 
        텍스트만 남는지 테스트.
        """
        self.onoff_teardown = True
        sample_txt = "hello, world!"
        self.txthandler.writeNew(sample_txt)
        self.txthandler.writeNew(TEXT_SAMPLE)
        with open(self.testdata_txtpath, 'r', encoding='utf-8') as f:
            txtdata = f.read()
        self.assertNotIn(sample_txt, txtdata)
        self.assertEqual(txtdata, TEXT_SAMPLE)

    def testAppendText(self):
        """지정된 경로에 존재하는 텍스트 파일에 이어쓰기가 되는지 테스트."""
        self.onoff_teardown = True
        self.txthandler.writeNew(TEXT_SAMPLE)
        additional_text = "테스트 글!"
        self.txthandler.appendText(additional_text)
        with open(self.testdata_txtpath, 'r', encoding='utf-8') as f:
            txtdata = f.readlines()
        self.assertTrue(txtdata)
        self.assertEqual(txtdata[-1], additional_text)

    def testRead(self):
        """텍스트 파일로부터 텍스트를 정상적으로 읽어들여오는지 테스트."""
        self.onoff_teardown = True
        self.txthandler.writeNew(TEXT_SAMPLE)
        
        # test 1
        txtdata = self.txthandler.readContent('read')
        self.assertIsInstance(txtdata, str)
        self.assertEqual(len(txtdata), len(TEXT_SAMPLE))

        # test 2
        txtdata = self.txthandler.readContent('readline')
        self.assertIsInstance(txtdata, str)
        txtdata = txtdata.strip('\n')
        expected_result \
            = '바다는 푸른 물결이 흐르고, 물 위에는 태양이 빛나고 있습니다. '
        self.assertEqual(txtdata, expected_result)

        # test 3
        txtdata = self.txthandler.readContent('readlines')
        self.assertIsInstance(txtdata, list)
        self.assertEqual(len(txtdata), 9)


class TestTxtHandlerMakeDirs(unittest.TestCase):
    """TextFileHandler 클래스 사용 시 주어진 텍스트 파일 경로 중간에 
    실존하지 않는 디렉토리 존재 시 이를 자동 생성하는 지 테스트.
    """
    def setUp(self):
        self.middirname = 'texts'
        self.txt_path = rf'..\testdata\{self.middirname}\mytext.txt'
        self.txthandler = fdh.TextFileHandler(self.txt_path)

        self.middirname2 = 'nontexts'
        self.non_txt_path = rf'..\testdata\{self.middirname2}\mytext.txt'
        self.non_txthandler = fdh.TextFileHandler(
            self.non_txt_path, create_dir_ok=False
        )

    def tearDown(self):
        shutil.rmtree(os.path.dirname(self.txt_path), True)
        shutil.rmtree(os.path.dirname(self.non_txt_path), True)

    def testCreateTxtFile(self):
        # test 1
        self.txthandler.createTxtFile()
        self.assertTrue(os.path.exists(self.txt_path))
        self.assertTrue(os.path.exists(os.path.dirname(self.txt_path)))
        self.assertTrue(os.path.isfile(self.txt_path))

        # test 2
        with self.assertRaises(FileNotFoundError):
            self.non_txthandler.createTxtFile()
        self.assertFalse(os.path.exists(self.non_txt_path))

    def testIOTextFile(self):
        # test 1
        self.txthandler.writeNew(TEXT_SAMPLE)
        self.assertTrue(os.path.exists(self.txt_path))
        self.assertTrue(os.path.exists(os.path.dirname(self.txt_path)))
        self.assertTrue(os.path.isfile(self.txt_path))
        txtdata = self.txthandler.readContent('read')
        self.assertEqual(txtdata, TEXT_SAMPLE)

        # test 2
        with self.assertRaises(FileNotFoundError):
            self.non_txthandler.writeNew(TEXT_SAMPLE)
            txtdata = self.non_txthandler.readContent('read')


class TestJsonHandler(unittest.TestCase):
    def setUp(self):
        self.middirname = 'jsonfiles'
        self.json_path = rf'..\testdata\{self.middirname}\myjson.json'
        self.json_handler = fdh.JsonFileHandler(self.json_path)

        self.middirname2 = 'nonjsonfiles'
        self.non_json_path = rf'..\testdata\{self.middirname2}\myjson.json'
        self.non_json_handler = fdh.JsonFileHandler(
            self.non_json_path, create_dir_ok=False
        )

        self.json_data = {
            "user": "나이썬",
            "details": {
                "serialNumber": 5,
                "age": 25,
                "main job": "프리랜서 개발자",
                "second job": "배달",
                "hobby" : [
                    "유튜브 보기", "넷플릭스 보기", "헬스"
                ]
            }
        }
    
    def tearDown(self):
        shutil.rmtree(os.path.dirname(self.json_path), True)
        shutil.rmtree(os.path.dirname(self.non_json_path), True)

    def testCreateJsonFile(self):
        # test 1
        self.json_handler.createJsonFile()
        self.assertTrue(os.path.exists(self.json_path))
        self.assertTrue(os.path.exists(os.path.dirname(self.json_path)))
        self.assertTrue(os.path.isfile(self.json_path))
        
        # test 2
        with self.assertRaises(FileNotFoundError):
            self.non_json_handler.createJsonFile()
        self.assertFalse(os.path.exists(self.non_json_path))

    def testWrite(self):
        # test 1
        self.json_handler.write(self.json_data)

        # json 데이터 가져오기
        with open(self.json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertEqual(data, self.json_data)

        # test 2
        with self.assertRaises(FileNotFoundError):
            self.non_json_handler.write(self.json_data)

    def testRead(self):
        # test 1
        # json 파일 생성 및 데이터 입력
        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(self.json_data, f)
        
        data = self.json_handler.read()
        self.assertEqual(data, self.json_data)

        # test 2
        with self.assertRaises(FileNotFoundError):
            data = self.non_json_handler.read()


class TestMakePackage(unittest.TestCase):
    """make_package() 함수 테스트."""
    def setUp(self):
        self.basedir = r"..\testdata\makepkg"

    def tearDown(self):
        shutil.rmtree(self.basedir)

    def testMakePackage(self):
        """사용자가 원하는 대로 최상위 디렉토리와 그 아래 
        여러 하위 디렉토리 및 파일들이 제대로 생성되는지 테스트.
        """
        entities = [
            'README.md', 'subdir\\hi.txt', 'subdir\\submods\\my_python.py',
            'logfiles\\debug.log',
        ]
        fdh.make_package(self.basedir, entities)

        self.assertTrue(os.path.exists(self.basedir))
        for en in entities:
            fullpath = os.path.join(self.basedir, en)
            self.assertTrue(os.path.exists(fullpath))
            if os.path.splitext(en):
                self.assertTrue(os.path.isfile(fullpath))
            else:
                self.assertTrue(os.path.isdir(fullpath))


class TestZip(unittest.TestCase):
    """make_zip_structure(), decompress_zip() 함수 테스트."""
    def setUp(self):
        self.test_root_dir_path = "..\\testdata\\zippkg"
        self.test_root_dirname = os.path.basename(self.test_root_dir_path)
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
        if not os.path.exists(self.test_root_dir_path):
            fdh.make_package(self.test_root_dir_path, self.testdata_path)

        self.zip_filename = 'myzip.zip'

        self.extract_path = '..\\testdata\\zipresult'
        os.makedirs(self.extract_path, exist_ok=True)
        
        self.save_path = r"..\testdata\savezip"  # zip 파일 저장 경로
        os.makedirs(self.save_path, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_root_dir_path)
        shutil.rmtree(self.extract_path)
        shutil.rmtree(self.save_path)

    def testMakeZipStructure(self):
        """make_zip_structure() 함수로 특정 루트 디렉토리 
        내부의 구조 그대로 압축하는 지 테스트.
        """
        # test
        # 압축할 대상 루트 디렉토리를 압축한 zip 파일을 해당 루트 디렉토리 
        # 안에 넣을 경우.
        fdh.make_zip_structure(
            self.test_root_dir_path,
            self.zip_filename,
            self.test_root_dir_path
        )

        zippath = os.path.join(self.test_root_dir_path, self.zip_filename)
        with zipfile.ZipFile(zippath) as zf:
            zf.extractall(self.extract_path)
        leaf_path = dirs.get_all_in_rootdir(
            os.path.join(self.extract_path, self.test_root_dirname), False
        )
        leaf_path = dirs.sort_length_order(leaf_path)

        for i, lp in enumerate(leaf_path):
            self.assertEqual(
                lp,
                self.testdata_path[i]
            )
            self.assertTrue(not lp.endswith('.zip'))

    def testDecom(self):
        """decompress_zip() 함수 테스트"""
        fdh.make_zip_structure(
            self.test_root_dir_path,
            self.zip_filename,
            self.save_path
        )
        zippath = os.path.join(self.save_path, self.zip_filename)
        fdh.decompress_zip(zippath, self.extract_path)
        leaf_path = dirs.get_all_in_rootdir(
            os.path.join(self.extract_path, self.test_root_dirname), False
        )
        leaf_path = dirs.sort_length_order(leaf_path)

        for i, lp in enumerate(leaf_path):
            self.assertEqual(
                lp,
                self.testdata_path[i]
            )


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
    #test_only(TestTxtHandler('testAppendText'))
    #test_only(TestMakePackage)
    #test_only(TestZip)
