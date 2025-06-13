import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter import messagebox

import customtkinter as ctk
import sqlite3
import openai
from openai import OpenAI
from PIL import Image, ImageTk
import requests
from io import BytesIO
import io

# connect to the SQLite database
conn = sqlite3.connect("user_database.db")
cursor = conn.cursor()
# Create a table to store user data if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT,
                    ingredients TEXT)''')
conn.commit()

PEXELS_API_KEY = 'LSsKoV2b3CAeztPTdVmkk8zEVCLkSDgARdyVeArddCz35plCZGs1Xom2'

global current_user, username_entry, password_entry

global selected_country, selected_time, selected_difficulty, selected_meal, selected_diet, selected_ingredients

global login_page, dashboard_page, parameters_page, new_meals_page, tabview, meal_options_page, meal_method_page, my_meals_page
selected_country = 0
selected_time = 0
selected_difficulty = 0
selected_meal = 0
selected_diet = 0
selected_ingredients = []



def login():
    global current_user

    username = username_entry.get()
    password = password_entry.get()

    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()

    if user:
        current_user = username
        login_page.pack_forget()
        dashboard()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")
        clear_entries()


def signup():
    username = username_entry.get()
    password = password_entry.get()

    if username and password:
        try:
            # Connect to the main users database and insert the new user
            main_conn = sqlite3.connect('user_database.db')
            main_cursor = main_conn.cursor()
            main_cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (username, password, 0))

            main_conn.commit()
            main_conn.close()

            messagebox.showinfo("Signup Successful", "Account created for " + username)
            clear_entries()
        except sqlite3.IntegrityError:
            messagebox.showerror("Signup Failed", "Username already exists")
        else:
            messagebox.showerror("Signup Failed", "Username and password are required")


def clear_entries():
    username_entry.delete(0, 'end')
    password_entry.delete(0, 'end')


# Define the loginPage function
def loginPage():
    global username_entry, password_entry, login_page

    login_label = ctk.CTkLabel(login_page, text="Login Page")
    login_label.place(relx=0.48, rely=0.2)  # Span across both columns

    username_label = ctk.CTkLabel(login_page, text="Username:")
    username_label.place(relx=0.38, rely=0.3)

    username_entry = ctk.CTkEntry(login_page, font=custom_font)
    username_entry.place(relx=0.48, rely=0.3)

    password_label = ctk.CTkLabel(login_page, text="Password:")
    password_label.place(relx=0.38, rely=0.4)

    password_entry = ctk.CTkEntry(login_page, show="*", font=custom_font)
    password_entry.place(relx=0.48, rely=0.4)

    login_button = ctk.CTkButton(login_page, text="Login", command=login)
    login_button.place(relx=0.35, rely=0.5)

    signup_button = ctk.CTkButton(login_page, text="Sign Up", command=signup)
    signup_button.place(relx=0.55, rely=0.5)


def dashboard():
    global dashboard_page, my_meals_page
    dashboard_page = ctk.CTkFrame(win)
    dashboard_page.pack()


    dashboard_page.tkraise()  # Show the dashboard

    my_meals_button = ctk.CTkButton(dashboard_page, text="My Meals", command=my_meals)
    my_meals_button.grid()
    new_meals_button = ctk.CTkButton(dashboard_page, text="New Meals", command=new_meals_before)
    new_meals_button.grid()


def back0():
    my_meals_page.pack_forget()
    dashboard()


def my_meals():
    global current_user, dashboard_page, my_meals_page

    # Hide the dashboard page
    dashboard_page.destroy()

    # Create and configure the My Meals page
    my_meals_page = ctk.CTkFrame(master=win, width=1200, height=700)
    my_meals_page.pack()

    my_meals_page.tkraise()

    user_db_name = 'user_database.db'

    # Clear the previous content
    for widget in my_meals_page.winfo_children():
        widget.destroy()

    # Title label
    lb2 = ctk.CTkLabel(my_meals_page, text="My Meals", font=("Helvetica", 36, "bold"))
    lb2.place(relx=0.38, rely=0.05)

    # Back button
    back_button = ctk.CTkButton(my_meals_page, text="Back", command=lambda: back0())
    back_button.place(relx=0.58, rely=0.05)

    # New Meal button
    my_meals_button = ctk.CTkButton(my_meals_page, text="New Meal", command=lambda: new_meals())
    my_meals_button.place(relx=0.78, rely=0.05)

    try:
        user_conn = sqlite3.connect(user_db_name)
        user_cursor = user_conn.cursor()
        user_cursor.execute(f"SELECT * FROM {current_user}")
        meals = user_cursor.fetchall()

        # Create a grid for 8 possible meals
        for i, meal in enumerate(meals):
            if i >= 8:
                break

            dish_name, origin, preparation_time, image_url = meal

            # Calculate row and column for the current grid
            row = i // 4  # 4 columns per row
            col = i % 4

            # Create a frame for each meal
            meal_frame = ctk.CTkFrame(my_meals_page, width=280, height=400, corner_radius=20)
            meal_frame.place(relx=0.2 + col * 0.25, rely=0.2 + row * 0.25)

            # Add meal details
            parts = dish_name.split(': ', 1)
            name = parts[0]
            dish_name = name.split('. ', 1)[1] if '. ' in name else name
            description = parts[1] if len(parts) > 1 else ''

            tk.Label(meal_frame, text=dish_name, font=("Helvetica", 20)).place(relx=0.25, rely=0.05)
            tk.Label(meal_frame, text=description , font=("Helvetica", 16)).place(relx=0.1, rely=0.15)
            tk.Label(meal_frame, text=f"Origin: {origin}", font=("Helvetica", 16)).place(relx=0.1, rely=0.25)

            # Fetch and display the image
            response = requests.get(image_url)
            img_data = response.content
            img = Image.open(io.BytesIO(img_data))
            img = img.resize((500, 500))  # Resize to 500x500
            photo = ImageTk.PhotoImage(img)

            # Create a label for the image and place it in the center
            img_label = tk.Label(meal_frame, image=photo)
            img_label.image = photo
            img_label.place(relx=0.1, rely=0.45)

        user_conn.close()

    except sqlite3.Error as error:
        messagebox.showerror("Error", f"Failed to fetch meals: {error}")


def new_meals_before():
    global pop
    pop = Toplevel(win)
    pop.title("Options")
    pop.geometry("800x450")

    pop_label = ctk.CTkLabel(pop, text="Keep/edit your current ingredients from your fridge or input new ingredients")
    pop_label.pack()

    yes = ctk.CTkButton(pop, text="Keep/edit", command=lambda: new_meals("yes"))
    yes.pack(pady=5)
    no = ctk.CTkButton(pop, text="New", command=lambda: new_meals("no"))
    no.pack(pady=5)

def new_meals(choice):
    global new_meals_page, dashboard_page, my_meals_page, tabview, selected_ingredients, current_user
    global pop
    pop.destroy()

    dashboard_page.pack_forget()

    new_meals_page = ctk.CTkFrame(win,
                                  width=1200,
                                  height=700,
                                  corner_radius=20,
                                  )
    new_meals_page.place(relx=0.0, rely=0.0)

    tabview = ctk.CTkTabview(new_meals_page, width=600,
                                  height=600,
                             )
    tabview.place(relx=0.1, rely=0.1)

    tabview.add("dairy")  # add tab at the end
    tabview.add("meats")  # add tab at the end
    tabview.add("other")  # add tab at the end
    tabview.set("dairy")  # set currently visible tab

    #dairy
    # Create a Listbox for dairy foods
    dairy_listbox = tk.Listbox(tabview.tab("dairy"), selectmode=tk.SINGLE, height=50, width=30, font=("Helvetica", 13))
    dairy_listbox.place(relx=0.1, rely=0.1)
    # Function to add the selected dairy food to the selected ingredients Listbox
    def add_ingredients():
        selected_index = dairy_listbox.curselection()
        if selected_index:
            selected_dairy_food = dairy_listbox.get(selected_index[0])
            selected_ingredients.append(selected_dairy_food)  # Append to the global list
            selected_ingredients_listbox.insert(tk.END, selected_dairy_food)
    # Create an Add Ingredient button
    add_ingredient_button = ctk.CTkButton(tabview.tab("dairy"), text="Add Ingredient", command=add_ingredients, hover_color="navy")
    add_ingredient_button.place(relx=0.7, rely=0.54)
    # Create a Listbox for selected ingredients
    selected_ingredients_listbox = tk.Listbox(new_meals_page, selectmode=tk.SINGLE, height=22, width=20, font=("Helvetica", 15))
    selected_ingredients_listbox.place(relx=0.62, rely=0.15)
    # Define a list of dairy foods
    dairy_foods = [
        "Milk",
        "Butter",
        "Yogurt",
        "Cheese",
        "Swiss Cheese",
        "Brie Cheese",
        "Mozzarella",
        "Eggs",
        "Sour Cream",
        "Cream Cheese",
        "Ricotta Cheese",
        "Mascarpone Cheese",
        "Cream Cheese",
        "Whipped Cream",
        "Heavy Cream",
        "Parmesan Cheese",
        "Feta Cheese",
        "Paneer",
        "Ice cream",
        "Goat Cheese",
    ]
    # Function to update the dairy Listbox
    def update_dairy_list(data):
        dairy_listbox.delete(0, tk.END)
        for item in data:
            dairy_listbox.insert(tk.END, item)
    # Function to handle item selection in the dairy Listbox
    def select_dairy_item(e):
        global selected_dairy_food
        selected_index = dairy_listbox.curselection()

        if selected_index:
            selected_dairy_food = dairy_listbox.get(selected_index[0])
    # Bind the select_dairy_item function to the dairy Listbox
    dairy_listbox.bind('<<ListboxSelect>>', select_dairy_item)
    # Initially, populate the dairy Listbox with dairy food items
    update_dairy_list(dairy_foods)

    if choice == "yes":
        # Populate selected ingredients from the database
        print("yes")
        user_db_name = 'user_database.db'
        conn = sqlite3.connect(user_db_name)
        cursor = conn.cursor()

        # Execute the SQL statement to retrieve the selected ingredients
        cursor.execute("SELECT ingredients FROM users WHERE username = ?", (current_user,))
        ingredients = cursor.fetchone()

        if ingredients:
            selected_ingredients = ingredients[0].split(', ')
            selected_ingredients_listbox.delete(0, tk.END)
            for ingredient in selected_ingredients:
                selected_ingredients_listbox.insert(tk.END, ingredient)

#meats
    # Create a Listbox for meet foods
    meats_listbox = tk.Listbox(tabview.tab("meats"), selectmode=tk.SINGLE, height=50, width=30, font=("Helvetica", 13))
    meats_listbox.place(relx=0.1, rely=0.1)
    # Function to add the selected meat food to the selected ingredients Listbox
    def add_ingredients():
        selected_index = meats_listbox.curselection()
        if selected_index:
            selected_meats_food = meats_listbox.get(selected_index[0])
            selected_ingredients.append(selected_meats_food)  # Append to the global list
            selected_ingredients_listbox.insert(tk.END, selected_meats_food)
    # Create an Add Ingredient button
    add_ingredient_button = ctk.CTkButton(tabview.tab("meats"), text="Add Ingredient", command=add_ingredients, hover_color="navy")
    add_ingredient_button.place(relx=0.7, rely=0.54)
    # Define a list of meat foods
    meat_foods = [
        "Chicken",
        "Beef",
        "Pork",
        "Lamb",
        "Turkey",
        "Duck",
        "Salmon",
        "Tuna",
        "Shrimp",
        "Crab",
        "Sausages",
        "Bacon",
        "Ham",
        "Pepperoni",
        "Ground Beef",
        "Steak",
        "Chorizo",
    ]
    def update_meats_list(data):
        meats_listbox.delete(0, tk.END)
        for item in data:
            meats_listbox.insert(tk.END, item)
    def select_meats_item(e):
        global selected_meats_food
        selected_index = meats_listbox.curselection()

        if selected_index:
            selected_meats_food = meats_listbox.get(selected_index[0])

    meats_listbox.bind('<<ListboxSelect>>', select_meats_item)
    # Initially, populate the dairy Listbox with dairy food items
    update_meats_list(meat_foods)

#other
    other_listbox = tk.Listbox(tabview.tab("other"), selectmode=tk.SINGLE, height=50, width=30,
                                   font=("Helvetica", 13))
    other_listbox.place(relx=0.1, rely=0.1)
    def add_ingredients():
        selected_index = other_listbox.curselection()
        global selected_ingredients
        if selected_index:
            selected_other_food = other_listbox.get(selected_index[0])
            selected_ingredients.append(selected_other_food)  # Append to the global list
            selected_ingredients_listbox.insert(tk.END, selected_other_food)
    add_ingredient_button = ctk.CTkButton(tabview.tab("other"), text="Add Ingredient", command=add_ingredients, hover_color="green")
    add_ingredient_button.place(relx=0.7, rely=0.54)
    other_foods = [
        "Tofu",
        "Apple", "Banana", "Orange", "Strawberry", "Grapes",
        "Carrot", "Broccoli", "Spinach", "Tomato", "Cucumber", "Salad",
        "Hummus",
        "Salad Dressing",
        "Ketchup",
        "Mustard",
        "Mayonnaise",
        "Pickles",
        "Olives",
        "Salsa",
        "hot sauce",
        "soy sauce"
    ]
    def update_other_list(data):
        other_listbox.delete(0, tk.END)
        for item in data:
            other_listbox.insert(tk.END, item)
    def select_other_item(e):
        global selected_other_food
        selected_index = other_listbox.curselection()
        if selected_index:
            selected_other_food = other_listbox.get(selected_index[0])
    other_listbox.bind('<<ListboxSelect>>', select_other_item)
    update_other_list(other_foods)

###########
    # Create an Entry widget for ingredient search
    search_entry = tk.Entry(new_meals_page, font=("Helvetica", 15))
    search_entry.place(relx=0.55, rely=0.05, width=200)

    # Function to add the searched ingredient to selected_ingredients
    def add_searched_ingredient():
        searched_ingredient = search_entry.get()
        if searched_ingredient:
            selected_ingredients.append(searched_ingredient)
            selected_ingredients_listbox.insert(tk.END, searched_ingredient)
            # Clear the search Entry after adding
            search_entry.delete(0, tk.END)

    # Create an Add Ingredient button for the searched ingredient
    add_searched_button = ctk.CTkButton(new_meals_page, text="Add Ingredient", command=add_searched_ingredient,
                                        hover_color="green")
    add_searched_button.place(relx=0.75, rely=0.05)


    # Add this function to delete selected ingredients
    def delete_ingredient():
        selected_index = selected_ingredients_listbox.curselection()
        if selected_index:
            selected_ingredients.pop(selected_index[0])
            selected_ingredients_listbox.delete(selected_index)

    # Create a Delete Ingredient button
    delete_ingredient_button = ctk.CTkButton(new_meals_page, text="Delete Ingredient", command=delete_ingredient,
                                             hover_color="red")
    delete_ingredient_button.place(relx=0.83, rely=0.54)
    selected_ingredients_listbox.bind('<BackSpace>', lambda event=None: delete_ingredient())

    tick_button = ctk.CTkButton(new_meals_page, text="✓", command=lambda: update_ingredients())
    tick_button.place(relx=0.85, rely=0.9)

    My_meals = ctk.CTkLabel(new_meals_page, text="Any other ingredients:")
    My_meals.place(relx=0.41, rely=0.05)


def update_ingredients():
    global selected_ingredients, current_user

    user_db_name = 'user_database.db'
    conn = sqlite3.connect(user_db_name)
    cursor = conn.cursor()

    # Convert the list of selected ingredients into a string with commas
    ingredients_str = ', '.join(selected_ingredients)

    # Define the SQL statement to update the users table with selected ingredients
    update_sql = "UPDATE users SET ingredients = ? WHERE username = ?"

    # Execute the SQL statement to update the table
    cursor.execute(update_sql, (ingredients_str, current_user))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    parameters()


def parameters():
    global selected_country, selected_time, selected_difficulty, selected_meal, selected_diet
    global new_meals_page, parameters_page, tabview

    new_meals_page.destroy()

    parameters_page = ctk.CTkFrame(win,
                                   width=1200,
                                   height=700)
    parameters_page.place(relx=0, rely=0)

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
            selected_difficulty = "Easy"
        elif selected_difficulty == 2:
            selected_difficulty = "Medium"
        elif selected_difficulty == 3:
            selected_difficulty = "Hard"

    ctk.CTkRadioButton(parameters_page, text="Easy", variable=r, value=1, command=lambda: clicked(r.get())).grid(row=2,
                                                                                                                 column=5,
                                                                                                                 padx=20,
                                                                                                                 pady=20)
    ctk.CTkRadioButton(parameters_page, text="Medium", variable=r, value=2, command=lambda: clicked(r.get())).grid(
        row=2, column=6, padx=20, pady=20)
    ctk.CTkRadioButton(parameters_page, text="Hard", variable=r, value=3, command=lambda: clicked(r.get())).grid(row=2,
                                                                                                                 column=7,
                                                                                                                 padx=20,
                                                                                                                 pady=20)

    # Preparation Time
    def time_selected(choice):
        global selected_time
        selected_time = choice

    lb2 = ctk.CTkLabel(parameters_page, text="Preparation time")
    lb2.grid(row=1, column=2, padx=20, pady=20)
    combo = ctk.CTkComboBox(parameters_page, values=time_options, state="readonly", command=time_selected)
    combo.grid(row=2, column=2, padx=20, pady=20)

    # Meal Type Dropdown
    def meal_selected(choice):
        global selected_meal
        selected_meal = choice

    meal_label = ctk.CTkLabel(parameters_page, text="Meal")
    meal_label.grid(row=9, column=0, padx=20, pady=20, sticky="w")
    meal_types = ["Breakfast", "Lunch", "Dinner", "Snack", "Any"]
    meal_dropdown = ctk.CTkComboBox(parameters_page, values=meal_types, state="readonly", command=meal_selected)
    meal_dropdown.grid(row=9, column=1, padx=20, pady=20, columnspan=2, sticky="we")

    # Diet Restrictions Dropdown
    def diet_selected(choice):
        global selected_diet
        selected_diet = choice

    diet_label = ctk.CTkLabel(parameters_page, text="Diets")
    diet_label.grid(row=7, column=0, padx=20, pady=20, sticky="w")
    diets = ["None", "Vegan", "Vegetarian", "Pescatarian", "Keto"]
    diet_dropdown = ctk.CTkComboBox(parameters_page, values=diets, state="readonly", command=diet_selected)
    diet_dropdown.grid(row=7, column=1, padx=20, pady=20, columnspan=2, sticky="we")

    tick_button = ctk.CTkButton(parameters_page, text="✓", command=lambda: meal_options())
    tick_button.grid()


def meal_options():
    global selected_country, selected_time, selected_difficulty, selected_meal, selected_diet, selected_ingredients
    global meal_options_page, parameters_page
    global dish_suggestions

    parameters_page.destroy()
    meal_options_page = ctk.CTkFrame(win,
                                     width=500,
                                     height=300,
                                     corner_radius=20,
                                     )
    meal_options_page.pack()

    meal_options_page.tkraise()

    # Check if the meal options are already loaded to avoid duplication
    if hasattr(meal_options_page, 'is_loaded') and meal_options_page.is_loaded:
        return  # The content is already there, so just return

    meal_options_page.is_loaded = True  # Set a flag indicating that the content has been loaded

    # Top frame for buttons
    top_frame = ctk.CTkFrame(meal_options_page)
    top_frame.pack(fill='x', pady=10)

    # Buttons
    back_button = ctk.CTkButton(top_frame, text="Back", command=lambda: back1())
    back_button.pack(side="left", padx=5)

    my_meals_button = ctk.CTkButton(top_frame, text="My meals", command=lambda: my_meals())
    my_meals_button.pack(side="right", padx=5)

    dish_suggestions = 0
    get_prompts(selected_ingredients, selected_country,
                selected_time,
                selected_difficulty,
                selected_diet,
                selected_meal)


    counter = 0
    # Fetch and display images with names for each dish suggestion
    # Splitting the text into individual recipes
    recipes = dish_suggestions.strip().split('\n\n')

    for dish in recipes:
        print(dish)
        img_url=get_image_url(dish)
        counter +=1
        if img_url:
            if counter == 1:
                display_image_with_name(img_url, dish, selected_country, selected_meal, selected_time,
                                        meal_options_page, 'top')
            elif counter == 2:
                display_image_with_name(img_url, dish, selected_country, selected_meal, selected_time,
                                        meal_options_page, 'top')
            elif counter == 3:
                display_image_with_name(img_url, dish, selected_country, selected_meal, selected_time,
                                        meal_options_page, 'bottom')
            else:
                display_image_with_name(img_url, dish, selected_country, selected_meal, selected_time,
                                        meal_options_page, 'bottom')


def back1():
    meal_options_page.pack_forget()
    parameters()


def get_prompts(selected_ingredients, selected_country, selected_time, selected_difficulty, selected_diet, selected_meal):
    # Get question from form data
    global method_output, dish_suggestions

    question = (
        f"Given the ingredients {selected_ingredients}, I'm looking for 4 dishes that originate from {selected_country}, "
        f"have a preparation time of {selected_time}, are {selected_difficulty} to prepare, "
        f"fit the dietary preference of {selected_diet}, and are suitable for {selected_meal}. "
        f"Please provide 4 dish suggestions based on these preferences, each with a short description. Don't output anything else apart from the 4 dishes. Ignore any zeros"
    )
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system",
             "content": "You are a professional chef and have access to infinite recipes and dishes."},
            {"role": "user", "content": f"{question}"}
        ]
    )

    # Extract the 5 dish suggestions from the API response

    dish_suggestions = response.choices[0].message.content
    return dish_suggestions


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


def display_image_with_name(url, dish, origin, type, time, container, position):
    response = requests.get(url)
    image_data = BytesIO(response.content)
    image = Image.open(image_data)

    # Resize the image
    IMAGE_WIDTH, IMAGE_HEIGHT = 500, 300
    image = image.resize((IMAGE_WIDTH, IMAGE_HEIGHT), Image.Resampling.LANCZOS)

    # Convert PIL Image to PhotoImage
    photo = ImageTk.PhotoImage(image)

    # Create a frame for the image and its details
    ind_frame = ctk.CTkFrame(container, cursor="hand2")
    ind_frame.pack(side=position, padx=10, pady=10)

    # Image label
    img_label = tk.Label(ind_frame, image=photo, cursor="hand2")
    img_label.photo = photo  # Keep a reference
    img_label.pack(side='left', padx=10, pady=10)

    # Container frame for labels
    labels_frame = ctk.CTkFrame(ind_frame, cursor="hand2")
    labels_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)

    parts = dish.split(': ', 1)
    dish_name = parts[0]

    # Dish name label
    name_label = ctk.CTkLabel(labels_frame, text=dish_name, cursor="hand2")
    name_label.pack(anchor='nw')

    # Packing origin, type, and duration labels
    pack_label_pair(labels_frame, "Origin", origin)
    pack_label_pair(labels_frame, "Meal", type)
    pack_label_pair(labels_frame, "Preparation", time)

    # Bind click event to the frame and its children
    bind_click_event(ind_frame, url, dish, origin, type, time)
    bind_click_event(img_label, url, dish, origin, type, time)
    bind_click_event(name_label, url, dish, origin, type, time)


def pack_label_pair(frame, label_text, value_text):
    # Helper function to pack a pair of labels (label and value)
    label_frame = ctk.CTkFrame(frame)
    label_frame.pack(fill='x')
    label = ctk.CTkLabel(label_frame, text=f"{label_text}: ", cursor="hand2")
    value_label = ctk.CTkLabel(label_frame, text=f"{value_text}", cursor="hand2")
    label.pack(side='left')
    value_label.pack(side='left')


def bind_click_event(widget, url, dish, origin, type, time):
    # Helper function to bind click event to a widget.
    widget.bind("<Button-1>", lambda event, dish=dish: on_frame_click(url, dish, origin, type, time))


def on_frame_click(url, dish, origin, type, time):
    # Code to navigate to the new frame
    meal_method(url, dish, origin, type, time)


def meal_method(url, dish, origin, type, time):
    global meal_method_page, meal_options_page

    meal_options_page.pack_forget()

    meal_method_page = ctk.CTkFrame(win,
                                    width=500,
                                    height=300,
                                    corner_radius=20,
                                    )
    meal_method_page.pack()
    meal_method_page.tkraise()

    # Top Frame for buttons in scrollable_frame
    top_frame = ctk.CTkFrame(meal_method_page)
    top_frame.grid(row=0, column=0, columnspan=5, sticky='ew')
    # Buttons in top_frame
    back_button = ctk.CTkButton(top_frame, text="Back", command=lambda: back2())
    back_button.grid(row=0, column=0, sticky='w', padx=5)

    my_meals_button = ctk.CTkButton(top_frame, text="My meals", command=lambda: next1())
    my_meals_button.grid(row=0, column=1, sticky='e', padx=5)

    # Meal Details Section
    meal_details_frame = Frame(meal_method_page, bg='white')
    meal_details_frame.grid(row=1, column=0, columnspan=3, sticky='ew', padx=20)

    # Image
    response = requests.get(url)
    image_data = BytesIO(response.content)
    image = Image.open(image_data)

    # Resize the image
    IMAGE_WIDTH, IMAGE_HEIGHT = 400, 200
    image = image.resize((IMAGE_WIDTH, IMAGE_HEIGHT), Image.Resampling.LANCZOS)

    # Convert PIL Image to PhotoImage
    photo = ImageTk.PhotoImage(image)

    # Image label
    img_label = tk.Label(meal_details_frame, image=photo)
    img_label.photo = photo  # Keep a reference
    img_label.grid(row=0, column=0, sticky='w', pady=2)

    # Meal Name and Details
    parts = dish.split(': ', 1)
    name = parts[0]
    dish_name = name.split('. ', 1)[1] if '. ' in name else name
    description = parts[1] if len(parts) > 1 else ''

    meal_name_label = ctk.CTkLabel(meal_details_frame, text=f"{dish_name}", font=("Helvetica", 16, 'bold'))
    meal_name_label.grid(row=0, column=1, sticky='w', pady=2)
    meal_des_label = ctk.CTkLabel(meal_details_frame, text=f"{description}", font=("Helvetica", 12))
    meal_des_label.grid(row=1, column=1, sticky='w', pady=2)
    preparation_label = ctk.CTkLabel(meal_details_frame, text=f"Preparation time: {time}")
    preparation_label.grid(row=2, column=1, sticky='w', pady=2)
    origin_label = ctk.CTkLabel(meal_details_frame, text=f"Origin: {origin}", font=("Helvetica", 12))
    origin_label.grid(row=4, column=1, sticky='w', pady=2)
    allergies_label = ctk.CTkLabel(meal_details_frame, text=f"Meal: {type}", font=("Helvetica", 12))
    allergies_label.grid(row=5, column=1, sticky='w', pady=2)

    # Add to My Meals Button
    global current_user
    add_button = ctk.CTkButton(meal_details_frame, text="+",
                               command=lambda: add_meal_to_database(current_user, dish, origin, time, url))
    add_button.grid(row=4, column=2, sticky='e', padx=10)

    links_label = ctk.CTkLabel(meal_details_frame, text="Links to other methods online", cursor="hand2")
    links_label.grid()

    # Method Section
    method_label = ctk.CTkLabel(meal_method_page, text="Method")
    method_label.grid(row=3, column=0, sticky='w', padx=20)

    global step_by_step
    method_for_meal(dish, time)

    counter = 0
    # Text Fields as Labels for Method Description
    steps = step_by_step.strip().split('\n\n')
    print(steps)
    for step in steps:  # Adjust the range for the number of steps you have
        counter += 1
        method_description_frame = Frame(meal_method_page, bg='white')
        method_description_frame.grid(row=4 + counter, column=0, columnspan=3, sticky='ew', padx=20)

        method_text_label = ctk.CTkLabel(method_description_frame, text=f"{step}", width=40, height=5,
                                         anchor='nw', justify='left')
        method_text_label.grid(row=0, column=2, padx=(0, 10))


def back2():
    meal_method_page.pack_forget()
    meal_options()


def next1():
    meal_method_page.pack_forget()
    my_meals()


# Function to get prompts and return dish suggestions
def method_for_meal(dish, time):
    # Get question from form data
    global step_by_step

    question = (
        f"Generate a numbered step by step cooking method for a dish named {dish}, with a preparation time of {time}. Maximum 8 steps, each steps maximum 20 words"
    )

    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system",
             "content": "You are a professional chef and have access to infinite recipes and dishes."},
            {"role": "user", "content": f"{question}"}
        ]
    )

    step_by_step = response.choices[0].message.content

    return step_by_step


def add_meal_to_database(current_user, dish, origin, time, url):
    print(current_user)
    if dish and origin and time and url:
        try:
            user_conn = sqlite3.connect('user_database.db')
            user_cursor = user_conn.cursor()

            # Create the user's table if it doesn't exist
            user_cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {current_user} (dish_name TEXT, origin TEXT, preparation_time TEXT, image_url TEXT)")

            # Insert the meal data into the user's table
            user_cursor.execute(
                f"INSERT INTO {current_user} (dish_name, origin, preparation_time, image_url) VALUES (?, ?, ?, ?)",
                (dish, origin, time, url))
            user_conn.commit()
            user_conn.close()
            messagebox.showinfo("Success", "Meal added successfully")
            # Clear the entries if needed or perform other actions
        except sqlite3.Error as error:
            messagebox.showerror("Error", f"Failed to add meal to the database: {error}")
    else:
        messagebox.showerror("Error", "All fields are required to add a meal")


win = ctk.CTk()
win.geometry("1200x700")  # Set the initial size to 500x400 pixels (width x height)
win.resizable(False, False)

custom_font = ("Helvetica", 12)

# Create and place the login page
login_page = ctk.CTkFrame(master=win,
                          width=1200,
                          height=700,
                          corner_radius=20)
login_page.pack()

# Call the function to set up the login page
loginPage()

# Main application loop
win.mainloop()
