UDP_IP = "10.74.1.33"

UDP_PORT = 5005








def hall_rising(channel):

	global pulse_interval, rising_time, falling_time
	falling_time = now



def setup():
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(HALL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)



	while True:

		if pulse_interval > 0:


			rpm = 60.0 / pulse_intereval


			message = f"RPM: {rpm:2f}"

			sock.sendto(message.encode(), (UDP_IP, UDP_PORT))

			print(f"Sent: {message}")

		time.sleep(0.1)
	try:

		setup()

		loop()


	except KeyobardInterrupt:

		print("\nExiting...")

	finally:

		GPIO.cleanup()


		sock.close()