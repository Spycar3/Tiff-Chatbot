import tkinter as tk
from PIL import Image, ImageTk
import asyncio
import edge_tts
import threading
import pygame
import os
import random
from main import handle_conversation  

window = tk.Tk()
window.title("Tiffany")
window.resizable(False, False)

canvas = tk.Canvas(window, width=563, height=248, bg="#252728", highlightthickness=0)  
canvas.create_text(80, 235, text="Tiffany_[ALPHA]_0.02", fill="#CFD2D5") 
canvas.pack()

# Load a custom icon!
icon_path = "E:/Chatbot/Face-Icon/Icon.png"  # Replace with your actual file path 
try:
    icon = Image.open(icon_path)
    icon = icon.resize((32, 32), Image.LANCZOS)
    photo_icon = ImageTk.PhotoImage(icon)
    window.iconphoto(True, photo_icon)
except FileNotFoundError:
    print(f"Error: Image file not found: {icon}") 



# Image animation setup way to janky.... can you tell is a mix of gemini and online exaples?

image_folder = "E:/ChatBot/Face-Icon"  # Change this to the path of your image folder mine is on E:/

blink_files = [os.path.join(image_folder, f"blink_{i}.png") for i in range(1, 3)]
talk_files = [os.path.join(image_folder, f"talk_{i}.png") for i in range(1, 3)]
thinking_files = [os.path.join(image_folder, f"thinking_{i}.png") for i in range(1, 3)]

blink_images = []
talk_images = []
thinking_images = []

def load_images(image_files, image_list):
    for file in image_files:
        try:
            image = Image.open(file)
            image = image.resize((200, 200), Image.LANCZOS)
            photo_image = ImageTk.PhotoImage(image)
            image_list.append(photo_image)
        except FileNotFoundError:
            print(f"Error: Image file not found: {file}")
            return False
    return True

if not load_images(blink_files, blink_images):
    blink_images = []
if not load_images(talk_files, talk_images):
    talk_images = []
if not load_images(thinking_files, thinking_images):
    thinking_images = []

animation_label = tk.Label(canvas)
animation_label.place(x=20, y=20, width=200, height=200)

animation_running = True
current_animation = "blink"

def animate(frame_index=0, animation_type="blink"):
    global current_animation
    if not animation_running or current_animation != animation_type:
        return

    images = []
    interval = 0

    if animation_type == "blink":
        images = blink_images
        interval = random.randint(1000, 2000)
    elif animation_type == "talk":
        images = talk_images
        interval = random.randint(100, 200)
    elif animation_type == "thinking":
        images = thinking_images
        interval = random.randint(200, 500)  # Adjust interval as needed

    if not images:
        return

    try:
        animation_label.config(image=images[frame_index])
        animation_label.image = images[frame_index]
    except tk.TclError:
        print("Error: Animation stopped due to TclError")
        return

    frame_index = (frame_index + 1) % len(images)
    window.after(interval, animate, frame_index, animation_type)


# Animation Call func.
def start_blink_animation():
    global animation_running, current_animation
    animation_running = True
    current_animation = "blink"
    animate(animation_type="blink")

def start_talk_animation():
    global animation_running, current_animation
    animation_running = True
    current_animation = "talk"
    animate(animation_type="talk")

def start_thinking_animation():
    global animation_running, current_animation
    animation_running = True
    current_animation = "thinking"
    animate(animation_type="thinking")

def stop_animation():
    global animation_running
    animation_running = False





response_text = tk.Text(canvas, wrap=tk.WORD, state=tk.DISABLED, bg="#333334", fg="#CFD2D5", highlightthickness=0, bd=0)  
response_text.place(x=250, y=20, width=297, height=155)

input_entry = tk.Entry(canvas, bg="#333334", fg="#CFD2D5", highlightthickness=0, bd=0, insertbackground="#CFD2D5")  # Set insertbackground color
input_entry.place(x=250, y=200, width=250)
input_entry.bind("<Return>", lambda event: send_message())

VOICE =  "en-IE-EmilyNeural" #"en-IE-EmilyNeural" "en-PH-RosaNeural" "en-GB-MaisieNeural" #"en-TZ-ImaniNeural" nice voices! 
OUTPUT_FILE = "output.mp3"

async def generate_speech(text):
    communicate = edge_tts.Communicate(text, VOICE, rate='+20%', pitch= '+15Hz')
    await communicate.save(OUTPUT_FILE)

# Play the generated Text to Speech audio file and the Talking animation.
def play_speech():
    try:
        start_talk_animation()  # Start talking animation
        pygame.mixer.init()
        pygame.mixer.music.load(OUTPUT_FILE)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    except pygame.error as e:
        print(f"Pygame error: {e}")
        print("Please ensure audio devices are properly configured.")
    finally:
        pygame.mixer.music.unload() # Unload the audio file and starts blinking again. 
        start_blink_animation() 
        
        
def send_message():
    user_message = input_entry.get()
    input_entry.delete(0, tk.END)

    # Get the chatbot's response from main.py
    
    start_thinking_animation()  # Start thinking animation while waiting for response
    def get_response():
        response = handle_conversation(user_message)
        stop_animation()  # Stop thinking animation when response is received
        start_blink_animation()  # back to blinking

        response_text.config(state=tk.NORMAL)
        response_text.delete("1.0", tk.END)
        response_text.insert(tk.END, response + "\n")
        response_text.config(state=tk.DISABLED)

        def tts_task():
            asyncio.run(generate_speech(response))
            start_thinking_animation()
            play_speech()

        threading.Thread(target=tts_task).start()

    window.after(2000, get_response)  # Wait 2 seconds

send_button = tk.Button(canvas, text="Send", command=send_message)
send_button.place(x=509, y=197)

start_blink_animation()  # Start blinking when the app starts
window.mainloop()



### ToDo: 
###         turn the front into a client,
###         add a character system? not so sure...
###         add a BGM? not sure
###         make so the Talk animation has 4 States. [Happy] [Nerv] [Angry] [Sad]
###         Make so the def play_speech(): selects an animation based on the result of the Text classification model before playing the animation. this will make emotes similar to silly tavern!

###         Future ToDo: 
###                  make her tell the time, wheather and make notes on a diferent ChromaDB collection. 
###                  compile the fornt end. 