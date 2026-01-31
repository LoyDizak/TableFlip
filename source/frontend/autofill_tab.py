import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from selenium.webdriver.common.by import By

import backend.web as web
from backend.json_handler import load_persons_from_json
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
        left = ttk.Frame(self.autofill_tab, width=360)
        left.pack(side='left', fill='y', padx=10, pady=10)

        right = ttk.Frame(self.autofill_tab)
        right.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        json_frame = ttk.LabelFrame(left, text="JSON")
        json_frame.pack(fill='x', pady=5)
        ttk.Button(json_frame, text="Открыть JSON", command=self.on_button_load_json_autofill).pack(side='left', padx=5, pady=5)
        self.autofill_json_label = ttk.Label(json_frame, text="Файл не выбран", wraplength=240)
        self.autofill_json_label.pack(side='left', padx=5)

        list_frame = ttk.LabelFrame(left, text="Текущий человек")
        list_frame.pack(fill='both', expand=False, pady=5)

        single_preview_frame = ttk.Frame(list_frame)
        single_preview_frame.pack(fill='both', expand=True, padx=3, pady=(3,6))
        self.current_person_preview = tk.Text(single_preview_frame, height=14, state='normal', wrap='none')
        sp_v = ttk.Scrollbar(single_preview_frame, orient='vertical', command=self.current_person_preview.yview)
        self.current_person_preview.configure(yscrollcommand=sp_v.set)
        sp_v.pack(side='right', fill='y')
        self.current_person_preview.pack(side='left', fill='both', expand=True)

        idx_frame = ttk.Frame(list_frame)
        idx_frame.pack(fill='x', padx=3, pady=2)
        ttk.Button(idx_frame, text="◀", width=3, command=lambda: self.change_current_person(self.current_person_index-1)).pack(side='left')
        self.current_label = ttk.Label(idx_frame, text="—", width=50, anchor='center')
        self.current_label.pack(side='left', padx=6, fill='x', expand=True)
        ttk.Button(idx_frame, text="▶", width=3, command=lambda: self.change_current_person(self.current_person_index+1)).pack(side='left')

        manual_frame = ttk.Frame(list_frame)
        manual_frame.pack(fill='x', padx=3, pady=(2,4))
        self.manual_index_var = tk.StringVar(value='0')
        ttk.Label(manual_frame, text="Индекс:").pack(side='left')
        manual_index_entry = ttk.Entry(manual_frame, textvariable=self.manual_index_var, width=6)
        manual_index_entry.pack(side='left', padx=4)
        ttk.Button(manual_frame, text="Перейти", command=self.on_button_go_to_person_index).pack(side='left')

        page_frame = ttk.LabelFrame(left, text="Страница")
        page_frame.pack(fill='x', pady=5)
        self.page_url_var = tk.StringVar()
        page_url_entry = ttk.Entry(page_frame, textvariable=self.page_url_var, width=40)
        page_url_entry.pack(fill='x', padx=3, pady=3)
        ttk.Button(page_frame, text="Открыть страницу", command=self.on_button_open_web_page).pack(fill='x', padx=3, pady=3)

        actions = ttk.LabelFrame(left, text="Действия")
        actions.pack(fill='x', pady=5)
        ttk.Button(actions, text="Заполнить данные", command=self.on_button_fill_info).pack(fill='x', padx=3, pady=3)
        ttk.Button(actions, text="Подтвердить", command=self.on_button_confirm).pack(fill='x', padx=3, pady=3)
        ttk.Button(actions, text="Подтвердить и заполнить", command=self.on_button_confirm_and_fill).pack(fill='x', padx=3, pady=3)


        preview_frame = ttk.LabelFrame(right, text="Предпросмотр JSON")
        preview_frame.pack(fill='both', expand=True)
        content_preview = ttk.Frame(preview_frame)
        content_preview.pack(fill='both', expand=True)
        self.autofill_preview = tk.Text(content_preview, state='normal', wrap='none')
        v_scroll = ttk.Scrollbar(content_preview, orient='vertical', command=self.autofill_preview.yview)
        self.autofill_preview.configure(yscrollcommand=v_scroll.set)
        v_scroll.pack(side='right', fill='y')
        self.autofill_preview.pack(side='left', fill='both', expand=True)

    def on_button_load_json_autofill(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not path:
            return
        try:
            persons = load_persons_from_json(path)
            self.persons = persons
            self.autofill_json_label.config(text=path)
            self.current_person_index = 0
            self.update_current_person_preview()
            self.update_autofill_preview()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def update_autofill_preview(self):
        self.autofill_preview.delete(1.0, tk.END)
        try:
            self.autofill_preview.insert(tk.END, persons_list_to_string(self.persons))
        except Exception:
            self.autofill_preview.insert(tk.END, "Нет данных")

    def update_current_person_preview(self):
        self.current_person_preview.delete(1.0, tk.END)
        if not self.persons:
            self.current_label.config(text='—')
            self.current_person_preview.insert(tk.END, 'Нет данных')
        else:
            current_person = self.persons[self.current_person_index]
            self.current_label.config(text=f"{self.current_person_index}/{len(self.persons)-1} — {current_person.full_name}")
            try:
                self.current_person_preview.insert(tk.END, person_to_string(current_person))
            except Exception:
                self.current_person_preview.insert(tk.END, str(current_person.__dict__))

    def change_current_person(self, new_index:int):
        new_index = max(0, min(new_index, len(self.persons) - 1))
        self.current_person_index = new_index
        self.update_current_person_preview()

    def on_button_go_to_person_index(self):
        if not self.persons:
            messagebox.showwarning("Внимание", "Сначала загрузите JSON с людьми")
            return
        try:
            new_index = int(self.manual_index_var.get())
            self.change_current_person(new_index)
        except Exception:
            messagebox.showerror("Ошибка", "Индекс должен быть числом")
            return
        
    def on_button_open_web_page(self):
        url = self.page_url_var.get()
        try:
            # open page in background to avoid blocking UI
            def _open():
                self.web_driver = web.open_page(url)
            
            t = threading.Thread(target=_open, daemon=True)
            t.start()
        
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def on_button_fill_info(self):
        if not self.web_driver:
            messagebox.showwarning("Внимание", "Сначала откройте страницу")
            return
        if not self.persons:
            messagebox.showwarning("Внимание", "Сначала загрузите JSON с людьми")
            return
        person = self.persons[self.current_person_index]
        try:
            web.fill_person_form(self.web_driver, person)
            self.update_current_person_preview()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def on_button_confirm(self):
        if not self.web_driver:
            messagebox.showwarning("Внимание", "Сначала откройте страницу")
            return
        try:
            drv = self.web_driver
            # попробуем найти кнопку submit с текстом "Сохранить"
            try:
                btn = drv.find_element(By.XPATH, "//input[@type='submit' and (@value='Сохранить' or @value='Save')]")
            except Exception:
                try:
                    btn = drv.find_element(By.CSS_SELECTOR, "input[type='submit'].btn.btn-primary")
                except Exception:
                    btn = None
            if btn:
                btn.click()
                self.change_current_person(self.current_person_index + 1)
            else:
                messagebox.showwarning("Внимание", "Кнопка подтверждения не найдена на странице")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))


    def on_button_confirm_and_fill(self):
        # Click confirm (submit current)
        self.on_button_confirm()
        # Move to next person
        self.change_current_person(self.current_person_index + 1)
        # Fill next person's data
        self.on_button_fill_info()
        