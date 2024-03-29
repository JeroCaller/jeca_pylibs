"""파일 및 디렉토리 조작 관련 기능 모음 모듈.
기존 os 모듈을 통해 파일 및 디렉토리 조작을 위한 코드들을 
캡슐화하여 사용자가 조금 더 사용하기 편리하게 하기 위함.

"""
import os
import json
import zipfile
import shutil
from typing import Literal


class TextFileHandler():
    """텍스트 파일 관련 클래스."""
    def __init__(
            self, 
            txtfilepath: str = '',
            encoding: str = 'utf-8',
            create_dir_ok: bool = True
        ):
        """
        Parameters
        -------------------
        txtfilepath : str
            텍스트 파일 경로.
        create_dir_ok : bool, default True
            txtfilepath 매개변수로 주어진 경로 중간의 디렉토리가 실존하지 않는 경우, 
            이를 자동으로 생성하게끔 할 것인지를 묻는 매개변수.
            True 시 실존하지 않는 중간 디렉토리를 자동 생성해준다. 
            False 시 해당 작업이 실행되지 않으며, 이 상태에서 해당 경로에 텍스트 파일
            입출력 시도 시 FileNotFoundError 예외가 발생한다.
        
        """
        self.txtfilepath = txtfilepath
        self.encoding = encoding
        self.create_dir_ok = create_dir_ok

        self._createSuperDirs()
        self._attachExt()

    def setTxtFilePath(self, new_txtpath: str):
        self.txtfilepath = new_txtpath
        self._createSuperDirs()
        self._attachExt()

    def getTxtFilePath(self):
        return self.txtfilepath
    
    def _createSuperDirs(self):
        if not self.txtfilepath or not self.create_dir_ok: return
        dirname = os.path.dirname(self.txtfilepath)
        if dirname:
            os.makedirs(dirname, exist_ok=True)

    def _attachExt(self):
        if (not self.txtfilepath or 
            os.path.splitext(self.txtfilepath)[-1]): return
        if not self.txtfilepath.endswith('.txt'):
            self.txtfilepath += '.txt'

    def createTxtFile(self):
        """텍스트 파일을 생성하기만 하고자 할 경우 사용하는 메서드."""
        with open(self.txtfilepath, 'w', encoding=self.encoding):
            pass

    def writeNew(self, content: str):
        """정해진 텍스트 파일에 텍스트를 삽입힌다.
        이 때, 기존의 텍스트는 모두 사라지고 새로 삽입할 
        텍스트만 기록된다.

        Parameters
        ----------
        content : str
            텍스트 파일에 삽입하고자 하는 텍스트.

        """
        with open(self.txtfilepath, 'w', encoding=self.encoding) as f:
            f.write(content)

    def appendText(self, content: str):
        """정해진 텍스트 파일 내 텍스트 내용에 이어서 작성.

        Parameters
        ----------
        content : str
            텍스트 파일에 삽입하고자 하는 텍스트.
        
        """
        with open(self.txtfilepath, 'a', encoding=self.encoding) as f:
            f.write(content)

    def readContent(
            self,
            read_mode: Literal['read', 'readline', 'readlines']
        ):
        """텍스트 파일 내 내용을 읽어 오고, 그 내용을 반환한다.

        Parameters
        ----------
        read_mode : Literal['read', 'readline', 'readlines']

        Returns
        -------
        str | list[str] | None
            매개변수 read_mode가 'read', 'readline', readlines' 중 
            하나라도 해당이 안될 경우 None 반환.

        """
        with open(self.txtfilepath, 'r', encoding='utf-8') as f:
            if read_mode == 'read':
                return f.read()
            if read_mode == 'readline':
                return f.readline()
            if read_mode == 'readlines':
                return f.readlines()
        return None


class JsonFileHandler():
    """Json 파일 입출력 클래스."""
    def __init__(
            self,
            json_file_path: str = '',
            encoding: str = 'utf-8',
            create_dir_ok: bool = True
        ):
        """
        Parameters
        ----------
        json_file_path : str
            json 파일 경로.
        create_dir_ok : bool, default True
            txtfilepath 매개변수로 주어진 경로 중간의 디렉토리가 실존하지 않는 경우, 
            이를 자동으로 생성하게끔 할 것인지를 묻는 매개변수.
            True 시 실존하지 않는 중간 디렉토리를 자동 생성해준다. 
            False 시 해당 작업이 실행되지 않으며, 이 상태에서 해당 경로에 텍스트 파일
            입출력 시도 시 FileNotFoundError 예외가 발생한다.
        
        """
        self.json_file_path = json_file_path
        self.encoding = encoding
        self.create_dir_ok = create_dir_ok
        self.indent = 4

        self._createSuperDirs()
        self._attachExt()

    def setJsonFilePath(self, new_json_path: str):
        self.json_file_path = new_json_path
        self._createSuperDirs()
        self._attachExt()

    def getJsonFilePath(self):
        return self.json_file_path
    
    def _createSuperDirs(self):
        if not self.json_file_path or not self.create_dir_ok: return
        dirname = os.path.dirname(self.json_file_path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)

    def _attachExt(self):
        if not self.json_file_path.endswith('.json'):
            self.json_file_path += '.json'

    def createJsonFile(self):
        """Json 파일을 생성하기만 하고자 할 경우 사용하는 메서드."""
        with open(self.json_file_path, 'w', encoding=self.encoding) as f:
            pass

    def write(self, json_data):
        """지정된 json 파일에 json 데이터로 변환할 파이썬 객체를 
        입력하면 이를 해당 json 파일에 저장하는 기능. 
        json.dump() 기능과 동일.
        """
        with open(self.json_file_path, 'w', encoding=self.encoding) as f:
            json.dump(json_data, f, indent=self.indent)

    def read(self):
        """지정된 json 파일로부터 json 데이터를 얻어온다.
        json.load()와 동일.

        Returns
        -------
        data : json.load()

        """
        with open(self.json_file_path, 'r', encoding=self.encoding) as f:
            data = json.load(f)
        return data
    

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
    

def make_package(base_dir: str, entities: list[str]) -> (None):
    """패키지 디렉토리를 생성하는 함수. 

    Parameters
    ----------
    base_dir : str
        생성하고자 하는 패키지의 최상위 디렉토리의 절대 경로. 
        해당 디렉토리는 실존하지 않아도 이 함수에서 자동으로 생성함.
    entities : list[str]
        base_dir 매개변수로 지정한 최상위 디렉토리 안에 생성할 하위 
        디렉토리 및 파일들의 경로. 경로를 이 매개변수에 대입 시에 
        base_dir의 절대 경로를 포함하여 넣지 말 것. 

    Examples
    --------

    생성하고자 하는 패키지 구조가 다음과 같다고 해보자.

    my_package/
        README.md
        subdir/
            hi.txt
            submods\
                my_python.py
        logfiles\
            debug.log

    base_dir 매개변수 대입 예)
    base_dir = 'C:\\projects\\test\\my_package

    entities 매개변수 대입 예)
    entities = [
        'README.md', 'subdir\\hi.txt', 'subdir\\submods\\my_python.py',
        'logfiles\\debug.log',
    ]
    
    """
    os.makedirs(base_dir, exist_ok=True)

    for en in entities:
        fullpath = os.path.join(base_dir, en)
        if os.path.splitext(fullpath)[1]:
            super_dir = os.path.split(fullpath)[0]
            os.makedirs(super_dir, exist_ok=True)
            with open(fullpath, 'w', encoding='utf-8'): pass
        else:
            os.makedirs(fullpath, exist_ok=True)

def rmtree_except_root(target_dir: str):
    """주어진 루트 디렉토리에 대해, 루트 디렉토리 자체는 
    삭제하지 않고 내부의 모든 파일, 디렉토리들만 삭제하는 함수. 
    shutil.rmtree() 함수는 루트 디렉토리까지 모두 삭제하기에 대안으로 만든 함수. 

    Parameters
    ----------
    target_dir : str
        내부의 모든 파일, 디렉토리들을 삭제하고자 하는 루트 디렉토리. 
    
    """
    for entity in os.listdir(target_dir):
        entity_path = os.path.join(target_dir, entity)
        if os.path.isdir(entity_path):
            shutil.rmtree(entity_path)
        else:
            os.remove(entity_path)

def make_zip_structure(
        rootdir: str,
        zip_filename: str,
        target_dir: str,
        exclude_zip: bool = True
    ):
    """zip 파일로 압축하고자 하는 루트 디렉토리 경로를 입력하면 
    해당 디렉토리 내 구조를 그대로 유지한 채로 압축해주는 함수.

    zip 파일로 압축한 뒤, 루트 디렉토리와 내부 파일, 디렉토리들은 
    삭제되지 않고 그대로 보존된다. 

    Parameters
    ----------
    rootdir : str
        zip 파일로 압축하고자 하는 루트 디렉토리의 경로.
    zip_file_path : str
        zip 파일명.
        ex) 'zipfile.zip'
    target_dir : str
        zip 파일을 저장할 경로. 해당 경로가 존재해야 한다. 
        존재하지 않으면 FileNotFoundError가 발생한다. 
    exclude_zip : bool, default True
        만약 루트 디렉토리 안에 zip 파일이 존재하면 해당 파일도 
        같이 압축할 것인지 아니면 배제할 것인지에 대한 매개변수. 
        True 시 내부의 모든 zip 파일들은 제외되고 나머지 파일, 
        디렉토리들만 압축 대상이 된다. 
        False 시 루트 디렉토리 내부의 zip 파일도 같이 압축된다.
    
    """
    
    # dirsearch.py 모듈로부터 가져옴. 
    # dirsearch.py 모듈과의 독립성을 유지하기 위해 
    # 일부러 해당 함수 코드를 그대로 가져와 여기에 정의함.
    def get_all_in_rootdir(
            root_dir: str, 
            to_abspath: bool = True
        ) -> (list[str]):
        """루트 디렉토리 경로가 주어지면 해당 디렉토리 내 
        모든 파일들과 leaf 디렉토리의 경로들을 리스트로 묶어 반환.

        Parameters
        ----------
        root_dir : str
            루트 디렉토리 경로
        to_abspath : bool, default True
            루트 디렉토리 내 하위 파일 및 디렉토리들의 경로를 절대경로 또는 
            상대경로로 반환할 지 결정하는 매개변수. 
            True 시 절대경로로 반환한다.
            False 시 상대경로로 반환한다. 여기서 상대경로는 해당 절대경로에서 
            root_dir로 지정된 루트 디렉토리의 절대경로를 뺀 경로이다.

        Returns
        -------
        list[str]
            루트 디렉토리 내 모든 최하위 파일 및 디렉토리들의 절대경로의 
            리스트.
        
        """
        results: list[str] = []
        root_dir = os.path.abspath(root_dir)
        
        def search(dirpath: str):
            entities = os.listdir(dirpath)
            if not entities:
                # leaf 디렉토리인 경우, 해당 디렉토리 경로를
                # 결과에 추가한다.
                if dirpath != root_dir:
                    results.append(dirpath)
                return
            for entity in entities:
                if os.path.splitext(entity)[1]:
                    # 해당 entity가 파일일 경우.
                    results.append(os.path.join(dirpath, entity))
                else:
                    # 해당 entity가 디렉토리일 경우.
                    subdir_path = os.path.join(dirpath, entity)
                    search(subdir_path)

        search(root_dir)

        if not to_abspath:
            for i, res in enumerate(results):
                results[i] = os.path.relpath(res, root_dir)
        
        return results
    
    leaf_path = get_all_in_rootdir(rootdir)
    if not zip_filename.endswith('.zip'):
        zip_filename += '.zip'
    zip_path = os.path.join(target_dir, zip_filename)
    with zipfile.ZipFile(zip_path, 'w') as zf:
        root_dirname = os.path.dirname(rootdir)
        for p in leaf_path:
            if exclude_zip and p.endswith('.zip'): continue
            zf.write(
                p,
                os.path.relpath(p, root_dirname)
            )

def decompress_zip(zippath: str, target_path: str):
    """zip 파일을 압축 해제하여 이를 지정된 경로 내에 
    저장하는 함수. 

    Parameters
    ---------
    zippath : str
        압축 해제하고자 하는 zip 파일 경로.
    target_path : str
        압축 해제한 결과물을 저장할 경로.
    
    """
    with zipfile.ZipFile(zippath) as zf:
        zf.extractall(target_path)
