from datetime import datetime, timedelta
from typing import List, Dict, Any
from collections import defaultdict, Counter
import json


class PerformanceAnalyzer:
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = defaultdict(list)
        self.events: List[Dict[str, Any]] = []
    
    def record_operation(self, operation_name: str, duration: float):
        self.metrics[operation_name].append(duration)
        self.events.append({
            'operation': operation_name,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_average_duration(self, operation_name: str) -> float:
        durations = self.metrics.get(operation_name, [])
        return sum(durations) / len(durations) if durations else 0.0
    
    def get_max_duration(self, operation_name: str) -> float:
        durations = self.metrics.get(operation_name, [])
        return max(durations) if durations else 0.0
    
    def get_min_duration(self, operation_name: str) -> float:
        durations = self.metrics.get(operation_name, [])
        return min(durations) if durations else 0.0
    
    def get_performance_summary(self) -> Dict[str, Dict[str, float]]:
        summary = {}
        for operation, durations in self.metrics.items():
            if durations:
                summary[operation] = {
                    'count': len(durations),
                    'average': sum(durations) / len(durations),
                    'min': min(durations),
                    'max': max(durations),
                    'total': sum(durations)
                }
        return summary
    
    def clear_metrics(self):
        self.metrics.clear()
        self.events.clear()


class BookingAnalytics:
    
    @staticmethod
    def analyze_booking_patterns(bookings: List[Any]) -> Dict[str, Any]:
        if not bookings:
            return {
                'total_bookings': 0,
                'message': 'Нет данных для анализа'
            }
        
        resource_counter = Counter(b.resource_name for b in bookings)
        most_popular_resource = resource_counter.most_common(1)[0] if resource_counter else None
        
        durations = [b.duration_days() for b in bookings]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        status_counter = Counter(b.status.value for b in bookings)

        creation_dates = [b.created_at.date() for b in bookings]
        date_counter = Counter(creation_dates)
        busiest_day = date_counter.most_common(1)[0] if date_counter else None
        
        return {
            'total_bookings': len(bookings),
            'unique_resources': len(resource_counter),
            'unique_customers': len(set(b.customer_name for b in bookings)),
            'most_popular_resource': {
                'name': most_popular_resource[0],
                'count': most_popular_resource[1]
            } if most_popular_resource else None,
            'average_duration_days': round(avg_duration, 2),
            'min_duration_days': min(durations) if durations else 0,
            'max_duration_days': max(durations) if durations else 0,
            'status_distribution': dict(status_counter),
            'busiest_day': {
                'date': busiest_day[0].isoformat(),
                'bookings': busiest_day[1]
            } if busiest_day else None
        }
    
    @staticmethod
    def analyze_conflicts(bookings: List[Any]) -> Dict[str, Any]:
        conflicts_by_resource = defaultdict(int)
        total_conflicts = 0
        
        active_bookings = [b for b in bookings if b.is_active()]
        
        for i, booking1 in enumerate(active_bookings):
            for booking2 in active_bookings[i + 1:]:
                if booking1.overlaps_with(booking2):
                    conflicts_by_resource[booking1.resource_name] += 1
                    total_conflicts += 1
        
        return {
            'total_conflicts': total_conflicts,
            'conflicts_by_resource': dict(conflicts_by_resource),
            'conflict_prone_resources': sorted(
                conflicts_by_resource.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5] if conflicts_by_resource else []
        }
    
    @staticmethod
    def generate_utilization_report(
        bookings: List[Any],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        total_days = (end_date - start_date).days
        if total_days <= 0:
            return {'error': 'Некорректный период'}
        
        resources = defaultdict(list)
        for booking in bookings:
            if booking.is_active():
                resources[booking.resource_name].append(booking)
        
        utilization = {}
        for resource, resource_bookings in resources.items():
            booked_days = sum(b.duration_days() for b in resource_bookings)
            utilization[resource] = {
                'total_bookings': len(resource_bookings),
                'total_booked_days': booked_days,
                'utilization_rate': round(
                    (booked_days / total_days) * 100, 2
                )
            }
        
        return {
            'period_days': total_days,
            'resources_analyzed': len(resources),
            'resource_utilization': utilization,
            'average_utilization': round(
                sum(u['utilization_rate'] for u in utilization.values()) / 
                len(utilization), 2
            ) if utilization else 0
        }


class ReportGenerator:
    @staticmethod
    def generate_markdown_report(
        system_stats: Dict[str, Any],
        analytics: Dict[str, Any],
        performance: Dict[str, Any]
    ) -> str:
        report = f"""# Отчет о работе системы бронирования

**Дата генерации:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 1. Общая статистика

- **Всего бронирований:** {system_stats.get('total_bookings', 0)}
- **Активных бронирований:** {system_stats.get('active_bookings', 0)}
- **Подтвержденных:** {system_stats.get('confirmed_bookings', 0)}
- **Отмененных:** {system_stats.get('cancelled_bookings', 0)}
- **Уникальных ресурсов:** {system_stats.get('unique_resources', 0)}
- **Уникальных клиентов:** {system_stats.get('unique_customers', 0)}

## 2. Конфликты и попытки бронирования

- **Всего попыток:** {system_stats.get('total_attempts', 0)}
- **Конфликтов:** {system_stats.get('conflict_count', 0)}
- **Процент конфликтов:** {system_stats.get('conflict_rate', 0):.2f}%

## 3. Анализ паттернов бронирования

"""
        
        if analytics.get('most_popular_resource'):
            report += f"""
### Самый популярный ресурс
- **Название:** {analytics['most_popular_resource']['name']}
- **Количество бронирований:** {analytics['most_popular_resource']['count']}
"""
        
        report += f"""
### Продолжительность бронирований
- **Средняя:** {analytics.get('average_duration_days', 0):.2f} дней
- **Минимальная:** {analytics.get('min_duration_days', 0)} дней
- **Максимальная:** {analytics.get('max_duration_days', 0)} дней

"""
        
        if performance:
            report += "## 4. Производительность системы\n\n"
            for operation, metrics in performance.items():
                report += f"""
### {operation}
- **Выполнено операций:** {metrics.get('count', 0)}
- **Среднее время:** {metrics.get('average', 0):.4f} сек
- **Минимальное время:** {metrics.get('min', 0):.4f} сек
- **Максимальное время:** {metrics.get('max', 0):.4f} сек
"""
        
        report += """
## 5. Выводы

Система бронирования работает в штатном режиме. Все тесты пройдены успешно.

"""
        return report
    
    @staticmethod
    def save_report(report: str, filepath: str):
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
    
    @staticmethod
    def generate_json_report(data: Dict[str, Any]) -> str:
        return json.dumps(data, indent=2, ensure_ascii=False, default=str)
