import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from selenium.webdriver.common.by import By

import web
from data import TableLayout, PERSON_FIELDS_RUSSIAN_NAMES
from string_converter import matrix_to_string, persons_list_to_string
from parser import extract_docx_table, parse_table_data, add_data_to_persons_list
from json_handler import save_persons_to_json, load_persons_from_json


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DOCX Analyze II   |   Автор: Артём Всяких")
        self.geometry("1200x750")

        self.docx_path = ""
        self.table_data = []
        self.persons_list = []

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)

        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="Парсинг")

        self.create_parser_tab()
        self.create_autofill_tab()

    def create_parser_tab(self):
        # Делим окно на две колонки: слева — управление, справа — превью (таблица + результаты)
        left = ttk.Frame(self.main_tab, width=420)
        left.pack(side='left', fill='y', padx=10, pady=10)

        right = ttk.Frame(self.main_tab)
        right.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        # --- Left: Controls (фиксированная область, не должна прокручиваться) ---
        file_frame = ttk.LabelFrame(left, text="Документ")
        file_frame.pack(fill='x', pady=5)

        ttk.Button(file_frame, text="Выбрать .docx", command=self.select_docx).pack(side='left', padx=5, pady=5)
        self.docx_label = ttk.Label(file_frame, text="Файл не выбран", wraplength=360)
        self.docx_label.pack(side='left', padx=5)

        table_idx_frame = ttk.Frame(left)
        table_idx_frame.pack(fill='x', pady=5)
        ttk.Label(table_idx_frame, text="Номер таблицы:").pack(side='left')
        self.table_index_var = tk.IntVar(value=0)
        table_index_entry = ttk.Entry(table_idx_frame, textvariable=self.table_index_var, width=6)
        table_index_entry.pack(side='left', padx=5)
        self.setup_entry_widget_menu(table_index_entry)
        ttk.Button(table_idx_frame, text="Загрузить таблицу", command=self.load_table).pack(side='left', padx=5)

        mapping_frame = ttk.LabelFrame(left, text="Соответствие столбцов")
        mapping_frame.pack(fill='both', pady=5)

        # создаём компактную сетку соответствий (числовые индексы столбцов)
        self.column_vars = {}
        mapping_keys = [k for k in PERSON_FIELDS_RUSSIAN_NAMES.keys() if k not in ("last_name", "first_name", "middle_name")]
        for row, key in enumerate(mapping_keys):
            label_text = PERSON_FIELDS_RUSSIAN_NAMES[key]
            lbl = ttk.Label(mapping_frame, text=label_text)
            lbl.grid(row=row, column=0, sticky='w', padx=3, pady=2)
            var = tk.IntVar(value=-1)
            self.column_vars[key] = var
            entry = ttk.Entry(mapping_frame, textvariable=var, width=6)
            entry.grid(row=row, column=1, padx=3, pady=2)
            self.setup_entry_widget_menu(entry)

        # Start row
        start_frame = ttk.Frame(left)
        start_frame.pack(fill='x', pady=5)
        ttk.Label(start_frame, text="Начать со строки:").pack(side='left')
        self.start_row_var = tk.IntVar(value=0)
        start_row_entry = ttk.Entry(start_frame, textvariable=self.start_row_var, width=6)
        start_row_entry.pack(side='left', padx=5)
        self.setup_entry_widget_menu(start_row_entry)

        ttk.Button(left, text="Выполнить парсинг", command=self.parse_table).pack(fill='x', pady=6)

        add_frame = ttk.LabelFrame(left, text="Добавить значение ко всем")
        add_frame.pack(fill='x', pady=5)
        self.add_field_var = tk.StringVar()
        self.add_field_combo = ttk.Combobox(add_frame, textvariable=self.add_field_var, state='readonly', values=list(PERSON_FIELDS_RUSSIAN_NAMES.values()))
        self.add_field_combo.pack(fill='x', padx=3, pady=3)
        self.add_value_var = tk.StringVar()
        add_value_entry = ttk.Entry(add_frame, textvariable=self.add_value_var)
        add_value_entry.pack(fill='x', padx=3, pady=3)
        self.setup_entry_widget_menu(add_value_entry)
        ttk.Button(add_frame, text="Добавить ко всем", command=self.add_additional_data).pack(fill='x', padx=3, pady=3)

        save_frame = ttk.Frame(left)
        save_frame.pack(fill='x', pady=5)
        ttk.Button(save_frame, text="Сохранить JSON", command=self.save_json).pack(fill='x', padx=0, pady=0)

        # --- Right: Previews (можно прокручивать) ---
        # Верхняя: предпросмотр таблицы
        table_preview_frame = ttk.LabelFrame(right, text="Предпросмотр таблицы")
        table_preview_frame.pack(fill='both', expand=True, pady=3)

        content = ttk.Frame(table_preview_frame)
        content.pack(fill='both', expand=True)
        content.rowconfigure(0, weight=1)
        content.columnconfigure(0, weight=1)

        self.table_preview = tk.Text(content, height=12, wrap='none', state='normal')
        self.table_preview.grid(row=0, column=0, sticky='nsew')

        table_scroll = ttk.Scrollbar(content, orient='vertical', command=self.table_preview.yview)
        table_scroll.grid(row=0, column=1, sticky='ns')

        h_scroll = ttk.Scrollbar(content, orient='horizontal', command=self.table_preview.xview)
        h_scroll.grid(row=1, column=0, sticky='ew')

        self.table_preview.config(yscrollcommand=table_scroll.set, xscrollcommand=h_scroll.set)

        # Нижняя: результаты парсинга
        result_frame = ttk.LabelFrame(right, text="Результат парсинга")
        result_frame.pack(fill='both', expand=True, pady=3)

        self.result_preview = tk.Text(result_frame, height=12, state='normal')
        self.result_preview.pack(side='left', fill='both', expand=True)
        result_scroll = ttk.Scrollbar(result_frame, orient='vertical', command=self.result_preview.yview)
        result_scroll.pack(side='right', fill='y')
        self.result_preview.config(yscrollcommand=result_scroll.set)

    # ---------------- Text Widget Context Menu & Shortcuts ----------------
    def setup_entry_widget_menu(self, entry_widget):
        """Create context menu for entry widget"""
        context_menu = tk.Menu(entry_widget, tearoff=0)
        context_menu.add_command(label="Копировать", command=lambda: self.copy_entry(entry_widget))
        context_menu.add_command(label="Вырезать", command=lambda: self.cut_entry(entry_widget))
        context_menu.add_command(label="Вставить", command=lambda: self.paste_entry(entry_widget))
        context_menu.add_separator()
        context_menu.add_command(label="Выделить всё", command=lambda: self.select_all_entry(entry_widget))
        
        def show_context_menu(event):
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
            return 'break'
        
        entry_widget.bind('<Button-3>', show_context_menu)
    
    def copy_entry(self, entry_widget):
        """Copy selected text from entry to clipboard"""
        try:
            text = entry_widget.selection_get()
            self.clipboard_clear()
            self.clipboard_append(text)
        except tk.TclError:
            pass
    
    def cut_entry(self, entry_widget):
        """Cut selected text from entry to clipboard"""
        try:
            text = entry_widget.selection_get()
            self.clipboard_clear()
            self.clipboard_append(text)
            entry_widget.delete('sel.first', 'sel.last')
        except tk.TclError:
            pass
    
    def paste_entry(self, entry_widget):
        """Paste text from clipboard to entry"""
        try:
            text = self.clipboard_get()
            entry_widget.insert(tk.INSERT, text)
            return 'break'  # Блокируем стандартное поведение
        except tk.TclError:
            pass
        return 'break'  # Даже если ошибка, блокируем стандартное поведение
    
    def select_all_entry(self, entry_widget):
        """Select all text in entry widget"""
        entry_widget.select_range(0, tk.END)
        entry_widget.icursor(tk.END)
    
    # ---------------- Actions ----------------
    def select_docx(self):
        path = filedialog.askopenfilename(filetypes=[("Word Documents", "*.docx")])
        if path:
            self.docx_path = path
            self.docx_label.config(text=path)

    def load_table(self):
        try:
            idx = self.table_index_var.get()
            if not self.docx_path:
                messagebox.showwarning("Внимание", "Сначала выберите .docx файл")
                return
            self.table_data = extract_docx_table(self.docx_path, idx)
            if not self.table_data:
                messagebox.showwarning("Внимание", "Таблица пустая")
                return

            # Сформируем превью с индексами столбцов и строк
            preview = []
            header = [" "] + [str(i) for i in range(len(self.table_data[0]))]
            preview.append(header)
            for r_idx, row in enumerate(self.table_data):
                preview.append([str(r_idx)] + row)

            self.table_preview.delete(1.0, tk.END)
            # используем широкую ширину, чтобы текст не был сильно завернут
            self.table_preview.insert(tk.END, matrix_to_string(preview, max_width=200))
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def add_additional_data(self):
        if not self.persons_list:
            messagebox.showwarning("Внимание", "Сначала выполните парсинг таблицы")
            return
        russian_name = self.add_field_var.get()
        value = self.add_value_var.get()
        if not russian_name:
            messagebox.showwarning("Внимание", "Выберите поле")
            return
        field = next((k for k, v in PERSON_FIELDS_RUSSIAN_NAMES.items() if v == russian_name), None)
        if not field:
            messagebox.showerror("Ошибка", "Неизвестное поле")
            return
        try:
            add_data_to_persons_list(self.persons_list, field, value)
            self.update_result_preview()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def parse_table(self):
        if not self.table_data:
            messagebox.showwarning("Внимание", "Таблица не загружена")
            return
        layout_kwargs = {k: v.get() for k, v in self.column_vars.items()}
        table_layout = TableLayout(**layout_kwargs)
        self.persons_list = parse_table_data(self.table_data, table_layout, self.start_row_var.get())
        self.update_result_preview()

    def update_result_preview(self):
        self.result_preview.delete(1.0, tk.END)
        self.result_preview.insert(tk.END, persons_list_to_string(self.persons_list))

    def save_json(self):
        path = filedialog.asksaveasfilename(filetypes=[("JSON files", "*.json")])
        if path:
            save_persons_to_json(path, self.persons_list)

    # ---------------- New Tab: Автозаполнение ----------------
    def create_autofill_tab(self):
        self.autofill_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.autofill_tab, text="Автозаполнение")

        left = ttk.Frame(self.autofill_tab, width=360)
        left.pack(side='left', fill='y', padx=10, pady=10)
        right = ttk.Frame(self.autofill_tab)
        right.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        # JSON loader
        json_frame = ttk.LabelFrame(left, text="JSON")
        json_frame.pack(fill='x', pady=5)
        ttk.Button(json_frame, text="Открыть JSON", command=self.on_button_load_json_autofill).pack(side='left', padx=5, pady=5)
        self.autofill_json_label = ttk.Label(json_frame, text="Файл не выбран", wraplength=240)
        self.autofill_json_label.pack(side='left', padx=5)

        # Current person controls (single-person preview above navigation)
        list_frame = ttk.LabelFrame(left, text="Текущий человек")
        list_frame.pack(fill='both', expand=False, pady=5)

        # Single-person preview (shows full information for the current person)
        single_preview_frame = ttk.Frame(list_frame)
        single_preview_frame.pack(fill='both', expand=True, padx=3, pady=(3,6))
        # increase height so info fits at once
        self.current_person_preview = tk.Text(single_preview_frame, height=14, state='normal', wrap='none')
        # self.setup_text_widget_menu(self.current_person_preview)
        # self.make_text_read_only(self.current_person_preview)
        sp_v = ttk.Scrollbar(single_preview_frame, orient='vertical', command=self.current_person_preview.yview)
        self.current_person_preview.configure(yscrollcommand=sp_v.set)
        sp_v.pack(side='right', fill='y')
        self.current_person_preview.pack(side='left', fill='both', expand=True)

        # Navigation (fixed-width label so buttons don't shift)
        idx_frame = ttk.Frame(list_frame)
        idx_frame.pack(fill='x', padx=3, pady=2)
        ttk.Button(idx_frame, text="◀", width=3, command=lambda: self.move_current_person_index(-1)).pack(side='left')
        self.current_index_var = tk.IntVar(value=0)
        # label centered between buttons (show index and name)
        self.current_label = ttk.Label(idx_frame, text="—", width=50, anchor='center')
        self.current_label.pack(side='left', padx=6, fill='x', expand=True)
        ttk.Button(idx_frame, text="▶", width=3, command=lambda: self.move_current_person_index(1)).pack(side='left')

        # Manual index entry to jump far without many clicks
        manual_frame = ttk.Frame(list_frame)
        manual_frame.pack(fill='x', padx=3, pady=(2,4))
        self.manual_index_var = tk.StringVar(value='1')
        ttk.Label(manual_frame, text="Индекс:").pack(side='left')
        manual_index_entry = ttk.Entry(manual_frame, textvariable=self.manual_index_var, width=6)
        manual_index_entry.pack(side='left', padx=4)
        self.setup_entry_widget_menu(manual_index_entry)
        ttk.Button(manual_frame, text="Перейти", command=self.on_button_go_to_person_index).pack(side='left')

        # Page controls
        page_frame = ttk.LabelFrame(left, text="Страница")
        page_frame.pack(fill='x', pady=5)
        self.page_url_var = tk.StringVar()
        page_url_entry = ttk.Entry(page_frame, textvariable=self.page_url_var, width=40)
        page_url_entry.pack(fill='x', padx=3, pady=3)
        self.setup_entry_widget_menu(page_url_entry)
        ttk.Button(page_frame, text="Открыть страницу", command=self.on_button_open_web_page).pack(fill='x', padx=3, pady=3)

        # Actions
        actions = ttk.LabelFrame(left, text="Действия")
        actions.pack(fill='x', pady=5)
        ttk.Button(actions, text="Заполнить данные", command=self.on_button_fill_info).pack(fill='x', padx=3, pady=3)
        ttk.Button(actions, text="Подтвердить", command=self.on_button_confirm).pack(fill='x', padx=3, pady=3)
        ttk.Button(actions, text="Подтвердить и заполнить", command=self.on_button_confirm_and_fill).pack(fill='x', padx=3, pady=3)


        # Right: preview of selected person / JSON
        preview_frame = ttk.LabelFrame(right, text="Предпросмотр JSON")
        preview_frame.pack(fill='both', expand=True)
        # content frame to hold text and vertical scrollbar
        content_preview = ttk.Frame(preview_frame)
        content_preview.pack(fill='both', expand=True)
        self.autofill_preview = tk.Text(content_preview, state='normal', wrap='none')
        v_scroll = ttk.Scrollbar(content_preview, orient='vertical', command=self.autofill_preview.yview)
        self.autofill_preview.configure(yscrollcommand=v_scroll.set)
        v_scroll.pack(side='right', fill='y')
        self.autofill_preview.pack(side='left', fill='both', expand=True)

        # Internal state for autofill
        self.auto_persons = []
        self.auto_driver = None

    def on_button_load_json_autofill(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not path:
            return
        try:
            persons = load_persons_from_json(path)
            self.auto_persons = persons
            self.autofill_json_label.config(text=path)
            # reset current index and update previews
            self.current_index_var.set(0)
            self.update_current_person_preview()
            self.update_autofill_preview()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def update_autofill_preview(self):
        self.autofill_preview.delete(1.0, tk.END)
        # always show full list preview here (JSON-like/persons list)
        try:
            self.autofill_preview.insert(tk.END, persons_list_to_string(self.auto_persons))
        except Exception:
            self.autofill_preview.insert(tk.END, "Нет данных")

    def update_current_person_preview(self):
        self.current_person_preview.delete(1.0, tk.END)
        if not self.auto_persons:
            self.current_label.config(text='—')
            self.current_person_preview.insert(tk.END, 'Нет данных')
        else:
            idx = self.current_index_var.get()
            if idx < 0:
                idx = 0
                self.current_index_var.set(0)
            if idx >= len(self.auto_persons):
                idx = len(self.auto_persons) - 1
                self.current_index_var.set(idx)
            p = self.auto_persons[idx]
            display = p.full_name if p.full_name else f"{p.last_name} {p.first_name}"
            self.current_label.config(text=f"{idx+1}/{len(self.auto_persons)} — {display}")
            # use existing formatter to show all fields
            try:
                from string_converter import person_to_string
                self.current_person_preview.insert(tk.END, person_to_string(p))
            except Exception:
                # fallback: simple dict
                self.current_person_preview.insert(tk.END, str(p.__dict__))

    def move_current_person_index(self, delta: int):
        if not self.auto_persons:
            return
        idx = self.current_index_var.get() + delta
        idx = max(0, min(len(self.auto_persons) - 1, idx))
        self.current_index_var.set(idx)
        self.update_current_person_preview()

    def on_button_go_to_person_index(self):
        if not self.auto_persons:
            messagebox.showwarning("Внимание", "Сначала загрузите JSON с людьми")
            return
        try:
            new_index = int(self.manual_index_var.get())
        except Exception:
            messagebox.showerror("Ошибка", "Индекс должен быть числом")
            return
        
        if new_index < 1:
            new_index = 1
        if new_index > len(self.auto_persons):
            new_index = len(self.auto_persons)
        
        self.current_index_var.set(new_index - 1)
        self.update_current_person_preview()

    def on_button_open_web_page(self):
        url = self.page_url_var.get()
        try:
            # open page in background to avoid blocking UI
            def _open():
                self.auto_driver = web.open_page(url)
            
            t = threading.Thread(target=_open, daemon=True)
            t.start()
        
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def on_button_fill_info(self):
        if not self.auto_driver:
            messagebox.showwarning("Внимание", "Сначала откройте страницу")
            return
        if not self.auto_persons:
            messagebox.showwarning("Внимание", "Сначала загрузите JSON с людьми")
            return
        person = self.auto_persons[self.current_index_var.get()]
        try:
            web.fill_person_form(self.auto_driver, person)
            self.update_current_person_preview()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def on_button_confirm(self):
        if not self.auto_driver:
            messagebox.showwarning("Внимание", "Сначала откройте страницу")
            return
        try:
            drv = self.auto_driver
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
                self.move_current_person_index(1)
            else:
                messagebox.showwarning("Внимание", "Кнопка подтверждения не найдена на странице")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))


    def on_button_confirm_and_fill(self):
        # Click confirm (submit current)
        self.on_button_confirm()
        # Move to next person
        self.move_current_person_index(1)
        # Fill next person's data
        self.on_button_fill_info()


if __name__ == "__main__":
    app = App()
    app.mainloop()
