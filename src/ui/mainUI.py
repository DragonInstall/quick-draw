import os
import random
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

root=tk.Tk()
root.title("Quick Draw")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
app_width = int(screen_width * (2/3))
app_height = screen_height
root.geometry(f"{app_width}x{app_height}")
root.lift()

image_time_clicked= tk.StringVar()
image_num_clicked= tk.StringVar()
folder_path=""
image_time=10
image_amount=1
#global labels (refreshing ones)
current_image_label=tk.Label()
which_image_label=tk.Label()
timer_label=tk.Label()
index=0

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
    global folder_path
    folder_path = filedialog.askdirectory(title="Choose a folder")

def pre_session_ui():
    global image_time_dict,image_num_dict,index
    #reset index for new session
    index=0
    #choose a file path
    browse_button = tk.Button(root, text="Browse", command=get_folder)
    browse_button.pack()

    #choose view time per image
    image_time_clicked.set(list(image_time_dict.keys())[0])
    image_time_dropdown = tk.OptionMenu(root, image_time_clicked, *image_time_dict)
    image_time_dropdown.pack()

    #choose number of images to view
    image_num_clicked.set(list(image_num_dict.keys())[0])
    image_num_dropdown = tk.OptionMenu(root, image_num_clicked, *image_num_dict)
    image_num_dropdown.pack()

    #start session
    start_session_button = tk.Button(root, text="Start Session", command=requirement_check)
    start_session_button.pack()


def requirement_check():
    global folder_path,image_time,image_amount
    if folder_path == "":
        messagebox.showerror("Error", "Please select a folder")
        return
    #check if there are any images inside the file
    try:
        all_files=os.listdir(folder_path)
        image_files = [os.path.join(folder_path,f) for f in all_files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if len(image_files) == 0:
            messagebox.showerror("Error", "No images found")
            return
        else:
            random.shuffle(image_files)
            image_amount=image_num_dict[image_num_clicked.get()]
            image_time=image_time_dict[image_time_clicked.get()]
            #loops through the shuffled deck and back to 0 if not enough images
            session_images = [image_files[i % len(image_files)] for i in range(image_amount)]

    except Exception as e:
        messagebox.showerror("Error", f"Could not read the folder:\n{e}")
        return
    #all good start session
    session_ui(session_images)


def session_ui(session_images):
    for widget in root.winfo_children():
        widget.destroy()
    root.update()
    timer()
    #loop through images until you done
    image_loop(session_images)




def image_loop(session_images):
    global index,image_time,current_image_label,which_image_label

    current_image_label.destroy()
    which_image_label.destroy()
    root.update()

    max_width = root.winfo_width() - 20
    max_height = root.winfo_height() - 20
    if index>=len(session_images):
        messagebox.showinfo("Completion","Session has ended")
        return
    else:
        which_image_label=tk.Label(root,text=f"{index+1}/{len(session_images)}")
        which_image_label.pack(side="top",pady=20)

        opened_image = Image.open(session_images[index])
        opened_image.thumbnail((max_width, max_height))

        displayed_image = ImageTk.PhotoImage(image=opened_image)

        current_image_label = tk.Label(root, image=displayed_image)
        current_image_label.image = displayed_image
        current_image_label.pack(expand=True)
        index+=1
        delay=image_time*1000
        root.after(delay, image_loop, session_images)

def timer():
    global image_time,timer_label


pre_session_ui()

root.mainloop()