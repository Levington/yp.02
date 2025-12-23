import pytest
from datetime import datetime, timedelta
import sys
import os


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from booking_system import Booking, BookingSystem, BookingStatus


class TestBooking:

    def test_create_valid_booking(self):

        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 5)
        booking = Booking(
            id=1,
            resource_name="Конференц-зал А",
            start_date=start,
            end_date=end,
            customer_name="Иван Иванов"
        )
        
        assert booking.id == 1
        assert booking.resource_name == "Конференц-зал А"
        assert booking.customer_name == "Иван Иванов"
        assert booking.status == BookingStatus.PENDING
    
    def test_booking_invalid_dates(self):

        start = datetime(2025, 1, 5)
        end = datetime(2025, 1, 1)
        
        with pytest.raises(ValueError, match="Дата начала должна быть раньше даты окончания"):
            Booking(
                id=1,
                resource_name="Ресурс",
                start_date=start,
                end_date=end,
                customer_name="Клиент"
            )
    
    def test_booking_empty_resource(self):

        with pytest.raises(ValueError, match="Название ресурса не может быть пустым"):
            Booking(
                id=1,
                resource_name="",
                start_date=datetime(2025, 1, 1),
                end_date=datetime(2025, 1, 5),
                customer_name="Клиент"
            )
    
    def test_booking_empty_customer(self):
        with pytest.raises(ValueError, match="Имя клиента не может быть пустым"):
            Booking(
                id=1,
                resource_name="Ресурс",
                start_date=datetime(2025, 1, 1),
                end_date=datetime(2025, 1, 5),
                customer_name=""
            )
    
    def test_duration_calculation(self):
        booking = Booking(
            id=1,
            resource_name="Ресурс",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 10),
            customer_name="Клиент"
        )
        
        assert booking.duration_days() == 9
    
    def test_is_active(self):
        booking = Booking(
            id=1,
            resource_name="Ресурс",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 5),
            customer_name="Клиент"
        )
        
        assert booking.is_active() is True
        
        booking.status = BookingStatus.CANCELLED
        assert booking.is_active() is False
    
    def test_overlaps_with_same_resource(self):
        booking1 = Booking(
            id=1,
            resource_name="Ресурс А",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 10),
            customer_name="Клиент 1"
        )
        
        booking2 = Booking(
            id=2,
            resource_name="Ресурс А",
            start_date=datetime(2025, 1, 5),
            end_date=datetime(2025, 1, 15),
            customer_name="Клиент 2"
        )
        
        assert booking1.overlaps_with(booking2) is True
    
    def test_overlaps_with_different_resource(self):
        booking1 = Booking(
            id=1,
            resource_name="Ресурс А",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 10),
            customer_name="Клиент 1"
        )
        
        booking2 = Booking(
            id=2,
            resource_name="Ресурс Б",
            start_date=datetime(2025, 1, 5),
            end_date=datetime(2025, 1, 15),
            customer_name="Клиент 2"
        )
        
        assert booking1.overlaps_with(booking2) is False
    
    def test_no_overlap_sequential(self):
        booking1 = Booking(
            id=1,
            resource_name="Ресурс А",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 10),
            customer_name="Клиент 1"
        )
        
        booking2 = Booking(
            id=2,
            resource_name="Ресурс А",
            start_date=datetime(2025, 1, 10),
            end_date=datetime(2025, 1, 15),
            customer_name="Клиент 2"
        )
        
        assert booking1.overlaps_with(booking2) is False


class TestBookingSystem:
    
    @pytest.fixture
    def system(self):
        return BookingSystem()
    
    def test_create_booking_success(self, system):
        booking = system.create_booking(
            resource_name="Зал А",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 5),
            customer_name="Клиент"
        )
        
        assert booking is not None
        assert booking.id == 1
        assert len(system.get_all_bookings()) == 1
    
    def test_create_booking_with_conflict(self, system):
        system.create_booking(
            resource_name="Зал А",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 10),
            customer_name="Клиент 1"
        )
        
        booking2 = system.create_booking(
            resource_name="Зал А",
            start_date=datetime(2025, 1, 5),
            end_date=datetime(2025, 1, 15),
            customer_name="Клиент 2"
        )
        
        assert booking2 is None
        assert len(system.get_all_bookings()) == 1
    
    def test_cancel_booking(self, system):
        booking = system.create_booking(
            resource_name="Зал А",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 5),
            customer_name="Клиент"
        )
        
        assert system.cancel_booking(booking.id) is True
        assert booking.status == BookingStatus.CANCELLED
    
    def test_confirm_booking(self, system):
        booking = system.create_booking(
            resource_name="Зал А",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 5),
            customer_name="Клиент"
        )
        
        assert system.confirm_booking(booking.id) is True
        assert booking.status == BookingStatus.CONFIRMED
    
    def test_get_active_bookings(self, system):
        booking1 = system.create_booking(
            resource_name="Зал А",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 5),
            customer_name="Клиент 1"
        )
        
        booking2 = system.create_booking(
            resource_name="Зал Б",
            start_date=datetime(2025, 2, 1),
            end_date=datetime(2025, 2, 5),
            customer_name="Клиент 2"
        )
        
        system.cancel_booking(booking1.id)
        
        active = system.get_active_bookings()
        assert len(active) == 1
        assert active[0].id == booking2.id
    
    def test_get_bookings_by_resource(self, system):
        system.create_booking(
            resource_name="Зал А",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 5),
            customer_name="Клиент 1"
        )
        
        system.create_booking(
            resource_name="Зал Б",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 5),
            customer_name="Клиент 2"
        )
        
        system.create_booking(
            resource_name="Зал А",
            start_date=datetime(2025, 2, 1),
            end_date=datetime(2025, 2, 5),
            customer_name="Клиент 3"
        )
        
        bookings_a = system.get_bookings_by_resource("Зал А")
        assert len(bookings_a) == 2
    
    def test_statistics(self, system):
        system.create_booking(
            resource_name="Зал А",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 5),
            customer_name="Клиент 1"
        )
        
        system.create_booking(
            resource_name="Зал А",
            start_date=datetime(2025, 1, 3),
            end_date=datetime(2025, 1, 7),
            customer_name="Клиент 2"
        )
        
        stats = system.get_statistics()
        
        assert stats['total_bookings'] == 1
        assert stats['total_attempts'] == 2
        assert stats['conflict_count'] == 1
        assert stats['conflict_rate'] == 50.0
