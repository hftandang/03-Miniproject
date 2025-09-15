# conductor.py
# To be run on a student's computer (not the Pico)
# Requires the 'requests' library: pip install requests

import requests
import time

# --- Configuration ---
# Students should populate this list with the IP address(es of their Picos
PICO_IPS = [
    "192.168.1.101",
]

# --- Music Definition ---
# Notes mapped to frequencies (in Hz)
C4 = 262
D4 = 294
E4 = 330
F4 = 349
G4 = 392
A4 = 440
B4 = 494
C5 = 523

# A simple melody: "Twinkle, Twinkle, Little Star"
# Format: (note_frequency, duration_in_ms)
SONG = [
    (C4, 400),
    (C4, 400),
    (G4, 400),
    (G4, 400),
    (A4, 400),
    (A4, 400),
    (G4, 800),
    (F4, 400),
    (F4, 400),
    (E4, 400),
    (E4, 400),
    (D4, 400),
    (D4, 400),
    (C4, 800),
]

# --- Conductor Logic ---

""" Code Written By Justin """
def raw_data_from_pico():
    """Obtains raw data from a pico by pulling data from it """
    healthUrl = f"http://{PICO_IPS[0]}/health"
    dataUrl = f"http://{PICO_IPS[0]}/sensor"
    try:
        healthResponse = requests.get(healthUrl, timeout=0.1) # Pulls request data from sensor
        healthData = healthResponse.json()                    # Gets JSON data from the request
        if healthData["status"] != "ok":                      # If the device isn't ok, print health data
            print("Status:", healthData["status"])
            print("Device ID:", healthData["device_id"])
            print("API Version:", healthData["api"])
    except requests.exceptions.Timeout:
        # This is expected, we can ignore it
        pass
    except requests.exceptions.RequestException as e:
        print(f"Error contacting {PICO_IPS[0]}: {e}")

    # For a time period of collectionDuration seconds, tries to obtain sensor info from the pico through looping for a certain duration
    sensorDataArray = []
    startTime = time.time()
    collectionDuration = 10
    timeoutInterval = 0.1

    print(f"Collecting sensor data for {collectionDuration} data points...")
    while (time.time() - startTime) < collectionDuration:
        try:
            sensorResponse = requests.get(dataUrl, timeout=0.1)
            data = sensorResponse.json()
            sensorDataArray.append(data)

        except requests.exceptions.RequestException as e:
            print(f"Error contacting {PICO_IPS[0]}: {e}")

        time.sleep(timeoutInterval)

    return sensorDataArray, len(sensorDataArray)


# Sends the song to all the picos using the digitalvalues, digital length method
def send_song_to_pico(digital_values, digital_length):
    # Loops through all of the values in digital_values, and send them one-by-one to the Picos
    for i in range(digital_length):
        play_note_on_all_picos(digital_values[i],0.5)



def play_note_on_all_picos(freq, ms):
    """Sends a /tone POST request to every Pico in the list."""
    print(f"Playing note: {freq}Hz for {ms}ms on all devices.")

    payload = {"freq": freq, "ms": ms, "duty": 0.5}

    for ip in PICO_IPS:
        url = f"http://{ip}/tone"
        try:
            # We use a short timeout because we don't need to wait for a response
            # This makes the orchestra play more in sync.
            requests.post(url, json=payload, timeout=0.1)
        except requests.exceptions.Timeout:
            # This is expected, we can ignore it
            pass
        except requests.exceptions.RequestException as e:
            print(f"Error contacting {ip}: {e}")


if __name__ == "__main__":
    print("--- Pico Light Orchestra Conductor ---")
    print(f"Found {len(PICO_IPS)} devices in the orchestra.")
    print("Press Ctrl+C to stop.")

    try:
        # Give a moment for everyone to get ready
        print("\nStarting in 3...")
        time.sleep(1)
        print("2...")
        time.sleep(1)
        print("1...")
        time.sleep(1)
        print("Go!\n")

        # Play the song
        for note, duration in SONG:
            play_note_on_all_picos(note, duration)
            # Wait for the note's duration plus a small gap before playing the next one
            time.sleep(duration / 1000 * 1.1)

        print("\nSong finished!")

    except KeyboardInterrupt:
        print("\nConductor stopped by user.")
