import socket
import RPi.GPIO as GPIO
import time
from collections import deque

# --- AGGRESSIVE CONFIG FOR DEBUGGING ---
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
HALL_PIN = 17
DEBOUNCE_DELAY = 0.05          # <- MUCH higher (200ms)
TIMEOUT = 5.0
MIN_VALID_INTERVAL = 0.020      # <- reject anything < 200ms (300 RPM max)
MAX_VALID_INTERVAL = 10.0       # <- allow very low RPM
AVERAGE_WINDOW = 1              # <- smaller window for debugging

UDP_IP = "10.74.255.93"
UDP_PORT = 5005

interval_history = deque(maxlen=AVERAGE_WINDOW)
pulse_interval = 0.0
last_valid_time = 0.0
pulse_count = 0
last_rpm_time = 0.0
raw_pulse_count = 0  # Count ALL pulses (including rejected ones)
sock = None

def hall_falling(channel):
    global pulse_interval, last_valid_time, pulse_count, last_rpm_time, raw_pulse_count
    
    now = time.perf_counter()
    raw_pulse_count += 1  # Count every interrupt
    
    # Extended bounce filter - wait longer and check multiple times
    time.sleep(0.005)  # 5ms wait
    if GPIO.input(channel) != GPIO.LOW:
        print(f"BOUNCE DETECTED - pin not low after delay")
        return
    
    time.sleep(0.005)  # Another 5ms
    if GPIO.input(channel) != GPIO.LOW:
        print(f"BOUNCE DETECTED - pin unstable")
        return
    
    time_since_last = now - last_valid_time
    
    print(f"Raw interval: {time_since_last:.3f}s")
    
    # Very aggressive filtering
    if time_since_last >= DEBOUNCE_DELAY and MIN_VALID_INTERVAL <= time_since_last <= MAX_VALID_INTERVAL:
        interval_history.append(time_since_last)
        if len(interval_history) >= 1:  # Use immediately, don't wait for averaging
            pulse_interval = sum(interval_history) / len(interval_history)
        else:
            pulse_interval = time_since_last
        
        last_rpm_time = now
        pulse_count += 1
        print(f"ACCEPTED: {time_since_last:.3f}s -> RPM: {60.0/time_since_last:.1f}")
    else:
        print(f"REJECTED: {time_since_last:.3f}s (debounce: {time_since_last < DEBOUNCE_DELAY}, range: {not (MIN_VALID_INTERVAL <= time_since_last <= MAX_VALID_INTERVAL)})")
    
    last_valid_time = now

def get_rpm():
    global pulse_interval, last_rpm_time, interval_history
    now = time.perf_counter()
    
    if (now - last_rpm_time) > TIMEOUT:
        interval_history.clear()
        return 0.0
    
    if pulse_interval > 0 and pulse_interval >= MIN_VALID_INTERVAL:
        return 60.0 / pulse_interval
    
    return 0.0

def setup():
    global sock, last_valid_time, last_rpm_time
    
    GPIO.setup(HALL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    # Use BOTH hardware and software debouncing
    hardware_bounce_ms = int(DEBOUNCE_DELAY * 1000)  # Convert to milliseconds
    GPIO.add_event_detect(HALL_PIN, GPIO.FALLING, callback=hall_falling, 
                          bouncetime=hardware_bounce_ms)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"Sending to {UDP_IP}:{UDP_PORT}")
    print("AGGRESSIVE FILTERING - watching for noise/bounce issues")
    print(f"Min interval: {MIN_VALID_INTERVAL}s = {60/MIN_VALID_INTERVAL:.0f} RPM max")
    print(f"Debounce: {DEBOUNCE_DELAY}s")
    
    t = time.perf_counter()
    last_valid_time = t
    last_rpm_time = t - (TIMEOUT + 1)

def loop():
    global pulse_count, raw_pulse_count
    last_count = 0
    last_raw_count = 0
    
    while True:
        rpm = get_rpm()
        pulses_this_second = pulse_count - last_count
        raw_pulses_this_second = raw_pulse_count - last_raw_count
        
        last_count = pulse_count
        last_raw_count = raw_pulse_count
        
        avg_interval = (sum(interval_history) / len(interval_history)) if interval_history else 0.0
        
        message = f"RPM: {rpm:.1f} | Valid: {pulses_this_second} | Raw: {raw_pulses_this_second} | Avg: {avg_interval:.3f}s"
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
