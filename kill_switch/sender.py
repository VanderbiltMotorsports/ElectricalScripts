import socket
from pynput import keyboard

HOST = "127.0.0.1" # need to change to ras pi id
port = 5000

key_pressed = False

def on_press(key):
    global key_pressed
    
    if (key.char == 'k' and not key_pressed):
        try:
            key_pressed = True

            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((HOST, port))

            client.sendall(b"KILL")

            client.close()

        except AttributeError:
            pass
def on_release(key):
    global key_pressed
    try:
        if (key.char == 'k' and key_pressed):
            key_pressed = False
    except AttributeError:
        pass

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()