# main.py for Raspberry Pi Pico W
# Title: Pico Light Orchestra Instrument Code

import machine
import time
import network
import json
import asyncio
from machine import Pin

# --- Pin Configuration ---
# The photosensor is connected to an Analog-to-Digital Converter (ADC) pin.
# We will read the voltage, which changes based on light.
photo_sensor_pin = machine.ADC(26)

# The buzzer is connected to a GPIO pin that supports Pulse Width Modulation (PWM).
# PWM allows us to create a square wave at a specific frequency to make a sound.
buzzer_pin = machine.PWM(machine.Pin(12))
buzzer_pin.duty_u16(0)

# Button is connected to a GPIO pin (28). If HIGH, 1; LOW, 0
button_pin = machine.Pin(28, machine.Pin.IN, machine.Pin.PULL_DOWN)

# Define all the pins for color in the RGB LED
red = Pin(15, Pin.OUT)
green = Pin(12, Pin.OUT)
blue = Pin(11, Pin.OUT)
# --- Global State ---
# This variable will hold the task that plays a note from an API call.
# This allows us to cancel it if a /stop request comes in.
api_note_task = None

# --- Core Functions ---


def connect_to_wifi(wifi_config: str = "wifi_config.json"):
    with open(wifi_config, "r") as f:
        data = json.load(f)

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(data["ssid"], data["password"])

    # Wait for connection or fail
    max_wait = 10
    print("Connecting to Wi-Fi...")
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        time.sleep(1)

    if wlan.status() != 3:
        raise RuntimeError("Network connection failed")
    else:
        status = wlan.ifconfig()
        ip_address = status[0]
        print(f"Connected! Pico IP Address: {ip_address}")
    return ip_address


def play_tone(frequency: int, duration_ms: int) -> None:
    """Plays a tone on the buzzer for a given duration."""
    if frequency > 0:
        green.value(1)
        buzzer_pin.freq(int(frequency))
        buzzer_pin.duty_u16(32768)  # 50% duty cycle
        time.sleep_ms(duration_ms)  # type: ignore[attr-defined]
        stop_tone()
        green.value(0)
    else:
        time.sleep_ms(duration_ms)  # type: ignore[attr-defined]


def stop_tone():
    """Stops any sound from playing."""
    buzzer_pin.duty_u16(0)  # 0% duty cycle means silence


async def play_api_note(frequency, duration_s):
    """Coroutine to play a note from an API call, can be cancelled."""
    try:
        print(f"API playing note: {frequency}Hz for {duration_s}s")
        buzzer_pin.freq(int(frequency))
        buzzer_pin.duty_u16(32768)  # 50% duty cycle
        await asyncio.sleep(duration_s)
        stop_tone()
        print("API note finished.")
    except asyncio.CancelledError:
        stop_tone()
        print("API note cancelled.")


def map_value(x, in_min, in_max, out_min, out_max):
    """Maps a value from one range to another."""
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

""" Alex's Code """
def play_song_on_pico(digital_values, digital_length, note_duration=0.05):
   
    for f in digital_values:
        if f <= 0:
            buzzer_pin.duty_u16(0)  # silence if freq <= 0
        else:
            green.value(1)
            buzzer_pin.freq(int(f))
            buzzer_pin.duty_u16(32768) # 50% duty cycle
            print(f)
            time.sleep(note_duration) # wait for next rising edge of 2 Hz clock
            green.value(0)

    buzzer_pin.duty_u16(0)  # turn off when done

""" Hannah's Code """
def collect_pico_data(record_button_stat):
    intensity_array = []
    # Read current sensor value, ranges from 0 to 65535, 0 being low voltage 65535 meaning high voltage around 3.3V, as voltage increases so does intensity of light
    if record_button_stat:
        start_time = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), start_time) < 10_000:
            blue.value(1)
            light_value = map_value(photo_sensor_pin.read_u16(),0,65535,0,699)
            intensity_array.append(light_value)
            time.sleep(0.05)  # clock is every 50ms
            blue.value(0)
    return intensity_array, len(intensity_array)


async def handle_request(reader, writer):
    """Handles incoming HTTP requests."""
    global api_note_task

    print("Client connected")
    request_line = await reader.readline()
    # Skip headers
    while await reader.readline() != b"\r\n":
        pass

    try:
        request = str(request_line, "utf-8")
        method, url, _ = request.split()
        print(f"Request: {method} {url}")
    except (ValueError, IndexError):
        writer.write(b"HTTP/1.0 400 Bad Request\r\n\r\n")
        await writer.drain()
        writer.close()
        await writer.wait_closed()
        return

    # Read current sensor value
    if button_pin.value() == True:
        light_value, raw_data_length = collect_pico_data(True)
    else:
        light_value = [0]
        raw_data_length = 0

    response = ""
    content_type = "text/html"

    # --- API Endpoint Routing ---
    if method == "GET" and url == "/sensor":
        data  = {"raw_data_array": light_value,
                 "raw_data_length": raw_data_length}
        response = json.dumps(data)
        content_type = "application/json"

    elif method == "GET" and url == "/health":
        data  = {"status": "ok",
                 "device_id": "hello world", #machine.unique_id(),
                 "api": "1.0.0"} # What do this do???
        
        response = json.dumps(data)
        print("Dump data")
        content_type = "application/json"


    elif method == "POST" and url == "/melody":
        # This requires reading the request body, which is not trivial.
        # A simple approach for a known content length:
        # Note: A robust server would parse Content-Length header.
        # For this student project, we'll assume a small, simple JSON body.
        raw_data = await reader.read(65536)
        try:
            # Loads data from the API
            data = json.loads(raw_data)
            musicArray = data.get("notes", 0)
            musicLength = data.get("entries", 0)
            print(musicArray)

            # If a note is already playing via API, cancel it first
            if api_note_task:
                api_note_task.cancel()

            # Start the new note as a background task
            play_song_on_pico(musicArray,musicLength)

            response = '{"status": "ok", "message": "Note playing started."}'
            content_type = "application/json"
        except (ValueError, json.JSONDecodeError):
            writer.write(b'HTTP/1.0 400 Bad Request\r\n\r\n{"error": "Invalid JSON"}\r\n')
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            return

    elif method == "POST" and url == "/stop":
        if api_note_task:
            api_note_task.cancel()
            api_note_task = None
        stop_tone()  # Force immediate stop
        response = '{"status": "ok", "message": "All sounds stopped."}'
        content_type = "application/json"
    else:
        writer.write(b"HTTP/1.0 404 Not Found\r\n\r\n")
        await writer.drain()
        writer.close()
        await writer.wait_closed()
        return

    # Send response
    writer.write(
        f"HTTP/1.0 200 OK\r\nContent-type: {content_type}\r\n\r\n".encode("utf-8")
    )
    writer.write(response.encode("utf-8"))
    await writer.drain()
    writer.close()
    await writer.wait_closed()
    print("Client disconnected")


async def main():
    """Main execution loop."""
    try:
        red.value(1)
        ip = connect_to_wifi()
        print(f"Starting web server on {ip}...")
        server = await asyncio.start_server(handle_request, "0.0.0.0", 80)
        print("Server started in port 80")
        red.value(0)
    except Exception as e:
        print(f"Failed to initialize: {e}")
        return
    
    while True:
        await asyncio.sleep(1)
        
    
    """
    # This loop runs the "default" behavior: playing sound based on light
    while True:
        # Only run this loop if no API note is currently scheduled to play
        if api_note_task is None or api_note_task.done():
            # Read the sensor. Values range from ~500 (dark) to ~65535 (bright)
            light_value = photo_sensor_pin.read_u16()

            # Map the light value to a frequency range (e.g., C4 to C6)
            # Adjust the input range based on your room's lighting
            min_light = 1000
            max_light = 65000
            min_freq = 261  # C4
            max_freq = 1046  # C6

            # Clamp the light value to the expected range
            clamped_light = max(min_light, min(light_value, max_light))

            if clamped_light > min_light:
                frequency = map_value(
                    clamped_light, min_light, max_light, min_freq, max_freq
                )
                buzzer_pin.freq(frequency)
                buzzer_pin.duty_u16(32768)  # 50% duty cycle
            else:
                stop_tone()  # If it's very dark, be quiet

        # await asyncio.sleep_ms(50)  # type: ignore[attr-defined]

        """
# Run the main event loop
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program stopped.")
        stop_tone()
