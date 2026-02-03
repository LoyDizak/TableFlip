import tkinter as tk
from tkinter import ttk, messagebox

from backend.data import APP_NAME, PUBLIC_KEY
from backend.licensing import LicenseSystem

from frontend.parser_tab import ParserTab
from frontend.autofill_tab import AutofillTab
from frontend.activation_dialog import ActivationDialog


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME + "   |   Автор: Артём Всяких")
        self.geometry("1200x670")

        self.license_system = LicenseSystem(APP_NAME, PUBLIC_KEY)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)

        self.parser_tab = ParserTab(self.notebook, self)
        self.notebook.add(self.parser_tab.main_tab, text="Извлечение данных")

        self.autofill_tab = AutofillTab(self.notebook, self)
        self.notebook.add(self.autofill_tab.autofill_tab, text="Автозаполнение")

        self.activation_dialog = ActivationDialog(self, self.license_system)

        if not self.license_system.is_system_activated(True):
            self.activation_dialog.show()


    def add_context_menu_to_widget(self, entry_widget):
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
            return 'break'
        except tk.TclError:
            pass
        return 'break'
    

    def select_all_entry(self, entry_widget):
        """Select all text in entry widget"""
        entry_widget.select_range(0, tk.END)
        return 'break'


    def check_license(self) -> bool:
        """Проверяет активацию лицензии"""
        if not self.license_system.is_system_activated(True):
            messagebox.showwarning(
                "Внимание", 
                "Данная версия программы не активирована.\n"
                "Пожалуйста, обратитесь к автору программы чтобы получить ключ."
            )
            return False
        else:
            return True