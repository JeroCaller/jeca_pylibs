"""로깅 관련 예외들을 정의한 모듈."""
import logging


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

