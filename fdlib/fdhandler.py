"""파일 및 디렉토리 조작 관련 기능 모음 모듈.
기존 os 모듈을 통해 파일 및 디렉토리 조작을 위한 코드들을 
캡슐화하여 사용자가 조금 더 사용하기 편리하게 하기 위함.

"""
from typing import Literal


class TextFileHandler():
    """텍스트 파일 관련 클래스."""
    def __init__(
            self, 
            txtfilepath: str = '',
            encoding: str = 'utf-8'
        ):
        """
        Instance Attributes
        -------------------
        self.txtfilepath : str
            텍스트 파일 경로.
        
        """
        self.txtfilepath = txtfilepath
        self.encoding = encoding

    def setTxtFilePath(self, new_txtpath: str):
        self.txtfilepath = new_txtpath

    def getTxtFilePath(self):
        return self.txtfilepath

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
