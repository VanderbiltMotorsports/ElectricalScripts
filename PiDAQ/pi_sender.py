import socket
import RPi.GPIO as GPIO
import time

BUTTON_PIN = 17
UDP_IP = "10.74.1.33"
UDP_PORT = 5005

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f"Sending to {UDP_IP}:{UDP_PORT}")
print("Press the button!")

try:
	while True:
		button_state = GPIO.input(BUTTON_PIN)

		if button_state == GPIO.LOW:
			timestamp = time.time()
			message = f"BUTTON_PRESS,{timestamp}"
			sock.sendto(message.encode(), (UDP_IP, UDP_PORT))
			print(f"Sent: {message}")
			time.sleep(0.2)

except KeyboardInterrupt:
	print("\nCleaning up...")
finally:
	GPIO.cleanup()
	sock.close()
