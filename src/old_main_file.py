#Libraries/Modules Import
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
def open_map():
    #start the 2d Map 
    def start_map():
        #thread.start()
        thread2.start()
        collision_thread.start()
        #thread3.start()
        return
    
    #online... feature (when pressed start in Map/Navigation)
    def blink_running_ui():
        canvas.create_oval(8,11,18,21,fill="green",outline="black")
        label=Label(canvas, text="online")
        label.place(x=20,y=3)
        label.config(bg="white",fg="black", font=('Arial', 16))
#         while True:
#             label.config(text="online.")
#             time.sleep(1)
#             label.config(text="online..")
#             time.sleep(1)
#             label.config(text="online...")
#             time.sleep(1)
#             label.config(text="online")
#             time.sleep(1)
            
    def move_image_continuously(canvas, image_id, dx, dy):
        while True:
            time.sleep(0.5)  # Sleep for 0.5 second
            canvas.move(image_id, dx, dy)

    def move_image(event=None):
        pass  # Placeholder function, not used in this version      
    
    #create an obstacle
    def create_obstacle(imgSrc, posx, posy):
        name = canvas.create_image(posx,posy,anchor=CENTER,image=imgSrc)
        return name
    
    #create a thread
    def create_movement_thread(threadSrc,dx,dy):
        temp = threading.Thread(target=move_image_continuously,args=(canvas,threadSrc,dx,dy), daemon=True)
        return temp
    
    #open help window
    def toggle_help_box():
        help_window = Toplevel(map_window)
        help_window.title("Help")
        help_window.geometry("200x100")
        help_window.config(bg="white")
        
        help_box_label = Label(help_window,image=helpBox_img)
        help_box_label.pack(pady=10)
    
        #adding grid onto the canvas
    def draw_grid():
        # Define the number of rows and columns
        rows = 3
        columns = 3

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

    #adding obstacles to map with left-click
    def add_image(event):
        x, y = event.x, event.y

    # Check if there's already an image at the clicked coordinates
        for existing_image, (image_x, image_y) in images.items():
            if x - 41 < image_x < x + 41 and y - 41 < image_y < y + 41:
                # If an image already exists at this location, do nothing
                return

        # Create an image item on the canvas
        image_id = canvas.create_image(x, y, anchor=CENTER, image=obs_image)

        # Store the image ID and its coordinates in the dictionary
        images[image_id] = (x, y)
        image_objects[image_id] = image  # Store the image object
    
    #rotate obstacles
    def rotate_obstacles():
        pivot_x = canvas.winfo_reqwidth() / 2
        pivot_y = canvas.winfo_reqheight() / 2

        for image_id, coords in list(images.items())[1:]:
            x, y = coords
            angle = math.radians(10)  # Rotate by 10 degrees (adjust as needed)
            rotated_x = pivot_x + (x - pivot_x) * math.cos(angle) - (y - pivot_y) * math.sin(angle)
            rotated_y = pivot_y + (x - pivot_x) * math.sin(angle) + (y - pivot_y) * math.cos(angle)
            
            diff_x = rotated_x - x
            diff_y = rotated_y - y
            
            #canvas.move(image_id, diff_x, diff_y)
            #detect obs
            obs_detection()
            canvas.coords(image_id, rotated_x, rotated_y)
            images[image_id] = (rotated_x, rotated_y)
            
    def move_obs_down():
        for image_id in list(images.keys())[1:]:
            x, y = canvas.coords(image_id)
            newY = y + 10
            canvas.coords(image_id, x, newY)
            obs_detection()
            images[image_id]=(x,newY)
        
    def clear_obs():
        for image_id in list(images.keys())[1:]:
            canvas.delete(image_id)
            del images[image_id]
            del image_objects[image_id]
    
    def obs_detection():
        for image_id in list(images.keys())[1:]:
            x, y = canvas.coords(image_id)
            if (x >220 and x <270) and (y>180 and y < 270):
                    obs_warning_img = canvas.create_image(250,430,anchor=CENTER,image=obs_warning)
                    canvas.after(3000,canvas.delete,obs_warning_img)                
                
        

    #map_window properties
    map_window = Toplevel(root)
    map_window.title("Map")
    map_window.geometry("600x500")

    # Create Canvas
    canvas = Canvas(map_window, width=500, height=500, bg="white")
    canvas.place(x=0,y=0)
    
    #Canvas click
    images = {}  # Dictionary to store images and their coordinates
    image_objects = {}  # Dictionary to store image objects

    canvas.bind("<Button-1>", add_image) #left click to add bind
    
    #Initializing Obstacle Image
    obs_image=PhotoImage(file="test/assets/obstacle.png")
    #Example Obstacles
    #exampleObstacle = create_obstacle(obs_image,400,40)
    #exampleObstacle2 = create_obstacle(obs_image,150,40)
    #thread3 = create_movement_thread(exampleObstacle2,0,15)
    
    #Control Panel for Canvas
    start_btn = Button(map_window, width = 5, text="Start",command=start_map)
    start_btn.place(x = 510, y = 200)
    quit_btn = Button(map_window, width =5,text="Quit", command=map_window.destroy)
    quit_btn.place(x=510,y=230)
    rotate_btn = Button(map_window, width=5, text="Rotate", command=rotate_obstacles)
    rotate_btn.place(x=510,y=260)
    clear_btn = Button(map_window,width=5,text="Clear", command=clear_obs)
    clear_btn.place(x=510, y=290)
    move_up_btn = Button(map_window, width=5, text="Forward", command=move_obs_down)
    move_up_btn.place(x=510,y=320)
    help_btn = Button(map_window, width=5, text="Help", command=toggle_help_box)
    help_btn.place(x=510,y=465)
    
    # Load Images
    image = PhotoImage(file="test/assets/car.png")  # Replace with the path to your image file
    image_id = canvas.create_image(250, 250, anchor=CENTER, image=image)
    helpBox_img = PhotoImage(file="test/assets/instructions.png")
    obs_warning = PhotoImage(file="test/assets/obs-warning.png")
    
    images[image_id] = (250,250)
    image_objects[image_id] = image
    
    #draw grid onto canvas
    draw_grid()

    
    # Set initial movement
    dx = 0
    dy = 15

    # Create a thread for continuous movement
    #thread = threading.Thread(target=move_image_continuously, args=(canvas, exampleObstacle, dx, dy))
    #thread.daemon = True  # Set the thread as a daemon so it will be terminated when the main program exits
    #thread.start()
    #thread for online label
    thread2 = threading.Thread(target=blink_running_ui, daemon=True)
    #thread to detect collision
    collision_thread = threading.Thread(target=obs_detection, daemon=True)

    map_window.mainloop()
    

def open_camera():
    #Capture Screen (Screenshot)
    def capture_screen():
        picam2.switch_mode_and_capture_file(capture_config, "image.jpg")
        
    #window properties
    camera_window = Toplevel(root)
    camera_window.title("Camera Mode")
    camera_window.geometry("400x450")
    
    #canvas for camera view
    camera_canvas = Canvas(camera_window, width=400, height=400, bg="white")
    camera_canvas.pack()
    
    #placeholder
    #insert camera view in canvas
    
    #Capture Button
    ss_btn = Button(camera_window,text="Capture",command=capture_screen)
    ss_btn.pack()
    
    #run camera_window
    camera_window.mainloop()

root = Tk()
root.title("Home")
root.geometry("300x200")
    
label1 = Label(root, text="Control Panel")
label1.pack(pady=20)

button = Button(root, text="Map/Navigations", command=open_map)
button.pack()

button3 = Button(root,width=11,text="Camera",command=open_camera)
button3.pack()

# #Run GUI
# root.mainloop()

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

def ultrasonic_sensor_detection():
    # = GPIO.input(SWITCH_BUTTON_GPIO)
    while True:
        time.sleep(0.2)
        print(sensor.distance * 100)
        if ((sensor.distance* 100) < MIN_obs_dis) and (GPIO.input(SWITCH_BUTTON_GPIO) == True):
            led.on()
            time.sleep(0.1)
            led.off()
            time.sleep(0.1)
        else:
            led.off()
        #led.on()
        #time.sleep(0.1)
        #led.off()
        #time.sleep(0.1)
    


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

# Collect events until released
with Listener(
    on_press=on_press,
    on_release=on_release
) as listener:
    listener.join()
    GPIO.cleanup()

#picam2 = Picamera2()
#picam2.start(show_preview=True)

ultrasonic_sensor_detection_thread = threading.Thread(target=ultrasonic_sensor_detection)
ultrasonic_sensor_detection_thread.start()

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

#SETUP BOARD




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


GPIO.cleanup()
ultrasonic_sensor_detection_thread.join()
#     
# try:
#     while True:
#         time.sleep(0.1)
# finally:
#     GPIO.cleanup()
#     ultrasonic_sensor_detection_thread.join()

# Quit Pygame
root.mainloop()
pygame.quit()
sys.exit()
