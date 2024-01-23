"""테스트 모듈들에서 사용할 함수, 클래스 등 기능 모음."""

import sys
import os
import time

from dirimporttool import get_super_dir_directly

for i in range(1, 2+1):
    super_dir = get_super_dir_directly(__file__, i)
    sys.path.append(super_dir)

from sub_modules.fdhandler import TextFileHandler

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

def get_datedir_filenames(
        leaf_entities: list[str],
    ) -> (dict[str, list[str]]):
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
        datedir = os.path.basename(os.path.dirname(en))
        filename = os.path.basename(en)
        if datedir not in results:
            results[datedir] = [filename]
        elif filename not in results[datedir]:
            results[datedir].append(filename)
    return results

def test_only_one(test_classname):
    try:
        suite_obj = unittest.TestSuite()
    except NameError:
        import unittest
        suite_obj = unittest.TestSuite()
    
    try:
        suite_obj.addTest(unittest.makeSuite(test_classname))
    except TypeError:
        suite_obj.addTest(test_classname)

    runner = unittest.TextTestRunner()
    runner.run(suite_obj)


class WorkCWD():
    """실행하고자 하는 파이썬 스크립트 내에 상대경로로 
    디렉토리, 파일을 조작하는 기능이 존재할 경우, 
    엉뚱한 경로로 지정되어 엉뚱한 결과를 내는 것을 방지하기 위해 
    현재 작업 디렉토리도 해당 파이썬 스크립트가 들어있는 디렉토리 
    경로로 바꾼 후, 실행한 후에 작업이 끝나면 다시 원래 작업 디렉토리로 
    변경해주는 클래스 데코레이터.
    """
    def __init__(self, curdir: str):
        """
        Parameters
        ----------
        curdir : str
            현재 파일의 경로 입력 (__file__을 입력해도 됨)
        
        """
        self.current_dir = os.path.dirname(curdir)

    def __call__(self, calla):
        def wrapper(*args, **kwargs):
            original_dir = os.getcwd()
            if original_dir != self.current_dir:
                os.chdir(self.current_dir)
            return_value = calla(*args, **kwargs)
            os.chdir(original_dir)
            return return_value
        return wrapper
