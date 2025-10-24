import socket

HOST = "0.0.0.0"
port = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, port))

server.listen(1)

while True:
    conn, addr = server.accept()

    data = conn.recv(1024).decode().strip()

    if data.upper() == "KILL":
        print("Kill signal recieved")
        conn.close()
        break
    else:
        print(f"unknown command: {data}")
        conn.close()

server.close()