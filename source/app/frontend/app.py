import tkinter as tk
from tkinter import ttk, messagebox

from backend.data import APP_NAME, PUBLIC_KEY
from backend.licensing import LicenseSystem

from frontend.parser_tab import ParserTab
from frontend.autofill_tab import AutofillTab
from frontend.activation_dialog import ActivationDialog
from frontend.context_menu import ContextMenu


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME + "   |   Автор: Артём Всяких")
        self.geometry("1200x670")

        self.license_system = LicenseSystem(APP_NAME, PUBLIC_KEY)
        self.context_menu = ContextMenu(self)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)

        self.parser_tab = ParserTab(self.notebook, self)
        self.notebook.add(self.parser_tab.main_tab, text="Извлечение данных")

        self.autofill_tab = AutofillTab(self.notebook, self)
        self.notebook.add(self.autofill_tab.autofill_tab, text="Автозаполнение")

        self.activation_dialog = ActivationDialog(self, self.license_system)

        if not self.license_system.is_system_activated(True):
            self.activation_dialog.show()


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