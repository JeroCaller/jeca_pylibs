"""로깅 관련 예외들을 정의한 모듈."""
import logging

# ===== 에러 메시지 상수 모음 =====
NO_TOPLEVEL_MODULE_AND_BASE_DIR = """
사용자가 작업하고 있는 프로젝트 패키지에서의 
최상위 모듈(ex. main.py)이 지정되지 않았습니다. 이로 인해, 
로그 파일들을 한꺼번에 저장하고 관리할 베이스 디렉토리의 위치를 
설정할 수 없었습니다. 해당 에러를 고치려면 다음의 선택지들 중 하나를 택하십시오.

    1. setTopLevelModulePath() 메서드를 통해 최상위 모듈의 경로를 대입하여
    해당 패키지 내 최상위 모듈이 무엇인지를 알려주삽시오. 
    2. setBaseDir() 메서드를 통해 로그 파일 저장, 관리 베이스 디렉토리의 위치와 
    해당 디렉토리명을 따로 지정해주십시오.
"""
NO_BASE_DIR = """
로그 파일 저장 베이스 디렉토리 경로가 
올바르지 않거나 설정되지 않았습니다. 올바른 베이스 디렉토리 
경로를 먼저 설정해야 합니다. 이 에러를 고치기 위해선 다음의 
선택지들 중 하나를 선택하여 실행해야 합니다.

    1. 베이스 디렉토리를 따로 지정하지 않았고, 시스템에서 
    자동으로 정해주길 원한다면, 이 클래스의 setTopLevelModulePath() 
    메서드에서 현재 로깅하고자 하는 프로젝트 패키지 내 최상위 모듈의 
    경로를 대입합니다. 
    2. 따로 베이스 디렉토리의 위치와 해당 디렉토리명을 지정하고자 한다면 
    이 클래스의 setBaseDir() 메서드를 통해 지정합니다.
"""
# ================================


class LogLowestLevelError(Exception):
    """현재 logger 객체에 설정된 최소 level이 필수 최소 level보다 높을 경우 발생하는 에러. 
    로깅 되어야 할 메시지가 최소 level을 만족시키지 않아 로깅되지 않는 것을 방지하기 위함. 

    예) 
    현재 logger 객체 최소 level: WARNING
    필수 최소 level: INFO
    => 현재 logger 객체의 INFO 수준의 로그 메시지가 로깅되지 않는다. 
    즉, current_level <= required_level 조건을 만족해야함.
    """
    def __init__(self, current_level: int, required_level: int):
        """
        Parameters
        ----------
        current_level : int
            현재 Logger 객체에 설정된 최소 level의 수치값. 
        required_level : int
            정해진 최소 level의 수치값. 
        
        """
        current_levelname = logging.getLevelName(current_level)
        required_levelname = logging.getLevelName(required_level)
        error_msg = "LogLowestLevelError: 현재 Logger 객체의 최소 level이 정해진 최소 level보다 높습니다.\n"
        error_msg += f"현재 logger 객체의 최소 level: {current_levelname}\n"
        error_msg += f"정해진 최소 level: {required_levelname}"
        super().__init__(error_msg)


class NotInitializedConfigError(Exception):
    """무언가를 초기 설정하지 않고 다른 기능 이용 시 발생시키는 예외."""
    def __init__(self, error_msg: str = ""):
        super().__init__(error_msg)

