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
window.title("Tiffany AI")
canvas = tk.Canvas(window, width=563, height=248, bg="#181818")
canvas.create_text(55, 238, text="[ALPHA] 0.01", fill="#FF9E23") # Version number
canvas.pack()




# Image animation setup way to janky.... can you tell is a mix of gemini and online exaples?
image_folder = "E:/ChatBot/Face-Icon" # Change this to the path of your image folder mine is on E:/ 

blink_files = [os.path.join(image_folder, f"blink_{i}.png") for i in range(1, 3)]  # blink_1.png and blink_2.png
talk_files = [os.path.join(image_folder, f"talk_{i}.png") for i in range(1, 3)]  # talk_1.png and talk_2.png


blink_images = []
talk_images = []

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

animation_label = tk.Label(canvas)
animation_label.place(x=20, y=20, width=200, height=200)

animation_running = True
current_animation = "blink"

def animate(frame_index=0, animation_type="blink"):
    global current_animation
    if not animation_running or current_animation != animation_type:
        return
    images = blink_images if animation_type == "blink" else talk_images
    interval = random.randint(1000, 2000) if animation_type == "blink" else random.randint(100, 200)
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

def stop_animation():
    global animation_running
    animation_running = False
    #maybe this is the problem... it doesn't stop the animation! but sometimes it does... janky




response_text = tk.Text(canvas, wrap=tk.WORD, state=tk.DISABLED, bg="#1F1F1F", fg="#FF9E23")
response_text.place(x=250, y=20, width=297, height=155)

input_entry = tk.Entry(canvas,bg="#1F1F1F", fg="#FF9E23")
input_entry.place(x=250, y=200, width=250)
input_entry.bind("<Return>", lambda event: send_message())

VOICE =  "en-IE-EmilyNeural" #"en-IE-EmilyNeural" "en-PH-RosaNeural" "en-GB-MaisieNeural" #"en-TZ-ImaniNeural" nice voices! 
OUTPUT_FILE = "output.mp3"

async def generate_speech(text):
    communicate = edge_tts.Communicate(text, VOICE, rate='+20%', pitch='+10Hz')
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
    response = handle_conversation(user_message) 

    response_text.config(state=tk.NORMAL)
    response_text.delete("1.0", tk.END)
    response_text.insert(tk.END, response + "\n")
    response_text.config(state=tk.DISABLED)
    

    def tts_task():
        
        asyncio.run(generate_speech(response))
        play_speech()
        start_blink_animation()  # the same here... janky

    threading.Thread(target=tts_task).start()

send_button = tk.Button(canvas, text="Send", command=send_message)
send_button.place(x=509, y=197)

start_blink_animation()  # Start blinking when the app starts
window.mainloop()


### ToDo: 
###         Add an icon.
###         Clean the interface. 
###         more expressions? with how complicated an coboluted the code is i dont think so...
###         make so is imposible to change the window res. 
###         change the color of the line that guides the text bc right now is nowere to be seen BC is black in a black background!! 
###         