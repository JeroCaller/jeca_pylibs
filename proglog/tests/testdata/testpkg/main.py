"""로깅 테스트를 위한 패키지 및 모듈 모음. 
테스트 모듈에 연결하여 통합 테스트를 하기 위한 용도. 

"""

import sys

from dirimporttool import get_super_dir_directly, get_current_absdir

super_dir = get_super_dir_directly(__file__, 3)
sys.path.append(super_dir)
c_dir = get_current_absdir(__file__)
sys.path.append(c_dir)

from logpackage import (PackageLogger, 
EasySetLogFileEnv, LogFuncEndPoint, DetectErrorAndLog, 
LogFileManager)

from pm import PlusMinus
from subdir.md import MultiDivide

main_pl = PackageLogger(EasySetLogFileEnv())

error_logger = main_pl.getErrorLogger(__file__)
program_start_end_logger = main_pl.getInfoLogger('program_start_end_logger')

@DetectErrorAndLog(error_logger, False)
@LogFuncEndPoint(program_start_end_logger)
def mainfunc(
        log_env_obj: EasySetLogFileEnv, 
        raise_error_log: bool = False,
        print_result: bool = True,
        log_file_manager: LogFileManager | None = None,
        limit_datedir_num: int = 3
    ):
    """
    Parameters
    ---------
    raise_error_log : bool, default False
        에러를 일으켜 에러 로그를 기록하게 할지 결정하는 매개변수.
        True 시 에러를 일으키며, 그에 관한 에러 로그를 기록하게 함.
        False 시 에러를 일으키지 않게 하여 이에 관한 에러 로그 기록되지 않게 함.
    print_result : bool, default True
        이 함수의 결과를 콘솔에 출력하도록 할 것인지 결정하는 매개변수.
    
    """
    global main_pl
    main_pl.setLogEnvObj(log_env_obj)

    pm_numset = 5, 10
    md_numset = 4, 12
    expected_error_num_set = 1, 0

    pm_obj = PlusMinus(pm_numset[0], pm_numset[1])
    md_obj = MultiDivide(md_numset[0], md_numset[1])
    expected_error_obj = MultiDivide(
        expected_error_num_set[0], expected_error_num_set[1]
    )

    pm_result = (pm_obj.getSumResult(2), pm_obj.getSubtractResult(1))
    md_result = (md_obj.getMultipliedResult(3), md_obj.getDividedResult(4))

    if raise_error_log:
        exp_err_result = (expected_error_obj.getMultipliedResult(1),
                        expected_error_obj.getDividedResult(2))
        print(exp_err_result)

    if print_result:
        print(pm_result)
        print(md_result)

    main_pl.logAllLoggersTree()

    if log_file_manager:
        log_file_manager.rotateDateDirs(limit_datedir_num)

if __name__ == '__main__':
    pass
    