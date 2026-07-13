import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

from backend.constants import DEFAULT_PERSON_TEMPLATE
from backend.to_string import matrix_to_string, persons_list_to_string
from backend.parsing import extract_docx_table, parse_table_data, add_data_to_persons_list
from backend.json_handling import save_to_json

class ParserTab:
    def __init__(self, parent, app):
        self.app = app
        self.main_tab = ttk.Frame(parent)
        
        self.docx_path: str = ""
        self.table_data: list[list[str]] = []
        self.persons_list: list = []
        self.template: dict[str, dict] = DEFAULT_PERSON_TEMPLATE
        
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
        self.table_index_var = tk.IntVar(value=1)
        table_index_entry = ttk.Entry(table_idx_frame, textvariable=self.table_index_var, width=6)
        self.app.context_menu.add_to_widget(table_index_entry)
        table_index_entry.pack(side='left', padx=5)
        ttk.Button(table_idx_frame, text="Выбрать таблицу", command=self.on_button_load_table).pack(side='left', padx=5)

        mapping_frame = ttk.LabelFrame(left, text="Соотнесение столбцов")
        mapping_frame.pack(fill='both', pady=5)

        self.column_vars = {}
        row_index: int = 0
        for field, mapping in self.template.items():
            if not mapping["show_in_ui"]:
                continue
            
            label = ttk.Label(mapping_frame, text=mapping["display_name"])
            label.grid(row=row_index, column=0, sticky='w', padx=3, pady=2)
            
            column_index_var = tk.StringVar(value="")
            self.column_vars[field] = column_index_var
            entry = ttk.Entry(mapping_frame, textvariable=column_index_var, width=6)
            self.app.context_menu.add_to_widget(entry)
            entry.grid(row=row_index, column=1, padx=3, pady=2)

            row_index += 1


        start_frame = ttk.Frame(left)
        start_frame.pack(fill='x', pady=5)
        ttk.Label(start_frame, text="Начать со строки:").pack(side='left')
        self.start_row_var = tk.IntVar(value=1)
        start_row_entry = ttk.Entry(start_frame, textvariable=self.start_row_var, width=6)
        self.app.context_menu.add_to_widget(start_row_entry)
        start_row_entry.pack(side='left', padx=5)

        ttk.Button(left, text="Извлечь данные из таблицы", command=self.on_button_parse_table).pack(fill='x', pady=6)

        add_to_all_frame = ttk.LabelFrame(left, text="Добавить значение ко всем")
        add_to_all_frame.pack(fill='x', pady=5)
        self.add_field_var = tk.StringVar()
        display_field_names: list[str] = [mapping["display_name"] for mapping in self.template.values()]
        self.add_to_all_combobox = ttk.Combobox(add_to_all_frame, textvariable=self.add_field_var, state='readonly', values=display_field_names)
        self.add_to_all_combobox.pack(fill='x', padx=3, pady=3)
        self.add_value_var = tk.StringVar()
        add_to_all_value_entry = ttk.Entry(add_to_all_frame, textvariable=self.add_value_var)
        self.app.context_menu.add_to_widget(add_to_all_value_entry)
        add_to_all_value_entry.pack(fill='x', padx=3, pady=3)
        ttk.Button(add_to_all_frame, text="Добавить ко всем", command=self.on_button_add_data_to_all).pack(fill='x', padx=3, pady=3)

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
        self.app.context_menu.add_to_widget(self.table_preview )
        self.table_preview.grid(row=0, column=0, sticky='nsew')

        table_scroll = ttk.Scrollbar(content, orient='vertical', command=self.table_preview.yview)
        table_scroll.grid(row=0, column=1, sticky='ns')

        h_scroll = ttk.Scrollbar(content, orient='horizontal', command=self.table_preview.xview)
        h_scroll.grid(row=1, column=0, sticky='ew')

        self.table_preview.config(yscrollcommand=table_scroll.set, xscrollcommand=h_scroll.set)

        result_frame = ttk.LabelFrame(right, text="Результат извлечения")
        result_frame.pack(fill='both', expand=True, pady=3)

        self.result_preview = tk.Text(result_frame, height=12, state='normal')
        self.app.context_menu.add_to_widget(self.result_preview)
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

            header = [""] + [str(col + 1) for col in range(cols)]
            formated_table_data.append(header)

            for i, row in enumerate(self.table_data):
                formated_table_data.append([str(i + 1)] + row)

        preview_text = matrix_to_string(formated_table_data)

        self.table_preview.delete(1.0, tk.END)
        self.table_preview.insert(tk.END, preview_text)


    def on_button_select_docx(self):
        if not self.app.check_license():
            return

        path = filedialog.askopenfilename(filetypes=[("DOCX files", "*.docx")])
        if path:
            self.table_index_var.set(1)
            self.docx_path = path
            self.docx_label.config(text=os.path.basename(path))
            self.on_button_load_table()


    def on_button_load_table(self):
        if not self.app.check_license():
            return
        if not self.docx_path:
            messagebox.showwarning("Внимание", "Сначала выберите .docx файл")
            return
        
        try:
            table_index = int(self.table_index_var.get())
            self.table_data = extract_docx_table(self.docx_path, table_index - 1)
            self.update_table_preview()
        except Exception:
            messagebox.showerror("Ошибка", "Не удалось загрузить таблицу")


    def on_button_parse_table(self):
        if not self.app.check_license():
            return

        if not self.table_data:
            messagebox.showwarning("Внимание", "Сначала загрузите таблицу")
            return
        

        # Update template column indices 
        for field, column_index_var in self.column_vars.items():
            try:
                column_index = int(column_index_var.get()) - 1
            except: 
                continue

            if column_index < 0 or column_index >= len(self.table_data[0]):
                messagebox.showerror("Ошибка", "Номер столбца выходит за рамки таблицы")
                return
            self.template[field]["column_index"] = column_index

        # Extract data from table
        try:
            start_row = self.start_row_var.get() - 1
            self.persons_list = parse_table_data(self.table_data, self.template, start_row)
            persons_preview = persons_list_to_string(self.persons_list, self.template)
            self.result_preview.delete(1.0, tk.END)
            self.result_preview.insert(tk.END, persons_preview)
        except:
            messagebox.showerror("Ошибка", "Не удалось извлечь данные из таблицы")


    def on_button_add_data_to_all(self):
        if not self.app.check_license():
            return

        if not self.persons_list:
            messagebox.showwarning("Внимание", "Сначала извлеките данные из таблицы")
            return
        
        russian_field = self.add_field_var.get()
        value = self.add_value_var.get()

        display_name_map = {mapping["display_name"]: field for field, mapping in self.template.items()}
        field_name = display_name_map[russian_field]
        
        if not field_name:
            messagebox.showerror("Ошибка", "Не удалось найти данное поле. Этого не должно было произойти, обратитесь к разработчику программы")
            return
        
        try:
            add_data_to_persons_list(self.persons_list, field_name, value)
            self.result_preview.delete(1.0, tk.END)
            self.result_preview.insert(tk.END, persons_list_to_string(self.persons_list, self.template))
        except Exception:
            messagebox.showerror("Ошибка", "Не удалось добавить данные")


    def on_button_save_json(self):
        if not self.app.check_license():
            return

        if not self.persons_list:
            messagebox.showwarning("Внимание", "Нет данных для сохранения")
            return
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not path:
            return
        try:
            save_to_json(path, {"template": self.template, "data": self.persons_list})
        except Exception:
            messagebox.showerror("Ошибка", "Не удалось сохранить файл")

