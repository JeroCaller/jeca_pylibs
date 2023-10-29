"""
로깅 테스트를 위한 패키지 및 모듈 모음. 
"""
import sys
from dirimporttool import get_super_dir_directly
super_dir = get_super_dir_directly(__file__, 3)
sys.path.append(super_dir)

from logpackage import PackageLogger, DetectErrorAndLog, LogFuncEndPoint
from logpackage import ALLFILES
from pm import PlusMinus
from subdir.md import MultiDivide

pl = PackageLogger(__file__)
pl.resetLogFile(ALLFILES)
error_logger = pl.getErrorLogger(__file__)
program_start_end_logger = pl.getInfoLogger('program_start_end')

@DetectErrorAndLog(error_logger)
@LogFuncEndPoint(program_start_end_logger)
def main():
    pm_numset = 5, 10
    md_numset = 4, 12
    expected_error_num_set = 1, 0

    pm_obj = PlusMinus(pm_numset[0], pm_numset[1])
    md_obj = MultiDivide(md_numset[0], md_numset[1])
    expected_error_obj = MultiDivide(expected_error_num_set[0], expected_error_num_set[1])

    pm_result = (pm_obj.getSumResult(2), pm_obj.getSubtractResult(1))
    md_result = (md_obj.getMultipliedResult(3), md_obj.getDividedResult(4))

    # 에러 로깅을 원치 않는다면 아래 코드 두 줄을 주석 처리. 
    #exp_err_result = (expected_error_obj.getMultipliedResult(1), expected_error_obj.getDividedResult(2))
    #print(exp_err_result)

    print(pm_result)
    print(md_result)


if __name__ == '__main__':
    main()
    """
    try:
        main()
    except Exception as e:
        error_logger.exception(e)
    """
    pl.logAllLoggersTree()
    