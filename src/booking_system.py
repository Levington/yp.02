from datetime import datetime
from typing import List, Optional, Dict
from dataclasses import dataclass, field
from enum import Enum


class BookingStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


@dataclass
class Booking:
    id: int
    resource_name: str
    start_date: datetime
    end_date: datetime
    customer_name: str
    status: BookingStatus = BookingStatus.PENDING
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if self.start_date >= self.end_date:
            raise ValueError("Дата начала должна быть раньше даты окончания")
        if not self.resource_name:
            raise ValueError("Название ресурса не может быть пустым")
        if not self.customer_name:
            raise ValueError("Имя клиента не может быть пустым")
    
    def duration_days(self) -> int:
        return (self.end_date - self.start_date).days
    
    def is_active(self) -> bool:
        return self.status in [BookingStatus.PENDING, BookingStatus.CONFIRMED]
    
    def overlaps_with(self, other: 'Booking') -> bool:
        if self.resource_name != other.resource_name:
            return False
        
        return not (self.end_date <= other.start_date or 
                   self.start_date >= other.end_date)
    
    def __str__(self) -> str:
        return (f"Бронирование #{self.id}: {self.resource_name} "
                f"для {self.customer_name} "
                f"с {self.start_date.strftime('%Y-%m-%d')} "
                f"по {self.end_date.strftime('%Y-%m-%d')} "
                f"[{self.status.value}]")


class BookingSystem:
    def __init__(self):
        self._bookings: List[Booking] = []
        self._next_id: int = 1
        self._conflict_count: int = 0
        self._total_attempts: int = 0
    
    def create_booking(
        self,
        resource_name: str,
        start_date: datetime,
        end_date: datetime,
        customer_name: str,
        notes: str = ""
    ) -> Optional[Booking]:
        self._total_attempts += 1
        
        new_booking = Booking(
            id=self._next_id,
            resource_name=resource_name,
            start_date=start_date,
            end_date=end_date,
            customer_name=customer_name,
            notes=notes
        )
        
        conflicts = self.check_conflicts(new_booking)
        if conflicts:
            self._conflict_count += 1
            return None
        
        self._bookings.append(new_booking)
        self._next_id += 1
        return new_booking
    
    def check_conflicts(self, booking: Booking) -> List[Booking]:
        conflicts = []
        for existing in self._bookings:
            if existing.is_active() and existing.overlaps_with(booking):
                conflicts.append(existing)
        return conflicts
    
    def get_booking(self, booking_id: int) -> Optional[Booking]:
        for booking in self._bookings:
            if booking.id == booking_id:
                return booking
        return None
    
    def cancel_booking(self, booking_id: int) -> bool:
        booking = self.get_booking(booking_id)
        if booking and booking.is_active():
            booking.status = BookingStatus.CANCELLED
            return True
        return False
    
    def confirm_booking(self, booking_id: int) -> bool:
        booking = self.get_booking(booking_id)
        if booking and booking.status == BookingStatus.PENDING:
            booking.status = BookingStatus.CONFIRMED
            return True
        return False
    
    def get_all_bookings(self) -> List[Booking]:
        return self._bookings.copy()
    
    def get_active_bookings(self) -> List[Booking]:
        return [b for b in self._bookings if b.is_active()]
    
    def get_bookings_by_resource(self, resource_name: str) -> List[Booking]:
        return [b for b in self._bookings if b.resource_name == resource_name]
    
    def get_statistics(self) -> Dict[str, any]:
        active = self.get_active_bookings()
        
        stats = {
            'total_bookings': len(self._bookings),
            'active_bookings': len(active),
            'cancelled_bookings': len([b for b in self._bookings 
                                      if b.status == BookingStatus.CANCELLED]),
            'confirmed_bookings': len([b for b in self._bookings 
                                       if b.status == BookingStatus.CONFIRMED]),
            'total_attempts': self._total_attempts,
            'conflict_count': self._conflict_count,
            'conflict_rate': (self._conflict_count / self._total_attempts * 100 
                            if self._total_attempts > 0 else 0),
            'unique_resources': len(set(b.resource_name for b in self._bookings)),
            'unique_customers': len(set(b.customer_name for b in self._bookings))
        }
        
        return stats
    
    def clear_all(self):
        self._bookings.clear()
        self._next_id = 1
        self._conflict_count = 0
        self._total_attempts = 0
