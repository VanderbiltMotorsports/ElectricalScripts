import socket
import RPi.GPIO as GPIO
import time
from collections import deque

# --- CONFIG ---
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)          # <- BCM numbering
HALL_PIN = 17                   # <- use a non-I2C pin (physical pin 11)
DEBOUNCE_DELAY = 0.050          # 50 ms
TIMEOUT = 3.0                   # seconds since last pulse -> RPM=0
MIN_VALID_INTERVAL = 0.050      # reject < 50 ms ( >1200 RPM for 1 pulse/rev)
MAX_VALID_INTERVAL = 5.0        # reject > 5 s ( <12 RPM )
AVERAGE_WINDOW = 5

UDP_IP = "10.74.255.93"
UDP_PORT = 5005

interval_history = deque(maxlen=AVERAGE_WINDOW)
pulse_interval = 0.0
last_valid_time = 0.0
pulse_count = 0
last_rpm_time = 0.0
sock = None

def hall_falling(channel):
    global pulse_interval, last_valid_time, pulse_count, last_rpm_time

    now = time.perf_counter()

    # Quick confirm: still low after a short delay (filters bounce)
    time.sleep(0.001)  # 1 ms
    if GPIO.input(channel) != GPIO.LOW:
        return

    # Compute interval
    time_since_last = now - last_valid_time

    # Software debounce + sanity range
    if time_since_last >= DEBOUNCE_DELAY and MIN_VALID_INTERVAL <= time_since_last <= MAX_VALID_INTERVAL:
        interval_history.append(time_since_last)
        if len(interval_history) >= 2:
            pulse_interval = sum(interval_history) / len(interval_history)
        else:
            pulse_interval = time_since_last
        last_rpm_time = now
        pulse_count += 1

    # Always update last_valid_time when we see a real falling edge
    last_valid_time = now

def get_rpm():
    global pulse_interval, last_rpm_time, interval_history

    now = time.perf_counter()
    if (now - last_rpm_time) > TIMEOUT:
        # reset smoothing so we don't reuse stale intervals
        interval_history.clear()
        return 0.0

    if pulse_interval > 0 and pulse_interval >= MIN_VALID_INTERVAL:
        return 60.0 / pulse_interval
    return 0.0

def setup():
    global sock, last_valid_time, last_rpm_time
    # Bias input high; expect hall to pull to GND -> FALLING edge
    GPIO.setup(HALL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # Hardware/driver debounce complement (in milliseconds)
    GPIO.add_event_detect(HALL_PIN, GPIO.FALLING, callback=hall_falling,
                          bouncetime=int(DEBOUNCE_DELAY * 1000))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"Sending to {UDP_IP}:{UDP_PORT}")
    print("Using BCM 17 with PUD_UP, FALLING edge, and filtered intervals.")
    t = time.perf_counter()
    last_valid_time = t
    last_rpm_time = t - (TIMEOUT + 1)  # so we start at RPM 0

def loop():
    global pulse_count
    last_count = 0

    while True:
        rpm = get_rpm()
        pulses_this_second = pulse_count - last_count
        last_count = pulse_count

        avg_interval = (sum(interval_history) / len(interval_history)) if interval_history else 0.0
        message = f"RPM: {rpm:.1f} | Pulses/sec: {pulses_this_second} | Avg_Interval: {avg_interval:.3f}s"
        sock.sendto(message.encode(), (UDP_IP, UDP_PORT))
        print(f"Sent: {message}")
        time.sleep(1.0)

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
