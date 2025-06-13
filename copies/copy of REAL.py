import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter import font
from tkinter import messagebox
import sqlite3
import cv2
import PIL.Image, PIL.ImageTk

# Create or connect to the SQLite database
conn = sqlite3.connect("../user_database.db")
cursor = conn.cursor()
# Create a table to store user data if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT)''')
conn.commit()

global username_entry
global password_entry
global ingredients

def login():
    username = username_entry.get()
    password = password_entry.get()

    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()

    if user:
        dashboard()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")

def signup():
    username = username_entry.get()
    password = password_entry.get()

    if username and password:
        try:
            cursor.execute("INSERT INTO users VALUES (?, ?)", (username, password))
            conn.commit()
            messagebox.showinfo("Signup Successful", "Account created for " + username)
            clear_entries()
        except sqlite3.IntegrityError:
            messagebox.showerror("Signup Failed", "Username already exists")
    else:
        messagebox.showerror("Signup Failed", "Username and password are required")

def clear_entries():
    username_entry.delete(0, 'end')
    password_entry.delete(0, 'end')

def loginPage():
    login_page.tkraise()
    username_label = Label(login_page, text="Username:", font=style1)
    username_label.pack(padx=200)
    username_entry = Entry(login_page, font=custom_font)
    username_entry.pack()

    password_label = Label(login_page, text="Password:", font=custom_font)
    password_label.pack()
    password_entry = Entry(login_page, show="*", font=custom_font)
    password_entry.pack()

    login_button = Button(login_page, text="Login", command=dashboard)
    login_button.pack()

    # Sign Up Button
    signup_button = Button(login_page, text="Sign Up", command=signup)
    signup_button.pack()

def dashboard():
    dashboard_page.tkraise()  # Show the dashboard
    my_meals_button = Button(dashboard_page, text="My Meals", command=lambda: my_meals(), font=style1)
    my_meals_button.pack()
    new_meals_button = Button(dashboard_page, text="New Meals", command=lambda: new_meals(), font=style1)
    new_meals_button.pack()

def my_meals():
    my_meals_page.tkraise()
    lb2 = Label(my_meals_page, text="My Meals", font=style1)
    lb2.pack(pady=20)

def show_webcam_in_frame(frame):
    cap = cv2.VideoCapture(0)  # 0 represents the default webcam (you can change this number if you have multiple cameras)

    def update_frame():
        ret, webcam_frame = cap.read()
        if ret:
            # Convert the OpenCV BGR format to RGB format for compatibility with Tkinter
            rgb_frame = cv2.cvtColor(webcam_frame, cv2.COLOR_BGR2RGB)
            img = PIL.Image.fromarray(rgb_frame)
            img = PIL.ImageTk.PhotoImage(image=img)

            # Update the label with the new frame
            frame.configure(image=img)
            frame.image = img

            frame.after(10, update_frame)  # Schedule the next update in 10ms

    update_frame()
    ingredients = [
        "Milk",
        "Eggs",
        "Butter",
        "Cheese",
        "Yogurt",
        "Bacon",
        "Lettuce",
        "Tomatoes",
        "Bell peppers",
        "Carrots",
        "Onions",
        "Garlic",
        "Lemons",
        "Apples",
        "Oranges",
        "Strawberries",
        "Chicken breasts",
        "Ground beef",
        "Fish fillets",
        "Tofu"
    ]

def new_meals():
    new_meals_page.tkraise()
    tick_button = ttk.Button(new_meals_page, text="✓", command=lambda: parameters())
    tick_button.pack()

    # Create a label for displaying the webcam feed
    webcam_label = Label(new_meals_page)
    webcam_label.pack()
    show_webcam_in_frame(webcam_label)

def parameters():
    parameters_page.tkraise()
    lb2 = Label(parameters_page, text="Parameters Page", font=style1)
    lb2.pack(pady=20)
#country
    def update(data):
        # clear the listbox first, to start from scratch
        my_list.delete(0, END)

        # Add countries to listbox
        for item in data:
            my_list.insert(END, item)
    # update entry box with listbox
    def fillout(e):
        # delete everything in entry box
        my_entry.delete(0, END)

        # add clicked list item to entry box
        my_entry.insert(0, my_list.get(ACTIVE))
    # create function to check entry and listbox
    def check(e):
        # grab what was typed
        typed = my_entry.get()

        if typed == '':
            data = countries
        else:
            data = []
            for item in countries:
                if typed.lower() in item.lower():
                    data.append(item)

        update(data)

    my_entry = Entry(parameters_page,)
    my_entry.pack(pady=20)
    my_list = Listbox(parameters_page, width=50)
    my_list.pack(pady=40)
    countries = [
        "United States",
        "Canada",
        "United Kingdom",
        "France",
        "Germany",
        "Spain",
        "Italy",
        "Japan",
        "Australia",
        "India",
        "China",
        "Switzerland",
        "Thailand"
    ]
    update(countries)
    # create a binding on the listbox onclick
    my_list.bind("<<ListboxSelect>>", fillout)
    # create a binding on the entry box
    my_entry.bind("<KeyRelease>", check)

#difficulty
    lb2 = Label(parameters_page, text="Preparation difficulty", font=style1)
    lb2.pack(pady=20)
    r= IntVar()
    r.set(1)
    def clicked(value):
        difficulty=value

    Radiobutton(parameters_page, text="Easy", variable=r, value="1", command=lambda: clicked(r.get())).pack()
    Radiobutton(parameters_page, text="Medium", variable=r, value="2", command=lambda: clicked(r.get())).pack()
    Radiobutton(parameters_page, text="Hard", variable=r, value="3", command=lambda: clicked(r.get())).pack()

#preparation time

    def time_selected(event):
        selected_time = combo.get()
        result_label.config(text=f"Selected Time: {selected_time}")

    # List of time options (replace with your own data if needed)
    time_options = [
        "12:00 AM",
        "1:00 AM",
        "2:00 AM",
        "3:00 AM",
        "4:00 AM",
        "5:00 AM",
        "6:00 AM",
        "7:00 AM",
        "8:00 AM",
        "9:00 AM",
        "10:00 AM",
        "11:00 AM",
        "12:00 PM",
        "1:00 PM",
        "2:00 PM",
        "3:00 PM",
        "4:00 PM",
        "5:00 PM",
        "6:00 PM",
        "7:00 PM",
        "8:00 PM",
        "9:00 PM",
        "10:00 PM",
        "11:00 PM",
    ]

    # Create a Combobox widget for selecting the time
    combo = ttk.Combobox(parameters_page, values=time_options, state="readonly")
    combo.pack(pady=10)
    combo.bind("<<ComboboxSelected>>", time_selected)

    # Create a label to display the selected time
    result_label = ttk.Label(parameters_page, text="", font=("Helvetica", 12))
    result_label.pack(pady=10)

win = tk.Tk()
custom_font = ("Helvetica", 12)
win.geometry("2024x768")  # Adjust as needed for your desired size

style1 = font.Font(size=25)
login_page = Frame(win)
dashboard_page = Frame(win)
my_meals_page = Frame(win)
new_meals_page = Frame(win)
parameters_page = Frame(win)

login_page.grid(row=0, column=0, sticky="nsew")
dashboard_page.grid(row=0, column=0, sticky="nsew")
my_meals_page.grid(row=0, column=0, sticky="nsew")
new_meals_page.grid(row=0, column=0, sticky="nsew")
parameters_page.grid(row=0, column=0, sticky="nsew")


loginPage()
win.geometry("650x650")
win.title("Meal Maker")
win.resizable(False,False)
win.mainloop()