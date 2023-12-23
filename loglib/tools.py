import datetime
import calendar
import os
import time
from typing import Literal, TypeAlias
from operator import itemgetter

try:
    from sub_modules.dirsearch import get_all_in_rootdir
except ModuleNotFoundError:
    from .sub_modules.dirsearch import get_all_in_rootdir


class DateOptions():
    """날짜 분류 관련 상수 정의 클래스. 
    해당 클래스에 정의된 상수들과 그에 대응되는 날짜 문자열 포맷 형식은 다음과 같다.

    DAY : 'YYYY-MM-DD'
    WEEK : 'YYYY-MM-N주'
    MONTH : 'YYYY-MM'
    YEAR : 'YYYY'
    FREE : (없음)

    """
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
        data = []
        for a in args:
            if 0 <= a <= 9:
                data.append('0' + str(a))
            else:
                data.append(str(a))
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
    
    def isDateStr(
            self, 
            target: str,
        ) -> (DateOptions.DateType | None):
        """주어진 문자열이 정해진 형태의 날짜 문자열인지 확인하는 메서드.

        정해진 형태의 날짜 문자열은 getDateStr() 메서드의 반환 가능한 
        문자열 형태를 따른다. 즉, DateOption 상수로 지정 가능한 날짜 
        형태들을 모두 검사한다. 
        DateOption 클래스 내 상수들)
        DAY: 'YYYY-MM-DD'
        WEEK: 'YYYY-MM-N주' (1 <= N <= 5)
        MONTH: 'YYYY-MM'
        YEAR: 'YYYY'

        Parameters
        ---------
        target : str
            날짜 문자열인지 검사할 문자열.

        Returns
        -------
        DateOption.DateType
            DAY: 'YYYY-MM-DD' 형태일 경우 반환.
            WEEK: 'YYYY-MM-N주' 형태일 경우 반환.
            MONTH: 'YYYY-MM' 형태일 경우 반환.
            YEAR: 'YYYY' 형태일 경우 반환.
        None
            정해진 날짜 형태 중 어느 것과도 만족되지 않을 경우.
            '2023-11-35'과 같이 형태는 날짜 형태이나 실질적으로 
            존재하지 않는 날짜여도 해당 문자열을 날짜 형태 문자열로 
            인식하지 않고 None을 반환함.

        Notes
        -----
        '2023-11-35'와 같이 날짜 형태는 만족하나 실질적으로는 존재하지 
        않는 날짜여도 해당 문자열을 날짜 형태 문자열로 인식하지 않는다. 
        정해진 날짜 형태를 만족하려면 다음의 조건들을 만족해야 한다.

        1. 일수의 경우 1 <= day <= 31을 만족해야 한다. 단, 특정 년, 월의 
        마지막 일수 이내의 범위여야 한다.
        2. 월의 경우 1 <= month <= 12을 만족해야 한다.
        3. 연도의 경우, datetime.MINYEAR <= year <= datetime.MAXYEAR을 
        만족해야 한다. 

        """
        def _is_in_range(data: str, min_value: int, max_value: int):
            try:
                return min_value <= int(data) <= max_value
            except ValueError:
                return False

        def is_year(data: str):
            return _is_in_range(data, datetime.MINYEAR, datetime.MAXYEAR)
        
        def is_month(data: str):
            return _is_in_range(data, 1, 12)
        
        def is_day(data: str, year: int = None, month: int = None):
            if year and month:
                end_day = calendar.monthrange(year, month)[1]
            else:
                end_day = 31
            return _is_in_range(data, 1, end_day)
        
        def is_week(data: str):
            if data.endswith('주'):
                return _is_in_range(data[:-1], 1, 5)
            return False
        
        target_split = target.split(self.delimiter)
        state = None
        year, month = 0, 0
        for i, data in enumerate(target_split):
            if i == 0:
                if is_year(data):
                    state = self.d_opt.YEAR
                    year = int(data)
                else:
                    return None
            elif i == 1:
                if is_month(data):
                    state = self.d_opt.MONTH
                    month = int(data)
                else:
                    return None
            elif i == 2:
                if is_week(data):
                    state = self.d_opt.WEEK
                elif is_day(data, year, month):
                    state = self.d_opt.DAY
                else:
                    state = None
            else:
                # len(target_split) >= 3 이상이면 
                # 정해진 날짜 형태 중 그 어느것도 만족하지 않는다.
                state = None
        return state
    
    def getDateFromWeek(
            self, 
            week_date: str, 
            weekday: int = calendar.MONDAY,
            to_str: bool = True
        ):
        """주어진 날짜 문자열이 'YYYY-MM-N주' 형태로 주어질 때, 
        해당 주의 날짜를 'YYYY-MM-DD'형태로 반환하는 메서드.

        week_date 매개변수로 주어지는 날짜 형태 문자열이 'YYYY-MM-N주' 
        형태인지 확인하기 위해 내부적으로 이 클래스의 isDateStr() 
        메서드를 사용함.

        Parameters
        ----------
        week_date : str
            변환하고자 하는 주 형태의 날짜 문자열.
        weekday : int
            해당 주의 어느 요일을 반환할 것인지에 대한 매개변수. 
            calendar 모듈의 MONDAY ~ SUNDAY 상수를 이용.
        to_str : bool, default True
            결과값을 'YYYY-MM-DD' 형태의 문자열로 반환할 것인지 
            datetime.date() 객체로 반환할 것인지 결정하는 매개변수. 
            True 시 문자열로, False 시 datetime.date() 객체를 반환.

        Returns
        -------
        datetime.date | str
            str -> 'YYYY-MM-DD'
            만약 첫 째 주에 weekday로 지정한 날이 없다면
            첫 째 주 첫 날인 1일로 기본으로 지정. 
            예) week_day = '2023-11-1주', weekday = calendar.TUESDAY
            => 2023-11-1주차인 2023-11-01은 수요일이다. 이 경우 해당 달의 해당 주차에 
            화요일은 없으므로 해당 달의 1일인 2023-11-01을 반환. 
            한 편, 특정 달의 마지막 주이고, weekday가 그 다음 달의 1일 이후 날짜에 해당된다면
            해당 날짜로 반환됨.
            예) 2023-11-5주, 금요일 = 2023-12-01
        None
            week_date 매개변수로 주어진 날짜가 'YYYY-MM-N주' 형태가 
            아닐 경우 반환.

        """
        if self.isDateStr(week_date) != self.d_opt.WEEK:
            return None
        
        year, month, week = week_date.split(self.delimiter)
        year, month, week = int(year), int(month), int(week[:-1])

        def return_what(day):
            if to_str:
                return self.combineDateToGetDateStr(year, month, day)
            return datetime.date(year, month, day)
    
        first_day = datetime.date(year, month, 1)
        criterion = [
            calendar.MONDAY, calendar.TUESDAY, 
            calendar.WEDNESDAY, calendar.THURSDAY,
        ]
        the_day = 0
        if first_day.weekday() in criterion:
            if week == 1:
                if weekday < first_day.weekday():
                    # 첫 째 주에 weekday로 지정한 날이 없다면
                    # 첫 째 주 첫 날인 1일로 기본으로 지정.
                    the_day = 1
                else:
                    the_day = 1 + weekday - first_day.weekday()
                return return_what(the_day)
            else:
                week -= 1
        # 달력 상에서 두 번째 행의 월요일에 해당하는 날
        the_day = first_day.day + (7 - first_day.weekday())
        the_day += 7 * (week-1) + weekday

        # 특정 달의 마지막 주이고, weekday가 그 다음 달의 1일 이후 날짜에 해당된다면
        # 그 날로 수정.
        # 예) 2023-11-5주, 금요일 -> 2023-12-01
        final_day = calendar.monthrange(year, month)[1]
        diff = the_day - final_day
        if diff > 0:
            next_date = datetime.date(year, month, final_day) \
                + datetime.timedelta(days=diff)
            year, month, the_day = next_date.year, next_date.month, next_date.day

        return return_what(the_day)
    
    def convertStrToDate(self, date_str: str) -> (datetime.date | None):
        """날짜 문자열을 입력받으면 이를 datetime.date 객체로 변환하여 
        반환하는 메서드. 

        날짜 문자열의 형태에 따라 반환되는 정확한 값이 다르다. 자세한 사항은 
        아래의 Returns 항목 참조.

        Parameters
        ----------
        date_str : str
            문자열 형태의 날짜 문자열. 이 메서드에서 해석 가능한 날짜 
            형태로 다음이 있다. 
            DAY : 'YYYY-MM-DD'
            WEEK : 'YYYY-MM-N주'
            MONTH : 'YYYY-MM'
            YEAR : 'YYYY'

        Returns
        ------
        datetime.date
            date_str 매개변수로 입력된 값의 날짜 형태마다 반환되는 정확한 값이 다르다.
            DAY ('YYYY-MM-DD'): datetime.date(YYYY, MM, DD) 날짜 그대로 반환.
            WEEK ('YYYY-MM-N주'): 해당 주의 첫 요일인 월요일에 해당하는 날짜를 반환.
                예) '2023-12-1주' -> datetime.date(2023, 12, 4)
            MONTH ('YYYY-MM'): 해당 월의 1일로 반환.
                예) '2023-12' -> datetime.date(2023, 12, 1)
            YEAR ('YYYY'): 해당 연도의 1월 1일로 반환.
                예) '2023' -> datetime.date(2023, 1, 1)
        None
            Parameters 부분의 date_str 매개변수 설명에 언급한 날짜 형태가 아닌 
            문자열이 date_str에 입력된 경우 반환됨.
        
        """
        datetype = self.isDateStr(date_str)
        if datetype is None: return None

        if datetype == self.d_opt.DAY:
            year, month, day = [int(d) for d in date_str.split(self.delimiter)]
            return datetime.date(year, month, day)
        if datetype == self.d_opt.WEEK:
            return self.getDateFromWeek(date_str, to_str=False)
        if datetype == self.d_opt.MONTH:
            year, month = [int(d) for d in date_str.split(self.delimiter)]
            return datetime.date(year, month, 1)
        if datetype == self.d_opt.YEAR:
            year = int(date_str)
            return datetime.date(year, 1, 1)
        
    def convertStrToDatetime(self, datetime_str: str):
        """'YYYY-MM-DD-HH:MM:SS' 형태의 시간 문자열을 
        datetime.datetime 객체로 변환하여 반환하는 메서드. 
        시간은 24시간제를 사용.

        Parameters
        ----------
        datetime_str : str

        Returns
        -------
        datetime.datetime
        None
            datetime_str 매개변수로 전달된 문자열이 지정된 시간 형태가 
            아닐 경우 반환되는 값.

        Raises
        ------
        ValueError
            날짜 및 시간 범위에 맞지 않을 경우 발생.
            예) 25시, 65분, -3초 등.
            날짜 및 시간 범위는 datetime.datetime 클래스에서 지정한 
            날짜 및 시간 범위에 따른다. 자세한 내용은 datetime의 공식문서 참조.
        
        """
        try:
            year, month, day, times = datetime_str.split('-')
            hour, minute, second = times.split(':')
        except ValueError:
            return None
        data_list = [year, month, day, hour, minute, second]
        data_list = [int(d) for d in data_list]

        # 날짜, 시간 범위에 맞지 않는 숫자 입력 시
        # datetime.datetime() 클래스 내에서 자체적으로 ValueError 발생.
        return datetime.datetime(*data_list)
    
    def searchDateDir(
            self, 
            root_dir: str
        ) -> (list[tuple[DateOptions.DateType, datetime.date, str]]):
        """루트 폴더 안에 날짜 문자열을 이름으로 갖는 모든 하위 디렉토리들의 
        경로와 그 문자열을 날짜 데이터로 변환하여 
        날짜순으로 정렬한 결과물을 반환하는 메서드.

        해당 루트 폴더 안에 보이는 디렉토리들만 검색하고 그 이상 더 하위에 
        있는 디렉토리들은 검색하지 않는다. 

        Parameters
        ----------
        root_dir : str
            날짜 형식의 문자열을 이름으로 갖는 하위 디렉토리들이 모여 있는 
            상위 디렉토리의 절대 경로.
        
        Returns
        -------
        list[tuple[DateOptions.DateType, datetime.date, str]]
            차례대로 DateOptions.DateType, datetime.date, 해당 날짜 문자열 디렉토리 경로로 이뤄진 
            튜플들의 리스트로 반환됨.
        None
            해당 루트 폴더를 찾지 못한 경우.
            
        """
        try:
            sub_entities = os.listdir(root_dir)
        except FileNotFoundError:
            return None
        
        datedirs = []
        for entity in sub_entities:
            date_type = self.isDateStr(entity)
            fullpath = os.path.join(root_dir, entity)
            if os.path.isdir(fullpath) and date_type:
                datedirs.append(
                    (
                        date_type,
                        self.convertStrToDate(entity),
                        fullpath
                    )
                )

        datedirs.sort(key=itemgetter(1))
        return datedirs
    
    def searchDateDirBirth(
            self,
            root_dir: str
        ) -> (list[tuple[DateOptions.DateType, datetime.datetime, str]]):
        """루트 폴더 내에 DateOptions 클래스 내 정의된 날짜 분류별 
        날짜 형식을 가지는 날짜 문자열을 이름으로 하는 모든 하위 디렉토리들을 
        검색하고 해당 디렉토리들의 최초 생성 시간별 오름차순 정렬하여 반환한다. 

        검색 시 루트 폴더에서 바로 보이는 하위 디렉토리들만 검색하고, 그 이상 
        더 하위에 있는 디렉토리들을 검색하진 않는다. 즉, 루트 폴더에서 한 단계 
        아래의 디렉토리들만 검색한다. 

        searchDateDir() 메서드는 검색된 날짜 디렉토리명을 추출하고 이를 해당 
        디렉토리의 생성 날짜로 간주하여 정렬 및 반환하는 반면, 
        이 메서드는 해당 디렉토리의 실제 최초 생성 시간 정보를 읽어와 이를 토대로 
        정렬한 결과를 반환하는 것이 차이점이다. 하지만 날짜 디렉토리명은 여전히 
        DateOptions 클래스에 정의된 날짜 분류 상수들의 날짜 포맷 형식을 만족해야만 
        이 메서드에서 검색된다. 

        Parameters
        ----------
        root_dir : str
            날짜 형식의 문자열을 이름으로 갖는 하위 디렉토리들이 모여 있는 
            상위 디렉토리의 절대 경로.

        Returns
        -------
        list[tuple[DateOptions.DateType, datetime.datetime, str]]
            차례대로 DateOptions.DateType, datetime.datetime, 
            해당 날짜명을 가지는 디렉토리의 경로로 이뤄진 튜플들의 리스트를 반환.

        """
        try:
            sub_entities = os.listdir(root_dir)
        except FileNotFoundError:
            return None
        
        datedirs = []
        for entity in sub_entities:
            date_type = self.isDateStr(entity)
            fullpath = os.path.join(root_dir, entity)
            if os.path.isdir(fullpath) and date_type:
                birthdatetime = time.localtime(os.path.getctime(fullpath))
                birthdatetime = time.strftime(
                    '%Y-%m-%d-%H:%M:%S', birthdatetime
                )
                birthdatetime = self.convertStrToDatetime(birthdatetime)
                datedirs.append(
                    (date_type, birthdatetime, fullpath)
                )

        datedirs.sort(key=itemgetter(1))
        return datedirs


if __name__ == '__main__':
    pass
