import socket
import RPi.GPIO as GPIO
import time
from collections import deque

# --- AGGRESSIVE CONFIG FOR DEBUGGING ---
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
HALL_PIN1 = 17
HALL_PIN2 = 27
HALL_PIN3 = 22
HALL_PIN4 = 23
DEBOUNCE_DELAY = 0.05          # <- MUCH higher (200ms)
TIMEOUT = 5.0
MIN_VALID_INTERVAL = 0.020      # <- reject anything < 200ms (300 RPM max)
MAX_VALID_INTERVAL = 10.0       # <- allow very low RPM
AVERAGE_WINDOW = 1              # <- smaller window for debugging

UDP_IP = "10.74.255.93"
UDP_PORT = 5005

interval_history1 = deque(maxlen=AVERAGE_WINDOW)
interval_history2 = deque(maxlen=AVERAGE_WINDOW)
interval_history3 = deque(maxlen=AVERAGE_WINDOW)
interval_history4 = deque(maxlen=AVERAGE_WINDOW)

pulse_interval1 = 0.0
pulse_interval2 = 0.0
pulse_interval3 = 0.0
pulse_interval4 = 0.0

last_valid_time1 = 0.0
last_valid_time2 = 0.0
last_valid_time3 = 0.0
last_valid_time4 = 0.0

pulse_count1 = 0
pulse_count2 = 0
pulse_count3 = 0
pulse_count4 = 0

last_rpm_time1 = 0.0
last_rpm_time2 = 0.0
last_rpm_time3 = 0.0
last_rpm_time4 = 0.0

raw_pulse_count1 = 0  # Count ALL pulses (including rejected ones)
raw_pulse_count2 = 0  # Count ALL pulses (including rejected ones)
raw_pulse_count3 = 0  # Count ALL pulses (including rejected ones)
raw_pulse_count4 = 0  # Count ALL pulses (including rejected ones)

sock = None

def hall_falling1(channel):
    global pulse_interval1, last_valid_time1, pulse_count1, last_rpm_time1, raw_pulse_count1
    
    now = time.perf_counter()
    raw_pulse_count1 += 1  # Count every interrupt
    
    
    # Extended bounce filter - wait longer and check multiple times
    time.sleep(0.005)  # 5ms wait
    if GPIO.input(channel) != GPIO.LOW:
        print(f"BOUNCE DETECTED - pin not low after delay")
        return
    
    time.sleep(0.005)  # Another 5ms
    if GPIO.input(channel) != GPIO.LOW:
        print(f"BOUNCE DETECTED - pin unstable")
        return
    
    time_since_last = now - last_valid_time1
    
    print(f"Raw interval: {time_since_last:.3f}s")
    
    # Very aggressive filtering
    if time_since_last >= DEBOUNCE_DELAY and MIN_VALID_INTERVAL <= time_since_last <= MAX_VALID_INTERVAL:
        interval_history1.append(time_since_last)
        if len(interval_history1) >= 1:  # Use immediately, don't wait for averaging
            pulse_interval1 = sum(interval_history1) / len(interval_history1)
        else:
            pulse_interval1 = time_since_last
        
        last_rpm_time1 = now
        pulse_count1 += 1
        print(f"ACCEPTED: {time_since_last:.3f}s -> RPM: {60.0/time_since_last:.1f}")
    else:
        print(f"REJECTED: {time_since_last:.3f}s (debounce: {time_since_last < DEBOUNCE_DELAY}, range: {not (MIN_VALID_INTERVAL <= time_since_last <= MAX_VALID_INTERVAL)})")
    
    last_valid_time1 = now

def hall_falling2(channel):
    global pulse_interval2, last_valid_time2, pulse_count2, last_rpm_time2, raw_pulse_count2
    
    now = time.perf_counter()
    raw_pulse_count2 += 1  # Count every interrupt
    
    
    # Extended bounce filter - wait longer and check multiple times
    time.sleep(0.005)  # 5ms wait
    if GPIO.input(channel) != GPIO.LOW:
        print(f"BOUNCE DETECTED - pin not low after delay")
        return
    
    time.sleep(0.005)  # Another 5ms
    if GPIO.input(channel) != GPIO.LOW:
        print(f"BOUNCE DETECTED - pin unstable")
        return
    
    time_since_last = now - last_valid_time2
    
    print(f"Raw interval: {time_since_last:.3f}s")
    
    # Very aggressive filtering
    if time_since_last >= DEBOUNCE_DELAY and MIN_VALID_INTERVAL <= time_since_last <= MAX_VALID_INTERVAL:
        interval_history2.append(time_since_last)
        if len(interval_history2) >= 1:  # Use immediately, don't wait for averaging
            pulse_interval2 = sum(interval_history2) / len(interval_history2)
        else:
            pulse_interval2 = time_since_last
        
        last_rpm_time2 = now
        pulse_count2 += 1
        print(f"ACCEPTED: {time_since_last:.3f}s -> RPM: {60.0/time_since_last:.1f}")
    else:
        print(f"REJECTED: {time_since_last:.3f}s (debounce: {time_since_last < DEBOUNCE_DELAY}, range: {not (MIN_VALID_INTERVAL <= time_since_last <= MAX_VALID_INTERVAL)})")
    
    last_valid_time2 = now


def hall_falling3(channel):
    global pulse_interval3, last_valid_time3, pulse_count3, last_rpm_time3, raw_pulse_count3
    
    now = time.perf_counter()
    raw_pulse_count3 += 1  # Count every interrupt
    
    
    # Extended bounce filter - wait longer and check multiple times
    time.sleep(0.005)  # 5ms wait
    if GPIO.input(channel) != GPIO.LOW:
        print(f"BOUNCE DETECTED - pin not low after delay")
        return
    
    time.sleep(0.005)  # Another 5ms
    if GPIO.input(channel) != GPIO.LOW:
        print(f"BOUNCE DETECTED - pin unstable")
        return
    
    time_since_last = now - last_valid_time3
    
    print(f"Raw interval: {time_since_last:.3f}s")
    
    # Very aggressive filtering
    if time_since_last >= DEBOUNCE_DELAY and MIN_VALID_INTERVAL <= time_since_last <= MAX_VALID_INTERVAL:
        interval_history3.append(time_since_last)
        if len(interval_history3) >= 1:  # Use immediately, don't wait for averaging
            pulse_interval3 = sum(interval_history3) / len(interval_history3)
        else:
            pulse_interval3 = time_since_last
        
        last_rpm_time3 = now
        pulse_count3 += 1
        print(f"ACCEPTED: {time_since_last:.3f}s -> RPM: {60.0/time_since_last:.1f}")
    else:
        print(f"REJECTED: {time_since_last:.3f}s (debounce: {time_since_last < DEBOUNCE_DELAY}, range: {not (MIN_VALID_INTERVAL <= time_since_last <= MAX_VALID_INTERVAL)})")
    
    last_valid_time3 = now

def hall_falling4(channel):
    global pulse_interval4, last_valid_time4, pulse_count4, last_rpm_time4, raw_pulse_count4
    
    now = time.perf_counter()
    raw_pulse_count4 += 1  # Count every interrupt
    
    
    # Extended bounce filter - wait longer and check multiple times
    time.sleep(0.005)  # 5ms wait
    if GPIO.input(channel) != GPIO.LOW:
        print(f"BOUNCE DETECTED - pin not low after delay")
        return
    
    time.sleep(0.005)  # Another 5ms
    if GPIO.input(channel) != GPIO.LOW:
        print(f"BOUNCE DETECTED - pin unstable")
        return
    
    time_since_last = now - last_valid_time4
    
    print(f"Raw interval: {time_since_last:.3f}s")
    
    # Very aggressive filtering
    if time_since_last >= DEBOUNCE_DELAY and MIN_VALID_INTERVAL <= time_since_last <= MAX_VALID_INTERVAL:
        interval_history4.append(time_since_last)
        if len(interval_history4) >= 1:  # Use immediately, don't wait for averaging
            pulse_interval4 = sum(interval_history4) / len(interval_history4)
        else:
            pulse_interval4 = time_since_last
        
        last_rpm_time4 = now
        pulse_count4 += 1
        print(f"ACCEPTED: {time_since_last:.3f}s -> RPM: {60.0/time_since_last:.1f}")
    else:
        print(f"REJECTED: {time_since_last:.3f}s (debounce: {time_since_last < DEBOUNCE_DELAY}, range: {not (MIN_VALID_INTERVAL <= time_since_last <= MAX_VALID_INTERVAL)})")
    
    last_valid_time4 = now


def get_rpm1():
    global pulse_interval1, last_rpm_time1, interval_history1
    now = time.perf_counter()
    
    if (now - last_rpm_time1) > TIMEOUT:
        interval_history1.clear()
        return 0.0
    
    if pulse_interval1 > 0 and pulse_interval1 >= MIN_VALID_INTERVAL:
        return 60.0 / pulse_interval1
    
    return 0.0

def get_rpm2():
    global pulse_interval2, last_rpm_time2, interval_history2
    now = time.perf_counter()
    
    if (now - last_rpm_time2) > TIMEOUT:
        interval_history2.clear()
        return 0.0
    
    if pulse_interval2 > 0 and pulse_interval2 >= MIN_VALID_INTERVAL:
        return 60.0 / pulse_interval2
    
    return 0.0

def get_rpm3():
    global pulse_interval3, last_rpm_time3, interval_history3
    now = time.perf_counter()
    
    if (now - last_rpm_time3) > TIMEOUT:
        interval_history3.clear()
        return 0.0
    
    if pulse_interval3 > 0 and pulse_interval3 >= MIN_VALID_INTERVAL:
        return 60.0 / pulse_interval3
    
    return 0.0

def get_rpm4():
    global pulse_interval4, last_rpm_time4, interval_history4
    now = time.perf_counter()
    
    if (now - last_rpm_time4) > TIMEOUT:
        interval_history4.clear()
        return 0.0
    
    if pulse_interval4 > 0 and pulse_interval4 >= MIN_VALID_INTERVAL:
        return 60.0 / pulse_interval4
    
    return 0.0

def setup():
    global sock, last_valid_time1, last_valid_time2, last_valid_time3, last_valid_time4, last_rpm_time1, last_rpm_time2, last_rpm_time3, last_rpm_time4
    
    GPIO.setup(HALL_PIN1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(HALL_PIN2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(HALL_PIN3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(HALL_PIN4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Use BOTH hardware and software debouncing
    hardware_bounce_ms = int(DEBOUNCE_DELAY * 1000)  # Convert to milliseconds
    GPIO.add_event_detect(HALL_PIN1, GPIO.FALLING, callback=hall_falling1, 
                          bouncetime=hardware_bounce_ms)
    GPIO.add_event_detect(HALL_PIN2, GPIO.FALLING, callback=hall_falling2,
                          bouncetime=hardware_bounce_ms)
    GPIO.add_event_detect(HALL_PIN3, GPIO.FALLING, callback=hall_falling3,
                          bouncetime=hardware_bounce_ms)
    GPIO.add_event_detect(HALL_PIN4, GPIO.FALLING, callback=hall_falling4,
                          bouncetime=hardware_bounce_ms)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"Sending to {UDP_IP}:{UDP_PORT}")
    print("AGGRESSIVE FILTERING - watching for noise/bounce issues")
    print(f"Min interval: {MIN_VALID_INTERVAL}s = {60/MIN_VALID_INTERVAL:.0f} RPM max")
    print(f"Debounce: {DEBOUNCE_DELAY}s")
    
    t = time.perf_counter()
    last_valid_time1 = t
    last_valid_time2 = t
    last_valid_time3 = t
    last_valid_time4 = t

    last_rpm_time1 = t - (TIMEOUT + 1)
    last_rpm_time2 = t - (TIMEOUT + 1)
    last_rpm_time3 = t - (TIMEOUT + 1)
    last_rpm_time4 = t - (TIMEOUT + 1)

def loop():
    global pulse_count1, pulse_count2, pulse_count3, pulse_count4, raw_pulse_count1, raw_pulse_count2, raw_pulse_count3, raw_pulse_count4
    last_count1 = 0
    last_count2 = 0
    last_count3 = 0
    last_count4 = 0

    last_raw_count1 = 0
    last_raw_count2 = 0
    last_raw_count3 = 0
    last_raw_count4 = 0
    
    while True:
        rpm1 = get_rpm1()
        rpm2 = get_rpm2()
        rpm3 = get_rpm3()
        rpm4 = get_rpm4()

        pulses_this_second1 = pulse_count1 - last_count1
        pulses_this_second2 = pulse_count2 - last_count2
        pulses_this_second3 = pulse_count3 - last_count3
        pulses_this_second4 = pulse_count4 - last_count4

        raw_pulses_this_second1 = raw_pulse_count1 - last_raw_count1
        raw_pulses_this_second2 = raw_pulse_count2 - last_raw_count2
        raw_pulses_this_second3 = raw_pulse_count3 - last_raw_count3
        raw_pulses_this_second4 = raw_pulse_count4 - last_raw_count4
        
        last_count1 = pulse_count1
        last_count2 = pulse_count2
        last_count3 = pulse_count3
        last_count4 = pulse_count4

        last_raw_count1 = raw_pulse_count1
        last_raw_count2 = raw_pulse_count2
        last_raw_count3 = raw_pulse_count3
        last_raw_count4 = raw_pulse_count4
        
        avg_interval1 = (sum(interval_history1) / len(interval_history1)) if interval_history1 else 0.0
        avg_interval2 = (sum(interval_history2) / len(interval_history2)) if interval_history2 else 0.0
        avg_interval3 = (sum(interval_history3) / len(interval_history3)) if interval_history3 else 0.0
        avg_interval4 = (sum(interval_history4) / len(interval_history4)) if interval_history4 else 0.0
        
        # message = f"RPM: {rpm:.1f} | Valid: {pulses_this_second} | Raw: {raw_pulses_this_second} | Avg: {avg_interval:.3f}s"
        message = f"RPM1 | RPM2 | RPM3 | RPM4: {rpm1:.1f} | {rpm2:.2f} | {rpm3:.3f} | {rpm4:.4f}"
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
