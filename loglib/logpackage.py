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