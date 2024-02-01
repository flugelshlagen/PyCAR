# PyCAR
python program + gui that remotes control a rc car made using raspberry Pi

features:
ultrasonic sensors (for obstacle scanning) (default - 10 cm ahead)
real-time environment map on gui 
Xbox/DualShock controller compatibility
Bluetooth mode (wireless)

requirements : a RC car made with Raspberry Pi, an ultrasonic sensor 
what it does : python program that lets users remotely control an Raspberry Pi RC Car via the HID or a bluetooth game controller (XBOX, PlayStation etc.), the python is also able to use the ultrasonic sensor to detect surrounding obstacles. It also uses tkinter to map its environment on a GUI.
