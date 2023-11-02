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

import os
import inspect
import logging
from typing import Literal, TypeAlias

import logexc
from sub_modules.tree import PathTree
from sub_modules.tree import AbsPath

# type aliases
NoneType: TypeAlias = Literal['NoneType']
LoggerLevel: TypeAlias = int

# 상수 정의
ALLFILES = 0
DEBUGFILE = 1
ERRORFILE = 2
LOGGERFILE = 3
WhichFile: TypeAlias = Literal[0, 1, 2, 3]

LOGGERTREE = 4
SpecialLoggerType: TypeAlias = Literal[4]


def makedir(superdirpath: str, dirname: str):
    """
    특정 위치에 디렉토리를 생성하는 함수. 
    폴더를 생성하고자 하는 상위 디렉토리 주소를 superdirpath에, 
    생성하고자 하는 폴더 이름을 dirname에 지정한다. 
    만약 superdirpath로 대입한 디렉토리 주소가 존재하지 않는다면 
    FileNotFoundError가 발생함. 

    사용 예)
    >>> makedir("C:/super_dir", "sub_dir")
    C:/super_dir/sub_dir

    """
    fullpath = os.path.join(superdirpath, dirname)
    try:
        os.mkdir(fullpath)
    except FileExistsError:
        return fullpath
    return fullpath


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
        if self.logger.level > logging.INFO:
            raise logexc.LogLowestLevelError(
                current_level=logging.getLevelName(self.logger.level),
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
        if self.logger.level > logging.ERROR:
            raise logexc.LogLowestLevelError(
                logging.getLevelName(self.logger.level),
                logging.ERROR
            )

    def __call__(self, func: callable):
        def wrapper(*args, **kwargs):
            try:
                return_value = func(*args, **kwargs)
            except Exception as e:
                self.logger.exception(e)
                return None
            return return_value
        return wrapper
# ================


class _LoggerPathTree(PathTree):
    def __init__(
            self,
            default_root: bool = True,
            delimiter: str = '.',
            always_raise_error: bool = False
        ):
        default_root = True  # 강제로 True로 전환하여 항상 트리에 <root>가 있게 함.
        super().__init__(default_root, delimiter, always_raise_error)
        self._adj_list = {}
        self._root = 'root'
        self._adj_list[self._root] = []

    def appendAbs(self, new_path: AbsPath, raise_error: bool = False):
        if not self.isAbsPath(new_path):
            if new_path == 'root':
                return None
            self.append(new_path, 'root')
            return None
        if not new_path.startswith('root' + self._delimiter):
            new_path = self._delimiter.join(['root', new_path])
        return super().appendAbs(new_path, raise_error)

    def clear(self):
        super().clear()
        self.append('root')


class _LoggerHierarchy():
    def __init__(self):
        """
        현재 등록된 모든 로거 객체들의 이름을 계층을 가진 트리로 보여주는 클래스. 
        """
        self._root_logger = logging.getLogger()
        self._logger_dict: dict[str, logging.Logger] = {}
        self._ptree = _LoggerPathTree()

        self.updateLoggerInfo()

    def _getCurrentLoggers(self):
        """
        현재까지 등록된 모든 로거 객체들의 정보를 받아온다. 
        기존 로거 객체 정보가 있다면 모두 리셋시키고 새로 받아온다. 
        """
        self._logger_dict = self._root_logger.manager.loggerDict.copy()

        # logger_dict에서 불필요한 정보는 필터링함.
        temp_dict = {}
        for k, v in self._logger_dict.items():
            if k.startswith('pkg_'): continue
            temp_dict[k] = v
        self._logger_dict = temp_dict.copy()

    def _getInfoHierarchy(self):
        """
        현재까지 등록된 모든 로거 객체들의 이름들을 트리로 구성. 
        """
        self._ptree.clear()
        for k in self._logger_dict.keys():
            self._ptree.appendAbs(k)

    def updateLoggerInfo(self):
        """
        지금까지 생성된 모든 로거 객체들의 정보를 이 객체에 업데이트. 
        """
        self._getCurrentLoggers()
        self._getInfoHierarchy()

    def getLoggerTree(self):
        """
        현재까지 등록된 로거 객체들의 계층 트리를 문자열로 반환. 
        중간에 새로운 로거 객체들을 생성한 경우, updateLoggerInfo() 메서드 
        호출로 새로고침 필요. 
        """
        return self._ptree.getTreeStructure()

    def getLeafLoggersName(self):
        """
        현재까지 등록된 모든 로거 객체들의 계층 트리에서 
        leaf 로거 이름만을 반환. 
        중간에 새로운 로거 객체들을 생성한 경우, updateLoggerInfo() 메서드 
        호출로 새로고침 필요. 
        """
        return self._ptree.getAllLeafAbs()

    def getNumberofNodes(self):
        """
        로거 객체 계층 트리 내 노드의 수 반환. 
        """
        return self._ptree.lenTree()


class PackageLogger():
    _this_instance = None
    _is_initialized: bool = False

    def __new__(cls, *args, **kwargs):
        if cls._this_instance is None:
            cls._this_instance = super().__new__(cls)
        return cls._this_instance

    def __init__(
            self,
            current_module_abspath: str | None = None
        ):
        """
        패키지 내 특정 함수, 메서드의 특정 지역변수를 로깅하고자 할 때 사용하는 클래스. 

        매개변수
        -----
        current_module_abspath: 패키지 내 모듈 중 최상위 모듈(ex) main.py)의 절대경로. 
        해당 모듈에서 '__file__'을 대입하면 됨. 처음 해당 클래스를 인스턴스화한 후에는 
        해당 매개변수에 값을 대입 안해도 됨. 
        None 입력 시 기본으로 지정된 주소에 디렉토리 형성. 
        """
        if PackageLogger._is_initialized is False:
            if current_module_abspath is None: return
            self._delimiter = '.'
            self._lh = _LoggerHierarchy()
            self._root_logger = logging.getLogger()
            self._root_logger.setLevel(logging.DEBUG)
            self.current_module_abspath = current_module_abspath
            self._log_hierarchy_logger_name = "__log_hierarchy__"  # 로거 계층 구조 로깅 전용 로거 이름.
            self._debug_logger_name = "__debug__"  # 디버그 로거 객체들의 상위 로거 객체 이름.
            self._error_logger_name = "__error__"  # 에러 로거 객체들의 상위 로거 객체 이름.
            self._info_logger_name = "__info__"  # info 로거 객체들의 상위 로거 객체 이름.

            self.debug_log_file_path, self.error_log_file_path, self.hierarchy_log_file_path \
                = self._defaultSetLogDirFile()
            self._setLoggerEnvironment()
            self._lh.updateLoggerInfo()

            PackageLogger._is_initialized = True

    def _defaultSetLogDirFile(self):
        """
        로그 파일명, 로그 파일들을 담을 디렉토리의 이름 및 경로 설정 등에 대해 
        이 메서드에서의 설정을 디폴트 설정으로 하고 디폴트 설정한다. 
        """
        if self.current_module_abspath is None: return None
        logfilesdirname = "logfiles"  # 로그 파일을 담을 폴더명.
        logdir = os.path.dirname(self.current_module_abspath)  # 로그 파일들을 담을 폴더를 생성할 주소.
        logdirfullpath = makedir(logdir, logfilesdirname)

        debug_log_file_name = 'debug.log'
        debug_log_file_path = os.path.join(logdirfullpath, debug_log_file_name)
        error_log_file_name = 'error.log'
        error_log_file_path = os.path.join(logdirfullpath, error_log_file_name)
        tree_log_file_name = 'logger_tree.log'
        tree_log_file_path = os.path.join(logdirfullpath, tree_log_file_name)

        return debug_log_file_path, error_log_file_path, tree_log_file_path

    def logVariable(self, var_str: str):
        """
        특정 함수 또는 메서드 내 로깅하고자 하는 특정 지역 변수 이름을 문자열로 대입하면 
        해당 변수값을 로깅해주는 메서드. 
        해당 메서드는 특정 함수(또는 메서드) 안에 작성하면 해당 함수의 이름과 
        메서드의 경우 해당 메서드가 포함된 클래스명까지 자동으로 얻는다. 

        사용 예) 
        >>> def calculator(a: int, b: int):
        ...     results = []
        ...     result = a + b
        ...     results.append(result)
        ...     result = a * b
        ...     results.append(result)

        위 예시 코드에서, calculator 함수 내 지역 변수인 result를 로깅하고자 한다면 
        다음과 같이 작성. 
        >>> from logpackage import DebugLogger
        >>> dl = DebugLogger()
        >>> def calculator(a: int, b: int):
        ...     results = []
        ...     result = a + b
        ...     dl.logVariable('result')
        ...     results.append(result)
        ...     result = a * b
        ...     dl.logVariable('result')
        ...     results.append(result) 

        만약 var_str로 대입된 변수를 찾지 못한다면 로깅 파일에 <The Variables Not Found>
        이라는 메시지가 대신 로깅됨. 

        만약 클래스 내 __init__에서 정의된 self. 로 시작되는 인스턴스 변수를 추적하여 
        로깅하고자 한다면 var_str에 'self.변수' 형식이 아닌 '변수' 형식으로 대입해야 함. 
        이 때, __init__에 정의되지 않은 self.로 시작되는 인스턴스 변수는 추적, 로깅이 안됨. 
        """
        target_frame = inspect.stack()[1]
        method_name = target_frame.function
        local_data = target_frame.frame.f_locals
        class_name = local_data.get('self', None).__class__.__name__
        current_module_name = inspect.getmodulename(target_frame.filename)
        current_lineno = target_frame.lineno
        not_found_msg = "<The Variables Not Found>"
        target_var_value = local_data.get(var_str, not_found_msg)

        # 로깅하려는 곳이 클래스의 인스턴스 메서드일 때, 로깅하려는 변수가
        # __init__ 메서드에서 정의된 self. 으로 시작되는 인스턴스 변수일 경우
        # __init__ 스페셜 메서드가 아닌 일반 인스턴스 메서드에서는 인스턴스 변수가
        # 위와 같은 방법으로는 탐지되지 않는다. 클래스 내에서 __init__ 내에 정의된
        # 인스턴스 변수가 다른 여러 인스턴스 메서드 실행을 거쳐 어떻게 변하는지 보기 위해
        # 로깅하는 용도를 위해 아래 코드를 작성함.
        if target_var_value == not_found_msg:
            target_class = local_data.get('self', None)
            if target_class:
                target_class_init_vars = target_class.__dict__
                try:
                    target_var_value = target_class_init_vars[var_str]
                except KeyError:
                    target_var_value = not_found_msg
            else:
                target_var_value = not_found_msg

        logger_obj = self._getDebugLogger(current_module_name, class_name, method_name)
        logmsg = ''.join([
                    f"module_name: {current_module_name}, class_name: {class_name}, ",
                    f"method_name: {method_name}, lineno: {current_lineno}\n",
                    f"variable: {var_str}: {target_var_value}"
                ])
        logger_obj.debug(logmsg)

    def _getDebugLogger(
            self,
            modulename: str,
            classname: str | NoneType,
            methodname: str,
        ):
        """
        logVariable() 메서드를 호출하는 함수 또는 메서드의 이름을 
        로거 객체 이름으로 사용하고 해당 로거 객체를 생성 또는 호출함. 
        """
        # 주어진 매개변수들의 정보를 토대로 로거 이름 생성.
        if classname == 'Nonetype':
            # 로깅하는 곳이 클래스의 메서드가 아닌 함수일 경우.
            logger_name = self._delimiter.join([self._debug_logger_name, modulename, methodname])
        else:
            # 클래스 내 특정 인스턴스 메서드 내에서 로깅할 경우.
            logger_name = self._delimiter.join(
                [self._debug_logger_name, modulename, classname, methodname])
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        return logger

    def getErrorLogger(self, name: str | None):
        """
        name 인자값을 이름으로 하는 에러 전용 로거 객체를 반환. 
        """
        error_logger = self._getTypeLogger(name, logging.ERROR)
        return error_logger

    def getLoggerTreeLogger(self, name: str | None):
        """
        name 인자값을 이름으로 하는 로거 계층 트리 전용 로거 객체를 반환. 
        """
        logger_tree_logger = self._getTypeLogger(name, LOGGERTREE)
        return logger_tree_logger

    def getInfoLogger(self, name: str | None):
        """
        name 인자값을 이름으로 하는 info 전용 로거 객체를 반환. 
        """
        info_logger = self._getTypeLogger(name, logging.INFO)
        return info_logger

    def getDebugLoggerExplictly(self, name: str | None):
        """
        name 인자값을 이름으로 하는 디버그 전용 로거 객체를 반환. 
        이 클래스의 logVariable() 메서드와는 따로 디버그 로거 객체를 생성하여 
        따로 쓰고자 할 때 사용. 
        """
        debug_logger = self._getTypeLogger(name, logging.DEBUG)
        return debug_logger

    def _getTypeLogger(self, name: str | None, level: LoggerLevel | SpecialLoggerType):
        """
        로거 객체명과 로거 타입을 레벨로 입력하면 해당 타입에 맞는 로거 객체 반환. 

        매개변수
        -----
        name: 로거 객체 이름. 해당 로거 객체를 사용하는 모듈에서 __file__로 대입하면 
        해당 모듈명이 로거 객체명이 됨. 
        """
        logger_obj = None
        if level == logging.DEBUG:
            if name == ('' or 'root' or None
                        or self._debug_logger_name):
                logger_name = self._debug_logger_name
            elif os.path.isfile(name) and inspect.getmodulename(name):
                logger_name = self._delimiter.join(
                    [self._debug_logger_name, inspect.getmodulename(name)])
            else:
                logger_name = self._delimiter.join([self._debug_logger_name, name])
            logger_obj = logging.getLogger(logger_name)
            logger_obj.setLevel(logging.DEBUG)
        elif level == logging.INFO:
            if name == ('' or 'root' or None
                        or self._info_logger_name):
                logger_name = self._info_logger_name
            elif os.path.isfile(name) and inspect.getmodulename(name):
                logger_name = self._delimiter.join(
                    [self._info_logger_name, inspect.getmodulename(name)])
            else:
                logger_name = self._delimiter.join([self._info_logger_name, name])
            logger_obj = logging.getLogger(logger_name)
            logger_obj.setLevel(logging.INFO)
        elif level == logging.ERROR:
            if name == ('' or 'root' or None
                        or self._error_logger_name):
                logger_name = self._error_logger_name
            elif os.path.isfile(name) and inspect.getmodulename(name):
                logger_name = self._delimiter.join(
                    [self._error_logger_name, inspect.getmodulename(name)])
            else:
                logger_name = self._delimiter.join([self._error_logger_name, name])
            logger_obj = logging.getLogger(logger_name)
            logger_obj.setLevel(logging.ERROR)
        elif level == LOGGERTREE:
            if name == ('' or 'root' or None or
                        self._log_hierarchy_logger_name):
                logger_name = self._log_hierarchy_logger_name
            elif os.path.isfile(name) and inspect.getmodulename(name):
                logger_name = self._delimiter.join(
                    [self._log_hierarchy_logger_name, inspect.getmodulename(name)])
            else:
                logger_name = self._delimiter.join([self._log_hierarchy_logger_name, name])
            logger_obj = logging.getLogger(logger_name)
            logger_obj.setLevel(logging.INFO)
        self._lh.updateLoggerInfo()
        return logger_obj

    def _setLoggerEnvironment(self):
        """
        로거 객체의 핸들러 관련 설정. 
        루트 로거에 적용되고, 모든 자식 로거에 자동 적용되도록 함. 
        """
        debug_filter = logging.Filter(self._debug_logger_name)
        debug_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s \n%(message)s"
        )
        debug_file_handler = logging.FileHandler(
            filename=self.debug_log_file_path,
            encoding='utf-8'
        )
        debug_file_handler.setLevel(logging.DEBUG)
        debug_file_handler.setFormatter(debug_formatter)
        debug_file_handler.addFilter(debug_filter)
        self._root_logger.addHandler(debug_file_handler)

        info_filter = logging.Filter(self._info_logger_name)
        info_file_handler = logging.FileHandler(
            filename=self.debug_log_file_path,
            encoding='utf-8'
        )
        info_file_handler.setLevel(logging.INFO)
        info_file_handler.setFormatter(debug_formatter)
        info_file_handler.addFilter(info_filter)
        self._root_logger.addHandler(info_file_handler)

        error_filter = logging.Filter(self._error_logger_name)
        error_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s \n%(message)s"
        )
        error_file_handler = logging.FileHandler(
            filename=self.error_log_file_path,
            encoding='utf-8'
        )
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(error_formatter)
        error_file_handler.addFilter(error_filter)
        self._root_logger.addHandler(error_file_handler)

        hierarchy_filter = logging.Filter(self._log_hierarchy_logger_name)
        hierarchy_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s \n%(message)s"
        )
        hierarchy_file_handler = logging.FileHandler(
            filename=self.hierarchy_log_file_path,
            encoding='utf-8'
        )
        hierarchy_file_handler.setLevel(logging.INFO)
        hierarchy_file_handler.setFormatter(hierarchy_formatter)
        hierarchy_file_handler.addFilter(hierarchy_filter)
        self._root_logger.addHandler(hierarchy_file_handler)

    def resetLogFile(self, file: WhichFile):
        """
        로그 파일 내용을 비운다. (로그 파일을 삭제하진 않음.)

        매개변수
        -----
        file: 삭제할 파일을 결정한다. 
            - DEBUGFILE: 디버그 로그 파일 내용을 지운다. 
            - ERRORFILE: 에러 로그 파일 내용을 지운다. 
            - LOGGERFILE: 로거 객체 계층 트리를 기록하는 파일 내용을 지운다. 
            - ALLFILES: 디버그, 에러, 로거 계층 트리 기록 파일 모두 내용을 지운다. 
        """
        if file == ALLFILES:
            files = [
                self.debug_log_file_path,
                self.error_log_file_path,
                self.hierarchy_log_file_path
            ]
            for f in files:
                with open(f, 'w', encoding='utf-8'):
                    pass
            return

        if file == DEBUGFILE:
            filepath = self.debug_log_file_path
        elif file == ERRORFILE:
            filepath = self.error_log_file_path
        elif file == LOGGERFILE:
            filepath = self._log_hierarchy_logger_name
        else: return

        with open(filepath, 'w', encoding='utf-8'):
            pass

    def getCurrentHierarchy(self):
        """
        현재까지 등록된 모든 로거 객체들을 계층에 따라 트리 구조로 
        나타낸 문자열 반환. 
        """
        self._lh.updateLoggerInfo()
        return self._lh.getLoggerTree()

    def getCurrentAllLeafLoggers(self):
        """
        현재까지 등록된 모든 로거 객체들을 계층에 따라 트리 구조로 나타낼 때 
        leaf 노드에 해당하는 모든 로거 객체 이름들을 리스트로 모아 반환. 
        """
        self._lh.updateLoggerInfo()
        return self._lh.getLeafLoggersName()

    def logAllLoggersTree(self):
        """
        현재까지 생성된 모든 로거 객체들의 이름을 계층 트리 형태로 
        로깅함. 
        """
        hierarchy_logger = logging.getLogger(self._log_hierarchy_logger_name)
        hierarchy_logger.setLevel(logging.INFO)
        tree_str = self.getCurrentHierarchy()
        all_leaf = self.getCurrentAllLeafLoggers()
        all_leaf = '\n'.join(all_leaf)
        hierarchy_logger.info(f"{tree_str}\n\n{all_leaf}")


if __name__ == '__main__':
    pass
    