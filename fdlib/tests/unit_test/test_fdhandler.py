import unittest
import sys
import os

from dirimporttool import get_super_dir_directly

for i in range(1, 2+1):
    super_dir = get_super_dir_directly(__file__, i)
    sys.path.append(super_dir)

import fdhandler as fdh

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
        self.fixture_txtpath = r'..\fixtures\testtext.txt'
        self.txthandler = fdh.TextFileHandler(self.fixture_txtpath)
        self.onoff_teardown: bool = True

    def tearDown(self):
        if self.onoff_teardown:
            try:
                os.remove(self.fixture_txtpath)
            except FileNotFoundError:
                pass

    def testCreateTxtFile(self):
        """지정된 경로에 텍스트 파일이 생성되었는지 확인하는 테스트."""
        self.onoff_teardown = True
        self.txthandler.createTxtFile()
        self.assertTrue(os.path.exists(self.fixture_txtpath))
        self.assertTrue(os.path.isfile(self.fixture_txtpath))

    def testWriteNew(self):
        """지정된 경로에 생성한 텍스트 파일에 텍스트가 삽입되었는지 테스트."""
        self.onoff_teardown = True
        self.txthandler.writeNew(TEXT_SAMPLE)
        with open(self.fixture_txtpath, 'r', encoding='utf-8') as f:
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
        with open(self.fixture_txtpath, 'r', encoding='utf-8') as f:
            txtdata = f.read()
        self.assertNotIn(sample_txt, txtdata)
        self.assertEqual(txtdata, TEXT_SAMPLE)

    def testAppendText(self):
        """지정된 경로에 존재하는 텍스트 파일에 이어쓰기가 되는지 테스트."""
        self.onoff_teardown = True
        self.txthandler.writeNew(TEXT_SAMPLE)
        additional_text = "테스트 글!"
        self.txthandler.appendText(additional_text)
        with open(self.fixture_txtpath, 'r', encoding='utf-8') as f:
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


if __name__ == '__main__':
    def test_only(casename):
        """
        Parameters
        ----------
        casename : callable
            테스트 하고자 하는 테스트 클래스명 또는 메서드명
        
        """
        suite_obj = unittest.TestSuite()
        suite_obj.addTest(casename)

        runner = unittest.TextTestRunner()
        runner.run(suite_obj)

    unittest.main()
    #test_only(TestTxtHandler('testAppendText'))
