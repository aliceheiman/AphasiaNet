from machine import Pin
import time

# Setup traffic lights
red_light = Pin(15, Pin.OUT)
yellow_light = Pin(14, Pin.OUT)
green_light = Pin(13, Pin.OUT)

# Setup buttons
red_button = Pin(20, Pin.IN, Pin.PULL_UP)
green_button = Pin(21, Pin.IN, Pin.PULL_UP)
yellow_button = Pin(22, Pin.IN, Pin.PULL_UP)


# Placeholder for recording function
def start_recording():
    print("Recording started...")


def stop_recording():
    print("Recording stopped.")


# Main loop
while True:
    if not red_button.value():  # Red button pressed
        red_light.value(1)  # Turn on red light
        start_recording()  # Start recording
        while not red_button.value():  # Wait for button to be released
            time.sleep(0.1)

    elif not green_button.value():  # Green button pressed
        green_light.value(1)  # Turn on green light
        stop_recording()  # Stop recording
        while not green_button.value():  # Wait for button to be released
            time.sleep(0.1)

    elif not yellow_button.value():  # Yellow button pressed
        yellow_light.value(1)  # Turn on yellow light
        while not yellow_button.value():  # Wait for button to be released
            time.sleep(0.1)

    # Turn off all lights if no button is pressed
    if red_button.value() and green_button.value() and yellow_button.value():
        red_light.value(0)
        yellow_light.value(0)
        green_light.value(0)

    time.sleep(0.1)  # Loop delay
