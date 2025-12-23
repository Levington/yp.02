import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime, timedelta
from tkcalendar import DateEntry
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from booking_system import BookingSystem, BookingStatus
from date_validator import DateValidator, ConflictChecker
from analyzer import PerformanceAnalyzer, BookingAnalytics, ReportGenerator


class BookingSystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Система бронирования")
        self.root.geometry("1000x700")
        
        self.booking_system = BookingSystem()
        self.analyzer = PerformanceAnalyzer()
        
        self.setup_ui()
        
        self.load_demo_data()
        
    def setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.create_booking_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.create_booking_tab, text="Создать бронирование")
        self.setup_create_booking_tab()
        
        self.bookings_list_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.bookings_list_tab, text="Список бронирований")
        self.setup_bookings_list_tab()
        
        self.statistics_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.statistics_tab, text="Статистика и аналитика")
        self.setup_statistics_tab()
        

        self.reports_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_tab, text="Отчеты")
        self.setup_reports_tab()
        
    def setup_create_booking_tab(self):
        frame = ttk.LabelFrame(self.create_booking_tab, text="Новое бронирование", padding=20)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(frame, text="Ресурс:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.resource_var = tk.StringVar()
        self.resource_combo = ttk.Combobox(frame, textvariable=self.resource_var, width=40)
        self.resource_combo['values'] = (
            'Конференц-зал А',
            'Конференц-зал Б',
            'Переговорная комната 1',
            'Переговорная комната 2',
            'Оборудование для презентаций',
            'Проектор'
        )
        self.resource_combo.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="Клиент:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.customer_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.customer_var, width=42).grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="Дата начала:").grid(row=2, column=0, sticky=tk.W, pady=5)
        date_frame = ttk.Frame(frame)
        date_frame.grid(row=2, column=1, pady=5, padx=5, sticky=tk.W)
        
        self.start_date = DateEntry(date_frame, width=20, background='darkblue',
                                    foreground='white', borderwidth=2, date_pattern='dd.mm.yyyy')
        self.start_date.pack(side=tk.LEFT)
        
        ttk.Label(date_frame, text="Время:").pack(side=tk.LEFT, padx=(10, 5))
        self.start_hour = ttk.Spinbox(date_frame, from_=0, to=23, width=5, format='%02.0f')
        self.start_hour.set('09')
        self.start_hour.pack(side=tk.LEFT)
        ttk.Label(date_frame, text=":").pack(side=tk.LEFT)
        self.start_minute = ttk.Spinbox(date_frame, from_=0, to=59, width=5, format='%02.0f')
        self.start_minute.set('00')
        self.start_minute.pack(side=tk.LEFT)
        
        ttk.Label(frame, text="Дата окончания:").grid(row=3, column=0, sticky=tk.W, pady=5)
        end_frame = ttk.Frame(frame)
        end_frame.grid(row=3, column=1, pady=5, padx=5, sticky=tk.W)
        
        self.end_date = DateEntry(end_frame, width=20, background='darkblue',
                                 foreground='white', borderwidth=2, date_pattern='dd.mm.yyyy')
        self.end_date.pack(side=tk.LEFT)
        
        ttk.Label(end_frame, text="Время:").pack(side=tk.LEFT, padx=(10, 5))
        self.end_hour = ttk.Spinbox(end_frame, from_=0, to=23, width=5, format='%02.0f')
        self.end_hour.set('17')
        self.end_hour.pack(side=tk.LEFT)
        ttk.Label(end_frame, text=":").pack(side=tk.LEFT)
        self.end_minute = ttk.Spinbox(end_frame, from_=0, to=59, width=5, format='%02.0f')
        self.end_minute.set('00')
        self.end_minute.pack(side=tk.LEFT)
        
        ttk.Label(frame, text="Примечания:").grid(row=4, column=0, sticky=tk.NW, pady=5)
        self.notes_text = tk.Text(frame, width=42, height=5)
        self.notes_text.grid(row=4, column=1, pady=5, padx=5)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Создать бронирование", 
                  command=self.create_booking, width=25).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Очистить", 
                  command=self.clear_create_form, width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Проверить доступность", 
                  command=self.check_availability, width=20).pack(side=tk.LEFT, padx=5)
        
        self.create_message = scrolledtext.ScrolledText(frame, width=70, height=8)
        self.create_message.grid(row=6, column=0, columnspan=2, pady=10, padx=5)
        
    def setup_bookings_list_tab(self):
        filter_frame = ttk.LabelFrame(self.bookings_list_tab, text="Фильтры", padding=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(filter_frame, text="Статус:").pack(side=tk.LEFT, padx=5)
        self.filter_status = ttk.Combobox(filter_frame, width=15)
        self.filter_status['values'] = ('Все', 'Ожидание', 'Подтверждено', 'Отменено')
        self.filter_status.set('Все')
        self.filter_status.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_frame, text="Ресурс:").pack(side=tk.LEFT, padx=5)
        self.filter_resource = ttk.Combobox(filter_frame, width=25)
        self.filter_resource['values'] = ('Все',)
        self.filter_resource.set('Все')
        self.filter_resource.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(filter_frame, text="Применить", 
                  command=self.refresh_bookings_list).pack(side=tk.LEFT, padx=10)
        
        list_frame = ttk.Frame(self.bookings_list_tab)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.bookings_tree = ttk.Treeview(list_frame, 
                                         columns=('ID', 'Ресурс', 'Клиент', 'Начало', 'Окончание', 'Статус'),
                                         show='headings',
                                         yscrollcommand=scrollbar.set)
        
        self.bookings_tree.heading('ID', text='ID')
        self.bookings_tree.heading('Ресурс', text='Ресурс')
        self.bookings_tree.heading('Клиент', text='Клиент')
        self.bookings_tree.heading('Начало', text='Дата начала')
        self.bookings_tree.heading('Окончание', text='Дата окончания')
        self.bookings_tree.heading('Статус', text='Статус')
        
        self.bookings_tree.column('ID', width=50)
        self.bookings_tree.column('Ресурс', width=200)
        self.bookings_tree.column('Клиент', width=150)
        self.bookings_tree.column('Начало', width=150)
        self.bookings_tree.column('Окончание', width=150)
        self.bookings_tree.column('Статус', width=100)
        
        self.bookings_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.bookings_tree.yview)
        
        control_frame = ttk.Frame(self.bookings_list_tab)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(control_frame, text="Подтвердить", 
                  command=self.confirm_selected_booking).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Отменить", 
                  command=self.cancel_selected_booking).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Обновить список", 
                  command=self.refresh_bookings_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Показать детали", 
                  command=self.show_booking_details).pack(side=tk.LEFT, padx=5)
        
    def setup_statistics_tab(self):
        stats_frame = ttk.LabelFrame(self.statistics_tab, text="Общая статистика", padding=15)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.stats_text = scrolledtext.ScrolledText(stats_frame, width=80, height=20)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(stats_frame, text="Обновить статистику", 
                  command=self.update_statistics).pack(pady=10)
        
    def setup_reports_tab(self):
        frame = ttk.LabelFrame(self.reports_tab, text="Генерация отчетов", padding=15)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Сгенерировать Markdown отчет", 
                  command=self.generate_markdown_report, width=30).pack(pady=5)
        ttk.Button(btn_frame, text="Показать анализ конфликтов", 
                  command=self.show_conflict_analysis, width=30).pack(pady=5)
        ttk.Button(btn_frame, text="Показать производительность", 
                  command=self.show_performance_stats, width=30).pack(pady=5)
        
        ttk.Label(frame, text="Предварительный просмотр:").pack(anchor=tk.W, pady=5)
        self.report_text = scrolledtext.ScrolledText(frame, width=80, height=25)
        self.report_text.pack(fill=tk.BOTH, expand=True)
        
    def create_booking(self):
        try:
            resource = self.resource_var.get()
            customer = self.customer_var.get()
            
            if not resource or not customer:
                messagebox.showwarning("Предупреждение", "Заполните все обязательные поля!")
                return
            

            start_dt = datetime.combine(
                self.start_date.get_date(),
                datetime.min.time().replace(
                    hour=int(self.start_hour.get()),
                    minute=int(self.start_minute.get())
                )
            )
            
            end_dt = datetime.combine(
                self.end_date.get_date(),
                datetime.min.time().replace(
                    hour=int(self.end_hour.get()),
                    minute=int(self.end_minute.get())
                )
            )
            
            notes = self.notes_text.get("1.0", tk.END).strip()
            
            import time
            start_time = time.time()
            
            booking = self.booking_system.create_booking(
                resource_name=resource,
                start_date=start_dt,
                end_date=end_dt,
                customer_name=customer,
                notes=notes
            )
            
            duration = time.time() - start_time
            self.analyzer.record_operation("create_booking", duration)
            
            if booking:
                self.create_message.insert(tk.END, 
                    f"✓ Бронирование успешно создано!\n"
                    f"  ID: {booking.id}\n"
                    f"  Ресурс: {booking.resource_name}\n"
                    f"  Период: {booking.start_date} - {booking.end_date}\n\n")
                messagebox.showinfo("Успех", "Бронирование создано!")
                self.clear_create_form()
                self.refresh_bookings_list()
            else:
                self.create_message.insert(tk.END, 
                    f"✗ Ошибка: Обнаружен конфликт бронирований!\n"
                    f"  Ресурс {resource} занят в указанное время.\n\n")
                messagebox.showerror("Ошибка", "Конфликт бронирований!")
                
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректные данные: {e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")
    
    def check_availability(self):
        try:
            resource = self.resource_var.get()
            if not resource:
                messagebox.showwarning("Предупреждение", "Выберите ресурс!")
                return
            
            start_dt = datetime.combine(
                self.start_date.get_date(),
                datetime.min.time().replace(
                    hour=int(self.start_hour.get()),
                    minute=int(self.start_minute.get())
                )
            )
            
            end_dt = datetime.combine(
                self.end_date.get_date(),
                datetime.min.time().replace(
                    hour=int(self.end_hour.get()),
                    minute=int(self.end_minute.get())
                )
            )
            
            existing = self.booking_system.get_bookings_by_resource(resource)
            active_bookings = [(b.start_date, b.end_date) for b in existing if b.is_active()]
            
            conflicts = ConflictChecker.check_date_conflicts(
                active_bookings, start_dt, end_dt
            )
            
            if conflicts:
                self.create_message.insert(tk.END,
                    f"⚠ Ресурс '{resource}' занят в указанное время!\n"
                    f"  Обнаружено конфликтов: {len(conflicts)}\n\n")
            else:
                self.create_message.insert(tk.END,
                    f"✓ Ресурс '{resource}' доступен!\n\n")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка проверки: {e}")
    
    def clear_create_form(self):
        self.resource_var.set('')
        self.customer_var.set('')
        self.notes_text.delete("1.0", tk.END)
        self.start_date.set_date(datetime.now())
        self.end_date.set_date(datetime.now())
        self.start_hour.set('09')
        self.start_minute.set('00')
        self.end_hour.set('17')
        self.end_minute.set('00')
    
    def refresh_bookings_list(self):
        for item in self.bookings_tree.get_children():
            self.bookings_tree.delete(item)
        all_bookings = self.booking_system.get_all_bookings()
        
        status_filter = self.filter_status.get()
        resource_filter = self.filter_resource.get()
        

        unique_resources = sorted(set(b.resource_name for b in all_bookings))
        self.filter_resource['values'] = ('Все',) + tuple(unique_resources)
        
        for booking in all_bookings:
            if status_filter != 'Все':
                status_map = {
                    'Ожидание': BookingStatus.PENDING,
                    'Подтверждено': BookingStatus.CONFIRMED,
                    'Отменено': BookingStatus.CANCELLED
                }
                if booking.status != status_map.get(status_filter):
                    continue
            
            if resource_filter != 'Все' and booking.resource_name != resource_filter:
                continue
            status_text = {
                BookingStatus.PENDING: 'Ожидание',
                BookingStatus.CONFIRMED: 'Подтверждено',
                BookingStatus.CANCELLED: 'Отменено',
                BookingStatus.COMPLETED: 'Завершено'
            }.get(booking.status, booking.status.value)
            
            self.bookings_tree.insert('', tk.END, values=(
                booking.id,
                booking.resource_name,
                booking.customer_name,
                booking.start_date.strftime('%d.%m.%Y %H:%M'),
                booking.end_date.strftime('%d.%m.%Y %H:%M'),
                status_text
            ))
    
    def confirm_selected_booking(self):
        selected = self.bookings_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите бронирование!")
            return
        
        item = self.bookings_tree.item(selected[0])
        booking_id = int(item['values'][0])
        
        if self.booking_system.confirm_booking(booking_id):
            messagebox.showinfo("Успех", f"Бронирование #{booking_id} подтверждено!")
            self.refresh_bookings_list()
        else:
            messagebox.showerror("Ошибка", "Не удалось подтвердить бронирование!")
    
    def cancel_selected_booking(self):
        selected = self.bookings_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите бронирование!")
            return
        
        item = self.bookings_tree.item(selected[0])
        booking_id = int(item['values'][0])
        
        if messagebox.askyesno("Подтверждение", 
                              f"Отменить бронирование #{booking_id}?"):
            if self.booking_system.cancel_booking(booking_id):
                messagebox.showinfo("Успех", f"Бронирование #{booking_id} отменено!")
                self.refresh_bookings_list()
            else:
                messagebox.showerror("Ошибка", "Не удалось отменить бронирование!")
    
    def show_booking_details(self):
        selected = self.bookings_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите бронирование!")
            return
        
        item = self.bookings_tree.item(selected[0])
        booking_id = int(item['values'][0])
        
        booking = self.booking_system.get_booking(booking_id)
        if booking:
            details = f"""
Детали бронирования #{booking.id}

Ресурс: {booking.resource_name}
Клиент: {booking.customer_name}
Начало: {booking.start_date.strftime('%d.%m.%Y %H:%M')}
Окончание: {booking.end_date.strftime('%d.%m.%Y %H:%M')}
Продолжительность: {booking.duration_days()} дней
Статус: {booking.status.value}
Создано: {booking.created_at.strftime('%d.%m.%Y %H:%M')}

Примечания:
{booking.notes if booking.notes else 'Нет примечаний'}
            """
            messagebox.showinfo("Детали бронирования", details)
    
    def update_statistics(self):
        self.stats_text.delete("1.0", tk.END)
        
        stats = self.booking_system.get_statistics()
        
        self.stats_text.insert(tk.END, "=" * 80 + "\n")
        self.stats_text.insert(tk.END, "СТАТИСТИКА СИСТЕМЫ БРОНИРОВАНИЯ\n")
        self.stats_text.insert(tk.END, "=" * 80 + "\n\n")
        
        self.stats_text.insert(tk.END, "1. ОБЩИЕ ПОКАЗАТЕЛИ\n")
        self.stats_text.insert(tk.END, "-" * 80 + "\n")
        self.stats_text.insert(tk.END, f"Всего бронирований: {stats['total_bookings']}\n")
        self.stats_text.insert(tk.END, f"Активных бронирований: {stats['active_bookings']}\n")
        self.stats_text.insert(tk.END, f"Подтвержденных: {stats['confirmed_bookings']}\n")
        self.stats_text.insert(tk.END, f"Отмененных: {stats['cancelled_bookings']}\n")
        self.stats_text.insert(tk.END, f"Уникальных ресурсов: {stats['unique_resources']}\n")
        self.stats_text.insert(tk.END, f"Уникальных клиентов: {stats['unique_customers']}\n\n")
        
        self.stats_text.insert(tk.END, "2. КОНФЛИКТЫ И ПОПЫТКИ\n")
        self.stats_text.insert(tk.END, "-" * 80 + "\n")
        self.stats_text.insert(tk.END, f"Всего попыток: {stats['total_attempts']}\n")
        self.stats_text.insert(tk.END, f"Конфликтов: {stats['conflict_count']}\n")
        self.stats_text.insert(tk.END, f"Процент конфликтов: {stats['conflict_rate']:.2f}%\n\n")
        
        analytics = BookingAnalytics.analyze_booking_patterns(
            self.booking_system.get_all_bookings()
        )
        
        self.stats_text.insert(tk.END, "3. АНАЛИЗ ПАТТЕРНОВ БРОНИРОВАНИЯ\n")
        self.stats_text.insert(tk.END, "-" * 80 + "\n")
        
        if analytics.get('most_popular_resource'):
            self.stats_text.insert(tk.END, 
                f"Самый популярный ресурс: {analytics['most_popular_resource']['name']} "
                f"({analytics['most_popular_resource']['count']} бронирований)\n")
        
        self.stats_text.insert(tk.END, 
            f"Средняя продолжительность: {analytics['average_duration_days']:.2f} дней\n")
        self.stats_text.insert(tk.END, 
            f"Мин/Макс продолжительность: {analytics['min_duration_days']} / "
            f"{analytics['max_duration_days']} дней\n\n")
        
        perf_summary = self.analyzer.get_performance_summary()
        if perf_summary:
            self.stats_text.insert(tk.END, "4. ПРОИЗВОДИТЕЛЬНОСТЬ\n")
            self.stats_text.insert(tk.END, "-" * 80 + "\n")
            
            for operation, metrics in perf_summary.items():
                self.stats_text.insert(tk.END, f"\n{operation}:\n")
                self.stats_text.insert(tk.END, f"  Выполнено: {metrics['count']}\n")
                self.stats_text.insert(tk.END, 
                    f"  Среднее время: {metrics['average']*1000:.4f} мс\n")
                self.stats_text.insert(tk.END, 
                    f"  Мин/Макс: {metrics['min']*1000:.4f} / "
                    f"{metrics['max']*1000:.4f} мс\n")
    
    def generate_markdown_report(self):
        stats = self.booking_system.get_statistics()
        analytics = BookingAnalytics.analyze_booking_patterns(
            self.booking_system.get_all_bookings()
        )
        performance = self.analyzer.get_performance_summary()
        
        report = ReportGenerator.generate_markdown_report(stats, analytics, performance)
        
        os.makedirs("reports", exist_ok=True)
        report_path = os.path.join("reports", "analysis_report.md")
        ReportGenerator.save_report(report, report_path)
        self.report_text.delete("1.0", tk.END)
        self.report_text.insert(tk.END, report)
        
        messagebox.showinfo("Успех", f"Отчет сохранен: {report_path}")
    
    def show_conflict_analysis(self):
        self.report_text.delete("1.0", tk.END)
        
        conflict_analysis = BookingAnalytics.analyze_conflicts(
            self.booking_system.get_all_bookings()
        )
        
        self.report_text.insert(tk.END, "=" * 80 + "\n")
        self.report_text.insert(tk.END, "АНАЛИЗ КОНФЛИКТОВ БРОНИРОВАНИЙ\n")
        self.report_text.insert(tk.END, "=" * 80 + "\n\n")
        
        self.report_text.insert(tk.END, 
            f"Всего обнаружено конфликтов: {conflict_analysis['total_conflicts']}\n\n")
        
        if conflict_analysis['conflicts_by_resource']:
            self.report_text.insert(tk.END, "Конфликты по ресурсам:\n")
            self.report_text.insert(tk.END, "-" * 80 + "\n")
            
            for resource, count in conflict_analysis['conflicts_by_resource'].items():
                self.report_text.insert(tk.END, f"  {resource}: {count}\n")
        
        if conflict_analysis['conflict_prone_resources']:
            self.report_text.insert(tk.END, "\nРесурсы с наибольшим количеством конфликтов:\n")
            self.report_text.insert(tk.END, "-" * 80 + "\n")
            
            for resource, count in conflict_analysis['conflict_prone_resources']:
                self.report_text.insert(tk.END, f"  {resource}: {count}\n")
    
    def show_performance_stats(self):
        self.report_text.delete("1.0", tk.END)
        
        perf_summary = self.analyzer.get_performance_summary()
        
        self.report_text.insert(tk.END, "=" * 80 + "\n")
        self.report_text.insert(tk.END, "СТАТИСТИКА ПРОИЗВОДИТЕЛЬНОСТИ\n")
        self.report_text.insert(tk.END, "=" * 80 + "\n\n")
        
        if perf_summary:
            for operation, metrics in perf_summary.items():
                self.report_text.insert(tk.END, f"{operation}:\n")
                self.report_text.insert(tk.END, "-" * 80 + "\n")
                self.report_text.insert(tk.END, f"  Выполнено операций: {metrics['count']}\n")
                self.report_text.insert(tk.END, 
                    f"  Среднее время: {metrics['average']*1000:.4f} мс\n")
                self.report_text.insert(tk.END, 
                    f"  Минимальное время: {metrics['min']*1000:.4f} мс\n")
                self.report_text.insert(tk.END, 
                    f"  Максимальное время: {metrics['max']*1000:.4f} мс\n")
                self.report_text.insert(tk.END, 
                    f"  Общее время: {metrics['total']:.4f} сек\n\n")
        else:
            self.report_text.insert(tk.END, "Нет данных о производительности.\n")
    
    def load_demo_data(self):
        demo_bookings = [
            {
                "resource": "Конференц-зал А",
                "start": datetime(2025, 1, 10, 9, 0),
                "end": datetime(2025, 1, 10, 17, 0),
                "customer": "ООО Компания 1",
                "notes": "Ежегодное собрание акционеров"
            },
            {
                "resource": "Конференц-зал А",
                "start": datetime(2025, 1, 11, 9, 0),
                "end": datetime(2025, 1, 11, 17, 0),
                "customer": "ООО Компания 2",
                "notes": "Презентация нового продукта"
            },
            {
                "resource": "Переговорная комната 1",
                "start": datetime(2025, 1, 10, 10, 0),
                "end": datetime(2025, 1, 10, 12, 0),
                "customer": "Иванов И.И.",
                "notes": "Встреча с клиентом"
            },
            {
                "resource": "Переговорная комната 1",
                "start": datetime(2025, 1, 10, 14, 0),
                "end": datetime(2025, 1, 10, 16, 0),
                "customer": "Петров П.П.",
                "notes": "Планирование проекта"
            },
            {
                "resource": "Оборудование для презентаций",
                "start": datetime(2025, 1, 15, 8, 0),
                "end": datetime(2025, 1, 20, 18, 0),
                "customer": "Проект X",
                "notes": "Конференция 2025"
            }
        ]
        
        import time
        for booking_data in demo_bookings:
            start_time = time.time()
            
            booking = self.booking_system.create_booking(
                resource_name=booking_data["resource"],
                start_date=booking_data["start"],
                end_date=booking_data["end"],
                customer_name=booking_data["customer"],
                notes=booking_data["notes"]
            )
            
            duration = time.time() - start_time
            self.analyzer.record_operation("create_booking", duration)
            
            if booking:
                self.booking_system.confirm_booking(booking.id)
        
        self.refresh_bookings_list()
        self.update_statistics()


def main():
    root = tk.Tk()
    app = BookingSystemGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
