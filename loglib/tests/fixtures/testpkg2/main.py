"""로깅 테스트를 위한 fixture 패키지.
logging.handlers.RotatingFileHandler()가 적용된 버전의 
로깅 테스트를 위함.

"""
import sys

from dirimporttool import (get_super_dir_directly,
get_current_absdir)

super_dir = get_super_dir_directly(__file__, 3)
c_dir = get_current_absdir(__file__)
sys.path.extend([super_dir, c_dir])

from logpackage import (PackageLogger, EasySetLogFileEnv,
LogFuncEndPoint, DetectErrorAndLog)

from pm import PlusMinus
from .subdir.md import MultiDivide

main_pl = PackageLogger()

error_logger = main_pl.getErrorLogger(__file__)
program_start_end_logger = main_pl.getInfoLogger('program_start_end_logger')

@DetectErrorAndLog(error_logger)
@LogFuncEndPoint(program_start_end_logger)
def mainfunc(
        log_env_obj: EasySetLogFileEnv,
        raise_error_log: bool = False,
        print_result: bool = True,
    ):
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
