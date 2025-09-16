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
