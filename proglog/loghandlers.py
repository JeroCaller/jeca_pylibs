"""기존 logging.handlers 모듈의 일부 코드를 상속하여 변경한 핸들러 모음."""

import os
from logging.handlers import RotatingFileHandler


class CustomRotatingFileHandler(RotatingFileHandler):
    """새 로그 파일 생성 시 해당 파일 명에 추가되는 넘버링 방식을 변경한 핸들러 클래스.
    기본 넘버링 방식은 다음과 같음.
    ex) mylog (1).log

    로그 파일명 넘버링 방식 외의 다른 모든 부분은 기존 
    logging.handlers.RotatingFileHandler 핸들러 클래스와 동일함.

    """
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0,
                 encoding=None, delay=False, errors=None):
        super().__init__(
            filename, mode, maxBytes, backupCount,
            encoding, delay, errors
            )
        self.filename_delimiter = ' '  # 새 로그 파일 숫자 부여 시 이전 이름과 구분하는 용도.

    def _modifyFilename(self, filename: str):
        if filename[:-4].find('.log') != -1:
            filename = filename.replace('.log', '')
            if not filename.endswith('.log'):
                filename += '.log'
        return filename

    def doRollover(self):
        """
        Do a rollover, as described in __init__().
        """
        # 새로 생성되는 파일 이름의 네이밍 방식 변경.

        if self.stream:
            self.stream.close()
            self.stream = None
        if self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                sfn = f"{self.baseFilename}{self.filename_delimiter}({i})"
                dfn = f"{self.baseFilename}{self.filename_delimiter}({i+1})"
                sfn = self._modifyFilename(sfn)
                dfn = self._modifyFilename(dfn)
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            dfn = f"{self.baseFilename}{self.filename_delimiter}(1)"
            dfn = self._modifyFilename(dfn)
            if os.path.exists(dfn):
                os.remove(dfn)
            os.rename(self.baseFilename, dfn)
        if not self.delay:
            self.stream = self._open()

