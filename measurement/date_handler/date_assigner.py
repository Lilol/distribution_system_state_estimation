from datetime import timedelta

from pandas import DataFrame


class TimeIntervalUnit:
    def __init__(self, week, start_quarter_hour, length):
        self.week = week
        self.start_quarter_hour = start_quarter_hour
        self.length = length


class DateIntervalCalculator:
    def __init__(self, output_year):
        self.year = output_year

    def get_time_units(self, dates):
        modified_dates = dates + timedelta(days=4)
        return self.__create_time_intervals(modified_dates)

    @staticmethod
    def __create_time_intervals(dates):
        dates = DataFrame(index=dates)
        dates["week"] = dates.index.dayofyear // 7
        for week in dates.week.unique():
            dates_of_week = dates.index[dates.week == week]
            start_idx = DateIntervalCalculator.__time_to_index(dates_of_week[0])
            end_idx = DateIntervalCalculator.__time_to_index(dates_of_week[-1])
            yield TimeIntervalUnit(week, start_idx, end_idx - start_idx)

    @staticmethod
    def __time_to_index(dt):
        return (dt.day % 7) * 96 + dt.hour * 4 + dt.minute // 15
