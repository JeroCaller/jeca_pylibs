"""파일 및 디렉토리 조작 관련 기능 모음 모듈.
기존 os 모듈을 통해 파일 및 디렉토리 조작을 위한 코드들을 
캡슐화하여 사용자가 조금 더 사용하기 편리하게 하기 위함.

"""
import os
import json
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