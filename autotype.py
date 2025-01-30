#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name          : ldapsearch.py
# Author             : Podalirius (@podalirius_)
# Date created       : 29 Jul 2021


import argparse
import os
import pyautogui
import time
from rich.progress import track
from enum import Enum


folder_icon_b64 = """
iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAMAAAD04JH5AAABDlBMVEUAPQNxAAB1AAAAAAD/nwD/
ogD/oQD/oAD/oAD/nwD/oAD/nwD/oQD/oAD/oAD/nwD/oQD/nwD/oAD/nwD/oAD/nwD/nwD/nwD/
nwD/nwD/nwD/uxr/vBv/uhf/uRf/uxX/wyH/vx7/tRD/vBv/xyX/thX/xST/vBn/uhn/wSD/uBf/
vx3/uxv/uhn/wiD/txf/vRv/pwb/rQz/thT/uxn/uBf/vhz/wyL/yij/ySj/yyj/ySf/yif/yij/
zyj/ySj/yiX/ySf/yij/zyD/yif/yyf/ySb/oAD/pgX/qwr/rgz/thT/owL/vBv/wiD/yij/txb/
qAf/uhn/xyX/sxH/xCP/vx7/rQz/sA//tBQ1btq6AAAAAXRSTlMAQObYZgAAAAFiS0dEAIgFHUgA
AAD6SURBVHja7dtPCoJAGIbxb9F3CZmBFtIfhCiFOoJGG8GF3v8kWZRIq4zybfE8B/D9MbN1zIiI
iJ75O2nXfyhwlwp8UnKAq/e/LnAXC1wscBcLXC1wtcDVAlcLhu8t6rrtptR+XLM7lq+AqglzFpNs
Mwbs0yLM3To7DYA6BkGrpnwAKsl+fw95eQfUQVVc3gBlKgOEbdYDzkFYfwmXVAnoj+AQpO2s0wKi
pVpAblF9AokWkAAAAAAAAABWaAGFBXEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADQA0y9
rweYel8psD8BqAjj35vV+/MbeFZFRERDV/z5F2EMeENpAAAAAElFTkSuQmCC
"""


def wait_seconds(seconds):
    """
    Waits for the specified number of seconds before returning,
    printing a countdown each second.
    
    Args:
        seconds (int): Number of seconds to wait
    """
    for _ in track(range(seconds, 0, -1), description="Waiting ..."):
        time.sleep(1)


def window_gui():
    """
    Starts the GUI mode.
    """
    from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTextEdit, QPushButton, QSpinBox, QLabel, QHBoxLayout, QScrollArea, QShortcut, QFileDialog, QMessageBox, QLineEdit
    from PyQt5.QtGui import QKeySequence, QIcon, QPixmap
    from PyQt5.QtCore import QTimer, QByteArray

    class State(Enum):
        """
        Enum class to represent the state of the application.
        """
        IDLE = 0
        WAITING = 1
        TYPING = 2
        CANCELLED = 3

    class MainWindow(QMainWindow):
        """
        Main window class for the application.
        """
        def __init__(self):
            super().__init__()
            
            self.font_size = 20
            self.delay_before_start = 0
            self.current_cursor_position = None

            self.state = State.IDLE

            self.timer = QTimer(self)   
            self.timer.timeout.connect(self.action_timer_update)

            self.setup_ui()
        
        def setup_ui(self):
            """
            Sets up the UI of the main window.
            """
            self.setWindowTitle("AutoType - v1.1 - by Remi GASCOU (Podalirius)")
            self.setGeometry(100, 100, 600, 400)

            # Create central widget and layout
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)

            # Text edit with scroll bar
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            self.text_edit = QTextEdit()
            self.text_edit.setAcceptRichText(False)           
            self.update_text_edit_style(self.font_size)
            scroll_area.setWidget(self.text_edit)
            layout.addWidget(scroll_area)

            # Create load file button
            load_file_layout = QHBoxLayout()
            # Create browse button
            folder_pixmap = QPixmap()
            global folder_icon_b64
            folder_icon_b64 = folder_icon_b64.strip().replace("\n", "").encode()
            folder_pixmap.loadFromData(QByteArray.fromBase64(folder_icon_b64))
            folder_icon = QIcon(folder_pixmap)
            self.browse_button = QPushButton(icon=folder_icon, text="Browse")
            self.browse_button.clicked.connect(self.action_browse_file)
            load_file_layout.addWidget(self.browse_button)
            # Create file path field
            self.file_path_input = QLineEdit()
            self.file_path_input.setPlaceholderText("File path ...")
            load_file_layout.addWidget(self.file_path_input)
            # Create load file button
            self.load_file_button = QPushButton("Load File")
            self.load_file_button.clicked.connect(self.action_load_file)
            load_file_layout.addWidget(self.load_file_button)
            # 
            layout.addLayout(load_file_layout)

            # Create config layout  
            config_layout = QHBoxLayout()
            # Create delay input with label
            delay_layout = QHBoxLayout()
            delay_label = QLabel("Delay:")
            self.delay_input = QSpinBox()
            self.delay_input.setRange(0, 1000)
            self.delay_input.setValue(5)
            self.delay_input.setSuffix(" seconds")
            delay_layout.addWidget(delay_label)
            delay_layout.addWidget(self.delay_input)
            config_layout.addLayout(delay_layout)
            # Create interval input with label
            interval_layout = QHBoxLayout()
            interval_label = QLabel("Interval:")
            self.interval_input = QSpinBox()
            self.interval_input.setRange(0, 1000)
            self.interval_input.setValue(50)
            self.interval_input.setSuffix(" ms")
            interval_layout.addWidget(interval_label)
            interval_layout.addWidget(self.interval_input)
            config_layout.addLayout(interval_layout)
            # add this to the final layout
            layout.addLayout(config_layout)

            # Create start and cancel buttons
            button_layout = QHBoxLayout()
            self.start_button = QPushButton("Start Typing")
            self.start_button.clicked.connect(self.action_start_typing)
            button_layout.addWidget(self.start_button)
            self.cancel_button = QPushButton("Cancel")
            self.cancel_button.clicked.connect(self.action_cancel_typing)
            self.cancel_button.setEnabled(False)
            self.cancel_button.hide()
            button_layout.addWidget(self.cancel_button)
            layout.addLayout(button_layout)

            # Create keyboard shortcuts
            self.shortcut = QShortcut(QKeySequence("Ctrl+Enter"), self)
            self.shortcut.activated.connect(self.action_start_typing)

            self.shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
            self.shortcut.activated.connect(self.action_cancel_typing)

            self.shortcut = QShortcut(QKeySequence("Ctrl++"), self)
            self.shortcut.activated.connect(self.action_zoom_in)

            self.shortcut = QShortcut(QKeySequence("Ctrl+-"), self)
            self.shortcut.activated.connect(self.action_zoom_out)

        def action_timer_update(self):
            """
            Updates the UI based on the current state of the application.
            """
            print("action_timer_update")
            if self.state == State.IDLE:
                self.start_button.setText(f"Start typing")
                self.cancel_button.setEnabled(False)

            elif self.state == State.WAITING:
                self.delay_before_start -= self.timer.interval()/1000
                self.start_button.setText(f"Starting in {round(self.delay_before_start, 1)} seconds...")
                if self.delay_before_start <= 0:
                    self.delay_before_start = 0
                    self.state = State.TYPING
                    self.start_button.setText("Typing ...")
                    self.cancel_button.setEnabled(True)
                    self.cancel_button.show()
                    self.current_cursor_position = pyautogui.position()

            elif self.state == State.TYPING:
                if self.current_cursor_position is None:
                    self.current_cursor_position = pyautogui.position()
                else:
                    curpos = pyautogui.position()
                    if curpos.x != self.current_cursor_position.x or curpos.y != self.current_cursor_position.y:
                        self.current_cursor_position = curpos
                        self.delay_before_start = self.delay_input.value()
                        self.state = State.WAITING
                    else:
                        text = self.text_edit.toPlainText()
                        if text:
                            pyautogui.write(text[0])
                            self.text_edit.setPlainText(text[1:])
                        else:
                            self.state = State.CANCELLED
                            self.start_button.setEnabled(True)
                            self.cancel_button.setEnabled(False)
                            self.cancel_button.hide()

            elif self.state == State.CANCELLED:
                self.start_button.setEnabled(True)
                self.cancel_button.setEnabled(False)
                self.cancel_button.hide()
                self.state = State.IDLE

        def action_start_typing(self):
            """
            Starts the typing process.
            """
            self.timer.stop()
            self.timer.start(self.interval_input.value())

            self.delay_before_start = self.delay_input.value()
            self.state = State.WAITING

        def action_cancel_typing(self):
            """
            Cancels the typing process.
            """
            self.state = State.CANCELLED
        
        def action_browse_file(self):
            """
            Opens a file dialog to select a file to load into the text editor.
            """
            file_types = [
                ("Text Files", "*.txt"),
                ("Python Files", "*.py"),
                ("JavaScript Files", "*.js"),
                ("HTML Files", "*.html"),
                ("CSS Files", "*.css"),
                ("XML Files", "*.xml"),
                ("JSON Files", "*.json"),
                ("Markdown Files", "*.md"),
                ("YAML Files", "*.yml;*.yaml"),
                ("SQL Files", "*.sql"),
                ("Shell Scripts", "*.sh"),
                ("Batch Files", "*.bat;*.cmd"),
                ("PowerShell Files", "*.ps1"),
                ("Ruby Files", "*.rb"),
                ("PHP Files", "*.php"),
                ("Java Files", "*.java"),
                ("C Files", "*.c;*.h"),
                ("C++ Files", "*.cpp;*.hpp"),
                ("C# Files", "*.cs"),
                ("Go Files", "*.go"),
                ("Rust Files", "*.rs"),
                ("TypeScript Files", "*.ts"),
                ("Swift Files", "*.swift"),
                ("Kotlin Files", "*.kt"),
                ("Perl Files", "*.pl"),
                ("Lua Files", "*.lua"),
                ("R Files", "*.r;*.R"),
                ("MATLAB Files", "*.m"),
                ("Assembly Files", "*.asm"),
                ("Config Files", "*.conf;*.config;*.ini"),
                ("Log Files", "*.log"),
                ("CSV Files", "*.csv"),
                ("All Files", "*.*")
            ]
            file_types = sorted(file_types, key=lambda x: x[0])
            load_file_path, _ = QFileDialog.getOpenFileName(
                parent=self, caption="Open File", 
                directory="", 
                filter=";;".join(["%s (%s)" % (ftype, fext) for ftype, fext in file_types])
            )
            if load_file_path:
                self.file_path_input.setText(load_file_path)
        
        def action_load_file(self):
            """
            Loads the selected file into the text editor.
            """
            load_file_path = self.file_path_input.text()
            if len(load_file_path) == 0:
                QMessageBox.critical(self, "Error", f"Please select a file first.")
            else:
                try:
                    if os.path.isdir(load_file_path):  
                        QMessageBox.critical(self, "Error", f"Please select a file, not a directory.")
                    else:
                        with open(load_file_path, 'r', encoding='utf-8') as file:
                            self.text_edit.setText(file.read())
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Could not load file: {str(e)}")

        def action_zoom_in(self):
            self.update_text_edit_style(self.font_size+1) 

        def action_zoom_out(self):
            self.update_text_edit_style(self.font_size-1) 

        def update_text_edit_style(self, value):
            self.font_size = max(value, 1)
            self.text_edit.setStyleSheet("""
                QTextEdit {
                    background-color: #1f1f1f;
                    color: #cfcfcf;
                    font-size: %dpx;
                    font-family: Consolas;
                }
            """ % self.font_size)
            self.text_edit.update()

    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()


def parseArgs():
    parser = argparse.ArgumentParser(add_help=True, description="AutoType, a Python tool to simulate keyboard typing when copy-paste functionality is unavailable, with both CLI and GUI modes.")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--stdin", action="store_true", default=None, help="Read input from stdin.")
    group.add_argument("--file", dest="input_file", type=str, default=None, help="Read input from a file.")
    group.add_argument("--gui", dest="gui", action="store_true", default=False, help="Start GUI mode.")

    group_options = parser.add_argument_group("Options")
    group_options.add_argument("--delay", dest="delay", type=int, default=5, help="Delay before starting to type in seconds.")
    group_options.add_argument("--interval", dest="interval", type=int, default=50, help="Interval between each character in milliseconds.")

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    options = parseArgs()

    options.interval = options.interval / 1000

    if options.stdin is not None:
        print("[>] Reading from stdin")
        while True:
            data = input("> ")
            if len(data) != 0:
                wait_seconds(options.delay)
                pyautogui.write(data, interval=options.interval)

    elif options.input_file is not None:
        print(f"[>] Reading from file: {options.input_file}")
        with open(options.input_file, "r") as f:
            data = f.read()
            wait_seconds(options.delay)
            pyautogui.write(data, interval=options.interval)

    elif options.gui:
        window_gui()

    else:
        print("[!] No input specified")
