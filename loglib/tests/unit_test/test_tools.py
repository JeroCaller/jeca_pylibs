import unittest
import sys
import re
import datetime
import calendar
import os
import random

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


class TestSearchDateDir(unittest.TestCase):
    """tools.DateTools.searchDateDir() 메서드 테스트"""
    datedir_made: bool = False

    def setUp(self):
        self.datetool = DateTools()
        self.d_opt = DateOptions()

        self.day_root_dir = '..\\fixtures\\datedirs\\days'
        self.week_root_dir = '..\\fixtures\\datedirs\\weeks'
        self.month_root_dir = '..\\fixtures\\datedirs\\months'
        self.year_root_dir = '..\\fixtures\\datedirs\\years'

        self.day_dates = [
            '010-5-10', '010-1234-5678', '2023-11-31', 
            '2023-12-', '2023-12-1', '2023-12-04', 
            '2023-12-21', '2023-12-21-', '2023-12-31',
            '2024-1-1', '2024-12-21'
        ]
        self.week_dates = [...]
        self.month_dates = [...]
        self.year_dates = [...]
        dates = [
            self.day_dates, self.week_dates, 
            self.month_dates, self.year_dates
        ]
        for d in dates:
            random.shuffle(d)

        if not TestSearchDateDir.datedir_made:
            make_datedirs(self.day_root_dir, self.day_dates)
            ...
            TestSearchDateDir.datedir_made = True

    def testDay(self):
        results = self.datetool.searchDateDir(self.day_root_dir)
        for i, tup in enumerate(results):
            tup = (tup[0], tup[1].isoformat(), tup[2])
            results[i] = tup
        expected_results = [
            ('0010-05-10', os.path.join(self.day_root_dir, '010-5-10')),
            ('2023-12-01', os.path.join(self.day_root_dir, '2023-12-1')),
            ('2023-12-04', os.path.join(self.day_root_dir, '2023-12-04')),
            ('2023-12-21', os.path.join(self.day_root_dir, '2023-12-21')),
            ('2023-12-31', os.path.join(self.day_root_dir, '2023-12-31')),
            ('2024-01-01', os.path.join(self.day_root_dir, '2024-1-1')),
            ('2024-12-21', os.path.join(self.day_root_dir, '2024-12-21')),
        ]
        for i, tup in enumerate(expected_results):
            tup = (tup[0], os.path.abspath(tup[1]))
            tup = tuple([self.d_opt.DAY] + list(tup))
            expected_results[i] = tup
        self.assertEqual(results, expected_results)

if __name__ == '__main__':
    unittest.main()
    