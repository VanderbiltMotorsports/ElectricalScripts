import socket

UDP_IP = "0.0.0.0"  # Listen on all interfaces
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Listening on port {UDP_PORT}...")

while True:
    data, addr = sock.recvfrom(1024)
    message = data.decode()
    print(f"Received from {addr}: {message}")