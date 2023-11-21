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
import warnings
from typing import Literal, TypeAlias

import logexc
from sub_modules.tree import PathTree
from sub_modules.tree import AbsPath
from sub_modules import tools

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
            해당 로거 객체의 최소 level이 적어도 INFO 이하로 지정되어야 함. 
            그래야 해당 로거 객체에 연결된 파일 대상에 로그 기록 가능. 

        Raises
        ------
        LogLowestLevelError
            `logger_obj` 매개변수의 로거 객체에 설정된 level이 
            ERROR보다 높을 경우 발생.
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
        """현재 등록된 모든 로거 객체들의 이름을 
        계층을 가진 트리로 보여주는 클래스. 
        """
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

    추가 예정 옵션들.
    * 디버그, 에러 등의 로그들을 수준에 따라 분류하여 저장할 것인지 
    아니면 하나의 로그 파일로 저장할 것인지를 결정하는 옵션.
    * 로그 파일들을 날짜별로 저장하는 옵션. 하루 단위로 로그 내역들을 
    하나의 파일에 담아 저장하여 하루 단위로 구별할 것인지, 아니면 
    달, 년 단위로 구별할 것인지에 대한 옵션.
    * 로그 파일들을 원할 때 zip파일로 묶는 옵션. 사용자가 원할 때 
    zip으로 묶는 옵션과 기간(일, 월, 년 등) 단위로 특정 날짜가 되면 자동으로 
    기존의 로그 파일들을 설정한 기간 단위로 zip으로 묶는 옵션.

    logging 내장 라이브러리를 이용하며, 해당 라이브러리의 루트 로거 객체를 
    이용함.

    """
    def __init__(self):
        self._root_logger = logging.getLogger()

        self.top_level_loggers_name: dict[LoggerLevel, str] = {}
        self.base_dir: str = ''
        self.date_type: tools.DateOptions = None
        self.toplevel_module_path: str = ''
        self.date_tool_obj = tools.DateTools()
        self.common_formatter: logging.Formatter \
            = self._getDefaultCommonFormatter()
        self.level_formatters: dict[LoggerLevel, logging.Formatter] = {}

    def setBaseDir(
            self, 
            path: str, 
            dirname: str | None = None
        ):
        """로그 파일들을 저장, 관리할 베이스 디렉토리의 위치를 지정하고, 
        디렉토리명을 결정한다. 

        Parameters
        ----------
        path : str
            로그 파일들을 저장할 베이스 디렉토리를 위치시킬 상위 디렉토리의 
            주소 대입. 
        dirname : str | None, default None
            로그 파일들을 저장할 베이스 디렉토리에 지어줄 이름 대입. 
            None 대입 시 'logfiles'라는 이름을 기본으로 설정된다. 
        
        """
        path = os.path.abspath(path)
        if dirname is None: dirname = 'logfiles'
        self.base_dir = os.path.join(path, dirname)

    def setTopLevelModulePath(self, module_path: str = ''):
        """로깅할 패키지 내 최상위 모듈 경로를 지정하는 메서드. 
        최상위 모듈(ex. main.py) 내에서 인자로 __file__을 대입하면 된다.

        Parameters
        ----------
        module_path : str
            최상위 모듈의 경로. 최상위 모듈 내에서 __file__를 대입하면 됨.
        
        """
        self.toplevel_module_path = module_path
        
    def setTopLevelLoggersName(self, data: dict[LoggerLevel, str]):
        """디버그, 에러, Info, 로거 객체 트리 기록 등의 각각의 수준에 따른 
        최상위 로거 이름을 설정한다. 

        로그 수준별로 나눠 각각의 로그 파일로 기록하고자 한다면 해당 메서드를 통해 
        최상위 로거 이름 설정이 필수.

        Parameters
        ----------
        data : dict[LoggerLevel, str]
            각 수준과 그 수준에서의 최상위 로거 객체 이름 정보가 담긴 
            딕셔너리.
            
        """
        self.top_level_loggers_name = data

    def setDate(self, option: tools.DateOptions):
        """로그 파일들을 기간별로 구분할 것인지를 결정하는 메서드.
        
        일, 주, 월, 연 단위로 로그 파일들을 각 폴더 안에 묶어 저장시키도록 
        설정할 수 있다. 또는 기간 구분 없이 모든 로그 파일들을 하나의 
        폴더에 몰아 넣어 저장하는 방식을 택할 수도 있다. 

        Parameters
        ----------
        option : self.DateOptions
            이 클래스(LogFileEnvironment)의 클래스 속성으로 정의된 
            클래스 DateOptions 내에 저장된 여러 상수들 중 하나를 택해 대입. 
            가능한 옵션들)
            DAY : 하루 단위로 로그 파일들을 폴더로 구분하여 저장.
            WEEK : 주 단위로 로그 파일들을 구분하여 저장.
            MONTH : 월 단위로 로그 파일들을 구분하여 저장.
            YEAR : 연 단위로 로그 파일들을 구분하여 저장.
            FREE : 기간 구분 없이 한 폴더 안에 모든 로그 파일들을 저장.
        
        """
        self.date_type = option

    def setLevelOption(
            self, 
            option: dict[LoggerLevel, str] | None
        ):
        """로그 파일들을 저장할 때 디버그, 에러, INFO 별로 로그 파일들을 나눠서 
        저장할 지, 아니면 모든 수준의 로그 기록들을 하나의 로그 파일 안에 몰아서 
        저장할 지에 대한 옵션을 결정하는 메서드. 

        Parameters
        ----------
        option : dict[LoggerLevel, TopLevelLoggerName] | None
            로그 파일들을 여러 수준으로 나눠서 저장하고자 하는 경우, 각 level 숫자와 
            각 level의 최상위 로거 객체 이름을 딕셔너리 형태로 기입한다. 자세한 예시는 
            아래 Examples 부분에 설명.
            None으로 설정 시 모든 수준의 로그들을 하나의 로그 파일 안에 저장한다. 

        Examples
        --------

        로그 파일들을 여러 수준으로 나누고 각 수준들의 로그들을 각각의 로그 파일에 
        기록, 저장하고자 할 경우, 각 수준의 최상위 로거 객체 이름을 딕셔너리 형태로 
        option 매개변수에 지정한다. 그러면 이후 각 수준의 로그 객체들은 해당 수준의 
        최상위 로거 객체 안에서 관리하게끔 함.

        예시)
        option = {
            logging.DEBUG : '__debug_log__', 
            logging.ERROR : '__error_log__',
            logging.INFO : '__info_log__',
        }

        """
        self.top_level_loggers_name = option

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
            문자열 포맷을 공통적으로 적용하지 않게 하려면 None으로 설정.

        See Also
        --------
        setLevelFormatter
        
        """
        if strfmt is None:
            self.common_formatter = None
            return
        self.common_formatter = logging.Formatter(strfmt)

    def _getDefaultCommonFormatter(self):
        """모든 로그 파일에 공통적으로 적용할 포맷을 사용자가 따로 지정하지 
        않은 경우, 기본 설정 포맷터를 사용하도록 한다.
        """
        format_str = "%(asctime)s - %(levelname)s \n%(message)s"
        return logging.Formatter(format_str)

    def setLevelFormatter(self, level: LoggerLevel, strfmt: str):
        """각 수준에 따른 로그 문자열 포맷 결정 메서드. 
        해당 포맷 문자열은 logging.Formatter() 객체 생성자에 대입하여 자동으로 
        생성하여 저장해줌. 
        
        예를 들어 이미 디버그 수준에 포맷을 설정한 상태에서 해당 수준에 다른 
        포맷을 설정하려고 시도하는 경우, 새로운 포맷으로 대체됨.

        만약 setCommonFormatter() 메서드를 통해 모든 로그 수준에 똑같은 
        로그 문자열 포맷을 지정한 경우, 이를 무시하고 각 로그 수준에 적용된 
        로그 포맷을 따른다.

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
        
        """
        self.level_formatters[level] = logging.Formatter(strfmt)

    def clearLevelFormatter(self):
        """여태까지 설정된 로그 수준별 포맷터들을 삭제한다."""
        self.level_formatters.clear()

    def generateDateDirPath(self):
        """오늘 실행된 로그 파일들을 오늘 날짜를 이름으로 가지는 
        하위 디렉토리에 저장하기 위해, 해당 디렉토리의 경로를 결정하고 
        반환하는 메서드. 

        해당 메서드는 해당 디렉토리의 경로만 생성할 뿐, 실제로 해당 
        디렉토리를 생성하지는 않음.
        """
        ...
        # 사용자가 이미 setDate() 메서드를 통해 로그 파일 구분 기준 기간을
        # 설정한 경우, 연도로 설정한 경우는 연도만, 월로 설정한 경우는
        # 연도-월로, 일로 설정한 경우는 연도-월-일 형태의 디렉토리명으로
        # 설정하도록 하는 코드 구현 필요. 
        # 만약 FREE로 기간 설정을 하지 않는 경우, 하위 디렉토리명을 
        # 생성하지 않도록 제한한다.

    def setLoggerEnvironment(self):
        """
        """
        def by_levels():
            """수준별 로거 객체들에 대한 핸들러, 포맷 등의 설정 함수."""
            def get_formatter(level: LoggerLevel):
                if self.level_formatters:
                    return self.level_formatters[level]
                return self.common_formatter
                
            def get_filter(level: LoggerLevel):
                error_msg = """각 로그 수준에 따른 최상위 로거 객체 이름을 
                    설정하지 않았습니다. setTopLevelLoggersName() 메서드를 통해 
                    먼저 설정해야 합니다.
                    """
                if not self.top_level_loggers_name:
                    raise logexc.NotInitializedConfigError(error_msg)
                try:
                    new_filter = logging.Filter(
                        self.top_level_loggers_name[level]
                    )
                except KeyError:
                    missing_level = logging.getLevelName(level)
                    error_msg2 = f"""{missing_level} 수준에 설정된 
                    최상위 로거 객체 이름이 설정되지 않았습니다. 
                    setTopLevelLoggersName() 메서드를 통해 설정 필요.
                    """
                    raise logexc.NotInitializedConfigError(error_msg2)
                return new_filter
            
            for level, logger_name in self.top_level_loggers_name.items():
                formatter_obj = get_formatter(level)
                filter_obj = get_filter(level)
                ...

        def by_all_in_one():
            """모든 수준의 로그들을 하나의 로그 파일로 저장하고자 할 때의
            로거 객체에 대한 핸들러, 포맷 등의 설정 함수.
            """
            ...

        if self.top_level_loggers_name:
            by_levels()
        else:
            # if not self.top_level_loggers_name
            by_all_in_one()


class PackageLogger():
    """패키지 내 특정 함수, 메서드의 특정 지역변수를 로깅하고자 할 때 사용하는 클래스.
    
    .. deprecated:
        나중에 해당 클래스가 삭제될 예정. 해당 클래스에서는 핸들러 커스터마이징, 
        로그 파일 기록 및 관리 방법 선택 등의 기능이 없기 때문. 
        향후 CustomizablePackageLogger 클래스로 대체될 예정.
    
    """
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
        Parameters
        ---------
        current_module_abspath : __file__ | None, default=None
            패키지 내 모듈 중 최상위 모듈(ex) main.py)의 절대경로. 
            해당 모듈에서 '__file__'을 대입하면 됨. 처음 해당 클래스를 인스턴스화한 후에는 
            해당 매개변수에 값을 대입 안해도 됨. 
            None 입력 시 기본으로 지정된 주소에 디렉토리 형성. 

        """
        warning_msg = "현재 PackageLogger 클래스는 추후에 삭제되고 다른 클래스로 대체될 예정."
        warnings.warn(warning_msg, DeprecationWarning)
        if PackageLogger._is_initialized is False:
            if current_module_abspath is None: return
            self._delimiter = '.'
            self._lh = _LoggerHierarchy()
            self._root_logger = logging.getLogger()
            self._root_logger.setLevel(logging.DEBUG)
            self.current_module_abspath = current_module_abspath
            self.log_onoff = True  # 로깅 온오프 기능.
            self._log_off_handler = logging.NullHandler()

            self._top_level_loggers = {
                LOGGERTREE: "__log_hierarchy__",
                logging.DEBUG: "__debug__",
                logging.ERROR: "__error__",
                logging.INFO: "__info__"
            }

            self.debug_log_file_path, self.error_log_file_path, \
            self.hierarchy_log_file_path = self._defaultSetLogDirFile()
            self._setLoggerEnvironment()
            self._lh.updateLoggerInfo()

            PackageLogger._is_initialized = True

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
            self._setLoggerEnvironment()
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

    def _defaultSetLogDirFile(self):
        """로그 파일명, 로그 파일들을 담을 디렉토리의 이름 및 경로 설정 등에 대해 
        이 메서드에서의 설정을 디폴트 설정으로 하고 디폴트 설정한다. 
        """
        if self.current_module_abspath is None: return None
        logfilesdirname = "logfiles"  # 로그 파일을 담을 폴더명.
        logdir = os.path.dirname(self.current_module_abspath)  # 로그 파일들을 담을 폴더를 생성할 주소.
        logdirfullpath = _makedir(logdir, logfilesdirname)

        debug_log_file_name = 'debug.log'
        debug_log_file_path = os.path.join(logdirfullpath, debug_log_file_name)
        error_log_file_name = 'error.log'
        error_log_file_path = os.path.join(logdirfullpath, error_log_file_name)
        tree_log_file_name = 'logger_tree.log'
        tree_log_file_path = os.path.join(logdirfullpath, tree_log_file_name)

        return debug_log_file_path, error_log_file_path, tree_log_file_path

    def logVariable(self, var_str: str):
        """특정 함수 또는 메서드 내 로깅하고자 하는 
        특정 지역 변수 이름을 문자열로 대입하면 해당 변수값을 로깅해주는 메서드. 

        해당 메서드는 특정 함수(또는 메서드) 안에서 호출하면 해당 함수의 이름과 
        메서드의 경우 해당 메서드가 포함된 클래스명까지 자동으로 얻는다. 

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
        """logVariable() 메서드를 호출하는 함수 또는 메서드의 이름을 
        로거 객체 이름으로 사용하고 해당 로거 객체를 생성 또는 호출함. 
        """
        debug_base_name = self._top_level_loggers[logging.DEBUG]
        # 주어진 매개변수들의 정보를 토대로 로거 이름 생성.
        if classname == 'Nonetype':
            # 로깅하는 곳이 클래스의 메서드가 아닌 함수일 경우.
            logger_name = self._delimiter.join([debug_base_name, modulename, methodname])
        else:
            # 클래스 내 특정 인스턴스 메서드 내에서 로깅할 경우.
            logger_name = self._delimiter.join(
                [debug_base_name, modulename, classname, methodname])
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        return logger

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

    def getDebugLoggerExplictly(self, name: str | None):
        """name 인자값을 이름으로 하는 디버그 전용 로거 객체를 반환. 

        이 클래스의 logVariable() 메서드와는 따로 디버그 로거 객체를 생성하여 
        따로 쓰고자 할 때 사용. 
        """
        debug_logger = self._getTypeLogger(name, logging.DEBUG)
        return debug_logger

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
        base_logger_name = self._top_level_loggers[level]
        if (name == ('' or 'root' or None)
                or name in self._top_level_loggers.values()):
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

        self._lh.updateLoggerInfo()
        return logger_obj

    def _setLoggerEnvironment(self):
        """로거 객체의 핸들러 관련 설정. 

        루트 로거에 적용되고, 모든 자식 로거에 자동 적용되도록 함. 
        """
        # 각 핸들러에 다른 포맷이 적용될 수도 있음을 대비해
        # 각각의 포매터를 따로 정의함.
        debug_filter = logging.Filter(self._top_level_loggers[logging.DEBUG])
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

        info_filter = logging.Filter(self._top_level_loggers[logging.INFO])
        info_file_handler = logging.FileHandler(
            filename=self.debug_log_file_path,
            encoding='utf-8'
        )
        info_file_handler.setLevel(logging.INFO)
        info_file_handler.setFormatter(debug_formatter)
        info_file_handler.addFilter(info_filter)
        self._root_logger.addHandler(info_file_handler)

        error_filter = logging.Filter(self._top_level_loggers[logging.ERROR])
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

        hierarchy_filter = logging.Filter(self._top_level_loggers[LOGGERTREE])
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
        """로그 파일 내용을 비운다. (로그 파일을 삭제하진 않음.)

        Parameters
        ----------
        file : ALLFILES | DEBUGFILE | ERRORFILE | LOGGERFILE
            삭제할 파일을 결정한다. 
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
            filepath = self.hierarchy_log_file_path
        else:
            return

        with open(filepath, 'w', encoding='utf-8'):
            pass

    def getCurrentHierarchy(self):
        """현재까지 등록된 모든 로거 객체들을 계층에 따라 트리 구조로 
        나타낸 문자열 반환. 
        """
        self._lh.updateLoggerInfo()
        return self._lh.getLoggerTree()

    def getCurrentAllLeafLoggers(self):
        """현재까지 등록된 모든 로거 객체들을 계층에 따라 트리 구조로 나타낼 때 
        leaf 노드에 해당하는 모든 로거 객체 이름들을 리스트로 모아 반환. 
        """
        self._lh.updateLoggerInfo()
        return self._lh.getLeafLoggersName()

    def logAllLoggersTree(self):
        """현재까지 생성된 모든 로거 객체들의 이름을 계층 트리 형태로 
        로깅함. 
        """
        hierarchy_logger = logging.getLogger(
            self._top_level_loggers[LOGGERTREE])
        hierarchy_logger.setLevel(logging.INFO)
        tree_str = self.getCurrentHierarchy()
        all_leaf = self.getCurrentAllLeafLoggers()
        all_leaf = '\n'.join(all_leaf)
        hierarchy_logger.info(f"{tree_str}\n\n{all_leaf}")


class CustomizablePackageLogger():
    """로그 관련 설정을 원하는대로 설정할 수 있는 클래스."""
    def __init__(self):
        """
        """
        ...


if __name__ == '__main__':
    pl = PackageLogger()
    