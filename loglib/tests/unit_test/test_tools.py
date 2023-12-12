import unittest
import sys
import re
import datetime

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
        data = '2023-11-31' # 해당 달에는 31일이 없다.
        self.assertEqual(self.datetool.isDateStr(data), self.dateop.DAY)
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


if __name__ == '__main__':
    unittest.main()
    