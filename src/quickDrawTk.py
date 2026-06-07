import os
import sys
import random
import json
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image

class QuickDrawApp(ctk.CTk):
    """
    An old version using Tkinter that is slow and laggy.
    still usable.
    """

    # Class constants for configuration options
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
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        self.title("Quick Draw")

        # Set default window size (75% of screen width, 16:9 ratio)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        app_width = int(screen_width * 0.75)
        app_height = int(app_width * (9 / 16))
        x = int((screen_width / 2) - (app_width / 2))
        y = int((screen_height / 2) - (app_height / 2))
        self.geometry(f"{app_width}x{app_height}+{x}+{y}")

        # ---- Application State Variables ----
        self.index = 0
        self.font_size = 14
        self.font_type = "Arial"
        self.session_running = False
        self.image_time = 10
        self.time_left = 0
        self.image_amount = 1
        self.folder_path = ""
        self.session_playlist = []

        # Track last window size to manage resizing events
        self.last_width = 0
        self.last_height = 0

        # References to prevent garbage collection and keep images loaded
        self._current_ctk_image = None
        self._timer_id = None
        self._resize_timer = None
        self._image_cache = {}  # Caches original PIL.Image objects

        # ---- Save File Configuration ----
        self.save_file = self._get_save_file_path()

        # ---- UI String Variables ----
        self.image_time_clicked = ctk.StringVar()
        self.image_num_clicked = ctk.StringVar()

        # ---- UI Component Placeholders ----
        self.central_frame = None
        self.current_image_label = ctk.CTkLabel(self, text="")
        self.which_image_label = ctk.CTkLabel(self, text="")
        self.timer_label = ctk.CTkLabel(self, text="")
        self.folder_label = ctk.CTkLabel(self, text="")

        # Load persisted settings from previous sessions
        self.load_settings()

        # Bind window resize event
        self.bind("<Configure>", self.on_resize)

        # Force window to the front on startup after the main loop has initialized
        self.after(100, self.force_focus)

    @staticmethod
    def _get_save_file_path() -> str:
        """Determines the OS-specific directory for saving application settings."""
        if sys.platform == "darwin":
            base_dir = os.path.expanduser("~/Library/Application Support/QuickDraw")
        elif sys.platform == "win32":
            base_dir = os.path.join(os.environ.get('APPDATA', ''), "QuickDraw")
        else:
            base_dir = os.path.expanduser("~/.local/share/QuickDraw")

        os.makedirs(base_dir, exist_ok=True)
        return os.path.join(base_dir, "quickdraw.json")

    # ---- Settings Persist Management ----

    def get_folder(self):
        temp_path = filedialog.askdirectory(parent=self, title="Choose a folder")
        if temp_path:
            self.folder_path = temp_path
            self.save_settings()

            # Instantly count images so user knows it worked
            try:
                count = sum(1 for f in os.listdir(self.folder_path)
                            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')) and not f.startswith('.'))
                self.folder_label.configure(text=f"{self.folder_path}\n({count} images found)")
            except OSError:
                self.folder_label.configure(text=f"{self.folder_path}\n(Error reading folder)")

    def save_settings(self):
        """Saves current directory and user preferences to the config JSON file."""
        data = {
            "folder_path": self.folder_path,
            "time_pref": self.image_time_clicked.get(),
            "num_pref": self.image_num_clicked.get()
        }
        try:
            with open(self.save_file, "w") as file:
                json.dump(data, file)
        except OSError:
            # Silently ignore if we cannot write settings (e.g., read-only disk)
            pass

    def load_settings(self):
        """Loads saved directory and user preferences from the config JSON file."""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, "r") as file:
                    data = json.load(file)
                    self.folder_path = data.get("folder_path", "")
                    self.image_time_clicked.set(data.get("time_pref", "10 Seconds"))
                    self.image_num_clicked.set(data.get("num_pref", "10 Images"))
            except (OSError, json.JSONDecodeError):
                # Silently ignore config load issues and fallback to defaults
                pass

    # ---- UI Layouts ----

    def pre_session_ui(self):
        """Draws the main setup UI where users choose settings and folders."""
        self.session_running = False
        self.time_left = 0
        self.index = 0
        self.stop_timer()

        # Clear active widgets from session
        for widget in self.winfo_children():
            widget.destroy()

        # Folder Selection Setup
        browse_button = ctk.CTkButton(
            self, text="Browse", command=self.get_folder,
            font=(self.font_type, self.font_size)
        )
        browse_button.pack(pady=10)

        folder_text = f"{self.folder_path}\n" if self.folder_path else "No folder selected\n"
        self.folder_label = ctk.CTkLabel(
            self, anchor="center", text=folder_text,
            font=(self.font_type, self.font_size + 2)
        )
        self.folder_label.pack(pady=(10, 5))

        # Default Option Values
        if not self.image_time_clicked.get():
            self.image_time_clicked.set(list(self.IMAGE_TIME_OPTIONS.keys())[0])
        if not self.image_num_clicked.get():
            self.image_num_clicked.set(list(self.IMAGE_COUNT_OPTIONS.keys())[0])

        # Settings Dropdowns
        image_time_dropdown = ctk.CTkOptionMenu(
            self, anchor="center", variable=self.image_time_clicked,
            values=list(self.IMAGE_TIME_OPTIONS.keys()), width=120,
            font=(self.font_type, self.font_size)
        )
        image_time_dropdown.pack(pady=(0, 5))

        image_num_dropdown = ctk.CTkOptionMenu(
            self, anchor="center", variable=self.image_num_clicked,
            values=list(self.IMAGE_COUNT_OPTIONS.keys()), width=120,
            font=(self.font_type, self.font_size)
        )
        image_num_dropdown.pack(pady=(0, 20))

        # Start Button
        start_session_button = ctk.CTkButton(
            self, text="Start Session", command=self.requirement_check,
            width=200, font=(self.font_type, int(self.font_size * 1.5))
        )
        start_session_button.pack()


    def requirement_check(self):
        """Checks folder validity and scans top-level files to set up the list of images."""
        if not self.folder_path:
            messagebox.showerror("Error", "Please select a folder")
            return

        self.save_settings()

        try:
            # 1. Scan for valid images
            valid_exts = ('.png', '.jpg', '.jpeg', '.webp')
            found_images = [
                os.path.join(self.folder_path, f) for f in os.listdir(self.folder_path)
                if f.lower().endswith(valid_exts) and not f.startswith('.')
            ]

            if not found_images:
                messagebox.showerror("Error", "No images found in the selected folder.")
                return

            random.shuffle(found_images)

            self.image_amount = self.IMAGE_COUNT_OPTIONS[self.image_num_clicked.get()]
            self.image_time = self.IMAGE_TIME_OPTIONS[self.image_time_clicked.get()]

            # Repeat/wrap images if the folder contains fewer files than the requested amount
            self.session_playlist = [
                found_images[i % len(found_images)] for i in range(self.image_amount)
            ]

            # Clear image cache for the new session
            self._image_cache.clear()

        except OSError as e:
            messagebox.showerror("Error", f"Could not read the folder:\n{e}")
            return

        self.session_running = True
        self.session_ui()

    def get_cached_image(self, image_path, max_width, max_height):
        """Fetches an image from cache, or loads it and manages memory capacity."""
        cache_key = f"{image_path}_{max_width}x{max_height}"

        # Fast return if already in memory
        if cache_key in self._image_cache:
            return self._image_cache[cache_key]

        # Cache miss: Allocate memory and process the image
        opened_image = Image.open(image_path)
        opened_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

        displayed_image = ctk.CTkImage(
            light_image=opened_image, dark_image=opened_image,
            size=opened_image.size
        )

        # Store in dictionary
        self._image_cache[cache_key] = displayed_image

        # Memory Safety: Explicitly drop the oldest reference if we exceed the session size.
        # This allows Python's garbage collector to instantly free the heap memory.
        if len(self._image_cache) > self.image_amount:
            self._image_cache.pop(next(iter(self._image_cache)))

        return displayed_image


    def session_ui(self):
        """Builds the active slideshow layout and starts the timer."""
        for widget in self.winfo_children():
            widget.destroy()

        # Top controls container
        self.central_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.central_frame.pack(side="top", pady=10)

        forward_button = ctk.CTkButton(
            self.central_frame, text=">>", command=self.forward,
            font=(self.font_type, self.font_size + 5)
        )
        forward_button.pack(side="right", padx=10)

        backward_button = ctk.CTkButton(
            self.central_frame, text="<<", command=self.backward,
            font=(self.font_type, self.font_size + 5)
        )
        backward_button.pack(side="left", padx=10)

        self.which_image_label = ctk.CTkLabel(
            self.central_frame, text=" ",
            font=(self.font_type, self.font_size + 5)
        )
        self.which_image_label.pack(side="top", pady=5)

        # Image display label (centered and expandable)
        self.current_image_label = ctk.CTkLabel(self, text="")
        self.current_image_label.pack(expand=True)

        # End Session control overlay
        end_session_button = ctk.CTkButton(
            self, text="End Session", command=self.pre_session_ui,
            font=(self.font_type, self.font_size)
        )
        end_session_button.place(relx=0.0, rely=0.0, anchor="nw", x=20, y=13)

        # Countdown Timer overlay
        self.timer_label = ctk.CTkLabel(self, font=(self.font_type, self.font_size + 10))
        self.timer_label.place(relx=1.0, rely=0.0, anchor="ne", x=-20, y=15)

        # Sync UI configuration to calculate geometry size before loading the first image
        self.update_idletasks()

        self.time_left = self.image_time
        self.load_next_image()
        self.start_timer()

    # ---- Image Processing & Rendering ----

    def load_next_image(self):
        """Updates the UI with the next image from the session playlist."""
        if not self.session_running:
            return

        # End session if we hit the end of the generated playlist
        if self.index >= len(self.session_playlist):
            messagebox.showinfo("Completion", "Session has ended")
            self.pre_session_ui()
            return

        self.which_image_label.configure(text=f"{self.index + 1}/{self.image_amount}")

        image_path = self.session_playlist[self.index]
        max_width = max(100, self.winfo_width() - 20)
        max_height = max(100, self.winfo_height() - 70)

        try:
            # Request the image from the cache manager
            displayed_image = self.get_cached_image(image_path, max_width, max_height)

            # Keep a hard reference to prevent the UI from flickering
            self._current_ctk_image = displayed_image

            self.current_image_label.configure(image=displayed_image, text="")
            self.current_image_label.pack(expand=True)

        except (OSError, Image.UnidentifiedImageError) as e:
            self.current_image_label.configure(image=None, text="Error loading image")
            self.current_image_label.pack(expand=True)
            print(f"Failed to load {image_path}: {e}")

    # ---- Navigation & Control Events ----

    def backward(self):
        """Navigates to the previous image, resetting the countdown timer."""
        if self.index > 0:
            self.index -= 1
            self.time_left = self.image_time
            self.update_timer_ui()
            self.load_next_image()
            self.start_timer()

    def forward(self):
        """Navigates to the next image, resetting the countdown timer."""
        self.index += 1
        self.time_left = self.image_time
        self.update_timer_ui()
        self.load_next_image()
        self.start_timer()

    def update_timer_ui(self):
        """Updates the visible countdown clock label."""
        if self.session_running:
            minutes = int(self.time_left / 60)
            seconds = self.time_left % 60
            self.timer_label.configure(text=f"{minutes:02}:{seconds:02}")

    def stop_timer(self):
        """Cancels active timer loops to prevent rapid clock speedups."""
        if self._timer_id is not None:
            self.after_cancel(self._timer_id)
            self._timer_id = None

    def start_timer(self):
        """Restarts the countdown timer cleanly."""
        self.stop_timer()
        self.update_timer_ui()
        self.timer()

    def timer(self):
        """Handles time updates and auto-advancing slide logic recursively."""
        if not self.session_running:
            return

        if self.time_left <= 0:
            self.index += 1
            self.time_left = self.image_time
            self.load_next_image()

        self.update_timer_ui()
        self.time_left -= 1

        self._timer_id = self.after(1000, self.timer)

    def on_resize(self, event):
        """Detects resize events but waits for them to stop before redrawing."""
        if event.widget == self and self.session_running:
            # Cancel the previous timer if it exists (user is still dragging)
            if self._resize_timer is not None:
                self.after_cancel(self._resize_timer)
            # Set a new timer to execute the heavy lifting after 200ms of inactivity
            self._resize_timer = self.after(200, self._perform_resize)

    def _perform_resize(self):
        """Actually redraws/scales the current image after resizing finishes."""
        current_width = self.winfo_width()
        current_height = self.winfo_height()
        if current_width != self.last_width or current_height != self.last_height:
            self.last_width = current_width
            self.last_height = current_height
            self.load_next_image()

    def force_focus(self):
        """Forces the application window to the foreground on startup."""
        self.lift()
        self.focus_force()
        # Temporarily set topmost to stay in front of IDE/terminal on startup
        self.attributes('-topmost', True)
        self.after(1000, lambda: self.attributes('-topmost', False))

def main():
    app = QuickDrawApp()
    app.pre_session_ui()
    app.mainloop()
if __name__ == "__main__":
    main()
