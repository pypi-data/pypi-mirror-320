import customtkinter as ctk
from tkinter import Misc
from CTkCalendar import CTkCalendar
import tkinter as tk
import datetime
from typing import Callable

class CTkStringVar(ctk.StringVar):
    def __init__(self, master: Misc | None = None, value: str | None = None, name: str | None = None):
        super().__init__(master=master, value=value, name=name)
    
    def set(self, value: str):
        """Define o valor da variável"""
        super().set(value)

    def get(self) -> str:
        """Retorna o valor atual da variável"""
        return super().get()

class CTkDateEntry(ctk.CTkFrame):
    def __init__(self,
                 master=None,
                 width: int = 140,
                 height: int = 28,
                 corner_radius: int | None = None,
                 bg_color: str | tuple = "transparent",
                 fg_color: str | tuple | None = None,
                 button_color: str | tuple | None = None,
                 button_hover_color: str | tuple | None = None,
                 text_color: str | tuple | None = None,
                 text_color_disabled: str | tuple | None = None,
                 font: tuple | ctk.CTkFont | None = None,
                 variable: CTkStringVar | None = None,  # Usando o CTkStringVar
                 state: str = tk.NORMAL,
                 command: Callable[[str], None] | None = None,
                 hover: bool = True,
                 justify: str = "left",  # Novo parâmetro justify
                 **kwargs: any):

        super().__init__(master, **kwargs)

        # Usa o CTkStringVar fornecido ou cria um novo se não for fornecido
        self.variable = variable if variable is not None else CTkStringVar(master)
        
        # Adiciona observador à variável para limpar o campo de entrada se o valor for vazio
        self.variable.trace_add('write', self.check_empty_value)

        # Campo de entrada para exibir a data
        self.entry = ctk.CTkEntry(self, textvariable=self.variable, 
                                  width=width, 
                                  height=height, 
                                  justify=justify,
                                  corner_radius=corner_radius,
                                  state=state)
        self.entry.grid(row=0, column=0, padx=0, pady=0, columnspan=2)

         # Aplica a fonte no Entry se fornecida
        if font:
            self.entry.configure(font=font)
        if fg_color:
            self.entry.configure(fg_color=fg_color)
        if bg_color:
            self.entry.configure(bg_color=bg_color)
        if text_color:
            self.entry.configure(text_color=text_color)
        if text_color_disabled:
            self.entry.configure(text_color_disabled=text_color_disabled)
        if command:
            self.entry.configure(command=command)
        
        # Botão para abrir o calendário
        self.calendar_button = ctk.CTkButton(self, text="📅", width=24, command=self.open_calendar, font=('noto sans', 12))
        #If para os parametros
        if button_color:
            self.calendar_button.configure(fg_color=button_color)
        if button_hover_color:
            self.calendar_button.configure(hover_color=button_hover_color)
        if hover:
            self.calendar_button.configure(hover=hover)
        self.calendar_button.grid(row=0, column=1, padx=0, pady=0, sticky='e')
        
        
    def open_calendar(self):
        """Abre o CTkCalendar em uma nova janela."""
        self.calendar_window = ctk.CTkToplevel(self)
        self.calendar_window.resizable(False, False)
        self.calendar_window.title("")
        self.calendar_window.iconbitmap()

        self.calendar_window.grab_set()
        self.calendar_window.lift()
        self.calendar_window.focus_force()

        x = self.winfo_rootx() + self.entry.winfo_x()
        y = self.winfo_rooty() + self.entry.winfo_height()
        self.calendar_window.geometry(f"+{x}+{y}")

        self.cal = CTkCalendar(self.calendar_window, command=self.set_date)
        self.cal.pack(padx=10, pady=10)

    def set_date(self, selected_date):
        """Define a data selecionada no campo de entrada."""
        self.variable.set(selected_date)
        self.calendar_window.destroy()
    
    def check_empty_value(self, *args):
        """Verifica se a variável está vazia e limpa a Entry se estiver."""
        if not self.variable.get():
            self.entry.delete(0, 'end')
