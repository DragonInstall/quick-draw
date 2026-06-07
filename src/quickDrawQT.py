import os
import sys
import random
import json
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QPushButton, QComboBox,
                               QFileDialog, QMessageBox, QSizePolicy)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QFont

class QuickDrawApp(QMainWindow):
    """
    New version of Quick Draw using PySide6.
    Faster and better performing than quickDrawTk.py
    """

    IMAGE_TIME_OPTIONS = {
        "10 Seconds": 10, "30 Seconds": 30, "1 Minute": 60,
        "2 Minutes": 120, "5 Minutes": 300, "10 Minutes": 600,
        "15 Minutes": 900, "30 Minutes": 1800, "1 Hour": 3600,
    }

    IMAGE_COUNT_OPTIONS = {
        "1 Image": 1, "10 Images": 10, "15 Images": 15,
        "20 Images": 20, "30 Images": 30, "40 Images": 40,
        "50 Images": 50, "60 Images": 60, "120 Images": 120,
    }

    def __init__(self):
        super().__init__()

        # ---- Window Configuration ----
        self.setWindowTitle("Quick Draw")
        self.font_family = "Arial"
        self.base_font_size = 14

        # Calculate initial window size
        screen = QApplication.primaryScreen().geometry()
        app_width = int(screen.width() * 0.75)
        app_height = int(app_width * (9 / 16))
        self.resize(app_width, app_height)

        # Center the window
        x = (screen.width() - app_width) // 2
        y = (screen.height() - app_height) // 2
        self.move(x, y)

        # ---- Application State Variables ----
        self.index = 0
        self.session_running = False
        self.image_time = 10
        self.time_left = 0
        self.image_amount = 1
        self.folder_path = ""
        self.session_playlist = []
        self.folder_label = None
        self.current_image_label = None
        self.time_dropdown = None
        self.count_dropdown= None
        self.timer_label= None
        self.which_image_label = None

        # Preferences state
        self.time_pref_val = "10 Seconds"
        self.num_pref_val = "10 Images"

        # ---- Timers & Caching ----
        self.session_timer = QTimer(self)
        self.session_timer.timeout.connect(self.timer_tick)

        self.resize_timer = QTimer(self)
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self._perform_resize)

        self._image_cache = {}

        # ---- Central Widget Setup ----
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # ---- Save File Configuration ----
        self.save_file = self._get_save_file_path()
        self.load_settings()

        # Start UI
        self.pre_session_ui()

    @staticmethod
    def _get_save_file_path() -> str:
        if sys.platform == "darwin":
            base_dir = os.path.expanduser("~/Library/Application Support/QuickDraw")
        elif sys.platform == "win32":
            base_dir = os.path.join(os.environ.get('APPDATA', ''), "QuickDraw")
        else:
            base_dir = os.path.expanduser("~/.local/share/QuickDraw")
        os.makedirs(base_dir, exist_ok=True)
        return os.path.join(base_dir, "quickdraw.json")

    def save_settings(self):
        data = {
            "folder_path": self.folder_path,
            "time_pref": self.time_pref_val,
            "num_pref": self.num_pref_val
        }
        try:
            with open(self.save_file, "w") as file:
                json.dump(data, file)
        except OSError:
            pass

    def load_settings(self):
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, "r") as file:
                    data = json.load(file)
                    self.folder_path = data.get("folder_path", "")
                    self.time_pref_val = data.get("time_pref", "10 Seconds")
                    self.num_pref_val = data.get("num_pref", "10 Images")
            except (OSError, json.JSONDecodeError):
                pass

    def clear_layout(self):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item is not None:
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                elif item.layout():
                    while item.layout().count():
                        sub_item = item.layout().takeAt(0)
                        if sub_item is not None and sub_item.widget():
                            sub_item.widget().deleteLater()
                    item.layout().deleteLater()


    # ---- UI Layouts ----

    def pre_session_ui(self):
        self.session_running = False
        self.time_left = 0
        self.index = 0
        self.session_timer.stop()
        self.clear_layout()

        # Container for centering items vertically
        self.main_layout.addStretch()

        font = QFont(self.font_family, self.base_font_size)
        large_font = QFont(self.font_family, int(self.base_font_size * 1.5))

        # Browse Button
        browse_btn = QPushButton("Browse")
        browse_btn.setFont(font)
        browse_btn.clicked.connect(self.get_folder)
        self.main_layout.addWidget(browse_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Folder Label
        folder_text = f"{self.folder_path}\n" if self.folder_path else "No folder selected\n"
        self.folder_label = QLabel(folder_text)
        self.folder_label.setFont(font)
        self.folder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.folder_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Time Dropdown
        self.time_dropdown = QComboBox()
        self.time_dropdown.addItems(list(self.IMAGE_TIME_OPTIONS.keys()))
        self.time_dropdown.setCurrentText(self.time_pref_val)
        self.time_dropdown.setFont(font)
        self.time_dropdown.currentTextChanged.connect(self.update_time_pref)
        self.main_layout.addWidget(self.time_dropdown, alignment=Qt.AlignmentFlag.AlignCenter)

        # Count Dropdown
        self.count_dropdown = QComboBox()
        self.count_dropdown.addItems(list(self.IMAGE_COUNT_OPTIONS.keys()))
        self.count_dropdown.setCurrentText(self.num_pref_val)
        self.count_dropdown.setFont(font)
        self.count_dropdown.currentTextChanged.connect(self.update_num_pref)
        self.main_layout.addWidget(self.count_dropdown, alignment=Qt.AlignmentFlag.AlignCenter)

        # Start Button
        start_btn = QPushButton("Start Session")
        start_btn.setFont(large_font)
        start_btn.setMinimumWidth(200)
        start_btn.clicked.connect(self.requirement_check)
        self.main_layout.addWidget(start_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.main_layout.addStretch()

    def update_time_pref(self, text):
        self.time_pref_val = text

    def update_num_pref(self, text):
        self.num_pref_val = text

    def get_folder(self):
        temp_path = QFileDialog.getExistingDirectory(self, "Choose a folder", self.folder_path)
        if temp_path:
            self.folder_path = temp_path
            self.save_settings()
            try:
                count = sum(1 for f in os.listdir(self.folder_path)
                            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')) and not f.startswith('.'))
                self.folder_label.setText(f"{self.folder_path}\n({count} images found)")
            except OSError:
                self.folder_label.setText(f"{self.folder_path}\n(Error reading folder)")

    def requirement_check(self):
        if not self.folder_path:
            QMessageBox.critical(self, "Error", "Please select a folder")
            return

        self.save_settings()

        try:
            valid_exts = ('.png', '.jpg', '.jpeg', '.webp')
            found_images = [
                os.path.join(self.folder_path, f) for f in os.listdir(self.folder_path)
                if f.lower().endswith(valid_exts) and not f.startswith('.')
            ]

            if not found_images:
                QMessageBox.critical(self, "Error", "No images found in the selected folder.")
                return

            random.shuffle(found_images)

            self.image_amount = self.IMAGE_COUNT_OPTIONS[self.num_pref_val]
            self.image_time = self.IMAGE_TIME_OPTIONS[self.time_pref_val]

            self.session_playlist = [
                found_images[i % len(found_images)] for i in range(self.image_amount)
            ]
            self._image_cache.clear()

        except OSError as e:
            QMessageBox.critical(self, "Error", f"Could not read the folder:\n{e}")
            return

        self.session_running = True
        self.session_ui()

    def session_ui(self):
        self.clear_layout()

        font = QFont(self.font_family, self.base_font_size)
        large_font = QFont(self.font_family, self.base_font_size + 5)

        # Top Control Bar (HBoxLayout)
        top_bar = QHBoxLayout()

        end_btn = QPushButton("End Session")
        end_btn.setFont(font)
        end_btn.clicked.connect(self.pre_session_ui)
        top_bar.addWidget(end_btn)

        top_bar.addStretch() # Spacer

        back_btn = QPushButton("<<")
        back_btn.setFont(large_font)
        back_btn.clicked.connect(self.backward)
        top_bar.addWidget(back_btn)

        self.which_image_label = QLabel(f" 1/{self.image_amount} ")
        self.which_image_label.setFont(large_font)
        top_bar.addWidget(self.which_image_label)

        fwd_btn = QPushButton(">>")
        fwd_btn.setFont(large_font)
        fwd_btn.clicked.connect(self.forward)
        top_bar.addWidget(fwd_btn)

        top_bar.addStretch() # Spacer

        self.timer_label = QLabel("00:00")
        self.timer_label.setFont(QFont(self.font_family, self.base_font_size + 10))
        top_bar.addWidget(self.timer_label)

        self.main_layout.addLayout(top_bar)

        # Image Display Area
        self.current_image_label = QLabel()
        self.current_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.main_layout.addWidget(self.current_image_label, stretch=1)

        self.time_left = self.image_time
        # Use a single-shot timer to load the first image after the UI finishes drawing
        QTimer.singleShot(50, self.start_session)

    def start_session(self):
        self.load_next_image()
        self.update_timer_ui()
        self.session_timer.start(1000)

    # ---- Image Processing & Rendering ----

    def load_next_image(self):
        if not self.session_running:
            return

        if self.index >= len(self.session_playlist):
            QMessageBox.information(self, "Completion", "Session has ended")
            self.pre_session_ui()
            return

        self.which_image_label.setText(f" {self.index + 1}/{self.image_amount} ")

        image_path = self.session_playlist[self.index]

        # Calculate available space in the label
        max_width = self.current_image_label.width()
        max_height = self.current_image_label.height()

        # Fallback if UI hasn't fully rendered yet
        if max_width < 100: max_width = self.width() - 40
        if max_height < 100: max_height = self.height() - 100

        cache_key = f"{image_path}_{max_width}x{max_height}"

        if cache_key in self._image_cache:
            pixmap = self._image_cache[cache_key]
        else:
            # Load and scale QPixmap
            pixmap = QPixmap(image_path)
            pixmap = pixmap.scaled(max_width, max_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self._image_cache[cache_key] = pixmap

            if len(self._image_cache) > self.image_amount:
                self._image_cache.pop(next(iter(self._image_cache)))

        self.current_image_label.setPixmap(pixmap)

    # ---- Navigation & Control Events ----

    def backward(self):
        if self.index > 0:
            self.index -= 1
            self.time_left = self.image_time
            self.update_timer_ui()
            self.load_next_image()
            self.session_timer.start(1000)

    def forward(self):
        self.index += 1
        self.time_left = self.image_time
        self.update_timer_ui()
        self.load_next_image()
        self.session_timer.start(1000)

    def update_timer_ui(self):
        if self.session_running:
            minutes = int(self.time_left / 60)
            seconds = self.time_left % 60
            self.timer_label.setText(f"{minutes:02}:{seconds:02}")

    def timer_tick(self):
        if not self.session_running:
            return

        if self.time_left <= 0:
            self.index += 1
            self.time_left = self.image_time
            self.load_next_image()

        self.time_left -= 1
        self.update_timer_ui()

    # Qt built-in resize event override
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.session_running:
            # Start/Restart the 200ms debounce timer
            self.resize_timer.start(200)

    def _perform_resize(self):
        if self.session_running:
            self.load_next_image()

def main():
    app = QApplication(sys.argv)

    # Force Qt to use dark mode if supported by the OS
    app.setStyle("Fusion")

    window = QuickDrawApp()
    window.show()

    # Bring to front on launch
    window.raise_()
    window.activateWindow()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()