import unittest
import sys
import re
import datetime
import calendar
import os
import random
import time
from operator import itemgetter

from dirimporttool import get_super_dir_directly

super_dir = get_super_dir_directly(__file__, 2)
sys.path.append(super_dir)

from tools import (DateOptions, DateTools)


class TestDateTools(unittest.TestCase):
    def setUp(self):
        self.dateop = DateOptions()
        self.datetool = DateTools()

    def tearDown(self):
        self.datetool.delimiter = '-'

    def testGetTodaysDateStr(self):
        self.datetool.delimiter = '.'
        today_str = self.datetool.getTodaysDateStr()
        re_search = re.search('[0-9]{4}.[0-9]{2}.[0-9]{2}', today_str)

        # 해당 조건을 원문에서 발견하였는가?
        # 그렇지 않은 경우, None이 반환되며,
        # 다음 코드에서 테스트가 실패할 것이다.
        self.assertIsInstance(re_search, re.Match)
        
        self.assertIn('.', re_search.group())

    def testCombineDateToGetDateStr(self):
        year = 2013
        month = 11
        day = 21
        result = self.datetool.combineDateToGetDateStr(year, month, day)
        self.assertEqual(result, '2013-11-21')

    def testGetLastDayOfLastMonth(self):
        def test_date(year: int, month: int, day: int, expected):
            target_date = datetime.date(year, month, day)
            last_day_of_last_month = \
                self.datetool._getLastDayOfLastMonth(target_date)
            last_day_of_last_month = str(last_day_of_last_month)
            self.assertEqual(last_day_of_last_month, expected)
        
        test_date(2023, 11, 21, '2023-10-31')
        test_date(2023, 12, 5, '2023-11-30')
        test_date(2024, 3, 12, '2024-02-29')

    def testGetWeekOfDayInMonth(self):
        def test_date(year: int, month: int, day: int, expected):
            target_date = datetime.date(year, month, day)
            n_week = self.datetool.getWeekOfDayInMonth(target_date)
            self.assertEqual(n_week, expected)

        test_date(2023, 11, 2, 1)
        test_date(2023, 11, 21, 4)
        test_date(2023, 12, 2, -5)
        test_date(2023, 12, 11, 2)

    def testGetDateStr(self):
        def get_date_str(t_date: datetime.date, option: DateOptions):
            return self.datetool.getDateStr(
                format_option=option, year=t_date.year,
                month=t_date.month, day=t_date.day
            )
        
        target_date = datetime.date(2023, 11, 21)
        day_result = get_date_str(target_date, self.dateop.DAY)
        self.assertEqual(day_result, '2023-11-21')
        week_result = get_date_str(target_date, self.dateop.WEEK)
        self.assertEqual(week_result, '2023-11-04주')
        month_result = get_date_str(target_date, self.dateop.MONTH)
        self.assertEqual(month_result, '2023-11')
        year_result = get_date_str(target_date, self.dateop.YEAR)
        self.assertEqual(year_result, '2023')

    def testIsDateStr(self):
        data = ''
        self.assertEqual(self.datetool.isDateStr(data), None)

        # test year
        data = '2023'
        self.assertEqual(self.datetool.isDateStr(data), self.dateop.YEAR)
        data = '0023'
        self.assertEqual(self.datetool.isDateStr(data), self.dateop.YEAR)
        data = '10000'
        self.assertEqual(self.datetool.isDateStr(data), None)
        data = '-1'
        self.assertEqual(self.datetool.isDateStr(data), None)

        # test month
        data = '2023-12'
        self.assertEqual(self.datetool.isDateStr(data), self.dateop.MONTH)
        data = '0023-01'
        self.assertEqual(self.datetool.isDateStr(data), self.dateop.MONTH)
        data = '2032-1'
        self.assertEqual(self.datetool.isDateStr(data), self.dateop.MONTH)
        data = '-2023-12'
        self.assertEqual(self.datetool.isDateStr(data), None)
        data = '2023-12-'
        self.assertEqual(self.datetool.isDateStr(data), None)
        data = '2023-13'
        self.assertEqual(self.datetool.isDateStr(data), None)
        data = '2023-00'
        self.assertEqual(self.datetool.isDateStr(data), None)
        data = '2023_12'
        self.assertEqual(self.datetool.isDateStr(data), None)

        # test day
        data = '2023-12-12'
        self.assertEqual(self.datetool.isDateStr(data), self.dateop.DAY)
        data = '0023-01-01'
        self.assertEqual(self.datetool.isDateStr(data), self.dateop.DAY)
        data = '2023-01-1'
        self.assertEqual(self.datetool.isDateStr(data), self.dateop.DAY)
        data = '2023-12-31'
        self.assertEqual(self.datetool.isDateStr(data), self.dateop.DAY)
        data = '2023-11-31' # 해당 달에는 31일이 없다.
        self.assertEqual(self.datetool.isDateStr(data), None)
        data = '2023-11-35'
        self.assertEqual(self.datetool.isDateStr(data), None)
        data = '2023-12-00'
        self.assertEqual(self.datetool.isDateStr(data), None)
        data = '2023-12-32'
        self.assertEqual(self.datetool.isDateStr(data), None)
        data = '-2023-12-12'
        self.assertEqual(self.datetool.isDateStr(data), None)
        data = '2023-12-12-'
        self.assertEqual(self.datetool.isDateStr(data), None)
        data = '2023_12_12'
        self.assertEqual(self.datetool.isDateStr(data), None)

        # test week
        data = '2023-12-02주'
        self.assertEqual(self.datetool.isDateStr(data), self.dateop.WEEK)
        data = '2023-12-2주'
        self.assertEqual(self.datetool.isDateStr(data), self.dateop.WEEK)
        data = '0001-01-03주'
        self.assertEqual(self.datetool.isDateStr(data), self.dateop.WEEK)
        data = '1-1-3주'
        self.assertEqual(self.datetool.isDateStr(data), self.dateop.WEEK)
        data = '2023-12-05주' # 해당 달에 5주는 없다.
        self.assertEqual(self.datetool.isDateStr(data), self.dateop.WEEK)
        data = '-2023-12-04주'
        self.assertEqual(self.datetool.isDateStr(data), None)
        data = '2023-12-04주-'
        self.assertEqual(self.datetool.isDateStr(data), None)
        data = '2023-12-주'
        self.assertEqual(self.datetool.isDateStr(data), None)
        data = '2023-12-00주'
        self.assertEqual(self.datetool.isDateStr(data), None)
        data = '2023_12_01주'
        self.assertEqual(self.datetool.isDateStr(data), None)

    def testGetDateFromWeek(self):
        # test 1
        data = '2023-11-1주' # 해당 월의 1일이 수요일 -> 1일부터 1주차
        result = self.datetool.getDateFromWeek(data)
        self.assertEqual(result, '2023-11-01')
        result = self.datetool.getDateFromWeek(data, calendar.TUESDAY)
        self.assertEqual(result, '2023-11-01')
        result = self.datetool.getDateFromWeek(data, calendar.WEDNESDAY)
        self.assertEqual(result, '2023-11-01')
        result = self.datetool.getDateFromWeek(data, calendar.FRIDAY)
        self.assertEqual(result, '2023-11-03')

        # test 2
        def do_test(
                week_range: list[int],
                ex_re_range: list[int],
                year_month: str
            ):
            s, e = week_range
            datas = [f'{year_month}{n}주' for n in range(s, e+1)]
            weekdays = [i for i in range(0, 6+1)]
            ex_re = []
            s, e = ex_re_range
            for i in range(s, e+1):
                date_str = year_month
                if i < 10:
                    date_str += '0'
                date_str += str(i)
                ex_re.append(date_str)

            def test_iterably():
                i = 0
                for j, week_date in enumerate(datas):
                    for k, wd in enumerate(weekdays):
                        if i >= len(ex_re): break
                        result = self.datetool.getDateFromWeek(week_date, wd)
                        self.assertEqual(
                            result, 
                            ex_re[i], 
                            f'{i} {j} {k}'
                        )
                        i += 1
            
            test_iterably()

        do_test([2, 5], [6, 30], '2023-11-')

        # test 3
        # 2023-12-01~03은 2023-11-5주차에 해당
        data = '2023-11-5주'
        result = self.datetool.getDateFromWeek(data, calendar.FRIDAY)
        self.assertEqual(result, '2023-12-01')
        result = self.datetool.getDateFromWeek(data, calendar.SATURDAY)
        self.assertEqual(result, '2023-12-02')
        result = self.datetool.getDateFromWeek(data, calendar.SUNDAY)
        self.assertEqual(result, '2023-12-03')

        # test 4
        # 2023-12-01일은 금요일, 즉 11월의 5주차이다. 
        # 해당 달의 1주차는 2023-12-04(월) 부터이다.
        do_test([1, 4], [4, 31], '2023-12-')

        # test 5
        data = '2023-12-5주'
        result = self.datetool.getDateFromWeek(data)
        self.assertEqual(result, '2024-01-01')
        data = '2023-12-6주'
        result = self.datetool.getDateFromWeek(data)
        self.assertEqual(result, None) # 1 <= N주 <= 5

        # test 6
        # 날짜 형식 테스트.
        data = '2023-12-05주'
        result = self.datetool.getDateFromWeek(data)
        self.assertEqual(result, '2024-01-01')

        # test 7
        # datetime.date 객체 반환 테스트.
        data = '2023-12-5주'
        result = self.datetool.getDateFromWeek(data, to_str=False)
        self.assertIsInstance(result, datetime.date)
        self.assertEqual(result.isoformat(), '2024-01-01')

    def testConvertStrToDate(self):
        # test day
        data = '2023-12-04'
        result = self.datetool.convertStrToDate(data)
        self.assertIsInstance(result, datetime.date)
        self.assertEqual(result.isoformat(), '2023-12-04')

        # test week
        data = '2023-12-1주'
        result = self.datetool.convertStrToDate(data)
        self.assertIsInstance(result, datetime.date)
        self.assertEqual(result.isoformat(), '2023-12-04')

        data = '2023-12-5주'
        result = self.datetool.convertStrToDate(data)
        self.assertIsInstance(result, datetime.date)
        self.assertEqual(result.isoformat(), '2024-01-01')

        # test month
        data = '2023-12'
        result = self.datetool.convertStrToDate(data)
        self.assertIsInstance(result, datetime.date)
        self.assertEqual(result.isoformat(), '2023-12-01')

        # test year
        data = '2023'
        result = self.datetool.convertStrToDate(data)
        self.assertIsInstance(result, datetime.date)
        self.assertEqual(result.isoformat(), '2023-01-01')

        # test None
        datas = [
            '2023-1-45', '2023-1-', '2023-12-6주', 
            '강동6주', '202312', '2023-13', '-1111',
        ]
        for d in datas:
            result = self.datetool.convertStrToDate(d)
            self.assertEqual(result, None)

    def testConvertStrIntoDatetime(self):
        # test 1
        data = '2023-12-23-13:24:11'
        result = self.datetool.convertStrToDatetime(data)
        self.assertIsInstance(result, datetime.datetime)
        self.assertEqual(result.year, 2023)
        self.assertEqual(result.month, 12)
        self.assertEqual(result.day, 23)
        self.assertEqual(result.hour, 13)
        self.assertEqual(result.minute, 24)
        self.assertEqual(result.second, 11)

        # test 2
        data = '0001-01-01-00:00:00'
        result = self.datetool.convertStrToDatetime(data)
        self.assertIsInstance(result, datetime.datetime)

        # test 3
        data = '2023-12-23-11:30:00'
        result = self.datetool.convertStrToDatetime(data)
        self.assertIsInstance(result, datetime.datetime)

        # test 4
        data = '2023-12-23-25:61:00'
        with self.assertRaises(ValueError):
            result = self.datetool.convertStrToDatetime(data)


# ==== TestSearchDateDir() 테스트 클래스에 쓰일 함수들
def make_datedirs(root_dir: str, datedirs: list[str]):
    """테스트를 위한 날짜 디렉토리 생성 함수.
    root_dir로 입력되는 루트 디렉토리 경로는 실제로 존재해야 함.
    datedirs는 날짜 디렉토리의 이름으로 설정할 날짜 형식 문자열들의 
    리스트.

    """
    for d in datedirs:
        try:
            fullpath = os.path.join(root_dir, d)
            os.mkdir(fullpath)
        except FileExistsError:
            pass

def process_real_data(
        test_results: list[tuple[int, datetime.date, str]]
    ) -> (list[tuple[int, str, str]]):
    work_done = []
    for tup in test_results:
        tup = (tup[0], tup[1].isoformat(), tup[2])
        work_done.append(tup)
    return work_done

def process_exp_res(
        data: list[tuple[str, str]],
        rootdir: str,
        datetype: DateOptions.DateType
    ) -> (list[tuple[int, str, str]]):
    """
    data : list[tuple[datetime.date.isoformat(), real_data_str]]
    ex) data = [
        ('2023-12-01', '2023-12-1'), ...
    ]
    """
    work_done = []
    for exre, datedir in data:
        fullpath = os.path.join(rootdir, datedir)
        tup = (datetype, exre, fullpath)
        work_done.append(tup)
    return work_done
# ===================


class TestSearchDateDir(unittest.TestCase):
    """tools.DateTools.searchDateDir() 메서드 테스트"""
    datedir_made: bool = False

    def setUp(self):
        self.maxDiff = None

        self.datetool = DateTools()
        self.d_opt = DateOptions()

        self.day_root_dir = '..\\testdata\\datedirs\\days'
        self.week_root_dir = '..\\testdata\\datedirs\\weeks'
        self.month_root_dir = '..\\testdata\\datedirs\\months'
        self.year_root_dir = '..\\testdata\\datedirs\\years'

        self.day_dates = [
            '010-5-10', '010-1234-5678', '2023-11-31', 
            '2023-12-', '2023-12-1', '2023-12-04', 
            '2023-12-21', '2023-12-21-', '2023-12-31',
            '2024-1-1', '2024-12-21', '2024-01-01'
        ]
        self.week_dates = [
            '2023-12-01주', '2023-12-1주', '-2023-12-1주',
            '강동6주', '강동-6주', '2023-12-6주', 
            '1-1-3주', '001-1-2주', '2023-8-주',
            '2024-1-3주-', '2023-5-0주', '2023-11-5주',
            '2023-11-1주', '2023-10-05주',
        ]
        self.month_dates = [
            '2023-12', '0023-01', '2032-1', '-2023-12',
            '2023-12-', '2023-13', '2023-00', '2032-01',
            '1-1',
        ]
        self.year_dates = [
            '2023', '2022', '2024', '10000', '-1', '0023', 
            '23', str(datetime.MINYEAR - 1), 
            str(datetime.MAXYEAR + 1), '-2024', '20-23',
            '02021',
        ]
        dates = [
            self.day_dates, self.week_dates, 
            self.month_dates, self.year_dates
        ]
        for d in dates:
            random.shuffle(d)

        if not TestSearchDateDir.datedir_made:
            make_datedirs(self.day_root_dir, self.day_dates)
            make_datedirs(self.week_root_dir, self.week_dates)
            make_datedirs(self.month_root_dir, self.month_dates)
            make_datedirs(self.year_root_dir, self.year_dates)
            TestSearchDateDir.datedir_made = True

    def testDay(self):
        results = process_real_data(
            self.datetool.searchDateDir(self.day_root_dir)
        )
        expected_data = [
            ('0010-05-10', '010-5-10'),
            ('2023-12-01', '2023-12-1'),
            ('2023-12-04', '2023-12-04'),
            ('2023-12-21', '2023-12-21'),
            ('2023-12-31', '2023-12-31'),
            ('2024-01-01', '2024-01-01'),
            ('2024-01-01', '2024-1-1'),
            ('2024-12-21', '2024-12-21'),
        ]
        expected_results = process_exp_res(
            expected_data, self.day_root_dir, self.d_opt.DAY
        )
        self.assertEqual(results, expected_results)

    def testWeek(self):
        results = process_real_data(
            self.datetool.searchDateDir(self.week_root_dir)
        )
        expected_data = [
            ('0001-01-08', '001-1-2주'),
            ('0001-01-15', '1-1-3주'),
            ('2023-10-30', '2023-10-05주'),
            ('2023-11-01', '2023-11-1주'),
            ('2023-11-27', '2023-11-5주'),
            ('2023-12-04', '2023-12-01주'),
            ('2023-12-04', '2023-12-1주'),
        ]
        expected_results = process_exp_res(
            expected_data, self.week_root_dir, self.d_opt.WEEK
        )
        self.assertEqual(len(results), len(expected_results))
        self.assertEqual(results, expected_results)

    def testMonth(self):
        results = process_real_data(
            self.datetool.searchDateDir(self.month_root_dir)
        )
        expected_data = [
            ('0001-01-01', '1-1'),
            ('0023-01-01', '0023-01'),
            ('2023-12-01', '2023-12'),
            ('2032-01-01', '2032-01'),
            ('2032-01-01', '2032-1'),
        ]
        expected_results = process_exp_res(
            expected_data, self.month_root_dir, self.d_opt.MONTH
        )
        self.assertEqual(len(results), len(expected_results))
        self.assertEqual(results, expected_results)

    def testYear(self):
        results = process_real_data(
            self.datetool.searchDateDir(self.year_root_dir)
        )
        expected_data = [
            ('0023-01-01', '0023'),
            ('0023-01-01', '23'),
            ('2021-01-01', '02021'),
            ('2022-01-01', '2022'),
            ('2023-01-01', '2023'),
            ('2024-01-01', '2024'),
        ]
        expected_results = process_exp_res(
            expected_data, self.year_root_dir, self.d_opt.YEAR
        )
        self.assertEqual(len(results), len(expected_results))
        self.assertEqual(results, expected_results)


# TestSearchDateDirBirth 클래스에서의 테스트를 위한 함수들
def make_datedirs_with_delay(
        root_dir: str, 
        sleep_date: list[tuple[int, str]],
        allow_print: bool = True
    ):
    """디렉토리 생성 시 디렉토리 생성 시각도 테스트 요소이기에 
    time.sleep() 함수를 이용하여 일부러 생성 시간을 딜레이 시키도록 함.

    Parameters
    ----------
    root_dir : str
        날짜 디렉토리들을 생성할 루트 디렉토리의 경로
    sleep_date : list[tuple[sec, date_dirname]]
        날짜 디렉토리 생성 지연 시간과 해당 날짜 디렉토리명을 묶은 데이터.
    
    """
    if allow_print:
        print("테스트를 위한 디렉토리 생성 중... 시간이 다소 걸립니다.")
        print("생성된 디렉토리 목록.")
    
    count_makedir = 0  # 날짜 디렉토리 생성 개수.
    for t, datedir in sleep_date:
        fullpath = os.path.join(root_dir, datedir)
        if os.path.isdir(fullpath):
            continue # 이미 존재하는 디렉토리를 재생성하지 않도록 한다.
        time.sleep(t)
        os.mkdir(fullpath)
        print(fullpath)
        count_makedir += 1
    
    if allow_print:
        print(f"생성 완료. 총 {count_makedir}개 생성됨.")
        print("이미 존재하는 디렉토리는 새로 생성되지 않습니다.")

def process_data_no_datetime(data):
    """searchDateDir(), searchDateDirBirth() 메서드 결과를 가공하는 함수.
    가운데 date(), datetime() 객체 요소는 제거, 맨 마지막의 경로 요소는 디렉토리명만 
    남도록 가공.

    Parameters
    ---------
    data : DateTools().searchDateDir() | DateTools().searchDateDirBirth()

    Returns
    -------
    list[tuple[DateOptions().DateType, date_str]]

    """
    new_result = []
    for tup in data:
        tup = (tup[0], os.path.basename(tup[-1]))
        new_result.append(tup)
    return new_result

# =================

class TestSearchDateDirBirth(unittest.TestCase):
    """DateTools.searchDateDirBirth() 메서드 테스트 클래스."""
    access_tried: bool = False
    has_real_dirs: bool = False

    made_testdirs: bool = False

    def setUp(self):
        self.datetool = DateTools()
        self.dopt = DateOptions()

        # 실제 생성 시각이 하루 이상 차이나는 디렉토리 대상 테스트를 위한 설정.
        self.logfile_basedir = r'..\testdata\testpkg\logfiles_day'

        if not TestSearchDateDirBirth.access_tried:
            # self.logfile_basedir로 지정된 경로가 실제로 존재하고 그 안에 
            # 실제 날짜 디렉토리들이 존재할 경우에만 특정 테스트를 실행하도록 세팅함.
            if os.path.isdir(self.logfile_basedir):
                TestSearchDateDirBirth.has_real_dirs = True
            TestSearchDateDirBirth.access_tried = True
        # ========

        # 테스트를 위해 임의로 날짜 디렉토리들을 형성하기 위한 초기 설정.
        self.datedirs_rootdir = r'..\testdata\datedirbirth'
        self.testdatas = [
            (0, '2023-12-24'),
            (1, '2023-12-25'),
            (3, '2023-12-32'),
            (2, '2024-01-01'),
            (1, '2024-01-2'),
            (2, '2123-02-03'),
            (1, '2024-01-5주'),
            (3, '2024-2'),
            (2, '2025'),
            (1, '2022-01-01'),
        ]
        if not TestSearchDateDirBirth.made_testdirs:
            make_datedirs_with_delay(
                self.datedirs_rootdir, self.testdatas, False
            )
            TestSearchDateDirBirth.made_testdirs = True

    def testWithRealDirs(self):
        """실제 생성 일시에 적어도 하루 이상 차이나는 날짜 디렉토리들에 
        대한 테스트. 
        지정된 경로가 없을 경우 이 테스트는 스킵됨.
        """
        if not TestSearchDateDirBirth.has_real_dirs:
            self.skipTest('테스트를 위한 루트 디렉토리가 실존하지 않아 스킵됨.')
        
        # 결과가 정말로 디렉토리 생성 시각순으로 정렬되어 있는가에 대한 테스트.
        results = self.datetool.searchDateDirBirth(self.logfile_basedir)
        ex_re = results.copy()
        ex_re.sort(key=itemgetter(1))
        self.assertEqual(results, ex_re)

        # 디렉토리명으로 쓰인 날짜 문자열의 날짜와 실제 생성 일자가 같은지 확인.
        for tup in results:
            self.assertEqual(
                tup[1].date().isoformat(), 
                os.path.basename(tup[2])
            )

    def testDirBirth(self):
        """디렉토리 생성 시각별로 데이터들이 정렬되는지 확인하는 테스트."""
        results = self.datetool.searchDateDirBirth(self.datedirs_rootdir)
        processed_result = process_data_no_datetime(results)

        # test 1
        # list[tuple[DateOptions.DateType, basename(datedirpath)]]
        ex_re = [
            (self.dopt.DAY, '2023-12-24'),
            (self.dopt.DAY, '2023-12-25'), 
            (self.dopt.DAY, '2024-01-01'),
            (self.dopt.DAY, '2024-01-2'),
            (self.dopt.DAY, '2123-02-03'),
            (self.dopt.WEEK, '2024-01-5주'),
            (self.dopt.MONTH, '2024-2'),
            (self.dopt.YEAR, '2025'),
            (self.dopt.DAY, '2022-01-01'),
        ]
        for i, data in enumerate(results):
            dtype, dtime, p = data
            pbase = os.path.basename(p)
            self.assertEqual(dtype, ex_re[i][0])
            self.assertEqual(pbase, ex_re[i][1])
        self.assertEqual(processed_result, ex_re)

        # test 2
        # 실제 디렉토리의 생성 시각과 디렉토리명인 날짜 문자열의 날짜가 
        # 서로 불일치할 경우, 해당 메서드가 실제 생성 시각순으로 정렬하는지
        # 확인하기 위한 테스트. 
        datedirname_sorted = self.datetool.searchDateDir(self.datedirs_rootdir)
        processed_result = process_data_no_datetime(datedirname_sorted)
        self.assertEqual(len(ex_re), len(processed_result))
        self.assertNotEqual(ex_re, processed_result)


if __name__ == '__main__':
    unittest.main()
    