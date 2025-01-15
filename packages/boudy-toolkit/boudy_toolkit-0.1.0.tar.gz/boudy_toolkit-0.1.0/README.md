# Advanced Python GUI Toolkit

A powerful yet simple toolkit that supercharges your GUI development in Python by providing high-level components and utilities to create stunning applications with minimal code. Built on top of tkinter, this toolkit offers themes, responsive layouts, data validation, and advanced widgets out of the box.

## Key Features

* **Pre-built Window Templates** - Create windows with common layouts in one line
* **Theme System** - Built-in light, dark and custom themes
* **Advanced Widgets** - Data grids, forms, charts, and tabbed interfaces
* **Data Validation** - Email, phone, date validators included
* **Database Integration** - Simple SQLite wrapper included
* **Async Operations** - Background tasks with progress indicators
* **File Operations** - JSON and CSV handling utilities

## Installation

```bash
pip install advanced-gui-toolkit
```

## Quick Examples

### Create a Simple Window
```python
from advanced_gui_toolkit import simplegui

# Create a basic window
simplegui(size="400x300", title="My App")
```

### Create a Form
```python
from advanced_gui_toolkit import create_form

def handle_submit(data):
    print(f"Form submitted with data: {data}")

# Create a form with automatic layout
fields = ["Name", "Email", "Phone"]
create_form(fields, handle_submit, size="400x300", title="Registration")
```

### Display Data in a Grid
```python
from advanced_gui_toolkit import create_data_grid

# Sample data
users = [
    ["John Doe", "john@email.com", "123-456-7890"],
    ["Jane Smith", "jane@email.com", "098-765-4321"]
]

# Create a scrollable data grid
create_data_grid(
    data=users,
    headers=["Name", "Email", "Phone"],
    size="600x400",
    title="User List"
)
```

### Create a Themed Application
```python
from advanced_gui_toolkit import BaseWindow, Theme

# Create a window with dark theme
window = BaseWindow(
    size="800x600",
    title="Themed App",
    theme=Theme.DARK
)

# Add widgets and run
window.run()
```

### Data Validation
```python
from advanced_gui_toolkit import Validator

# Validate email
is_valid = Validator.is_email("user@example.com")  # Returns True

# Validate phone
is_valid = Validator.is_phone("+1234567890")  # Returns True

# Validate date
is_valid = Validator.is_date("2024-01-13")  # Returns True
```

### Create Charts (requires matplotlib)
```python
from advanced_gui_toolkit import create_chart

# Create a bar chart
data = [10, 25, 15, 30]
create_chart(data, chart_type="bar", title="Sales Data")
```

### Handle Background Tasks
```python
from advanced_gui_toolkit import AsyncTask
import time

def long_running_task():
    time.sleep(2)  # Simulate work
    return "Task completed!"

def on_complete(result):
    print(result)

# Run task with progress indicator
task = AsyncTask(long_running_task, on_complete)
task.run()
```

### Create Tabbed Interface
```python
from advanced_gui_toolkit import create_tabbed_interface

def tab1_content(frame):
    # Add widgets to frame
    tk.Label(frame, text="Tab 1 Content").pack()

def tab2_content(frame):
    # Add widgets to frame
    tk.Label(frame, text="Tab 2 Content").pack()

tabs = {
    "Info": tab1_content,
    "Settings": tab2_content
}

create_tabbed_interface(tabs, title="Tabbed App")
```

## Requirements

* Python 3.x
* tkinter (included in standard Python distribution)
* matplotlib (optional, for charts)

## Optional Features

* **Charts**: Install matplotlib for charting capabilities
* **Custom Themes**: Create your own color themes
* **Database**: SQLite support included, extensible for other databases

## Documentation

For full documentation, visit [documentation link].

## Support

For bugs, feature requests or questions, please visit our [issue tracker].

## License

This project is licensed under the MIT License - see the LICENSE file for details.