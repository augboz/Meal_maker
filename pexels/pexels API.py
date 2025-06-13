import requests
import tkinter as tk
from PIL import Image, ImageTk
import requests
from io import BytesIO


# Your Pexels API key (obtained after signing up)
API_KEY = 'IEZ6AmJlHK6Z925QNk14ITzhmwamUYgZMumd5hpBayO6muG3ZD851edu'

# Base URL for Pexels search endpoint
BASE_URL = 'https://api.pexels.com/v1/search'

# Function to get the image URL of the first result for a given query (dish name in your case)
def get_image_url(query):
    headers = {
        'Authorization': API_KEY
    }
    params = {
        'query': query,
        'per_page': 1  # We're only interested in the first result for simplicity
    }
    response = requests.get(BASE_URL, headers=headers, params=params)
    data = response.json()

    # Extracting the URL of the first image result
    try:
        return data['photos'][0]['src']['medium']
    except (IndexError, KeyError):
        return None  # Return None if there's no result or if there's any error in the response

# Function to fetch and display image in the Tkinter frame
def display_image_in_frame(url, frame):
    response = requests.get(url)
    image_data = BytesIO(response.content)
    image = Image.open(image_data)
    photo = ImageTk.PhotoImage(image)

    # Create a label to display the image
    img_label = tk.Label(frame, image=photo)
    img_label.photo = photo  # Keep a reference to prevent garbage collection
    img_label.pack(padx=5, pady=5)


# Your main window and frame setup (modify as needed)
root = tk.Tk()
frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

# Let's say these are the dishes returned from OpenAI
dishes = ['Spaghetti', 'Tacos', 'Biryani', 'Sushi', 'Salad']

# Fetching image URLs for each dish and displaying them
for dish in dishes:
    img_url = get_image_url(dish)
    if img_url:
        display_image_in_frame(img_url, frame)

root.mainloop()
