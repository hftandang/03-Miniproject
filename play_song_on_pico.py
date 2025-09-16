
#Libraries
from machine import Pin, PWM
import time

#Set buzzer pin 
buzzer = PWM(Pin(16))  #can change pin number if needed
buzzer.duty_u16(0) 


def play_song_on_pico(digital_values, digital_length, note_duration=0.5):
   
    for f in digital_values:
        if f <= 0:
            buzzer.duty_u16(0)  # silence if freq <= 0
        else:
            buzzer.freq(int(f))
            time.sleep(note_duration) # wait for next rising edge of 2 Hz clock

    buzzer.duty_u16(0)  # turn off when done
    buzzer.deinit()
#test
