import socket

ARDUINO_IP = "192.168.1.50" #need to change to ardiuno ip
PORT = 5000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect((ARDUINO_IP, PORT))

s.sendall("message")