
import socket
import RPi.GPIO as GPIO
import time

HALL_PIN = 3
DEBOUNCE_DELAY = 0.027

pulse_interval = 0
rising_time = 0
falling_time = 0

UDP_IP = "10.74.1.33"
UDP_PORT = 5005

sock = None

def hall_rising(channel):
	global pulse_interval, rising_time, falling_time

	now = time.time()

	if (now - falling_time) > DEBOUNCE_DELAY:
		pulse_interval = now - rising_time
		rising_time = now
		falling_time = now

def setup():
	global sock
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(HALL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

	GPIO.add_event_detect(HALL_PIN, GPIO.RISING, callback=hall_rising)

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	print(f"Sending to {UDP_IP}:{UDP_PORT}")


def loop():
	global pulse_interval

	while True:
		if pulse_interval > 0:
			rpm = 60.0 / pulse_interval
			message = f"RPM: {rpm:.2f}"
			sock.sendto(message.encode(), (UDP_IP, UDP_PORT))
			print(f"Sent: {message}")
		time.sleep(0.1)

if __name__ == "__main__":
	try:
		setup()
		loop()
	except KeyboardInterrupt:
		print("\nExiting...")
	finally:
		GPIO.cleanup()
		if sock:
			sock.close()
