# Basic colors

This Python module provides you with:
- set of variables that you can use to **color** your text in terminal,
- **logging** like messages with or without icons,
- **verbose** on/off printing.

## Installation
You can install the module using pip:
```bash
pip install basic-colors
```

## Usage
Module `basic_colors` provides you with a set of variables that you can use to color your text in terminal.

### Colored text
```python
from basic_colors import *

print(Blue + "Ahoj" + Reset)
```

### Logging like messages
```python
from basic_colors import enable_icons, print_info, print_warning, print_error, verbose_print, 

enable_icons(True)
print_info("This is an info message.")
print_warning("This is a warning message.")
print_success("This is a success message.")
print_error("This is an error message.", False)
```

```Bash
 ℹ️  Info: This is an info message.     
⚠️ Warning: This is a warning message.
✅ Success: This is a success message.  
❌ Error: This is an error message.
```
*(in color)*

### Verbose print
The `set_verbose(True)` command enables verbose printing. If you want to print a message only in verbose mode, use the `verbose_print()` function.

```python
from basic_colors import set_verbose, verbose_print

set_verbose(False)
verbose_print("This is a non-verbose message.")
set_verbose(True)
verbose_print("This is a verbose message.")
```

## Sources:
- [stackoverflow.com](https://stackoverflow.com/questions/287871/how-do-i-print-colored-text-to-the-terminal)
