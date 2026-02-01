import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

from backend.data import TableLayout, PERSON_FIELDS_RUSSIAN_NAMES
from backend.string_converter import matrix_to_string, persons_list_to_string
from backend.parser import extract_docx_table, parse_table_data, add_data_to_persons_list
from backend.json_handler import save_persons_to_json, load_persons_from_json


class ParserTab:
    def __init__(self, parent, app):
        self.app = app
        self.main_tab = ttk.Frame(parent)
        
        self.docx_path = ""
        self.table_data = []
        self.persons_list = []
        
        self.create_parser_tab()
    
    def create_parser_tab(self):
        left = ttk.Frame(self.main_tab, width=420)
        left.pack(side='left', fill='y', padx=10, pady=10)

        right = ttk.Frame(self.main_tab)
        right.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        file_frame = ttk.LabelFrame(left, text="Документ")
        file_frame.pack(fill='x', pady=5)

        ttk.Button(file_frame, text="Выбрать файл", command=self.on_button_select_docx).pack(side='left', padx=5, pady=5)
        self.docx_label = ttk.Label(file_frame, text="Файл не выбран", wraplength=150)
        self.docx_label.pack(side='left', padx=5)

        table_idx_frame = ttk.Frame(left)
        table_idx_frame.pack(fill='x', pady=5)
        ttk.Label(table_idx_frame, text="Номер таблицы:").pack(side='left')
        self.table_index_var = tk.IntVar(value=0)
        table_index_entry = ttk.Entry(table_idx_frame, textvariable=self.table_index_var, width=6)
        table_index_entry.pack(side='left', padx=5)
        ttk.Button(table_idx_frame, text="Выбрать таблицу", command=self.on_button_load_table).pack(side='left', padx=5)

        mapping_frame = ttk.LabelFrame(left, text="Соответствие столбцов")
        mapping_frame.pack(fill='both', pady=5)

        self.column_vars = {}
        mapping_keys = [k for k in PERSON_FIELDS_RUSSIAN_NAMES.keys() if k not in ("last_name", "first_name", "middle_name")]
        for row, key in enumerate(mapping_keys):
            label_text = PERSON_FIELDS_RUSSIAN_NAMES[key]
            lbl = ttk.Label(mapping_frame, text=label_text)
            lbl.grid(row=row, column=0, sticky='w', padx=3, pady=2)
            column_index_var = tk.StringVar(value="")
            self.column_vars[key] = column_index_var
            entry = ttk.Entry(mapping_frame, textvariable=column_index_var, width=6)
            entry.grid(row=row, column=1, padx=3, pady=2)

        start_frame = ttk.Frame(left)
        start_frame.pack(fill='x', pady=5)
        ttk.Label(start_frame, text="Начать со строки:").pack(side='left')
        self.start_row_var = tk.IntVar(value=0)
        start_row_entry = ttk.Entry(start_frame, textvariable=self.start_row_var, width=6)
        start_row_entry.pack(side='left', padx=5)

        ttk.Button(left, text="Извлечь данные из таблицы", command=self.on_button_parse_table).pack(fill='x', pady=6)

        add_frame = ttk.LabelFrame(left, text="Добавить значение ко всем")
        add_frame.pack(fill='x', pady=5)
        self.add_field_var = tk.StringVar()
        self.add_field_combo = ttk.Combobox(add_frame, textvariable=self.add_field_var, state='readonly', values=list(PERSON_FIELDS_RUSSIAN_NAMES.values()))
        self.add_field_combo.pack(fill='x', padx=3, pady=3)
        self.add_value_var = tk.StringVar()
        add_value_entry = ttk.Entry(add_frame, textvariable=self.add_value_var)
        add_value_entry.pack(fill='x', padx=3, pady=3)
        ttk.Button(add_frame, text="Добавить ко всем", command=self.on_button_add_data_to_all).pack(fill='x', padx=3, pady=3)

        save_frame = ttk.Frame(left)
        save_frame.pack(fill='x', pady=5)
        ttk.Button(save_frame, text="Сохранить данные", command=self.on_button_save_json).pack(fill='x', padx=0, pady=0)

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

        result_frame = ttk.LabelFrame(right, text="Результат извлечения данных")
        result_frame.pack(fill='both', expand=True, pady=3)

        self.result_preview = tk.Text(result_frame, height=12, state='normal')
        self.result_preview.pack(side='left', fill='both', expand=True)
        result_scroll = ttk.Scrollbar(result_frame, orient='vertical', command=self.result_preview.yview)
        result_scroll.pack(side='right', fill='y')
        self.result_preview.config(yscrollcommand=result_scroll.set)


    def load_table(self, table_index: int):
        try:
            self.table_data = extract_docx_table(self.docx_path, table_index)
        except Exception:
            messagebox.showerror("Ошибка", "Не удалось загрузить таблицу")


    def update_table_preview(self):
        formated_table_data = []

        if self.table_data:
            cols = len(self.table_data[0])

            header = [""] + [str(col) for col in range(cols)]
            formated_table_data.append(header)

            for i, row in enumerate(self.table_data):
                formated_table_data.append([str(i)] + row)

        preview_text = matrix_to_string(formated_table_data)

        self.table_preview.delete(1.0, tk.END)
        self.table_preview.insert(tk.END, preview_text)


    def on_button_select_docx(self):
        path = filedialog.askopenfilename(filetypes=[("DOCX files", "*.docx")])
        if path:
            self.table_index_var.set(0)
            self.docx_path = path
            self.docx_label.config(text=os.path.basename(path))
            self.on_button_load_table()


    def on_button_load_table(self):
        if not self.docx_path:
            messagebox.showwarning("Внимание", "Сначала выберите .docx файл")
            return
        try:
            table_index = int(self.table_index_var.get())
            self.table_data = extract_docx_table(self.docx_path, table_index)
            self.update_table_preview()
        except Exception:
            messagebox.showerror("Ошибка", "Не удалось загрузить таблицу")


    def on_button_parse_table(self):
        if not self.table_data:
            messagebox.showwarning("Внимание", "Сначала загрузите таблицу")
            return
        
        try:
            layout = TableLayout()
            for key, column_index_var in self.column_vars.items():
                if column_index_var.get().isspace() or column_index_var.get() == "":
                    continue

                column_index = int(column_index_var.get())

                if column_index < 0 or column_index >= len(self.table_data[0]):
                    messagebox.showerror("Ошибка", "Номер столбца выходит за рамки таблицы")
                    return

                setattr(layout, key, column_index)
        except Exception:
            messagebox.showerror("Ошибка", "Неверно указан номер столбца")
            return

        try:
            start_row = self.start_row_var.get()
            self.persons_list = parse_table_data(self.table_data, layout, start_row)
            out = persons_list_to_string(self.persons_list)
            self.result_preview.delete(1.0, tk.END)
            self.result_preview.insert(tk.END, out)
        except Exception:
            messagebox.showerror("Ошибка", "Не удалось извлечь данные из таблицы")


    def on_button_add_data_to_all(self):
        if not self.persons_list:
            messagebox.showwarning("Внимание", "Сначала извлеките данные из таблицы")
            return
        
        russian_field = self.add_field_var.get()
        value = self.add_value_var.get()
        
        field_name = None
        for eng_key, rus_val in PERSON_FIELDS_RUSSIAN_NAMES.items():
            if rus_val == russian_field:
                field_name = eng_key
                break
        
        if not field_name:
            messagebox.showerror("Ошибка", "Неизвестное поле")
            return
        
        try:
            add_data_to_persons_list(self.persons_list, field_name, value)
            self.result_preview.delete(1.0, tk.END)
            self.result_preview.insert(tk.END, persons_list_to_string(self.persons_list))
        except Exception:
            messagebox.showerror("Ошибка", "Не удалось добавить данные")


    def on_button_save_json(self):
        if not self.persons_list:
            messagebox.showwarning("Внимание", "Нет данных для сохранения")
            return
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not path:
            return
        try:
            save_persons_to_json(path, self.persons_list)
        except Exception:
            messagebox.showerror("Ошибка", "Не удалось сохранить файл")

