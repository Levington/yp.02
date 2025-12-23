import sys
import os
from datetime import datetime, timedelta
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from booking_system import BookingSystem, BookingStatus
from date_validator import DateValidator, ConflictChecker
from analyzer import PerformanceAnalyzer, BookingAnalytics, ReportGenerator


def demonstrate_booking_system():
    print("=" * 80)
    print("ДЕМОНСТРАЦИЯ СИСТЕМЫ БРОНИРОВАНИЯ")
    print("=" * 80)
    
    system = BookingSystem()
    analyzer = PerformanceAnalyzer()
    
    print("\n1. Создание бронирований...")
    print("-" * 80)
    
    test_bookings = [
        {
            "resource": "Конференц-зал А",
            "start": datetime(2025, 1, 10, 9, 0),
            "end": datetime(2025, 1, 10, 17, 0),
            "customer": "ООО Компания 1"
        },
        {
            "resource": "Конференц-зал А",
            "start": datetime(2025, 1, 11, 9, 0),
            "end": datetime(2025, 1, 11, 17, 0),
            "customer": "ООО Компания 2"
        },
        {
            "resource": "Переговорная комната Б",
            "start": datetime(2025, 1, 10, 10, 0),
            "end": datetime(2025, 1, 10, 12, 0),
            "customer": "Иванов И.И."
        },
        {
            "resource": "Переговорная комната Б",
            "start": datetime(2025, 1, 10, 14, 0),
            "end": datetime(2025, 1, 10, 16, 0),
            "customer": "Петров П.П."
        },
        {
            "resource": "Оборудование 1",
            "start": datetime(2025, 1, 15, 8, 0),
            "end": datetime(2025, 1, 20, 18, 0),
            "customer": "Проект X"
        }
    ]
    
    for booking_data in test_bookings:
        start_time = time.time()
        
        booking = system.create_booking(
            resource_name=booking_data["resource"],
            start_date=booking_data["start"],
            end_date=booking_data["end"],
            customer_name=booking_data["customer"],
            notes=f"Тестовое бронирование для {booking_data['customer']}"
        )
        
        duration = time.time() - start_time
        analyzer.record_operation("create_booking", duration)
        
        if booking:
            print(f"✓ Создано: {booking}")
            system.confirm_booking(booking.id)
        else:
            print(f"✗ Конфликт: {booking_data['resource']} "
                  f"({booking_data['start']} - {booking_data['end']})")
    
    print("\n2. Тестирование конфликтов...")
    print("-" * 80)
    
    conflict_attempts = [
        {
            "resource": "Конференц-зал А",
            "start": datetime(2025, 1, 10, 15, 0),  
            "end": datetime(2025, 1, 10, 18, 0),
            "customer": "Конфликтующий клиент"
        },
        {
            "resource": "Переговорная комната Б",
            "start": datetime(2025, 1, 10, 11, 0),
            "end": datetime(2025, 1, 10, 13, 0),
            "customer": "Конфликтующий клиент 2"
        }
    ]
    
    for booking_data in conflict_attempts:
        start_time = time.time()
        
        booking = system.create_booking(
            resource_name=booking_data["resource"],
            start_date=booking_data["start"],
            end_date=booking_data["end"],
            customer_name=booking_data["customer"]
        )
        
        duration = time.time() - start_time
        analyzer.record_operation("create_booking_conflict", duration)
        
        if booking:
            print(f"✓ Создано: {booking}")
        else:
            print(f"✗ ОЖИДАЕМЫЙ КОНФЛИКТ: {booking_data['resource']} "
                  f"({booking_data['start'].strftime('%H:%M')} - "
                  f"{booking_data['end'].strftime('%H:%M')})")
    
    print("\n3. Отмена бронирования...")
    print("-" * 80)
    
    booking_to_cancel = system.get_all_bookings()[0]
    if system.cancel_booking(booking_to_cancel.id):
        print(f"✓ Бронирование #{booking_to_cancel.id} отменено")
    
    print("\n4. Статистика системы")
    print("-" * 80)
    
    stats = system.get_statistics()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")
    
    print("\n5. Анализ бронирований")
    print("-" * 80)
    
    analytics = BookingAnalytics.analyze_booking_patterns(system.get_all_bookings())
    
    print(f"\nОбщие показатели:")
    print(f"  - Всего бронирований: {analytics['total_bookings']}")
    print(f"  - Уникальных ресурсов: {analytics['unique_resources']}")
    print(f"  - Уникальных клиентов: {analytics['unique_customers']}")
    
    if analytics.get('most_popular_resource'):
        print(f"\nСамый популярный ресурс:")
        print(f"  - {analytics['most_popular_resource']['name']}: "
              f"{analytics['most_popular_resource']['count']} бронирований")
    
    print(f"\nПродолжительность:")
    print(f"  - Средняя: {analytics['average_duration_days']} дней")
    print(f"  - Минимальная: {analytics['min_duration_days']} дней")
    print(f"  - Максимальная: {analytics['max_duration_days']} дней")
    
    print("\n6. Анализ конфликтов")
    print("-" * 80)
    
    conflict_analysis = BookingAnalytics.analyze_conflicts(system.get_all_bookings())
    print(f"Обнаружено потенциальных конфликтов: {conflict_analysis['total_conflicts']}")
    
    print("\n7. Производительность")
    print("-" * 80)
    
    perf_summary = analyzer.get_performance_summary()
    for operation, metrics in perf_summary.items():
        print(f"\n{operation}:")
        print(f"  - Выполнено: {metrics['count']}")
        print(f"  - Среднее время: {metrics['average']*1000:.4f} мс")
        print(f"  - Мин/Макс: {metrics['min']*1000:.4f} / {metrics['max']*1000:.4f} мс")
    
    print("\n8. Генерация отчета...")
    print("-" * 80)
    
    report = ReportGenerator.generate_markdown_report(
        system_stats=stats,
        analytics=analytics,
        performance=perf_summary
    )
    
    os.makedirs("reports", exist_ok=True)
    
    report_path = os.path.join("reports", "analysis_report.md")
    ReportGenerator.save_report(report, report_path)
    
    print(f"✓ Отчет сохранен: {report_path}")
    
    print("\n9. Демонстрация валидатора дат")
    print("-" * 80)
    
    existing_bookings = [
        (b.start_date, b.end_date) 
        for b in system.get_bookings_by_resource("Конференц-зал А")
        if b.is_active()
    ]
    
    if existing_bookings:
        search_start = datetime(2025, 1, 10)
        search_end = datetime(2025, 1, 15)
        required_duration = timedelta(hours=8)
        
        available_slots = ConflictChecker.find_available_slots(
            existing_bookings,
            search_start,
            search_end,
            required_duration
        )
        
        print(f"\nДоступные слоты для 'Конференц-зал А' "
              f"({search_start.date()} - {search_end.date()}):")
        
        if available_slots:
            for i, (slot_start, slot_end) in enumerate(available_slots, 1):
                print(f"  {i}. {slot_start} - {slot_end}")
        else:
            print("  Нет доступных слотов")
    
    print("\n" + "=" * 80)
    print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 80)
    
    return system, analyzer


def main():
    print("=" * 80)
    print("СИСТЕМА БРОНИРОВАНИЯ")
    print("=" * 80)
    print("\nВыберите режим запуска:")
    print("1. Консольная демонстрация (автоматический прогон)")
    print("2. GUI приложение (графический интерфейс)")
    print("3. Выход")
    print()
    
    choice = input("Ваш выбор (1-3): ").strip()
    
    if choice == "1":
        try:
            system, analyzer = demonstrate_booking_system()
            
            print("\n📊 Для просмотра полного отчета откройте: reports/analysis_report.md")
            print("🧪 Для запуска тестов выполните: pytest tests/ -v")
            print("🖥️  Для запуска GUI выполните: python main_gui.py")
            
            return 0
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    elif choice == "2":
        print("\n🚀 Запуск GUI приложения...")
        try:
            import subprocess
            subprocess.run([sys.executable, "main_gui.py"])
            return 0
        except Exception as e:
            print(f"\n❌ Ошибка запуска GUI: {e}")
            print("💡 Попробуйте запустить напрямую: python main_gui.py")
            return 1
    
    elif choice == "3":
        print("\n👋 До свидания!")
        return 0
    
    else:
        print("\n❌ Неверный выбор!")
        return 1


if __name__ == "__main__":
    exit(main())
