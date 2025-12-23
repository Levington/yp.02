from datetime import datetime, timedelta
from typing import List, Tuple, Optional
from dateutil.relativedelta import relativedelta


class DateValidator:
    @staticmethod
    def is_valid_date_range(start_date: datetime, end_date: datetime) -> bool:
        if start_date >= end_date:
            return False
        return True
    
    @staticmethod
    def is_future_date(date: datetime) -> bool:
        return date > datetime.now()
    
    @staticmethod
    def is_past_date(date: datetime) -> bool:
        return date < datetime.now()
    
    @staticmethod
    def dates_overlap(
        start1: datetime,
        end1: datetime,
        start2: datetime,
        end2: datetime
    ) -> bool:
        return not (end1 <= start2 or start1 >= end2)
    
    @staticmethod
    def get_overlap_duration(
        start1: datetime,
        end1: datetime,
        start2: datetime,
        end2: datetime
    ) -> Optional[timedelta]:
        if not DateValidator.dates_overlap(start1, end1, start2, end2):
            return None
        
        overlap_start = max(start1, start2)
        overlap_end = min(end1, end2)
        return overlap_end - overlap_start
    
    @staticmethod
    def normalize_date(date: datetime) -> datetime:
        return date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    @staticmethod
    def is_same_day(date1: datetime, date2: datetime) -> bool:
        return (date1.year == date2.year and 
                date1.month == date2.month and 
                date1.day == date2.day)
    
    @staticmethod
    def get_date_range_list(start_date: datetime, end_date: datetime) -> List[datetime]:
        dates = []
        current = DateValidator.normalize_date(start_date)
        end = DateValidator.normalize_date(end_date)
        
        while current < end:
            dates.append(current)
            current += timedelta(days=1)
        
        return dates
    
    @staticmethod
    def is_weekend(date: datetime) -> bool:
        return date.weekday() >= 5
    
    @staticmethod
    def get_business_days_count(start_date: datetime, end_date: datetime) -> int:
        dates = DateValidator.get_date_range_list(start_date, end_date)
        return sum(1 for date in dates if not DateValidator.is_weekend(date))


class ConflictChecker:
    @staticmethod
    def check_date_conflicts(
        bookings: List[Tuple[datetime, datetime]],
        new_start: datetime,
        new_end: datetime
    ) -> List[int]:
        conflicts = []
        for idx, (start, end) in enumerate(bookings):
            if DateValidator.dates_overlap(start, end, new_start, new_end):
                conflicts.append(idx)
        return conflicts
    
    @staticmethod
    def find_available_slots(
        bookings: List[Tuple[datetime, datetime]],
        search_start: datetime,
        search_end: datetime,
        required_duration: timedelta
    ) -> List[Tuple[datetime, datetime]]:
        if not bookings:
            return [(search_start, search_end)]
        
        sorted_bookings = sorted(bookings, key=lambda x: x[0])
        available_slots = []
        
        first_start = sorted_bookings[0][0]
        if first_start - search_start >= required_duration:
            available_slots.append((search_start, first_start))
        
        for i in range(len(sorted_bookings) - 1):
            current_end = sorted_bookings[i][1]
            next_start = sorted_bookings[i + 1][0]
            
            if next_start - current_end >= required_duration:
                available_slots.append((current_end, next_start))
        
        last_end = sorted_bookings[-1][1]
        if search_end - last_end >= required_duration:
            available_slots.append((last_end, search_end))
        
        return available_slots
    
    @staticmethod
    def can_accommodate(
        bookings: List[Tuple[datetime, datetime]],
        new_start: datetime,
        new_end: datetime
    ) -> bool:
        return len(ConflictChecker.check_date_conflicts(
            bookings, new_start, new_end
        )) == 0
