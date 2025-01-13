import calendar as _calendar
import datetime
import sys
import warnings
from calendar import SATURDAY, SUNDAY
from importlib.metadata import metadata
from itertools import pairwise
from typing import ClassVar, Final, Self, SupportsIndex, overload

_package_metadata = metadata(str(__package__))
__version__ = _package_metadata["Version"]
__author__ = _package_metadata.get("Author-email", "")

_1DAY = datetime.timedelta(days=1)
MIN_YEAR: Final[int] = 2000
MAX_YEAR: Final[int] = 2027
NUM_MONTH: Final[int] = 12


class DateWithName(datetime.date):
    """名前付きdate"""

    name: str

    def __new__(cls, year: int, month: int, day: int, name: str = ""):
        dt = super().__new__(cls, year, month, day)
        dt.name = name
        return dt

    def __repr__(self):
        return f"{self} ({self.name})"

    @overload
    def replace(self, year: SupportsIndex = ..., month: SupportsIndex = ..., day: SupportsIndex = ...) -> Self: ...

    @overload
    def replace(self, **kwargs) -> Self: ...

    def replace(self, **kwargs):
        year = kwargs.pop("year", self.year)
        month = kwargs.pop("month", self.month)
        day = kwargs.pop("day", self.day)
        name = kwargs.pop("name", self.name)
        if kwargs:
            k = next(iter(kwargs))
            msg = f"'{k}' is an invalid keyword argument for replace()"
            raise TypeError(msg)
        return DateWithName(year, month, day, name)


def _japanese_holidays(year: int) -> list[DateWithName]:
    """振替休日や国民の休日を含まない日本の祝日"""
    sp = int(20.8431 + 0.242194 * (year - 1980) - (int)((year - 1980) / 4))
    au = int(23.2488 + 0.242194 * (year - 1980) - (int)((year - 1980) / 4))
    sh = {
        (1, 1, "元日"),
        (1, -2, "成人の日"),
        (2, 11, "建国記念の日"),
        (2, 23, "天皇誕生日"),
        (3, sp, "春分の日"),
        (4, 29, "昭和の日"),
        (5, 3, "憲法記念日"),
        (5, 4, "みどりの日"),
        (5, 5, "こどもの日"),
        (7, -3, "海の日"),
        (8, 11, "山の日"),
        (9, -3, "敬老の日"),
        (9, au, "秋分の日"),
        (10, -2, "スポーツの日"),
        (11, 3, "文化の日"),
        (11, 23, "勤労感謝の日"),
    }
    # 海の日の調整
    if year <= 2002:  # noqa: PLR2004
        sh -= {(7, -3, "海の日"), (9, -3, "敬老の日")}
        sh |= {(7, 20, "海の日"), (9, 15, "敬老の日")}
    # みどりの日の調整
    if year <= 2006:  # noqa: PLR2004
        sh -= {(4, 29, "昭和の日"), (5, 4, "みどりの日")}
        sh.add((4, 29, "みどりの日"))
    # 山の日の調整
    if year <= 2015:  # noqa: PLR2004
        sh.remove((8, 11, "山の日"))
    if year <= 2019:  # noqa: PLR2004
        sh -= {(2, 23, "天皇誕生日"), (10, -2, "スポーツの日")}
        # 天皇誕生日の調整
        if year == 2019:  # noqa: PLR2004
            sh |= {(5, 1, "天皇の即位の日"), (10, 22, "即位礼正殿の儀が行われる日")}
        else:
            sh.add((12, 23, "天皇誕生日"))
        # スポーツの日の調整
        sh.add((10, -2, "体育の日"))
    # 東京オリンピックの調整
    if 2020 <= year <= 2021:  # noqa: PLR2004
        sh -= {(7, -3, "海の日"), (8, 11, "山の日"), (10, -2, "スポーツの日")}
        if year == 2020:  # noqa: PLR2004
            sh |= {(7, 23, "海の日"), (7, 24, "スポーツの日"), (8, 10, "山の日")}
        elif year == 2021:  # noqa: PLR2004
            sh |= {(7, 22, "海の日"), (7, 23, "スポーツの日"), (8, 8, "山の日")}
    jh = []
    for month, day, name in sh:
        dt = datetime.date(year, month, max(1, day))
        if day < 0:  # 第N月曜日の計算
            dt += ((7 - dt.weekday()) % 7 + 7 * (-1 - day)) * _1DAY
        jh.append(DateWithName(dt.year, dt.month, dt.day, name))
    return sorted(jh)


def holidays(year: int) -> set[DateWithName]:
    if not (MIN_YEAR <= year <= MAX_YEAR):
        warnings.warn(f"Not applicable for the year {year}.", DeprecationWarning, stacklevel=2)
    jh = _japanese_holidays(year)
    sh = set(jh)
    for dt in jh:
        if dt.weekday() == SUNDAY:
            dt_ = dt + _1DAY
            while dt_ in sh:  # 振替
                dt_ += _1DAY
            sh.add(dt_.replace(name="振替休日"))
    sorted_sh = sorted(sh)
    for d1, d2 in pairwise(sorted_sh):
        if (d2 - d1).days == 2 and d1.weekday() != SATURDAY:  # noqa: PLR2004
            sh.add((d1 + _1DAY).replace(name="国民の休日"))
    return sh


holidays.__doc__ = f"""日本の休日({MIN_YEAR}-{MAX_YEAR})"""


class ColorTextCalendar(_calendar.TextCalendar):
    _the_year: ClassVar[int] = -1
    _holiday: ClassVar[set[DateWithName]] = set()
    _themonth: ClassVar[int] = -1

    @staticmethod
    def _set_the_year(theyear):
        ColorTextCalendar._the_year = theyear
        ColorTextCalendar._holiday = holidays(theyear)

    @staticmethod
    def _day(day):
        cls = ColorTextCalendar
        return datetime.date(cls._the_year, cls._themonth, day)

    def formatday(self, day, weekday, width):  # noqa: PLR6301
        return (
            ""
            if day == 0
            else f"\x1b[1;31m{day:2}\x1b[0m"
            if weekday == SUNDAY or ColorTextCalendar._day(day) in ColorTextCalendar._holiday
            else f"\x1b[1;36m{day:2}\x1b[0m"
            if weekday == SATURDAY
            else f"{day:2}"
        ).center(width)

    def formatweekday(self, day, width):
        s = super().formatweekday(day, width)
        f1, f2 = "\x1b[1;31m%s\x1b[0m", "\x1b[1;36m%s\x1b[0m"
        return f1 % s if day == SUNDAY else f2 % s if day == SATURDAY else s

    def formatmonth(self, theyear, themonth, w=0, l=0):  # noqa: E741
        ColorTextCalendar._set_the_year(theyear)
        ColorTextCalendar._themonth = themonth
        return super().formatmonth(theyear, themonth, w, l)

    def formatyear(self, theyear, w=2, l=1, c=6, m=3):  # noqa: E741
        ColorTextCalendar._set_the_year(theyear)
        w = max(2, w)
        ln = max(1, l)
        c = max(2, c)
        col_width = (w + 1) * 7 - 1
        v = []
        a = v.append
        a(repr(theyear).center(col_width * m + c * (m - 1)).rstrip())
        a("\n" * ln)
        header = self.formatweekheader(w)
        for i, row in enumerate(self.yeardays2calendar(theyear, m)):
            # months in this row
            months = range(m * i + 1, min(m * (i + 1) + 1, 13))
            a("\n" * ln)
            names = (self.formatmonthname(theyear, k, col_width, withyear=False) for k in months)
            a(_calendar.formatstring(names, col_width, c).rstrip())  # type: ignore[reportArgumentType]
            a("\n" * ln)
            headers = (header for k in months)
            a(_calendar.formatstring(headers, col_width, c).rstrip())  # type: ignore[reportArgumentType]
            a("\n" * ln)
            # max number of weeks for this row
            height = max(len(cal) for cal in row)
            for j in range(height):
                weeks = []
                for k, cal in zip(months, row, strict=False):
                    if j >= len(cal):
                        weeks.append("")
                    else:
                        ColorTextCalendar._themonth = k
                        weeks.append(self.formatweek(cal[j], w))  # type: ignore[reportArgumentType]
                a(_calendar.formatstring(weeks, col_width, c).rstrip())  # type: ignore[reportArgumentType]
                a("\n" * ln)
        return "".join(v)


def main():
    _c = ColorTextCalendar()  # noqa: RUF052
    prmonth = _c.prmonth
    prcal = _c.pryear
    theyear = int(sys.argv[1]) if len(sys.argv) > 1 else datetime.datetime.today().year
    month = int(sys.argv[2]) if len(sys.argv) > 2 else None  # noqa: PLR2004
    if 1 <= theyear <= NUM_MONTH:
        month = theyear
        theyear = datetime.datetime.today().year
    if month:
        prmonth(theyear, month)
    else:
        prcal(theyear)
