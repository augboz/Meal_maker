import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter import font
from tkinter import messagebox
import customtkinter as ctk
import sqlite3
import PIL.Image, PIL.ImageTk
import openai
from PIL import Image, ImageTk
import requests
from io import BytesIO
import cv2



#connect to the SQLite database
conn = sqlite3.connect("../user_database.db")
cursor = conn.cursor()
# Create a table to store user data if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT)''')
conn.commit()

PEXELS_API_KEY = 'IEZ6AmJlHK6Z925QNk14ITzhmwamUYgZMumd5hpBayO6muG3ZD851edu'

global username_entry
global password_entry
global ingredients

global selected_country
global selected_time
global selected_difficulty
global selected_meal
global selected_diet
selected_country = 0
selected_time = 0
selected_difficulty=0
selected_meal = 0
selected_diet = 0

def login():
    username = username_entry.get()
    password = password_entry.get()

    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()

    if user:
        print("yes")
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
    global username_entry  # Declare as global
    global password_entry  # Declare as global

    login_page.tkraise()
    username_label = ctk.CTkLabel(login_page, text="Username:")
    username_label.grid(row=0, column=0, padx=20, pady=10)

    username_entry = ctk.CTkEntry(login_page, font=custom_font)
    username_entry.grid(row=0, column=1, padx=20, pady=10)

    password_label = ctk.CTkLabel(login_page, text="Password:")
    password_label.grid(row=1, column=0, padx=20, pady=10)

    password_entry = ctk.CTkEntry(login_page, show="*", font=custom_font)
    password_entry.grid(row=1, column=1, padx=20, pady=10)

    login_button = ctk.CTkButton(login_page, text="Login", command=login)
    login_button.grid(row=2, column=0, padx=20, pady=10)

    # Sign Up Button
    signup_button = ctk.CTkButton(login_page, text="Sign Up", command=signup)
    signup_button.grid(row=2, column=1, padx=20, pady=10)

def dashboard():
    dashboard_page.tkraise()  # Show the dashboard

    my_meals_button = ctk.CTkButton(dashboard_page, text="My Meals", command=my_meals)
    my_meals_button.grid()
    new_meals_button = ctk.CTkButton(dashboard_page, text="New Meals", command=new_meals)
    new_meals_button.grid()

def my_meals():
    my_meals_page.tkraise()
    lb2 = ctk.CTkLabel(my_meals_page, text="My Meals")
    lb2.grid(pady=20)

def show_webcam_in_frame(frame):
    global ingredients

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
    return ingredients

def new_meals():
    new_meals_page.tkraise()
    tick_button = ctk.CTkButton(new_meals_page, text="✓",command=lambda: parameters(), cursor="hand2")
    tick_button.grid()

def parameters():
    global selected_country
    global selected_time
    global selected_difficulty
    global selected_meal
    global selected_diet

    # List of country names (replace with your own data if needed)
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

    # List of time options (replace with your own data if needed)
    time_options = [
        "5-10 minutes",
        "15 minutes",
        "20-30 minutes",
        "45 minutes",
        "1 hour",
        "More than 1 hour",
    ]

    parameters_page.tkraise()

    # Check if the meal options are already loaded to avoid duplication
    if hasattr(parameters_page, 'is_loaded') and parameters_page.is_loaded:
        return  # The content is already there, so just return

    parameters_page.is_loaded = True  # Set a flag indicating that the content has been loaded

    lb2 = ctk.CTkLabel(parameters_page, text="Parameters Page")
    lb2.grid(row=0, column=0, columnspan=3, pady=20)

# Country
    def update(data):
        my_list.delete(0, tk.END)
        for item in data:
            my_list.insert(tk.END, item)

    def fillout(e):
        global selected_country
        selected_country = my_list.get(tk.ACTIVE)
        # Get selected index
        selected_index = my_list.curselection()

        # If there's a selection, update the entry
        if selected_index:
            selected_country = my_list.get(selected_index[0])
            my_entry.delete(0, tk.END)
            my_entry.insert(0, selected_country)
        return selected_country

    def check(e):
        typed = my_entry.get()
        if typed == '':
            data = countries
        else:
            data = [item for item in countries if typed.lower() in item.lower()]
        update(data)

    lb2 = ctk.CTkLabel(parameters_page, text="Origin")
    lb2.grid(row=1, column=0, padx=20, pady=20)
    my_entry = ctk.CTkEntry(parameters_page)
    my_entry.grid(row=2, column=0, padx=20, pady=20)

    # Create a frame for the listbox and scrollbar
    listbox_frame = tk.Frame(parameters_page)
    listbox_frame.grid(row=3, column=0, padx=20, pady=5)

    # Create a listbox with a fixed height
    listbox_height = 3  # Adjust this value as needed
    my_list = tk.Listbox(listbox_frame, width=30, height=listbox_height)
    my_list.pack(side=tk.LEFT, fill=tk.Y)

    # Create a scrollbar
    scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=my_list.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Configure the listbox to use the scrollbar
    my_list.config(yscrollcommand=scrollbar.set)

    update(countries)
    my_list.bind("<<ListboxSelect>>", fillout)
    my_entry.bind("<KeyRelease>", check)

# Difficulty
    lb2 = ctk.CTkLabel(parameters_page, text="Preparation difficulty")
    lb2.grid(row=1, column=6, padx=20, pady=20)
    r = tk.IntVar()
    r.set(1)
    def clicked(value):
        global selected_difficulty
        selected_difficulty = value
        if selected_difficulty == 1:
            selected_difficulty ="Easy"
        elif selected_difficulty == 2:
            selected_difficulty ="Medium"
        elif selected_difficulty == 3:
            selected_difficulty ="Hard"
        return selected_difficulty

    ctk.CTkRadioButton(parameters_page, text="Easy", variable=r, value=1, command=lambda: clicked(r.get())).grid(row=2, column=5, padx=20, pady=20)
    ctk.CTkRadioButton(parameters_page, text="Medium", variable=r, value=2, command=lambda: clicked(r.get())).grid(row=2, column=6, padx=20, pady=20)
    ctk.CTkRadioButton(parameters_page, text="Hard", variable=r, value=3, command=lambda: clicked(r.get())).grid(row=2, column=7, padx=20, pady=20)

# Preparation Time
    def time_selected(event):
        global selected_time
        selected_time = combo.get()
        return selected_time

    lb2 = ctk.CTkLabel(parameters_page, text="Preparation time")
    lb2.grid(row=1, column=2, padx=20, pady=20)
    combo = ctk.CTkComboBox(parameters_page, values=time_options, state="readonly")
    combo.grid(row=2, column=2, padx=20, pady=20)
    combo.bind("<<ComboboxSelected>>", time_selected)

# Meal Type Dropdown
    def meal_selected(event):
        global selected_meal
        selected_meal = meal_dropdown.get()
        return selected_meal

    meal_label = ctk.CTkLabel(parameters_page, text="Meal")
    meal_label.grid(row=9, column=0, padx=20, pady=20, sticky="w")
    meal_types = ["Breakfast", "Lunch", "Dinner", "Snack"]
    meal_dropdown = ctk.CTkComboBox(parameters_page, values=meal_types, state="readonly")
    meal_dropdown.grid(row=9, column=1, padx=20, pady=20, columnspan=2, sticky="we")
    meal_dropdown.bind("<<ComboboxSelected>>", meal_selected)

# Diet Restrictions Dropdown
    def diet_selected(event):
        global selected_diet
        selected_diet = diet_dropdown.get()
        return selected_diet

    diet_label = ctk.CTkLabel(parameters_page, text="Diets")
    diet_label.grid(row=7, column=0, padx=20, pady=20, sticky="w")
    diets = ["None", "Vegan", "Vegetarian", "Pescatarian", "Keto"]
    diet_dropdown = ctk.CTkComboBox(parameters_page, values=diets, state="readonly")
    diet_dropdown.grid(row=7, column=1, padx=20, pady=20, columnspan=2, sticky="we")
    diet_dropdown.bind("<<ComboboxSelected>>", diet_selected)


    tick_button = ctk.CTkButton(parameters_page, text="✓", command=lambda: meal_options())
    tick_button.grid()

    return selected_country, selected_time, selected_difficulty, selected_diet, selected_meal

def meal_options():
    global selected_country
    global selected_time
    global selected_difficulty
    global selected_meal
    global selected_diet
    global ingredients
    print("hello")
    meal_options_page.tkraise()

    def on_mousewheel(event, canvas):
        canvas.yview_scroll(int(-1 * (event.delta // 120)), "units")

    # Rebind the mousewheel scrolling every time the page is raised
    if hasattr(meal_options_page, 'canvas'):
        meal_options_page.canvas.bind_all("<MouseWheel>", lambda event: on_mousewheel(event, meal_options_page.canvas))

    # Check if the meal options are already loaded to avoid duplication
    if hasattr(meal_options_page, 'is_loaded') and meal_options_page.is_loaded:
        return  # The content is already there, so just return

    meal_options_page.is_loaded = True  # Set a flag indicating that the content has been loaded

    # Top frame for buttons
    top_frame = ctk.CTkFrame(meal_options_page)
    top_frame.pack(fill='x', pady=10)

    # Buttons
    back_button = ctk.CTkButton(top_frame, text="Back", command=lambda: parameters())
    back_button.pack(side="left", padx=5)

    refresh_button = ctk.CTkButton(top_frame, text="Refresh", command=lambda: meal_options())
    refresh_button.pack(side="right", padx=5)

    my_meals_button = ctk.CTkButton(top_frame, text="My meals", command=lambda: my_meals())
    my_meals_button.pack(side="right", padx=5)

    dish_suggestions = ['Butter chicken:', 'Chicken Tikka Masala:', 'Beef Curry:', 'Lasagna:', 'Sushi:']

    # Fetch and display images with names for each dish suggestion
    for idx, dish in enumerate(dish_suggestions):
        img_url = get_image_url(dish)
        if img_url:
            display_image_with_name(img_url, dish, selected_country, selected_meal, selected_time, meal_options_page)

# Base URL for Pexels search endpoint
BASE_URL = 'https://api.pexels.com/v1/search'

# Function to get the image URL of the first result for a given query
def get_image_url(query):
    headers = {
        'Authorization': PEXELS_API_KEY
    }
    params = {
        'query': query,
        'per_page': 1
    }
    response = requests.get(BASE_URL, headers=headers, params=params)
    data = response.json()
    try:
        return data['photos'][0]['src']['original']
    except (IndexError, KeyError):
        return None

    # Function to display the image with name and other details
def display_image_with_name(url, dish, origin, type, time, container):
    # Fetch the image from the URL
    response = requests.get(url)
    image_data = BytesIO(response.content)
    image = Image.open(image_data)

    # Resize the image to the specified size
    IMAGE_WIDTH = 400
    IMAGE_HEIGHT = 300
    image = image.resize((IMAGE_WIDTH, IMAGE_HEIGHT), Image.Resampling.LANCZOS)

    # Convert PIL Image to CTkImage
    photo = ctk.CTkImage(image)

    # Individual option frame using CustomTkinter
    ind_frame = ctk.CTkFrame(container)
    ind_frame.pack(fill='x', padx=10, pady=10)

    # Image label using CustomTkinter
    img_label = ctk.CTkLabel(ind_frame, image=photo)
    img_label.photo = photo  # Keep a reference to avoid garbage collection
    img_label.pack(side='left', padx=10, pady=10)

    # Container frame for labels
    labels_frame = ctk.CTkFrame(ind_frame)
    labels_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)

    colon_index = dish.find(':')

    # Option name
    name_label = ctk.CTkLabel(labels_frame, text=f"{dish[:colon_index]}", cursor="hand2")
    name_label.pack(anchor='nw')

    # Create a frame for each set of labels (Origin, Type of Meal, Duration)
    origin_frame = ctk.CTkFrame(labels_frame)
    origin_frame.pack(fill='x')
    type_frame = ctk.CTkFrame(labels_frame)
    type_frame.pack(fill='x')
    duration_frame = ctk.CTkFrame(labels_frame)
    duration_frame.pack(fill='x')

    # Origin label
    origin_label = ctk.CTkLabel(origin_frame, text=f"Origin: ")
    origin_value_label = ctk.CTkLabel(origin_frame, text=f"{origin}")
    origin_label.pack(side='left')
    origin_value_label.pack(side='left')

    # Type of Meal label
    type_label = ctk.CTkLabel(type_frame, text=f"Type of Meal: ")
    type_value_label = ctk.CTkLabel(type_frame, text=f"{type}")
    type_label.pack(side='left')
    type_value_label.pack(side='left')

    # Duration label
    duration_label = ctk.CTkLabel(duration_frame, text=f"Duration: ")
    duration_value_label = ctk.CTkLabel(duration_frame, text=f"{time}")
    duration_label.pack(side='left')
    duration_value_label.pack(side='left')

    # Bind click event
    ind_frame.bind("<Button-1>", lambda event, dish=dish: on_frame_click(event, dish))
    img_label.bind("<Button-1>", lambda event, dish=dish: on_frame_click(event, dish))
    name_label.bind("<Button-1>", lambda event, dish=dish: on_frame_click(event, dish))

def on_frame_click(event, dish_name):
    # Code to navigate to the new frame
    # You can use dish_name or other parameters to determine which frame to show
    meal_method(dish_name)

def meal_method(meal):
    meal_method_page.tkraise()

    # Check if the meal options are already loaded to avoid duplication
    if hasattr(meal_method_page, 'is_loaded') and meal_method_page.is_loaded:
        return  # The content is already there, so just return

    print(meal)
    meal_method_page.is_loaded = True  # Set a flag indicating that the content has been loaded

    # Top Frame for buttons in scrollable_frame
    top_frame = (meal_method_page)
    top_frame.grid(row=0, column=0, columnspan=5, sticky='ew')
    # Buttons in top_frame
    back_button = ctk.CTkButton(top_frame, text="Back")
    back_button.grid(row=0, column=0, sticky='w', padx=5)

    my_meals_button = ctk.CTkButton(top_frame, text="My meals")
    my_meals_button.grid(row=0, column=1, sticky='e', padx=5)

    # Meal Details Section
    meal_details_frame = Frame(meal_method_page, bg='white')
    meal_details_frame.grid(row=1, column=0, columnspan=3, sticky='ew', padx=20)

    # Placeholder for Image
    image_placeholder = ctk.CTkLabel(meal_details_frame, text="Image Placeholder", width=20, height=10)
    image_placeholder.grid(row=0, column=0, rowspan=4, padx=10, pady=10)

    # Meal Name and Details
    meal_name_label = ctk.CTkLabel(meal_details_frame, text=f"hi", font=("Helvetica", 16, 'bold'))
    meal_name_label.grid(row=0, column=1, sticky='w', pady=2)
    preparation_label = ctk.CTkLabel(meal_details_frame, text="Preparation time: ", font=("Helvetica", 12))
    preparation_label.grid(row=1, column=1, sticky='w', pady=2)
    difficulty_label = ctk.CTkLabel(meal_details_frame, text="Difficulty: ", font=("Helvetica", 12))
    difficulty_label.grid(row=2, column=1, sticky='w', pady=2)
    origin_label = ctk.CTkLabel(meal_details_frame, text="Origin: ", font=("Helvetica", 12))
    origin_label.grid(row=3, column=1, sticky='w', pady=2)
    allergies_label = ctk.CTkLabel(meal_details_frame, text="Allergies: ", font=("Helvetica", 12))
    allergies_label.grid(row=4, column=1, sticky='w', pady=2)

    # Add to My Meals Button
    add_button = ctk.CTkButton(meal_details_frame, text="+")
    add_button.grid(row=4, column=2, sticky='e', padx=10)

    links_label = ctk.CTkLabel(meal_details_frame, text="Links to other methods online",
                                         font=("Helvetica", 12, 'underline'),
                                         cursor="hand2")
    links_label.grid()

    # Method Section
    method_label = ctk.CTkLabel(meal_method_page, text="Method")
    method_label.grid(row=3, column=0, sticky='w', padx=20)

    # Text Fields as Labels for Method Description
    for i in range(5):  # Adjust the range for the number of steps you have
        method_description_frame = Frame(meal_method_page, bg='white')
        method_description_frame.grid(row=4 + i, column=0, columnspan=3, sticky='ew', padx=20)

        # Alternate the side of the text and image based on whether i is even or odd
        if i % 2 == 0:  # Even
            text_side = 'w'
            image_side = 'e'
            col_text = 0
            col_img = 2
        else:  # Odd
            text_side = 'e'
            image_side = 'w'
            col_text = 2
            col_img = 0

        step_number_label = ctk.CTkLabel(method_description_frame, text=f"{i + 1}.", font=("Helvetica", 12))
        step_number_label.grid(row=0, column=col_text, sticky=text_side, padx=(0, 10))

        method_text_label = ctk.CTkLabel(method_description_frame, text="TextField", width=40, height=5,
                                                   anchor='nw', justify='left')
        method_text_label.grid(row=0, column=col_text, sticky=text_side, padx=(0, 10))

        if i == 3:
            continue
        else:
            image_placeholder_small = ctk.CTkLabel(method_description_frame, width=15, height=5)
            image_placeholder_small.grid(row=0, column=col_img, sticky=image_side, padx=10)


win = ctk.CTk()

custom_font = ("Helvetica", 12)

style1 = font.Font(size=25)
login_page = ctk.CTkFrame(win)
dashboard_page = ctk.CTkFrame(win)
my_meals_page = ctk.CTkFrame(win)
new_meals_page = ctk.CTkFrame(win)
parameters_page = ctk.CTkFrame(win)
meal_options_page = ctk.CTkFrame(win)
meal_method_page = ctk.CTkScrollableFrame(win,
                                                    width=1200,
                                                    height=600,
                                                    scrollbar_button_color="pink",
                                                    scrollbar_button_hover_color="black",
                                                    corner_radius=30
                                                    )

login_page.grid(row=0, column=0, sticky="nsew")
dashboard_page.grid(row=0, column=0, sticky="nsew")
my_meals_page.grid(row=0, column=0, sticky="nsew")
new_meals_page.grid(row=0, column=0, sticky="nsew")
parameters_page.grid(row=0, column=0, sticky="nsew")
meal_options_page.grid()
meal_method_page.grid(row=0, column=0, sticky="nsew")


loginPage()
win.geometry("1200x600")
win.title("Meal Maker")
win.resizable(False,False)
win.mainloop()