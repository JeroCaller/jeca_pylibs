"""

함수 내에 깊이를 알 수 없는 중첩 함수들이 있을 때 
예외를 로깅하려면 다음과 같이 처리.
예)
import logging

error_logger = logging.getLogger()
error_logger.setLevel(logging.ERROR)

try:
    main()
except Exception as e:
    error_logger.exception(e)


"""

import logging
import logexp
from sub_modules.tree import PathTree
from sub_modules.tree import (ALPHABET, LENGTH, AbsPath, SortMode)


# 로깅 관련 데코레이터 클래스들.
class LogFuncEndPoint():
    def __init__(self, logger_obj: logging.Logger):
        """
        특정 함수 또는 메서드의 호출 시작과 작업 종료 사실을 
        로깅해주는 데코레이터.

        매개변수
        -------
        logger_obj: 로깅하는 모듈 내에서 정의된 Logger 객체. 
        해당 로거 객체의 최소 level이 적어도 INFO 이하로 지정되어야 함. 
        그래야 해당 로거 객체에 연결된 파일 대상에 로그 기록 가능. 
        """
        self.logger = logger_obj
        if self.logger.getEffectiveLevel() > logging.INFO:
            raise logexp.LogLowestLevelError(
                current_level=self.logger.getEffectiveLevel(), 
                required_level=logging.INFO
            )

    def __call__(self, func: callable):
        def wrapper(*args, **kwargs):
            self.logger.info(f"{func.__name__} 함수(메서드) 호출됨.")
            return_value = func(*args, **kwargs)
            self.logger.info(f"{func.__name__} 함수(메서드) 작업 종료.")
            return return_value
        return wrapper
    

class DetectErrorAndLog():
    def __init__(self, logger_obj: logging.Logger):
        """
        특정 함수 또는 메서드 내에서 발생할 수 있는 모든 예외 메시지를 
        로그에 기록하는 데코레이터. 

        매개변수
        -------
        logger_obj: 로깅하는 모듈 내에서 정의된 Logger 객체. 
        해당 로거 객체의 최소 level이 적어도 INFO 이하로 지정되어야 함. 
        그래야 해당 로거 객체에 연결된 파일 대상에 로그 기록 가능. 
        """
        self.logger = logger_obj
        if self.logger.getEffectiveLevel() > logging.ERROR:
            raise logexp.LogLowestLevelError(
                self.logger.getEffectiveLevel(),
                logging.ERROR
            )

    def __call__(self, func: callable):
        def wrapper(*args, **kwargs):
            try:
                return_value = func(*args, **kwargs)
            except Exception as e:
                self.logger.exception(e)
            else:
                return return_value
        return wrapper
    

# LoggerWHT 클래스 전용. 
class LoggerPathTree(PathTree):
    def __init__(
            self, 
            default_root: bool = True, 
            delimiter: str = '.',
            always_raise_error: bool = False
        ):
        default_root = True
        super().__init__(default_root, delimiter, always_raise_error)
        self._adj_list = {}
        self._root = '<root>'
        self._adj_list[self._root] = []

    def getAllLeafAbs(
            self, 
            how_to_sort: SortMode = ALPHABET, 
            ascending: bool = True
        ) -> (list[AbsPath]):
        super_results = super().getAllLeafAbs(how_to_sort, ascending)
        new_results = []
        for data in super_results:
            new_path = data.replace('<root>.', '')  # 절대경로에 "<root>" 부분은 안 나오게 함.
            new_results.append(new_path)
        return new_results

    def clear(self):
        super().clear()
        self.append('<root>')

    def lenTree(self): return super().lenTree() - 1


class LoggerWHT(logging.Logger):
    logtree = LoggerPathTree(default_root=True, always_raise_error=False)

    def __init__(self, name: str | None = None, level: int = 0):
        """
        Logger With Hierarchy Tracker. 
        로거 객체의 계층 구조도 저장하는 로거 클래스. 
        그 외 모든 부분은 logging.Logger 객체와 동일. 
        로거 객체 이름 부여 시 계층을 구분해주는 기호는 마침표 '.'로 통일해야함. 
        """
        new_named_root = LoggerWHT.logtree.getRoot()
        if name is None or name == '': name = 'root'
        super().__init__(name, level)
        if LoggerWHT.logtree.delimiter in name:
            fullpath = LoggerWHT.logtree.combineNodesToAbsPath(new_named_root, name)
            LoggerWHT.logtree.appendAbs(fullpath)
        else:
            LoggerWHT.logtree.append(name, new_named_root)

    def clear(self):
        """
        여태 입력했던 모든 로거 객체 이름들을 초기화하고 싶을 때 사용.
        """
        LoggerWHT.logtree.clear()


class DebugLogger():
    def __init__(self):
        """
        패키지 내 특정 함수, 메서드의 특정 지역변수를 로깅하고자 할 때 사용하는 클래스. 
        """
        ...

if __name__ == '__main__':
    pass
    