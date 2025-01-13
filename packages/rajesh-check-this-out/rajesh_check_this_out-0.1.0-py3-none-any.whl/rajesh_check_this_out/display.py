import tkinter as tk
from tkinter import messagebox
import random

def show_message():
    emojis = ['🌈']
    message = f"You are rainbow {random.choice(emojis)}"
    print(message)
    return message

def show_popup():
    positive_messages = [
        "Remember: Rainbow is colourful, unlike your life",
        "Learn to live but i would kms if i were you"
    ]
    root = tk.Tk()
    root.withdraw()

    message = random.choice(positive_messages)
    messagebox.showinfo("Rainbow", message)

    root.destroy()