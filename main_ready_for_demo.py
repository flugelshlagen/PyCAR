# Libraries/Modules Import
import RPi.GPIO as GPIO
from tkinter import *
import math
import threading
import time
from gpiozero import DistanceSensor
from gpiozero import LED
from picamera2 import Picamera2
from pynput.keyboard import Key, Listener

#   ====================== Global Vars ======================
FRONT_PIN_1_GPIO = 17
FRONT_PIN_2_GPIO = 27
FRONT_PIN_7_GPIO = 22

FRONT_PIN_9_GPIO = 23
FRONT_PIN_10_GPIO = 24
FRONT_PIN_15_GPIO = 25

BACK_PIN_1_GPIO = 5
BACK_PIN_2_GPIO = 6
BACK_PIN_7_GPIO = 13

BACK_PIN_9_GPIO = 16
BACK_PIN_10_GPIO = 20
BACK_PIN_15_GPIO = 21
forward_flag = True

SWITCH_BUTTON_GPIO = 2

# OBJECT DETECTION
PIN_echo = 15
PIN_trigger = 14
PIN_led = 3
MIN_obs_dis = 10#cm

GPIO.setmode(GPIO.BCM)

#   ====================== GUI ======================
def open_map(root):
    
    def blink_running_ui():
        canvas.create_oval(8, 11, 18, 21, fill="green",outline="black")
        label=Label(canvas, text="Online")
        label.place(x=22, y=2)
        label.config(bg="white",fg="black", font=('Arial', 16))
        
        while True:
            label.config(text="Online.")
            time.sleep(1)
            label.config(text="Online..")
            time.sleep(1)
            label.config(text="Online...")
            time.sleep(1)
            label.config(text="Online")
            time.sleep(1)

    def draw_grid():
        # Define the number of rows and columns
        rows = 5
        columns = 5

        # Calculate the size of each grid cell
        cell_width = canvas.winfo_reqwidth() // columns
        cell_height = canvas.winfo_reqheight() // rows

        # Draw horizontal lines
        for i in range(1, rows):
            y = i * cell_height
            canvas.create_line(0, y, canvas.winfo_reqwidth(), y, fill="gray")

        # Draw vertical lines
        for j in range(1, columns):
            x = j * cell_width
            canvas.create_line(x, 0, x, canvas.winfo_reqheight(), fill="gray")

    global images
    global image_objects
    global canvas
    
    #map_window properties
    map_window = Toplevel()
    map_window.title("Map")
    map_window.geometry("500x500")
    
    # Create Canvas
    canvas = Canvas(map_window, width=500, height=500, bg="white")
    canvas.place(x=0, y=0)
    
    #Canvas click
    images = {}  # Dictionary to store images and their coordinates
    image_objects = {}  # Dictionary to store image objects

    #Initializing Obstacle Image
    obs_image=PhotoImage(file="test/assets/obstacle.png")
    
    # Load Images
    image = PhotoImage(file="test/assets/car.png")  # Replace with the path to your image file
    image_id = canvas.create_image(250, 250, anchor=CENTER, image=image)
    
    obs_warning = PhotoImage(file="test/assets/obs-warning.png")
    
    images[image_id] = (250,250)
    image_objects[image_id] = image
    
    # draw grid onto canvas
    draw_grid()

    status_thread = threading.Thread(target=blink_running_ui, daemon=True)
    status_thread.start()
    
    map_window.mainloop()

def create_obstacle(canvas, posx, posy):
    global images
    global image_objects
    
    image_source = PhotoImage(file="./test/assets/obstacle.png")
    obstacle_id = canvas.create_image(posx, posy, anchor=CENTER, image=image_source)
    
    # Store the reference to the obstacle image on the canvas in the global images dictionary
    images[obstacle_id] = (posx, posy)
    image_objects[obstacle_id] = image_source
    
    obstacle_source = PhotoImage(file="./test/assets/obs-warning.png")
    obstacle_warning_id = canvas.create_image(250,430, anchor=CENTER,image=obstacle_source)
    
    images[obstacle_warning_id] = (posx, posy + 200)
    image_objects[obstacle_warning_id] = obstacle_source
    
def clear_obs():
    for image_id in list(images.keys())[1:]:
        canvas.delete(image_id)
        del images[image_id]
        del image_objects[image_id]

def run_gui():
    root = Tk()
    root.title("Help")
    root.geometry("200x100")
    root.config(bg="white")
    
    help_box_image = PhotoImage(file="test/assets/instructions.png")
    help_box_label = Label(root, image=help_box_image)
    help_box_label.pack(pady=10)

    open_map(root)

# Turning off
def turn_off_top_left_wheel():
    GPIO.output(FRONT_PIN_9_GPIO, False)
    GPIO.output(FRONT_PIN_10_GPIO, False)
    GPIO.output(FRONT_PIN_15_GPIO, False)
    
def turn_off_top_right_wheel():
    GPIO.output(FRONT_PIN_1_GPIO, False)
    GPIO.output(FRONT_PIN_2_GPIO, False)
    GPIO.output(FRONT_PIN_7_GPIO, False)

def turn_off_bottom_left_wheel():
    GPIO.output(BACK_PIN_9_GPIO, False)
    GPIO.output(BACK_PIN_10_GPIO, False)
    GPIO.output(BACK_PIN_15_GPIO, False)

def turn_off_bottom_right_wheel():
    GPIO.output(BACK_PIN_1_GPIO, False)
    GPIO.output(BACK_PIN_2_GPIO, False)
    GPIO.output(BACK_PIN_7_GPIO, False)
    
def stop_car():
    turn_off_top_left_wheel()
    turn_off_top_right_wheel()
    turn_off_bottom_left_wheel()
    turn_off_bottom_right_wheel()

# Moving forward
def move_forward_top_left_wheel():
    GPIO.output(FRONT_PIN_9_GPIO, forward_flag)
    GPIO.output(FRONT_PIN_10_GPIO, not forward_flag)
    GPIO.output(FRONT_PIN_15_GPIO, forward_flag)
    
def move_forward_top_right_wheel():
    GPIO.output(FRONT_PIN_1_GPIO, forward_flag)
    GPIO.output(FRONT_PIN_2_GPIO, not forward_flag)
    GPIO.output(FRONT_PIN_7_GPIO, forward_flag)

def move_forward_bottom_left_wheel():
    GPIO.output(BACK_PIN_9_GPIO, forward_flag)
    GPIO.output(BACK_PIN_10_GPIO, not forward_flag)
    GPIO.output(BACK_PIN_15_GPIO, forward_flag)

def move_forward_bottom_right_wheel():
    GPIO.output(BACK_PIN_1_GPIO, forward_flag)
    GPIO.output(BACK_PIN_2_GPIO, not forward_flag)
    GPIO.output(BACK_PIN_7_GPIO, forward_flag)

# Moving backward
def move_backward_top_left_wheel():
    GPIO.output(FRONT_PIN_9_GPIO, forward_flag)
    GPIO.output(FRONT_PIN_10_GPIO, forward_flag)
    GPIO.output(FRONT_PIN_15_GPIO, not forward_flag)

def move_backward_top_right_wheel():
    GPIO.output(FRONT_PIN_1_GPIO, forward_flag)
    GPIO.output(FRONT_PIN_2_GPIO, forward_flag)
    GPIO.output(FRONT_PIN_7_GPIO, not forward_flag)
    
def move_backward_bottom_left_wheel():
    GPIO.output(BACK_PIN_9_GPIO, forward_flag)
    GPIO.output(BACK_PIN_10_GPIO, forward_flag)
    GPIO.output(BACK_PIN_15_GPIO, not forward_flag)

def move_backward_bottom_right_wheel():
    GPIO.output(BACK_PIN_1_GPIO, forward_flag)
    GPIO.output(BACK_PIN_2_GPIO, forward_flag)
    GPIO.output(BACK_PIN_7_GPIO, not forward_flag)

def move_forward():
    move_forward_top_left_wheel()
    move_forward_top_right_wheel()
    move_forward_bottom_left_wheel()
    move_forward_bottom_right_wheel()
     
def move_backward():
    move_backward_top_left_wheel()
    move_backward_top_right_wheel()
    move_backward_bottom_left_wheel()
    move_backward_bottom_right_wheel()
     
def steer_left():
    move_forward_top_right_wheel()
    move_forward_bottom_right_wheel()
    
    move_backward_top_left_wheel()
    move_backward_bottom_left_wheel()
    
def steer_right():
    move_forward_top_left_wheel()
    move_forward_bottom_left_wheel()
    move_backward_top_right_wheel()
    move_backward_bottom_right_wheel()

OBSTACLE_EXIST = False

def ultrasonic_sensor_detection():
    while True:
        time.sleep(0.2)
        global OBSTACLE_EXIST;
        print(sensor.distance * 100)
        if ((sensor.distance * 100) < MIN_obs_dis) and (GPIO.input(SWITCH_BUTTON_GPIO) == True): 
            if (not OBSTACLE_EXIST):
                create_obstacle(canvas, 250, 180)
                OBSTACLE_EXIST = True

            led.on()
            time.sleep(0.1)
            led.off()
            time.sleep(0.1)
        else:
            time.sleep(0.1)
            
            if (OBSTACLE_EXIST):
                clear_obs()
                OBSTACLE_EXIST = False

            led.off()

# Re enable this only iff the bluetooth does not work.    
W_KEY = 'w'
A_KEY = 'a'
S_KEY = 's'
D_KEY = 'd'
G_KEY = 'g'

pressed_keys = set()

def on_press(key):
    if key is not None and hasattr(key, 'char'):
        char = key.char
        
        pressed_keys.add(char)

        if A_KEY in pressed_keys:
            steer_left()
            print("steer_left")
            
        elif D_KEY in pressed_keys:
            steer_right()
            print("steer_left")
            
        elif W_KEY in pressed_keys:
            move_forward()
            print("move_forward")
            
        elif S_KEY in pressed_keys:
            move_backward()
            print("move_backward")

def on_release(key):
    if key is not None and hasattr(key, 'char'):
        char = key.char
        
        #print(f"{pressed_keys}")
        if char in pressed_keys:
            pressed_keys.remove(char)
            
        if char == W_KEY or char == S_KEY or char == A_KEY or char == D_KEY:
            stop_car()

    if key == Key.esc:
        # Stop listener
        listener.stop()

# SETUP BOARD
sensor = DistanceSensor(echo=PIN_echo, trigger=PIN_trigger) #max_distance=1 (default value in meter)
led = LED(PIN_led)

# Toggle
GPIO.setup(SWITCH_BUTTON_GPIO, GPIO.IN)

# Outputs
GPIO.setup(FRONT_PIN_1_GPIO, GPIO.OUT)
GPIO.setup(FRONT_PIN_2_GPIO, GPIO.OUT)
GPIO.setup(FRONT_PIN_7_GPIO, GPIO.OUT)

GPIO.setup(FRONT_PIN_9_GPIO, GPIO.OUT)
GPIO.setup(FRONT_PIN_10_GPIO, GPIO.OUT)
GPIO.setup(FRONT_PIN_15_GPIO, GPIO.OUT)

GPIO.setup(BACK_PIN_1_GPIO, GPIO.OUT)
GPIO.setup(BACK_PIN_2_GPIO, GPIO.OUT)
GPIO.setup(BACK_PIN_7_GPIO, GPIO.OUT)

GPIO.setup(BACK_PIN_9_GPIO, GPIO.OUT)
GPIO.setup(BACK_PIN_10_GPIO, GPIO.OUT)
GPIO.setup(BACK_PIN_15_GPIO, GPIO.OUT)

# Quit Pygame
try:
    images = []
    canvas = None

    ultrasonic_sensor_detection_thread = threading.Thread(target=ultrasonic_sensor_detection)
    gui_thread = threading.Thread(target=run_gui)
    
    ultrasonic_sensor_detection_thread.start()
    gui_thread.start()
    
    # Collect events until released
    with Listener(
        on_press=on_press,
        on_release=on_release
    ) as listener:
        listener.join()
        GPIO.cleanup()

    #picam2 = Picamera2()
    #picam2.start(show_preview=True)

    # import pygame
    # import sys
    #  
    #  # Initialize Pygame
    # pygame.init()
    # 
    # # Initialize the joystick
    # pygame.joystick.init()
    # joystick_count = pygame.joystick.get_count()
    # # # 
    # if joystick_count == 0:
    #    print("No joystick detected. Exiting...")
    #    pygame.quit()
    #    sys.exit()
    # 
    # joystick = pygame.joystick.Joystick(0)
    # joystick.init()
    # 
    # # Main game loop
    # running = True
    # while running:
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             running = False
    #      # Get joystick axes values
    #     x_axis = joystick.get_axis(0)
    #     y_axis = joystick.get_axis(1)
    # 
    #     threshold = 0.5
    #      
    #      # Determine joystick direction
    #     if x_axis < -threshold:
    #         direction = "Left"
    #         steer_left()
    #         print("steer_left")
    #     elif x_axis > threshold:
    #         direction = "Right"
    #         steer_right()
    #         print("steer_right")
    #     elif y_axis < -threshold:
    #         direction = "Up"
    #         move_forward()
    #         print("move_forward")
    #     elif y_axis > threshold:
    #         direction = "Down"
    #         move_backward()
    #         print("move_backward")
    #     else:
    #         stop_car()

finally:
    gui_thread.join()
    ultrasonic_sensor_detection_thread.join()
    
    GPIO.cleanup()
    
    # Quit Pygame
    pygame.quit()
    sys.exit()
