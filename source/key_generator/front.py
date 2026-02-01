"""
GUI приложение для генерации лицензионных ключей
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime, timedelta
import os
import re

from key_generator import KeyGenerator


class DateEntry(ttk.Entry):
    """Entry с автоформатированием для ввода даты в формате ДД.ММ.ГГГГ"""
    
    def __init__(self, parent, **kwargs):
        self.var = tk.StringVar()
        super().__init__(parent, textvariable=self.var, **kwargs)
        
        self.var.trace('w', self.on_change)
        self.bind('<KeyRelease>', self.on_key_release)
        
    def on_change(self, *args):
        """Автоматическое форматирование при вводе"""
        text = self.var.get()
        
        # Удаляем все кроме цифр и точек
        cleaned = ''.join(c for c in text if c.isdigit() or c == '.')
        
        # Убираем лишние точки
        parts = cleaned.split('.')
        if len(parts) > 3:
            cleaned = '.'.join(parts[:3])
        
        # Ограничиваем длину частей
        parts = cleaned.split('.')
        formatted_parts = []
        for i, part in enumerate(parts):
            if i == 0:  # День (макс 2 цифры)
                formatted_parts.append(part[:2])
            elif i == 1:  # Месяц (макс 2 цифры)
                formatted_parts.append(part[:2])
            elif i == 2:  # Год (макс 4 цифры)
                formatted_parts.append(part[:4])
        
        formatted = '.'.join(formatted_parts)
        
        if formatted != text:
            # Сохраняем позицию курсора
            cursor_pos = self.index(tk.INSERT)
            self.var.set(formatted)
            # Восстанавливаем позицию курсора
            self.icursor(min(cursor_pos, len(formatted)))
    
    def on_key_release(self, event):
        """Автоматическая вставка точек"""
        text = self.var.get()
        cursor_pos = self.index(tk.INSERT)
        
        # Автоматически добавляем точки после дня и месяца
        if len(text) == 2 and '.' not in text and cursor_pos == 2:
            self.var.set(text + '.')
            self.icursor(3)
        elif len(text) == 5 and text.count('.') == 1 and cursor_pos == 5:
            self.var.set(text + '.')
            self.icursor(6)
    
    def get_date(self):
        """Получить дату в формате ISO (ГГГГ-ММ-ДД) или None если невалидна"""
        text = self.var.get()
        
        # Проверяем формат ДД.ММ.ГГГГ
        match = re.match(r'^(\d{2})\.(\d{2})\.(\d{4})$', text)
        if not match:
            return None
        
        day, month, year = match.groups()
        
        try:
            # Пытаемся создать дату для проверки валидности
            date = datetime(int(year), int(month), int(day))
            # Возвращаем в формате ISO
            return date.strftime('%Y-%m-%d')
        except ValueError:
            return None


class LicenseGeneratorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Генератор лицензий - DOCX Analyze II")
        self.geometry("600x500")
        
        self.generator = KeyGenerator()
        
        self.create_widgets()
        self.setup_keyboard_shortcuts()
        
    def create_widgets(self):
        # Notebook для вкладок
        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка 1: Управление ключами
        keys_tab = ttk.Frame(notebook)
        notebook.add(keys_tab, text="Управление ключами")
        self.create_keys_tab(keys_tab)
        
        # Вкладка 2: Генерация лицензий
        gen_tab = ttk.Frame(notebook)
        notebook.add(gen_tab, text="Генерация лицензий")
        self.create_generation_tab(gen_tab)
        
    def create_keys_tab(self, parent):
        """Вкладка управления RSA ключами"""
        
        frame = ttk.LabelFrame(parent, text="RSA ключи")
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Статус ключей
        status_frame = ttk.Frame(frame)
        status_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(status_frame, text="Статус ключей:").pack(side='left')
        self.keys_status_label = ttk.Label(status_frame, text="Не загружены", foreground="red")
        self.keys_status_label.pack(side='left', padx=10)
        
        # Кнопки
        buttons_frame = ttk.Frame(frame)
        buttons_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(
            buttons_frame,
            text="Сгенерировать новые ключи",
            command=self.generate_new_keys
        ).pack(side='left', padx=5)
        
        ttk.Button(
            buttons_frame,
            text="Загрузить приватный ключ",
            command=self.load_private_key
        ).pack(side='left', padx=5)
        
        ttk.Button(
            buttons_frame,
            text="Сохранить ключи",
            command=self.save_keys
        ).pack(side='left', padx=5)
        
        # Публичный ключ для встраивания
        pub_key_frame = ttk.LabelFrame(frame, text="Публичный ключ (для встраивания в приложение)")
        pub_key_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        text_frame = ttk.Frame(pub_key_frame)
        text_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.public_key_text = tk.Text(text_frame, height=15, wrap='word')
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=self.public_key_text.yview)
        self.public_key_text.configure(yscrollcommand=scrollbar.set)
        
        self.public_key_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Настройка контекстного меню для публичного ключа
        self.setup_text_context_menu(self.public_key_text)
        
        ttk.Button(
            pub_key_frame,
            text="Копировать в буфер обмена (Ctrl+C)",
            command=self.copy_public_key
        ).pack(pady=5)
        
    def create_generation_tab(self, parent):
        """Вкладка генерации лицензий"""
        
        # Параметры лицензии
        params_frame = ttk.LabelFrame(parent, text="Параметры лицензии")
        params_frame.pack(fill='x', padx=10, pady=10)
        
        # Срок действия
        expire_frame = ttk.Frame(params_frame)
        expire_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(expire_frame, text="Срок действия:").pack(side='left')
        
        self.expire_days_var = tk.IntVar(value=365)
        ttk.Radiobutton(
            expire_frame,
            text="30 дней",
            variable=self.expire_days_var,
            value=30
        ).pack(side='left', padx=5)
        
        ttk.Radiobutton(
            expire_frame,
            text="1 год",
            variable=self.expire_days_var,
            value=365
        ).pack(side='left', padx=5)
        
        ttk.Radiobutton(
            expire_frame,
            text="Бессрочная",
            variable=self.expire_days_var,
            value=36500  # 100 лет
        ).pack(side='left', padx=5)
        
        # Пользовательский срок - используем DateEntry
        custom_frame = ttk.Frame(params_frame)
        custom_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(custom_frame, text="Или указать дату:").pack(side='left')
        self.custom_date_entry = DateEntry(custom_frame, width=15)
        self.custom_date_entry.pack(side='left', padx=5)
        ttk.Label(custom_frame, text="(формат: ДД.ММ.ГГГГ)").pack(side='left')
        
        # Настройка контекстного меню для поля даты
        self.setup_entry_context_menu(self.custom_date_entry)
        
        # Hardware ID
        hwid_frame = ttk.Frame(params_frame)
        hwid_frame.pack(fill='x', padx=10, pady=5)
        
        self.bind_hwid_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            hwid_frame,
            text="Привязать к компьютеру",
            variable=self.bind_hwid_var,
            command=self.toggle_hwid_entry
        ).pack(side='left')
        
        self.hwid_var = tk.StringVar(value="")
        self.hwid_entry = ttk.Entry(hwid_frame, textvariable=self.hwid_var, width=20, state='disabled')
        self.hwid_entry.pack(side='left', padx=5)
        
        # Настройка контекстного меню для HWID
        self.setup_entry_context_menu(self.hwid_entry)
                
        # Кнопка генерации
        ttk.Button(
            params_frame,
            text="Сгенерировать лицензию (F5)",
            command=self.generate_license
        ).pack(pady=10)
        
        # Результат
        result_frame = ttk.LabelFrame(parent, text="Сгенерированный ключ")
        result_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        text_frame = ttk.Frame(result_frame)
        text_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.license_key_text = tk.Text(text_frame, height=8, wrap='word')
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=self.license_key_text.yview)
        self.license_key_text.configure(yscrollcommand=scrollbar.set)
        
        self.license_key_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Настройка контекстного меню для лицензионного ключа
        self.setup_text_context_menu(self.license_key_text)
        
        buttons = ttk.Frame(result_frame)
        buttons.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(
            buttons,
            text="Копировать ключ (Ctrl+Shift+C)",
            command=self.copy_license_key
        ).pack(side='left', padx=5)
        
        ttk.Button(
            buttons,
            text="Сохранить в файл (Ctrl+S)",
            command=self.save_license_to_file
        ).pack(side='left', padx=5)
        
        ttk.Button(
            buttons,
            text="Очистить",
            command=lambda: self.license_key_text.delete(1.0, tk.END)
        ).pack(side='left', padx=5)
    
    # ----- Keyboard shortcuts -----
    
    def setup_keyboard_shortcuts(self):
        """Настройка горячих клавиш"""
        # Ctrl+C для копирования публичного ключа
        self.public_key_text.bind('<Control-c>', lambda e: self.copy_public_key())
        self.public_key_text.bind('<Control-a>', lambda e: self.select_all_text(self.public_key_text))
        
        # Ctrl+Shift+C для копирования лицензионного ключа
        self.bind('<Control-Shift-C>', lambda e: self.copy_license_key())
        self.bind('<Control-Shift-c>', lambda e: self.copy_license_key())
        
        # Ctrl+S для сохранения лицензии
        self.bind('<Control-s>', lambda e: self.save_license_to_file())
        self.bind('<Control-S>', lambda e: self.save_license_to_file())
        
        # F5 для генерации лицензии
        self.bind('<F5>', lambda e: self.generate_license())
        
        # Ctrl+C, Ctrl+V, Ctrl+A для текстового поля с ключом
        self.license_key_text.bind('<Control-c>', lambda e: self.copy_from_text(self.license_key_text))
        self.license_key_text.bind('<Control-a>', lambda e: self.select_all_text(self.license_key_text))
        
    def setup_text_context_menu(self, text_widget):
        """Настройка контекстного меню для Text виджета"""
        context_menu = tk.Menu(text_widget, tearoff=0)
        context_menu.add_command(label="Копировать", command=lambda: self.copy_from_text(text_widget))
        context_menu.add_separator()
        context_menu.add_command(label="Выделить всё", command=lambda: self.select_all_text(text_widget))
        
        def show_context_menu(event):
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
        
        text_widget.bind('<Button-3>', show_context_menu)
    
    def setup_entry_context_menu(self, entry_widget):
        """Настройка контекстного меню для Entry виджета"""
        context_menu = tk.Menu(entry_widget, tearoff=0)
        context_menu.add_command(label="Копировать", command=lambda: self.copy_from_entry(entry_widget))
        context_menu.add_command(label="Вырезать", command=lambda: self.cut_from_entry(entry_widget))
        context_menu.add_command(label="Вставить", command=lambda: self.paste_to_entry(entry_widget))
        context_menu.add_separator()
        context_menu.add_command(label="Выделить всё", command=lambda: self.select_all_entry(entry_widget))
        
        def show_context_menu(event):
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
        
        entry_widget.bind('<Button-3>', show_context_menu)
        
        # Стандартные горячие клавиши для Entry
        entry_widget.bind('<Control-a>', lambda e: self.select_all_entry(entry_widget))
    
    # ----- Context menu helpers -----
    
    def copy_from_text(self, text_widget):
        """Копировать выделенный текст из Text виджета"""
        try:
            text = text_widget.selection_get()
            self.clipboard_clear()
            self.clipboard_append(text)
        except tk.TclError:
            # Если ничего не выделено, копируем весь текст
            text = text_widget.get(1.0, tk.END).strip()
            if text:
                self.clipboard_clear()
                self.clipboard_append(text)
        return 'break'
    
    def select_all_text(self, text_widget):
        """Выделить весь текст в Text виджете"""
        text_widget.tag_add('sel', '1.0', 'end')
        text_widget.mark_set('insert', '1.0')
        text_widget.see('insert')
        return 'break'
    
    def copy_from_entry(self, entry_widget):
        """Копировать из Entry виджета"""
        try:
            text = entry_widget.selection_get()
            self.clipboard_clear()
            self.clipboard_append(text)
        except tk.TclError:
            pass
    
    def cut_from_entry(self, entry_widget):
        """Вырезать из Entry виджета"""
        try:
            text = entry_widget.selection_get()
            self.clipboard_clear()
            self.clipboard_append(text)
            entry_widget.delete('sel.first', 'sel.last')
        except tk.TclError:
            pass
    
    def paste_to_entry(self, entry_widget):
        """Вставить в Entry виджет"""
        try:
            text = self.clipboard_get()
            entry_widget.insert(tk.INSERT, text)
        except tk.TclError:
            pass
    
    def select_all_entry(self, entry_widget):
        """Выделить весь текст в Entry виджете"""
        entry_widget.select_range(0, tk.END)
        entry_widget.icursor(tk.END)
        return 'break'
        
    # ----- Обработчики событий -----
    
    def generate_new_keys(self):
        """Сгенерировать новую пару RSA ключей"""
        if messagebox.askyesno(
            "Подтверждение",
            "Сгенерировать новую пару ключей? Старые ключи будут заменены."
        ):
            try:
                self.generator.generate_rsa_keys()
                self.keys_status_label.config(text="Ключи сгенерированы", foreground="green")
                
                # Отображаем публичный ключ
                public_key_pem = self.generator.get_public_key_pem()
                self.public_key_text.delete(1.0, tk.END)
                self.public_key_text.insert(1.0, public_key_pem)
                
            except Exception:
                messagebox.showerror("Ошибка", "Не удалось сгенерировать ключи")
    
    def load_private_key(self):
        """Загрузить приватный ключ из файла"""
        file_path = filedialog.askopenfilename(
            title="Выберите файл приватного ключа",
            filetypes=[("PEM files", "*.pem"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            self.generator.load_keys(file_path)
            self.keys_status_label.config(text="Ключи загружены", foreground="green")
            
            # Отображаем публичный ключ
            public_key_pem = self.generator.get_public_key_pem()
            self.public_key_text.delete(1.0, tk.END)
            self.public_key_text.insert(1.0, public_key_pem)
            
        except Exception:
            messagebox.showerror("Ошибка", "Не удалось загрузить ключ")
    
    def save_keys(self):
        """Сохранить ключи в файлы"""
        if not self.generator.private_key:
            messagebox.showwarning("Внимание", "Сначала сгенерируйте или загрузите ключи")
            return
        
        # Выбираем директорию
        directory = filedialog.askdirectory(title="Выберите директорию для сохранения ключей")
        
        if not directory:
            return
        
        try:
            private_path = os.path.join(directory, "private_key.pem")
            public_path = os.path.join(directory, "public_key.pem")
            
            self.generator.save_keys(private_path, public_path)
        
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить ключи:\n{e}")
    
    def copy_public_key(self):
        """Копировать публичный ключ в буфер обмена"""
        public_key = self.public_key_text.get(1.0, tk.END).strip()
        if public_key:
            self.clipboard_clear()
            self.clipboard_append(public_key)
            # Визуальная обратная связь
            original_text = self.keys_status_label.cget("text")
            original_color = self.keys_status_label.cget("foreground")
            self.keys_status_label.config(text="Скопировано!", foreground="blue")
            self.after(1500, lambda: self.keys_status_label.config(text=original_text, foreground=original_color))
        else:
            messagebox.showwarning("Внимание", "Нет ключа для копирования")
    
    def toggle_hwid_entry(self):
        """Включить/выключить поле HWID"""
        if self.bind_hwid_var.get():
            self.hwid_entry.config(state='normal')
        else:
            self.hwid_entry.config(state='disabled')
            self.hwid_var.set("")
    
    def generate_license(self):
        """Сгенерировать лицензионный ключ"""
        if not self.generator.private_key:
            messagebox.showwarning("Внимание", "Сначала сгенерируйте или загрузите ключи")
            return
        
        try:
            # Определяем дату истечения
            custom_date = self.custom_date_entry.get_date()
            if custom_date:
                # Используем дату из поля
                expire_date = datetime.fromisoformat(custom_date)
            else:
                # Используем радиокнопки
                days = self.expire_days_var.get()
                expire_date = datetime.now() + timedelta(days=days)
            
            # HWID
            hwid = ""
            if self.bind_hwid_var.get():
                hwid = self.hwid_var.get()
                if not hwid:
                    messagebox.showwarning("Внимание", "Укажите Hardware ID или снимите галочку")
                    return
            
            # Генерируем ключ
            license_key = self.generator.generate_license(
                expire_date=expire_date,
                hwid=hwid
            )
            
            # Отображаем
            self.license_key_text.delete(1.0, tk.END)
            self.license_key_text.insert(1.0, license_key)
            
            # Информация
            info = f"\n\nСрок действия до: {expire_date.date()}"
            if hwid:
                info += f"\nПривязано к HWID: {hwid}"
            else:
                info += "\nБез привязки к компьютеру"
            
            self.license_key_text.insert(tk.END, info)
            
            # Автоматически выделяем ключ для удобного копирования
            self.license_key_text.tag_add('sel', '1.0', '1.end')
                        
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сгенерировать лицензионный ключ:\n{e}")
    
    def copy_license_key(self):
        """Копировать лицензионный ключ"""
        text = self.license_key_text.get(1.0, tk.END).strip()
        # Берем только первую строку (сам ключ)
        lines = text.split('\n')
        license_key = lines[0] if lines else ""
        
        if license_key:
            self.clipboard_clear()
            self.clipboard_append(license_key)
            
        else:
            messagebox.showwarning("Внимание", "Нет ключа для копирования")
    
    def save_license_to_file(self):
        """Сохранить лицензию в файл"""
        text = self.license_key_text.get(1.0, tk.END).strip()
        lines = text.split('\n')
        license_key = lines[0] if lines else ""
        
        if not license_key:
            messagebox.showwarning("Внимание", "Нет ключа для сохранения")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".lic",
            filetypes=[("License files", "*.lic"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(license_key)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")


if __name__ == "__main__":
    app = LicenseGeneratorApp()
    app.mainloop()