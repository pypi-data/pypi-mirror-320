# boudy_toolkit module 

import tkinter as tk
from tkinter import ttk, messagebox, colorchooser, filedialog
import json
import sqlite3
import threading
from datetime import datetime
import csv
import re

# Module level variables
_main_root = None
_app_instance = None

class Theme:
    """Predefined color themes for GUI applications"""
    DARK = {
        'bg': '#2E2E2E',
        'fg': '#FFFFFF',
        'button': '#404040',
        'highlight': '#505050'
    }
    LIGHT = {
        'bg': '#F0F0F0',
        'fg': '#000000',
        'button': '#E0E0E0',
        'highlight': '#D0D0D0'
    }
    BLUE = {
        'bg': '#2C3E50',
        'fg': '#ECF0F1',
        'button': '#3498DB',
        'highlight': '#2980B9'
    }

def get_root():
    """Get the current root window"""
    global _main_root
    if _main_root is None or not _main_root.winfo_exists():
        raise RuntimeError("Application not initialized. Call initialize() first.")
    return _main_root

def initialize(title="Application", size="800x600", theme=Theme.LIGHT):
    """Initialize the main application window"""
    global _main_root, _app_instance
    
    if _main_root is not None and _main_root.winfo_exists():
        _main_root.destroy()
    
    _main_root = tk.Tk()
    _main_root.title(title)
    _main_root.geometry(size)
    
    # Apply theme
    style = ttk.Style()
    style.configure('TFrame', background=theme['bg'])
    style.configure('TLabel', background=theme['bg'], foreground=theme['fg'])
    style.configure('TButton', background=theme['button'])
    _main_root.configure(bg=theme['bg'])
    
    return _main_root

def run():
    """Start the application main loop"""
    root = get_root()
    root.mainloop()

def create_form(fields, callback, title="Form", parent=None):
    """Create a form with specified fields and callback"""
    parent = parent or get_root()
    frame = ttk.Frame(parent)
    frame.pack(expand=True, fill='both', padx=10, pady=10)
    
    entries = {}
    
    def submit():
        data = {field: entries[field].get() for field in fields}
        callback(data)
        
    for field in fields:
        field_frame = ttk.Frame(frame)
        field_frame.pack(fill='x', padx=5, pady=5)
        
        label = ttk.Label(field_frame, text=field)
        label.pack(side='left')
        
        entry = ttk.Entry(field_frame)
        entry.pack(side='right', expand=True, fill='x')
        entries[field] = entry
    
    submit_btn = ttk.Button(frame, text="Submit", command=submit)
    submit_btn.pack(pady=10)
    
    return frame

def create_data_grid(data, headers=None, title="Data Grid", parent=None):
    """Create a scrollable data grid"""
    parent = parent or get_root()
    frame = ttk.Frame(parent)
    frame.pack(expand=True, fill='both')
    
    tree = ttk.Treeview(frame)
    tree.pack(expand=True, fill='both')
    
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    vsb.pack(side='right', fill='y')
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    hsb.pack(side='bottom', fill='x')
    
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    if headers:
        tree["columns"] = headers
        for header in headers:
            tree.heading(header, text=header)
    elif data and len(data) > 0:
        headers = [f"Column {i}" for i in range(len(data[0]))]
        tree["columns"] = headers
        for header in headers:
            tree.heading(header, text=header)
    
    for row in data:
        tree.insert("", "end", values=row)
    
    return frame

def create_chart(data, chart_type="bar", title="Chart", labels=None, parent=None):
    """Create a simple chart using matplotlib"""
    try:
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        
        parent = parent or get_root()
        frame = ttk.Frame(parent)
        frame.pack(expand=True, fill='both')
        
        fig, ax = plt.subplots()
        
        if chart_type == "bar":
            ax.bar(range(len(data)), data)
        elif chart_type == "line":
            ax.plot(data)
        elif chart_type == "pie":
            ax.pie(data, labels=labels if labels else [f"Slice {i}" for i in range(len(data))])
        
        if labels and chart_type != "pie":
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels)
        
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill='both')
        
        return frame
    except ImportError:
        messagebox.showerror("Error", "matplotlib is required for charts")
        return ttk.Frame(parent)

def create_menu_bar(menu_config, parent=None):
    """Create a menu bar from configuration"""
    parent = parent or get_root()
    menubar = tk.Menu(parent)
    
    for menu_name, items in menu_config.items():
        menu = tk.Menu(menubar, tearoff=0)
        for item in items:
            if item == '-':
                menu.add_separator()
            else:
                label, command = item
                menu.add_command(label=label, command=command)
        menubar.add_cascade(label=menu_name, menu=menu)
    
    parent.config(menu=menubar)
    return menubar

def create_tabbed_interface(tabs, title="Tabbed Interface", parent=None):
    """Create a tabbed interface"""
    parent = parent or get_root()
    frame = ttk.Frame(parent)
    frame.pack(expand=True, fill='both')
    
    notebook = ttk.Notebook(frame)
    notebook.pack(expand=True, fill='both')
    
    for tab_name, content in tabs.items():
        tab_frame = ttk.Frame(notebook)
        content(tab_frame)
        notebook.add(tab_frame, text=tab_name)
    
    return frame

def create_dialog(message, dialog_type="info", title=None, parent=None):
    """Create various types of dialog boxes"""
    parent = parent or get_root()
    if dialog_type == "info":
        return messagebox.showinfo(title or "Information", message, parent=parent)
    elif dialog_type == "warning":
        return messagebox.showwarning(title or "Warning", message, parent=parent)
    elif dialog_type == "error":
        return messagebox.showerror(title or "Error", message, parent=parent)
    elif dialog_type == "question":
        return messagebox.askquestion(title or "Question", message, parent=parent)
    elif dialog_type == "color":
        return colorchooser.askcolor(title=title or "Choose Color", parent=parent)
    elif dialog_type == "file":
        return filedialog.askopenfilename(title=title or "Choose File", parent=parent)
    elif dialog_type == "save":
        return filedialog.asksaveasfilename(title=title or "Save As", parent=parent)

class AsyncTask:
    """Handle asynchronous tasks with progress updates"""
    def __init__(self, task, callback, parent=None):
        self.parent = parent or get_root()
        self.task = task
        self.callback = callback
        
    def run(self):
        def worker():
            result = self.task()
            self.frame.after(0, lambda: self.callback(result))
            self.frame.destroy()
            
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(expand=True, fill='both')
        
        label = ttk.Label(self.frame, text="Please wait...")
        label.pack(pady=20)
        
        progress = ttk.Progressbar(self.frame, mode='indeterminate')
        progress.pack(fill='x', padx=20)
        progress.start()
        
        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.start()

# Utility classes
class Database:
    """Simple database operations wrapper"""
    def __init__(self, db_path):
        self.db_path = db_path
        
    def execute(self, query, params=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.fetchall()

class Validator:
    """Input validation utilities"""
    @staticmethod
    def is_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def is_phone(phone):
        pattern = r'^\+?1?\d{9,15}$'
        return re.match(pattern, phone) is not None

    @staticmethod
    def is_date(date_string):
        try:
            datetime.strptime(date_string, '%Y-%m-%d')
            return True
        except ValueError:
            return False

def file_operations():
    """Common file operations utility"""
    class FileOps:
        @staticmethod
        def save_json(data, filepath):
            with open(filepath, 'w') as f:
                json.dump(data, f)
                
        @staticmethod
        def load_json(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
                
        @staticmethod
        def save_csv(data, filepath, headers=None):
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                if headers:
                    writer.writerow(headers)
                writer.writerows(data)
                
        @staticmethod
        def load_csv(filepath):
            with open(filepath, 'r') as f:
                reader = csv.reader(f)
                return list(reader)
    
    return FileOps

#ADDITIONAL NONE GUI FUNCTIONS

import subprocess

def cmd(command):
    """Run a specific command in the command prompt."""
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result.stdout)  # Print the command's output
    except subprocess.CalledProcessError as e:
        print(f"Error executing command '{command}': {e.stderr}")

import time
#usage cmd("ipconfig")

def countdown_timer(seconds):
    """Run a countdown timer for the specified number of seconds."""
    while seconds:
        mins, secs = divmod(seconds, 60)
        print(f"{mins:02}:{secs:02}", end="\r")
        time.sleep(1)
        seconds -= 1
    print("Time's up!")
#usage countdown_timer(10)  # 10-second timer

def write_to_file(filename, text):
    """Write the specified text to a file."""
    with open(filename, "w") as file:
        file.write(text)
    print(f"Text written to {filename}")
#usage write_to_file("example.txt", "Hello, world!")

import psutil

def cpu_usage():
    """Get the current CPU usage percentage."""
    return f"CPU Usage: {psutil.cpu_percent(interval=1)}%"
#usage print(cpu_usage())

import subprocess

def ping(host):
    """Ping a host and return whether it is reachable."""
    try:
        result = subprocess.run(["ping", "-n", "1", host], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return f"{host} is reachable."
        else:
            return f"{host} is not reachable."
    except Exception as e:
        return f"Error: {e}"
#usage print(ping("google.com"))
from PIL import ImageGrab

def screenshot(save_path="screenshot.png"):
    """Capture a screenshot and save it to the specified path."""
    image = ImageGrab.grab()
    image.save(save_path)
    print(f"Screenshot saved to {save_path}")
#usage screenshot("screenshot.png")


import requests

def get_public_ip():
    """Fetch and return the public IP address of the current machine."""
    try:
        response = requests.get("https://api.ipify.org?format=text")
        return response.text
    except requests.RequestException as e:
        return f"Error: {e}"
#usage print(get_public_ip())


import webbrowser

def open_url(url):
    """Open the specified URL in the default web browser."""
    webbrowser.open(url)
#usage open_url("https://www.google.com")

from plyer import notification

def send_desktop_notification(title, message):
    """Send a desktop notification."""
    notification.notify(
        title=title,
        message=message,
        timeout=5  # Notification disappears after 5 seconds
    )
#usage send_desktop_notification("Reminder", "Time to take a break!")



import qrcode

def qr_code_generator(data, filename="qrcode.png"):
    """Generate a QR code for the given data."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)
    print(f"QR code saved as {filename}")
#usage qr_code_generator("https://www.google.com", "google_qr.png")


import playsound

def play_sound(file_path):
    """Play an audio file."""
    try:
        playsound.playsound(file_path)
        print(f"Playing {file_path}")
    except Exception as e:
        print(f"Error: {e}")
#usage play_sound("alarm.mp3")


import pyttsx3

def text_to_speech(text):
    """Convert text to speech."""
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
#usage text_to_speech("Hello, how are you?")

from PIL import Image

def resize_image(input_path, output_path, size=(100, 100)):
    """Resize an image to the specified size."""
    try:
        with Image.open(input_path) as img:
            img_resized = img.resize(size)
            img_resized.save(output_path)
            print(f"Image saved to {output_path}")
    except Exception as e:
        print(f"Error: {e}")

# Usage:
# resize_image("input.jpg", "output.jpg", (200, 200))

import zipfile

def compress_file(file_path, zip_name="compressed.zip"):
    """Compress a file into a ZIP archive."""
    try:
        with zipfile.ZipFile(zip_name, "w") as zipf:
            zipf.write(file_path)
            print(f"{file_path} compressed into {zip_name}")
    except Exception as e:
        print(f"Error: {e}")

# Usage:
# compress_file("example.txt")

import time

def run_timer():
    """Run a simple stopwatch."""
    print("Press Enter to start the timer and Ctrl+C to stop.")
    input()
    start_time = time.time()
    try:
        while True:
            elapsed_time = time.time() - start_time
            print(f"Elapsed: {elapsed_time:.2f} seconds", end="\r")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print(f"\nTotal time: {elapsed_time:.2f} seconds")

# Usage:
# run_timer()
