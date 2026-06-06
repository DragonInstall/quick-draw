import os,sys
import random
import json
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageOps


class QuickDrawApp(ctk.CTk):
    def __init__(self):
        super().__init__()


        # ---- CONFIGURATION ----
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        self.title("Quick Draw")

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        app_width = int(screen_width * 0.75)
        app_height = int(app_width * (9 / 16))
        x = int((screen_width / 2) - (app_width / 2))
        y = int((screen_height / 2) - (app_height / 2))
        self.geometry(f"{app_width}x{app_height}+{x}+{y}")

        # ---- FORCING WINDOW TO FRONT ----
        self.lift()
        self.attributes('-topmost', True)
        self.after(50, lambda: self.attributes('-topmost', False))
        self.focus_force()


        # ---- VARIABLES ----
        self.INDEX=0
        self.FONT_SIZE=14
        self.FONT_TYPE= "Arial"
        self.SESSION_RUNNING=False
        self.IMAGE_TIME=10
        self.TIME_LEFT=0
        self.IMAGE_AMOUNT=1
        self.FOLDER_PATH = ""
        self.FOLDER_IMAGES=[]


        # ---- CROSS-PLATFORM SAVE LOGIC ----
        if sys.platform == "darwin":
            # macOS: ~/Library/Application Support/QuickDraw/
            base_dir = os.path.expanduser("~/Library/Application Support/QuickDraw")
        elif sys.platform == "win32":
            # Windows: %APPDATA%/QuickDraw/
            base_dir = os.path.join(os.environ['APPDATA'], "QuickDraw")
        else:
            # Linux: ~/.local/share/QuickDraw/
            base_dir = os.path.expanduser("~/.local/share/QuickDraw")

        # Create the folder if it doesn't exist
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        self.SAVE_FILE = os.path.join(base_dir, "quickdraw.json")
        self.load_settings()

        # ---- WIDGETS ----
        self.image_time_clicked = ctk.StringVar()
        self.image_num_clicked = ctk.StringVar()
        self.central_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.current_image_label = ctk.CTkLabel(self)
        self.which_image_label = ctk.CTkLabel(self)
        self.timer_label = ctk.CTkLabel(self)
        self.folder_label = ctk.CTkLabel(self)

        # ---- DICTIONARIES ----
        self.image_time_dict={
                         "10 Seconds": 10,
                         "30 Seconds": 30,
                         "1 Minute"  : 60,
                         "2 Minutes" : 120,
                         "5 Minutes" : 300,
                         "10 Minutes": 600,
                         "15 Minutes": 900,
                         "30 Minutes": 1800,
                         "1 Hour"    : 3600,
        }

        self.image_num_dict={
                         "1 Image"   :1,
                         "10 Images" :10,
                         "15 Images" :15,
                         "20 Images" :20,
                         "30 Images" :30,
                         "40 Images" :40,
                         "50 Images" :50,
                         "60 Images" :60,
                         "120 Images":120,
        }


    # ---- FUNCTIONS ----
    def get_folder(self):
        temp_path = filedialog.askdirectory(title="Choose a folder")
        if temp_path != "":
            self.FOLDER_PATH = temp_path
            self.save_settings()
        self.folder_label.configure(text=f"{self.FOLDER_PATH}\n")

    def save_settings(self):
        data = {"folder_path": self.FOLDER_PATH}
        try:
            with open(self.SAVE_FILE, "w") as file:
                json.dump(data, file)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def load_settings(self):
        if os.path.exists(self.SAVE_FILE):
            try:
                with open(self.SAVE_FILE, "r") as file:
                    data = json.load(file)
                    # Use .get() to avoid errors if the key is missing
                    self.FOLDER_PATH = data.get("folder_path", "")
            except Exception:
                self.FOLDER_PATH = ""

    def pre_session_ui(self):
        self.SESSION_RUNNING = False
        self.TIME_LEFT = 0
        self.INDEX = 0

        for widget in self.winfo_children():
            widget.destroy()

        browse_button = ctk.CTkButton(self, text="Browse", command=self.get_folder, font=(self.FONT_TYPE, self.FONT_SIZE))
        browse_button.pack(pady=10)

        self.folder_label = ctk.CTkLabel(self, anchor="center", text=f"{self.FOLDER_PATH}\n", font=(self.FONT_TYPE, self.FONT_SIZE+2))
        self.folder_label.pack(pady=(10,5))

        if   self.image_time_clicked.get() == "":
            self.image_time_clicked.set(list(self.image_time_dict.keys())[0])
        if   self.image_num_clicked.get() == "":
            self.image_num_clicked.set(list(self.image_num_dict.keys())[0])

        image_time_dropdown = ctk.CTkOptionMenu(self,anchor="center",variable=self.image_time_clicked,values=list(self.image_time_dict.keys()),width=120,font=(self.FONT_TYPE, self.FONT_SIZE))
        image_time_dropdown.pack(pady=(0, 5))

        image_num_dropdown = ctk.CTkOptionMenu(self,anchor="center",variable=self.image_num_clicked,values=list(self.image_num_dict.keys()),width=120,font=(self.FONT_TYPE, self.FONT_SIZE))
        image_num_dropdown.pack(pady=(0,20))

        start_session_button = ctk.CTkButton(self, text="Start Session", command=self.requirement_check,width=200, font=(self.FONT_TYPE, int(self.FONT_SIZE*1.5)))
        start_session_button.pack()

    def requirement_check(self):
        if   self.FOLDER_PATH == "":
            messagebox.showerror("Error", "Please select a folder")
            return
        #check if there are any images inside the file
        try:
            all_files=os.listdir(self.FOLDER_PATH)
            image_files = [os.path.join(self.FOLDER_PATH, f) for f in all_files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            if len(image_files) == 0:
                messagebox.showerror("Error", "No images found")
                return
            else:
                random.shuffle(image_files)
                self.IMAGE_AMOUNT=self.image_num_dict[self.image_num_clicked.get()]
                self.IMAGE_TIME=self.image_time_dict[self.image_time_clicked.get()]
                #loops through the shuffled deck and back to 0 if not enough images
                self.FOLDER_IMAGES = [image_files[i % len(image_files)] for i in range(self.IMAGE_AMOUNT)]

        except Exception as e:
            messagebox.showerror("Error", f"Could not read the folder:\n{e}")
            return
        #all good start session
        self.SESSION_RUNNING=True
        self.session_ui()


    def session_ui(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.update()

        #build frames
        self.central_frame=ctk.CTkFrame(self, fg_color="transparent")
        self.central_frame.pack(side="top", pady=10)

        forward_button=ctk.CTkButton(self.central_frame, text=">>", command=self.forward, font=(self.FONT_TYPE, self.FONT_SIZE+5))
        forward_button.pack(side="right",padx=10)

        backward_button=ctk.CTkButton(self.central_frame, text="<<", command=self.backward, font=(self.FONT_TYPE, self.FONT_SIZE+5))
        backward_button.pack(side="left",padx=10)

        self.which_image_label = ctk.CTkLabel(self.central_frame, font=(self.FONT_TYPE,self.FONT_SIZE+5))
        self.which_image_label.pack(side="top", pady=5)

        self.current_image_label = ctk.CTkLabel(self)
        self.current_image_label.pack(expand=True)

        end_session_button=ctk.CTkButton(self, text="End Session", command=self.pre_session_ui, font=(self.FONT_TYPE,self.FONT_SIZE))
        end_session_button.place(relx=0.0,rely=0.0,anchor="nw",x=20,y=13)


        self.timer_label=ctk.CTkLabel(self,font=(self.FONT_TYPE,self.FONT_SIZE + 10))
        self.timer_label.place(relx=1.0,rely=0.0,anchor="ne",x=-20,y=15)

        # start the session
        self.timer()


    def load_next_image(self):
        if not   self.SESSION_RUNNING:
            return

        self.update_idletasks()

        max_width = max(100, self.winfo_width()-20)
        max_height = max(100, self.winfo_height()-70)

        if   self.INDEX>=len(  self.FOLDER_IMAGES):
            messagebox.showinfo("Completion","Session has ended")
            self.pre_session_ui()
            return

        else:
            self.which_image_label.configure(text=f"{self.INDEX + 1}/{len(self.FOLDER_IMAGES)}")

            opened_image = Image.open(self.FOLDER_IMAGES[self.INDEX])
            perfect_image = ImageOps.contain(opened_image, (max_width, max_height))

            displayed_image = ctk.CTkImage(light_image=perfect_image, size=perfect_image.size)
            self.current_image_label.configure(image=displayed_image, text="")

            self.INDEX += 1

    def backward(self):
        if self.INDEX>=2:
            self.INDEX-=2
            self.forward()
        else:
            return

    def update_timer_ui(self):
        if self.SESSION_RUNNING:
            minutes = int(self.TIME_LEFT / 60)
            seconds = self.TIME_LEFT % 60
            self.timer_label.configure(text=f"{minutes:02}:{seconds:02}")
        return

    def forward(self):
        self.TIME_LEFT = self.IMAGE_TIME

        self.update_timer_ui()
        self.load_next_image()

    def timer(self):
        if not self.SESSION_RUNNING:
            return

        if self.TIME_LEFT <= 0:
            self.TIME_LEFT = self.IMAGE_TIME
            self.load_next_image()

        self.update_timer_ui()
        self.TIME_LEFT -= 1

        self.after(1000, self.timer)


if __name__=="__main__":
    app=QuickDrawApp()
    app.pre_session_ui()
    app.mainloop()
