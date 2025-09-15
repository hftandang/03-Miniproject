import machine
import time
import network
import json
import asyncio
photo_sensor_pin = machine.ADC(26) # change with proper ADC pin number

# this func to be added to main.py, for now put here and test in parallel
# Input: button press
# Output: Array of light intensities (analog values) and length of that array
# interfaces w. photoresistor and button

def collect_pico_data(record_button_stat):
    intensity_array = []
    # Read current sensor value, ranges from 0 to 65535, 0 being low voltage 65535 meaning high voltage around 3.3V, as voltage increases so does intensity of light
    if record_button_stat:  
        start_time = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), start_time) < 10_000:  
            light_value = photo_sensor_pin.read_u16()
            intensity_array.append(light_value)
            time.sleep(0.05)  # clock is every 50ms
    return intensity_array, len(intensity_array)
