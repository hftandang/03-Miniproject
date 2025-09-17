# conductor.py
# To be run on a student's computer (not the Pico)
# Requires the 'requests' library: pip install requests

import requests
import time

# --- Configuration ---
# Students should populate this list with the IP address(es of their Picos
PICO_IPS = [
    "192.168.0.234",
]

# --- Conductor Logic ---
""" Code Written By Justin """
# Retrieves raw sensor data from the Pico
def raw_data_from_pico():
    """Obtains raw data from a pico by pulling data from it """
    dataUrl = f"http://{PICO_IPS[0]}/sensor"

    # Collects data from the Pico from a JSON file
    print("Collecting sensor data")
    try:
        sensorResponse = requests.get(dataUrl, timeout=11)
        data = sensorResponse.json()
        sensorDataArray = (data["raw_data_array"])[:]
        sensorDataLength = data["raw_data_length"]

    except requests.exceptions.RequestException as e:
        print(f"Error contacting {PICO_IPS[0]}: {e}")
        return None, None

    return sensorDataArray, sensorDataLength


# Sends the song to all the picos using the digital values, digital length method
def send_song_to_pico(digital_values, digital_length):
    """Sends a /melody melody request to every Pico in the list."""
    # Loops through all of the values in digital_values, and send them one-by-one to the Picos
    payload = {"notes": digital_values,
               "entries": digital_length}
    for ip in PICO_IPS:
        url = f"http://{ip}/melody"
        try:
            # We use a short timeout because we don't need to wait for a response
            # This makes the orchestra play more in sync.
            requests.post(url, json=payload, timeout=10)
        except requests.exceptions.Timeout:
            # This is expected, we can ignore it
            pass
        except requests.exceptions.RequestException as e:
            print(f"Error contacting {ip}: {e}")

    return


""" Code Written By AJ"""
# Function to convert the raw data to music notes
def convert_to_song(analog_values, analog_length): # Function expects 2 inputs, a list of analog values and the analog length (which should be equal to the analog values list's length)

    # Used Hertz for middle octive keys from link on Github
    C = 262.0
    D = 294.0
    E = 330.0
    F = 349.0
    G = 392.0
    A = 440.0
    B = 494.0

    digital_values = [None] * analog_length # Empty python list for the digital values that is equal in length to the original analog list's length

    # For loop for converting each value in the analog_values list into a note equivalent and saving that in the respective digital_values list spot
    for i in range(analog_length):
        if analog_values[i] <= 99.0:
            digital_values[i] = C
        elif analog_values[i] <= 199.0 and analog_values[i] > 99.0:
            digital_values[i] = D
        elif analog_values[i] <= 299.0 and analog_values[i] > 199.0:
            digital_values[i] = E
        elif analog_values[i] <= 399.0 and analog_values[i] > 299.0:
            digital_values[i] = F
        elif analog_values[i] <= 499.0 and analog_values[i] > 399.0:
            digital_values[i] = G
        elif analog_values[i] <= 599.0 and analog_values[i] > 499.0:
            digital_values[i] = A
        elif analog_values[i] <= 699.0 and analog_values[i] > 599.0:
            digital_values[i] = B

    digital_length = len(digital_values) # Length of the new digital_values list (should be identical to the original length)

    return digital_values, digital_length # Return both the digital_values list and the new digital length (which should be identical to the original analg length)


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

        # Receives the data from the Pico
        sensorDataArray, sensorDataLength = None, None
        while sensorDataLength is None:
            sensorDataArray, sensorDataLength = raw_data_from_pico()
            print("Waiting for sensor")
            time.sleep(1)

        print("Sensor Data Array:")
        print(sensorDataArray)

        # Converts the Data
        songArray, songLength = convert_to_song(sensorDataArray, sensorDataLength)

        print("Song Data Array:")
        print(songArray)
        # Plays the song
        send_song_to_pico(songArray, songLength)

        print("\nSong finished!")

    except KeyboardInterrupt:
        print("\nConductor stopped by user.")
