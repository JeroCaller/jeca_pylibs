"""패키지 로거 모듈.
기존 logging 사용 시 코드 내에 로깅 코드가 많아지는 것을 방지, 
사용자로 하여금 로깅 설정을 최소화하고, 
로깅하는 함수, 메서드, 클래스, 모듈의 이름을 자동으로 얻어와 
로거 객체 이름 생성을 자동화하기 위해 만듦. 
로깅 시 현재까지 생성된 로거 객체들을 계층별로 트리로 나타내는 
기능 추가. 

"""

import os
import inspect
import logging
import shutil
from typing import Literal, TypeAlias

import logexc
import tools
import sub_modules.dirsearch as dirs
import sub_modules.fdhandler as fdh
from sub_modules.tree import PathTree
from sub_modules.tree import AbsPath
from loghandlers import CustomRotatingFileHandler

# type aliases
NoneType: TypeAlias = Literal['NoneType']
LoggerLevel: TypeAlias = int
DirPath: TypeAlias = str
DirName: TypeAlias = str
FilePath: TypeAlias = str
FileName: TypeAlias = str

# 상수 정의
ALLFILES = 0
DEBUGFILE = 1
ERRORFILE = 2
LOGGERFILE = 3
WhichFile: TypeAlias = Literal[0, 1, 2, 3]

LOGGERTREE = 4
SpecialLoggerType: TypeAlias = Literal[4]

DEFAULT = 'default'

DEFAULT_TOPLEVEL_LOGGERS = {
    LOGGERTREE: "__log_hierarchy__",
    logging.DEBUG: "__debug__",
    logging.ERROR: "__error__",
    logging.INFO: "__info__"
}
DEFAULT_LEVEL_LOG_FILE_NAMES = {
    logging.DEBUG: 'debug.log',
    logging.INFO: 'info.log',
    logging.ERROR: 'error.log',
    LOGGERTREE: 'logger_tree.log',
}

def _makedir(superdirpath: str, dirname: str):
    """특정 위치에 디렉토리를 생성하는 함수. 

    Parameters
    ----------
    superdirpath : str
        폴더를 생성하고자 하는 상위 디렉토리 주소
    dirname : str
        생성하고자 하는 폴더 이름.

    Raises
    -----
    FileNotFoundError
        만약 superdirpath로 대입한 디렉토리 주소가 존재하지 않는다면 
        FileNotFoundError가 발생함.

    Examples
    --------

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
        """특정 함수 또는 메서드의 호출 시작과 작업 종료 사실을 
        로깅해주는 데코레이터.

        Parameters
        ----------
        logger_obj : logging.Logger
            로깅하는 모듈 내에서 정의된 Logger 객체. 
            해당 로거 객체의 최소 level이 적어도 INFO 이하로 지정되어야 함. 
            그래야 해당 로거 객체에 연결된 파일 대상에 로그 기록 가능. 

        Raises
        ------
        LogLowestLevelError
            `logger_obj` 매개변수의 로거 객체에 설정된 level이 
            INFO보다 높을 경우 발생.
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
        """특정 함수 또는 메서드 내에서 발생할 수 있는 모든 예외 메시지를 
        로그에 기록하는 데코레이터. 

        함수 내에 깊이를 알 수 없는 중첩 함수들이 있을 때 
        예외를 로깅하려면 다음과 같이 처리.
        예)
        >>> import logging
        >>> error_logger = logging.getLogger()
        >>> error_logger.setLevel(logging.ERROR)
        >>> try:
        ...    main()
        ... except Exception as e:
        ...    error_logger.exception(e)

        Parameters
        ----------
        logger_obj : logging.Logger
            로깅하는 모듈 내에서 정의된 Logger 객체. 
            해당 로거 객체의 최소 level이 적어도 ERROR 이하로 지정되어야 함. 
            그래야 해당 로거 객체에 연결된 파일 대상에 로그 기록 가능. 

        Raises
        ------
        LogLowestLevelError
            `logger_obj` 매개변수의 로거 객체에 설정된 level이 
            ERROR보다 높을 경우 발생.
        """
        self.logger = logger_obj
        self.no_err_msg = "No error occured."
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
            else:
                # WARNING - 테스트 코드에서 일별을 제외한 날짜별 로깅 시 
                # WARNING - 에러 미발생 로깅이 여러 번 발생.
                # WARNING - 그러나 실제 사용 예에선 해당 버그 없는 것으로 파악됨.
                if self.logger.level == logging.DEBUG:
                    self.logger.debug(self.no_err_msg)
                elif self.logger.level == logging.INFO:
                    self.logger.info(self.no_err_msg)
                elif self.logger.level == logging.WARNING:
                    self.logger.warning(self.no_err_msg)
                else:
                    self.logger.error(self.no_err_msg)
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
    """현재 등록된 모든 로거 객체들의 이름을 
    계층을 가진 트리로 보여주는 클래스.
    """
    def __init__(self):
        self._root_logger = logging.getLogger()
        self._logger_dict: dict[str, logging.Logger] = {}
        self._ptree = _LoggerPathTree()

        self.updateLoggerInfo()

    def _getCurrentLoggers(self):
        """현재까지 등록된 모든 로거 객체들의 정보를 받아온다. 
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
        """현재까지 등록된 모든 로거 객체들의 이름들을 트리로 구성."""
        self._ptree.clear()
        for k in self._logger_dict.keys():
            self._ptree.appendAbs(k)

    def updateLoggerInfo(self):
        """지금까지 생성된 모든 로거 객체들의 정보를 이 객체에 업데이트."""
        self._getCurrentLoggers()
        self._getInfoHierarchy()

    def getLoggerTree(self):
        """현재까지 등록된 로거 객체들의 계층 트리를 문자열로 반환. 
        중간에 새로운 로거 객체들을 생성한 경우, updateLoggerInfo() 메서드 
        호출로 새로고침 필요. 
        """
        return self._ptree.getTreeStructure()

    def getLeafLoggersName(self):
        """현재까지 등록된 모든 로거 객체들의 계층 트리에서 
        leaf 로거 이름만을 반환. 
        중간에 새로운 로거 객체들을 생성한 경우, updateLoggerInfo() 메서드 
        호출로 새로고침 필요. 
        """
        return self._ptree.getAllLeafAbs()

    def getNumberofNodes(self):
        """로거 객체 계층 트리 내 노드의 수 반환."""
        return self._ptree.lenTree()


class LogFileEnvironment():
    """로그 파일들을 어떻게 저장 및 관리할 것인지를 설정하는 클래스.

    여러 옵션들을 제공하며, 그 중에 원하는 것을 선택하는 형식. 

    logging 내장 라이브러리를 이용하며, 해당 라이브러리의 루트 로거 객체를 
    이용함.

    이 클래스에서 디렉토리 경로 문자열을 생성하는 메서드들은 모두 실제 
    해당 경로에 디렉토리를 생성하지는 않음.

    로그 파일 환경 설정 과정

    1. 먼저 모든 로그 파일들을 하나의 장소 안에 저장, 생성, 관리하기 위해 
    이를 위한 베이스 디렉토리를 생성한다. 이를 위해 둘 중 하나를 선택한다.
        (1) setBaseDir() 메서드를 통해 베이스 디렉토리를 위치시킬 상위
        디렉토리의 위치와 해당 베이스 디렉토리의 이름을 정한다.
        (2) setTopLevelModulePath() 메서드를 통해, 사용자의 프로젝트 패키지 
        내 최상위 모듈(예: main.py)의 경로를 대입한다. 그러면 기본 베이스 
        디렉토리 경로로 자동 결정된다. 
    2. 로그 파일 분류 옵션을 설정한다. 로그 수준별 로그 파일 분류 여부를 
    결정하려면 setLevelOption()을, 날짜별 분류 옵션은 setDate() 메서드를 
    이용한다. 
    3. setLoggerEnvironment() 메서드를 호출하면 여태까지 설정한 모든 
    로그 파일 환경 관련 옵션들이 적용된다.

    """
    def __init__(self):
        self._root_logger = logging.getLogger()

        self.base_dir: DirPath = ''
        self.toplevel_module_path: FilePath = ''

        self.date_type: tools.DateOptions = tools.DateOptions.FREE
        self.datetool = tools.DateTools()

        # 로그 파일을 로그 수준별로 나눠서 저장할 지, 
        # 하나의 로그 파일 안에 모든 수준의 로그를 기록하도록
        # 할지 결정하는 변수.
        # True : 로그 수준별로 나눠서 저장하는 모드.
        # False : 하나의 로그 파일 안에 모든 수준의 로그 기록 모드.
        self.level_mode: bool = True

        self.level_log_file_names: dict[LoggerLevel, FileName] = {}
        self.setLogFileNamesForEachLevels(
            DEFAULT_LEVEL_LOG_FILE_NAMES.copy()
        )

        self.default_common_formatter \
            = logging.Formatter(
            "%(asctime)s - %(levelname)s\n%(message)s"
            )
        self.common_formatter: logging.Formatter \
            = self.default_common_formatter
        self.level_formatters: dict[LoggerLevel, logging.Formatter] = {}

        self.handler = DEFAULT
        self.handler_args = None
        self.handler_kwargs = None

    def setBaseDir(
            self, 
            superpath: DirPath, 
            dirname: str | None = None
        ):
        """로그 파일들을 저장, 관리할 베이스 디렉토리의 위치를 지정하고, 
        디렉토리명을 결정한다. 

        Parameters
        ----------
        superpath : str
            로그 파일들을 저장할 베이스 디렉토리를 위치시킬 상위 디렉토리의 
            주소 대입. 
        dirname : str | None, default None
            로그 파일들을 저장할 베이스 디렉토리에 지어줄 이름 대입. 
            None 대입 시 'logfiles'라는 이름을 기본으로 설정된다. 
        
        """
        superpath = os.path.abspath(superpath)
        if dirname is None: dirname = 'logfiles'
        self.base_dir = os.path.join(superpath, dirname)

    def _setDefaultBaseDir(self):
        """사용자가 따로 로그 파일들을 저장, 관리할 베이스 디렉토리를 생성할 
        위치와 베이스 디렉토리 이름을 정하지 않은 경우, 자동으로 기본 설정해주는 메서드.

        setTopLevelModulePath() 메서드를 통해 사용자가 최상위 모듈을 지정한 경우, 
        해당 모듈과 같은 디렉토리에 베이스 디렉토리가 생성될 수 있도록 경로를 생성한다.
        해당 베이스 디렉토리명은 'logfiles'로 한다.

        Raises
        ------
        logexc.NotInitConfigError
            사용자가 작업하고 있는 프로젝트 패키지에서의 최상위 모듈(ex. main.py)을 
            지정하지 않은 경우 발생하는 예외. 이 예외를 해결하는 방법은 두 가지이다.

            1. setTopLevelModulePath() 메서드를 통해 최상위 모듈의 경로를 대입하여
            해당 패키지 내 최상위 모듈을 지정해준다.

            2. 기본 설정을 사용하지 않고, 
            setBaseDir() 메서드를 통해 로그 파일 저장, 관리 베이스 디렉토리의 위치와 
            해당 디렉토리명을 따로 지정한다.

        See Also
        --------
        setTopLevelModulePath

        """
        if not os.path.isfile(self.toplevel_module_path):
            raise logexc.NotInitConfigError(
                logexc.NO_TOPLEVEL_MODULE_AND_BASE_DIR
            )
        tl_module_dirname = os.path.dirname(self.toplevel_module_path)
        self.setBaseDir(tl_module_dirname)

    def setTopLevelModulePath(self, module_path: FilePath = ''):
        """로깅할 패키지 내 최상위 모듈 경로를 지정하는 메서드. 
        최상위 모듈(ex. main.py) 내에서 인자로 __file__을 대입하면 된다.

        이 메서드를 호출하면 최상위 모듈이 존재하는 디렉토리 내에 
        로그 파일들을 한꺼번에 저장, 관리할 베이스 디렉토리의 위치와 
        그 이름이 자동으로 결정된다(이 메서드만으로는 실제로 해당 베이스
        디렉토리가 생성되지는 않으니 따로 작업 필요). 
        만약 다른 곳에 베이스 디렉토리를 생성하고자 한다면 
        이 메서드 호출 코드 다음에 setBaseDir() 메서드에 원하는 위치와 
        해당 디렉토리명을 지어주고 호출하면 된다. 

        Parameters
        ----------
        module_path : str
            최상위 모듈의 경로. 최상위 모듈 내에서 __file__를 대입하면 됨.
        
        """
        self.toplevel_module_path = os.path.abspath(module_path)
        self._setDefaultBaseDir()

    def setLevelOption(self, set_to_level: bool):
        """로그 파일들을 저장할 때 디버그, 에러, INFO 별로 로그 파일들을 나눠서 
        저장할 지, 아니면 모든 수준의 로그 기록들을 하나의 로그 파일 안에 몰아서 
        저장할 지에 대한 옵션을 결정하는 메서드.

        Parameters
        ---------- 
        set_to_level : bool
            True - 로그 파일을 각 수준별로 나눠서 저장하는 모드로 설정.
            False - 모든 로거 수준의 로그 기록들을 하나의 로그 파일로 
            저장하는 모드로 설정.
        
        """
        self.level_mode = set_to_level

    def setLogFileNamesForEachLevels(
            self, 
            level_file_names: dict[LoggerLevel, str] | None = None,
            suffix_date: bool = True
        ):
        """수준별로 로그 파일들을 분류하여 저장할 경우, 각 수준별 
        로그 파일명을 설정하는 메서드. 

        기존에 설정한 상태에서 새로 설정하는 경우, 기존의 수준별 
        로그 파일명 정보들은 삭제되고, 새로 설정된 정보들로 리셋된다.

        Parameters
        ----------
        level_file_names : dict[LoggerLevel, str] | None
            각 수준별 로그 파일명을 담는 딕셔너리. 뒤에 '.log' 확장자를 붙이지
            않아도 자동으로 추가해줌.

            예)
            level_file_names = {
                logging.DEBUG: 'debug',
                logging.ERROR: 'error',
            }

            None 입력 시 기본 로그 파일명으로 설정됨.
        suffix_date : bool, default True
            로그 파일명 뒤에 오늘 날짜를 '_YYYY-MM-DD'형태로 추가할 지 결정하는 
            매개변수. 
            예) debug_2023-12-18.log
        
        """
        if level_file_names is None:
            self.level_log_file_names \
                = DEFAULT_LEVEL_LOG_FILE_NAMES.copy()
            return

        self.level_log_file_names.clear()
        for k, v in level_file_names.items():
            if not v.endswith('.log'):
                if suffix_date:
                    v = '_'.join([v, self.datetool.getTodaysDateStr()])
                self.level_log_file_names[k] = '.'.join([v, 'log'])
            else:
                if suffix_date:
                    v = v.split('.')[0]
                    v = '_'.join([v, self.datetool.getTodaysDateStr()])
                    v = '.'.join([v, 'log'])
                self.level_log_file_names[k] = v

    def setCommonFormatter(self, strfmt: str | None):
        """모든 로그 파일들에 똑같은 로그 포맷을 사용하고자 할 때 
        설정하는 메서드.

        만약 setLevelFormatter() 메서드를 통해 로그 수준에 따른 
        포맷들을 따로 설정한 경우, 이를 우선으로 적용함.

        Parameters
        ----------
        strfmt : str | None
            로그 파일에 기록될 로그 포맷을 문자열로 설정. 문자열 
            포맷 방식은 logging 내장 모듈의 Formatter() 클래스 생성자 
            내에 사용하는 문자열 포맷 형식을 따름.
            기본 공통 문자열 포맷으로 설정하고자 한다면 None 대입.

        See Also
        --------
        setLevelFormatter
        
        """
        if strfmt is None:
            self.common_formatter = self.default_common_formatter
        else:
            self.common_formatter = logging.Formatter(strfmt)

    def setLevelFormatter(self, level: LoggerLevel, strfmt: str):
        """각 수준에 따른 로그 문자열 포맷 결정 메서드. 
        해당 포맷 문자열은 logging.Formatter() 객체 생성자에 대입하여 자동으로 
        생성하여 저장해줌. 
        
        예를 들어 이미 디버그 수준에 포맷을 설정한 상태에서 해당 수준에 다른 
        포맷을 설정하려고 시도하는 경우, 새로운 포맷으로 대체됨.

        만약 setCommonFormatter() 메서드를 통해 모든 로그 수준에 똑같은 
        로그 문자열 포맷을 지정한 경우, 이를 무시하고 각 로그 수준에 적용된 
        로그 포맷을 따른다.

        이 메서드는 먼저 setLevelOption 메서드를 통해 수준별 로그 파일 저장
        모드로 설정해야 효과가 있음. 

        Parameters
        ----------
        level : LoggerLevel
            로그 수준. logging.DEBUG, ERROR 등을 사용.
        strfmt : str
            각 수준의 로그 파일에 기록될 문자열 포맷. 문자열 
            포맷 방식은 logging 내장 모듈의 Formatter() 클래스 생성자 
            내에 사용하는 문자열 포맷 형식을 따름.

        See Also
        --------
        setCommonFormatter
        clearLevelFormatter
        setLevelOption
        
        """
        self.level_formatters[level] = logging.Formatter(strfmt)

    def clearLevelFormatter(self):
        """여태까지 설정된 로그 수준별 포맷터들을 삭제한다."""
        self.level_formatters.clear()

    def setCustomHandler(self, classname: callable, *args, **kwargs):
        """핸들러 설정 메서드. 
        기본은 logging.FileHandler 핸들러를 사용함. 
        이 핸들러를 사용하고자 할 경우 이 메서드를 호출할 필요는 없음. 
        해당 핸들러 외 다른 핸들러를 사용하고자 할 때 이 메서드로 설정하면 됨.

        Parameters
        ----------
        classname : callable
            설정하고자 하는 logging의 핸들러 클래스명을 기입. 
        *args, **kwargs
            classname 매개변수로 설정한 핸들러 클래스의 생성자에 들어갈 매개변수들.
        
        Examples
        --------
        
        만약 logging.handlers의 RotatingFileHandler 핸들러를 사용하고자 하는 경우.

        일반적인 예)

        >>> from logging.handlers import RotatingFileHandler
        >>> handler = RotatingFileHandler('some_log.log', maxBytes=10, backupCount=3,
        ... encoding='utf-8')

        이 메서드에 각 인자들 대입법)

        setCustomHandler(RotatingFileHandler, 'some_log.log', maxBytes=10,
        backupCount=3, encoding='utf-8')

        """
        self.handler = classname
        self.handler_args = args
        self.handler_kwargs = kwargs

    def setCustomRotatingFileHandler(self, *args, **kwargs):
        """로그 환경 설정에 쓰일 파일 핸들러를 
        CustomRotatingFileHandler 핸들러 클래스로 설정한다. 
        해당 핸들러 클래스에 대한 것은 loghandlers.py 파일 참조.

        해당 핸들러 클래스로 설정하고자 한다면 setCustomHandler() 메서드를 
        직접 이용하는 대신 이 메서드를 호출하면 된다.

        Parameters
        ----------
        *args, **kwargs
            CustomRotatingFileHandler 클래스의 생성자에 들어갈 매개변수들
        
        """
        self.setCustomHandler(CustomRotatingFileHandler, *args, **kwargs)

    def setDefaultFileHandler(self):
        """LogFileEnvironment() 클래스에서 사용할 로그 파일 핸들러를 기본 
        핸들러로 지정한다. 

        logging.FileHandler()를 기본 핸들러로 지정한다.

        """
        self.handler = DEFAULT
        self.handler_args = None
        self.handler_kwargs = None

    def _getCustomHandler(self, *args, **kwargs):
        """setCustomHandler() 메서드로 지정한 핸들러 클래스를 인스턴스화하여 이를 
        반환.

        Parameters
        ----------
        *args, **kwargs
            설정한 핸들러 클래스 생성자에 추가로 입력할 매개변수가 있으면 입력.
        
        """
        if not callable(self.handler):
            return None
        
        if args:
            self.handler_args = tuple(
                list(self.handler_args).extend(list(args))
            )
        if kwargs:
            for k, v in kwargs.items():
                self.handler_kwargs[k] = v
        return self.handler(*self.handler_args, **self.handler_kwargs)

    def setDate(self, option: tools.DateOptions):
        """로그 파일들을 기간별로 구분할 것인지를 결정하는 메서드.
        
        일, 주, 월, 연 단위로 로그 파일들을 각 폴더 안에 묶어 저장시키도록 
        설정할 수 있다. 또는 기간 구분 없이 모든 로그 파일들을 하나의 
        폴더(setBaseDir()메서드로 지정한 로그 파일 저장용 베이스 디렉토리)에 
        몰아 넣어 저장하는 방식을 택할 수도 있다. 

        Parameters
        ----------
        option : tools.DateOptions
            tools.py 모듈의 DateOptions 클래스에 정의된 여러 
            상수들 중 하나를 택해 대입. 
            가능한 옵션들)
            DAY : 하루 단위로 로그 파일들을 폴더로 구분하여 저장.
            WEEK : 주 단위로 로그 파일들을 구분하여 저장.
            MONTH : 월 단위로 로그 파일들을 구분하여 저장.
            YEAR : 연 단위로 로그 파일들을 구분하여 저장.
            FREE : 기간 구분 없이 한 폴더 안에 모든 로그 파일들을 저장.
        
        """
        self.date_type = option

    def generateDateDirPath(self):
        """오늘 실행된 로그 파일들을 오늘 날짜를 이름으로 가지는 
        하위 디렉토리에 저장하기 위해, 해당 디렉토리의 경로를 결정하고 
        반환하는 메서드. 

        해당 메서드는 해당 디렉토리의 절대경로 문자열만 생성할 뿐, 실제로 해당 
        디렉토리를 생성하지는 않음.

        setDate() 메서드에 FREE 인자값을 대입하였거나 해당 메서드를 통해 
        기간별 구분 설정을 하지 않은 경우, 날짜 디렉토리 경로를 따로 생성하지 않고, 
        베이스 디렉토리 경로 문자열을 반환한다.

        Returns
        -------
        str
            날짜별 로그 파일들을 저장할 디렉토리의 절대경로. 
            setDate() 메서드에서 지정된 날짜 옵션에 따라 디렉토리명의 형태가 달라짐.
            
            예)
            'C:\\my_project\\logfiles\\2023-11-24'

            날짜 옵션값을 FREE로 한 경우, 베이스 디렉토리 경로를 반환한다. 

            예)
            'C:\\my_project\\logfiles'
        None
            tools.DateOptions에 정의된 상수값이 아닌 다른 값으로 날짜 옵션 설정한 경우.
            setDate() 메서드에서 엉뚱한 값을 설정해서 발생할 수도 있음.

        Raises
        ------
        logexc.NotInitConfigError
            로그 파일들을 한꺼번에 저장, 관리하는 베이스 디렉토리 경로가 
            결정되지 않은 경우 발생하는 예외. 이 예외를 없앨려면 다음의 선택지들 중 
            하나를 골라서 실행해야 함.

            1. 베이스 디렉토리를 따로 지정하지 않았고, 시스템에서 
            자동으로 정해주길 원한다면, 이 클래스의 setTopLevelModulePath() 
            메서드에서 현재 로깅하고자 하는 프로젝트 패키지 내 최상위 모듈의 
            경로를 대입한다.

            2. 따로 베이스 디렉토리의 위치와 해당 디렉토리명을 지정하고자 한다면 
            이 클래스의 setBaseDir() 메서드를 통해 지정.

        See Also
        --------
        setDate
        setTopLevelModulePath : Raises 부분에 언급된 예외가 발생할 경우 
        고려해볼 수 있는 메서드 중 하나.
        setBaseDir : Raises 부분에 언급된 예외가 발생할 경우 
        고려해볼 수 있는 메서드 중 하나.

        """
        if self.date_type == tools.DateOptions.FREE:
            return self.base_dir
        
        if not os.path.isdir(self.base_dir):
            raise logexc.NotInitConfigError(logexc.NO_BASE_DIR)
        
        if self.date_type == tools.DateOptions.DAY:
            today = self.datetool.getDateStr(
                tools.DateOptions.DAY, True
            )
        elif self.date_type == tools.DateOptions.WEEK:
            today = self.datetool.getDateStr(
                tools.DateOptions.WEEK, True
            )
        elif self.date_type == tools.DateOptions.MONTH:
            today = self.datetool.getDateStr(
                tools.DateOptions.MONTH, True
            )
        elif self.date_type == tools.DateOptions.YEAR:
            today = self.datetool.getDateStr(
                tools.DateOptions.YEAR, True
            )
        else:
            # self.date_type 변수에 tools.DateOptions 클래스에 정의된
            # 상수값들 중 어디에도 포함되지 않는 비정상적인 경우.
            return None
        today_dir = os.path.join(self.base_dir, today)
        return today_dir

    def setLoggerEnvironment(self):
        """로거 객체에 관한 설정을 하는 메서드.
        
        수준별 로그 기록 분류 여부 및 날짜별 분류 옵션에 따라 
        로거 객체의 파일 handler, filter, formatter 등을 설정한다. 

        모든 로거 객체 관련 설정들은 logging 라이브러리의 루트 로거
        객체를 이용함.

        """
        os.makedirs(self.base_dir, exist_ok=True)

        def by_levels():
            """수준별 로거 객체들에 대한 핸들러, 포맷 등의 설정 함수."""
            def get_formatter(level: LoggerLevel):
                try:
                    return self.level_formatters[level]
                except KeyError:
                    return self.common_formatter
                
            def get_filter(level: LoggerLevel):
                try:
                    new_filter = logging.Filter(
                        DEFAULT_TOPLEVEL_LOGGERS[level]
                    )
                except KeyError:
                    missing_level = logging.getLevelName(level)
                    error_msg = f"""{missing_level} 수준에 설정된 
                    최상위 로거 객체 이름이 설정되지 않았습니다. 
                    setTopLevelLoggersName() 메서드를 통해 설정 필요.
                    """
                    raise logexc.NotInitConfigError(error_msg)
                return new_filter
            
            def get_file_handler(level: LoggerLevel):
                date_dir = self.generateDateDirPath()
                os.makedirs(date_dir, exist_ok=True)
                log_file_name = self.level_log_file_names[level]
                if not log_file_name.endswith('.log'):
                    log_file_name = '.'.join([log_file_name, 'log'])
                target_file = os.path.join(date_dir, log_file_name)
                
                if self.handler == DEFAULT:
                    file_handler = logging.FileHandler(
                        filename=target_file,
                        encoding='utf-8'
                    )
                else:
                    file_handler = self._getCustomHandler(filename=target_file)
                return file_handler

            for level in DEFAULT_TOPLEVEL_LOGGERS:
                formatter_obj = get_formatter(level)
                filter_obj = get_filter(level)
                file_handler_obj = get_file_handler(level)
                file_handler_obj.setLevel(level)
                file_handler_obj.setFormatter(formatter_obj)
                file_handler_obj.addFilter(filter_obj)
                self._root_logger.addHandler(file_handler_obj)

        def by_all_in_one():
            """모든 수준의 로그들을 하나의 로그 파일로 저장하고자 할 때의
            로거 객체에 대한 핸들러, 포맷 등의 설정 함수.
            """
            date_dir = self.generateDateDirPath()
            os.makedirs(date_dir, exist_ok=True)
            log_file_name = self.datetool.getDateStr(
                tools.DateOptions.DAY, True
            )
            log_file_name = '.'.join([log_file_name, 'log'])
            target_file = os.path.join(date_dir, log_file_name)

            if self.handler == DEFAULT:
                file_handler = logging.FileHandler(
                    filename=target_file,
                    encoding='utf-8'
                )
            else:
                file_handler = self._getCustomHandler(filename=target_file)
            file_handler.setLevel(logging.DEBUG)
            if not self.common_formatter:
                file_handler.setFormatter(self.default_common_formatter)
            else:
                file_handler.setFormatter(self.common_formatter)
            self._root_logger.addHandler(file_handler)

        if self.level_mode:
            by_levels()
        else:
            # if not self.level_mode
            by_all_in_one()


class EasySetLogFileEnv(LogFileEnvironment):
    """LogFileEnvironment 클래스를 이용해 로그 파일 환경 설정을 
    더 쉽게 해주는 클래스.
    기존 LogFileEenvironment 클래스는 로그 환경 설정 절차는 따로 없어서
    복잡하기에 고안된 클래스. 
    해당 클래스의 setEssentialLogEnv() 메서드를 이용하면 됨.
    """
    def setEssentialLogEnv(
            self,
            base_dir: DirPath | None = None,
            base_dir_name: DirName | None = None,
            toplevel_module_path: FilePath | None = None,
            level_option: bool = True,
            date_opt: tools.DateOptions | None = None
        ):
        """LogFileEnvironment 클래스로 로그 환경 설정이 어려울 경우 대신 
        사용할 수 있는 메서드. 

        각각의 설정에 대한 자세한 사항은 LogFileEnvironment 클래스를 참조.

        이 메서드를 통해 기본 설정하기 전 추가적인 설정을 원한다면 
        이 메서드를 호출하기 전에 먼저 추가적인 설정을 해주는 메서드를 사용하기를 권장. 

        Parameters
        ----------
        base_dir : str | None, default None
            로그 파일들을 저장할 베이스 디렉토리를 위치시킬 상위 디렉토리의 주소 대입.
        base_dir_name : str | None, default None
            로그 파일들을 저장할 베이스 디렉토리에 지어줄 이름 대입. 
            None 대입 시 'logfiles'라는 이름을 기본으로 설정된다.
        toplevel_module_path: str | None, default None
            로깅을 하고자 하는 사용자의 패키지 디렉토리 내 최상위 모듈(ex. main.py)의 
            절대경로. 최상위 모듈 내에서 이 메서드 사용 시 __file__ 인자를 대입해도 됨.
            로그 파일 저장, 관리할 베이스 디렉토리를 기본값으로 설정하고자 한다면 반드시
            설정해야한다. 만약 베이스 디렉토리 위치와 그 이름을 사용자가 따로 결정한다면 
            필수 매개변수는 아님.
        level_option : dict[LoggerLevel, TopLevelLoggerName] | DEFAULT | None, default None
            로그 파일들을 여러 수준으로 나눠서 저장하고자 하는 경우, 각 level 숫자와 
            각 level의 최상위 로거 객체 이름을 딕셔너리 형태로 기입한다. 자세한 예시는 
            아래 Examples 부분에 설명.
            None으로 설정 시 모든 수준의 로그들을 하나의 로그 파일 안에 저장하는 모드로 전환.
            logpackage 모듈의 전역 상수인 DEFAULT 입력 시 기본 최상위 로거 객체 이름으로 설정됨.
        date_opt: tools.DateOptions | None
            로그 파일들을 기간별로 구분하고자 할 때 일, 주, 월, 연 단위 중 하나를 택하는 옵션.
            tools.DateOptions 클래스에 정의된 상수들.
            DAY : 하루 단위로 로그 파일들을 폴더로 구분하여 저장.
            WEEK : 주 단위로 로그 파일들을 구분하여 저장.
            MONTH : 월 단위로 로그 파일들을 구분하여 저장.
            YEAR : 연 단위로 로그 파일들을 구분하여 저장.
            FREE : 기간 구분 없이 한 폴더 안에 모든 로그 파일들을 저장.

        Examples
        --------

        level_option 매개변수
        로그 파일들을 여러 수준으로 나누고 각 수준들의 로그들을 각각의 로그 파일에 
        기록, 저장하고자 할 경우, 각 수준의 최상위 로거 객체 이름을 딕셔너리 형태로 
        level_option 매개변수에 지정한다. 그러면 이후 각 수준의 로그 객체들은 해당 수준의 
        최상위 로거 객체 안에서 관리하게끔 함.

        예시)
        level_option = {
            logging.DEBUG : '__debug_log__', 
            logging.ERROR : '__error_log__',
            logging.INFO : '__info_log__',
        }

        """
        if toplevel_module_path and os.path.isfile(toplevel_module_path):
            self.setTopLevelModulePath(toplevel_module_path)

        if base_dir:
            self.setBaseDir(base_dir, base_dir_name)

        self.setLevelOption(level_option)
        
        if date_opt:
            self.setDate(date_opt)
        
        self.setLoggerEnvironment()


class PackageLogger():
    """패키지 내 모듈들의 로깅을 하나로 관리할 수 있는 클래스.
    로그 관련 설정을 원하는대로 설정할 수 있다.

    해당 클래스를 인스턴스화 하기 전에 반드시 로그 관련 환경 설정 클래스인 
    EasySetLogFileEnv 또는 LogFileEnvironment 클래스를 먼저 인스턴스화해야 함.
    """
    _this_instance = None
    _is_initialized: bool = False
    _unique_logenv = None

    def __new__(cls, logenv=None):
        if cls._this_instance is None:
            cls._this_instance = super().__new__(cls)
        if logenv and (cls._unique_logenv is None):
            cls._unique_logenv = logenv
        return cls._this_instance

    def __init__(self, logenv: EasySetLogFileEnv | LogFileEnvironment = None):
        """
        Parameters
        ----------
        logenv : EasySetLogFileEnv | LogFileEnvironment
            로그 환경 설정 클래스의 인스턴스를 대입. 
        
        """
        if not PackageLogger._is_initialized:
            self.logenv = PackageLogger._unique_logenv
            self._delimiter = '.'
            self._log_hier = _LoggerHierarchy()
            self._root_logger = logging.getLogger()
            self._root_logger.setLevel(logging.DEBUG)
            self.log_onoff = True # 로깅 온오프 기능.
            
            PackageLogger._is_initialized = True

    def setLogEnvObj(
            self, 
            new_logenv: EasySetLogFileEnv | LogFileEnvironment
        ):
        """새 로그 환경 설정 클래스 EasySetLogFileEnv 
        또는 LogFileEnvironment의 인스턴스 를 대입하여 새 로그 환경으로 설정한다.
        """
        PackageLogger._unique_logenv = new_logenv
        self.logenv = PackageLogger._unique_logenv

    def setLoggingOnOff(self, on_off: bool):
        """로깅 기능을 킬지 끌지를 결정하는 메서드. 

        자신의 프로젝트 패키지 내 구현한 로깅 코드가 너무 많거나 
        복잡해서 일일이 로깅 코드들을 삭제하기 어려울 때 로깅 기능을 
        끌 수 있다. 
        이 메서드 실행 시 로깅 기능이 곧바로 켜지거나 꺼지는 기능이 즉시 적용된다.

        Parameters
        ----------
        on_off : bool
            로깅 기능을 킬지 끌지에 대한 매개변수
            True : 로깅 기능을 켠다. 로그 파일에 로그가 기록된다. 
            False : 로깅 기능을 끈다. 프로그램을 실행해도 로그 기록이 되지 않는다.
        
        """
        self.log_onoff = on_off
        if on_off:
            # on
            self.logenv.setLoggerEnvironment()
        else:
            # off
            self._root_logger.handlers = []

    def getCurrentLogOnOff(self):
        """현재 로깅 기능이 켜져 있는지 확인하기 위한 메서드.
        
        self.log_onoff 인스턴스 변수에 저장된 값에 따라 반환.

        Returns
        -------
        bool
            True : 로깅 기능 켜져 있는 상태.
            False : 로깅 기능 꺼져 있는 상태.
        
        """
        return self.log_onoff
    
    def _getDebugVarLogger(
            self,
            modulename: str,
            classname: str | NoneType,
            methodname: str,
        ):
        """logVariable() 메서드 호출로 로깅을 시도하는 함수(또는 메서드)의 
        이름을 로거 객체 이름으로 사용하고, 해당 로거 객체를 생성, 호출하는 메서드.
        """
        debug_toplevel_name = DEFAULT_TOPLEVEL_LOGGERS[logging.DEBUG]
        # 주어진 매개변수들의 정보를 토대로 로거 이름 생성.
        if classname == 'NoneType':
            # 로깅하는 곳이 클래스의 메서드가 아닌 함수일 경우.
            logger_name = self._delimiter.join(
                [debug_toplevel_name, modulename, methodname]
            )
        else:
            # 클래스 내 특정 인스턴스 메서드 내에서 로깅할 경우.
            logger_name = self._delimiter.join(
                [debug_toplevel_name, modulename, classname, methodname]
            )
        logger_obj = logging.getLogger(logger_name)
        logger_obj.setLevel(logging.DEBUG)
        return logger_obj
    
    def logVariable(self, var_str: str):
        """특정 함수 또는 메서드 내 로깅하고자 하는 
        특정 지역 변수 이름을 문자열로 대입하면 해당 변수값을 로깅해주는 메서드. 

        해당 메서드는 특정 함수(또는 메서드) 안에서 호출하면 해당 함수의 이름과 
        메서드의 경우 해당 메서드가 포함된 클래스명까지 자동으로 추출한다. 

        만약 `var_str`로 대입된 변수를 찾지 못한다면 로깅 파일에 <The Variables Not Found>
        이라는 메시지가 대신 로깅됨. 

        만약 클래스 내 `__init__`에서 정의된 self. 로 시작되는 인스턴스 변수를 추적하여 
        로깅하고자 한다면 `var_str`에 'self.변수' 형식이 아닌 '변수' 형식으로 대입해야 함. 
        이 때, `__init__`에 정의되지 않은 self.로 시작되는 인스턴스 변수는 추적, 로깅이 안됨. 

        Parameters
        ----------
        var_str : str
            로깅하고자 하는 변수명의 문자열 형태. 

        Examples
        --------

        사용 예)

        >>> def calculator(a: int, b: int):
        ...     results = []
        ...     result = a + b
        ...     results.append(result)
        ...     result = a * b
        ...     results.append(result)

        위 예시 코드에서, calculator 함수 내 지역 변수인 result를 로깅하고자 한다면 
        다음과 같이 작성. 

        >>> from logpackage import CustomizablePackageLogger
        >>> dl = CustomizablePackageLogger()
        >>> def calculator(a: int, b: int):
        ...     results = []
        ...     result = a + b
        ...     dl.logVariable('result')
        ...     results.append(result)
        ...     result = a * b
        ...     dl.logVariable('result')
        ...     results.append(result) 

        """
        if not self.log_onoff: return

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
        # 위 코드와 같은 방법으로는 탐지되지 않는다. 클래스 내에서 __init__ 내에 정의된
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

        logger_obj = self._getDebugVarLogger(current_module_name, class_name, method_name)
        logmsg = ''.join([
                    f"module_name: {current_module_name}, class_name: {class_name}, ",
                    f"method_name: {method_name}, lineno: {current_lineno}\n",
                    f"variable: {var_str}: {target_var_value}"
                ])
        logger_obj.debug(logmsg)

    def _getTypeLogger(
            self,
            name: str | None,
            level: LoggerLevel | SpecialLoggerType
        ):
        """로거 객체명과 로거 타입을 레벨로 입력하면 해당 타입에 맞는 로거 객체 반환. 

        Parameters
        ----------
        name : str | None
            로거 객체 이름. 해당 로거 객체를 사용하는 모듈에서 __file__로 대입하면 
            해당 모듈명이 로거 객체명이 됨. 
        level : LoggerLevel | LOGGERTREE
            logging 모듈에서 제공하는 일부 level (DEBUG, INFO, ERROR) 
            또는 LOGGERTREE 상수. 
        
        """
        logger_obj = None

        base_logger_name = DEFAULT_TOPLEVEL_LOGGERS[level]
        if (name == ('' or 'root' or None)
                or name in DEFAULT_TOPLEVEL_LOGGERS.values()):
            logger_name = base_logger_name
        elif os.path.isfile(name) and inspect.getmodulename(name):
            logger_name = self._delimiter.join(
                    [base_logger_name, inspect.getmodulename(name)]
                )
        else:
            logger_name = self._delimiter.join([base_logger_name, name])
        logger_obj = logging.getLogger(logger_name)
        if level == LOGGERTREE:
            logger_obj.setLevel(logging.INFO)
        else:
            logger_obj.setLevel(level)

        self._log_hier.updateLoggerInfo()
        return logger_obj
    
    def getErrorLogger(self, name: str | None):
        """name 인자값을 이름으로 하는 에러 전용 로거 객체를 반환."""
        error_logger = self._getTypeLogger(name, logging.ERROR)
        return error_logger

    def getLoggerTreeLogger(self, name: str | None):
        """name 인자값을 이름으로 하는 로거 계층 트리 전용 로거 객체를 반환."""
        logger_tree_logger = self._getTypeLogger(name, LOGGERTREE)
        return logger_tree_logger

    def getInfoLogger(self, name: str | None):
        """name 인자값을 이름으로 하는 info 전용 로거 객체를 반환."""
        info_logger = self._getTypeLogger(name, logging.INFO)
        return info_logger

    def getDebugLogger(self, name: str | None):
        """name 인자값을 이름으로 하는 디버그 전용 로거 객체를 반환. 

        이 클래스의 logVariable() 메서드와는 따로 디버그 로거 객체를 생성하여 
        따로 쓰고자 할 때 사용. 
        """
        debug_logger = self._getTypeLogger(name, logging.DEBUG)
        return debug_logger
    
    def getCurrentHierarchy(self):
        """현재까지 등록된 모든 로거 객체들을 계층에 따라 트리 구조로 
        나타낸 문자열 반환. 
        """
        self._log_hier.updateLoggerInfo()
        return self._log_hier.getLoggerTree()

    def getCurrentAllLeafLoggers(self):
        """현재까지 등록된 모든 로거 객체들을 계층에 따라 트리 구조로 나타낼 때 
        leaf 노드에 해당하는 모든 로거 객체 이름들을 리스트로 모아 반환. 
        """
        self._log_hier.updateLoggerInfo()
        return self._log_hier.getLeafLoggersName()

    def logAllLoggersTree(self):
        """현재까지 생성된 모든 로거 객체들의 이름을 계층 트리 형태로 
        로깅함. 
        """
        hierarchy_logger = logging.getLogger(
            DEFAULT_TOPLEVEL_LOGGERS[LOGGERTREE]
        )
        hierarchy_logger.setLevel(logging.INFO)
        tree_str = self.getCurrentHierarchy()
        all_leaf = self.getCurrentAllLeafLoggers()
        all_leaf = '\n'.join(all_leaf)
        hierarchy_logger.info(f"{tree_str}\n\n{all_leaf}")


class LogFileManager():
    """로그 파일 및 디렉토리를 조작, 관리하는 기능의 클래스. 

    이 클래스에서 진행되는 모든 작업은 로그 파일들을 하나로 모아 
    관리하는 베이스 디렉토리 안에서만 진행된다.

    추후 추가 예정 기능들.
    1. 로그 파일들 중 원하는 로그 파일의 내용을 전부 지우는 기능. 
    또는 날짜별 또는 베이스 디렉토리 내 모든 로그 파일 내 내용을 지우는 기능. 
    (로그 파일 자체를 삭제하지는 않음.)
    2. 특정 로그 파일 또는 날짜 디렉토리를 삭제하는 기능. 
    또는 특정 디렉토리 또는 베이스 디렉토리 내 모든 내용물을 삭제하는 기능. 
        - 오늘 날짜를 기준으로 특정 기간 이상 지난 날짜 디렉토리와 그 안의 
        로그 파일들을 삭제하는 기능 추가 예정.
    (베이스 디렉토리 자체를 삭제하는 기능도 추가 예정)
    3. 베이스 디렉토리 내 로그 파일들을 zip 파일로 압축하는 기능.
        - 날짜별로 구분되어 있는 경우, 여러 날짜 디렉토리 중 원하는 
        날짜의 디렉토리와 그 안의 로그 파일들만 zip 파일로 압축하거나, 
        베이스 디렉토리 내에 있는 모든 날짜별 디렉토리들을 압축하는 기능.

    """
    # 상수 정의
    DELETE_MODE = 'delete'
    ERASE_MODE = 'erase'

    def __init__(self, base_dir_path: DirPath = None):
        """
        Parameters
        ----------
        base_dir_path
            로그 파일들을 하나로 모아 저장, 관리하고 있는 
            베이스 디렉토리 경로.

        Raises
        ------
        FileNotFoundError
            base_dir_path 매개변수로 입력한 경로가 존재하지 않거나 
            디렉토리가 아닐 경우 발생.

        """
        if base_dir_path is not None and not os.path.isdir(base_dir_path):
            err_msg = """base_dir_path 매개변수로 입력한 경로가 
            존재하지 않거나 디렉토리가 아닙니다.
            """
            raise FileNotFoundError(err_msg)
        self.base_dir_path = base_dir_path
        self.txthandler = fdh.TextFileHandler(create_dir_ok=False)

    def setBaseDirPath(self, new_basedir_path: DirPath):
        """로그 파일들을 하나로 모아 저장, 관리하고 있는 
        베이스 디렉토리 경로 설정.

        Raises
        ------
        FileNotFoundError
            new_basedir_path 매개변수로 입력한 경로가 존재하지 않거나 
            디렉토리가 아닐 경우 발생.
        
        """
        if not os.path.isdir(new_basedir_path):
            err_msg = """new_basedir_path 매개변수로 입력한 경로가 
            존재하지 않거나 디렉토리가 아닙니다.
            """
            raise FileNotFoundError(err_msg)
        self.base_dir_path = new_basedir_path

    def eraseAllInLogFile(
            self, 
            date_dirname: DirName | None,
            logfile_name: FileName,
            find_all_files: bool = False
        ):
        """특정 로그 파일 내 모든 로그 기록을 지우는 메서드.

        Parameters
        ---------
        date_dirname : Dirname(str) | None
            내용을 지우고자 하는 로그 파일이 날짜 디렉토리 안에 
            있을 경우 해당 디렉토리명을 문자열로 입력. 
            만약 해당 로그 파일이 날짜 디렉토리 안이 아닌 
            베이스 디렉토리에 존재한다면 None을 입력.
            날짜 디렉토리명은 tools.DateTools().getDateStr() 메서드의 
            반환 형태 중 하나와 맞아야 함. 
            자세한 반환 형태는 해당 메서드의 독스트링의 Returns 참조.
        logfile_name : FileName(str)
            내용을 지우고자 하는 로그 파일 이름.
        find_all_files : bool, default False
            logfile_name 매개변수 값과 동일한 파일명을 가지는 
            모든 로그 파일들을 찾아 내용을 지울지 결정하는 메서드. 
            True시 베이스 디렉토리 내 logfile_name과 같은 파일명을 
            가지는 모든 로그 파일들에 대해 내용 삭제 작업이 진행되며, 
            이는 date_dirname 매개변수에 지정된 값과 상관없이 진행된다. 
            False시 지정된 위치의 로그 파일에만 내용 삭제 작업을 진행한다. 
            date_dirname에 지정된 디렉토리 내 로그 파일의 내용만 지우고, 만약 
            해당 매개변수가 None이면 베이스 디렉토리 내에 있는 해당 로그 
            파일을 찾아 해당 파일에만 작업 수행.

        Returns
        -------
        bool
            해당 로그 파일이 존재하여 작업을 수행헀다면 True를, 해당 로그 파일이 단 
            하나도 존재하지 않아 작업을 수행할 수 없었다면 False를 반환.
        
        """
        if not logfile_name.endswith('.log'):
            logfile_name = '.'.join(logfile_name, 'log')
        
        if find_all_files:
            all_leaf_fds = dirs.get_all_in_rootdir(self.base_dir_path)
            count_removed = 0
            for fd in all_leaf_fds:
                if os.path.basename(fd) == logfile_name:
                    self.txthandler.setTxtFilePath(fd)
                    self.txthandler.writeNew('')
                    count_removed += 1
            if count_removed == 0: return False
        else:
            if date_dirname:
                if tools.DateTools().isDateStr(date_dirname) is None:
                    return False
                logpath = os.path.join(self.base_dir_path, date_dirname)
                logpath = os.path.join(logpath, logfile_name)
            else:
                logpath = os.path.join(self.base_dir_path, logfile_name)
            if not os.path.isfile(logpath): return False
            self.txthandler.setTxtFilePath(logpath)
            self.txthandler.writeNew('')
        return True

    def eraseAllInDateDir(
            self,
            date_dirname: DirName
        ):
        """특정 날짜 디렉토리 내 모든 로그 파일 내 내용들을 전부 지운다.

        Parameters
        ----------
        date_dirname : DirName(str)
            날짜 디렉토리명은 tools.DateTools().getDateStr() 메서드의 
            반환 형태 중 하나와 맞아야 함. 
            자세한 반환 형태는 해당 메서드의 독스트링의 Returns 참조.

        Returns
        -------
        bool
            해당 로그 파일이 존재하여 작업을 수행헀다면 True를, 해당 로그 파일이 단 
            하나도 존재하지 않아 작업을 수행할 수 없었다면 False를 반환.

        """
        if tools.DateTools().isDateStr(date_dirname) is None: return False
        date_dir_fullpath = os.path.join(self.base_dir_path, date_dirname)
        if not os.path.isdir(date_dir_fullpath): return False

        all_leaf_fds = dirs.get_all_in_rootdir(date_dir_fullpath)
        count_removed = 0
        for fd in all_leaf_fds:
            if os.path.basename(fd).endswith('.log'):
                self.txthandler.setTxtFilePath(fd)
                self.txthandler.writeNew('')
                count_removed += 1
        if count_removed == 0: return False
        return True

    def deleteLogFile(
            self,
            date_dirname: DirName | None,
            logfile_name: FileName,
            find_all_files: bool = False
        ):
        """특정 로그 파일을 삭제한다. 

        Parameters
        ----------
        date_dirname : DirName(str) | None
            삭제하고자 하는 로그 파일이 날짜 디렉토리 안에 있는 경우, 
            해당 날짜 디렉토리명을 문자열로 입력. 만약 로그 파일이 
            날짜 디렉토리가 아닌 베이스 디렉토리 내에 있는 경우 None을 
            입력.
            날짜 디렉토리명은 tools.DateTools().getDateStr() 메서드의 
            반환 형태 중 하나와 맞아야 함. 
            자세한 반환 형태는 해당 메서드의 독스트링의 Returns 참조.
        logfile_name : FileName(str)
            삭제하고자 하는 로그 파일명.
        find_all_files : bool, default False
            True시 date_dirname 매개변수에 지정한 날짜 디렉토리에 상관없이 
            베이스 디렉토리 내 logfile_name 매개변수에 지정된 로그 파일명을 
            가지는 모든 로그 파일들에 대해 삭제 작업을 진행한다. 
            False시 지정된 로그 파일만 지운다. date_dirname 매개변수에 
            지정된 날짜 디렉토리 내의 logfile_name 매개변수로 지정된 
            로그 파일만을 지우고, 만약 date_dirname이 None일 경우 베이스 
            디렉토리에서 해당 로그 파일을 찾아 지운다. 

        Returns
        -------
        bool
            해당 로그 파일이 존재하여 작업을 수행헀다면 True를, 해당 로그 파일이 단 
            하나도 존재하지 않아 작업을 수행할 수 없었다면 False를 반환.
        
        """
        if not logfile_name.endswith('.log'):
            logfile_name = '.'.join(logfile_name, 'log')
        if find_all_files:
            all_leaf_fds = dirs.get_all_in_rootdir(self.base_dir_path)
            count_removed = 0
            for fd in all_leaf_fds:
                if os.path.basename(fd) == logfile_name:
                    try:
                        os.remove(fd)
                    except:
                        pass
                    else:
                        count_removed += 1
            if count_removed == 0: return False
        else:
            if date_dirname:
                if tools.DateTools().isDateStr(date_dirname) is None:
                    return False
                logpath = os.path.join(self.base_dir_path, date_dirname)
                logpath = os.path.join(logpath, logfile_name)
            else:
                logpath = os.path.join(self.base_dir_path, logfile_name)
            try:
                os.remove(logpath)
            except FileNotFoundError:
                return False
            return True

    def deleteAllInDateDir(
            self,
            date_dirname: DirName,
            delete_dir: bool = False
        ):
        """특정 날짜 디렉토리 내 모든 로그 파일들을 삭제한다. 

        Parameters
        ----------
        date_dirname : DirName(str)
            안의 로그 파일들을 모두 삭제할 날짜 디렉토리명을 문자열로 대입.
            날짜 디렉토리명은 tools.DateTools().getDateStr() 메서드의 
            반환 형태 중 하나와 맞아야 함. 
            자세한 반환 형태는 해당 메서드의 독스트링의 Returns 참조.
        delete_dir : bool, default False
            date_dirname 매개변수로 지정된 디렉토리 내 모든 로그 파일들을 
            삭제하고나서 해당 디렉토리 자체도 지울지 결정하는 매개변수.
            True시 해당 디렉토리 자체도 삭제하고, False시 해당 디렉토리는 
            삭제하지 않고 남긴다.

        Returns
        -------
        bool
            해당 로그 파일이 존재하여 작업을 수행헀다면 True를, 해당 로그 파일이 단 
            하나도 존재하지 않아 작업을 수행할 수 없었다면 False를 반환.
        
        """
        if tools.DateTools().isDateStr(date_dirname) is None: return False
        date_dir_fullpath = os.path.join(self.base_dir_path, date_dirname)
        if not os.path.isdir(date_dir_fullpath): return False

        if delete_dir:
            if dirs.validate_if_your_dir_with_ext(
                date_dir_fullpath, ['.log'])[0]:
                shutil.rmtree(date_dir_fullpath)
                return True
            return False

        all_leaf_fds = dirs.get_all_in_rootdir(date_dir_fullpath)
        count_removed = 0
        for fd in all_leaf_fds:
            if os.path.basename(fd).endswith('.log'):
                try:
                    os.remove(fd)
                except:
                    continue
                else:
                    count_removed += 1
        if count_removed == 0: return False
        return True

    def rotateDateDirs(
            self,
            maxdir: int = 10
        ):
        """베이스 디렉토리 내 로그 파일 기록용 날짜 디렉토리들의 
        개수를 제한하는 메서드. 

        만약 날짜 디렉토리 개수가 지정된 개수를 넘을 경우 가장 
        오래된 날짜 디렉토리와 그 안의 모든 로그 파일들을 자동으로 삭제한다. 
        이는 새로운 날짜 디렉토리가 생성될 때도 마찬가지로 적용된다. 
        tools.py의 DateTools 클래스가 인식할 수 있는 날짜 문자열을 가진 
        디렉토리들에 대해서만 해당 작업이 가능.

        인식 가능한 날짜 문자열 형식)
        DAY : 'YYYY-MM-DD'
        WEEK : 'YYYY-MM-N주'
        MONTH : 'YYYY-MM'
        YEAR : 'YYYY'

        만약 베이스 디렉토리 내 날짜 디렉토리들의 날짜 형태가 섞여 있다면, 
        모든 날짜 디렉토리명의 날짜 문자열들을 'YYYY-MM-DD' 형태로 변환한 뒤,
        가장 오래된 날짜 문자열을 가진 디렉토리를 삭제한다. 
        만약 둘 이상의 같은 날짜가 감지되면, 디렉토리명의 알파벳 순으로 삭제한다. 
        
        Parameters
        ----------
        maxdir : int, default 10
            베이스 디렉토리 내에 남길 날짜 디렉토리의 개수. 
        
        """
        data = tools.DateTools().searchDateDirBirth(self.base_dir_path)
        if data is None:
            err_msg = """로그 파일들을 보관, 관리하는 베이스 디렉토리의 경로가 
            검색되지 않았습니다. 초기에 베이스 디렉토리 경로를 설정하지 않았거나 
            잘못된 경로를 설정했습니다. setBaseDirPath() 메서드를 통해 대상 
            베이스 디렉토리 경로를 설정해주세요. 
            """
            raise logexc.NotInitConfigError(err_msg)
        
        temp = []
        for dtype, dtime, dpath in data:
            if dirs.validate_if_your_dir_with_ext(dpath, ['.log'])[0]:
                temp.append((dtype, dtime, dpath))
        data = temp.copy()
        
        diff = maxdir - len(data)
        if diff < 0:
            for i in range(-diff):
                dirpath = data[i][-1]
                shutil.rmtree(dirpath)

    def zipDateDir(
            self,
            date_dir: DirName,
            left_original: bool
        ):
        """특정 날짜 디렉토리를 zip파일로 압축한다. 

        zip파일은 지정된 베이스 디렉토리 안에 저장된다.

        Parameters
        ----------
        date_dir : DirName(str)
            압축할 날짜 디렉토리
        left_original : bool
            zip파일로 압축한 이후, 원본 날짜 디렉토리를 남길지를 결정하는 매개변수.
            True시 원본 날짜 디렉토리를 남긴다.
            False시 원본 날짜 디렉토리를 삭제한다. 
        
        """
        ...
    
    def zipAllDateDir(
            self,
            separate: bool,
            left_original: bool
        ):
        """지정된 베이스 디렉토리 내 모든 날짜 디렉토리들을 
        zip 파일로 압축한다. 

        해당 zip파일들은 지정된 베이스 디렉토리 내에 저장된다.
        
        날짜 디렉토리가 아닌 개별 파일로 베이스 디렉토리에 저장된 로그 
        파일들도 자동으로 압축해준다. 

        Parameters
        ----------
        separate : bool
            지정된 베이스 디렉토리 내 모든 날짜 디렉토리들을 zip파일로 
            압축할 떄, 날짜별로 따로따로 zip파일로 압축할지, 아니면 모든 
            날짜 디렉토리들을 하나의 zip파일로 압축할지를 결정하는 매개변수.
            True시 날짜별로 나눠서 zip파일로 압축.
            False시 모든 날짜 디렉토리를 하나로 모아 하나의 zip파일로 압축.
            베이스 디렉토리에 있는 개별 로그 파일들은 해당 매개변수 값에 상관없이
            모두 하나의 zip파일로 압축된다. 날짜 디렉토리들과 섞여 있는 경우, 
            날짜 디렉토리와는 구별되어 압축된다.
        left_original : bool
            zip파일로 압축한 뒤, 원본 디렉토리들을 그대로 남길지 결정하는 매개변수.
            True시 원본 디렉토리 및 로그 파일들을 그대로 남긴다.
            False시 원본 디렉토리 및 로그 파일들은 모두 삭제한다.
        
        """
        ...


if __name__ == '__main__':
    pass
    