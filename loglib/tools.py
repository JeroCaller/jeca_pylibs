import datetime
import calendar
from typing import Literal, TypeAlias


class DateOptions():
    DAY = 'day'
    WEEK = 'week'
    MONTH = 'month'
    YEAR = 'year'
    FREE = 'free'

    DateType: TypeAlias = Literal['day', 'week', 'month', 'year']


class DateTools():
    """logpackage.py 모듈 내에서만 사용하는 클래스.
    날짜 문자열을 다루는 툴 성격의 클래스이다.
    """
    def __init__(self):
        self.d_opt = DateOptions()

        # 하나의 날짜 데이터에서 연, 월, 일을 구분하는 기호.
        self.delimiter = "-"

    def getTodaysDateStr(self) -> (str):
        """오늘 날짜를 연-월-일 형태의 문자열로 반환.
        예) '2023-11-20'

        Returns
        -------
        str
            '2023-11-20'과 같이 'YYYY-MM-DD' 형태로 오늘 
            날짜를 문자열로 반환.
        
        """
        today = datetime.date.today()
        today = today.isoformat()
        if self.delimiter not in today:
            today = today.replace('-', self.delimiter)
        return today
    
    def combineDateToGetDateStr(self, *args: int):
        """특정 날짜의 연, 월, 일 등의 숫자들을 원하는 만큼만 입력하면 
        '연-월-일-...' 형태의 문자열로 반환. 

        Parameters
        ----------
        *args : int
            문자열로 나타내고자 하는 날짜의 일부 정보만큼만 숫자로 입력. 
            예1) (2023, 11) -> '2023-11'
            예2) (2023, 11, 20) -> '2023-11-20'
        
        Returns
        -------
        str
            입력받은 날짜 숫자 정보들을 토대로 문자열로 반환.
        
        """
        data = [str(a) for a in args]
        return self.delimiter.join(data)
    
    def _getLastDayOfLastMonth(
            self,
            current_date: datetime.date
        ) -> (datetime.date):
        """주어진 날짜의 지난 달의 마지막 일의 날짜를 datetime.date 객체로 반환."""
        last_day_this_month = calendar.monthrange(
            current_date.year, current_date.month
        )[1]
        before_a_month = current_date \
            - datetime.timedelta(days=last_day_this_month)
        before_a_month_last_day = calendar.monthrange(
            before_a_month.year, before_a_month.month
        )[1]
        before_a_month = datetime.date(
            before_a_month.year, before_a_month.month, before_a_month_last_day
        )
        return before_a_month
    
    def getDateStr(
            self, 
            format_option: DateOptions.DateType,
            is_today: bool = False,
            year: int = 1,
            month: int = 1,
            day: int = 1,
        ) -> (str):
        """특정 날짜의 연, 월, 일을 각각 숫자로 입력하면 이를 토대로 
        특정 포맷의 날짜 문자열로 반환.

        Parameters
        ----------
        format_option : DateOptions.DateType
            DAY, WEEK, MONTH, YEAR 상수 중 하나를 기입. 
            각 상수에 따른 반환값 형태는 Returns 항목 참조.
        is_today : bool, default False
            오늘 날짜를 입력하고자 하는 경우 True를 선택. 
            True 대입 시 매개변수 year, month, day에 대입된 값을 모두 
            무시한다.
        year : int, default 1
        month : int, default 1
        day : int, default 1
        
        Returns
        ------
        str
            문자열 형태의 날짜 문자열. 
            format_option 매개변수 지정에 따른 포맷 타입)
            DAY : 'YYYY-MM-DD' 형태의 날짜 문자열로 변환하고자 할 때.
            WEEK : 'YYYY-MM-N주' 형태의 날짜 문자열로 변환하고자 할 때.
            MONTH : 'YYYY-MM' 형태의 날짜 문자열로 변환하고자 할 때.
            YEAR : 'YYYY' 형태의 날짜 문자열로 변환하고자 할 때.
        
        """
        the_day = datetime.date(year, month, day)
        if is_today:
            the_day = datetime.date.today()
        
        if format_option == self.d_opt.WEEK:
            n_week = self.getWeekOfDayInMonth(the_day)
            if n_week < 0:
                before_month = self._getLastDayOfLastMonth(the_day)
                return self.combineDateToGetDateStr(
                    before_month.year, before_month.month, -n_week
                ) + '주'
            return self.combineDateToGetDateStr(
                the_day.year, the_day.month, n_week
            ) + '주'
        if format_option == self.d_opt.DAY:
            return self.combineDateToGetDateStr(
                the_day.year, the_day.month, the_day.day
            )
        if format_option == self.d_opt.MONTH:
            return self.combineDateToGetDateStr(
                the_day.year, the_day.month
            )
        if format_option == self.d_opt.YEAR:
            return self.combineDateToGetDateStr(
                the_day.year
            )
    
    def getWeekOfDayInMonth(self, the_day: datetime.date):
        """특정 날짜가 주어졌을 때, 그 날이 해당 달에서 몇 쨰주인지를 
        반환하는 메서드.
        예) 2023-11-1 -> 1 (2023-11월의 첫 째주)

        Parameters
        ----------
        the_day : datetime.date
            파이썬 내장 라이브러리 datetime의 date 객체.
        
        Returns
        ------
        int
            사용자가 입력한 특정 일이 해당 달의 몇 째주인지를 int형으로 반환.
            만약 특정 일이 포함된 달의 1일이 금, 토, 일 중 하나이고, 특정 일이
            그 주에 포함되어 있다면, 해당 일은 지난 달의 마지막 주로 계산되며, 
            이 경우 반환값 앞에 마이너스(-) 부호가 붙는다. 
            예) 2023-12-2 (토) -> -5 (2023-11월 5째 주)

        Notes
        -----
        특정 날이 해당 달의 몇 째주인지를 계산하는 기준은 ISO-8601 기준을 따랐다. 
        해당 기준은 다음을 정의한다.
        1. 매 주의 시작일은 월요일이다.
        2. 매 월의 첫 주는 과반수(즉, 4일 이상)가 포함된 주를 첫 주로 삼는다. 
        
        위의 2번 정의에 따르면, 만약 이번 달의 1일이 월, 화, 수, 목 중 하나라면 
        그 주를 차지하는 일 수가 적어도 4일 이상이기에 해당 주를 이번 달의 
        첫 주로 인정한다. 반면, 이번 달의 1일이 금, 토, 일 중에 하나라면 
        해당 주의 구성일은 4일보다 적기에 이 경우 저번 달의 마지막 주차로 인정하고, 
        그 다음 주를 이번 달의 1주차로 인정한다. 

        References
        .. [1] https://antennagom.com/844

        """
        first_day = datetime.date(the_day.year, the_day.month, 1)
        criterion = [
            calendar.MONDAY, calendar.TUESDAY, 
            calendar.WEDNESDAY, calendar.THURSDAY,
        ]
        n_week = 0
        monday_of_second_week = first_day.day + (7 - first_day.weekday())
        if first_day.weekday() in criterion:
            n_week = 1
            if the_day.day >= monday_of_second_week:
                n_week += (the_day.day - monday_of_second_week) // 7 + 1
        else:
            if the_day.day < monday_of_second_week:
                last_day_of_last_month = self._getLastDayOfLastMonth(the_day)
                before_month_weeks = self.getWeekOfDayInMonth(
                    last_day_of_last_month
                )
                n_week = - before_month_weeks
            else:
                n_week += (the_day.day - monday_of_second_week) // 7 + 1
        return n_week
