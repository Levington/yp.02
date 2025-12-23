import pytest
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from booking_system import Booking, BookingSystem, BookingStatus
from date_validator import DateValidator, ConflictChecker


class TestEdgeCases:

    
    @pytest.fixture
    def system(self):

        return BookingSystem()
    
    def test_same_day_booking(self):

        start = datetime(2025, 1, 1, 9, 0)
        end = datetime(2025, 1, 1, 18, 0)
        
        booking = Booking(
            id=1,
            resource_name="Переговорная",
            start_date=start,
            end_date=end,
            customer_name="Клиент"
        )
        assert booking.duration_days() == 0
        assert booking.is_active()
    
    def test_one_minute_booking(self):
        start = datetime(2025, 1, 1, 12, 0)
        end = datetime(2025, 1, 1, 12, 1)
        
        booking = Booking(
            id=1,
            resource_name="Оборудование",
            start_date=start,
            end_date=end,
            customer_name="Клиент"
        )
        
        assert booking is not None
    
    def test_long_term_booking(self):
        start = datetime(2025, 1, 1)
        end = datetime(2026, 1, 1)
        
        booking = Booking(
            id=1,
            resource_name="Офис",
            start_date=start,
            end_date=end,
            customer_name="Компания"
        )
        
        assert booking.duration_days() == 365
    
    def test_exact_boundary_bookings(self, system):
        booking1 = system.create_booking(
            resource_name="Зал",
            start_date=datetime(2025, 1, 1, 9, 0),
            end_date=datetime(2025, 1, 1, 12, 0),
            customer_name="Клиент 1"
        )
        
        booking2 = system.create_booking(
            resource_name="Зал",
            start_date=datetime(2025, 1, 1, 12, 0),
            end_date=datetime(2025, 1, 1, 15, 0),
            customer_name="Клиент 2"
        )
        assert booking1 is not None
        assert booking2 is not None
        assert len(system.get_all_bookings()) == 2
    
    def test_one_second_overlap(self, system):
        booking1 = system.create_booking(
            resource_name="Зал",
            start_date=datetime(2025, 1, 1, 9, 0, 0),
            end_date=datetime(2025, 1, 1, 12, 0, 1),
            customer_name="Клиент 1"
        )
        
        booking2 = system.create_booking(
            resource_name="Зал",
            start_date=datetime(2025, 1, 1, 12, 0, 0),
            end_date=datetime(2025, 1, 1, 15, 0, 0),
            customer_name="Клиент 2"
        )
        
        assert booking1 is not None
        assert booking2 is None
    
    def test_multiple_simultaneous_bookings_different_resources(self, system):
        start = datetime(2025, 1, 1, 10, 0)
        end = datetime(2025, 1, 1, 14, 0)
        
        bookings = []
        for i in range(10):
            booking = system.create_booking(
                resource_name=f"Ресурс {i}",
                start_date=start,
                end_date=end,
                customer_name=f"Клиент {i}"
            )
            bookings.append(booking)
        
        assert all(b is not None for b in bookings)
        assert len(system.get_all_bookings()) == 10
    
    def test_midnight_crossing_booking(self):
        booking = Booking(
            id=1,
            resource_name="Офис",
            start_date=datetime(2025, 1, 1, 22, 0),
            end_date=datetime(2025, 1, 2, 2, 0),
            customer_name="Клиент"
        )
        
        assert booking.duration_days() == 0
    
    def test_year_boundary_booking(self):
        booking = Booking(
            id=1,
            resource_name="Зал",
            start_date=datetime(2025, 12, 31, 20, 0),
            end_date=datetime(2026, 1, 1, 4, 0),
            customer_name="Клиент"
        )
        
        assert booking is not None
    
    def test_leap_year_february_29(self):
        booking = Booking(
            id=1,
            resource_name="Зал",
            start_date=datetime(2024, 2, 29, 10, 0), 
            end_date=datetime(2024, 3, 1, 10, 0),
            customer_name="Клиент"
        )
        
        assert booking.duration_days() == 1
    
    def test_unicode_characters_in_names(self, system):
        booking = system.create_booking(
            resource_name="Конференц-зал «Москва» №1",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 2),
            customer_name="Иванов Иван Иванович 中文"
        )
        
        assert booking is not None
        assert "Москва" in booking.resource_name
    
    def test_very_long_names(self, system):
        long_name = "A" * 1000
        
        booking = system.create_booking(
            resource_name=long_name,
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 2),
            customer_name=long_name
        )
        
        assert booking is not None
        assert len(booking.resource_name) == 1000
    
    def test_special_characters_in_notes(self, system):
        special_notes = """
        <script>alert('test')</script>
        SELECT * FROM bookings;
        ../../../etc/passwd
        \x00\x01\x02
        """
        
        booking = system.create_booking(
            resource_name="Зал",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 2),
            customer_name="Клиент",
            notes=special_notes
        )
        
        assert booking is not None
        assert booking.notes == special_notes
    
    def test_massive_booking_load(self, system):
        start_date = datetime(2025, 1, 1)
        
        for i in range(1000):
            booking_start = start_date + timedelta(hours=i)
            booking_end = booking_start + timedelta(hours=1)
            
            system.create_booking(
                resource_name=f"Ресурс {i % 10}",
                start_date=booking_start,
                end_date=booking_end,
                customer_name=f"Клиент {i}"
            )
        
        stats = system.get_statistics()
        assert stats['total_attempts'] == 1000
        assert stats['total_bookings'] > 0
    
    def test_cancel_already_cancelled(self, system):
        booking = system.create_booking(
            resource_name="Зал",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 2),
            customer_name="Клиент"
        )
        
        assert system.cancel_booking(booking.id) is True
        assert system.cancel_booking(booking.id) is False  
    
    def test_confirm_cancelled_booking(self, system):
        booking = system.create_booking(
            resource_name="Зал",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 2),
            customer_name="Клиент"
        )
        
        system.cancel_booking(booking.id)
        assert system.confirm_booking(booking.id) is False
    
    def test_get_nonexistent_booking(self, system):
        booking = system.get_booking(99999)
        assert booking is None


class TestDateValidatorEdgeCases:
    
    def test_same_date_overlap(self):
        date = datetime(2025, 1, 1, 12, 0)
        
        assert not DateValidator.is_valid_date_range(date, date)
    
    def test_microsecond_difference(self):
        start = datetime(2025, 1, 1, 12, 0, 0, 0)
        end = datetime(2025, 1, 1, 12, 0, 0, 1)
        
        assert DateValidator.is_valid_date_range(start, end)
    
    def test_business_days_weekend_only(self):
        saturday = datetime(2025, 1, 4) 
        monday = datetime(2025, 1, 6)    
        
        business_days = DateValidator.get_business_days_count(saturday, monday)
        assert business_days == 0
    
    def test_date_range_single_day(self):
        start = datetime(2025, 1, 1, 0, 0)
        end = datetime(2025, 1, 1, 23, 59)
        
        dates = DateValidator.get_date_range_list(start, end)
        assert len(dates) == 0  

    def test_find_slots_no_bookings(self):

        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 10)
        duration = timedelta(days=2)
        
        slots = ConflictChecker.find_available_slots([], start, end, duration)
        
        assert len(slots) == 1
        assert slots[0] == (start, end)
    
    def test_find_slots_no_space(self):
        bookings = [
            (datetime(2025, 1, 1), datetime(2025, 1, 10))
        ]
        
        slots = ConflictChecker.find_available_slots(
            bookings,
            datetime(2025, 1, 1),
            datetime(2025, 1, 10),
            timedelta(days=1)
        )
        
        assert len(slots) == 0
    
    def test_find_slots_exact_fit(self):
        bookings = [
            (datetime(2025, 1, 1), datetime(2025, 1, 5)),
            (datetime(2025, 1, 10), datetime(2025, 1, 15))
        ]
        
        slots = ConflictChecker.find_available_slots(
            bookings,
            datetime(2025, 1, 1),
            datetime(2025, 1, 15),
            timedelta(days=5)
        )
        assert len(slots) == 1
        assert slots[0] == (datetime(2025, 1, 5), datetime(2025, 1, 10))
