import os
import random
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageOps

root=tk.Tk()
root.title("Quick Draw")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
app_width = int(screen_width * (2/3))
app_height = screen_height
root.geometry(f"{app_width}x{app_height}")
root.lift()
central_frame = tk.Frame(root)
central_frame.pack(side="top", pady=10)

INDEX=0
LOOP_ID=None
FONT_SIZE=14
FONT_TYPE= "Arial"
SESSION_RUNNING=False
FOLDER_PATH= ""
IMAGE_TIME=10
IMAGE_AMOUNT=1
FOLDER_IMAGES=[]

#global labels
image_time_clicked= tk.StringVar()
image_num_clicked= tk.StringVar()
current_image_label=tk.Label(root)
which_image_label=tk.Label(central_frame)
timer_label=tk.Label()
folder_label=tk.Label()
end_session_button=tk.Button()


image_time_dict={"10 seconds": 10,
                 "30 seconds": 30,
                 "1 minute"  : 60,
                 "2 minutes" : 120,
                 "5 minutes" : 300,
                 "10 minutes": 600,
                 "15 minutes": 900,
                 "30 minutes": 1800,
                 "1 hour"    : 3600,
                 }

image_num_dict={
    "1 image"   :1,
    "10 images" :10,
    "15 images" :15,
    "20 images" :20,
    "30 images" :30,
    "40 images" :40,
    "50 images" :50,
    "60 images" :60,
    "120 images":120,
}
def get_folder():
    global FOLDER_PATH,folder_label
    FOLDER_PATH = filedialog.askdirectory(title="Choose a folder")
    folder_label.config(text=f"{FOLDER_PATH}")

def pre_session_ui():
    global image_time_dict,image_num_dict,INDEX,folder_label,LOOP_ID,SESSION_RUNNING
    SESSION_RUNNING=False
    for widget in root.winfo_children():
        widget.destroy()

    #reset index for new session
    INDEX=0
    #choose a file path
    browse_button = tk.Button(root, text="Browse", command=get_folder, font=(FONT_TYPE, FONT_SIZE))
    browse_button.pack(pady=10)

    folder_label = tk.Label(root, text=f"{FOLDER_PATH}", font=(FONT_TYPE, FONT_SIZE))
    folder_label.pack()

    #choose view time per image
    image_time_clicked.set(list(image_time_dict.keys())[0])
    image_time_dropdown = tk.OptionMenu(root, image_time_clicked, *image_time_dict)
    image_time_dropdown.pack()

    #choose number of images to view
    image_num_clicked.set(list(image_num_dict.keys())[0])
    image_num_dropdown = tk.OptionMenu(root, image_num_clicked, *image_num_dict)
    image_num_dropdown.pack()

    #start session
    start_session_button = tk.Button(root, text="Start Session", command=requirement_check, font=(FONT_TYPE, FONT_SIZE))
    start_session_button.pack()


def requirement_check():
    global FOLDER_PATH,IMAGE_TIME,IMAGE_AMOUNT,FOLDER_IMAGES,SESSION_RUNNING
    if FOLDER_PATH == "":
        messagebox.showerror("Error", "Please select a folder")
        return
    #check if there are any images inside the file
    try:
        all_files=os.listdir(FOLDER_PATH)
        image_files = [os.path.join(FOLDER_PATH, f) for f in all_files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if len(image_files) == 0:
            messagebox.showerror("Error", "No images found")
            return
        else:
            random.shuffle(image_files)
            IMAGE_AMOUNT=image_num_dict[image_num_clicked.get()]
            IMAGE_TIME=image_time_dict[image_time_clicked.get()]
            #loops through the shuffled deck and back to 0 if not enough images
            FOLDER_IMAGES = [image_files[i % len(image_files)] for i in range(IMAGE_AMOUNT)]

    except Exception as e:
        messagebox.showerror("Error", f"Could not read the folder:\n{e}")
        return
    #all good start session
    SESSION_RUNNING=True
    session_ui()


def session_ui():
    global which_image_label,current_image_label,central_frame,timer_label,end_session_button
    for widget in root.winfo_children():
        widget.destroy()
    root.update()

    #build frames
    central_frame=tk.Frame(root)
    central_frame.pack(side="top", pady=10)

    forward_button=tk.Button(central_frame, text=">>", command=image_loop, font=(FONT_TYPE, FONT_SIZE))
    forward_button.pack(side="right",padx=10)

    backward_button=tk.Button(central_frame, text="<<", command=backward, font=(FONT_TYPE, FONT_SIZE))
    backward_button.pack(side="left",padx=10)

    which_image_label = tk.Label(central_frame, font=(FONT_TYPE, FONT_SIZE))
    which_image_label.pack(side="top", pady=5)

    current_image_label = tk.Label(root)
    current_image_label.pack(expand=True)

    end_session_button=tk.Button(root, text="End Session", command=pre_session_ui, font=(FONT_TYPE, FONT_SIZE))
    end_session_button.place(relx=0.0,rely=0.0,anchor="nw",x=20,y=13)


    timer_label=tk.Label(root,font=(FONT_TYPE, FONT_SIZE + 2))
    timer_label.place(relx=1.0,rely=0.0,anchor="ne",x=-20,y=15)
    img_time_copy=IMAGE_TIME-1
    timer(img_time_copy)
    image_loop()


def image_loop():
    global INDEX,IMAGE_TIME,current_image_label,which_image_label,FOLDER_IMAGES,LOOP_ID
    delay= IMAGE_TIME * 1000
    if not SESSION_RUNNING:
        return
    if LOOP_ID is not None:
        root.after_cancel(LOOP_ID)
    root.update_idletasks()

    max_width = root.winfo_width()-20
    max_height = root.winfo_height()-70

    if INDEX>=len(FOLDER_IMAGES):
        messagebox.showinfo("Completion","Session has ended")
        pre_session_ui()
        return

    else:
        which_image_label.config(text=f"{INDEX + 1}/{len(FOLDER_IMAGES)}")

        opened_image = Image.open(FOLDER_IMAGES[INDEX])
        opened_image.thumbnail((max_width, max_height))

        displayed_image = ImageTk.PhotoImage(image=ImageOps.contain(opened_image,(max_width,max_height)))

        current_image_label .config( image=displayed_image)
        current_image_label.image = displayed_image
        INDEX+=1
        LOOP_ID=root.after(delay, image_loop)

def backward():
    global INDEX
    if INDEX>=2:
        INDEX-=2
        image_loop()
    else:
        return

def forward():
    return

def timer(time):
    global timer_label

    if SESSION_RUNNING:
        minutes = int(time / 60)
        seconds = time % 60
        timer_label.config(text=f"{minutes:02}:{seconds:02}")

        if time>0:
            time-=1
        else:
            time=IMAGE_TIME-1
        root.after(1000, timer,time)
    else:
        return


pre_session_ui()

root.mainloop()