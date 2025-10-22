import socket
import RPi.GPIO as GPIO
import time
from collections import deque

HALL_PIN = 3
DEBOUNCE_DELAY = 0.050  # Changed from 0.027
TIMEOUT = 3.0  # number of seconds since last pulse before it reports rpm as 0
MIN_VALID_INTERVAL = 0.050  # Reject intervals shorter than 50ms 
MAX_VALID_INTERVAL = 5.0    # Reject intervals longer than 5s 

# Rolling average for smoother readings
AVERAGE_WINDOW = 5
interval_history = deque(maxlen=AVERAGE_WINDOW)

pulse_interval = 0
last_valid_time = 0
pulse_count = 0
last_rpm_time = 0

UDP_IP = "10.74.255.93"
UDP_PORT = 5005

sock = None

def hall_rising(channel):
    global pulse_interval, last_valid_time, pulse_count, last_rpm_time
    
    now = time.time()
    
    # Improved debouncing with minimum interval check
    time_since_last = now - last_valid_time
    if time_since_last > DEBOUNCE_DELAY:
        
        # filters out noise - only readings from within the interval
        if MIN_VALID_INTERVAL <= time_since_last <= MAX_VALID_INTERVAL:
            interval_history.append(time_since_last)
            
            # rolling average for stability
            if len(interval_history) >= 2:
                pulse_interval = sum(interval_history) / len(interval_history)
            else:
                pulse_interval = time_since_last
                
            last_rpm_time = now
            
        last_valid_time = now
        pulse_count += 1

def get_rpm():
    global pulse_interval, last_rpm_time
    
    now = time.time()
    
    # Check for timeout
    if (now - last_rpm_time) > TIMEOUT:
        return 0.0
    
    # Check for valid interval
    if pulse_interval > 0 and pulse_interval >= MIN_VALID_INTERVAL:
        return 60.0 / pulse_interval
    
    return 0.0

def setup():
    global sock
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(HALL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    
    GPIO.add_event_detect(HALL_PIN, GPIO.RISING, callback=hall_rising)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"Sending to {UDP_IP}:{UDP_PORT}")
    print("Improved low-RPM accuracy with filtering and averaging")

def loop():
    global pulse_count
    last_count = 0
    
    while True:
        rpm = get_rpm()
        pulses_this_second = pulse_count - last_count
        last_count = pulse_count
        
        # Additional info for debugging
        avg_interval = sum(interval_history) / len(interval_history) if interval_history else 0
        
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
