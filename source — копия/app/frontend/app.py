import tkinter as tk
from tkinter import ttk, messagebox

from backend.data import APP_NAME, PUBLIC_KEY
from backend.licensing import LicenseSystem

from frontend.parser_tab import ParserTab
from frontend.autofill_tab import AutofillTab

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME + "   |   Автор: Артём Всяких")
        self.geometry("1200x670")

        self.license_system = LicenseSystem(APP_NAME, PUBLIC_KEY)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)

        # Create parser tab
        self.parser_tab = ParserTab(self.notebook, self)
        self.notebook.add(self.parser_tab.main_tab, text="Извлечение данных")

        # Create autofill tab
        self.autofill_tab = AutofillTab(self.notebook, self)
        self.notebook.add(self.autofill_tab.autofill_tab, text="Автозаполнение")

        if not self.license_system.is_system_activated():
            self.show_license_dialog()

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
    

    def show_license_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Активация программы")
        dialog.geometry("420x300")
        dialog.resizable(False, False)

        tk.Label(dialog, text="Активация программы", font=("Arial", 13, "bold")).pack(pady=(15, 10))
        tk.Label(dialog, font=("Arial", 10), wraplength=380, justify="center",
            text=(
                "Пожалуйста, введите ключ активации.\n"
                "Если у вас его нет - обратитесь к автору программы "
                "и предоставьте ему уникальный идентификатор."
            )).pack(padx=20, pady=(0, 15))

        hwid_frame = tk.Frame(dialog)
        hwid_frame.pack(padx=20, pady=(0, 15), fill="x")

        tk.Label(hwid_frame, text="Уникальный идентификатор:", font=("Arial", 10)).pack(anchor="w")

        hwid_row = tk.Frame(hwid_frame)
        hwid_row.pack(fill="x", pady=(5, 0))

        hwid_var = tk.StringVar(value=self.license_system.get_hardware_id())
        ttk.Entry( hwid_row, textvariable=hwid_var, state="readonly").pack(side="left", fill="x", expand=True)

        def copy_hwid():
            self.clipboard_clear()
            self.clipboard_append(hwid_var.get())
        ttk.Button(hwid_row, text="Копировать", command=copy_hwid, width=12).pack(side="right", padx=(8, 0))

        tk.Label(dialog, text="Ключ активации:", font=("Arial", 10)).pack(anchor="w", padx=20)

        key_frame = tk.Frame(dialog)
        key_frame.pack(padx=20, pady=(5, 15), fill="x")

        key_var = tk.StringVar()
        key_entry = ttk.Entry(key_frame, textvariable=key_var)
        key_entry.pack(side="left", fill="x", expand=True)
        key_entry.focus()

        def paste_key():
            key_entry.delete(0, tk.END)
            key_entry.insert(0, self.clipboard_get())
        ttk.Button(key_frame, text="Вставить", command=paste_key, width=12).pack(side="right", padx=(8, 0))

        # ----- Кнопки -----
        def on_confirm():
            entered_key = key_var.get().strip()
            if not entered_key:
                messagebox.showwarning("Внимание", "Введите ключ активации.", parent=dialog)
                return
            if self.license_system.is_license_key_valid(entered_key):
                self.license_system.set_license_key(entered_key)
                dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Ключ недействителен", parent=dialog)


        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=(0, 15))

        ttk.Button(btn_frame, text="Подтвердить", command=on_confirm, width=15).pack(side="left", padx=8)
        ttk.Button(btn_frame, text="Отмена", command=dialog.destroy, width=15).pack(side="right", padx=8)

        # ----- Модальность -----
        dialog.grab_set()
        self.wait_window(dialog)



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
            return 'break'
        except tk.TclError:
            pass
        return 'break'
    
    def select_all_entry(self, entry_widget):
        """Select all text in entry widget"""
        entry_widget.select_range(0, tk.END)
        return 'break'

    def check_license(self) -> bool:
        if not self.license_system.is_system_activated():
            messagebox.showwarning("Внимание", "Данная версия программы не активирована.\n" \
                                               "Пожалуйста, обратитесь к автору программы чтобы получить ключ.")
            return False
        else:
            return True