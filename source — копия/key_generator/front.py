"""
GUI приложение для генерации лицензионных ключей
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime, timedelta
import os

from key_generator import KeyGenerator


class LicenseGeneratorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Генератор лицензий - DOCX Analyze II")
        self.geometry("600x450")
        
        self.generator = KeyGenerator()
        
        self.create_widgets()
        
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
        
        ttk.Button(
            pub_key_frame,
            text="Копировать в буфер обмена",
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
        
        # Пользовательский срок
        custom_frame = ttk.Frame(params_frame)
        custom_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(custom_frame, text="Или указать дату:").pack(side='left')
        self.custom_date_var = tk.StringVar(value="")
        ttk.Entry(custom_frame, textvariable=self.custom_date_var, width=15).pack(side='left', padx=5)
        ttk.Label(custom_frame, text="(формат: ГГГГ-ММ-ДД)").pack(side='left')
        
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
                
        # Кнопка генерации
        ttk.Button(
            params_frame,
            text="Сгенерировать лицензию",
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
        
        buttons = ttk.Frame(result_frame)
        buttons.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(
            buttons,
            text="Копировать ключ",
            command=self.copy_license_key
        ).pack(side='left', padx=5)
        
        ttk.Button(
            buttons,
            text="Сохранить в файл",
            command=self.save_license_to_file
        ).pack(side='left', padx=5)
        
        ttk.Button(
            buttons,
            text="Очистить",
            command=lambda: self.license_key_text.delete(1.0, tk.END)
        ).pack(side='left', padx=5)
        
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
            
            messagebox.showinfo(
                "Успех",
                f"Ключи сохранены:\n\nПриватный: {private_path}\nПубличный: {public_path}\n\n"
                "ВАЖНО: Храните приватный ключ в секрете!"
            )
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить ключи:\n{e}")
    
    def copy_public_key(self):
        """Копировать публичный ключ в буфер обмена"""
        public_key = self.public_key_text.get(1.0, tk.END).strip()
        if public_key:
            self.clipboard_clear()
            self.clipboard_append(public_key)
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
            if self.custom_date_var.get():
                expire_date = datetime.fromisoformat(self.custom_date_var.get())
            else:
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
                        
        except Exception as e:
            messagebox.showerror("Ошибка", "Не удалось сгенерировать лицензионный ключ")
    
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
                messagebox.showinfo("Успех", f"Лицензия сохранена в:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")


if __name__ == "__main__":
    app = LicenseGeneratorApp()
    app.mainloop()