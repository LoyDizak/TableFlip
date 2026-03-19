import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os

import backend.web as web
from backend.json_handling import load_persons
from backend.string_converter import persons_list_to_string, person_to_string


class AutofillTab:
    def __init__(self, parent, app):
        self.app = app
        self.autofill_tab = ttk.Frame(parent)
        
        self.persons: list = []
        self.current_person_index: int = 0
        self.web_driver = None
        
        self.create_autofill_tab()


    def create_autofill_tab(self):
        left = ttk.Frame(self.autofill_tab, width=450)
        left.pack(side='left', fill='y', padx=10, pady=10)
        left.pack_propagate(False)

        right = ttk.Frame(self.autofill_tab)
        right.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        json_frame = ttk.LabelFrame(left, text="Загрузка данных")
        json_frame.pack(fill='x', pady=5)
        ttk.Button(json_frame, text="Открыть файл", command=self.on_button_load_json).pack(side='left', padx=5, pady=5)
        self.current_json_label = ttk.Label(json_frame, text="Файл не выбран", wraplength=350)
        self.current_json_label.pack(side='left', padx=5)

        list_frame = ttk.LabelFrame(left, text="Текущий человек")
        list_frame.pack(fill='both', expand=False, pady=5)

        single_preview_frame = ttk.Frame(list_frame)
        single_preview_frame.pack(fill='both', expand=True, padx=3, pady=(3,6))
        self.current_person_preview = tk.Text(single_preview_frame, height=14, state='normal', wrap='none')
        self.app.context_menu.add_to_widget(self.current_person_preview)
        scroll_horizontal = ttk.Scrollbar(single_preview_frame, orient='horizontal', command=self.current_person_preview.xview)
        self.current_person_preview.configure(xscrollcommand=scroll_horizontal.set)
        scroll_horizontal.pack(side='bottom', fill='x')
        self.current_person_preview.pack(side='left', fill='both', expand=True)

        idx_frame = ttk.Frame(list_frame)
        idx_frame.pack(fill='x', padx=3, pady=2)
        ttk.Button(idx_frame, text="◀", width=3, command=lambda: self.change_current_person(self.current_person_index-1)).pack(side='left')
        self.current_label = ttk.Label(idx_frame, text="—", width=50, anchor='center')
        self.current_label.pack(side='left', padx=6, fill='x', expand=True)
        ttk.Button(idx_frame, text="▶", width=3, command=lambda: self.change_current_person(self.current_person_index+1)).pack(side='left')

        manual_frame = ttk.Frame(list_frame)
        manual_frame.pack(fill='x', padx=3, pady=(2,4))
        self.manual_index_var = tk.StringVar(value='1')
        ttk.Label(manual_frame, text="Номер:").pack(side='left')
        manual_index_entry = ttk.Entry(manual_frame, textvariable=self.manual_index_var, width=6)
        self.app.context_menu.add_to_widget(manual_index_entry)
        manual_index_entry.pack(side='left', padx=4)
        ttk.Button(manual_frame, text="Перейти", command=self.on_button_go_to_person_index).pack(side='left')

        actions = ttk.LabelFrame(left, text="Действия")
        actions.pack(fill='x', pady=5)
        ttk.Button(actions, text="Открыть браузер", command=self.on_button_open_web_page).pack(fill='x', padx=3, pady=3)
        ttk.Separator(actions, orient="horizontal").pack(fill="x", pady=5)
        ttk.Button(actions, text="Заполнить данные", command=self.on_button_fill_info).pack(fill='x', padx=3, pady=3)
        ttk.Button(actions, text="Подтвердить", command=self.on_button_confirm).pack(fill='x', padx=3, pady=3)
        ttk.Button(actions, text="Подтвердить и заполнить", command=self.on_button_confirm_and_fill).pack(fill='x', padx=3, pady=3)

        preview_frame = ttk.LabelFrame(right, text="Предпросмотр данных")
        preview_frame.pack(fill='both', expand=True)
        content_preview = ttk.Frame(preview_frame)
        content_preview.pack(fill='both', expand=True)
        self.autofill_preview = tk.Text(content_preview, state='normal', wrap='none')
        self.app.context_menu.add_to_widget(self.autofill_preview)
        v_scroll = ttk.Scrollbar(content_preview, orient='vertical', command=self.autofill_preview.yview)
        self.autofill_preview.configure(yscrollcommand=v_scroll.set)
        v_scroll.pack(side='right', fill='y')
        self.autofill_preview.pack(side='left', fill='both', expand=True)

    
    def update_json_preview(self):
        self.autofill_preview.delete(1.0, tk.END)
        self.autofill_preview.insert(tk.END, persons_list_to_string(self.persons))


    def update_current_person_preview(self):
        self.current_person_preview.delete(1.0, tk.END)
        if not self.persons:
            self.current_label.config(text='—')
            self.current_person_preview.insert(tk.END, 'Нет данных')
        else:
            current_person = self.persons[self.current_person_index]
            self.current_label.config(text=f"{self.current_person_index + 1}/{len(self.persons)} — {current_person.full_name}")
            self.current_person_preview.insert(tk.END, person_to_string(current_person))


    def change_current_person(self, new_index:int):
        new_index = max(0, min(new_index, len(self.persons) - 1))
        self.current_person_index = new_index
        self.update_current_person_preview()


    def on_button_load_json(self):
        if not self.app.check_license():
            return

        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not path:
            return
        
        try:
            self.persons = load_persons(path)
            self.current_json_label.config(text=os.path.basename(path))
            self.current_person_index = 0
            self.update_current_person_preview()
            self.update_json_preview()
        except:
            messagebox.showerror("Ошибка", "Не удалось загрузить файл")


    def on_button_go_to_person_index(self):
        if not self.app.check_license():
            return

        if not self.persons:
            messagebox.showwarning("Внимание", "Сначала загрузите JSON с людьми")
            return
        try:
            new_index = int(self.manual_index_var.get()) - 1
            self.change_current_person(new_index)
        except Exception:
            messagebox.showerror("Ошибка", "Неверный формат номера")
            return
        

    def on_button_open_web_page(self):
        if not self.app.check_license():
            return

        if self.web_driver:
            self.web_driver.quit()
        try:
            thread = threading.Thread(target = web.open_browser, daemon = True)
            thread.start()
        except Exception:
            messagebox.showerror("Ошибка", "Не удалось открыть страницу браузера")


    def on_button_fill_info(self):
        if not self.app.check_license():
            return

        if not self.web_driver:
            messagebox.showwarning("Внимание", "Сначала откройте страницу")
            return
        if not self.persons:
            messagebox.showwarning("Внимание", "Сначала откройте файл с данными")
            return
        try:
            web.fill_person_form(self.web_driver, self.persons[self.current_person_index])
        except Exception:
            messagebox.showerror("Ошибка", "Не удалось заполнить данные")


    def on_button_confirm(self):
        if not self.app.check_license():
            return

        if not self.web_driver:
            messagebox.showwarning("Внимание", "Сначала откройте страницу")
            return
        try:
            web.confirm_entry(self.web_driver)
        except Exception:
            messagebox.showerror("Ошибка", "Не удалось найти кнопку подтверждения")


    def on_button_confirm_and_fill(self):
        if not self.app.check_license():
            return

        self.on_button_confirm()
        self.change_current_person(self.current_person_index + 1)
        self.on_button_fill_info()
