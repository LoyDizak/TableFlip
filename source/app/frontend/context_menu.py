import tkinter as tk


class ContextMenu:
    """Класс для создания контекстного меню для виджетов ввода"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
    
    def add_to_widget(self, entry_widget):
        """Добавить контекстное меню к виджету ввода"""
        context_menu = tk.Menu(entry_widget, tearoff=0)
        context_menu.add_command(label="Копировать", command=lambda: self._copy_entry(entry_widget))
        context_menu.add_command(label="Вырезать", command=lambda: self._cut_entry(entry_widget))
        context_menu.add_command(label="Вставить", command=lambda: self._paste_entry(entry_widget))
        context_menu.add_separator()
        context_menu.add_command(label="Выделить всё", command=lambda: self._select_all_entry(entry_widget))

        def show_context_menu(event):
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
            return 'break'
        
        entry_widget.bind('<Button-3>', show_context_menu)


    def _copy_entry(self, entry_widget):
        """Копировать выделенный текст в буфер обмена"""
        try:
            text = entry_widget.selection_get()
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
        except tk.TclError:
            pass


    def _cut_entry(self, entry_widget):
        """Вырезать выделенный текст в буфер обмена"""
        try:
            text = entry_widget.selection_get()
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            entry_widget.delete('sel.first', 'sel.last')
        except tk.TclError:
            pass


    def _paste_entry(self, entry_widget):
        """Вставить текст из буфера обмена"""
        try:
            text = self.root.clipboard_get()
            entry_widget.insert(tk.INSERT, text)
            return 'break'
        except tk.TclError:
            pass
        return 'break'


    def _select_all_entry(self, entry_widget):
        """Выделить весь текст в виджете"""
        entry_widget.select_range(0, tk.END)
        return 'break'