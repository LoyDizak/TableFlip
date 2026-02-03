import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from backend.licensing import LicenseSystem

class ActivationDialog:
    def __init__(self, parent: tk.Tk, license_system: LicenseSystem):
        self.parent: tk.Tk = parent
        self.license_system: LicenseSystem = license_system
        
        self.dialog: tk.Toplevel = tk.Toplevel(self.parent)
        self.dialog.title("Активация программы")
        self.dialog.geometry("420x250")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)

        tk.Label(self.dialog, text="Активация программы", font=("Arial", 13, "bold")).pack(pady=(15, 10))
        
        tk.Label(self.dialog, font=("Arial", 10), wraplength=380, justify="center",
            text=(
                "Пожалуйста, введите ключ активации.\n"
                "Если у вас его нет - обратитесь к автору программы "
                "и предоставьте ему уникальный идентификатор."
            )
        ).pack(padx=20, pady=(0, 15))

        hwid_frame = tk.Frame(self.dialog)
        hwid_frame.pack(padx=20, pady=(0, 15), fill="x")

        tk.Label(hwid_frame, text="Уникальный идентификатор:", font=("Arial", 10)).pack(anchor="w")

        hwid_row = tk.Frame(hwid_frame)
        hwid_row.pack(fill="x", pady=(5, 0))

        hwid_var = tk.StringVar(value=self.license_system.get_hardware_id())
        ttk.Entry(hwid_row, textvariable=hwid_var, state="readonly").pack(side="left", fill="x", expand=True)

        ttk.Button(hwid_row, text="Копировать", command=lambda: self._copy_hwid(hwid_var.get()), width=12).pack(side="right", padx=(8, 0))

        btn_frame_open_key_file = tk.Frame(self.dialog)
        btn_frame_open_key_file.pack(padx=20, pady=(8, 15), fill="x")
        ttk.Button(btn_frame_open_key_file, text="Открыть файл с ключом", command=self._open_license_file).pack(anchor="center")

        
    def show(self):
        self.dialog.update_idletasks() 

        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()

        window_width = 420
        window_height = 250

        x = (screen_width - window_width)  // 2
        y = (screen_height - window_height) // 2

        self.dialog.geometry(f"+{x}+{y}")

        self.parent.wait_window(self.dialog)


    def _copy_hwid(self, hwid):
        self.parent.clipboard_clear()
        self.parent.clipboard_append(hwid)


    def _open_license_file(self):
        file_path = filedialog.askopenfilename(
            title="Выберите файл лицензии",
            filetypes=[("License files", "*.key")],
            parent=self.dialog
        )
        
        if not file_path:
            return

        try:
            with open(file_path, 'r') as f:
                entered_key = f.read().strip()
            
            if self.license_system.is_license_key_valid(entered_key):
                self.license_system.set_license_key(entered_key)
                self.dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Ключ недействителен", parent=self.dialog)
        except Exception:
            messagebox.showerror("Ошибка", f"Не удалось прочитать файл", parent=self.dialog)