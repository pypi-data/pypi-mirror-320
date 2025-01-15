"""
Classes for Shell-Style package.
This module defines _BaseObject, Theme, Console, ProgressBar and Table.
"""

from time import sleep
from os import get_terminal_size
from abc import ABC
from typing import Any
from .constants import (
    FG_CYAN, FG_YELLOW, FG_RED, FG_GREEN, BOLD, DIM, ITALIC, 
    UNDERLINE, BLINK, INVERSE, HIDDEN, STRIKETHROUGH, 
    FG_BLACK, FG_WHITE, FG_BLUE, FG_MAGENTA, BG_BLACK, 
    BG_RED, BG_GREEN, BG_BLUE, BG_MAGENTA, BG_CYAN, 
    BG_WHITE, STOP, CENTER, RIGHT, LEFT, CLEAR, DEFAULT
)

# Set __all__
__all__ = ["Theme", "Console", "Table", "ProgressBar", "DEFAULT_THEME", "interpret_ssml"]

def interpret_ssml(text: str) -> str:
    """
    Interprets SSML (Shell-Style Markup Language) text into ANSI escape sequences for terminal styling.
    
    Args:
        text: str 
        
    Returns: str 
    """
    
    ssml_to_ansi = {
        "<@bold>": BOLD,
        "<@dim>": DIM,
        "<@italic>": ITALIC,
        "<@underline>": UNDERLINE,
        "<@blink>": BLINK,
        "<@inverse>": INVERSE,
        "<@hidden>": HIDDEN,
        "<@strikethrough>": STRIKETHROUGH,
        "<@fg_black>": FG_BLACK,
        "<@fg_red>": FG_RED,
        "<@fg_green>": FG_GREEN,
        "<@fg_yellow>": FG_YELLOW,
        "<@fg_blue>": FG_BLUE,
        "<@fg_magenta>": FG_MAGENTA,
        "<@fg_cyan>": FG_CYAN,
        "<@fg_white>": FG_WHITE,
        "<@bg_black>": BG_BLACK,
        "<@bg_red>": BG_RED,
        "<@bg_green>": BG_GREEN,
        "<@bg_blue>": BG_BLUE,
        "<@bg_magenta>": BG_MAGENTA,
        "<@bg_cyan>": BG_CYAN,
        "<@bg_white>": BG_WHITE,
        "<@stop>": STOP,
        "<@info>": FG_CYAN,
        "<@success>": FG_GREEN,
        "<@warning>": FG_YELLOW,
        "<@error>": FG_RED,
        "<@heading>": BOLD + UNDERLINE,
        "<@section>": INVERSE + UNDERLINE
    }

    for (ssml, ansi) in ssml_to_ansi.items():
        text = text.replace(ssml, ansi)

    return text

class _BaseObject(ABC):
    """
    Abstract Base Class for all other classes defined here.
    Defines the help method.
    
    Args: None
    """
    
    @classmethod
    def help(cls) -> str:
        return interpret_ssml(f"<@heading>{cls.__name__}<@stop>\n{cls.__doc__}")

class Theme(_BaseObject):
    """
    Class for themes. 
    
    Args:
        **styles
    """
    
    def __init__(self, **styles) -> None:
        self.__styles = styles
        
    @property
    def styles(self) -> dict[str, str]:
        return self.__styles
    
    @styles.setter
    def styles(self, styles: dict[str, str]) -> None:
        self.__styles.update(styles)
        
    def get_style(self, target: str) -> str:
        return self.__styles.get(target)
    
    def __getitem__(self, target: str) -> Any:
        return self.__styles.get(target)
    
    def __setitem__(self, style: str, value: str) -> None:
        self.__styles[style] = value

DEFAULT_THEME = Theme(
    info=FG_CYAN, warning=FG_YELLOW, error=FG_RED, success=FG_GREEN, bold=BOLD, dim=DIM, italic=ITALIC, 
    underline=UNDERLINE, blink=BLINK, inverse=INVERSE, hidden=HIDDEN, strikethrough=STRIKETHROUGH, 
    fg_black=FG_BLACK, fg_white=FG_WHITE, fg_green=FG_GREEN, fg_yellow=FG_YELLOW, fg_blue=FG_BLUE, 
    fg_magenta=FG_MAGENTA, fg_cyan=FG_CYAN, bg_black=BG_BLACK, bg_red=BG_RED, bg_blue=BG_BLUE, stop=STOP,
    bg_green=BG_GREEN, bg_magenta=BG_MAGENTA, bg_cyan=BG_CYAN, bg_white=BG_WHITE, default=DEFAULT,
    header=BOLD + UNDERLINE, section=INVERSE + UNDERLINE
    )

class Console(_BaseObject):
    """
    Console object on which text can be printed and input can be taken.

    Args:
        title: str, 
        theme: Theme = DEFAULT_THEME
    """
    
    def __init__(self, title: str, theme: Theme = DEFAULT_THEME, print_title: bool = True) -> None:
        self.__title = title
        self.__theme = theme
        
        if print_title:
            self.print_title()
        
    def print_title(self) -> None:
        self.write(f"@bold@underline{self.__title}@stop", alignment=CENTER)
        
    @property
    def theme(self) -> Theme:
        return self.__theme
    
    @theme.setter
    def theme(self, new: Theme) -> None:
        self.__theme = new
        
    @property
    def title(self) -> str:
        return self.__title
    
    @title.setter
    def title(self, new: str) -> None:
        self.__title = new
    
    def clear(self, print_title: bool = True) -> None:
        """
        Clear the terminal.
        
        Args:
            print_title: bool = True
            
        Returns: None
        """
        
        print(CLEAR, end="")
        if print_title:
            self.print_title()
        
    def log(self, *objects, end: str = f"{STOP}\n", sep: str = " ", 
            style: str = "default", alignment: str = LEFT) -> None:
        """
        Customized log method.
        
        Args: 
            *objects: Any, 
            end: str = f"{STOP}\\n",
            alignment: str = LEFT,
            sep: str = " ", 
            style: str = "default"
            
        Returns: None
        """
        
        print(
        interpret_ssml(self.__align_text(self.__theme.get_style(style) + "".join(map(str, objects)), alignment)), end=end, sep=sep
            )
            
    def write(self, *objects: Any, alignment: str = LEFT, end: str = f"{STOP}\n", 
              sep: str = " ", style: str = "default") -> None:
        """
        Customized print method.
        
        Args:
            *objects: Any,
            alignment: str, 
            end: str = STOP, 
            sep: str = "", 
            style: str
        
        Returns: None
        """
        
        print(
        interpret_ssml(self.__align_text(self.__theme.get_style(style) + "".join(map(str, objects)), alignment)), end=end, sep=sep
            )
        
    def prompt(self, *objects, end: str = STOP, style: str = "default") -> str:
        """
        Customized input method.
        
        Args:
            *objects: Any,
            end: str = STOP, 
            style: str
        
        Returns: str
        """
        
        try:
            text = input(interpret_ssml(self.__theme.get_style(style) + "".join(map(str, objects))) + end)
        
        except EOFError:
            return ""
        
        else:
            return text
    
    @staticmethod
    def __align_text(text: Any, alignment: str) -> str:
        """
        Private static method for text alignment.
        
        Args:
            text: Any, 
            alignment: str
        
        Returns: str 
        
        Raises: ValueError (if alignment is not valid)
        """
        
        width = get_terminal_size().columns
        
        if alignment == CENTER:
            padding = (width - len(text)) // 2
            return " " * padding + text + " " * (width - len(text) - padding)
        
        elif alignment == RIGHT:
            return (" " * (width - len(text)) + text).rstrip(" ")
        
        elif alignment == LEFT:
            return (text + " " * (width - len(text))).lstrip(" ")
        
        else:
            raise ValueError(f"Invalid argument for function 'Console.__align_text': {alignment}")
    
class ProgressBar(_BaseObject):
    """
    Class for representing basic progress bars.
    
    Args:
        values: int,
        theme: Theme = DEFAULT_THEME
        symbol: str = "-",
        delay: float = 1
    """
    
    def __init__(self, values: int, *, theme: Theme = DEFAULT_THEME, 
                 symbol: str = "-", delay: float = 1) -> None:
        self.__values = values
        self.__theme = theme
        self.__symbol = interpret_ssml(symbol)
        self.__delay = delay
        
    @property
    def values(self) -> int:
        return self.__values
    
    @values.setter
    def values(self, new: int) -> None:
        self.__values = new
        
    @property
    def theme(self) -> Theme:
        return self.__theme
    
    @theme.setter
    def theme(self, new: Theme) -> None:
        self.__theme = new
        
    @property
    def symbol(self) -> str:
        return self.__symbol
    
    @symbol.setter
    def symbol(self, new: str) -> None:
        self.__symbol = interpret_ssml(new)
        
    @property
    def delay(self) -> float:
        return self.__delay
    
    @delay.setter
    def delay(self, new: float) -> None:
        self.__delay = new
        
    def run(self, style: str = "default") -> None:
        """
        Run the progress bar.
        
        Args:
            style: str = "default",
            
        Returns: None
        """
        
        for _ in range(self.__values):
            print(self.__theme.get_style(style) + self.__symbol, end=STOP, flush=True)
            sleep(self.__delay)
            
class Table(_BaseObject):
    """
    Table class for representing data.
    
    Args: 
        columns: int = 0,
        theme: Theme = DEFAULT_THEME
    """
    
    def __init__(self, columns: int = 0, theme: Theme = DEFAULT) -> None:
        self.__columns = columns
        if columns < 0:
            self.__columns = 0
        self.__theme = theme
        self.__rows = 0
        self.__table = []
        
    def add_row(self, *objects: Any, style: str = "default") -> None:
        """
        Add a row to self.__table.
        
        Args:
            *objects: Any
            
        Returns: None
        """
        
        objects = list(objects)
        
        while len(objects) < self.__columns:
            objects.append(None)
            
        while len(objects) > self.__columns:
            objects.pop()
            
        for object in objects:
            object = interpret_ssml(self.__theme.get_style(style) + object + STOP)
            
        self.__table.append(objects)
        self.__rows += 1
        
    def del_row(self, index: int) -> None:
        """
        Delete a row in self.__table.
        
        Args:
            index: int
            
        Returns: None    
        """
        
        del self.__table[index]
        self.__rows -= 1
        
    def del_column(self, index: int) -> None:
        """
        Delete a column in self.__table.
        
        Args:
            index: int
            
        Returns: None
        """
        
        for row in self.__table:
            del row[index]
            
        self.__columns -= 1
        
    def add_column(self, placeholder: Any = "", style: str = "default") -> None:
        """
        Add a column in self.__table.
        
        Args:
            placeholder: Any = ""
            
        Returns: None
        """
        
        placeholder = interpret_ssml(self.__theme.get_style(style) + placeholder + STOP)
        
        for row in self.__table:
            row.append(placeholder)
        
        self.__columns += 1
            
    def get_column(self, row_index: int, column_index: int) -> Any:
        """
        Get the information in a column in self.__table.
        
        Args:
            row_index: int,
            column_index: int
            
        Returns: Any
        """
        
        return self.__table[row_index][column_index]
    
    def set_column(self, info: Any, row_index: int, column_index: int, style: str = "default") -> None:
        """
        Set the information in a column in self.__table.
        
        Args:
            info: Any,
            row_index: int,
            column_index: int
            
        Returns: None
        """
        
        self.__table[row_index][column_index] = interpret_ssml(self.__theme.get_style(style) + info + STOP)
        
    def get_row(self, index: int) -> list:
        """
        Returns a row in self.__table.
        
        Args:
            index: int
            
        Returns: list
        """
        
        return self.__table[index]
    
    def get_table(self) -> str:
        """
        Return a string representation of self.__table.
        
        Args: None
        
        Returns: str
        """
        
        return_str = ""
        
        for row in self.__table:
            return_str += "| " + " | ".join(str(cell) if cell is not None else "" for cell in row) + " |" + "\n"
            
        return return_str
    
    def display(self) -> None:
        print(self.get_table())
        
    def symbol_separated_values(self, symbol: str = ",") -> str:
        """
        Turn self.__table into a symbol separated format, like CSV, TSV, SSV or PSV.
        
        Args:
            symbol: str = ","
            
        Returns: str
        """
        
        text = ""
        
        for row in self.__table:
            for column in row: 
                text += f"\"{column}\"{symbol}"
                
            text += "\n"
            
        return text
    
    def load(self, path: str, symbol: str = ",") -> None:
        """
        Load self.__table into a file, typically a CSV, TSV, SSV or PSV.
        
        Args:
            path: str,
            symbol: str = ","
            
        Returns: None
        """
        
        with open(path, "w") as file:
            file.write(self.symbol_separated_values(symbol))
        
    @property
    def rows(self) -> int:
        return self.__rows
    
    @property
    def columns(self) -> int:
        return self.__columns
    
    @property
    def table(self) -> list[list[Any]]:
        return self.__table
    
    @property
    def theme(self) -> Theme:
        return self.__theme
    
    @theme.setter
    def theme(self, new: Theme) -> None:
        self.__theme = new
    